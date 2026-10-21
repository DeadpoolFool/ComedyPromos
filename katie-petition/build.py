"""Katie Zacharia petition: IG story, 1080x1920, Artem's theme (the petition has no look of its own).

Usage: python3 build.py   (photo.jpg here, logo from ../brand/logo_silhouette.png)
Copy is lifted from the petition page itself, nothing invented:
https://www.change.org/p/reinstate-katie-zacharia-an-appeal-by-comedians
"""
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
LOGO = HERE.parent / "brand" / "logo_silhouette.png"

RED, CREAM = "#df2731", "#efe6d2"


def prep_logo():
    """Silhouette on light bg -> cream figure on transparent, per brand rule."""
    a = np.array(Image.open(LOGO).convert("RGBA"))
    lum = a[..., :3].mean(axis=2)
    a[..., 3] = np.where(lum > 200, 0, a[..., 3])
    a[..., 0], a[..., 1], a[..., 2] = 0xEF, 0xE6, 0xD2
    p = HERE / "logo_cream.png"
    Image.fromarray(a).save(p)
    return p


def prep_photo():
    """Fill the top of the story, black-and-white so it sits in the black/red/cream palette."""
    src = Image.open(HERE / "photo.jpg").convert("RGB")
    w, h = src.size
    s = 1080 / w
    im = src.resize((1080, round(h * s)), Image.LANCZOS).crop((0, 0, 1080, 1160))
    im = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.15).convert("RGB")
    im.save(HERE / "story_photo.jpg", quality=92)


CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1920px; background:#000; color:{CREAM}; position:relative; overflow:hidden; }}
.anton {{ font-family:'Anton'; text-transform:uppercase; letter-spacing:.5px; }}
.mono {{ font-family:'Space Mono'; font-weight:700; text-transform:uppercase; }}
.barlow {{ font-family:'Barlow Condensed'; font-weight:500; }}
.red {{ color:{RED}; }}
.chip {{ display:inline-block; background:{RED}; color:{CREAM}; padding:8px 18px; }}
.logo {{ position:absolute; top:40px; right:44px; width:170px; }}
.photo {{ position:absolute; top:0; left:0; width:1080px; height:1160px; }}
.fade {{ position:absolute; top:720px; left:0; width:1080px; height:450px;
         background:linear-gradient(to bottom, rgba(0,0,0,0), #000 90%); }}
.stamp {{ position:absolute; top:610px; left:64px; transform:rotate(-6deg); border:6px solid {RED};
          color:{RED}; padding:6px 22px 2px; font-size:84px; line-height:1; background:rgba(0,0,0,.35); }}
.info {{ position:absolute; top:930px; left:64px; right:64px; }}
.kicker {{ font-size:30px; letter-spacing:2px; }}
h1 {{ font-size:150px; line-height:.92; margin-top:26px; }}
.sub {{ font-size:52px; line-height:1.12; margin-top:30px; }}
.tag {{ font-size:30px; letter-spacing:1px; margin-top:22px; }}
.sign {{ position:absolute; left:64px; right:64px; top:1530px; font-size:34px; letter-spacing:2px; text-align:center; }}
.band {{ position:absolute; left:140px; right:140px; top:1600px; height:150px; border:3px dashed rgba(239,230,210,.25); }}
.foot {{ position:absolute; left:64px; right:64px; top:1800px; text-align:right; font-size:28px; letter-spacing:1px; }}
"""


def story_html(logo):
    return f"""<html><head><style>{CSS}</style></head><body>
<img class="photo" src="file://{HERE}/story_photo.jpg"><div class="fade"></div>
<img class="logo" src="file://{logo}">
<div class="anton stamp">5 days</div>
<div class="info">
  <div class="mono kicker"><span class="chip">An appeal by comedians</span></div>
  <h1 class="anton">Reinstate<br><span class="red">Katie Zacharia</span></h1>
  <div class="barlow sub">Five days was not a tenure.<br>It was a teaser.</div>
  <div class="mono tag">The Mooch got ten. <span class="red">We demand parity.</span></div>
</div>
<div class="mono sign">Sign the petition &darr;</div>
<div class="band"></div>
<div class="mono foot">@ARTEMISFUNNY</div>
</body></html>"""


def render(html, png):
    src = HERE / (png.stem + ".html")
    src.write_text(html)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1080,1920", f"--screenshot={png}", f"file://{src}"],
                   check=True, capture_output=True)


if __name__ == "__main__":
    prep_photo()
    logo = prep_logo()
    # Two cuts: with the dashed guide (shows where the link sticker goes) and clean for posting.
    html = story_html(logo)
    render(html, OUT / "katie_story_guide_1080x1920.png")
    render(html.replace('<div class="band"></div>', ""), OUT / "katie_story_1080x1920.png")
    print("done:", *sorted(p.name for p in OUT.iterdir()))
