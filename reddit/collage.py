"""Reddit collage (r/dataisbeautiful style), light background, 2700 x 2025 px: map of how often snow lay on Christmas Day
in 116 UK towns (labels on the sea, leaders ordered so they never cross), the share of towns with lying snow each
Christmas since 1950, and headline numbers. Run after code/03_results.py:  python3 reddit/collage.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np, pandas as pd, shapely
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "IBMPlexMono-Regular.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name()
plt.rcParams.update({"font.family": "Source Serif 4", "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#5E6B78", "xtick.color": "#5E6B78", "ytick.color": "#5E6B78"})
PAPER, INK, MUT, RED, BLUE = "#F8F7F3", "#1F2A36", "#5E6B78", "#B3412F", "#1D4F86"
CM = LinearSegmentedColormap.from_list("snow", ["#DCE7EF", "#9EC2DE", "#4F8DC3", "#1D4F86", "#0B2447"])
HALO = [pe.withStroke(linewidth=4, foreground="#E7EEF2")]
R = jload(f"{DATA}/results.json"); S = R["sample"]
T = pd.read_csv(f"{DATA}/town_odds.csv"); A = pd.read_csv(f"{DATA}/annual.csv")
tr = Transformer.from_crs(4326, 27700, always_xy=True)
L = jload(f"{GEO}/lad23_bgc.geojson")
uk = unary_union([shape(f["geometry"]) for f in L["features"]]).buffer(0).simplify(0.004)
C = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
irl = [shape(f["geometry"]) for f in C["features"] if f["properties"].get("ADMIN") == "Ireland"][0]
fra = [shape(f["geometry"]) for f in C["features"] if f["properties"].get("ADMIN") == "France"][0].intersection(shapely.box(-6, 47.5, 3, 51.5))
P = lambda g: shapely.transform(g, lambda c: np.c_[tr.transform(c[:, 0], c[:, 1])])


def patch(ax, g, **kw):
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon": continue
        v, c = [], []
        for ring in [p.exterior] + list(p.interiors):
            cs = np.asarray(ring.coords); v += cs.tolist(); c += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(v, c), **kw))


fig = plt.figure(figsize=(13.5, 10.125), dpi=200); fig.patch.set_facecolor(PAPER)
fig.text(0.03, 0.958, "What are the odds of a white Christmas where you live?", family=DISP, fontsize=29, fontweight="bold", color=INK, va="top")
fig.text(0.03, 0.9, f"Every Christmas Day from {S['first']} to {S['last']} in {S['towns']} UK towns, from weather reanalysis (ERA5, ERA5-Land).\n"
         "Snow lying = more than 1 cm on the ground on 25 December.", fontsize=13, color=MUT, va="top")
ax = fig.add_axes([0.0, 0.07, 0.5, 0.78]); ax.set_facecolor("#E7EEF2")
patch(ax, P(irl), fc="#F1EFEA", ec="#BDC3C8", lw=0.4); patch(ax, P(fra), fc="#F1EFEA", ec="#BDC3C8", lw=0.4)
patch(ax, P(uk), fc="#FFFFFF", ec="#8D98A3", lw=0.5)
ax.set_xlim(-250000, 860000); ax.set_ylim(-10000, 1230000); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
T["x"], T["y"] = tr.transform(T.lon.values, T.lat.values)
d = T.sort_values("lie_pc")
sc = ax.scatter(d.x, d.y, c=d.lie_pc, cmap=CM, vmin=0, vmax=30, s=46, lw=0.7, edgecolor="white", zorder=3)
for names, xl, ha in ((["Fort William", "Glasgow", "Belfast", "Cardiff", "Plymouth"], -40000, "right"),
                      (["Aviemore", "Inverness", "Edinburgh", "Buxton", "London"], 660000, "left")):
    dd = T[T.town.isin(names)].sort_values("y"); ys = []
    for y in dd.y: ys.append(y if not ys else max(y, ys[-1] + 40000))
    for r, y2 in zip(dd.itertuples(), ys):
        ax.plot([r.x, xl + (6000 if ha == "right" else -6000)], [r.y, y2], color="#7A8794", lw=0.7, zorder=2.5)
        ax.text(xl, y2, f"{r.town} {r.lie_pc:.0f}%", ha=ha, va="center", fontsize=11, color=INK, path_effects=HALO, zorder=5)
rb = T[T.town == "Bournemouth"].iloc[0]  # labelled below, in the Channel (a label on the right would sit on France)
ax.plot([rb.x, rb.x], [rb.y, 47000], color="#7A8794", lw=0.7, zorder=2.5)
ax.text(rb.x, 36000, f"Bournemouth {rb.lie_pc:.0f}%", ha="center", va="center", fontsize=11, color=INK, path_effects=HALO, zorder=5)
cax = fig.add_axes([0.03, 0.8, 0.17, 0.012])
cb = fig.colorbar(sc, cax=cax, orientation="horizontal", ticks=[0, 10, 20, 30], extend="max"); cb.outline.set_visible(False)
cb.ax.set_xticklabels(["0%", "10%", "20%", "30%+"], fontsize=10)
fig.text(0.03, 0.818, "Christmas Days with snow lying, 1950 to 2025", fontsize=11.5, fontweight="bold", color=INK)
fig.text(0.03, 0.765, "Highland towns sit in\nreanalysis cells that include\nhills (about 9 to 11 km across),\nso their odds partly reflect\nthe hills around them.", fontsize=10, color=MUT, va="top")
# stat cards
def card(x0, y0, big, txt, col):
    fig.text(x0, y0, big, family=DISP, fontsize=34, fontweight="bold", color=col, va="top")
    fig.text(x0, y0 - 0.065, txt, fontsize=11.8, color=INK, va="top", linespacing=1.3)
card(0.55, 0.83, f"1 in {R['overall']['lie']['one_in']}", f"Christmas Days with snow\nlying, across all {S['towns']} towns", BLUE)
card(0.78, 0.83, "Never", "in Bournemouth,\n1950 to 2025", BLUE)
card(0.55, 0.64, f"{R['towns']['London']['lie_k']} of 76", "Christmases with snow\nlying in London", BLUE)
card(0.78, 0.64, f"+{R['TEMP_1950']['b']:.1f}°C", "a decade: Christmas Day's\ntop temperature since 1950", RED)
# annual bars
a2 = fig.add_axes([0.56, 0.13, 0.41, 0.27]); a2.set_facecolor(PAPER)
AL = A[A.year >= YL0]
cols = [RED if y in MO_WIDESPREAD else "#4F8DC3" for y in AL.year]
a2.bar(AL.year, AL.lie, color=cols, width=0.8)
for y in MO_WIDESPREAD:
    v = float(AL[AL.year == y].lie.iloc[0]); a2.text(y - (1.2 if y == 2009 else 0), v + 2.5, str(y), ha="right" if y == 2009 else "center", fontsize=10, color=RED)
a2.set_ylim(0, 95); a2.set_xlim(1948, 2027); a2.set_yticks([0, 25, 50, 75]); a2.set_yticklabels(["0", "25%", "50%", "75%"], fontsize=10)
a2.tick_params(axis="x", labelsize=10)
fig.text(0.56, 0.44, "Share of the towns with snow lying, each Christmas", fontsize=12.5, fontweight="bold", color=INK)
fig.text(0.56, 0.398, "Red: the Met Office's four widespread snowy Christmases since 1960.\nNo Christmas since 2010 has had snow lying in even one town in ten.", fontsize=10.5, color=MUT)
fig.text(0.03, 0.045, f"Snow lay on {R['halves']['lie']['first']:.1f}% of town Christmases 1950 to 1987 and {R['halves']['lie']['second']:.1f}% 1988 to 2025, but with 2009 and 2010 in the data the planned trend model cannot rule out no change.",
         fontsize=10.5, color=MUT)
fig.text(0.03, 0.018, "Data: Open-Meteo Historical Weather API (ERA5, ERA5-Land; Copernicus/ECMWF), CC BY 4.0; Met Office white Christmas record.  "
         "Dr Tristan Hotham  ·  maps.tristanhotham.com/white-christmas", fontsize=8.0, color=MUT, family="IBM Plex Mono")
out = os.path.join(HERE, "white_christmas_collage.png")
fig.savefig(out, dpi=200, facecolor=PAPER)
print(out)
