# Deep learning for automated chromosome karyotyping: systematic review data and code

This repository contains the screening records, coded study tables, and analysis scripts behind the systematic review

> Lu C-H, Tseng J-J, Kuo C-E. *Deep Learning for Automated Chromosome Karyotyping: A Systematic Review from Metaphase Detection to Cross-Institutional Deployment.* Manuscript submitted for publication, 2026.

The review follows PRISMA 2020. Searches of Scopus, Web of Science Core Collection, IEEE Xplore, and PubMed (October 2026, publication years 2017–2026) returned 854 records. After 378 duplicates were removed, 476 records were screened, and 207 studies were included: 193 from the databases and 14 from citation chasing and preprint servers. The files here reproduce the PRISMA counts (Fig. 2a), the quantitative analysis in Sect. 3, and Fig. 3 of the review.

## Contents

| Path | Description |
|---|---|
| `data/screening_records.csv` | All 476 unique database records with the two screening passes (rule-based keyword screen and LLM-assisted reviewer screen), the consensus decision, final status, task category, and citation key in the review |
| `data/other_sources.csv` | The 14 studies added by citation chasing and preprint servers |
| `data/prisma_counts.json` | Counts behind the PRISMA 2020 flow diagram and the inter-pass agreement (Cohen's κ = 0.66) |
| `data/included_studies.csv` | The 207 included studies (ID, origin, year, title, source, DOI, task category, source of the abstract used for coding) |
| `data/core_studies_manual.csv` | Manual full-text codes of the 87 core method studies discussed in Sects. 6–12: data source and external validation |
| `data/core_validation.csv` | Manual full-text judgements (external validation, use of public data) used to check the abstract-level coding |
| `results/` | Outputs used in the paper: `coded_studies.csv`, `summary.json`, `agreement.json`, `core_coded.json`, `core_summary.json` |
| `figures/` | Fig. 3 of the review (PDF and PNG) |
| `scripts/` | `fetch_abstracts.py`, `code_studies.py`, `core_coding.py`, `make_quant_figure.py` |

Abstract texts are not redistributed because they are copyrighted by their publishers. `scripts/fetch_abstracts.py` downloads them again by DOI from the public OpenAlex and Semantic Scholar APIs; only DOIs are sent.

## Coding scheme

**Abstract-level coding (all 207 studies).** A predefined keyword dictionary, given in full in `scripts/code_studies.py`, is applied to each study's title and abstract. It assigns the study to one or more of seven model families: CNN classifier, segmentation network, object detector, transformer, generative model, self-supervised/foundation/language model, and graph or recurrent model. It also records whether public or clinical (private) data are named, and flags mentions of external or cross-site validation, patient-level splitting, code release, specimen type, and banding method. Venue type comes from the OpenAlex source record. Studies are grouped by year of first publication into 2017–2020, 2021–2023, and 2024–2026.

**Full-text coding (87 core studies).** Data source is coded as C (clinical/private only), P (public only), B (both), or U (not reported or synthetic). External validation is coded Y when a model was tested on data from an institution, centre, or banding method not used for training. The core set excludes papers that only released a dataset and studies cited only for context.

**Agreement.** On the 104 entries of the full-text extraction table that match an included study by DOI, the abstract-level coding agrees with the full-text coding for 87.5% of entries on external validation and 77.9% on the use of public data.

## Reproducing the analysis

Python 3.9 or later is required.

```bash
pip install -r requirements.txt
python scripts/fetch_abstracts.py                 # writes work/abstracts.json (needs internet)
python scripts/code_studies.py results_rerun      # abstract-level coding, summary and agreement
python scripts/core_coding.py results_rerun       # summary of the manual full-text codes
python scripts/make_quant_figure.py results_rerun figures/Fig3_rerun --print
```

To redraw Fig. 3 exactly as it appears in the manuscript, run `python scripts/make_quant_figure.py results figures/Fig3_check --print`. With the abstracts available when the review was written (OpenAlex for 159 studies, Semantic Scholar for 9, none for 39), `code_studies.py` reproduces `results/coded_studies.csv` exactly. The databases change over time, so a fresh download may return a slightly different set of abstracts.

## Licences

The code is released under the MIT License (`LICENSE`). The data tables and figure are released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0, `DATA_LICENSE.md`). Titles, DOIs, and venue names are bibliographic metadata of the cited works.

## Contact

Chih-En Kuo, Institute of Data Science and Information Computing, National Chung Hsing University, Taichung, Taiwan (cekuo@nchu.edu.tw).
