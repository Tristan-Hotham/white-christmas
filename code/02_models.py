"""Step 2: every model in the analysis plan (NOTES.md). Writes data/models.json (all estimates) and data/models.csv.
M1 trend (logit, town FE, SE clustered by year), M1b Mann-Kendall and Sen slope on the national annual share, temperature
trend, M2 geography (logit with year FE, SE clustered two-way by town and year), V1 to V3 validation against the Met Office
record, R1 to R7 robustness, P1 permutation test (2,000 year shuffles), P2 persistence placebo."""
import warnings, time
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy import stats
from common import *
warnings.filterwarnings("ignore")

T = pd.read_csv(f"{DATA}/towns.csv")
Y = pd.read_csv(f"{DATA}/town_years.csv").merge(T[["town", "nation", "lat", "lon", "elev", "coast_km", "cell10_mean"]], on="town")
for d in (24, 25, 26):
    Y[f"fall{d}"] = (Y[f"sf{d}"] > FALL_MIN).astype(int)
    Y[f"lie{d}"] = np.where(Y.year >= YL0, (Y[f"sd{d}"] > LIE_MIN).astype(float), np.nan)
Y["fall"] = Y.fall25; Y["lie"] = Y.lie25
Y["both"] = np.where(Y.year >= YL0, Y.fall * Y.lie, np.nan)
Y["fall07"] = (Y.sf25 >= FALL_ALT).astype(int)
Y["lie0"] = np.where(Y.year >= YL0, (Y.sd25 > LIE_ALT[0]).astype(float), np.nan)
Y["lie5"] = np.where(Y.year >= YL0, (Y.sd25 > LIE_ALT[1]).astype(float), np.nan)
Y["dec"] = (Y.year - 2000) / 10.0
Y.to_csv(f"{SCR}/panel.csv", index=False)
OUT = {}


