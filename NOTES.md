# white-christmas: working notes

Brief: /home/claude/work/new13/BRIEFS.md section L (+ the shared rules it points to: new12, new11, new10, new9, new8 BRIEFS
tops, house brief /home/claude/newdata/BRIEF.md, GIF brief /home/claude/gifs/BRIEF.md). Format refs: byelection-attention,
fame-half-life, janus-places. Scratch: /home/claude/scratch/white-christmas (delete at the end).

## The data (read before writing the plan)

/home/claude/newdata/raw_new13/white_christmas.json, retrieved 2026 by the lead from the Open-Meteo Historical Weather API
(archive endpoint, default model, CC BY 4.0). 116 UK towns x 86 years (1940 to 2025) = 9,976 town-years, complete.
Values: snowfall_sum (cm) for 24, 25, 26 December; snow_depth_max (m) for the same days; temperature_2m_max (C) for the same
days; the grid point latitude and longitude Open-Meteo used, and the elevation it reports. (The brief said precipitation for
the third array: it is daily maximum temperature, per the lead's correction.)

What Open-Meteo's own documentation says (page source of open-meteo.com/en/docs/historical-weather-api, fetched from the
open-meteo-website repository on GitHub, 2026):
- Sources: ERA5 (0.25 deg, ~25 km, from 1940), ERA5-Land (0.1 deg, ~11 km, from 1950), ECMWF IFS (9 km, from 2017).
  "The default Best Match combines IFS HRES, ERA5 and ERA5-Land seamlessly."
- Snowfall: ERA5 and IFS (not ERA5-Land). Snow depth: ERA5-Land only (not ERA5, not IFS) "Snow depth in ERA5-Land tends to
  be overestimated. As the spatial resolution for snow depth is limited, please use it with care."
- "when studying climate change over decades, it is advisable to exclusively utilise ERA5 or ERA5-Land" (because IFS
  model upgrades can alter the series). So snowfall and temperature from 2017 may come from IFS: a possible break. Planned
  check below (trend on 1940 to 2016 only).
- Snow depth is missing (null) for all towns 1940 to 1949: ERA5-Land starts in 1950. So lying snow is 1950 to 2025 only.
- The grid point is the same in every year for a town (e.g. London 51.4938, -0.1630). Elevation: Open-Meteo reports the
  elevation of the requested point from a 90 m DEM and downscales temperature to it; it is not the model grid's own height.
- Citations given by Open-Meteo: Zippenfenig (2023) Open-Meteo.com Weather API, Zenodo, doi:10.5281/zenodo.7970649;
  Hersbach et al. (2023) ERA5 hourly data on single levels, doi:10.24381/cds.adbb2d47; Munoz Sabater (2019) ERA5-Land
  hourly data, doi:10.24381/cds.e2161bac. Journal papers: Hersbach et al. (2020) QJRMS; Munoz-Sabater et al. (2021) ESSD.

What I looked at before writing the plan: the missingness pattern above, and the raw totals over all town-years
(snowfall on 25 December > 0 in 879 of 9,976; snow depth > 1 cm on 25 December in 779 of 8,816). Nothing by year, place
or decade.

## Met Office reference (for validation; Met Office press release "Will it be a white Christmas?", 11 December 2024, and
the Met Office white Christmas learning page, both read 2026)

- Definition (betting): "a single snowflake has to be observed falling on the 24 hours of 25 December", by an official
  observer or automatic station. A reanalysis cannot see a single flake: it gives a grid-cell average of modelled snowfall.
- Widespread lying snow (> 40% of stations reporting snow on the ground at 9 am) happened four times since 1960:
  1981, 1995, 2009 and 2010. 2010: snow lying at 83% of stations (highest on record), snow or sleet falling at 19%.
  2009: falling at 13% (press release; the learning page says 20%), lying at 57%.
- Falling snow % of stations: 2018 0, 2019 0, 2020 6, 2021 6, 2022 9, 2023 11. Lying: 2020 4, 2021 under 1, 2022 0, 2023 0.
- "Since 1960, around half of the years have seen at least 5% of the network record snow falling on Christmas Day."

## Analysis plan (written before computing any result by year, place or decade)

Question: what are the odds of a white Christmas in 116 UK towns, have they fallen since 1940/1950, and how do they depend
on height and latitude? Does a reanalysis reproduce the Met Office's own record of white Christmases?

