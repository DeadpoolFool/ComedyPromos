"""LBC Fall Fest promo: story + feed stills, and a 15s vertical reel.

Usage: python3 build.py   (uses ../brand/logo_silhouette.png; a logo.png here overrides it)
"""
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"

RED, CREAM = "#df2731", "#efe6d2"

# Show facts, all straight from the confirmation email. Nothing invented.
SHOW = {
    "event": "LBC FALL FEST",
    "round": "PRELIMINARY ROUND",
    "date": "SAT OCT 17",
    "time": "6:30PM",  # Artem's standing rule: show seating (showtime 7PM minus 30 min), labelled SEATING
    "venue": "THE BUDDHA ROOM",
    "addr": "410 8TH AVE, 2ND FLOOR",
    "prize": "$1,500 + 10 SHOW SPOTS",
}

LOGO = next((p for p in (HERE / "logo.png", HERE.parent / "brand" / "logo_silhouette.png") if p.exists()), None)


def prep_logo():
    """Silhouette on light bg -> cream figure on transparent, per brand rule."""
    if not LOGO:
        return None
    import numpy as np
    im = Image.open(LOGO).convert("RGBA")
    a = np.array(im)
    lum = a[..., :3].mean(axis=2)
    a[..., 3] = np.where(lum > 200, 0, a[..., 3])  # keep the PNG's own transparency
    a[..., 0], a[..., 1], a[..., 2] = 0xEF, 0xE6, 0xD2
    p = HERE / "logo_cream.png"
    Image.fromarray(a).save(p)
    return p


def prep_photos():
    src = Image.open(HERE / "stage.jpg").convert("RGB")
    w, h = src.size
    # Story: head to knees, mic and STAND sign in frame.
    src.crop((0, 0, w, int(w * 1150 / 1080))).resize((1080, 1150), Image.LANCZOS).save(HERE / "story_photo.jpg", quality=92)
    # Feed: head to waist.
    src.crop((0, 260, 950, 929)).resize((1080, 760), Image.LANCZOS).save(HERE / "feed_photo.jpg", quality=92)
    # Reel background: cover 1080x1920, anchored left so the performer stays in.
    s = 1920 / h
    big = src.resize((round(w * s), 1920), Image.LANCZOS)
    big.crop((0, 0, 1080, 1920)).save(HERE / "reel_bg.jpg", quality=92)


BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background: transparent; color:{CREAM}; }}
.anton {{ font-family:'Anton'; text-transform:uppercase; letter-spacing:.5px; }}
.mono {{ font-family:'Space Mono'; font-weight:700; text-transform:uppercase; }}
.barlow {{ font-family:'Barlow Condensed'; font-weight:500; }}
.red {{ color:{RED}; }}
.chip {{ display:inline-block; background:{RED}; color:{CREAM}; padding:8px 18px; }}
.logo {{ position:absolute; top:40px; right:44px; width:170px; }}
"""


def logo_tag(logo):
    return f'<img class="logo" src="file://{logo}">' if logo else ""


def story_html(logo):
    return f"""<html><head><style>{BASE_CSS}