def fe_logit(d, y, x="dec", fe="town", cl="year", extra=None):
    """Logit of y on x with fixed effects (dummies) for fe; groups with no variation in y are dropped (they carry no
    information about the slope). SE clustered by cl."""
    d = d.dropna(subset=[y]).copy()
    v = d.groupby(fe)[y].agg(["min", "max"]); keep = v.index[v["min"] < v["max"]]
    dd = d[d[fe].isin(keep)]
    X = pd.get_dummies(dd[fe], prefix="fe", drop_first=False).astype(float)
    cols = [x] + (extra or [])
    X = pd.concat([dd[cols].astype(float), X], axis=1)
    m = sm.GLM(dd[y].astype(float), X, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": dd[cl].values})
    b, se = m.params[x], m.bse[x]
    r = dict(b=b, se=se, OR=math.exp(b), lo=math.exp(b - 1.959964 * se), hi=math.exp(b + 1.959964 * se), p=m.pvalues[x],
             n=len(d), n_used=len(dd), groups_dropped=int(len(v) - len(keep)), clusters=int(dd[cl].nunique()), events=int(dd[y].sum()))
    return r, m, dd


def implied(m, dd, years, x="dec"):
    """average predicted probability across the towns in the model at given years"""
    out = {}
    X0 = m.model.exog.copy(); names = m.model.exog_names; j = names.index(x)
    # one row per town in the model
    tows = dd.drop_duplicates("town").index
    pos = [dd.index.get_loc(i) for i in tows]
    for yy in years:
        X = X0[pos].copy(); X[:, j] = (yy - 2000) / 10
        out[yy] = float(np.mean(m.predict(X)))
    return out


def lpm(d, y, x="dec", fe="town", cl="year"):
    d = d.dropna(subset=[y])
    X = pd.concat([d[[x]], pd.get_dummies(d[fe], drop_first=True).astype(float)], axis=1); X = sm.add_constant(X)
    m = sm.OLS(d[y].astype(float), X).fit(cov_type="cluster", cov_kwds={"groups": d[cl].values})
    return dict(b=m.params[x] * 100, lo=(m.params[x] - 1.959964 * m.bse[x]) * 100, hi=(m.params[x] + 1.959964 * m.bse[x]) * 100, p=m.pvalues[x], n=len(d))


def annual(d, y):
    s = d.dropna(subset=[y]).groupby("year")[y].mean() * 100
    return s


def mk(s):
    tau, p = stats.kendalltau(s.index.values, s.values)
    sl = stats.theilslopes(s.values, s.index.values)
    return dict(tau=tau, p=p, sen_pp_dec=sl[0] * 10, sen_lo=sl[2] * 10, sen_hi=sl[3] * 10, n_years=len(s))


t0 = time.time()
# ---------- M1 trend
for y, y0 in (("lie", YL0), ("fall", Y0), ("both", YL0)):
    d = Y[Y.year >= y0]
    r, m, dd = fe_logit(d, y)
    r["implied"] = implied(m, dd, [y0, 1950, 2025])
    r["from"] = y0
    OUT[f"M1_{y}"] = r
    OUT[f"MK_{y}"] = mk(annual(d, y))
d = Y[Y.year >= YL0]; r, m, dd = fe_logit(d, "fall"); r["implied"] = implied(m, dd, [1950, 2025]); r["from"] = YL0; OUT["M1_fall_1950"] = r
OUT["MK_fall_1950"] = mk(annual(d, "fall"))
# temperature trend (OLS, town FE, cluster by year)
for y0 in (Y0, YL0):
    d = Y[Y.year >= y0]
    X = sm.add_constant(pd.concat([d[["dec"]], pd.get_dummies(d.town, drop_first=True).astype(float)], axis=1))
    m = sm.OLS(d.tx25, X).fit(cov_type="cluster", cov_kwds={"groups": d.year.values})
    OUT[f"TEMP_{y0}"] = dict(b=m.params["dec"], lo=m.conf_int().loc["dec", 0], hi=m.conf_int().loc["dec", 1], p=m.pvalues["dec"], n=len(d))
    s = d.groupby("year").tx25.mean(); OUT[f"TEMP_{y0}"]["mk"] = mk(s)
# does Christmas Day temperature predict lying snow? (descriptive, exploratory)
print("M1 done", round(time.time() - t0))

# ---------- M2 geography
Y["elev100"] = Y.elev / 100; Y["coast10"] = Y.coast_km / 10
GEOX = ["elev100", "lat", "lon", "coast10"]


def geo_model(d, y, xs=GEOX, twoway=True):
    d = d.dropna(subset=[y]).copy()
    v = d.groupby("year")[y].max(); keep = v.index[v > 0]
    dd = d[d.year.isin(keep)]
    X = pd.concat([dd[xs].astype(float), pd.get_dummies(dd.year, prefix="y").astype(float)], axis=1)
    mod = sm.GLM(dd[y].astype(float), X, family=sm.families.Binomial())
    fit0 = mod.fit()
    if twoway:
        # two-way cluster (Cameron, Gelbach and Miller): V = V_town + V_year - V_town-year (town-year = observation, HC0)
        g1 = pd.factorize(dd.town)[0]; g2 = pd.factorize(dd.year)[0]
        V1 = mod.fit(cov_type="cluster", cov_kwds={"groups": g1}).cov_params()
        V2 = mod.fit(cov_type="cluster", cov_kwds={"groups": g2}).cov_params()
        V12 = mod.fit(cov_type="HC0").cov_params()
        V = V1 + V2 - V12
        se = np.sqrt(np.diag(V.loc[xs, xs]).clip(min=0))
    else:
        se = np.sqrt(np.diag(mod.fit(cov_type="cluster", cov_kwds={"groups": dd.year.values}).cov_params().loc[xs, xs]))
    res = {}
    for i, x in enumerate(xs):
        b = fit0.params[x]
        res[x] = dict(b=b, se=se[i], OR=math.exp(b), lo=math.exp(b - 1.959964 * se[i]), hi=math.exp(b + 1.959964 * se[i]),
                      p=2 * (1 - stats.norm.cdf(abs(b / se[i]))))
    res["n"] = len(d); res["n_used"] = len(dd); res["years_dropped"] = int(len(v) - len(keep)); res["towns"] = int(dd.town.nunique())
    return res


for y, y0 in (("lie", YL0), ("fall", Y0), ("both", YL0)):
    OUT[f"M2_{y}"] = geo_model(Y[Y.year >= y0], y)
OUT["M2_lie_year"] = geo_model(Y[Y.year >= YL0], "lie", twoway=False)
# exploratory (added after the plan): the hilliness of the ERA5-Land cell around the town (01b_terrain.py)
Y["cell100"] = Y.cell10_mean / 100; Y["excess100"] = (Y.cell10_mean - Y.elev) / 100
for y, y0 in (("lie", YL0), ("fall", Y0)):
    OUT[f"X1_{y}"] = geo_model(Y[Y.year >= y0], y, xs=["elev100", "excess100", "lat", "lon", "coast10"])
# town-level: share of years vs elevation (Spearman), for the text
TS = Y.groupby("town").agg(lie=("lie", "mean"), fall=("fall", "mean"), elev=("elev", "first"), lat=("lat", "first"))
OUT["spearman_elev_lie"] = dict(zip(("rho", "p"), stats.spearmanr(TS.elev, TS.lie)))
OUT["spearman_lat_lie"] = dict(zip(("rho", "p"), stats.spearmanr(TS.lat, TS.lie)))
OUT["spearman_elev_fall"] = dict(zip(("rho", "p"), stats.spearmanr(TS.elev, TS.fall)))
OUT["spearman_lat_fall"] = dict(zip(("rho", "p"), stats.spearmanr(TS.lat, TS.fall)))
print("M2 done", round(time.time() - t0))

# ---------- validation
sl = annual(Y[(Y.year >= 1960)], "lie"); sf = annual(Y[(Y.year >= 1960)], "fall")
rk = sl.rank(ascending=False, method="min")
ranks = {int(y): int(rk[y]) for y in MO_WIDESPREAD}
# probability that 4 random distinct years of 66 all rank within the worst observed rank of the four
worst = max(ranks.values()); nyr = len(sl)
from math import comb
p_rand = comb(worst, 4) / comb(nyr, 4)
OUT["V1"] = dict(ranks=ranks, n_years=nyr, worst=worst, p_random=p_rand, top10=[int(y) for y in sl.sort_values(ascending=False).index[:10]],
                 share={int(y): float(sl[y]) for y in MO_WIDESPREAD}, all_top10=all(v <= 10 for v in ranks.values()))
ly = sorted(MO_LYING); fy = sorted(MO_FALL)
OUT["V2"] = dict(lying=dict(zip(("rho", "p"), stats.spearmanr([MO_LYING[y] for y in ly], [sl[y] for y in ly]))), lying_n=len(ly),
                 lying_pairs={y: [MO_LYING[y], float(sl[y])] for y in ly},
                 falling=dict(zip(("rho", "p"), stats.spearmanr([MO_FALL[y] for y in fy], [sf[y] for y in fy]))), falling_n=len(fy),
                 falling_pairs={y: [MO_FALL[y], float(sf[y])] for y in fy})
OUT["V3"] = dict(years_ge5=int((sf >= 5).sum()), n_years=len(sf), pct=float((sf >= 5).mean() * 100),
                 years_any=int((sf > 0).sum()))
print("V done", OUT["V1"]["ranks"], OUT["V3"])

# ---------- robustness (on the main outcomes lie and fall)
ROB = []
def add(group, label, r, outcome):
    ROB.append(dict(group=group, label=label, outcome=outcome, OR=r["OR"], lo=r["lo"], hi=r["hi"], p=r["p"], n=r["n"], clusters=r["clusters"]))
for y, y0 in (("lie", YL0), ("fall", Y0)):
    add("Main", "Main model (M1)", OUT[f"M1_{y}"], y)
    if y == "lie":
        add("Thresholds", "Any snow on the ground (> 0 m)", fe_logit(Y[Y.year >= YL0], "lie0")[0], y)
        add("Thresholds", "More than 5 cm on the ground", fe_logit(Y[Y.year >= YL0], "lie5")[0], y)
    else:
        add("Thresholds", "At least 0.7 cm of snowfall (1 mm water)", fe_logit(Y[Y.year >= Y0], "fall07")[0], y)
        add("Period", "From 1950", OUT["M1_fall_1950"], y)
    add("Period", f"To 2016 (before IFS may enter the series)", fe_logit(Y[(Y.year >= y0) & (Y.year < IFS_FROM)], y)[0], y)
    add("Period", "From 1960", fe_logit(Y[Y.year >= 1960], y)[0], y)
    for nt in ("England", "Scotland", "Wales", "Northern Ireland"):
        add("Leave one nation out", f"Without {nt}", fe_logit(Y[(Y.year >= y0) & (Y.nation != nt)], y)[0], y)
    add("Influential years", "Without 2009 and 2010", fe_logit(Y[(Y.year >= y0) & (~Y.year.isin([2009, 2010]))], y)[0], y)
    add("Other days", "24 December", fe_logit(Y[Y.year >= y0], f"{y}24")[0], y)
    add("Other days", "26 December", fe_logit(Y[Y.year >= y0], f"{y}26")[0], y)
OUT["robust"] = ROB
OUT["LPM_lie"] = lpm(Y[Y.year >= YL0], "lie"); OUT["LPM_fall"] = lpm(Y[Y.year >= Y0], "fall")
print("R done", round(time.time() - t0))

# ---------- P1 permutation (shuffle whole years), fast Newton logit with town FE as the statistic
def irls(X, y, beta, it=25):
    for _ in range(it):
        eta = X @ beta; p = 1 / (1 + np.exp(-eta)); w = p * (1 - p)
        H = (X * w[:, None]).T @ X; g = X.T @ (y - p)
        step = np.linalg.solve(H + 1e-9 * np.eye(len(beta)), g); beta = beta + step
        if np.max(np.abs(step)) < 1e-8: break
    return beta


def perm(y, y0, B=2000, seed=2026):
    """Shuffle the year labels of whole Christmases (all towns of a year move together) and refit the M1 logit."""
    d = Y[Y.year >= y0].dropna(subset=[y])
    v = d.groupby("town")[y].agg(["min", "max"]); d = d[d.town.isin(v.index[v["min"] < v["max"]])]
    D_ = pd.get_dummies(d.town).astype(float).values
    yv = d[y].values.astype(float); yrs = np.sort(d.year.unique()); yi = np.searchsorted(yrs, d.year.values)
    X = np.c_[d.dec.values, D_]
    b0 = irls(X, yv, np.zeros(X.shape[1])); o = b0[0]
    assert abs(o - OUT[f"M1_{y}"]["b"]) < 1e-5, (o, OUT[f"M1_{y}"]["b"])
    rng = np.random.default_rng(seed); sl = np.empty(B)
    for b in range(B):
        py = rng.permutation(yrs); X[:, 0] = (py[yi] - 2000) / 10
        sl[b] = irls(X, yv, b0.copy())[0]
    return dict(obs=o, B=B, p_two=float((np.abs(sl) >= abs(o)).mean()), p_lower=float((sl <= o).mean()), q025=float(np.quantile(sl, .025)), q975=float(np.quantile(sl, .975)))
PC = f"{SCR}/perm.json"
if os.path.exists(PC): OUT.update(jload(PC))
else:
    OUT["P1_lie"] = perm("lie", YL0)
    OUT["P1_fall"] = perm("fall", Y0); jsave({k: OUT[k] for k in ("P1_lie", "P1_fall")}, PC)
print("P1", OUT["P1_lie"], OUT["P1_fall"], round(time.time() - t0))

# ---------- P2 persistence placebo: P(lying 25 | lying 24)
d = Y[(Y.year >= YL0) & (Y.lie24 == 1)].copy(); d["keep"] = d.lie25
r, m, dd = fe_logit(d, "keep", fe="town")
OUT["P2"] = dict(r, share=float(d.keep.mean() * 100), n24=int(len(d)))
s = d.groupby("year").keep.mean() * 100
OUT["P2"]["mk"] = mk(s)
jsave(OUT, f"{DATA}/models.json", indent=1)
rows = []
for k, v in OUT.items():
    if isinstance(v, dict) and "OR" in v:
        rows.append(dict(model=k, **{c: v.get(c) for c in ("OR", "lo", "hi", "p", "n", "n_used", "clusters", "events")}))
    elif k.startswith("M2_") or k.startswith("X1_"):
        for x in [c for c in v if isinstance(v[c], dict)]:
            rows.append(dict(model=f"{k}.{x}", **{c: v[x].get(c) for c in ("OR", "lo", "hi", "p")}, n=v["n"], n_used=v["n_used"]))
for r in ROB:
    rows.append(dict(model=f"robust.{r['outcome']}.{r['label']}", OR=r["OR"], lo=r["lo"], hi=r["hi"], p=r["p"], n=r["n"], clusters=r["clusters"]))
pd.DataFrame(rows).to_csv(f"{DATA}/models.csv", index=False, float_format="%.5g")
print("done", round(time.time() - t0))
