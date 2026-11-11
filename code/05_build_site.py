"""Step 5: index.html from code/page_template.html and code/page.css, filled from data/results.json, with the full-screen
snippet. 10.5281/zenodo.24132735, https://doi.org/10.5281/zenodo.24132735 and https://blog.tristanhotham.com/2026/10/31/white-christmas/ are left for the publisher to fill."""
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
# facts stated in words in the page text
assert R["towns"]["Bournemouth"]["lie_k"] == 0 and R["n_towns_lie_never"] == 1
assert all(R["towns"][t]["nation"] == "Scotland" for t in R["towns"] if (R["towns"][t]["lie_last"] or 0) > 2010)
assert R["annual"]["y2024"]["n_lie"] == 0 and R["annual"]["y2025"]["n_lie"] == 0
assert sorted(R["V1"]["ranks"].values()) == [1, 2, 3, 5] and R["V1"]["n_years"] == 66
assert R["M1_lie"]["lo"] < 1 < R["M1_lie"]["hi"] and R["MK_lie"]["p"] < 0.05 and R["robust_no0910_lie"]["hi"] < 1
assert R["n_towns_fall_never"] == 0
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{CSS}}", open(os.path.join(ROOT, "code", "page.css"), encoding="utf-8").read())
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "2026a")
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "pre-registered"):
    assert bad not in vis, bad
assert '<script src="https://maps.tristanhotham.com/assets/site-nav.js" defer></script>\n</body>' in t
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
