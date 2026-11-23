"""Fetch abstracts and venue metadata of the included studies by DOI.

OpenAlex is queried first (abstract, venue name and venue type); Semantic Scholar fills abstracts that OpenAlex lacks.
Only DOIs are sent. Results are cached in work/abstracts.json, which is not part of the repository because abstracts
are copyrighted by their publishers.

Usage: python scripts/fetch_abstracts.py [data/included_studies.csv] [work/abstracts.json]
"""
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

INC = Path(sys.argv[1] if len(sys.argv) > 1 else "data/included_studies.csv")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "work/abstracts.json")
OUT.parent.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "systematic-review-coding/1.0"}
studies = list(csv.DictReader(open(INC, encoding="utf-8")))
cache = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def inverted_to_text(inv):
    if not inv:
        return ""
    return " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))


todo = [s["doi"] for s in studies if s["doi"] and s["doi"] not in cache]
for k in range(0, len(todo), 40):
    batch = todo[k:k + 40]
    flt = "doi:" + "|".join("https://doi.org/" + d for d in batch)
    data = get("https://api.openalex.org/works?per-page=50&filter=" + urllib.parse.quote(flt, safe=":|/"))
    for w in data.get("results", []):
        d = (w.get("doi") or "").lower().replace("https://doi.org/", "")
        src = (w.get("primary_location") or {}).get("source") or {}
        cache[d] = {"openalex_abstract": inverted_to_text(w.get("abstract_inverted_index")),
                    "venue": src.get("display_name") or "", "venue_type": src.get("type") or ""}
    print(f"OpenAlex batch {k // 40 + 1}: {len(data.get('results', []))}/{len(batch)}")
    time.sleep(1)

for s in studies:
    d = s["doi"]
    if not d or cache.get(d, {}).get("openalex_abstract") or "s2_abstract" in cache.get(d, {}):
        continue
    try:
        r = get("https://api.semanticscholar.org/graph/v1/paper/DOI:" + d + "?fields=abstract")
        cache.setdefault(d, {})["s2_abstract"] = r.get("abstract") or ""
    except Exception as e:  # noqa: BLE001
        print("Semantic Scholar miss", d, str(e)[:60])
    time.sleep(1.2)

OUT.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
n_oa = sum(1 for s in studies if cache.get(s["doi"], {}).get("openalex_abstract"))
n_s2 = sum(1 for s in studies if not cache.get(s["doi"], {}).get("openalex_abstract") and cache.get(s["doi"], {}).get("s2_abstract"))
print(f"abstracts: OpenAlex {n_oa}, Semantic Scholar {n_s2}, none {len(studies) - n_oa - n_s2}")
