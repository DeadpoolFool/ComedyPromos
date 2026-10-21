"""Two-photo joke carousel slides. Usage: python3 split_posts.py spec.json"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

FONT = os.path.expanduser("~/.fonts/Poppins-SemiBold.ttf")
W, H, GAP = 1080, 1350, 6
PANEL_H = (H - GAP) // 2

# Algospeak: words that get a post held back from Explore and Reels when Meta reads them off the image
# (profanity, sex, violence, self-harm, drugs, hate), swapped for the sound-alikes comics use.
# Matching is whole-word and case-insensitive; a capitalised word keeps its capital.
ALGOSPEAK = {
    "fuck": "fug", "fucking": "fugging", "fucked": "fugged", "fucker": "fugger", "motherfucker": "motherfugger",
    "shit": "sh!t", "shitty": "sh!tty", "bullshit": "bullsh!t",
    "sex": "seggs", "sexy": "seggsy", "sexual": "seggsual",
    "porn": "corn", "dick": "dih", "dicks": "dihs", "cock": "c0ck", "pussy": "p*ssy",
    "bitch": "b!tch", "bitches": "b!tches", "whore": "h0e", "slut": "sl*t",
    "pedophile": "PDFile", "pedophiles": "PDFiles", "pedo": "PDF", "rape": "grape", "raped": "graped",
    "kill": "unalive", "killed": "unalived", "suicide": "unalive", "dead": "unalive",
    "nazi": "n@zi", "nazis": "n@zis", "hitler": "H!tler", "cocaine": "coke", "heroin": "her0in",
}


def algospeak(text, extra=None):
    """'so fucking cold' -> 'so fugging cold'. `extra` adds or overrides swaps from the spec."""
    swaps = {**ALGOSPEAK, **{k.lower(): v for k, v in (extra or {}).items()}}

    def swap(m):
        word, new = m.group(0), swaps[m.group(0).lower()]
        return new[0].upper() + new[1:] if word[0].isupper() else new
    pattern = r"\b(" + "|".join(sorted(map(re.escape, swaps), key=len, reverse=True)) + r")\b"
    return re.sub(pattern, swap, text, flags=re.IGNORECASE)


def panel(path):
    """Photo scaled to the panel height, trimmed evenly at the sides only."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im = im.resize((round(im.width * PANEL_H / im.height), PANEL_H), Image.LANCZOS)
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
    extra = spec.get("algospeak", {})
    for name, slides in spec["carousels"].items():
        for i, (top, setup, bottom, punch) in enumerate(slides, 1):
            if spec.get("censor", True):
                setup, punch = algospeak(setup, extra), algospeak(punch, extra)
            img = build(spec["photos"], spec.get("handle", "@artemisfunny"), top, setup, bottom, punch)
            img.save(os.path.join(out, f"split_{name}_{i}.jpg"), quality=92)


if __name__ == "__main__":
    main()
