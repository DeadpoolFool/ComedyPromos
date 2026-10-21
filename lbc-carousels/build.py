"""Build the LBC Fall Fest photo carousels (1080x1080, per the README).

Usage: python3 build.py /path/to/photos  (folder with Miguel's 85.jpg..104.jpg)
Photos are fit to width and letterboxed, never cropped, so the sign and his body stay whole.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/photos/lbc-prelim-2026-10-17/all"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONTS = os.path.expanduser("~/.fonts")
S = 1080
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"  # closest to IG's Classic text
BLACK, RED, CREAM = (10, 10, 10), (0xDF, 0x27, 0x31), (0xEF, 0xE6, 0xD2)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def photo(n, width=S):
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, f"{n}.jpg"))).convert("RGB")
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def wrap(draw, text, fnt, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            test = f"{cur} {word}".strip()
            if draw.textlength(test, font=fnt) <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(draw, lines_spec, top, bottom, pad=72):
    """lines_spec: list of (text, font, color). Vertically centred between top and bottom."""
    rendered = []
    for text, fnt, color in lines_spec:
        for line in wrap(draw, text, fnt, S - 2 * pad):
            asc, desc = fnt.getmetrics()
            rendered.append((line, fnt, color, asc + desc))
        rendered.append(None)  # paragraph gap
    rendered.pop()
    gap = 22
    total = sum(r[3] if r else gap for r in rendered)
    y = top + (bottom - top - total) // 2
    for r in rendered:
        if r is None:
            y += gap
            continue
        line, fnt, color, h = r
        draw.text((pad, y), line, font=fnt, fill=color)
        y += h


def joke_slide(n, lines_spec, swipe=False, handle=False):
    """Text band on top, letterboxed stage photo underneath."""
    img = Image.new("RGB", (S, S), BLACK)
    ph = photo(n)
    img.paste(ph, (0, S - ph.height))
    d = ImageDraw.Draw(img)
    text_block(d, lines_spec, 0, S - ph.height)
    mono = font("SpaceMono-Bold.ttf", 26)
    if swipe:
        d.text((S - 72, S - ph.height - 44), "→", font=font("SpaceMono-Bold.ttf", 40), fill=RED, anchor="rm")
    if handle:
        d.text((S - 72, S - ph.height - 44), "@ARTEMISFUNNY", font=mono, fill=CREAM, anchor="rm")
    return img


def dump_slide(n):
    """Photo only, centred on black. No text on the photo."""
    img = Image.new("RGB", (S, S), BLACK)
    ph = photo(n)
    if ph.height > S:  # vertical shot: fit by height instead
        ph = ph.resize((round(ph.width * S / ph.height), S), Image.LANCZOS)
    img.paste(ph, ((S - ph.width) // 2, (S - ph.height) // 2))
    return img


def notes_card(text):
    """Plain written-joke card, the format comics post as the first slide."""
    img = Image.new("RGB", (S, S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    pad = 96
    head = ImageOps.fit(Image.open(os.path.join(HERE, "..", "brand", "headshot.jpeg")).convert("RGB"),
                        (110, 110), centering=(0.5, 0.3))
    mask = Image.new("L", (110, 110), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 109, 109), fill=255)
    img.paste(head, (pad, pad), mask)
    d.text((pad + 136, pad + 14), "Artem Mashkov", font=font("BarlowCondensed-SemiBold.ttf", 44), fill=(15, 15, 15))
    d.text((pad + 136, pad + 64), "@artemisfunny", font=font("SpaceMono-Regular.ttf", 28), fill=(110, 110, 110))
    body = font("BarlowCondensed-Medium.ttf", 64)
    y = pad + 190
    for line in wrap(d, text, body, S - 2 * pad):
        if line:
            d.text((pad, y), line, font=body, fill=(15, 15, 15))
        y += 78
    return img


def caption_slide(n, text, at=0.88):
    """Stage photo with the joke line typed over it in plain white, the way the caption sits on IG.

    The photo is letterboxed (never cropped); the line sits low, like a subtitle.
    """
    img = dump_slide(n)
    return caption(img, text, *photo_box(n), at)


def photo_box(n):
    """Top and height of photo n as dump_slide places it."""
    h = photo(n).height
    h = min(h, S)
    return (S - h) // 2, h


def caption(img, text, top, height, at, size=44):
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(INTER, size)
    lines = wrap(d, text, fnt, 820)
    lh = sum(fnt.getmetrics()) + 6
    y = top + round(at * height) - (len(lines) - 1) * lh
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i, line in enumerate(lines):
        sd.text((S // 2 + 2, y + i * lh + 3), line, font=fnt, fill=(0, 0, 0, 200), anchor="ma")
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    img.paste(shadow, (0, 0), shadow)
    for i, line in enumerate(lines):
        d.text((S // 2, y + i * lh), line, font=fnt, fill=(255, 255, 255), anchor="ma", stroke_width=2, stroke_fill=(0, 0, 0))
    return img


def stacked_slide(top_n, top_text, bottom_n, bottom_text):
    """One slide, two stage shots: setup captioned on the top photo, punch on the bottom one."""
    img = Image.new("RGB", (S, S), BLACK)
    w = 960
    y = 0
    for n, text in ((top_n, top_text), (bottom_n, bottom_text)):
        ph = photo(n, w)
        img.paste(ph, ((S - w) // 2, y))
        caption(img, text, y, ph.height, 0.9, size=36)
        y += ph.height
    return img


def save(img, name):
    img.save(os.path.join(OUT, name), quality=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    head = font("Anton-Regular.ttf", 92)
    body = font("BarlowCondensed-SemiBold.ttf", 66)

    # 1. Swipe for the punchline: Russian Superstitions, stage order from the 2026-10-13 tape fix.
    slides = [
        (92, [("Russians don't believe in a lot.", head, CREAM)], True, False),
        (91, [("Human rights. Borders.", body, CREAM), ("Paying for software.", body, CREAM)], True, False),
        (89, [("But we do believe in superstitions.", body, CREAM),
              ("Don't whistle inside the house, or you'll lose money.", body, CREAM)], True, False),
        (88, [("Don't split a pole, or you'll get into a fight.", body, CREAM)], True, False),
        (93, [("No keys on the table...", body, CREAM), ("or you have to invade Ukraine.", head, RED)], False, True),
    ]
    for i, (n, spec, swipe, handle) in enumerate(slides, 1):
        save(joke_slide(n, spec, swipe, handle), f"superstitions_{i}.jpg")

    # 2. Written joke card + the stage shot: Both of The Bad Guys (Notion Joke field, stage-fix ending).
    save(notes_card("I'm exactly what I look like. A Russian Jew.\n\nNo no, don't clap.\n\n"
                    "We're both of the bad guys right now. And I promise you, I'm not one of the good ones."),
         "badguys_1.jpg")
    save(dump_slide(93), "badguys_2.jpg")

    # 4. Caption-on-photo version of the same joke: one beat per slide, plain white text over the photo.
    beats = [
        (92, "Russians don't believe in a lot."),
        (91, "Human rights. Borders. Paying for software."),
        (89, "But we do believe in superstitions."),
        (88, "Don't whistle inside the house, or you'll lose money."),
        (102, "Don't split a pole, or you'll get into a fight."),
        (93, "No keys on the table, or you have to invade Ukraine."),
        (100, "I told my mom not to do that."),
    ]
    for i, (n, text) in enumerate(beats, 1):
        save(caption_slide(n, text), f"captioned_{i}.jpg")

    # 5. Two-photo single slides: setup on top, punch underneath.
    save(stacked_slide(92, "I'm exactly what I look like. A Russian Jew.",
                       93, "We're both of the bad guys right now. And I'm not one of the good ones."),
         "stacked_badguys.jpg")
    save(stacked_slide(91, "Russians don't believe in human rights, borders, or paying for software.",
                       93, "But we do believe in superstitions. No keys on the table, or you have to invade Ukraine."),
         "stacked_superstitions.jpg")

    # 3. Photo dump: no text on any slide, the caption does the talking.
    for i, n in enumerate([93, 92, 100, 89, 101, 103], 1):
        save(dump_slide(n), f"dump_{i}.jpg")


if __name__ == "__main__":
    main()