Unit: town-year (Christmas Day of year y at town i). N = 9,976 for snowfall (1940 to 2025), 8,816 for lying snow (1950 to 2025).

Outcomes (binary, 25 December):
- (a) FALL: snowfall_sum on 25 Dec > 0 (the smallest stored amount is 0.07 cm, 0.1 mm of water). The closest a
  reanalysis gets to "a single flake"; it is a grid-cell average, so it will miss isolated flakes and showers and
  may show light modelled snow where none was observed.
- (b) LYING: snow_depth_max on 25 Dec > 0.01 m (more than 1 cm on the ground at some time in the day).
- (c) BOTH: (a) and (b). Main outcome for the "proper white Christmas" headline is (b) lying; (a) is the bookmakers' sense.
Sensitivity thresholds: FALL >= 0.7 cm (1 mm water); LYING > 0 m (any) and > 0.05 m (5 cm).

Per-town odds: share of years with each outcome, 95% Wilson interval, and "1 in N years". By decade (1940s to 2020s, the
2020s being 2020 to 2025, six years) nationally (share of town-years) and per town.

H1 (trend): the probability of a white Christmas has fallen over time.
- M1 (main): logistic regression of the outcome on year (scaled per decade) with town fixed effects; standard errors
  clustered by year (Christmas weather is shared across towns in a year, so the year is the effective unit; 76 or 86
  clusters). Report the odds ratio per decade with 95% CI, and model-implied probabilities for 1950 and 2025 at the average
  town. Run for LYING (1950 to 2025, main) and FALL (1940 to 2025 and 1950 to 2025).
- M1b: Mann-Kendall test and Sen's slope on the national annual series (share of the 116 towns with the outcome).
- What would count against H1: an odds ratio per decade whose 95% CI includes 1, or a Mann-Kendall p >= 0.05. Given only
  76 to 86 independent Christmases, a null is likely and will be reported as such, not as "no change".
- Mechanism check: Christmas Day maximum temperature, OLS with town fixed effects, SE clustered by year, C per decade.

H2 (geography): height and latitude raise the odds.
- M2: logistic regression across towns of the outcome on DEM elevation (per 100 m), latitude (per degree north),
  longitude (per degree east) and distance to the sea (km, Natural Earth 1:10m land), with year fixed effects; two-way
  clustered SE by town and year where it converges, otherwise clustered by year. What counts against H2: elevation or
  latitude odds ratios with CIs including 1.

H3 (validation): the reanalysis tracks the Met Office station record.
- V1: the four widespread lying-snow years since 1960 (1981, 1995, 2009, 2010) should rank in the top ten of 66 years
  (1960 to 2025) by share of towns with LYING; report their ranks and the exact permutation probability that four random
  years would all rank that high.
- V2: Spearman correlation between the share of towns and the Met Office % of stations, for the years with published
  figures (lying: 2009, 2010, 2020, 2021 (taken as 0.5), 2022, 2023; falling: 2009, 2010, 2018 to 2023). Few points:
  descriptive only.
- V3: share of years since 1960 with FALL at >= 5% of towns, against the Met Office's "around half".

Robustness (planned):
- R1 thresholds (above). R2 FALL trend on 1940 to 2016 and LYING on 1950 to 2016 (dropping the years Best Match may take
  snowfall and temperature from IFS). R3 start in 1960. R4 leave one nation out (England, Scotland, Wales, Northern
  Ireland). R5 drop 2009 and 2010 (the two biggest lying-snow years in the Met Office record) to check one or two years
  do not drive the trend. R6 linear probability model with town fixed effects. R7 alternative days: 24 or 26 December
  instead of the 25th (same weather regime; trend should be similar).
- Falsification / placebo: P1 permutation test: shuffle whole years (keeping all towns of a year together) 2,000
  times and re-estimate the M1 slope; report where the observed slope sits. P2 persistence placebo: among town-years with
  snow lying on 24 December, the chance it is still lying on the 25th is a matter of overnight physics, not of how often
  snow arrives, so it should show no clear trend; a strong trend there would suggest a drift in the snow model itself.
- Leave-one-region-out is R4 (nations).

Labelled exploratory if added later.

## Log

