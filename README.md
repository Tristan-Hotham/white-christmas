# What are the odds of a white Christmas where you live?

Snow on Christmas Day in 116 UK towns from reanalysis, 1940 to 2025. Every Christmas Day in 116 towns across England, Scotland, Wales and Northern Ireland, classified from the ERA5 and ERA5-Land reanalyses (via the Open-Meteo archive) as snow falling, snow lying (more than 1 cm) or both; odds by town and decade, the geography of the odds, a test against the Met Office's white Christmas record, and trend tests fixed in a written analysis plan before the results (NOTES.md). A data study by Dr Tristan Hotham (Independent researcher).

Interactive page: https://maps.tristanhotham.com/white-christmas/
Paper: https://doi.org/10.5281/zenodo.24132735
Blog post: https://blog.tristanhotham.com/2026/10/31/white-christmas/
Code and data: https://github.com/Tristan-Hotham/white-christmas
Theme: Everyday life

## Headline results

- Snow lay on Christmas Day in 8.8% of town-years 1950 to 2025 (95% CI 8.3 to 9.4; about 1 in 11); snow fell in 8.8% 1940 to 2025; both in 3.6% (1 in 28).
- Local odds: never in Bournemouth; 5 of 76 in London, 7 in Manchester, 13 in Glasgow, 11 in Edinburgh. Aviemore 70% and Fort William 62%, partly because their reanalysis cells include hills.
- Geography (logit, year fixed effects, two-way clustered): odds ratio 3.39 per 100 m of height (95% CI 1.67 to 6.85) and 1.65 per degree north (1.29 to 2.11).
- Validation: the Met Office's four widespread lying-snow Christmases since 1960 (1981, 1995, 2009, 2010) rank 1, 2, 3 and 5 of 66 years by share of towns with lying snow.
- Trend: planned main model (logit, town fixed effects, errors clustered by year) odds ratio per decade 0.89 (95% CI 0.68 to 1.16): no decline distinguishable from chance. Planned Mann-Kendall test on the national series: tau -0.23, p = 0.004 (decline). Without 2009 and 2010: 0.72 (0.57 to 0.89). Christmas Day maximum temperature +0.49 C a decade since 1950 (0.17 to 0.81).

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; the 116 towns coloured by the share of Christmases with snow lying, falling or both, for all years or one decade; search, layers, full screen, popups with each town's Christmas calendar strip. |
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

Hotham, T. (2026) What are the odds of a white Christmas? Snow on Christmas Day in 116 UK towns from reanalysis, 1940 to 2025. Zenodo. https://doi.org/10.5281/zenodo.24132735

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
