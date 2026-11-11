"""Step 1b (exploratory, added after the plan): how hilly is the reanalysis cell around each town? For each town, the mean
and maximum land height inside the 0.1 x 0.1 degree ERA5-Land cell that contains it (cells centred on multiples of 0.1
degree) and inside the 0.25 degree ERA5 cell, from Mapzen/AWS Terrain Tiles (terrarium encoding, zoom 9). Adds
cell10_mean, cell10_max, cell25_mean and cell_minus_town to data/towns.csv."""
import io, glob
import numpy as np, pandas as pd
from PIL import Image
from common import *

idx = {}
for js in sorted(glob.glob(f"{RAW}/terrarium_z9_pack*.json")):
    for fn, off, ln in json.load(open(js)):
        idx[fn] = (js[:-5] + ".bin", off, ln)
Z = 9; N = 2 ** Z
cache = {}


def tile(x, y):
    k = f"t9_{x}_{y}.png"
    if k not in cache:
        if k not in idx: cache[k] = None
        else:
            b, off, ln = idx[k]
            with open(b, "rb") as f:
                f.seek(off); a = np.asarray(Image.open(io.BytesIO(f.read(ln))).convert("RGB")).astype(float)
            cache[k] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return cache[k]


def heights(lon0, lat0, lon1, lat1, step=0.004):
    lons = np.arange(lon0 + step / 2, lon1, step); lats = np.arange(lat0 + step / 2, lat1, step)
    LO, LA = np.meshgrid(lons, lats)
    fx = (LO + 180) / 360 * N; fy = (1 - np.log(np.tan(np.radians(LA)) + 1 / np.cos(np.radians(LA))) / math.pi) / 2 * N
    tx, ty = fx.astype(int), fy.astype(int); px = ((fx - tx) * 256).astype(int); py = ((fy - ty) * 256).astype(int)
    out = np.full(LO.shape, np.nan)
    for (a, b) in set(zip(tx.ravel(), ty.ravel())):
        t = tile(a, b)
        if t is None: continue
        m = (tx == a) & (ty == b); out[m] = t[py[m], px[m]]
    return out


T = pd.read_csv(f"{DATA}/towns.csv")
r10m, r10x, r25m, miss = [], [], [], 0
for la, lo in zip(T.lat, T.lon):
    c = round(lo / 0.1) * 0.1, round(la / 0.1) * 0.1
    h = heights(c[0] - 0.05, c[1] - 0.05, c[0] + 0.05, c[1] + 0.05); land = h[h > 0]
    if np.isnan(h).all(): miss += 1
    r10m.append(round(float(land.mean()), 1) if land.size else 0.0); r10x.append(round(float(land.max()), 1) if land.size else 0.0)
    c = round(lo / 0.25) * 0.25, round(la / 0.25) * 0.25
    h = heights(c[0] - 0.125, c[1] - 0.125, c[0] + 0.125, c[1] + 0.125, step=0.008); land = h[h > 0]
    r25m.append(round(float(land.mean()), 1) if land.size else 0.0)
assert miss == 0
T["cell10_mean"] = r10m; T["cell10_max"] = r10x; T["cell25_mean"] = r25m
T["cell_minus_town"] = (T.cell10_mean - T.elev).round(1)
T.to_csv(f"{DATA}/towns.csv", index=False)
print(T.sort_values("cell_minus_town", ascending=False).head(10)[["town", "elev", "cell10_mean", "cell10_max", "cell25_mean"]].to_string())
print(T[["elev", "cell10_mean", "cell_minus_town"]].describe().round(0))
