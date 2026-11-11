"""Fri Nov 13 2026 bonus show, The Buddha Room: IG story (1080x1920).

Usage: python3 build.py
Show facts: LBC booking confirmation email (screenshot, 2026-11-11).
Seating = showtime minus 30 min, per the README rule. No show flyer exists,
so this uses Artem's own theme. MC Jin headlines (Artem, 2026-11-11). Background: Artem with MC Jin (from Artem's
own story; the old @iammcjin sticker is covered by the info panel, re-add
mentions in the IG app so they're tappable).
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
PHOTO = (HERE / "photo_jin.jpg").as_uri()  # 1166x2100, rounded screenshot corners trimmed

RED, CREAM, BG = "#df2731", "#efe6d2", "#0b0b0b"

CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:{BG}; color:{CREAM}; overflow:hidden; }}
.page {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:{BG}; }}
.bg {{ position:absolute; left:0; top:-10px; width:1080px; height:1945px; object-fit:cover; }}
.shade-t {{ position:absolute; left:0; right:0; top:0; height:520px;
           background:linear-gradient(to bottom, rgba(11,11,11,.92) 0%, rgba(11,11,11,.75) 45%, rgba(11,11,11,0) 100%); }}
.shade-b {{ position:absolute; left:0; right:0; top:1080px; bottom:0;
           background:linear-gradient(to bottom, rgba(11,11,11,0) 0px, rgba(11,11,11,.85) 260px, {BG} 330px); }}
.logo {{ position:absolute; top:0; right:0; width:300px; height:230px; background:{RED};
        clip-path:polygon(22% 0, 100% 0, 100% 100%, 0 100%); z-index:3; }}
.logo img {{ position:absolute; width:195px; left:88px; top:20px; filter:brightness(0); }}
.top {{ position:absolute; left:64px; top:70px; }}
.kicker {{ font-family:'Space Mono'; font-weight:700; color:{RED}; letter-spacing:8px; font-size:26px; }}
.head {{ font-family:'Anton'; font-size:138px; line-height:.95; margin-top:10px; text-shadow:0 4px 24px rgba(0,0,0,.5); }}
.hl {{ font-family:'Anton'; font-size:64px; line-height:1; margin-top:14px; text-shadow:0 2px 14px rgba(0,0,0,.7); }}
.hl span {{ font-family:'Space Mono'; font-weight:700; font-size:22px; letter-spacing:4px; background:{RED};
           color:{CREAM}; padding:4px 12px; margin-right:16px; vertical-align:middle; text-shadow:none; }}
.sub {{ font-family:'Barlow Condensed'; font-weight:600; font-size:38px; color:{CREAM}; margin-top:8px;
       text-shadow:0 2px 12px rgba(0,0,0,.8); }}
.info {{ position:absolute; left:64px; right:64px; top:1430px; }}
.row {{ display:flex; align-items:center; border-top:2px solid #2a2a2a; border-bottom:2px solid #2a2a2a; padding:24px 0; }}
.t {{ flex:0 0 300px; }}
.t .lbl {{ font-family:'Space Mono'; font-weight:700; color:{RED}; letter-spacing:4px; font-size:22px; }}
.t .tm {{ font-family:'Anton'; font-size:110px; line-height:1; }}
.t .tm small {{ font-size:50px; margin-left:8px; }}
.v .name {{ font-family:'Anton'; font-size:62px; line-height:1.05; }}
.v .addr {{ font-family:'Barlow Condensed'; font-weight:500; color:#bdb5a3; font-size:34px; }}
.v .cta {{ font-family:'Space Mono'; font-weight:700; font-size:22px; color:{CREAM};
          background:{RED}; display:inline-block; padding:2px 12px; margin-top:10px; letter-spacing:2px; }}
.handle {{ position:absolute; right:64px; top:1800px; font-family:'Space Mono'; font-weight:700;
          letter-spacing:4px; font-size:26px; }}
.handle b {{ color:{RED}; }}
"""


def story():
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class="page">
  <img class="bg" src="{PHOTO}">
  <div class="shade-t"></div><div class="shade-b"></div>
  <div class="logo"><img src="{LOGO}"></div>
  <div class="top">
    <div class="kicker">FRI · NOV 13</div>
    <div class="head">BONUS SHOW</div>
    <div class="hl"><span>HEADLINER</span>MC JIN</div>
    <div class="sub">I'm the one pointing at me.</div>
  </div>
  <div class="info">
    <div class="row">
      <div class="t"><div class="lbl">SEATING</div><div class="tm">7:30<small>PM</small></div></div>
      <div class="v"><div class="name">THE BUDDHA ROOM</div>
        <div class="addr">410 8th Ave, 2nd Fl · Laughing Buddha</div>
        <div class="cta">TICKETS ↓</div></div>
    </div>
  </div>
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
    render("nov13_story_1080x1920", story())
