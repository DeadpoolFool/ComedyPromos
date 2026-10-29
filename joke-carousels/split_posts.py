"""Two-photo joke carousel slides. Usage: python3 split_posts.py spec.json"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

FONT = os.path.expanduser("~/.fonts/Poppins-SemiBold.ttf")
W, H, GAP = 1080, 1350, 6
PANEL_H = (H - GAP) // 2


def panel(path):
    """Photo scaled to the panel height, trimmed evenly at the sides only."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im = im.resize((max(W, round(im.width * PANEL_H / im.height)), PANEL_H), Image.LANCZOS)
    if im.width < W:
        raise SystemExit(f"{path} is too narrow for a full-width panel; use a horizontal shot")
    left = (im.width - W) // 2
    return im.crop((left, 0, left + W, PANEL_H))


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def caption(img, text, size, bottom):
    """White text, dark outline, soft shadow, centred; last line ends at `bottom`."""
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(FONT, size)
    lines = wrap(d, text, fnt, W - 140)
    lh = round(size * 1.22)
    top = bottom - lh * len(lines)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i, line in enumerate(lines):
        sd.text((W // 2 + 3, top + i * lh + 4), line, font=fnt, fill=(0, 0, 0, 170), anchor="ma")
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    img.paste(shadow, (0, 0), shadow)
    for i, line in enumerate(lines):
        d.text((W // 2, top + i * lh), line, font=fnt, fill="white", anchor="ma",
               stroke_width=max(2, size // 18), stroke_fill=(20, 20, 20))


def text_size(text):
    # Short punches go big like Jenny's "...34"; long setups drop so they stay at 2-3 lines.
    return 64 if len(text) <= 30 else 50 if len(text) <= 70 else 44


def build(photos, handle, top, setup, bottom, punch):
    img = Image.new("RGB", (W, H), "white")
    img.paste(panel(os.path.join(photos, top)), (0, 0))
    img.paste(panel(os.path.join(photos, bottom)), (0, PANEL_H + GAP))
    caption(img, setup, text_size(setup), PANEL_H - 44)
    caption(img, punch, text_size(punch), H - 70)
    ImageDraw.Draw(img).text((W - 36, H - 26), handle, font=ImageFont.truetype(FONT, 30), fill="white",
                             anchor="rs", stroke_width=2, stroke_fill=(20, 20, 20))
    return img


def main():
    with open(sys.argv[1]) as f:
        spec = json.load(f)
    out = spec.get("out", "out")
    os.makedirs(out, exist_ok=True)
    for name, slides in spec["carousels"].items():
        for i, slide in enumerate(slides, 1):
            img = build(spec["photos"], spec.get("handle", "@artemisfunny"), *slide)
            img.save(os.path.join(out, f"split_{name}_{i}.jpg"), quality=92)


if __name__ == "__main__":
    main()
