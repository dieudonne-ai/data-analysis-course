"""Generate the PDF diagrams for module 04 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, color="#dbeafe"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10)


def cleaning_pipeline():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("Data cleaning pipeline", fontsize=15, weight="bold")
    steps = [("Raw data", "#fecaca"), ("Remove\nduplicates", "#dbeafe"),
             ("Fix text\n& types", "#dbeafe"), ("Handle\nmissing", "#dbeafe"),
             ("Remove invalid\n& outliers", "#dbeafe"), ("Clean data", "#bbf7d0")]
    for i, (s, c) in enumerate(steps):
        x = 0.2 + i * 1.95
        box(ax, x, 1.2, 1.6, 1.3, s, c)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.92, 1.85), xytext=(x + 1.65, 1.85),
                        arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(6, 0.4, "Always keep the raw file untouched; write the result to a new file.",
            ha="center", style="italic")
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


def outlier_iqr():
    data = [10, 3, 3, 1, 5, 2, 400]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.boxplot(data[:-1], vert=False, positions=[1], widths=0.5)
    ax.scatter([400], [1], color="red", zorder=3)
    ax.axvline(15, color="red", ls="--")
    ax.text(17, 1.3, "upper fence = Q3 + 1.5 x IQR", color="red", fontsize=9)
    ax.annotate("outlier (400)", xy=(400, 1), xytext=(250, 1.25),
                arrowprops=dict(arrowstyle="->"))
    ax.set_yticks([]); ax.set_xlabel("quantity")
    ax.set_title("Detecting outliers with the IQR rule", weight="bold")
    fig.savefig(OUT / "outlier_iqr.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline()
    outlier_iqr()
