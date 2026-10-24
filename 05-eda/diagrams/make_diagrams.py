"""Generate the PDF diagrams for module 05 (run from anywhere)."""
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


def eda_loop():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 8); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("The EDA loop", fontsize=15, weight="bold")
    pos = [(0.5, 3.2, "Ask a question"), (5.0, 3.2, "Summarise / plot"),
           (5.0, 0.8, "Spot patterns\nor surprises"), (0.5, 0.8, "Refine the\nquestion")]
    for x, y, t in pos:
        box(ax, x, y, 2.5, 1.0, t, fs=11)
    for a, b in [((3.0, 3.7), (5.0, 3.7)), ((6.25, 3.2), (6.25, 1.8)),
                 ((5.0, 1.3), (3.0, 1.3)), ((1.75, 1.8), (1.75, 3.2))]:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", lw=1.8))
    fig.savefig(OUT / "eda_loop.pdf", bbox_inches="tight")


def groupby():
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("groupby = split - apply - combine", fontsize=15, weight="bold")
    box(ax, 0.1, 1.2, 2.2, 1.8, "Table\nA 10\nB 20\nA 30\nB 40", "#fde68a")
    box(ax, 4.0, 2.4, 2.2, 1.2, "Group A\n10, 30", "#dbeafe")
    box(ax, 4.0, 0.6, 2.2, 1.2, "Group B\n20, 40", "#dbeafe")
    box(ax, 8.4, 1.2, 2.4, 1.8, "Result\nA 20\nB 30", "#bbf7d0")
    for a, b in [((2.35, 2.4), (4.0, 3.0)), ((2.35, 1.8), (4.0, 1.2)),
                 ((6.25, 3.0), (8.4, 2.4)), ((6.25, 1.2), (8.4, 1.8))]:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(3.1, 0.15, "1. split", ha="center"); ax.text(7.3, 0.15, "3. combine", ha="center")
    ax.text(5.1, 3.85, "2. apply mean()", ha="center")
    fig.savefig(OUT / "groupby.pdf", bbox_inches="tight")


if __name__ == "__main__":
    eda_loop()
    groupby()
