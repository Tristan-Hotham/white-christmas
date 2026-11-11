"""Step 8: README.md, LICENSE, reddit/post.md and release/paper/cover_note.md, numbers from data/results.json."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json"); S = R["sample"]; o = R["overall"]; t = R["towns"]
m, mk, tp, g = R["M1_lie"], R["MK_lie"], R["TEMP_1950"], R["M2_lie"]
nb = R["robust_no0910_lie"]
txt = subprocess.run(["pdftotext", f"{REL}/paper/Hotham_White_Christmas.pdf", "-"], capture_output=True, text=True).stdout
words = len(re.split(r"\n\f?References\n", txt)[0].split())
readme = f"""# What are the odds of a white Christmas where you live?

Snow on Christmas Day in {S['towns']} UK towns from reanalysis, {S['first']} to {S['last']}. Every Christmas Day in {S['towns']} towns across England, Scotland, Wales and Northern Ireland, classified from the ERA5 and ERA5-Land reanalyses (via the Open-Meteo archive) as snow falling, snow lying (more than 1 cm) or both; odds by town and decade, the geography of the odds, a test against the Met Office's white Christmas record, and trend tests fixed in a written analysis plan before the results (NOTES.md). A data study by Dr Tristan Hotham (Independent researcher).

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24132735}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/white-christmas/}}
Code and data: {REPO}
Theme: {THEME}

## Headline results

- Snow lay on Christmas Day in {o['lie']['pc']:.1f}% of town-years 1950 to {S['last']} (95% CI {o['lie']['lo']:.1f} to {o['lie']['hi']:.1f}; about 1 in {o['lie']['one_in']}); snow fell in {o['fall']['pc']:.1f}% 1940 to {S['last']}; both in {o['both']['pc']:.1f}% (1 in {o['both']['one_in']}).
- Local odds: never in Bournemouth; {t['London']['lie_k']} of 76 in London, {t['Manchester']['lie_k']} in Manchester, {t['Glasgow']['lie_k']} in Glasgow, {t['Edinburgh']['lie_k']} in Edinburgh. Aviemore {t['Aviemore']['lie_pc']:.0f}% and Fort William {t['Fort William']['lie_pc']:.0f}%, partly because their reanalysis cells include hills.
- Geography (logit, year fixed effects, two-way clustered): odds ratio {g['elev100']['OR']:.2f} per 100 m of height (95% CI {g['elev100']['lo']:.2f} to {g['elev100']['hi']:.2f}) and {g['lat']['OR']:.2f} per degree north ({g['lat']['lo']:.2f} to {g['lat']['hi']:.2f}).
- Validation: the Met Office's four widespread lying-snow Christmases since 1960 (1981, 1995, 2009, 2010) rank 1, 2, 3 and 5 of 66 years by share of towns with lying snow.
- Trend: planned main model (logit, town fixed effects, errors clustered by year) odds ratio per decade {m['OR']:.2f} (95% CI {m['lo']:.2f} to {m['hi']:.2f}): no decline distinguishable from chance. Planned Mann-Kendall test on the national series: tau {mk['tau']:.2f}, p = {mk['p']:.3f} (decline). Without 2009 and 2010: {nb['OR']:.2f} ({nb['lo']:.2f} to {nb['hi']:.2f}). Christmas Day maximum temperature +{tp['b']:.2f} C a decade since 1950 ({tp['lo']:.2f} to {tp['hi']:.2f}).

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; the {S['towns']} towns coloured by the share of Christmases with snow lying, falling or both, for all years or one decade; search, layers, full screen, popups with each town's Christmas calendar strip. |
| `header.png` | Social card, 1200 x 630. |
| `data/towns.csv` | Towns: point, nation, reanalysis grid point, elevation, distance to the sea, mean and maximum height of the ERA5-Land cell. |
| `data/town_years.csv` | One row per town and year: snowfall (cm), snow depth (m) and maximum temperature (C) on 24, 25 and 26 December. |
| `data/town_odds.csv` | Per town: counts, shares, Wilson intervals and last year for each outcome. |
| `data/annual.csv` | Per year: share of towns with each outcome, mean Christmas Day maximum temperature. |
| `data/models.json`, `data/models.csv` | Every model estimate. |
| `data/results.json`, `data/site.json` | Every number quoted anywhere; page data. |
| `code/` | Scripts in order, templates, `qa.js`. |
| `release/` | Paper (PDF, LaTeX, figures, `cover_note.md`), blog post and figures, Zenodo files. |
| `reddit/` | Collage, its script, the looping GIF and the post text. |
| `NOTES.md` | Working notes and the analysis plan, written before the results. |

