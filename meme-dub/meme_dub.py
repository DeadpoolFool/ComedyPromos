#!/usr/bin/env python3
"""Dub a meme clip with Artem: his face on the subject, his voice note, synced lips, new caption.

    python meme_dub.py --clip bernie.mov --voice take1.m4a --face face.jpg \
        --erase-box 110,570,500,100 --out out/bernie.mp4

Steps: trim the voice note's dead air, fit the clip to the voice (ping-pong if the
voice runs longer), erase the old burned-in caption, swap face + lip-sync + enhance
with FaceFusion, transcribe the voice note, burn the new caption, mux the audio.

Needs ffmpeg, a FaceFusion checkout (--facefusion, default ./facefusion) and
`pip install sherpa-onnx opencv-python-headless pillow numpy`. See README.md.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ASR_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"
           "sherpa-onnx-whisper-small.en.tar.bz2")
FONT_CANDIDATES = [
    HERE / "fonts/Inter-Bold.otf",
    Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), file=sys.stderr)
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
                          "-show_streams", str(path)], check=True, capture_output=True, text=True)
    info = json.loads(out.stdout)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    return float(info["format"]["duration"]), video


def speech_bounds(audio, noise_db=-35, min_silence=0.15):
    """Return (start, end) of the speech in a voice note, ignoring leading/trailing silence."""
    total, _ = probe(audio)
    log = subprocess.run(["ffmpeg", "-i", str(audio), "-af",
                          f"silencedetect=n={noise_db}dB:d={min_silence}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    start = ends[0] if starts and starts[0] < 0.05 and ends else 0.0
    # Trailing silence either never ends or ends at the last sample.
    trailing = starts and (len(ends) < len(starts) or ends[-1] >= total - 0.1)
    end = starts[-1] if trailing and starts[-1] > start else total
    if end <= start:  # all silence by this threshold; keep the whole note
        return 0.0, total
    return start, end


def trim_voice(src, dst, pad=0.08):
    start, end = speech_bounds(src)
    start = max(0.0, start - pad)
    end = end + pad
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", src,
         "-af", "afade=t=in:d=0.02", "-ac", "1", "-ar", "48000", dst])
    return end - start


def fit_clip(src, dst, duration):
    """Make the clip exactly `duration` long, ping-ponging when the voice outlasts it."""
    clip_len, _ = probe(src)
    if clip_len >= duration:
        vf = f"[0:v]trim=duration={duration:.3f},setpts=PTS-STARTPTS[v]"
    else:
        loops = int(duration // (2 * clip_len)) + 1
        split = f"[0:v]split=2[f][b];[b]reverse[rv];[f]split={loops}" + "".join(
            f"[a{i}]" for i in range(loops)) + f";[rv]split={loops}" + "".join(
            f"[r{i}]" for i in range(loops)) + ";"
        chain = "".join(f"[a{i}][r{i}]" for i in range(loops))
        vf = (split + chain + f"concat=n={2 * loops}:v=1:a=0,trim=duration={duration:.3f},"
              "setpts=PTS-STARTPTS[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", vf, "-map", "[v]", "-an",
         "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst])


def erase_caption(src, dst, box, threshold=190):
    """Inpaint bright caption text inside box=(x, y, w, h) on every frame."""
    x, y, w, h = box
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp = Path(dst).with_suffix(".raw.mp4")
    writer = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    kernel = np.ones((5, 5), np.uint8)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        roi = frame[y:y + h, x:x + w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        mask = cv2.dilate((gray > threshold).astype(np.uint8) * 255, kernel, iterations=2)
        frame[y:y + h, x:x + w] = cv2.inpaint(roi, mask, 7, cv2.INPAINT_TELEA)
        writer.write(frame)
    cap.release()
    writer.release()
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-crf", "14",
         "-pix_fmt", "yuv420p", dst])
    tmp.unlink()


def transcribe(audio, models_dir):
    import sherpa_onnx
    import wave

    model = models_dir / "sherpa-onnx-whisper-small.en"
    if not model.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
        archive = models_dir / "whisper-small.en.tar.bz2"
        print("downloading Whisper small.en (~600 MB)", file=sys.stderr)
        urllib.request.urlretrieve(ASR_URL, archive)
        run(["tar", "xjf", archive, "-C", models_dir])
        archive.unlink()
    wav = Path(tempfile.mkstemp(suffix=".wav")[1])
    run(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ar", "16000", "-ac", "1", wav])
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=str(model / "small.en-encoder.int8.onnx"),
        decoder=str(model / "small.en-decoder.int8.onnx"),
        tokens=str(model / "small.en-tokens.txt"), num_threads=4)
    with wave.open(str(wav)) as w:
        samples = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    wav.unlink()
    stream = rec.create_stream()
    stream.accept_waveform(16000, samples)
    rec.decode_stream(stream)
    return stream.result.text.strip()


def wrap(text, font, max_width, draw):
    """Greedy wrap, then rebalance two lines so the top one isn't a long line over a stub."""
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    if len(lines) == 2:
        best = min(range(1, len(words)), key=lambda i: abs(
            draw.textlength(" ".join(words[:i]), font=font) - draw.textlength(" ".join(words[i:]), font=font)))
        top, bottom = " ".join(words[:best]), " ".join(words[best:])
        if max(draw.textlength(top, font=font), draw.textlength(bottom, font=font)) <= max_width:
            lines = [top, bottom]
    return lines