- 01_data.py: 116 towns (England 80, Scotland 21, Wales 8, Northern Ireland 7), 9,976 town-years, no gaps; snow depth null
  exactly 1940 to 1949 as expected; grid point constant by town (median 3.7 km from the town point, max 12.6 km).
- 02_models.py first run (as planned). Main results: lying M1 OR per decade 0.89 [0.68, 1.16], p 0.39 (null); falling
  0.94 [0.82, 1.08] (null). Mann-Kendall on the national annual share: lying tau -0.23, p 0.004 (decline); falling p 0.56.
  So H1 is mixed: the planned main model cannot exclude no change; the planned rank test finds fewer snowy Christmases.
  Christmas Day max temperature +0.49 C a decade from 1950 [0.17, 0.81]. Geography: lying OR 3.4 per 100 m of height,
  1.65 per degree north. Validation: the four Met Office widespread years rank 1, 2, 3 and 5 of 66 (all in the top ten).
  Robustness: only "without 2009 and 2010" (lying, OR 0.72 [0.57, 0.89]) and "from 1960" (falling) exclude 1. Reported
  as such: the decline is not robust across specifications; it depends on whether the two snowy Christmases of 2009 and
  2010 are kept, and on the start year for falling snow.
- The permutation loop first ran out of memory with statsmodels GLM refits; replaced by a numpy IRLS (same estimates,
  asserted equal to M1). Cached in scratch/perm.json.
- Exploratory (added after the plan, labelled as such): 01b_terrain.py computes the mean land height of the ERA5-Land
  cell (0.1 deg) around each town from the terrarium tiles in raw_new13. Lying-snow odds rise with the cell's excess height
  over the town (OR 3.3 per 100 m) but falling-snow odds do not (0.84, CI includes 1): consistent with ERA5-Land modelling
  snow depth for the cell's average terrain. Aviemore and Fort William (70% and 62% of Christmases with lying snow) are
  cell artefacts in part; said so on the map, blog and paper.
- Observed: the 1940s show snow falling on only 2.2% of town Christmases, far below the 1950s (13.2%); ERA5 before 1950 is
  less constrained by observations (Bell et al. 2021 cover the 1950s extension). The falling-snow trend depends on the
  start year (1940: OR 0.94, 1950: 0.83, 1960: 0.80 significant).

## References verified online (2026)
Hersbach et al. 2020 QJRMS 146(730) 1999-2049 (ADS); Bell et al. 2021 QJRMS 147(741) 4186-4227 (NOAA repository);
Munoz-Sabater et al. 2021 ESSD 13(9) 4349-4383 (journal page); Zippenfenig 2023 Zenodo 10.5281/zenodo.7970649,
Hersbach et al. 2023 ERA5 dataset 10.24381/cds.adbb2d47, Munoz Sabater 2019 ERA5-Land dataset 10.24381/cds.e2161bac (Open-Meteo
docs); Kay 2016 PPG 40(5) 676-698 (NORA); Brown 2019 IJC 39(12) 4611-4626 and Brown 2020 Weather 75(2) 61-66 (Dundee
portal); Kouki et al. 2023 TC 17(12) 5007-5026; Monteiro and Morin 2023 TC 17(8) 3617-3660 (journal pages); Marty 2008 GRL
doi 10.1029/2008GL033998 (record; volume 35 and article L12501 from the search result, abstract truncated); Brown and
Robinson 2011 TC 5 219 (journal); Hollis et al. 2019 GDJ doi 10.1002/gdj3.78 (title, year, journal, DOI; volume and pages
not reachable, cited without pages); Kendon et al. 2025 IJC 45(S1) 1-72 (NORA); Lindsey and Osborne 2022 climate.gov
(page); Met Office 2024 press release and learning page; Mann 1945 Econometrica 13 245-259; Sen 1968 JASA 63 1379-1389;
Wilson 1927 JASA 22 209-212; Cameron, Gelbach and Miller 2011 JBES 29(2) 238-249 (RePEc); Seabold and Perktold 2010
SciPy proceedings (doi 10.25080/Majora-92bf1922-011). Kendall 1975 (book, Griffin) cited from standard knowledge.
Blocked: open-meteo.com docs page and api.crossref.org (WebFetch permission timed out); Wiley Weather author page.
