"""Summarize the manual full-text codes of the 87 core method studies (data source and external validation).

data/core_studies_manual.csv holds one row per included method study discussed in Sects. 6-12 of the review.
data_source: C = clinical/private data only, P = public data only, B = both, U = not reported or synthetic.
external_validation: Y = tested on data from an institution, centre or banding method not used for training.

Usage: python scripts/core_coding.py [out_dir]          (default out_dir: results_rerun)
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "results_rerun")
OUT.mkdir(parents=True, exist_ok=True)
studies = []
for r in csv.DictReader(open("data/core_studies_manual.csv", encoding="utf-8")):
    y = int(r["year"])
    studies.append({"key": r["key"], "year": y,
                    "period": "2017–2020" if y <= 2020 else "2021–2023" if y <= 2023 else "2024–2026",
                    "data": r["data_source"], "external": r["external_validation"] == "Y"})
per = Counter(s["period"] for s in studies)
summ = {"n_core": len(studies), "period_n": dict(per), "data": dict(Counter(s["data"] for s in studies)),
        "external": sum(s["external"] for s in studies),
        "data_by_period": {p: dict(Counter(s["data"] for s in studies if s["period"] == p)) for p in per},
        "external_by_period": {p: [sum(1 for s in studies if s["period"] == p and s["external"]), per[p]] for p in per},
        "external_keys": [s["key"] for s in studies if s["external"]]}
(OUT / "core_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "core_coded.json").write_text(json.dumps(studies, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(summ, ensure_ascii=False, indent=1))