body {{ width:1080px; height:1920px; background:#000; position:relative; overflow:hidden; }}
.photo {{ position:absolute; top:0; left:0; width:1080px; height:1150px; }}
.fade {{ position:absolute; top:700px; left:0; width:1080px; height:460px;
         background:linear-gradient(to bottom, rgba(0,0,0,0), #000 92%); }}
.info {{ position:absolute; top:880px; left:64px; right:64px; }}
.kicker {{ font-size:30px; letter-spacing:2px; }}
h1 {{ font-size:170px; line-height:.92; margin-top:24px; }}
.sub {{ font-size:46px; line-height:1.15; margin-top:24px; max-width:900px; }}
.date {{ font-size:104px; line-height:1; margin-top:36px; }}
.venue {{ font-size:32px; line-height:1.45; margin-top:14px; letter-spacing:1px; }}
.cta {{ position:absolute; left:0; right:0; top:1712px; height:104px; background:{RED};
        display:flex; align-items:center; justify-content:center; font-size:40px; letter-spacing:2px; }}
.foot {{ position:absolute; left:64px; right:64px; top:1846px; display:flex; justify-content:space-between;
         font-size:26px; letter-spacing:1px; }}
</style></head><body>
<img class="photo" src="file://{HERE}/story_photo.jpg"><div class="fade"></div>{logo_tag(logo)}
<div class="info">
  <div class="mono kicker"><span class="chip">{SHOW['event']}</span></div>
  <h1 class="anton">Your laugh<br><span class="red">is my vote.</span></h1>
  <div class="barlow sub">The audience picks who wins {SHOW['prize'].lower()}.<br>I need you there, and I need you loud.</div>
  <div class="anton date">{SHOW['date']} · <span class="red">{SHOW['time']}</span></div>
  <div class="mono venue"><span class="red">SEATING {SHOW['time']}</span> · {SHOW['venue']}<br>{SHOW['addr']} · MIDTOWN</div>
</div>
<div class="mono cta">GET TICKETS → LINK IN BIO</div>
<div class="mono foot"><span>@ARTEMISFUNNY</span><span class="red">@LAUGHINGBUDDHACOMEDY</span></div>
</body></html>"""


def feed_html(logo):
    return f"""<html><head><style>{BASE_CSS}
body {{ width:1080px; height:1350px; background:#000; position:relative; overflow:hidden; }}
.photo {{ position:absolute; top:0; left:0; width:1080px; height:760px; }}
.fade {{ position:absolute; top:440px; left:0; width:1080px; height:330px;
         background:linear-gradient(to bottom, rgba(0,0,0,0), #000 92%); }}
.info {{ position:absolute; top:560px; left:56px; right:56px; }}
.kicker {{ font-size:26px; letter-spacing:2px; }}
h1 {{ font-size:150px; line-height:.92; margin-top:20px; }}
.row {{ margin-top:26px; }}
.date {{ font-size:84px; line-height:1; white-space:nowrap; }}
.venue {{ font-size:25px; line-height:1.45; margin-top:12px; letter-spacing:1px; white-space:nowrap; }}
.prize {{ font-size:40px; margin-top:22px; }}
.cta {{ position:absolute; left:0; right:0; top:1196px; height:88px; background:{RED};
        display:flex; align-items:center; justify-content:center; font-size:34px; letter-spacing:2px; }}
.foot {{ position:absolute; left:56px; right:56px; top:1302px; display:flex; justify-content:space-between;
         font-size:22px; letter-spacing:1px; }}
</style></head><body>
<img class="photo" src="file://{HERE}/feed_photo.jpg"><div class="fade"></div>{logo_tag(logo)}
<div class="info">
  <div class="mono kicker"><span class="chip">{SHOW['event']}</span></div>
  <h1 class="anton">Your laugh<br><span class="red">is my vote.</span></h1>
  <div class="barlow prize">Audience-judged. {SHOW['prize'].title().replace('Spots','spots').replace('Show','show')} on the line.</div>
  <div class="row">
    <div class="anton date">{SHOW['date']} · <span class="red">{SHOW['time']}</span></div>
    <div class="mono venue"><span class="red">SEATING {SHOW['time']}</span> · {SHOW['venue']} · {SHOW['addr']}</div>
  </div>
</div>
<div class="mono cta">GET TICKETS → LINK IN BIO</div>
<div class="mono foot"><span>@ARTEMISFUNNY</span><span class="red">#LBCFF</span></div>
</body></html>"""


# Reel beats: (seconds, overlay html body). Transparent PNGs laid over the zooming photo.
def reel_beats(logo):
    grad = ('<div style="position:absolute;left:0;top:900px;width:1080px;height:1020px;'
            'background:linear-gradient(to bottom,rgba(0,0,0,0),rgba(0,0,0,.92) 55%)"></div>')
    lower = "position:absolute;left:64px;right:64px;top:1240px;"
    beats = [
        (3.2, f'{grad}<div style="{lower}"><div class="mono" style="font-size:30px;letter-spacing:2px"><span class="chip">OCT 17 · NYC</span></div>'
              f'<div class="anton" style="font-size:150px;line-height:.92;margin-top:24px">I\'m in a<br><span class="red">comedy<br>competition.</span></div></div>'),
        (3.4, f'{grad}<div style="{lower}"><div class="anton" style="font-size:150px;line-height:.92;margin-top:70px">No judges.<br><span class="red">You\'re the<br>judges.</span></div></div>'),
        (3.4, f'{grad}<div style="{lower}"><div class="barlow" style="font-size:56px">The crowd picks who wins</div>'
              f'<div class="anton" style="font-size:190px;line-height:.92;margin-top:10px" ><span class="red">$1,500</span></div>'
              f'<div class="anton" style="font-size:110px;line-height:.95">+ 10 show spots</div></div>'),
    ]
    card = f"""<div style="position:absolute;left:0;top:0;width:1080px;height:1920px;background:#000"></div>{logo_tag(logo)}
<div style="position:absolute;left:64px;right:64px;top:420px">
  <div class="mono" style="font-size:30px;letter-spacing:2px"><span class="chip">{SHOW['event']}</span></div>
  <div class="anton" style="font-size:170px;line-height:.92;margin-top:40px">Come<br><span class="red">be loud.</span></div>
  <div class="anton" style="font-size:120px;line-height:1;margin-top:70px">{SHOW['date']}</div>
  <div class="anton red" style="font-size:120px;line-height:1">{SHOW['time']}</div>
  <div class="mono" style="font-size:36px;line-height:1.5;margin-top:40px">{SHOW['venue']}<br>{SHOW['addr']}</div>
</div>
<div class="mono" style="position:absolute;left:0;right:0;top:1640px;height:110px;background:{RED};display:flex;align-items:center;justify-content:center;font-size:42px;letter-spacing:2px">TICKETS → LINK IN BIO</div>
<div class="mono" style="position:absolute;left:64px;right:64px;top:1800px;font-size:28px;text-align:center">@ARTEMISFUNNY</div>"""
    beats.append((5.0, card))
    return beats


def page(body, w, h):
    return f'<html><head><style>{BASE_CSS} body{{width:{w}px;height:{h}px;position:relative;overflow:hidden}}</style></head><body>{body}</body></html>'


def render(html, png, w, h):
    src = HERE / (png.stem + ".html")
    src.write_text(html)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{h}", "--default-background-color=00000000",
                    f"--screenshot={png}", f"file://{src}"], check=True, capture_output=True)


def build_reel(overlays):
    """Slow push-in on the photo for the hype beats, crossfade overlays, end on the info card."""
    fps = 30
    total = sum(d for d, _ in overlays)
    photo_t = total - overlays[-1][0]
    frames = round(total * fps)
    inputs = ["-loop", "1", "-framerate", str(fps), "-t", f"{total}", "-i", str(HERE / "reel_bg.jpg")]
    for _, p in overlays:
        inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total}", "-i", str(p)]
    inputs += ["-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=44100:cl=stereo"]
    # Upscale before zoompan so the push-in doesn't jitter.
    f = [f"[0:v]scale=2160:3840,zoompan=z='min(1+on*0.0009,1.25)':x='iw/2-(iw/zoom/2)-on*0.6':y='ih/3-(ih/zoom/3)':"
         f"d={frames}:s=1080x1920:fps={fps},setsar=1[bg]"]
    t, last = 0.0, "bg"
    for i, (d, _) in enumerate(overlays, start=1):
        fade = 0.35
        fin = f"fade=t=in:st={max(t - fade / 2, 0):.2f}:d={fade}:alpha=1"
        fout = "" if i == len(overlays) else f",fade=t=out:st={t + d - fade / 2:.2f}:d={fade}:alpha=1"
        f.append(f"[{i}:v]format=rgba,{fin}{fout}[o{i}]")
        f.append(f"[{last}][o{i}]overlay=0:0:format=auto[v{i}]")
        last = f"v{i}"
        t += d
    f.append(f"[{last}]format=yuv420p[out]")
    out = OUT / "lbc_reel_1080x1920.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(f),
                    "-map", "[out]", "-map", f"{len(overlays) + 1}:a", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "18", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    return out, photo_t


if __name__ == "__main__":
    logo = prep_logo()
    prep_photos()
    render(story_html(logo), OUT / "lbc_story_1080x1920.png", 1080, 1920)
    render(feed_html(logo), OUT / "lbc_feed_1080x1350.png", 1080, 1350)
    overlays = []
    for i, (d, body) in enumerate(reel_beats(logo), start=1):
        p = HERE / f"beat{i}.png"
        render(page(body, 1080, 1920), p, 1080, 1920)
        overlays.append((d, p))
    out, _ = build_reel(overlays)
    print("logo:", logo or "none (drop logo.png here and rerun)")
    print("done:", *sorted(OUT.iterdir()), sep="\n  ")