## Method in brief

- Data: Open-Meteo Historical Weather API (default best match: ERA5 from 1940, ERA5-Land from 1950, ECMWF IFS from 2017). Snow depth only from ERA5-Land, so lying snow starts in 1950.
- Definitions (25 December): falling = any snowfall (at least 0.07 cm, 0.1 mm of water); lying = snow depth above 1 cm; both. Sensitivity thresholds 0.7 cm, any depth, 5 cm.
- Models: logistic regression with town fixed effects and errors clustered by year (trend); Mann-Kendall and Sen slope on the national annual share; logistic regression with year fixed effects and two-way clustering (geography); 11 robustness checks per outcome, a 2,000-shuffle permutation test and a persistence placebo.
- Exploratory (added after the plan): the mean height of each town's ERA5-Land cell from Mapzen/AWS Terrain Tiles.

## How to rerun

Needs Python 3 with pandas, numpy, statsmodels, scipy, shapely, pyproj, matplotlib, Pillow; xelatex; node with Playwright for QA. Raw inputs are listed in `code/common.py`.

```
python3 code/01_data.py         # tidy the Open-Meteo extract
python3 code/01b_terrain.py     # reanalysis cell heights (exploratory)
python3 code/02_models.py       # all models (permutations take a few minutes)
python3 code/03_results.py      # results.json and page data
python3 code/04_figures.py      # figures and header
python3 code/05_build_site.py   # index.html
python3 code/06_paper.py        # paper (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py
python3 code/08_readme.py       # README, LICENSE, Reddit post, cover note
python3 code/07_release.py      # blog post, Zenodo files
```

## Sources and licences

- Open-Meteo Historical Weather API (Zippenfenig 2023, doi:10.5281/zenodo.7970649), CC BY 4.0, retrieved 2026. Contains modified Copernicus Climate Change Service information: ERA5 (Hersbach et al. 2020, doi:10.1002/qj.3803; data doi:10.24381/cds.adbb2d47) and ERA5-Land (Muñoz-Sabater et al. 2021, doi:10.5194/essd-13-4349-2021; data doi:10.24381/cds.e2161bac).
- Met Office, "Will it be a white Christmas?" (2024 press release) and the Met Office white Christmas page: definition and station figures used for validation.
- ONS local authority districts December 2023 (Open Government Licence v3.0); Natural Earth (public domain); Mapzen/AWS Terrain Tiles (exploratory cell heights).
- Base map: OpenFreeMap Positron (OpenStreetMap contributors, ODbL). MapLibre GL JS (BSD 3-Clause).
- Text, figures and derived data CC BY 4.0; code MIT.

## Citation

