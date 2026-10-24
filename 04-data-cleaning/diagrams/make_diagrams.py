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
    ax.set_xlim(0, 11); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("Data cleaning pipeline", fontsize=15, weight="bold")
    steps = [("Raw data", "#fecaca"), ("Find problems\nisna, duplicated", "#dbeafe"),
             ("Missing values\ndrop / fill", "#dbeafe"), ("Duplicates\n& text", "#dbeafe"),
             ("Types & dates", "#dbeafe"), ("Outliers\nIQR rule", "#dbeafe"),
             ("Clean data", "#bbf7d0")]
    w = 1.35
    for i, (s, c) in enumerate(steps):
        x = 0.1 + i * 1.55
        box(ax, x, 1.5, w, 1.2, s, c)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.55, 2.1), xytext=(x + w + 0.03, 2.1),
                        arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(5.5, 0.6, "Always keep the raw file untouched; write cleaned output to a new file.",
            ha="center", style="italic")
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline()
