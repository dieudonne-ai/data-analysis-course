"""Generate the PDF diagram for module 06 (run from anywhere)."""
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


def choose_chart():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("Which chart should I use?", fontsize=15, weight="bold")
    box(ax, 3.7, 3.9, 2.6, 0.8, "What is your question?", "#fde68a", 12)
    rows = [("Distribution\nof one number", "Histogram\nBox plot"),
            ("Compare\ncategories", "Bar chart"),
            ("Relationship\nbetween 2 numbers", "Scatter plot"),
            ("Change\nover time", "Line chart")]
    for i, (q, c) in enumerate(rows):
        x = 0.3 + i * 2.45
        box(ax, x, 2.2, 2.2, 1.0, q)
        box(ax, x, 0.6, 2.2, 1.0, c, "#bbf7d0")
        ax.annotate("", xy=(x + 1.1, 3.2), xytext=(5.0, 3.9), arrowprops=dict(arrowstyle="->"))
        ax.annotate("", xy=(x + 1.1, 1.6), xytext=(x + 1.1, 2.2), arrowprops=dict(arrowstyle="->"))
    fig.savefig(OUT / "choose_chart.pdf", bbox_inches="tight")


if __name__ == "__main__":
    choose_chart()
