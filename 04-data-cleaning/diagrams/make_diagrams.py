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
    steps = ["Raw data", "Duplicates\ndrop_duplicates", "Text & types\nstr.strip,\nto_datetime",
             "Invalid values\n(negatives)", "Missing values\nfillna / dropna",
             "Outliers\nIQR rule", "Clean data"]
    colors = ["#fecaca"] + ["#dbeafe"] * 5 + ["#bbf7d0"]
    w = 1.5
    for i, (s, c) in enumerate(zip(steps, colors)):
        x = 0.1 + i * 1.7
        box(ax, x, 1.2, w, 1.4, s, c)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.7, 1.9), xytext=(x + w + 0.05, 1.9),
                        arrowprops=dict(arrowstyle="->", lw=1.5))
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


def missing_strategies():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Which strategy for missing values?", fontsize=15, weight="bold")
    box(ax, 3.5, 4.6, 3, 0.9, "Value is missing", "#fde68a")
    box(ax, 0.3, 2.6, 2.8, 1.1, "Few rows, random\n-> dropna()", "#dbeafe")
    box(ax, 3.6, 2.6, 2.8, 1.1, "Numeric column\n-> fillna(median)", "#dbeafe")
    box(ax, 6.9, 2.6, 2.8, 1.1, "Category column\n-> fillna('Unknown')", "#dbeafe")
    for x in (1.7, 5.0, 8.3):
        ax.annotate("", xy=(x, 3.75), xytext=(5, 4.55),
                    arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(5, 1.3, "Always report how many values you changed.",
            ha="center", style="italic")
    fig.savefig(OUT / "missing_strategies.pdf", bbox_inches="tight")


def outlier_iqr():
    fig, ax = plt.subplots(figsize=(8, 4))
    data = [1, 2, 3, 3, 5, 5, 7, 10, 400]
    ax.boxplot(data, orientation='horizontal', whis=1.5)
    ax.set_title("IQR rule: 400 lies beyond Q3 + 1.5 x IQR", fontsize=13, weight="bold")
    ax.set_xlabel("quantity")
    fig.savefig(OUT / "outlier_iqr.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline(); missing_strategies(); outlier_iqr()
