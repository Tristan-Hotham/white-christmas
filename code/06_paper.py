"""Step 6: the paper. Fills code/paper_template.tex from data/results.json and data/town_odds.csv, adds the tables and
compiles with xelatex. Output: release/paper/Hotham_White_Christmas.pdf and .tex beside the f_*.pdf figures. The DOI stays
a placeholder (https://doi.org/10.5281/zenodo.24132735 printed) unless DOI is set:  DOI=10.5281/zenodo.N python3 code/06_paper.py"""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(REL, "paper"); NAME = "Hotham_White_Christmas"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    for k in ("f0", "f1", "f2", "f3"):
        if f == k: return f"{float(v):.{k[1]}f}".replace("-", "$-$")
    return tex(str(v))


def ci(d, k="OR"):
    return f"{d[k]:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


T = pd.read_csv(f"{DATA}/town_odds.csv")
# towns table: top 10 and bottom 10 by lying snow, plus large cities
def trow(r):
    return (f"{tex(r.town)} & {tex(r.nation)} & {int(r.elev)} & {r.lie_pc:.1f} [{r.lie_lo:.1f}, {r.lie_hi:.1f}] & {r.fall_pc:.1f} & {r.both_pc:.1f} & "
            f"{'' if pd.isna(r.lie_last) else int(r.lie_last)}\\\\\n")
top = T.sort_values(["lie_pc", "fall_pc"], ascending=False).head(10); bot = T.sort_values(["lie_pc", "fall_pc"]).head(10)
cities = T[T.town.isin(["London", "Birmingham", "Glasgow", "Manchester", "Edinburgh", "Belfast", "Cardiff"])].sort_values("lie_pc", ascending=False)
head = "Town & Nation & Height (m) & Lying \\% [95\\% CI] & Falling \\% & Both \\% & Last lying\\\\\\midrule\n"
TT = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Odds of a white Christmas by town: share of Christmas Days with snow lying (1950 to 2025, Wilson 95\\% interval), falling (1940 to 2025) and both (1950 to 2025), and the last year with lying snow. All towns are in Appendix Table~\\ref{tab:all}.}\\label{tab:towns}"
      "\\setlength{\\tabcolsep}{4pt}\\begin{tabular}{llrlrrr}\\toprule " + head +
      "\\multicolumn{7}{l}{\\textit{Ten highest (lying snow)}}\\\\\n" + "".join(trow(r) for r in top.itertuples()) +
      "\\midrule\\multicolumn{7}{l}{\\textit{Ten lowest}}\\\\\n" + "".join(trow(r) for r in bot.itertuples()) +
      "\\midrule\\multicolumn{7}{l}{\\textit{Largest cities}}\\\\\n" + "".join(trow(r) for r in cities.itertuples()) + "\\bottomrule\\end{tabular}\\end{table}")
lab = {"elev100": "Height (per 100 m)", "lat": "Latitude (per degree N)", "lon": "Longitude (per degree E)", "coast10": "Distance to the sea (per 10 km)", "excess100": "Cell height above the town (per 100 m)"}
rows = ""
for x in ("elev100", "lat", "lon", "coast10"):
    rows += f"{lab[x]} & {ci(R['M2_lie'][x])} & {ci(R['M2_fall'][x])} & {ci(R['M2_both'][x])}\\\\\n"
rows += f"\\midrule Town-years used & {R['M2_lie']['n_used']:,} & {R['M2_fall']['n_used']:,} & {R['M2_both']['n_used']:,}\\\\\n"
rows += f"Years dropped (no town with the outcome) & {R['M2_lie']['years_dropped']} & {R['M2_fall']['years_dropped']} & {R['M2_both']['years_dropped']}\\\\\n"
rows += "\\midrule\\multicolumn{4}{l}{\\textit{Exploratory (added after the plan): with the ERA5-Land cell's height}}\\\\\n"
for x in ("elev100", "excess100"):
    rows += f"{lab[x]} & {ci(R['X1_lie'][x])} & {ci(R['X1_fall'][x])} & \\\\\n"
