"""Quantitative overview figure (Fig. 3): model families, venues, data sources and external validation.

Usage: python scripts/make_quant_figure.py <results_dir> <out_stem> [--print]   (writes <out_stem>.pdf and .png)
Example: python scripts/make_quant_figure.py results figures/Fig3_quantitative_overview --print
--print draws the published layout at the 13.1-cm text width with all text at 8 pt or larger; without it the
script draws an earlier, larger 2 x 2 layout.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

AD, STEM = Path(sys.argv[1]), sys.argv[2]
PRINT = "--print" in sys.argv[3:]
rows = list(csv.DictReader(open(AD / "coded_studies.csv", encoding="utf-8-sig")))
core = json.loads((AD / "core_coded.json").read_text(encoding="utf-8"))
P = ["2017–2020", "2021–2023", "2024–2026"]
PS = ["2017–20", "2021–23", "2024–26"]
n207 = Counter(r["period"] for r in rows)
ncore = Counter(s["period"] for s in core)

if PRINT:
    plt.rcParams.update({"font.family": "Arial", "font.size": 8.5, "axes.labelsize": 8.5, "axes.titlesize": 9,
                         "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.dpi": 600, "pdf.fonttype": 42, "axes.linewidth": 0.8})
    NUM_FS = 8
else:
    plt.rcParams.update({"font.family": "Arial", "font.size": 10.5, "axes.labelsize": 11, "axes.titlesize": 11.5,
                         "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 9.5, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.dpi": 600, "pdf.fonttype": 42})
    NUM_FS = 9.5
PER_COL = ["#BBD4EA", "#5B9BD5", "#1F4E79"]

if PRINT:
    # Print layout for the 13.1-cm text width: (a) across the top, (b)-(d) side by side below, all text >= 8 pt.
    FW, FH = 5.1, 5.25
    fig = plt.figure(figsize=(FW, FH))

    def axin(l, b, w, h):
        return fig.add_axes([l / FW, b / FH, w / FW, h / FH])

    fam = ["CNN classifier", "Segmentation network", "Object detector", "Transformer", "Generative model",
           "Foundation, SSL or language model"]
    lab = ["CNN classifier", "Segmentation net", "Object detector", "Transformer", "Generative model",
           "Foundation/SSL/LLM"]
    ax = axin(1.2, 3.35, 3.8, 1.6); y = np.arange(len(fam))[::-1]; h = 0.26
    for k, p in enumerate(P):
        v = [100 * sum(1 for r in rows if r["period"] == p and r["arch:" + f] == "True") / n207[p] for f in fam]
        ax.barh(y + (1 - k) * h, v, h, color=PER_COL[k], edgecolor="black", linewidth=0.4,
                label=f"{p} (n = {n207[p]})")
    ax.set_yticks(y); ax.set_yticklabels(lab); ax.set_xlabel("Studies in period (%)"); ax.set_xlim(0, 70)
    ax.set_title("(a) Model families, all 207 studies", loc="left", x=-0.3, fontsize=9)
    ax.legend(frameon=False, loc="lower right", handlelength=1.0)
    PL = ["'17–20", "'21–23", "'24–26"]

    def stacked_p(ax, cats, colors, count, n_fn, title, labels, dark):
        bottom = np.zeros(3)
        for c, col, ll in zip(cats, colors, labels):
            v = np.array([100 * count(p, c) / n_fn(p) for p in P])
            ax.bar(range(3), v, 0.66, bottom=bottom, color=col, edgecolor="black", linewidth=0.4, label=ll)
            for i, (b, vv) in enumerate(zip(bottom, v)):
                if vv >= 8:
                    ax.text(i, b + vv / 2, f"{vv:.0f}", ha="center", va="center", fontsize=8,
                            color="white" if col in dark else "black")
            bottom += v
        ax.set_ylim(0, 100); ax.set_ylabel("Share of studies (%)"); ax.set_title(title, loc="left", x=-0.32, fontsize=9)
        ax.set_xticks(range(3)); ax.set_xticklabels([f"{s}\nn = {n_fn(p)}" for s, p in zip(PL, P)])
        ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(-0.32, -0.3), ncol=1, handlelength=1.0,
                  labelspacing=0.25, borderaxespad=0)

    stacked_p(axin(0.45, 1.05, 1.18, 1.7), ["Journal", "Conference", "Preprint"], ["#0072B2", "#E69F00", "#999999"],
              lambda p, c: sum(1 for r in rows if r["period"] == p and r["venue"] == c), lambda p: n207[p],
              "(b) Venue, all studies", ["Journal", "Conference", "Preprint"], {"#0072B2"})
    stacked_p(axin(2.15, 1.05, 1.18, 1.7), ["C", "P", "B", "U"], ["#D55E00", "#009E73", "#56B4E9", "#BBBBBB"],
              lambda p, c: sum(1 for s in core if s["period"] == p and s["data"] == c), lambda p: ncore[p],
              "(c) Data source, core studies", ["Clinical/private only", "Public only", "Both", "Not reported/synthetic"],
              {"#D55E00", "#009E73"})
    ax = axin(3.85, 1.05, 1.18, 1.7); x = np.arange(3); w = 0.36
    nc = [sum(1 for s in core if s["period"] == p and s["external"]) for p in P]
    na = [sum(1 for r in rows if r["period"] == p and r["external"] == "True") for p in P]
    b1 = ax.bar(x - w / 2, [100 * a / ncore[p] for a, p in zip(nc, P)], w, color="#1F4E79", edgecolor="black",
                linewidth=0.4, label="Core studies (full text)")
    b2 = ax.bar(x + w / 2, [100 * a / n207[p] for a, p in zip(na, P)], w, color="#5B9BD5", edgecolor="black",
                linewidth=0.4, label="All studies (abstract)")
    for bars, nums in ((b1, nc), (b2, na)):
        for bar, n in zip(bars, nums):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, str(n), ha="center", va="bottom",
                    fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(PL); ax.set_ylabel("With external validation (%)"); ax.set_ylim(0, 40)
    ax.set_title("(d) External validation", loc="left", x=-0.32, fontsize=9)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(-0.32, -0.3), ncol=1, handlelength=1.0,
              labelspacing=0.25, borderaxespad=0)
    fig.savefig(STEM + ".pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(STEM + ".png", bbox_inches="tight", pad_inches=0.02, dpi=600)
    print("saved", STEM)
    sys.exit(0)

fig, axs = plt.subplots(2, 2, figsize=(7.5, 7.6))

# (a) model families by period, horizontal bars
fam = ["CNN classifier", "Segmentation network", "Object detector", "Transformer", "Generative model",
       "Foundation, SSL or language model"]
lab = ["CNN classifier", "Segmentation net", "Object detector", "Transformer", "Generative model", "Foundation/SSL/LLM"]
ax = axs[0, 0]; y = np.arange(len(fam))[::-1]; h = 0.26
for k, p in enumerate(P):
    v = [100 * sum(1 for r in rows if r["period"] == p and r["arch:" + f] == "True") / n207[p] for f in fam]
    ax.barh(y + (1 - k) * h, v, h, color=PER_COL[k], edgecolor="black", linewidth=0.5, label=f"{PS[k]} (n = {n207[p]})")
ax.set_yticks(y); ax.set_yticklabels(lab); ax.set_xlabel("Studies in period (%)"); ax.set_xlim(0, 70)
ax.set_title("(a) Model families" if PRINT else "(a) Model families (all 207 studies)", loc="left")
ax.legend(frameon=False, loc="lower right")


def stacked(ax, cats, colors, count, n_fn, title, labels, dark):
    bottom = np.zeros(3)
    for c, col, ll in zip(cats, colors, labels):
        v = np.array([100 * count(p, c) / n_fn(p) for p in P])
        ax.bar(range(3), v, 0.62, bottom=bottom, color=col, edgecolor="black", linewidth=0.5, label=ll)
        for i, (b, vv) in enumerate(zip(bottom, v)):
            if vv >= 8:
                ax.text(i, b + vv / 2, f"{vv:.0f}", ha="center", va="center", fontsize=NUM_FS,
                        color="white" if col in dark else "black")
        bottom += v
    ax.set_ylim(0, 100); ax.set_ylabel("Share of studies (%)"); ax.set_title(title, loc="left")
    ax.set_xticks(range(3)); ax.set_xticklabels([f"{s}\n(n = {n_fn(p)})" for s, p in zip(PS, P)])
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)


stacked(axs[0, 1], ["Journal", "Conference", "Preprint"], ["#0072B2", "#E69F00", "#999999"],
        lambda p, c: sum(1 for r in rows if r["period"] == p and r["venue"] == c), lambda p: n207[p],
        "(b) Publication venue" if PRINT else "(b) Venue (all 207 studies)", ["Journal", "Conference", "Preprint"], {"#0072B2"})
stacked(axs[1, 0], ["C", "P", "B", "U"], ["#D55E00", "#009E73", "#56B4E9", "#BBBBBB"],
        lambda p, c: sum(1 for s in core if s["period"] == p and s["data"] == c), lambda p: ncore[p],
        "(c) Data source, core studies" if PRINT else "(c) Data source (%d core studies)" % len(core), ["Clinical/private only", "Public only", "Both", "Not reported/synthetic"],
        {"#D55E00", "#009E73"})
# (d) external validation
ax = axs[1, 1]; x = np.arange(3); w = 0.36
nc = [sum(1 for s in core if s["period"] == p and s["external"]) for p in P]
na = [sum(1 for r in rows if r["period"] == p and r["external"] == "True") for p in P]
b1 = ax.bar(x - w / 2, [100 * a / ncore[p] for a, p in zip(nc, P)], w, color="#1F4E79", edgecolor="black", linewidth=0.5,
            label="Core studies (full text)")
b2 = ax.bar(x + w / 2, [100 * a / n207[p] for a, p in zip(na, P)], w, color="#5B9BD5", edgecolor="black", linewidth=0.5,
            label="All studies (abstract)")
for bars, nums in ((b1, nc), (b2, na)):
    for bar, n in zip(bars, nums):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, str(n), ha="center", va="bottom", fontsize=NUM_FS)
ax.set_xticks(x); ax.set_xticklabels(PS); ax.set_ylabel("With external validation (%)"); ax.set_ylim(0, 40)
ax.set_title("(d) External validation" if PRINT else "(d) External or cross-site validation", loc="left")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
fig.tight_layout(pad=0.8, w_pad=1.2, h_pad=1.0)
fig.savefig(STEM + ".pdf", bbox_inches="tight"); fig.savefig(STEM + ".png", bbox_inches="tight", dpi=300)
print("saved", STEM)
