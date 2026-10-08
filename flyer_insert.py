"""Put Artem's headshot into the official LBC Fall Fest flyer.

Needs headshot_alpha.npy (person mask from MediaPipe selfie_multiclass, see README in captions.md).
Outputs out/lbc_flyer_feat_1080x1350.png and out/lbc_flyer_feat_1080x1920.png.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
FLYER = Image.open(HERE / "lbc_flyer.png").convert("RGB")  # 1080x1350
NAME, TAGLINE = "ARTEM MASHKOV", "WINNER DECIDED BY AUDIENCE"
ANTON = str(Path.home() / ".fonts/Anton-Regular.ttf")

# Flyer regions (px, from the 1080x1350 original).
TOP_END, BOTTOM_START = 395, 1000
PRELIM_BOX = (160, 435, 935, 500)
SIGN_BOX = (48, 512, 1048, 950)  # board + hooks + orange shadow
HOOKS_X = (130, 952)             # hook centres, flyer coords
HOOK_Y = 592
TEXT_RED, TEXT_CREAM = (176, 18, 38), (247, 214, 160)
STRING = (0, 0, 0)
STRING_RIM = (164, 94, 29)  # orange edge on the original strings


def _clean():
    """Flyer with the two original hanging strings painted out.

    Planks run vertically, so the columns just beside a string are the best patch for it.
    """
    im = FLYER.copy()
    for x0, x1, y0 in ((122, 140, 358), (946, 964, 250)):  # start under the logo circle / #LBCFF
        w = x1 - x0
        im.paste(FLYER.crop((x0 - w, y0, x0, 600)), (x0, y0))
    return im


CLEAN = _clean()


def _erase_hashtag(im):
    """Paint #LBCFF out with mirrored planks from just below it (same columns, so no seam)."""
    band = im.crop((600, 252, 1000, 300))
    patch = Image.new("RGB", (400, 120))
    for i, y in enumerate(range(0, 120, band.height)):
        patch.paste(band if i % 2 else band.transpose(Image.FLIP_TOP_BOTTOM), (0, 120 - y - band.height))
    im.paste(patch, (600, 135))


_erase_hashtag(CLEAN)
HEADER_BOTTOM = 300  # festival name ends here; right-hand string hangs from it


def festival_name(canvas):
    d = ImageDraw.Draw(canvas)
    outlined(d, (735, 92), "LAUGHING BUDDHA", 84, anchor="ma")
    outlined(d, (735, 192), "COMEDY FESTIVAL", 84, anchor="ma")


def _mirror_tile(band, h, from_bottom=False):
    """Stack band / flipped band so every joint is continuous (planks run vertically)."""
    tiles = [band, band.transpose(Image.FLIP_TOP_BOTTOM)]
    out = Image.new("RGB", (1080, h))
    y, i = 0, 0
    while y < h:
        t = tiles[i % 2]
        out.paste(t, (0, h - y - t.height) if from_bottom else (0, y))
        y += t.height
        i += 1
    return out


def wood(h, blend_at=None):
    """Plank fill for the gap between the flyer's top band (ends 395) and bottom band (starts 1000).

    Top half continues the clean rows right under the logo; bottom half continues the rows right
    above the address, so both joints are seamless. They crossfade at blend_at.
    """
    top = _mirror_tile(CLEAN.crop((0, TOP_END, 1080, 436)), h)
    bot = _mirror_tile(CLEAN.crop((0, 955, 1080, BOTTOM_START)), h, from_bottom=True)
    blend_at = blend_at or h // 2
    ramp = np.clip((np.arange(h) - (blend_at - 60)) / 120, 0, 1).astype(np.float32)
    a = np.repeat(ramp[:, None], 1080, axis=1)
    mix = np.array(top, np.float32) * (1 - a[..., None]) + np.array(bot, np.float32) * a[..., None]
    return Image.fromarray(mix.astype(np.uint8))


