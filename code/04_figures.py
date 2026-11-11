"""Step 4: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px), the paper (release/paper/f_*.pdf,
vector) and header.png (1200 x 630). Light paper background; snow in blues (pale = rarely, deep = often), warm red for the
Met Office's own record and for temperature."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm, ListedColormap
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path
import numpy as np, pandas as pd
from PIL import Image
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union
import shapely
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
SERIF = "Source Serif 4"; DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name(); MONO = "IBM Plex Mono"
PAPER, INK, MUT, RULE = "#F7F5EF", "#1F2A36", "#5E6B78", "#D8DDE2"
SNOW = ["#E6EEF4", "#B9D2E6", "#7FAED3", "#3F7FB6", "#1D4F86", "#0E2D57"]
CM = LinearSegmentedColormap.from_list("snow", ["#DCE7EF", "#9EC2DE", "#4F8DC3", "#1D4F86", "#0B2447"])
RED, GOLD, GREY = "#B3412F", "#C98A2B", "#A3A9AF"
C_NONE, C_FALL, C_LIE, C_BOTH, C_UNK, C_UNKF = "#EEF0F2", "#9FC3E0", "#4C86BE", "#0E2D57", "#F4F1EA", "#C9D7E3"
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": MUT, "axes.labelcolor": INK, "xtick.color": MUT,
                     "ytick.color": MUT, "axes.facecolor": PAPER, "figure.facecolor": PAPER, "axes.unicode_minus": False,
                     "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
R = jload(f"{DATA}/results.json"); S = R["sample"]
T = pd.read_csv(f"{DATA}/town_odds.csv"); A = pd.read_csv(f"{DATA}/annual.csv"); SITE = jload(f"{DATA}/site.json")
BLOG, PAPD = f"{REL}/blog", f"{REL}/paper"
for d_ in (BLOG, PAPD): os.makedirs(d_, exist_ok=True)
SRC = ("Data: Open-Meteo Historical Weather API (ERA5 and ERA5-Land reanalysis, Copernicus/ECMWF), CC BY 4.0\n"
       "maps.tristanhotham.com/white-christmas")


def out(fig, name, page=True, blog=True, paper=True):
    if paper: fig.savefig(f"{PAPD}/f_{name}.pdf", facecolor=fig.get_facecolor())
    fig.savefig(f"{SCR}/{name}.png", dpi=220, facecolor=fig.get_facecolor()); plt.close(fig)
    im = Image.open(f"{SCR}/{name}.png").convert("RGB")
    if page:
        w = min(1500, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=85, optimize=True)
    if blog: im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    os.remove(f"{SCR}/{name}.png")


def title(fig, t, sub, y=0.965, x=0.04):
    fig.text(x, y, t, fontsize=21, fontweight="bold", family=DISP, color=INK, va="top")
    fig.text(x, y - 0.05, sub, fontsize=12, color=MUT, va="top", linespacing=1.35)


def foot(fig, s=SRC):
    fig.text(0.04, 0.012, s, fontsize=8.3, family=MONO, color=MUT, va="bottom", linespacing=1.4)


# ---------- outlines (BNG)
tr = Transformer.from_crs(4326, 27700, always_xy=True)
L = jload(f"{GEO}/lad23_bgc.geojson")
uk = unary_union([shape(f["geometry"]) for f in L["features"]]).buffer(0).simplify(0.004)
C = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
irl = [shape(f["geometry"]) for f in C["features"] if f["properties"].get("ADMIN") == "Ireland"][0]
fra = [shape(f["geometry"]) for f in C["features"] if f["properties"].get("ADMIN") == "France"][0]
fra = fra.intersection(shapely.box(-6, 47.5, 3, 51.5))
ukp = shapely.transform(uk, lambda c: np.c_[tr.transform(c[:, 0], c[:, 1])])
irp = shapely.transform(irl, lambda c: np.c_[tr.transform(c[:, 0], c[:, 1])])
frp = shapely.transform(fra, lambda c: np.c_[tr.transform(c[:, 0], c[:, 1])])


def patch(ax, g, **kw):
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon": continue
        v, c = [], []
        for ring in [p.exterior] + list(p.interiors):
            cs = np.asarray(ring.coords); v += cs.tolist(); c += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(v, c), **kw))


EXT = (-60000, 680000, -10000, 1230000)


def basemap(ax, ext=EXT):
    ax.set_facecolor("#E7EEF2")
    patch(ax, irp, fc="#F1EFEA", ec="#BDC3C8", lw=0.4); patch(ax, frp, fc="#F1EFEA", ec="#BDC3C8", lw=0.4)
    patch(ax, ukp, fc="#FFFFFF", ec="#8D98A3", lw=0.55)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)


T["x"], T["y"] = tr.transform(T.lon.values, T.lat.values)
LBL_W = ["Fort William", "Glasgow", "Belfast", "Londonderry", "Lancaster", "Aberystwyth", "Cardiff", "Plymouth"]
LBL_E = ["Lerwick", "Aviemore", "Inverness", "Aberdeen", "Edinburgh", "Hawick", "Newcastle", "Buxton", "Norwich", "London"]


def labels(ax, fig, side_w, side_e, xw, xe, fs=10.5, minsep=26000, val="lie_pc"):
    """Labels in the sea margins, joined to their towns by straight leaders; ordered by height on each side so leaders
    never cross."""
    for names, xl, ha in ((side_w, xw, "right"), (side_e, xe, "left")):
        d = T[T.town.isin(names)].sort_values("y")
        ys = []
        for y in d.y:
            y2 = y if not ys else max(y, ys[-1] + minsep); ys.append(y2)
        for (r, y2) in zip(d.itertuples(), ys):
            ax.plot([r.x, xl + (6000 if ha == "right" else -6000)], [r.y, y2], color="#7A8794", lw=0.6, zorder=2.5)
            ax.text(xl, y2, f"{r.town} {getattr(r, val):.0f}%", ha=ha, va="center", fontsize=fs, color=INK, path_effects=HALO, zorder=5)


# ---------- 1. map of lying-snow odds
fig = plt.figure(figsize=(11, 13.2))
title(fig, "How often is there snow on the ground on Christmas Day?", f"Share of Christmas Days {S['lie_first']} to {S['last']} with more than 1 cm of snow lying, {S['towns']} UK towns (reanalysis)", y=0.975)
ax = fig.add_axes([0.02, 0.05, 0.96, 0.86]); basemap(ax, (-330000, 980000, -10000, 1230000))
d = T.sort_values("lie_pc")
sc = ax.scatter(d.x, d.y, c=d.lie_pc, cmap=CM, vmin=0, vmax=30, s=70, lw=0.8, edgecolor="white", zorder=3)
labels(ax, fig, LBL_W, LBL_E, -60000, 690000)
rb = T[T.town == "Bournemouth"].iloc[0]  # below, in the Channel: a label on the east side would sit on France
ax.plot([rb.x, rb.x], [rb.y, 47000], color="#7A8794", lw=0.6, zorder=2.5)
ax.text(rb.x, 36000, f"Bournemouth {rb.lie_pc:.0f}%", ha="center", va="center", fontsize=10.5, color=INK, path_effects=HALO, zorder=5)
cax = fig.add_axes([0.06, 0.835, 0.25, 0.014])
cb = fig.colorbar(sc, cax=cax, orientation="horizontal", ticks=[0, 10, 20, 30], extend="max"); cb.outline.set_visible(False)
cb.ax.set_xticklabels(["0%", "10%", "20%", "30%+"], fontsize=9.5)
fig.text(0.06, 0.855, "Christmas Days with snow lying,\n1950 to 2025", fontsize=11, color=INK, va="bottom", fontweight="bold")
fig.text(0.06, 0.805, f"Each dot is a town; the value is for\nthe reanalysis cell (about 9 to 11 km)\naround it. Highland towns sit in cells\nthat include hills, so their odds are\nhigher than in the town itself.\n\nAll {S['towns']} towns: {R['overall']['lie']['pc']:.1f}% of Christmas\nDays, about 1 in {R['overall']['lie']['one_in']}.", fontsize=9.8, color=MUT, va="top")
foot(fig); out(fig, "map")

# ---------- 2. calendar strips (barcode)
order = T.sort_values("lat", ascending=False)
yrs = np.arange(Y0, Y1 + 1)
code_col = {"0": C_NONE, "1": C_FALL, "2": C_LIE, "3": C_BOTH, "4": C_UNK, "5": C_UNKF}
S_by = {t["n"]: t["s"] for t in SITE["t"]}
fig = plt.figure(figsize=(11, 17))
title(fig, "Every Christmas Day since 1940 in 116 towns", "One row per town, north at the top; one square per year", y=0.988)
ax = fig.add_axes([0.2, 0.08, 0.77, 0.81]); ax.set_facecolor(PAPER)
for i, t in enumerate(order.town):
    s = S_by[t]
    for j, c in enumerate(s):
        if c in "04": continue
        ax.add_patch(Rectangle((yrs[j] - 0.45, i - 0.42), 0.9, 0.84, fc=code_col[c], lw=0))
ax.add_patch(Rectangle((Y0 - 0.5, -0.5), Y1 - Y0 + 1, len(order), fc=C_NONE, lw=0, zorder=0))
ax.add_patch(Rectangle((Y0 - 0.5, -0.5), YL0 - Y0, len(order), fc=C_UNK, lw=0, zorder=0))
ax.set_ylim(len(order) - 0.5, -0.5); ax.set_xlim(Y0 - 0.6, Y1 + 0.6)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order.town, fontsize=6.4)
ax.tick_params(axis="y", length=0, pad=2); ax.set_xticks(range(1940, 2030, 10)); ax.tick_params(axis="x", labelsize=10)
for s in ax.spines.values(): s.set_visible(False)
for y in R["met_office"]["widespread"]:
    ax.annotate("", (y, -0.6), (y, -2.6), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2), annotation_clip=False)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(fc=C_BOTH, label="snow fell and lay"), Patch(fc=C_LIE, label="snow lying (more than 1 cm)"), Patch(fc=C_FALL, label="snow fell, none lying"),
                    Patch(fc=C_UNKF, label="snow fell (1940s: no lying-snow data)"), Patch(fc=C_NONE, ec="#D5D9DD", label="no snow")],
           loc="lower left", bbox_to_anchor=(0.2, 0.012), ncol=3, frameon=False, fontsize=9.5)
fig.text(0.2, 0.918, "Red arrows: the four Christmases since 1960 when the Met Office's stations found snow lying widely (1981, 1995, 2009, 2010)", fontsize=9.5, color=RED)
fig.text(0.97, 0.012, "Open-Meteo (ERA5, ERA5-Land), CC BY 4.0 · maps.tristanhotham.com/white-christmas", fontsize=7.5, family=MONO, color=MUT, ha="right")
out(fig, "strip")

# ---------- 3. annual series
fig = plt.figure(figsize=(11, 9))
title(fig, "Snowy Christmases come in a few big years", f"Share of the {S['towns']} towns with snow lying (top) or falling (middle) on Christmas Day; Christmas Day maximum temperature (bottom)", y=0.975)
a1 = fig.add_axes([0.08, 0.63, 0.88, 0.25]); a2 = fig.add_axes([0.08, 0.36, 0.88, 0.2]); a3 = fig.add_axes([0.08, 0.09, 0.88, 0.2])
AL = A[A.year >= YL0]
cols = [RED if y in R["met_office"]["widespread"] else "#3F7FB6" for y in AL.year]
a1.bar(AL.year, AL.lie, color=cols, width=0.8)
for y in R["met_office"]["widespread"]:
    v = float(AL[AL.year == y].lie.iloc[0]); a1.text(y, v + 2, str(y), ha="center", fontsize=9.5, color=RED, path_effects=HALO)
a1.set_ylim(0, 95); a1.set_xlim(Y0 - 1, Y1 + 1); a1.set_ylabel("% of towns, lying")
a1.text(1941, 60, "lying snow:\nno data\nbefore 1950", fontsize=9.5, color=MUT)
a1.text(1951, 88, "Red: the Met Office's four widespread lying-snow Christmases since 1960", fontsize=9.5, color=RED)
a2.bar(A.year, A.fall, color="#7FAED3", width=0.8); a2.set_xlim(Y0 - 1, Y1 + 1); a2.set_ylabel("% of towns, falling"); a2.set_ylim(0, 80)
for y, v in R["annual"]["fall_top"][:3]:
    a2.text(y, v + 2, str(y), ha="center", fontsize=9.5, color=INK, path_effects=HALO)
a3.plot(A.year, A.tx25, color=RED, lw=1.2, marker="o", ms=2.5)
mk = R["TEMP_1950"]["mk"]; yy = np.array([1950, 2025]); mid = A[A.year >= 1950].tx25.median(); ymid = A[A.year >= 1950].year.median()
a3.plot(yy, mid + mk["sen_pp_dec"] / 10 * (yy - ymid), color=INK, lw=1.2, ls=(0, (4, 2)))
a3.set_xlim(Y0 - 1, Y1 + 1); a3.set_ylabel("°C, mean of towns")
a3.text(1951, A.tx25.max() - 0.3, f"dashed: Sen slope since 1950, {mk['sen_pp_dec']:+.1f} °C a decade", fontsize=9.5, color=INK, va="top", path_effects=HALO)
foot(fig); out(fig, "annual")

# ---------- 4. decades
D = R["decade"]; labs = list(D)
fig = plt.figure(figsize=(11, 6.4))
title(fig, "Christmas Days with snow, decade by decade", f"Share of town-years across {S['towns']} towns (the 2020s are 2020 to 2025; lying-snow data start in 1950)", y=0.965)
ax = fig.add_axes([0.08, 0.13, 0.9, 0.66]); x = np.arange(len(labs)); w = 0.27
for k, (o, c, l) in enumerate((("fall", "#9FC3E0", "snow falling"), ("lie", "#3F7FB6", "snow lying (more than 1 cm)"), ("both", "#0E2D57", "both"))):
    v = [D[d][o] if D[d][o] is not None else np.nan for d in labs]
    ax.bar(x + (k - 1) * w, v, w * 0.95, color=c, label=l)
    for xi, vi in zip(x + (k - 1) * w, v):
        if not np.isnan(vi): ax.text(xi, vi + 0.3, f"{vi:.0f}", ha="center", fontsize=8.5, color=MUT)
ax.set_xticks(x); ax.set_xticklabels(labs); ax.set_ylabel("% of town Christmases"); ax.legend(frameon=False, fontsize=10.5, loc="upper right")
foot(fig); out(fig, "decade")

# ---------- 5. geography
fig = plt.figure(figsize=(11, 6.6))
title(fig, "Height and latitude", f"Each dot is a town: share of Christmas Days {S['lie_first']} to {S['last']} with snow lying, against its height and latitude", y=0.965)
b1 = fig.add_axes([0.07, 0.19, 0.42, 0.61]); b2 = fig.add_axes([0.56, 0.19, 0.42, 0.61])
s1 = b1.scatter(T.elev, T.lie_pc, c=T.lat, cmap="viridis_r", s=34, lw=0.5, edgecolor="white")
b1.set_xlabel("height of the town (m)"); b1.set_ylabel("% of Christmas Days with snow lying")
b2.scatter(T.lat, T.lie_pc, c=T.elev.clip(0, 250), cmap="cividis", s=34, lw=0.5, edgecolor="white")
b2.set_xlabel("latitude (°N)")
# labels placed in empty space, joined by thin leaders drawn under the dots
def lab(ax, x, y, tx, ty, t, ha="left"):
    if (tx, ty) != (x, y): ax.plot([x, tx], [y, ty], color="#9AA5B1", lw=0.6, zorder=1)
    ax.text(tx, ty, t, fontsize=9, color=INK, ha=ha, va="center", path_effects=HALO, zorder=4)
r_ = lambda t: T[T.town == t].iloc[0]
for t, tx, ty, ha in (("Aviemore", 225, 69.7, "left"), ("Fort William", 26, 61.8, "left"), ("Buxton", 300, 27, "center"),
                      ("Brecon", 170, 30, "left"), ("Greenock", 40, 32, "left"), ("London", 100, -4.5, "left"), ("Bournemouth", 20, -4.5, "left")):
    r = r_(t); lab(b1, r.elev, r.lie_pc, tx if ha != "left" or t not in ("Aviemore", "Fort William") else r.elev + 10, ty, t, ha)
for t, tx, ty, ha in (("Aviemore", 57.4, 69.7, "left"), ("Fort William", 57.0, 61.8, "left"), ("Buxton", 52.6, 38, "center"),
                      ("Brecon", 50.4, 31, "left"), ("London", 50.4, 25, "left"), ("Greenock", 55.0, 42, "center"),
                      ("Bournemouth", 51.2, -4.5, "left"), ("Lerwick", 59.6, 16, "center")):
    r = r_(t); lab(b2, r.lat, r.lie_pc, tx, ty, t, ha)
for b in (b1, b2): b.set_ylim(-7, 74); b.set_yticks([0, 10, 20, 30, 40, 50, 60, 70])
b2.set_xlim(49.8, 60.8)
s1.set_zorder(3); b2.collections[0].set_zorder(3)
fig.text(0.07, 0.83, "Left: colour = latitude (yellow south, purple north)", fontsize=9.5, color=MUT)
fig.text(0.56, 0.83, "Right: colour = height (dark low, yellow 250 m or more)", fontsize=9.5, color=MUT)
foot(fig); out(fig, "geo")

# ---------- 6. robustness forest
fig = plt.figure(figsize=(11, 7.6))
title(fig, "Is the decline real? Every planned check", "Odds ratio per decade for snow on Christmas Day (below 1 = getting rarer), with 95% intervals", y=0.97)
for k, (o, nm) in enumerate((("lie", "Snow lying, from 1950"), ("fall", "Snow falling, from 1940"))):
    ax = fig.add_axes([0.27 + k * 0.37, 0.1, 0.3, 0.72]); rows = [r for r in R["robust"] if r["outcome"] == o]
    for i, r in enumerate(rows):
        c = RED if r["hi"] < 1 else ("#3F7FB6" if r["group"] != "Main" else INK)
        ax.plot([r["lo"], r["hi"]], [i, i], color=c, lw=2); ax.plot(r["OR"], i, "o", color=c, ms=6 if r["group"] != "Main" else 8)
    ax.axvline(1, color=INK, lw=0.8); ax.set_xscale("log"); ax.set_xticks([0.5, 0.7, 1, 1.4]); ax.set_xticklabels(["0.5", "0.7", "1", "1.4"]); ax.minorticks_off()
    ax.set_xlim(0.45, 1.6); ax.set_ylim(len(rows) - 0.5, -0.7); ax.set_title(nm, fontsize=12, color=INK, loc="left")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r["label"] for r in rows] if k == 0 else [], fontsize=9.5)
fig.text(0.27, 0.035, "Red: interval excludes 1. Black: the main model (logit, town fixed effects, errors clustered by year).", fontsize=9.5, color=MUT)
out(fig, "robust")

# ---------- 7. validation (paper and page only)
fig = plt.figure(figsize=(11, 5.4))
title(fig, "Does the reanalysis match the Met Office's stations?", "Published station shares against the share of the 116 towns, for the years the Met Office reports", y=0.965)
v1 = fig.add_axes([0.08, 0.14, 0.4, 0.62]); v2 = fig.add_axes([0.57, 0.14, 0.4, 0.62])
for ax, key, nm in ((v1, "falling", "snow falling"), (v2, "lying", "snow lying")):
    pr = R["V2"][f"{key}_pairs"]
    xs = [v[0] for v in pr.values()]; ys = [v[1] for v in pr.values()]
    ax.scatter(xs, ys, color="#3F7FB6", s=40, zorder=3)
    for yname, (a_, b_) in pr.items():
        if key == "lying" and a_ < 10: continue
        ax.annotate(yname, (a_, b_), (5, 4), textcoords="offset points", fontsize=9, color=INK, path_effects=HALO)
    m = max(xs + ys) * 1.1; ax.plot([0, m], [0, m], color=GREY, lw=0.8, ls=(0, (3, 2))); ax.set_xlim(-2, m); ax.set_ylim(-2, m)
    ax.set_xlabel(f"Met Office: % of stations, {nm}"); ax.set_ylabel(f"reanalysis: % of towns, {nm}")
    rho = R["V2"][key]["rho"]; ax.text(0.97, 0.05, f"Spearman rho {rho:.2f}, {R['V2'][key + '_n']} years" + ("\n2020 to 2023: all near zero" if key == "lying" else ""), transform=ax.transAxes, fontsize=10, color=INK, va="bottom", ha="right")
out(fig, "valid", blog=False)

# ---------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100)
ax = fig.add_axes([0.6, 0.02, 0.38, 0.96]); basemap(ax, (-90000, 680000, -10000, 1230000))
ax.scatter(d.x, d.y, c=d.lie_pc, cmap=CM, vmin=0, vmax=30, s=34, lw=0.6, edgecolor="white", zorder=3)
fig.text(0.05, 0.915, "DATA STUDY · 2026", family=MONO, fontsize=12, color=MUT)
fig.text(0.05, 0.5, "What are the odds\nof a white Christmas\nwhere you live?", family=DISP, fontsize=40, fontweight="bold", color=INK, va="bottom", linespacing=0.95)
fig.text(0.05, 0.43, f"Every Christmas Day from {S['first']} to {S['last']} in {S['towns']} UK towns,\nfrom weather reanalysis", fontsize=15, color=INK, va="top")
fig.text(0.05, 0.25, f"Snow lying on about 1 Christmas Day in {R['overall']['lie']['one_in']}.\nIn Bournemouth: never.", fontsize=18, color="#1D4F86", fontweight="bold", va="top")
fig.text(0.05, 0.06, "Dr Tristan Hotham · maps.tristanhotham.com/white-christmas", family=MONO, fontsize=10.5, color=MUT)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER); plt.close(fig)
assert Image.open(f"{ROOT}/header.png").size == (1200, 630)
assert R["towns"]["Bournemouth"]["lie_k"] == 0
print("figures done")
