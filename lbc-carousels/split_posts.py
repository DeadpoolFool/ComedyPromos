"""Two-photo joke posts, the format from Zucker's "The Year of the Carousel" (Jenny Gorelick, JFL, Michael Good).

One 1080x1350 image per joke: the setup captioned on the top photo, the punch on the bottom one,
both from the same camera position so only his face changes. Each photo is trimmed at the sides
only (about 5% each side) to fit its half, so the sign and his body stay in frame.

Usage: python3 split_posts.py /path/to/photos  (Miguel's 85.jpg..104.jpg)
Needs Poppins: curl -sfL https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-SemiBold.ttf -o ~/.fonts/Poppins-SemiBold.ttf
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/photos/lbc-prelim-2026-10-17/all"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
FONT = os.path.expanduser("~/.fonts/Poppins-SemiBold.ttf")
W, H, GAP = 1080, 1350, 6
PANEL_H = (H - GAP) // 2
HANDLE = "@artemisfunny"

# (file name, top photo, setup, bottom photo, punch). Wording follows each joke's Notion page and
# its latest tape fix.
POSTS = [
    ("split_badguys", 92, "I'm exactly what I look like. A Russian Jew. We're both of the bad guys right now.",
     93, "And I promise you, I'm not one of the good ones."),
    ("split_superstitions", 88,
     "Russians don't believe in human rights, borders, or paying for software. But we do believe in superstitions.",
     89, "If you leave your keys on the table, you have to invade Ukraine."),
    ("split_jewish_viagra", 96, "I'm 38, I needed a little help to finish. So I took the Jewish Viagra...",
     97, "Lactaid."),
    ("split_other_team", 91, "My wife is Yemeni, Hungarian, Austrian and German.",
     92, "If you're keeping track, that's the entire other team."),
]


def panel(n):
    """Photo n scaled to the panel height, trimmed evenly at the sides."""
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, f"{n}.jpg"))).convert("RGB")
    scale = PANEL_H / im.height
    im = im.resize((round(im.width * scale), PANEL_H), Image.LANCZOS)
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
    """White text with a dark outline and soft shadow, centred, its last line ending at `bottom`."""
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
    # Short punches go big like Jenny's "...34"; long setups drop down so they stay at 2-3 lines.
    return 64 if len(text) <= 30 else 50 if len(text) <= 70 else 44


def build(top_n, setup, bottom_n, punch):
    img = Image.new("RGB", (W, H), "white")
    img.paste(panel(top_n), (0, 0))
    img.paste(panel(bottom_n), (0, PANEL_H + GAP))
    caption(img, setup, text_size(setup), PANEL_H - 44)
    caption(img, punch, text_size(punch), H - 70)
    d = ImageDraw.Draw(img)
    d.text((W - 36, H - 26), HANDLE, font=ImageFont.truetype(FONT, 30), fill="white", anchor="rs",
           stroke_width=2, stroke_fill=(20, 20, 20))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, top_n, setup, bottom_n, punch in POSTS:
        build(top_n, setup, bottom_n, punch).save(os.path.join(OUT, f"{name}.jpg"), quality=92)


if __name__ == "__main__":
    main()
