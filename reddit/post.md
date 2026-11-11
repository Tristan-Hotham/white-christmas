**Title:** [OC] What are the odds of a white Christmas where you live? Snow lay on about 1 Christmas Day in 11 across 116 UK towns since 1950. In Bournemouth: never.

**Body:**

I took every Christmas Day from 1940 to 2025 in 116 UK towns from weather reanalysis (ERA5 and ERA5-Land) and counted when snow fell, when it lay on the ground (more than 1 cm), and both.

- Snow lying: 8.8% of town Christmases since 1950. Snow falling: 8.8% since 1940.
- London: 5 of 76 Christmases with snow lying. Glasgow 13, Edinburgh 11, Bournemouth 0.
- Every 100 m of height multiplies the odds by about 3.4; every degree north by about 1.6.
- It comes in a few big years: in 2010 snow lay in 96 of the 116 towns, in 1981 in 94. The reanalysis puts the Met Office's four widespread snowy Christmases since 1960 at ranks 1, 2, 3 and 5 of 66 years.
- Rarer? Probably: 10.4% of town Christmases had lying snow 1950 to 1987, 7.3% 1988 to 2025. But with 2009 and 2010 in the data my main trend model can't rule out no change.

Interactive map with every town's Christmas calendar: https://maps.tristanhotham.com/white-christmas/

**Source comment:**

Data: Open-Meteo Historical Weather API (ERA5, ERA5-Land reanalysis from Copernicus/ECMWF), CC BY 4.0; Met Office white Christmas record for the check. Method: logistic regression with town fixed effects, errors clustered by year, plan written before the analysis; Mann-Kendall test on the national series. Caveat: reanalysis averages over cells about 9 to 11 km across and puts too much snow on hills, so Highland towns look snowier than their streets. Tools: Python (pandas, statsmodels, matplotlib), MapLibre. Paper and code: https://github.com/Tristan-Hotham/white-christmas
