"""Put Artem's headshot into LBC's quarter-final flyer (Fri Oct 23, 9PM).

Reuses headshot.jpg + headshot_alpha.npy from the prelim build (see flyer_insert.py).
Outputs out/lbc_qf_flyer_1080x1350.png and out/lbc_qf_flyer_1080x1920.png.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
FLYER = Image.open(HERE / "lbc_qf_flyer.png").convert("RGB")  # 1080x1350, LBC's own
NAME = "ARTEM MASHKOV"
ANTON = str(Path.home() / ".fonts/Anton-Regular.ttf")
GREEN, GOLD = (67, 81, 41), (246, 198, 70)  # flyer's own lettering colors
CREAM = (252, 233, 185)
BANNERS_END = 965  # quarter-final ribbon ends here; address row starts ~1080


def cutout():
    rgb = Image.open(HERE / "headshot.jpg").convert("RGB")
    a = np.load(HERE / "headshot_alpha.npy").squeeze()
    a = np.clip((a - 0.35) / 0.4, 0, 1)
    # The model mask is coarse around the fingers (fine on dark wood, ghosty on cream).
    # Outside the shirt, key out the near-black studio backdrop by luminance.
    lum = np.array(rgb.convert("L")).astype(np.float32)
    key = np.clip((lum - 34) / 22, 0, 1)
    hands = np.zeros_like(a)
    hands[480:900, :176] = 1   # left hand (headshot coords; stays clear of the black sleeve)
    hands[705:900, :232] = 1   # left forearm, below the sleeve, outside the torso
    hands[480:900, 584:] = 1   # right hand
    hands[705:900, 528:] = 1   # right forearm
    hands = np.array(Image.fromarray((hands * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))) / 255
    a = a * (1 - hands + hands * key)
    m =Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im = rgb.copy()
    im.putalpha(m)
    return im.crop((70, 225, 710, 960))  # head to belt, both hands


def fade_bottom(im, px):
    a = np.array(im.getchannel("A")).astype(np.float32)
    ramp = np.ones(a.shape[0], np.float32)
    ramp[-px:] = np.linspace(1, 0, px)
    im.putalpha(Image.fromarray((a * ramp[:, None]).astype(np.uint8)))
    return im


def sticker(p, stroke, color=CREAM):
    """Cut-out with a solid outline, the flat sticker look the flyer's art uses."""
    pad = stroke + 30
    big = Image.new("RGBA", (p.width + pad * 2, p.height + pad * 2), (0, 0, 0, 0))
    big.paste(p, (pad, pad), p)
    a = big.getchannel("A").point(lambda v: 255 if v > 230 else 0)
    ring = a.filter(ImageFilter.MaxFilter(stroke * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
    # keep the outline's own fade where the photo fades out
    ring = Image.fromarray(np.minimum(np.array(ring), np.array(big.getchannel("A").filter(ImageFilter.MaxFilter(stroke * 2 + 1)))))
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sh.putalpha(ring.point(lambda v: int(v * 0.45)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    out.paste(sh, (6, 9), sh)
    rim = Image.new("RGBA", big.size, color + (0,))
    rim.putalpha(ring)
    out = Image.alpha_composite(out, rim)
    out = Image.alpha_composite(out, big)
    return out, pad


def ribbon_occluder(h_offset=0, height=1350):
    """Mask of the #LBCFF ribbon + red band, so he stands behind them."""
    m = Image.new("L", (1080, height), 0)
    d = ImageDraw.Draw(m)
    y = lambda v: v + h_offset
    d.rectangle((345, y(416), 756, y(520)), fill=255)                          # ribbon face
    d.polygon([(290, y(436)), (346, y(436)), (346, y(520)), (318, y(520))], fill=255)  # left tail
    d.polygon([(755, y(436)), (812, y(436)), (790, y(520)), (755, y(520))], fill=255)  # right tail
    d.rectangle((0, y(512), 1080, y(BANNERS_END)), fill=255)                  # red band + QF ribbon
    return m


def name(canvas, cx, y, size):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(ANTON, size)
    d.text((cx, y), NAME, font=f, fill=GREEN, stroke_width=max(3, size // 18), stroke_fill=GOLD, anchor="mm")


def feed():
    base = FLYER.convert("RGBA")
    p = cutout()
    p = p.resize((round(p.width * 0.74), round(p.height * 0.74)), Image.LANCZOS)
    p = fade_bottom(p, 60)
    s, pad = sticker(p, 3)
    x, y = 300, 52  # head peeks up over the pie, hands clear the ribbon
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(s, (x - pad, y - pad), s)
    # cut him off behind the ribbon
    occ = ribbon_occluder()
    la = np.array(layer.getchannel("A")).astype(np.float32) * (1 - np.array(occ) / 255)
    layer.putalpha(Image.fromarray(la.astype(np.uint8)))
    c = Image.alpha_composite(base, layer)
    name(c, 540, 1022, 76)
    return c.convert("RGB")


def story():
    """9:16: LBC's art top and bottom; Artem gets the new cream space between them."""
    extra = 1920 - 1350
    c = Image.new("RGBA", (1080, 1920), CREAM + (255,))
    c.paste(FLYER.crop((0, 0, 1080, BANNERS_END)), (0, 0))
    c.paste(FLYER.crop((0, 1070, 1080, 1350)), (0, 1070 + extra))
    p = cutout()
    p = p.resize((round(p.width * 0.84), round(p.height * 0.84)), Image.LANCZOS)
    p = fade_bottom(p, 230)
    s, pad = sticker(p, 3)
    c.alpha_composite(s, (1080 - p.width - 12 - pad, 1000 - pad))
    d = ImageDraw.Draw(c)
    f = ImageFont.truetype(ANTON, 124)
    for k, word in enumerate(("ARTEM", "MASHKOV")):
        d.text((272, 1250 + k * 150), word, font=f, fill=GREEN, stroke_width=8, stroke_fill=GOLD, anchor="mm")
    return c.convert("RGB")


if __name__ == "__main__":
    feed().save(OUT / "lbc_qf_flyer_1080x1350.png")
    story().save(OUT / "lbc_qf_flyer_1080x1920.png")
    print("ok")