def text_only(im):
    """Keep the flyer's red/cream lettering, drop the wood behind it."""
    a = np.array(im.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 120) & (r - g > 70)
    cream = (r > 200) & (g > 150) & (r - b > 30)
    m = Image.fromarray(((red | cream) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def circle_bottom(x, cx=232, cy=218, r=172):
    """Lowest y of the LBC logo circle at column x, so strings start under it, not across it."""
    dx = abs(x - cx)
    return cy + int((r * r - dx * dx) ** 0.5) if dx < r else 0


def cutout():
    rgb = Image.open(HERE / "headshot.jpg").convert("RGB")
    a = np.load(HERE / "headshot_alpha.npy").squeeze()
    a = np.clip((a - 0.35) / 0.4, 0, 1)                    # tighten the soft dark halo
    m = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im = rgb.copy()
    im.putalpha(m)
    return im.crop((70, 225, 710, 960))                    # head to belt, both hands


def fade_bottom(im, px):
    a = np.array(im.getchannel("A")).astype(np.float32)
    h = a.shape[0]
    ramp = np.ones(h, np.float32)
    ramp[h - px:] = np.linspace(1, 0, px)
    im.putalpha(Image.fromarray((a * ramp[:, None]).astype(np.uint8)))
    return im


def shadow(im, blur=18, offset=(10, 14), alpha=0.55):
    a = im.getchannel("A").point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a)
    pad = blur * 3
    big = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.paste(sh, (pad, pad))
    return big.filter(ImageFilter.GaussianBlur(blur)), (offset[0] - pad, offset[1] - pad)


def outlined(draw, xy, text, size, anchor="la"):
    f = ImageFont.truetype(ANTON, size)
    draw.text(xy, text, font=f, fill=TEXT_RED, stroke_width=max(3, size // 16), stroke_fill=TEXT_CREAM, anchor=anchor)


def place_sign(canvas, scale, x, y, string_tops):
    sign = FLYER.crop(SIGN_BOX)
    sign = sign.resize((round(sign.width * scale), round(sign.height * scale)), Image.LANCZOS)
    # Mask out the wood around the board so only the board + its shadow land on the new planks.
    mask = Image.new("L", sign.size, 0)
    ImageDraw.Draw(mask).rectangle((0, round(5 * scale), sign.width, sign.height), fill=255)
    d = ImageDraw.Draw(canvas)
    for hx, top in zip(HOOKS_X, string_tops):
        cx = x + round((hx - SIGN_BOX[0]) * scale)
        if top == "logo":
            top = circle_bottom(cx) - 4
        bottom = y + round((HOOK_Y - SIGN_BOX[1]) * scale)
        d.line((cx, top, cx, bottom), fill=STRING_RIM, width=max(6, round(15 * scale)))
        d.line((cx, top, cx, bottom), fill=STRING, width=max(3, round(4 * scale)))
    canvas.paste(sign, (x, y), mask)
    prelim = FLYER.crop(PRELIM_BOX)
    prelim = prelim.resize((round(prelim.width * scale), round(prelim.height * scale)), Image.LANCZOS)
    return prelim


def paste_prelim(canvas, prelim, cx, y):
    t = text_only(prelim)
    canvas.paste(t, (cx - t.width // 2, y), t)


def person(canvas, h, x, y, fade):
    p = cutout()
    p = p.resize((round(p.width * h / p.height), h), Image.LANCZOS)
    p = fade_bottom(p, fade)
    sh, (ox, oy) = shadow(p)
    canvas.paste(sh, (x + ox, y + oy), sh)
    canvas.paste(p, (x, y), p)
    return p.size


def feed():
    c = CLEAN.copy()
    c.paste(wood(BOTTOM_START - TOP_END), (0, TOP_END))
    c = c.convert("RGBA")
    s, sx, sy = 0.55, 46, 590
    prelim = place_sign(c, s, sx, sy, string_tops=("logo", HEADER_BOTTOM))
    person(c, 600, 1080 - 515, 412, fade=90)
    d = ImageDraw.Draw(c)
    outlined(d, (sx + 8, 870), NAME, 66)
    outlined(d, (sx + 10, 950), TAGLINE, 32)
    festival_name(c)
    return c.convert("RGB")


def story():
    mid = 1920 - (1350 - BOTTOM_START) - TOP_END
    c = Image.new("RGB", (1080, 1920))
    c.paste(CLEAN.crop((0, 0, 1080, TOP_END)), (0, 0))
    c.paste(wood(mid, blend_at=mid - 300), (0, TOP_END))
    c.paste(CLEAN.crop((0, BOTTOM_START, 1080, 1350)), (0, TOP_END + mid))
    c = c.convert("RGBA")
    s, sx, sy = 0.82, 90, 1180
    prelim = place_sign(c, s, sx, sy, string_tops=("logo", HEADER_BOTTOM))
    person(c, 730, 1080 // 2 - 317, 290, fade=120)
    d = ImageDraw.Draw(c)
    outlined(d, (540, 960), NAME, 96, anchor="ma")
    outlined(d, (540, 1082), TAGLINE, 44, anchor="ma")
    festival_name(c)
    return c.convert("RGB")


if __name__ == "__main__":
    feed().save(OUT / "lbc_flyer_feat_1080x1350.png")
    story().save(OUT / "lbc_flyer_feat_1080x1920.png")
    print("ok")
