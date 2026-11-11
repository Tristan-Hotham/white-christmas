"""Shared paths, constants and helpers for the white-christmas study ("What are the odds of a white Christmas where you live?").

Inputs (read in place, never modified):
  RAW/white_christmas.json  Open-Meteo Historical Weather API (archive endpoint, default "best match" model: ERA5 0.25 deg
                            from 1940, ERA5-Land 0.1 deg from 1950, ECMWF IFS 9 km from 2017), retrieved 2026, CC BY 4.0.
                            {vars, towns: [[name, lat, lon] x 116], data: {"YYYY|Town": [snowfall_sum cm for 24, 25, 26 Dec,
                            snow_depth_max m for 24, 25, 26 Dec, temperature_2m_max C for 24, 25, 26 Dec, grid lat, grid lon,
                            elevation m]}}, 1940 to 2025. Snow depth is null 1940 to 1949 (ERA5-Land starts in 1950).
  GEO/lad23_bgc.geojson     UK local authority districts, December 2023 (ONS, Open Government Licence v3.0): nation of each
                            town and, with Ireland from Natural Earth, the coastline for distance to the sea.
  GEO/ne_10m_admin_0_countries.geojson  Natural Earth 1:10m countries (public domain): Ireland, for the land mask.
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("WC_RAW", "/home/claude/newdata/raw_new13")
GEO = os.environ.get("WC_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("WC_FONTS", "/home/claude/ref/fonts")
SCR = os.environ.get("WC_SCRATCH", "/home/claude/scratch/white-christmas")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
REL = os.path.join(ROOT, "release")
for d in (DATA, IMG, SCR):
    os.makedirs(d, exist_ok=True)

SLUG = "white-christmas"
TITLE = "What are the odds of a white Christmas where you live?"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
THEME = "Everyday life"

Y0, Y1 = 1940, 2025          # snowfall and temperature
YL0 = 1950                   # snow depth (ERA5-Land) starts
IFS_FROM = 2017              # Open-Meteo best match may use ECMWF IFS for snowfall/temperature from 2017
FALL_MIN = 0.0               # snowfall_sum on 25 Dec > 0 cm (smallest stored value 0.07 cm = 0.1 mm water)
FALL_ALT = 0.7               # sensitivity: >= 0.7 cm (1 mm water)
LIE_MIN = 0.01               # snow_depth_max on 25 Dec > 0.01 m
LIE_ALT = (0.0, 0.05)        # sensitivity: > 0 m, > 0.05 m
# Met Office station record (press release "Will it be a white Christmas?", 11 December 2024; white Christmas learning page)
MO_WIDESPREAD = [1981, 1995, 2009, 2010]          # > 40% of stations with snow lying at 9 am, since 1960
MO_LYING = {2009: 57, 2010: 83, 2020: 4, 2021: 0.5, 2022: 0, 2023: 0}       # % of stations (2021 "less than 1%")
MO_FALL = {2009: 13, 2010: 19, 2018: 0, 2019: 0, 2020: 6, 2021: 6, 2022: 9, 2023: 11}
NATIONS = {"E": "England", "S": "Scotland", "W": "Wales", "N": "Northern Ireland"}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "abs0": return f"{abs(float(v)):.0f}"
    if f == "abs1": return f"{abs(float(v)):.1f}"
    raise ValueError(f)


def wilson(k, n, z=1.959964):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def one_in(p):
    """'1 in N' for a probability (None if never)."""
    return None if not p else round(1 / p)
