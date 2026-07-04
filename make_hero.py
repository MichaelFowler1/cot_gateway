#!/usr/bin/env python3
"""
Generate docs/hero.png - the README image.

Everything shown is produced by the real pipeline code: track positions come
from fakegen's walk parameters in config.py, colors from affiliation.py's
policy, and the XML panel is the literal output of cot.make_cot_event().

Run (from the repo root):  .venv\\Scripts\\python make_hero.py
"""
import os
import sys
import xml.dom.minidom

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

# import the package by its directory name from the parent folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cot_gateway import config
from cot_gateway.affiliation import affiliation_for
from cot_gateway.cot import Track, make_cot_event
from cot_gateway.fakegen import _DEMO_CLASSES

BG, PANEL, INK, DIM = "#070b12", "#0b1220", "#d7e2f0", "#6b7d95"
AFF_COLOR = {"f": "#3fa7ff", "h": "#ff4d4d", "u": "#ffd23f"}
AFF_NAME = {"f": "FRIENDLY", "h": "HOSTILE", "u": "UNKNOWN"}

# --- replay fakegen's exact walk for N ticks ---
TICKS = 9
n = config.FAKE_TRACK_COUNT
lats = [[config.FAKE_START_LAT] for _ in range(n)]
lons = [[config.FAKE_START_LON + i * config.FAKE_TRACK_SPACING_LON] for i in range(n)]
for _ in range(TICKS):
    for i in range(n):
        lats[i].append(lats[i][-1] + config.FAKE_STEP_LAT)
        lons[i].append(lons[i][-1] + config.FAKE_STEP_LON)

tracks = [
    Track(track_id=f"fake-{i}", lat=lats[i][-1], lon=lons[i][-1],
          class_name=_DEMO_CLASSES[i % len(_DEMO_CLASSES)], confidence=0.9)
    for i in range(n)
]

# --- real CoT XML from the real serializer ---
xml_raw = make_cot_event(tracks[1])          # the hostile drone
xml_pretty = xml.dom.minidom.parseString(xml_raw).toprettyxml(indent="  ")


def _wrap(line, width=58):
    """Wrap long attribute lines at spaces, continuing with a hanging indent."""
    out = []
    indent = (len(line) - len(line.lstrip())) * " "
    while len(line) > width:
        cut = line.rfind(" ", 0, width)
        if cut <= len(indent):
            break
        out.append(line[:cut])
        line = indent + "    " + line[cut + 1:]
    out.append(line)
    return out


xml_lines = []
for l in xml_pretty.splitlines():
    if l.strip():
        xml_lines += _wrap(l)
xml_pretty = "\n".join(xml_lines[:24])

# --- figure ---
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})
fig = plt.figure(figsize=(13, 7), facecolor=BG)
fig.text(0.05, 0.945, "COT_GATEWAY  ·  SENSOR TRACKS  →  TAK COMMON OPERATING PICTURE",
         fontsize=15.5, fontweight="bold")
fig.text(0.05, 0.897, "detections  →  affiliation policy (ROE + confidence floor)  →  "
                      "CoT 2.0 XML  →  pytak TCP  →  TAK server  →  ATAK / WinTAK / iTAK",
         fontsize=10, color=DIM)

# ---- left: TAK-style map ----
axm = fig.add_axes([0.05, 0.06, 0.52, 0.76], facecolor=PANEL)
axm.set_title("live tracks on the TAK map (fakegen replay)", fontsize=10,
              color=DIM, loc="left", pad=8)
for s in axm.spines.values():
    s.set_edgecolor("#1b2740")
axm.grid(color="#16233b", linewidth=0.8)
axm.tick_params(colors=DIM, labelsize=7)
axm.set_xlabel("longitude", fontsize=8, color=DIM)
axm.set_ylabel("latitude", fontsize=8, color=DIM)
axm.ticklabel_format(useOffset=False)
axm.xaxis.set_major_formatter(lambda v, _: f"{v:.4f}")
axm.yaxis.set_major_formatter(lambda v, _: f"{v:.4f}")

for i, tr in enumerate(tracks):
    aff = affiliation_for(tr.class_name, tr.confidence)
    col = AFF_COLOR[aff]
    # motion trail
    axm.plot(lons[i], lats[i], color=col, alpha=0.35, linewidth=1.5)
    axm.scatter(lons[i][:-1], lats[i][:-1], s=8, color=col, alpha=0.35)
    # current position: 2525-flavored marker
    marker = {"f": "s", "h": "D", "u": "o"}[aff]
    axm.scatter([tr.lon], [tr.lat], s=210, marker=marker, facecolor=col,
                edgecolor="white", linewidth=1.4, zorder=5)
    # stagger the labels so the three tracks don't overprint each other
    dy = (28, -2, -32)[i % 3]
    axm.annotate(f"cvgw-{tr.track_id}   [{AFF_NAME[aff]}]\n"
                 f"{tr.class_name}  conf {tr.confidence:.2f}",
                 (tr.lon, tr.lat), textcoords="offset points", xytext=(16, dy),
                 fontsize=8, color=col, fontweight="bold")

axm.margins(x=0.42, y=0.18)

# ---- right: the real CoT XML ----
axx = fig.add_axes([0.60, 0.06, 0.355, 0.76], facecolor=PANEL)
axx.set_title("actual output of cot.make_cot_event()  -  one event",
              fontsize=10, color=DIM, loc="left", pad=8)
axx.set_xticks([]); axx.set_yticks([])
for s in axx.spines.values():
    s.set_edgecolor("#1b2740")
axx.text(0.04, 0.97, xml_pretty, transform=axx.transAxes, va="top",
         fontsize=7.6, family="monospace", color="#9fd0ff", linespacing=1.45)
axx.text(0.04, 0.06,
         'type "a-h-G" = hostile ground track\n'
         "stable UID moves the icon in place;\n"
         f"stale = now + {config.STALE_SECONDS}s drops dead tracks",
         transform=axx.transAxes, fontsize=8.2, color=DIM, style="italic")

os.makedirs("docs", exist_ok=True)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "hero.png")
fig.savefig(out, dpi=140, facecolor=BG)
print(f"[+] wrote {out}")