def caption_png(text, size, dst, center_y, font_px):
    width, height = size
    font_path = next(p for p in FONT_CANDIDATES if p.exists())
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(font_path), font_px)
    while True:
        lines = wrap(text, font, width * 0.86, draw)
        if len(lines) <= 2 or font_px <= 20:
            break
        font_px -= 2
        font = ImageFont.truetype(str(font_path), font_px)
    line_h = int(font_px * 1.2)
    top = int(center_y - line_h * len(lines) / 2)
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    for i, line in enumerate(lines):
        x = (width - draw.textlength(line, font=font)) / 2
        sdraw.text((x, top + i * line_h), line, font=font, fill=(0, 0, 0, 170))
        draw.text((x, top + i * line_h), line, font=font, fill="white")
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    Image.alpha_composite(shadow, img).save(dst)


def facefusion(ff_dir, face, voice, target, dst, threads):
    run([sys.executable, "facefusion.py", "headless-run", "-s", Path(face).resolve(),
         Path(voice).resolve(), "-t", Path(target).resolve(), "-o", Path(dst).resolve(),
         "--processors", "face_swapper", "lip_syncer", "face_enhancer",
         "--face-swapper-model", "inswapper_128", "--lip-syncer-model", "wav2lip_gan_96",
         "--face-enhancer-model", "gfpgan_1.4", "--face-enhancer-blend", "60",
         "--output-video-quality", "90", "--execution-thread-count", str(threads)], cwd=ff_dir)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clip", required=True, help="meme video")
    ap.add_argument("--voice", required=True, help="Artem's voice note")
    ap.add_argument("--face", required=True, help="clear, front-facing photo of Artem")
    ap.add_argument("--out", required=True)
    ap.add_argument("--caption", help="caption text; default is a transcript of the voice note")
    ap.add_argument("--erase-box", help="x,y,w,h of the clip's old burned-in caption")
    ap.add_argument("--caption-y", type=float, default=0.86, help="caption center, fraction of height")
    ap.add_argument("--font-px", type=int, default=0, help="caption size; default 4.5%% of width")
    ap.add_argument("--no-caption", action="store_true")
    ap.add_argument("--facefusion", default=str(HERE / "facefusion"))
    ap.add_argument("--models", default=str(HERE / ".models"))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--keep", action="store_true", help="keep the work folder")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="meme_dub_"))
    try:
        # Transcribe the untouched note before the slow render, so a misheard word
        # shows up in seconds (rerun with --caption to fix it).
        text = None
        if not args.no_caption:
            text = args.caption or transcribe(args.voice, Path(args.models))
            print(f"caption: {text}", file=sys.stderr)
        voice = work / "voice.wav"
        duration = trim_voice(args.voice, voice)
        target = work / "target.mp4"
        fit_clip(args.clip, target, duration)
        if args.erase_box:
            clean = work / "clean.mp4"
            erase_caption(target, clean, [int(v) for v in args.erase_box.split(",")])
            target = clean
        swapped = work / "swapped.mp4"
        facefusion(args.facefusion, args.face, voice, target, swapped, args.threads)

        if args.no_caption:
            shutil.copy(swapped, out)
        else:
            _, video = probe(swapped)
            size = (int(video["width"]), int(video["height"]))
            png = work / "caption.png"
            caption_png(text, size, png, size[1] * args.caption_y, args.font_px or int(size[0] * 0.045))
            run(["ffmpeg", "-v", "error", "-y", "-i", swapped, "-i", png, "-filter_complex",
                 "[0:v][1:v]overlay=0:0", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
        print(out)
    finally:
        if args.keep:
            print(f"work folder: {work}", file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
