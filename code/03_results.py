"""Step 3: data/results.json (every number quoted anywhere), data/town_odds.csv, data/annual.csv and data/site.json
(the map page data: towns with odds, decade counts and a calendar strip per town)."""
import numpy as np, pandas as pd
from common import *

T = pd.read_csv(f"{DATA}/towns.csv")
Y = pd.read_csv(f"{SCR}/panel.csv")
M = jload(f"{DATA}/models.json")
R = {"title": TITLE, "slug": SLUG, "theme": THEME}
Y["decade"] = (Y.year // 10) * 10
R["sample"] = dict(towns=len(T), first=Y0, last=Y1, years=Y1 - Y0 + 1, town_years=len(Y), lie_first=YL0, lie_years=Y1 - YL0 + 1,
                   lie_town_years=int(Y.lie.notna().sum()), nations=T.nation.value_counts().to_dict(),
                   elev_min=int(T.elev.min()), elev_max=int(T.elev.max()), elev_median=float(T.elev.median()),
                   grid_off_median=float(T.grid_off_km.median()), grid_off_max=float(T.grid_off_km.max()))
assert R["sample"]["town_years"] == 9976 and R["sample"]["lie_town_years"] == 8816


def share(s):
    s = s.dropna(); k, n = int(s.sum()), len(s); lo, hi = wilson(k, n)
    return dict(k=k, n=n, pc=100 * k / n, lo=100 * lo, hi=100 * hi, one_in=one_in(k / n))


R["overall"] = {o: share(Y[o]) for o in ("fall", "lie", "both", "fall07", "lie0", "lie5")}
# per town
rows = []
for t, g in Y.groupby("town"):
    r = dict(town=t)
    for o in ("fall", "lie", "both"):
        s = share(g[o]); r.update({f"{o}_k": s["k"], f"{o}_n": s["n"], f"{o}_pc": round(s["pc"], 2), f"{o}_lo": round(s["lo"], 2), f"{o}_hi": round(s["hi"], 2), f"{o}_one_in": s["one_in"]})
        last = g[g[o] == 1].year.max(); r[f"{o}_last"] = None if pd.isna(last) else int(last)
    for o in ("fall", "lie"):
        for d0, d1 in ((1950, 1987), (1988, 2025)):
            gg = g[(g.year >= d0) & (g.year <= d1)][o]; r[f"{o}_{d0}"] = round(100 * gg.mean(), 2)
    r["tx25_mean"] = round(g.tx25.mean(), 2)
    rows.append(r)
TO = T.merge(pd.DataFrame(rows), on="town")
TO.to_csv(f"{DATA}/town_odds.csv", index=False)
R["towns"] = {r.town: {k: r[k] for k in ("nation", "elev", "fall_pc", "fall_k", "fall_n", "fall_one_in", "fall_last", "lie_pc", "lie_k", "lie_n", "lie_one_in", "lie_last",
                                          "both_pc", "both_k", "both_one_in", "both_last", "lie_lo", "lie_hi", "fall_lo", "fall_hi")} for _, r in TO.iterrows()}
rank = TO.sort_values(["lie_pc", "fall_pc"], ascending=False)
R["top_lie"] = list(rank.town[:10]); R["bottom_lie"] = list(TO.sort_values(["lie_pc", "fall_pc"]).town[:10])
R["top_fall"] = list(TO.sort_values(["fall_pc", "lie_pc"], ascending=False).town[:10])
R["n_towns_lie_never"] = int((TO.lie_k == 0).sum()); R["towns_lie_never"] = list(TO[TO.lie_k == 0].town)
R["n_towns_lie_once"] = int((TO.lie_k == 1).sum())
R["n_towns_both_never"] = int((TO.both_k == 0).sum())
R["n_towns_fall_never"] = int((TO.fall_k == 0).sum())
R["n_towns_lie_ge10"] = int((TO.lie_pc >= 10).sum()); R["n_towns_lie_lt5"] = int((TO.lie_pc < 5).sum())
R["n_towns_lie_since2011"] = int((TO.lie_last > 2010).sum())
R["n_towns_fall_since2011"] = int((TO.fall_last > 2010).sum())
R["median_town"] = dict(lie=float(TO.lie_pc.median()), fall=float(TO.fall_pc.median()), both=float(TO.both_pc.median()))
# nation summaries
R["nation"] = {n: dict(towns=int(len(g)), lie=float(Y[Y.nation == n].lie.mean() * 100), fall=float(Y[Y.nation == n].fall.mean() * 100)) for n, g in TO.groupby("nation")}
# by decade (national share of town-years)
dec = {}
for d, g in Y.groupby("decade"):
    lab = f"{d}s"
    dec[lab] = dict(years=int(g.year.nunique()), fall=float(g.fall.mean() * 100), lie=None if g.lie.isna().all() else float(g.lie.mean() * 100),
                    both=None if g.both.isna().all() else float(g.both.mean() * 100))
R["decade"] = dec
# annual series
A = Y.groupby("year").agg(fall=("fall", "mean"), lie=("lie", "mean"), both=("both", "mean"), tx25=("tx25", "mean"), sf25=("sf25", "mean")).reset_index()
for c in ("fall", "lie", "both"): A[c] = (A[c] * 100).round(3)
A["tx25"] = A.tx25.round(3); A["sf25"] = A.sf25.round(4)
A.to_csv(f"{DATA}/annual.csv", index=False)
AL = A[A.year >= YL0]
R["annual"] = dict(
    lie_top=[[int(y), float(v)] for y, v in AL.sort_values("lie", ascending=False)[["year", "lie"]].head(10).values],
    fall_top=[[int(y), float(v)] for y, v in A.sort_values("fall", ascending=False)[["year", "fall"]].head(10).values],
    lie_zero_years=int((AL.lie == 0).sum()), lie_any_years=int((AL.lie > 0).sum()), lie_ge10_years=int((AL.lie >= 10).sum()),
    lie_ge10_list=[int(y) for y in AL[AL.lie >= 10].year],
    fall_any_years=int((A.fall > 0).sum()), fall_ge10_years=int((A.fall >= 10).sum()),
    lie_ge10_first_half=int(((AL.lie >= 10) & (AL.year <= 1987)).sum()), lie_ge10_second_half=int(((AL.lie >= 10) & (AL.year >= 1988)).sum()),
    lie_zero_first_half=int(((AL.lie == 0) & (AL.year <= 1987)).sum()), lie_zero_second_half=int(((AL.lie == 0) & (AL.year >= 1988)).sum()),
    last_lie_ge10=int(AL[AL.lie >= 10].year.max()), last_fall_ge10=int(A[A.fall >= 10].year.max()))
for y in (1981, 1995, 2009, 2010, 2020, 2021, 2022, 2023, 2024, 2025, 1950, 1968, 1956, 1962):
    r = A[A.year == y].iloc[0]
    R["annual"][f"y{y}"] = dict(fall=float(r.fall), lie=None if pd.isna(r.lie) else float(r.lie), n_lie=None if pd.isna(r.lie) else int(round(r.lie * len(T) / 100)),
                                n_fall=int(round(r.fall * len(T) / 100)))
# first half vs second half (1950 to 1987, 1988 to 2025: 38 years each)
for o in ("fall", "lie", "both"):
    a = Y[(Y.year >= 1950) & (Y.year <= 1987)][o].mean() * 100; b = Y[(Y.year >= 1988)][o].mean() * 100
    R.setdefault("halves", {})[o] = dict(first=float(a), second=float(b))
# models
pc = lambda OR: (OR - 1) * 100
for o in ("lie", "fall", "both", "fall_1950"):
    m = M[f"M1_{o}"]
    R[f"M1_{o}"] = dict(OR=m["OR"], lo=m["lo"], hi=m["hi"], p=m["p"], n=m["n"], n_used=m["n_used"], clusters=m["clusters"], events=m["events"], groups_dropped=m["groups_dropped"],
                        pc=pc(m["OR"]), pc_lo=pc(m["lo"]), pc_hi=pc(m["hi"]), implied={k: 100 * v for k, v in m["implied"].items()})
    if o != "fall_1950":
        R[f"MK_{o}"] = M[f"MK_{o}"]
R["MK_fall_1950"] = M["MK_fall_1950"]
for y0 in ("1940", "1950"):
    R[f"TEMP_{y0}"] = M[f"TEMP_{y0}"]
for k in ("M2_lie", "M2_fall", "M2_both", "M2_lie_year", "X1_lie", "X1_fall"):
    R[k] = M[k]
for k in ("spearman_elev_lie", "spearman_lat_lie", "spearman_elev_fall", "spearman_lat_fall", "V1", "V2", "V3", "LPM_lie", "LPM_fall", "P1_lie", "P1_fall", "P2"):
    R[k] = M[k]
R["robust"] = M["robust"]
rb = {o: [r for r in M["robust"] if r["outcome"] == o and r["group"] != "Main"] for o in ("lie", "fall")}
R["robust_range"] = {o: dict(n_checks=len(v), n_sig=sum(r["hi"] < 1 for r in v), n_below1=sum(r["OR"] < 1 for r in v), min=min(r["OR"] for r in v), max=max(r["OR"] for r in v),
                             sig_labels=[r["label"] for r in v if r["hi"] < 1]) for o, v in rb.items()}
R["robust_no0910_lie"] = [r for r in M["robust"] if r["outcome"] == "lie" and r["label"] == "Without 2009 and 2010"][0]
R["robust_to2016_lie"] = [r for r in M["robust"] if r["outcome"] == "lie" and r["label"].startswith("To 2016")][0]
R["robust_from1960_fall"] = [r for r in M["robust"] if r["outcome"] == "fall" and r["label"] == "From 1960"][0]
R["V1"]["per_million"] = R["V1"]["p_random"] * 1e6
R["decade_tx"] = {f"{d}s": float(g.tx25.mean()) for d, g in Y.groupby("decade")}
R["met_office"] = dict(widespread=MO_WIDESPREAD, lying=MO_LYING, falling=MO_FALL)
R["geo_ref"] = {k: R["towns"][k] for k in ("London", "Birmingham", "Manchester", "Glasgow", "Edinburgh", "Belfast", "Cardiff", "Aviemore", "Buxton", "Bournemouth")}
R["cells"] = dict(median_excess=float(T.cell_minus_town.median()), aviemore_cell=float(T.set_index("town").loc["Aviemore", "cell10_mean"]),
                  fortwilliam_cell=float(T.set_index("town").loc["Fort William", "cell10_mean"]), fortwilliam_cellmax=float(T.set_index("town").loc["Fort William", "cell10_max"]),
                  greenock_cell=float(T.set_index("town").loc["Greenock", "cell10_mean"]), brecon_cell=float(T.set_index("town").loc["Brecon", "cell10_mean"]))
jsave(R, f"{DATA}/results.json", indent=1)

# site.json: towns with strip codes per year: 0 nothing, 1 snow fell only, 2 snow lying only, 3 both; 1940s: 4 (no data on lying, no fall), 5 (fell, lying unknown)
S = {"y0": Y0, "y1": Y1, "yl0": YL0, "t": []}
P = Y.set_index(["town", "year"])
for r in TO.itertuples():
    codes = []
    for y in range(Y0, Y1 + 1):
        q = P.loc[(r.town, y)]
        if y < YL0: codes.append("5" if q.fall else "4")
        else: codes.append(str(int(q.fall) + 2 * int(q.lie)))
    dc = {}
    for d in range(1940, 2030, 10):
        g = Y[(Y.town == r.town) & (Y.decade == d)]
        dc[str(d)] = [int(g.fall.sum()), None if g.lie.isna().all() else int(g.lie.sum()), int(g.year.nunique())]
    S["t"].append(dict(n=r.town, la=r.lat, lo=r.lon, na=r.nation, el=int(r.elev), ce=round(r.cell10_mean), ck=round(r.coast_km, 1),
                       f=round(r.fall_pc, 1), l=round(r.lie_pc, 1), b=round(r.both_pc, 1), fk=r.fall_k, lk=r.lie_k, bk=r.both_k,
                       fl=r.fall_last, ll=r.lie_last, bl=r.both_last, tx=r.tx25_mean, s="".join(codes), d=dc))
jsave(S, f"{DATA}/site.json")
print("results.json", os.path.getsize(f"{DATA}/results.json") // 1024, "KB; site.json", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")
print(json.dumps(R["annual"], indent=0)[:1500]); print(R["halves"], R["robust_range"])
print(R["top_lie"], R["bottom_lie"], R["top_fall"], R["n_towns_lie_never"], R["towns_lie_never"], R["n_towns_lie_since2011"], R["n_towns_fall_since2011"])
print(R["overall"]); print(R["nation"]); print(R["median_town"])
