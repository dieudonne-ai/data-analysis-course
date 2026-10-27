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
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.5); ax.axis("off")
    ax.set_title("Data cleaning pipeline", fontsize=15, weight="bold")
    steps = ["Raw data", "Missing values\nisna, fillna,\ndropna", "Duplicates\ndrop_duplicates",
             "Text & types\nstr.strip,\nastype", "Invalid values\nfilter / clip", "Clean data"]
    colors = ["#fecaca"] + ["#dbeafe"] * 4 + ["#bbf7d0"]
    for i, (s, c) in enumerate(zip(steps, colors)):
        x = 0.1 + i * 1.8
        box(ax, x, 1.0, 1.5, 1.3, s, c)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.78, 1.65), xytext=(x + 1.55, 1.65),
                        arrowprops=dict(arrowstyle="->", lw=2))
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline()