TG = ("\\begin{table}[tbp]\\centering\\small\\caption{Geography of the odds (M2): odds ratios [95\\% CI] from logistic regressions with year fixed effects, standard errors clustered by town and by year. Lying and both 1950 to 2025; falling 1940 to 2025.}\\label{tab:geo}"
      "\\begin{tabular}{llll}\\toprule & Lying & Falling & Both\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for o, nm in (("lie", "Lying (1950 to 2025)"), ("fall", "Falling (1940 to 2025)"), ("fall_1950", "Falling (1950 to 2025)"), ("both", "Both (1950 to 2025)")):
    m = R[f"M1_{o}"]; mk = R[f"MK_{o}"]
    rows += f"{nm} & {ci(m)} & {m['p']:.3f} & {m['n_used']:,} / {m['clusters']} & {mk['tau']:.2f} & {mk['p']:.3f}\\\\\n".replace("-0.", "$-$0.")
TR_ = ("\\begin{table}[tbp]\\centering\\small\\caption{Trend tests. M1: odds ratio per decade [95\\% CI] from logistic regression with town fixed effects, standard errors clustered by year (towns with no variation drop out). M1b: Mann-Kendall test on the annual share of towns.}\\label{tab:trend}"
       "\\begin{tabular}{p{4.4cm}lrrrr}\\toprule & \\multicolumn{3}{c}{M1} & \\multicolumn{2}{c}{M1b}\\\\\\cmidrule(lr){2-4}\\cmidrule(lr){5-6} Outcome & OR per decade & $p$ & Town-years / years & $\\tau$ & $p$\\\\\\midrule\n" + rows +
       f"\\midrule Christmas Day max. temperature, 1950 to 2025 (°C a decade, OLS) & {R['TEMP_1950']['b']:.2f} [{R['TEMP_1950']['lo']:.2f}, {R['TEMP_1950']['hi']:.2f}] & {R['TEMP_1950']['p']:.3f} & {R['TEMP_1950']['n']:,} / 76 & {R['TEMP_1950']['mk']['tau']:.2f} & {R['TEMP_1950']['mk']['p']:.3f}\\\\\n"
       f"Christmas Day max. temperature, 1940 to 2025 & {R['TEMP_1940']['b']:.2f} [{R['TEMP_1940']['lo']:.2f}, {R['TEMP_1940']['hi']:.2f}] & {R['TEMP_1940']['p']:.3f} & {R['TEMP_1940']['n']:,} / 86 & {R['TEMP_1940']['mk']['tau']:.2f} & {R['TEMP_1940']['mk']['p']:.3f}\\\\\n".replace("$-$0.", "$-$0.").replace("[-", "[$-$")
       + "\\bottomrule\\end{tabular}\\end{table}")
V = R["V1"]; V2 = R["V2"]
rows = "".join(f"{y} & {R['met_office']['lying'].get(str(y), R['met_office']['lying'].get(y, ''))} & {V2['lying_pairs'][str(y)][1]:.1f} & {R['met_office']['falling'].get(str(y), '')} & {R['annual']['y' + str(y)]['fall'] if 'y' + str(y) in R['annual'] else ''}\\\\\n" for y in ())
yrs = sorted(set(int(y) for y in V2["lying_pairs"]) | set(int(y) for y in V2["falling_pairs"]))
for y in yrs:
    lp = V2["lying_pairs"].get(str(y)); fp = V2["falling_pairs"].get(str(y))
    rows += f"{y} & {'' if lp is None else ('$<$1' if lp[0] == 0.5 else f'{lp[0]:g}')} & {'' if lp is None else f'{lp[1]:.1f}'} & {'' if fp is None else f'{fp[0]:g}'} & {'' if fp is None else f'{fp[1]:.1f}'}\\\\\n"
TV = ("\\begin{table}[tbp]\\centering\\small\\caption{Validation against the Met Office's published Christmas Day figures: percentage of stations and of the 116 towns with snow lying and falling. "
      f"Widespread lying-snow years since 1960 (1981, 1995, 2009, 2010) rank {', '.join(str(V['ranks'][str(y)]) for y in (1981, 1995, 2009, 2010))} of {V['n_years']} by the share of towns. "
      f"Spearman $\\rho$: lying {V2['lying']['rho']:.2f} ({V2['lying_n']} years), falling {V2['falling']['rho']:.2f} ({V2['falling_n']} years).}}\\label{{tab:valid}}"
      "\\begin{tabular}{lrrrr}\\toprule & \\multicolumn{2}{c}{Lying} & \\multicolumn{2}{c}{Falling}\\\\\\cmidrule(lr){2-3}\\cmidrule(lr){4-5} Year & Stations \\% & Towns \\% & Stations \\% & Towns \\%\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""; cur = None
for r in R["robust"]:
    if r["outcome"] != cur:
        cur = r["outcome"]; rows += f"\\multicolumn{{4}}{{l}}{{\\textit{{{'Lying snow, from 1950' if cur == 'lie' else 'Falling snow, from 1940'}}}}}\\\\\n"
    rows += f"\\quad {tex(r['label'])} & {r['OR']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}] & {r['p']:.3f} & {r['n']:,} / {r['clusters']}\\\\\n"
rows += f"\\midrule Linear probability model, lying (points a decade) & {R['LPM_lie']['b']:.2f} [{R['LPM_lie']['lo']:.2f}, {R['LPM_lie']['hi']:.2f}] & {R['LPM_lie']['p']:.3f} & {R['LPM_lie']['n']:,}\\\\\n"
rows += f"Linear probability model, falling & {R['LPM_fall']['b']:.2f} [{R['LPM_fall']['lo']:.2f}, {R['LPM_fall']['hi']:.2f}] & {R['LPM_fall']['p']:.3f} & {R['LPM_fall']['n']:,}\\\\\n"
rows += f"P1 permutation, lying (two-sided $p$, 2,000 shuffles) & & {R['P1_lie']['p_two']:.3f} & \\\\\nP1 permutation, falling & & {R['P1_fall']['p_two']:.3f} & \\\\\n"
rows += f"P2 persistence: still lying on 25th given lying on 24th & {R['P2']['OR']:.2f} [{R['P2']['lo']:.2f}, {R['P2']['hi']:.2f}] & {R['P2']['p']:.3f} & {R['P2']['n']:,} / {R['P2']['clusters']}\\\\\n"
rows = rows.replace("[-", "[$-$").replace(" -", " $-$")
TRB = ("\\begin{table}[tbp]\\centering\\small\\caption{Robustness and falsification: odds ratio per decade [95\\% CI], $p$, and town-years / years used.}\\label{tab:robust}"
       "\\begin{tabular}{p{7.6cm}lrr}\\toprule Check & Estimate & $p$ & N\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(r.town)} & {tex(r.nation)} & {int(r.elev)} & {int(round(r.cell10_mean))} & {r.lie_pc:.1f} & {r.lie_k} & {r.fall_pc:.1f} & {r.fall_k} & {r.both_pc:.1f} & {'' if pd.isna(r.lie_last) else int(r.lie_last)} & {'' if pd.isna(r.fall_last) else int(r.fall_last)}\\\\\n"
               for r in T.sort_values("lat", ascending=False).itertuples())
TA = ("{\\scriptsize\\setlength{\\tabcolsep}{3pt}\\begin{longtable}{llrrrrrrrrr}\\caption{All towns, north to south: town height and mean height of its ERA5-Land cell (m); share (\\%) and number of Christmases with snow lying (of 76), falling (of 86) and both; last year with lying and falling snow.}\\label{tab:all}\\\\\\toprule "
      "Town & Nation & Height & Cell & Lying \\% & n & Falling \\% & n & Both \\% & Last lying & Last falling\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", "\\url{" + PAGE + "}").replace("{{REPO}}", "\\url{" + REPO + "}")
for k, v in (("TABLE_TOWNS", TT), ("TABLE_GEO", TG), ("TABLE_TREND", TR_), ("TABLE_VALID", TV), ("TABLE_ROBUST", TRB), ("TABLE_ALL", TA)):
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24132735", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:5]
for bad in ("DSIT", "DCMS", "pre-registered", "preregistered", "civil serv"):
    assert bad not in t, bad
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:15])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
body = re.split(r"\n\f?References\n", txt)[0]
ab = txt.split("Abstract")[1].split("Keywords")[0]
print("paper", r.returncode, len(txt.split()), "words total;", len(body.split()), "before references; abstract", len(ab.split()), "words;",
      [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–"))
