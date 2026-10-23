"""Generate the PDF diagrams for module 04 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, color="#dbeafe", fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def cleaning_pipeline():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("Data cleaning pipeline", fontsize=15, weight="bold")
    steps = ["Raw data\nsales_messy.csv", "Remove\nduplicates", "Fix text\nstrip / case",
             "Parse\ndates", "Handle invalid\n& missing", "Flag\noutliers", "Clean data\nsales_clean.csv"]
    colors = ["#fecaca"] + ["#dbeafe"] * 5 + ["#bbf7d0"]
    for i, (s, c) in enumerate(zip(steps, colors)):
        x = 0.1 + i * 1.7
        box(ax, x, 1.2, 1.4, 1.3, s, c, fs=9)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.7, 1.85), xytext=(x + 1.4, 1.85),
                        arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(6, 0.5, "Always keep the raw file untouched: write the result to a new file.",
            ha="center", style="italic")
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


def missing_strategies():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("Which missing-value strategy?", fontsize=15, weight="bold")
    box(ax, 3.5, 4.0, 3, 0.7, "Value is missing", "#fde68a")
    box(ax, 0.3, 2.3, 2.8, 0.9, "Few rows, random\n-> dropna()", "#dbeafe")
    box(ax, 3.6, 2.3, 2.8, 0.9, "Numeric column\n-> fillna(median)", "#dbeafe")
    box(ax, 6.9, 2.3, 2.8, 0.9, "Category / key field\n-> fillna('Unknown')", "#dbeafe")
    for x in (1.7, 5.0, 8.3):
        ax.annotate("", xy=(x, 3.25), xytext=(5, 4.0), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(5, 1.2, "Median beats mean when outliers exist. Document every choice.",
            ha="center", style="italic")
    fig.savefig(OUT / "missing_strategies.pdf", bbox_inches="tight")


def iqr_rule():
    import numpy as np
    prices = np.array([1.5, 1.5, 1.5, 1.5, 150.0])
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.boxplot([[1.5, 1.4, 1.6, 1.5, 1.7, 1.5], prices], orientation="horizontal",
               tick_labels=["typical", "with outlier"])
    ax.set_title("IQR rule: points beyond Q1-1.5*IQR / Q3+1.5*IQR are outliers",
                 fontsize=11, weight="bold")
    ax.set_xlabel("price")
    fig.savefig(OUT / "iqr_rule.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline(); missing_strategies(); iqr_rule()
