"""One-photo slide with a list on the right. Usage: list_slide.py photo out.jpg item1 item2 ..."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT = os.path.expanduser("~/.fonts/Poppins-SemiBold.ttf")
W, H = 1080, 1350
photo, out, items = sys.argv[1], sys.argv[2], sys.argv[3:]
img = Image.open(photo).convert("RGB").resize((W, H))
# Darken the right side so the list reads over the sign.
shade = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(shade)
for x in range(W):
    sd.line([(x, 0), (x, H)], fill=int(max(0, min(1, (x - 430) / 260)) * 175))
img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shade)
d = ImageDraw.Draw(img); fnt = ImageFont.truetype(FONT, 56); x0, maxw = 560, W - 560 - 40
def wrap(t):
    lines, cur = [], ""
    for w in t.split():
        test = f"{cur} {w}".strip()
        if d.textlength(test, font=fnt) <= maxw: cur = test
        else: lines.append(cur); cur = w
    return lines + [cur]
blocks = [wrap(t) for t in items]; lh = 68; gap = 30
total = sum(len(b) * lh for b in blocks) + gap * (len(blocks) - 1); y = (H - total) // 2
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sdr = ImageDraw.Draw(sh); yy = y
for b in blocks:
    for line in b: sdr.text((x0 + 3, yy + 4), line, font=fnt, fill=(0, 0, 0, 170)); yy += lh
    yy += gap
img.paste(sh.filter(ImageFilter.GaussianBlur(5)), (0, 0), sh.filter(ImageFilter.GaussianBlur(5)))
for b in blocks:
    for line in b: d.text((x0, y), line, font=fnt, fill="white", stroke_width=3, stroke_fill=(20, 20, 20)); y += lh
    y += gap
d.text((W - 36, H - 26), "@artemisfunny", font=ImageFont.truetype(FONT, 30), fill="white", anchor="rs", stroke_width=2, stroke_fill=(20, 20, 20))
img.save(out, quality=92)
