"""Code the 207 included studies from titles and abstracts with a predefined keyword dictionary.

Reproduces results/coded_studies.csv, results/summary.json and results/agreement.json of the review
(Sect. 2.3 and Sect. 3). Run scripts/fetch_abstracts.py first; without work/abstracts.json all studies are coded from
their titles only.

Usage: python scripts/code_studies.py [out_dir]          (default out_dir: results_rerun)
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "results_rerun")
studies = list(csv.DictReader(open("data/included_studies.csv", encoding="utf-8")))
ab = Path("work/abstracts.json")
cache = json.loads(ab.read_text(encoding="utf-8")) if ab.exists() else {}
if not cache:
    print("warning: work/abstracts.json not found; coding from titles only")

# ---- keyword dictionary (identical to the one used in the review)
ARCH = {
    "CNN classifier": r"\bcnns?\b|convolutional|resnet|vgg|inception|densenet|efficientnet|mobilenet|xception|alexnet|googlenet|resnext|squeeze[- ]and[- ]excitation|\bsenet\b",
    "Object detector": r"\byolo|faster r-?cnn|cascade r-?cnn|retinanet|\bssd\b|centernet|\bdetr\b|object detection|bounding box|detector",
    "Segmentation network": r"u-?net|mask r-?cnn|deeplab|\bfcn\b|segnet|semantic segmentation|instance segmentation|panoptic",
    "Transformer": r"transformer|\bvit\b|vision transformer|swin|\bdeit\b|\bdetr\b|self-attention",
    "Generative model": r"\bgans?\b|generative adversarial|pix2pix|cyclegan|diffusion model|denoising diffusion|\bddpm\b|latent diffusion|\bvae\b|variational auto-?encoder",
    "Foundation, SSL or language model": r"self-supervised|contrastive learning|foundation model|segment anything|\bsam\b|\bclip\b|vision[- ]language|large language model|\bllms?\b|\bgpt",
    "Graph or recurrent model": r"graph neural|\bgnn|graph convolution|\blstm|recurrent|\brnn\b|\bgru\b",
}
PUBLIC = r"bioimlab|crcn-?ne|autokary|chromseg|cir-?net|chrcluster|kaggle|public(ly)? (available )?data ?set|open[- ]access data ?set|open data ?set|benchmark data ?set|pki-?3|passau|tcvgh|taichung veterans|overlapping chromosome data|chromosome-images"
PRIVATE = r"hospital|clinical (data|dataset|images|samples|cases)|collected (from|at|in)|in-house|private data|our own|medical (center|centre|university)|laboratory of|department of|patients?\b|prenatal diagnosis cent|retrospective"
SPEC = {"Amniotic fluid / prenatal": r"amniotic|amniocyte|prenatal|fetal|fetus|chorionic",
        "Peripheral blood": r"peripheral blood|lymphocyte|blood (sample|culture|specimen)",
        "Bone marrow / oncology": r"bone marrow|leuk(a)?emia|lymphoma|myelo|cancer|tumou?r|hematolog|haematolog|oncolog"}
BAND = {"G-band": r"g-?band|giemsa|g-banded|trypsin", "Q-band / DAPI": r"q-?band|quinacrine|dapi", "R-band": r"r-?band",
        "Multicolour FISH": r"m-?fish|multicolou?r fish|spectral karyotyp|\bfish\b"}
EXTERNAL = r"external (validation|test|dataset|data)|cross-?(hospital|institution|institutional|site|center|centre|domain)|multi-?(cent(er|re)|institution|site|hospital)|independent (test|validation|cohort|dataset) |another hospital|different hospital|other hospital|unseen (hospital|domain|dataset)|domain (shift|adaptation|generali[sz]ation)|generali[sz]ation to"
PATIENT = r"patient-?(level|wise)|split by patient|per-?patient|patient[- ]independent|subject-?(level|wise)"
CODE = r"github|code (is|are) (publicly )?available|source code|open-?source(d)? (code|implementation)|publicly available at"
PREPRINT = r"arxiv|biorxiv|medrxiv|research square|ssrn|preprint"
CONF = r"conference|proceedings|symposium|workshop|congress|\bicassp|\bmiccai|\bisbi|\bembc|\biccv|\bcvpr|\beccv|\bkdd|\bbibm|\bicip|\bbigdata|lecture notes"


def has(rx, t):
    return re.search(rx, t, flags=re.I) is not None


def period(y):
    return "2017–2020" if y <= 2020 else "2021–2023" if y <= 2023 else "2024–2026"


rows = []
for s in studies:
    c = cache.get(s["doi"], {})
    abstract = c.get("openalex_abstract") or c.get("s2_abstract") or ""
    t = (s["title"] or "") + " . " + abstract
    v = c.get("venue") or s["source"] or ""
    vtype = c.get("venue_type") or ""
    if has(PREPRINT, v) or vtype == "repository":
        venue = "Preprint"
    elif vtype == "conference" or has(CONF, v):
        venue = "Conference"
    elif v:
        venue = "Journal"
    else:
        venue = "Journal" if s["origin"] == "database" else "Preprint" if has(PREPRINT, s["doi"]) else "Journal"
    pub, priv = has(PUBLIC, t), has(PRIVATE, t)
    data = "Public and private" if pub and priv else "Public only" if pub else "Private only" if priv else "Not stated"
    y = int(s["year"])
    r = {"id": s["id"], "year": y, "period": period(y), "task": s["task"], "doi": s["doi"], "has_abstract": bool(abstract),
         "venue": venue, "data": data, "external": has(EXTERNAL, t), "patient_split": has(PATIENT, t), "code": has(CODE, t)}
    for k, rx in ARCH.items():
        r["arch:" + k] = has(rx, t)
    for k, rx in SPEC.items():
        r["spec:" + k] = has(rx, t)
    for k, rx in BAND.items():
        r["band:" + k] = has(rx, t)
    rows.append(r)

OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "coded_studies.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

per = Counter(r["period"] for r in rows)
summ = {"N": len(rows), "with_abstract": sum(r["has_abstract"] for r in rows), "period_n": dict(per),
        "venue": dict(Counter(r["venue"] for r in rows)), "data": dict(Counter(r["data"] for r in rows)),
        "external": sum(r["external"] for r in rows), "patient_split": sum(r["patient_split"] for r in rows),
        "code": sum(r["code"] for r in rows)}
summ["arch_by_period"] = {k: {p: sum(1 for r in rows if r["period"] == p and r["arch:" + k]) for p in per} for k in ARCH}
summ["arch_total"] = {k: sum(r["arch:" + k] for r in rows) for k in ARCH}
summ["spec"] = {k: sum(r["spec:" + k] for r in rows) for k in SPEC}
summ["band"] = {k: sum(r["band:" + k] for r in rows) for k in BAND}
summ["external_by_task"] = {t: [sum(1 for r in rows if r["task"] == t and r["external"]), sum(1 for r in rows if r["task"] == t)]
                            for t in sorted(set(r["task"] for r in rows))}
summ["data_by_period"] = {p: dict(Counter(r["data"] for r in rows if r["period"] == p)) for p in per}
summ["external_by_period"] = {p: [sum(1 for r in rows if r["period"] == p and r["external"]), per[p]] for p in per}
(OUT / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- agreement with the manual full-text extraction table (matched by DOI)
coded = {r["doi"]: r for r in rows if r["doi"]}
agree, matched = defaultdict(lambda: [0, 0]), 0
for m in csv.DictReader(open("data/core_validation.csv", encoding="utf-8")):
    if m["doi"] not in coded:
        continue
    matched += 1; r = coded[m["doi"]]
    agree["external"][0] += int((m["manual_external"] == "True") == r["external"]); agree["external"][1] += 1
    auto_pub = r["data"] in ("Public only", "Public and private")
    agree["public data"][0] += int((m["manual_public"] == "True") == auto_pub); agree["public data"][1] += 1
(OUT / "agreement.json").write_text(json.dumps({"matched": matched, **dict(agree)}, ensure_ascii=False, indent=1), encoding="utf-8")
print("coded", len(rows), "studies; with abstract:", summ["with_abstract"], "| agreement:", matched, dict(agree))
