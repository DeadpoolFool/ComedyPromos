"""Sat Nov 7 2026 double: IG story (1080x1920) for The Stand + The LMAO Show (LIC).

Usage: python3 build.py
Show facts: Comedy Workbook Shows tab + Artem's calendar (checked 2026-11-07).
Times are SEATING (showtime minus 30 min), per the README rule.
Two different shows in one day, so Artem's own theme (like a mini tour).
"""
import glob
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
CHROME = (glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-*/headless_shell")
          + glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))[0]
LOGO = (HERE.parent / "brand" / "logo_silhouette.png").as_uri()
PHOTO = (HERE / "stage_stand.jpg").as_uri()  # The Stand 3/21/26, neon STAND sign, full body, mic up

RED, CREAM, BG = "#df2731", "#efe6d2", "#0b0b0b"

# (seating, venue headline, address line, cta)
SHOWS = [
    ("4:30", "THE STAND", "116 E 16th St · Union Sq", "TICKETS ↓"),
    ("6:30", "THE LMAO SHOW", "The Local Hostel · 1302 44th Ave, LIC", ""),
]

CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:{BG}; color:{CREAM}; overflow:hidden; }}
.page {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:{BG}; }}
.logo {{ position:absolute; top:0; right:0; width:300px; height:230px; background:{RED};
        clip-path:polygon(22% 0, 100% 0, 100% 100%, 0 100%); z-index:3; }}
.logo img {{ position:absolute; width:195px; left:88px; top:20px; filter:brightness(0); }}
.kicker {{ font-family:'Space Mono'; font-weight:700; color:{RED}; letter-spacing:8px; font-size:26px; }}
.head {{ font-family:'Anton'; font-size:104px; line-height:.95; }}
.photo {{ position:absolute; left:160px; top:330px; width:760px; height:950px; }}
.photo img {{ width:760px; height:950px; display:block; }}
.fade-b {{ position:absolute; left:0; right:0; bottom:0; height:260px;
          background:linear-gradient(to bottom, rgba(11,11,11,0), {BG}); }}
.fade-t {{ position:absolute; left:0; right:0; top:0; height:70px;
          background:linear-gradient(to top, rgba(11,11,11,0), {BG}); }}
.fade-l, .fade-r {{ position:absolute; top:0; bottom:0; width:90px; }}
.fade-l {{ left:0; background:linear-gradient(to right, {BG}, rgba(11,11,11,0)); }}
.fade-r {{ right:0; background:linear-gradient(to left, {BG}, rgba(11,11,11,0)); }}
.rows {{ position:absolute; left:64px; right:64px; top:1225px; }}
.row {{ display:flex; align-items:center; border-top:2px solid #2a2a2a; padding:22px 0; }}
.row:last-child {{ border-bottom:2px solid #2a2a2a; }}
.t {{ flex:0 0 300px; }}
.t .lbl {{ font-family:'Space Mono'; font-weight:700; color:{RED}; letter-spacing:4px; font-size:22px; }}
.t .tm {{ font-family:'Anton'; font-size:104px; line-height:1; }}
.t .tm small {{ font-size:48px; margin-left:8px; }}
.v .name {{ font-family:'Anton'; font-size:58px; line-height:1.05; }}
.v .addr {{ font-family:'Barlow Condensed'; font-weight:500; color:#bdb5a3; font-size:32px; }}
.v .cta {{ font-family:'Space Mono'; font-weight:700; font-size:22px; color:{CREAM};
          background:{RED}; display:inline-block; padding:2px 12px; margin-top:8px; letter-spacing:2px; }}
.handle {{ position:absolute; right:64px; top:1770px; font-family:'Space Mono'; font-weight:700;
          letter-spacing:4px; font-size:26px; }}
.handle b {{ color:{RED}; }}
"""


def rows():
    out = []
    for seat, name, addr, cta in SHOWS:
        cta_html = f'<div class="cta">{cta}</div>' if cta else ""
        out.append(f"""
<div class="row">
  <div class="t"><div class="lbl">SEATING</div><div class="tm">{seat}<small>PM</small></div></div>
  <div class="v"><div class="name">{name}</div><div class="addr">{addr}</div>{cta_html}</div>
</div>""")
    return "".join(out)


def story():
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class="page">
  <div class="logo"><img src="{LOGO}"></div>
  <div style="position:absolute;left:64px;top:70px">
    <div class="kicker">TODAY · NOV 7</div>
    <div class="head" style="margin-top:12px">BACK TO BACK<br>ON A SAT</div>
  </div>
  <div class="photo"><img src="{PHOTO}"><div class="fade-t"></div><div class="fade-l"></div><div class="fade-r"></div><div class="fade-b"></div></div>
  <div class="rows">{rows()}</div>
  <div class="handle"><b>@</b>ARTEMISFUNNY</div>
</div></body></html>"""


def render(name, html, w=1080, h=1920):
    src = HERE / f"_{name}.html"
    src.write_text(html)
    dst = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={w},{h}", f"--screenshot={dst}", "--virtual-time-budget=3000", src.as_uri()],
                   check=True, capture_output=True)
    src.unlink()
    print(dst)


if __name__ == "__main__":
    render("nov7_story_1080x1920", story())
