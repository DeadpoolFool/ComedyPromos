"""NYC November 2026 run: IG carousel (1080x1080 x3) + story (1080x1920).

Usage: python3 build.py
Show facts come from the Comedy Workbook Shows tab (checked 2026-11-03).
Times are SEATING (showtime minus 30 min), per the README rule.
"""
import glob
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
CHROME = (glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-*/headless_shell") + glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))[0]
LOGO = (HERE.parent / "brand" / "logo_silhouette.png").as_uri()
PHOTO = (HERE / "stage_buddha_95.jpg").as_uri()  # LBC prelim 10/17, Buddha Room sign in frame

RED, CREAM = "#df2731", "#efe6d2"

STAND = ("THE STAND", "116 E 16th St · Union Sq")
NYCC = ("NEW YORK COMEDY CLUB", "236 W 78th St · UWS")
BUDDHA = ("THE BUDDHA ROOM", "410 8th Ave, 2nd Fl")

# (day, date, seating, venue, address, note)
SHOWS = [
    ("THU", "NOV 5", "7:30 PM", "LBC FALL FEST FINAL", "The Buddha Room · 410 8th Ave, 2nd Fl", "final"),
    ("SAT", "NOV 7", "4:30 PM", *STAND, ""),
    ("SAT", "NOV 7", "6:30 PM", "THE LMAO SHOW", "The Local Hostel · 1302 44th Ave, LIC", ""),
    ("SUN", "NOV 8", "7:30 PM", *BUDDHA, ""),
    ("SAT", "NOV 14", "4:30 PM", *STAND, ""),
    ("MON", "NOV 16", "DM ME", "SECRET SHOW", "Pro comics · Location: ask me", "secret"),
    ("SAT", "NOV 21", "4:30 PM", *STAND, ""),
    ("SUN", "NOV 22", "3:30 PM", *NYCC, ""),
    ("SUN", "NOV 22", "DM ME", "SECRET SHOW", "Pro comics · Location: ask me", "secret"),
    ("SAT", "NOV 28", "4:30 PM", *STAND, ""),
    ("SUN", "NOV 29", "3:30 PM", *NYCC, ""),
]

CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:#0b0b0b; color:{CREAM}; overflow:hidden; }}
.page {{ position:relative; overflow:hidden; background:#0b0b0b; }}
.mono {{ font-family:'Space Mono', monospace; }}
.anton {{ font-family:'Anton', sans-serif; font-weight:400; }}
.barlow {{ font-family:'Barlow Condensed', sans-serif; }}
.logo {{ position:absolute; top:0; right:0; background:{RED};
        clip-path:polygon(22% 0, 100% 0, 100% 100%, 0 100%); }}
.logo img {{ position:absolute; filter:brightness(0); }}
.handle {{ position:absolute; font-family:'Space Mono'; font-weight:700; letter-spacing:4px; }}
.handle b {{ color:{RED}; }}
.kicker {{ font-family:'Space Mono'; font-weight:700; color:{RED}; letter-spacing:8px; }}
.row {{ display:flex; align-items:center; border-top:2px solid #2a2a2a; }}
.row:last-child {{ border-bottom:2px solid #2a2a2a; }}
.d {{ flex:0 0 auto; }}
.d .dow {{ font-family:'Space Mono'; font-weight:700; color:{RED}; letter-spacing:3px; }}
.d .dt {{ font-family:'Anton'; line-height:1; }}
.v {{ flex:1 1 auto; min-width:0; }}
.v .name {{ font-family:'Anton'; line-height:1.05; }}
.v .addr {{ font-family:'Barlow Condensed'; font-weight:500; color:#bdb5a3; }}
.s {{ flex:0 0 auto; text-align:right; font-family:'Space Mono'; }}
.s .lbl {{ color:#8d877b; letter-spacing:3px; }}
.s .t {{ font-weight:700; color:{CREAM}; }}
.final .name {{ color:{RED}; }}
.secret .name {{ color:{RED}; letter-spacing:1px; }}
.secret .name::after {{ content:"!"; color:{CREAM}; }}
.secret .t {{ background:{RED}; color:{CREAM}; padding:2px 10px; }}
"""


def logo(w, h, img_w, img_x, img_y):
    return (f'<div class="logo" style="width:{w}px;height:{h}px">'
            f'<img src="{LOGO}" style="width:{img_w}px;left:{img_x}px;top:{img_y}px"></div>')


def rows(shows, dt_px, name_px, addr_px, t_px, pad):
    out = []
    for dow, dt, seat, name, addr, note in shows:
        lbl = "SEATING" if seat[0].isdigit() else "&nbsp;"
        out.append(f"""
<div class="row {note}" style="padding:{pad}px 0">
  <div class="d" style="width:{dt_px * 3.1:.0f}px">
    <div class="dow" style="font-size:{t_px * 0.8:.0f}px">{dow}</div>
    <div class="dt" style="font-size:{dt_px}px">{dt}</div>
  </div>
  <div class="v">
    <div class="name" style="font-size:{name_px}px">{name}</div>
    <div class="addr" style="font-size:{addr_px}px">{addr}</div>
  </div>
  <div class="s">
    <div class="lbl" style="font-size:{t_px * 0.7:.0f}px">{lbl}</div>
    <div class="t" style="font-size:{t_px}px">{seat}</div>
  </div>
</div>""")
    return "".join(out)


def page(w, h, body):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body><div class='page' style='width:{w}px;height:{h}px'>{body}</div></body></html>")


def cover():
    return page(1080, 1080, f"""
{logo(330, 250, 210, 95, 22)}
<div style="position:absolute;left:64px;top:64px">
  <div class="kicker" style="font-size:24px">NYC · NOV 5 – 29</div>
  <div class="anton" style="font-size:148px;line-height:.92;margin-top:18px">ARTEM<br>MASHKOV</div>
  <div class="mono" style="font-size:26px;margin-top:30px;color:#bdb5a3;width:600px;line-height:1.45">
    11 shows in 25 days.<br><span style="color:{CREAM};font-weight:700">Then Switzerland takes me back.</span></div>
</div>
<div style="position:absolute;left:64px;top:620px;width:566px;border:3px solid {CREAM};padding:28px 30px">
  <div class="mono" style="display:inline-block;background:{RED};color:{CREAM};font-weight:700;font-size:20px;letter-spacing:2px;padding:8px 12px;white-space:nowrap">THU · NOV 5 · SEATING 7:30 PM</div>
  <div class="anton" style="font-size:58px;line-height:1;margin-top:18px">LBC FALL FEST FINAL</div>
  <div class="barlow" style="font-size:30px;font-weight:500;color:#bdb5a3;margin-top:8px">The Buddha Room · 410 8th Ave, 2nd Fl</div>
  <div class="mono" style="font-size:22px;font-weight:700;margin-top:10px">Tickets: link in bio</div>
</div>
<img src="{PHOTO}" style="position:absolute;right:0;bottom:0;height:770px">
<div class="handle" style="left:64px;bottom:34px;font-size:26px"><b>@</b>ARTEMISFUNNY</div>
<div class="mono" style="position:absolute;right:28px;bottom:34px;font-size:20px;font-weight:700;background:#0b0b0bcc;padding:4px 10px">ALL DATES →</div>
""")


def list_slide(shows, title, outro=""):
    return page(1080, 1080, f"""
{logo(250, 190, 160, 72, 16)}
<div style="position:absolute;left:64px;top:60px">
  <div class="kicker" style="font-size:22px">ARTEM MASHKOV · NYC</div>
  <div class="anton" style="font-size:92px;line-height:1;margin-top:10px">{title}</div>
</div>
<div style="position:absolute;left:64px;right:64px;top:225px">
  {rows(shows, 48, 42, 26, 27, 15)}
</div>
<div class="handle" style="left:64px;bottom:40px;font-size:24px"><b>@</b>ARTEMISFUNNY</div>
<div class="mono" style="position:absolute;right:64px;bottom:40px;font-size:20px;color:#8d877b">Times are seating.</div>
{outro}
""")


def story():
    return page(1080, 1920, f"""
{logo(300, 230, 195, 88, 20)}
<div style="position:absolute;left:64px;top:150px">
  <div class="kicker" style="font-size:24px">NYC · NOVEMBER</div>
  <div class="anton" style="font-size:140px;line-height:.92;margin-top:14px">ARTEM<br>MASHKOV</div>
</div>
<div style="position:absolute;left:64px;right:64px;top:520px">
  {rows(SHOWS, 44, 38, 24, 25, 14)}
</div>
<div class="mono" style="position:absolute;left:64px;right:64px;top:1700px;font-size:22px;color:#8d877b">Times are seating. Final tickets ↓</div>
<div class="handle" style="right:64px;top:1700px;font-size:22px"><b>@</b>ARTEMISFUNNY</div>
""")


OUTRO = f"""<div style="position:absolute;left:64px;top:850px">
  <div class="mono" style="font-size:22px;font-weight:700;color:{RED};letter-spacing:4px">DEC 4</div>
  <div class="anton" style="font-size:54px;margin-top:4px">DEPORTED TO SWITZERLAND</div>
</div>"""


def render(name, html, w, h):
    src = HERE / f"_{name}.html"
    src.write_text(html)
    dst = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={w},{h}", f"--screenshot={dst}", "--virtual-time-budget=3000", src.as_uri()],
                   check=True, capture_output=True)
    src.unlink()
    print(dst)


if __name__ == "__main__":
    render("nov_carousel_1_1080x1080", cover(), 1080, 1080)
    render("nov_carousel_2_1080x1080", list_slide(SHOWS[:6], "NOV 5 – 16"), 1080, 1080)
    render("nov_carousel_3_1080x1080", list_slide(SHOWS[6:], "NOV 21 – 29", OUTRO), 1080, 1080)
    render("nov_story_1080x1920", story(), 1080, 1920)