Hotham, T. (2026) What are the odds of a white Christmas? Snow on Christmas Day in 116 UK towns from reanalysis, 1940 to 2025. Zenodo. {{https://doi.org/10.5281/zenodo.24132735}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(f"{ROOT}/README.md", "w", encoding="utf-8").write(readme)
mit = open("/home/claude/studies/byelection-attention/LICENSE", encoding="utf-8").read().split("Text, figures")[0]
lic = mit + ("Text, figures and the paper: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/\n"
             "Derived data (data/): CC BY 4.0. Source data: Open-Meteo Historical Weather API (CC BY 4.0), containing modified Copernicus Climate Change Service information (ERA5, ERA5-Land).\n")
open(f"{ROOT}/LICENSE", "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] What are the odds of a white Christmas where you live? Snow lay on about 1 Christmas Day in {o['lie']['one_in']} across {S['towns']} UK towns since 1950. In Bournemouth: never.

**Body:**

I took every Christmas Day from {S['first']} to {S['last']} in {S['towns']} UK towns from weather reanalysis (ERA5 and ERA5-Land) and counted when snow fell, when it lay on the ground (more than 1 cm), and both.

- Snow lying: {o['lie']['pc']:.1f}% of town Christmases since 1950. Snow falling: {o['fall']['pc']:.1f}% since 1940.
- London: {t['London']['lie_k']} of 76 Christmases with snow lying. Glasgow {t['Glasgow']['lie_k']}, Edinburgh {t['Edinburgh']['lie_k']}, Bournemouth 0.
- Every 100 m of height multiplies the odds by about {g['elev100']['OR']:.1f}; every degree north by about {g['lat']['OR']:.1f}.
- It comes in a few big years: in 2010 snow lay in {R['annual']['y2010']['n_lie']} of the {S['towns']} towns, in 1981 in {R['annual']['y1981']['n_lie']}. The reanalysis puts the Met Office's four widespread snowy Christmases since 1960 at ranks 1, 2, 3 and 5 of 66 years.
- Rarer? Probably: {R['halves']['lie']['first']:.1f}% of town Christmases had lying snow 1950 to 1987, {R['halves']['lie']['second']:.1f}% 1988 to 2025. But with 2009 and 2010 in the data my main trend model can't rule out no change.

Interactive map with every town's Christmas calendar: {PAGE}

**Source comment:**

Data: Open-Meteo Historical Weather API (ERA5, ERA5-Land reanalysis from Copernicus/ECMWF), CC BY 4.0; Met Office white Christmas record for the check. Method: logistic regression with town fixed effects, errors clustered by year, plan written before the analysis; Mann-Kendall test on the national series. Caveat: reanalysis averages over cells about 9 to 11 km across and puts too much snow on hills, so Highland towns look snowier than their streets. Tools: Python (pandas, statsmodels, matplotlib), MapLibre. Paper and code: {REPO}
"""
open(f"{ROOT}/reddit/post.md", "w", encoding="utf-8").write(post)
cover = f"""# Cover note: What are the odds of a white Christmas?

## Suitable journals (checked 2026)

None of these charges authors to publish; open access is optional and paid where offered. Word limits could not all be confirmed from this workspace (several author pages were blocked); recheck before submitting.

1. **Weather** (Royal Meteorological Society, Wiley). Named in the brief and the natural home: it publishes accessible, well-illustrated articles for a broad readership, including Brown (2020) on snow cover in Great Britain, cited here. The RMetS journal page states that articles are published free of charge unless the author chooses open access. Its length limit could not be confirmed; Weather articles are typically much shorter than this paper (about {words:,} words including tables and captions), so a condensed version (odds, map, validation, trend in brief) would be needed.
2. **International Journal of Climatology** (Royal Meteorological Society, Wiley). Named in the brief; a hybrid subscription journal (MPDL open access listing: "hybrid OA"), so no charge for the subscription route. It published Brown (2019) and the annual State of the UK Climate reports. Its word limit could not be confirmed. The validation of ERA5-Land snow against the Met Office record and the trend analysis suit it best.
3. **Climatologie** (Association Internationale de Climatologie, EDP Sciences). Accepts English; research papers are capped at 40,000 characters including spaces (about 6,000 words), so the paper would need shortening. Its fee page could not be read; check that it is free to authors before submitting.

## Summary of the contribution (for a cover letter)

The odds of a white Christmas are a perennial public question, but published figures are national counts of stations. Using ERA5 and ERA5-Land reanalysis, this paper classifies every Christmas Day from 1940 to 2025 in {S['towns']} UK towns as having snow falling, lying or both, giving the first town-by-town odds across the four nations. Snow lay on {o['lie']['pc']:.1f}% of town Christmases since 1950, rising strongly with height and latitude, from never in Bournemouth to most years in Highland towns whose reanalysis cells include hills. The reanalysis reproduces the Met Office record: its four widespread lying-snow Christmases since 1960 rank 1, 2, 3 and 5 of 66 years. In trend tests specified in a written plan, the main logistic model finds no clear decline (odds ratio per decade {m['OR']:.2f}, 95% CI {m['lo']:.2f} to {m['hi']:.2f}), while a rank test on the national series does; the result turns on 2009 and 2010. Christmas Day has warmed by {tp['b']:.2f} C a decade since 1950. Data and code are openly released.
"""
open(f"{REL}/paper/cover_note.md", "w", encoding="utf-8").write(cover)
for f_ in (f"{ROOT}/README.md", f"{ROOT}/reddit/post.md", f"{REL}/paper/cover_note.md"):
    s_ = open(f_, encoding="utf-8").read()
    for bad in ("—", "–", " -- ", "DSIT", "DCMS", "civil serv", "pre-registered"):
        assert bad not in s_, (f_, bad)
print("readme, licence, post, cover note; paper words", words)
