"""Generate the PDF diagrams for module 04 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, color="#dbeafe"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10)


def cleaning_pipeline():
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("The data cleaning pipeline", fontsize=15, weight="bold")
    steps = [("Raw\ndata", "#fecaca"), ("Remove\nduplicates", "#dbeafe"),
             ("Fix text\n& types", "#dbeafe"), ("Handle\nmissing", "#dbeafe"),
             ("Treat\noutliers", "#dbeafe"), ("Clean\ndata", "#bbf7d0")]
    for i, (t, c) in enumerate(steps):
        box(ax, 0.2 + i * 1.95, 1.4, 1.6, 1.2, t, c)
        if i < len(steps) - 1:
            ax.annotate("", xy=(0.2 + (i + 1) * 1.95, 2.0),
                        xytext=(1.8 + i * 1.95, 2.0),
                        arrowprops=dict(arrowstyle="->", lw=1.5))
    code = ["drop_duplicates()", "str.strip().str.title()\nastype()",
            "isna() / fillna()\ndropna()", "IQR rule"]
    for i, t in enumerate(code):
        ax.text(0.2 + (i + 1) * 1.95 + 0.8, 0.8, t, ha="center", fontsize=8,
                family="monospace", color="#1e3a8a")
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


def outlier_iqr():
    rng = np.random.default_rng(0)
    data = np.concatenate([rng.normal(5, 2, 60).clip(1, 10), [22, 25]])
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.boxplot(data, vert=False, widths=0.5)
    ax.axvline(hi, color="red", ls="--")
    ax.text(hi + 0.3, 1.32, f"Q3 + 1.5·IQR = {hi:.1f}", color="red", fontsize=9)
    ax.annotate("outliers", xy=(23.5, 1.02), xytext=(16, 0.7),
                arrowprops=dict(arrowstyle="->"))
    ax.set_yticks([]); ax.set_xlabel("quantity")
    ax.set_title("Outlier detection with the IQR rule", weight="bold")
    fig.savefig(OUT / "outlier_iqr.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline()
    outlier_iqr()
