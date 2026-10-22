"""Generate the PDF diagram for module 04 (run from anywhere)."""
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
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("The data cleaning pipeline", fontsize=15, weight="bold")
    steps = [("Raw data", "#fecaca"), ("Remove\nduplicates", "#dbeafe"),
             ("Fix text\n(strip, case)", "#dbeafe"), ("Handle\nmissing values", "#dbeafe"),
             ("Treat\noutliers", "#dbeafe"), ("Fix types", "#dbeafe"),
             ("Clean data", "#bbf7d0")]
    w = 1.45
    for i, (t, c) in enumerate(steps):
        x = 0.2 + i * 1.65
        box(ax, x, 1.5, w, 1.0, t, c)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.62, 2.0), xytext=(x + w + 0.03, 2.0),
                        arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(6, 0.7, "Always check df.shape and df.isna().sum() after each step",
            ha="center", style="italic")
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


def missing_strategies():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Missing values: which strategy?", fontsize=15, weight="bold")
    box(ax, 3.5, 4.6, 3, 0.8, "Value is missing", "#fde68a")
    box(ax, 0.3, 2.6, 2.8, 1.0, "Few rows affected,\nrow not usable", "#f3f4f6")
    box(ax, 3.6, 2.6, 2.8, 1.0, "Numeric column,\nrow still useful", "#f3f4f6")
    box(ax, 6.9, 2.6, 2.8, 1.0, "Category column", "#f3f4f6")
    box(ax, 0.3, 0.7, 2.8, 1.0, "df.dropna(subset=[...])", "#bbf7d0")
    box(ax, 3.6, 0.7, 2.8, 1.0, "fillna(median / mean)", "#bbf7d0")
    box(ax, 6.9, 0.7, 2.8, 1.0, "fillna('Unknown')", "#bbf7d0")
    for x in (1.7, 5.0, 8.3):
        ax.annotate("", xy=(x, 3.65), xytext=(5.0, 4.55), arrowprops=dict(arrowstyle="->"))
        ax.annotate("", xy=(x, 1.75), xytext=(x, 2.55), arrowprops=dict(arrowstyle="->"))
    fig.savefig(OUT / "missing_strategies.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline()
    missing_strategies()
