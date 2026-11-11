"""Step 1: tidy the Open-Meteo extract into data/town_years.csv (one row per town and Christmas) and data/towns.csv
(one row per town: nation, point, grid point, elevation, distance to the sea). Checks completeness and the null pattern."""
import pandas as pd, numpy as np
from shapely.geometry import shape, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer
from common import *

D = jload(f"{RAW}/white_christmas.json")
assert D["vars"] == ["snowfall_sum_cm_24_25_26", "snow_depth_max_m_24_25_26", "temperature_2m_max_C_24_25_26", "grid_lat", "grid_lon", "grid_elevation_m"]
towns = [(n, float(a), float(b)) for n, a, b in D["towns"]]
assert len(towns) == 116 and len({t[0] for t in towns}) == 116
rows = []
for y in range(Y0, Y1 + 1):
    for n, la, lo in towns:
        v = D["data"][f"{y}|{n}"]
        sf, sd, tx = v[0], v[1], v[2]
        assert len(sf) == len(sd) == len(tx) == 3 and None not in sf and None not in tx
        if y < YL0: assert sd == [None, None, None]
        else: assert None not in sd, (y, n)
        rows.append(dict(town=n, year=y, sf24=sf[0], sf25=sf[1], sf26=sf[2], sd24=sd[0], sd25=sd[1], sd26=sd[2],
                         tx24=tx[0], tx25=tx[1], tx26=tx[2], glat=v[3], glon=v[4], elev=v[5]))
assert len(D["data"]) == len(rows) == 116 * (Y1 - Y0 + 1)
TY = pd.DataFrame(rows)
g = TY.groupby("town")[["glat", "glon", "elev"]].nunique()
assert (g == 1).all().all(), "grid point varies by year"
# nation by point in polygon (LAD 2023 code prefix)
L = jload(f"{GEO}/lad23_bgc.geojson")
lads = [(f["properties"]["LAD23CD"][0], shape(f["geometry"])) for f in L["features"]]
from shapely.strtree import STRtree
tree = STRtree([s for _, s in lads])
nat = {}
for n, la, lo in towns:
    p = Point(lo, la)
    hit = [lads[i][0] for i in tree.query(p) if lads[i][1].contains(p)]
    if not hit:  # on the coast just outside the generalised boundary: nearest district
        hit = [lads[int(tree.nearest(p))][0]]
    nat[n] = NATIONS[hit[0]]
# distance to the sea: boundary of (UK districts + island of Ireland), in British National Grid km
C = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
ire = [shape(f["geometry"]) for f in C["features"] if f["properties"].get("ADMIN") == "Ireland"]
assert len(ire) == 1
landm = unary_union([s for _, s in lads] + ire).buffer(0)
bng = Transformer.from_crs(4326, 27700, always_xy=True).transform
landb = transform(bng, landm).boundary
T = pd.DataFrame([dict(town=n, lat=la, lon=lo) for n, la, lo in towns])
T["nation"] = T.town.map(nat)
T = T.merge(TY.groupby("town")[["glat", "glon", "elev"]].first().reset_index(), on="town")
T["coast_km"] = [round(landb.distance(Point(*bng(lo, la))) / 1000, 2) for la, lo in zip(T.lat, T.lon)]
T["grid_off_km"] = [round(math.hypot(*(np.subtract(bng(a, b), bng(c, d)))) / 1000, 2) for a, b, c, d in zip(T.lon, T.lat, T.glon, T.glat)]
T.to_csv(f"{DATA}/towns.csv", index=False)
TY.drop(columns=["glat", "glon", "elev"]).to_csv(f"{DATA}/town_years.csv", index=False)
print(T.nation.value_counts().to_dict())
print(T.describe()[["elev", "coast_km", "grid_off_km"]].round(1))
print(T.sort_values("elev", ascending=False).head(8)[["town", "elev", "nation"]].to_string())
print(T.sort_values("coast_km", ascending=False).head(5)[["town", "coast_km"]].to_string())
