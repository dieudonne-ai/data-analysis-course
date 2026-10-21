"""Generate the PDF diagrams for module 03 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, color="#dbeafe"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)


def dataframe_anatomy():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Anatomy of a DataFrame", fontsize=15, weight="bold")
    cols = ["order_id", "product", "quantity", "price", "month"]
    rows = [[1, "Pen", 10, 1.5, "Jan"], [2, "Notebook", 3, 4.0, "Jan"],
            [3, "Pen", 5, 1.5, "Feb"]]
    x0, w, h = 2.0, 1.5, 0.7
    for j, c in enumerate(cols):
        box(ax, x0 + j * w, 4.0, w - 0.1, h, c, "#fde68a")
    for i, r in enumerate(rows):
        box(ax, 0.6, 3.1 - i * 0.8, 1.2, h, str(i), "#bbf7d0")
        for j, v in enumerate(r):
            box(ax, x0 + j * w, 3.1 - i * 0.8, w - 0.1, h, str(v))
    ax.text(1.2, 4.35, "index", ha="center", color="#166534", weight="bold")
    ax.annotate("column = Series\n(df['product'])", xy=(x0 + 1.4, 4.8),
                xytext=(5.0, 5.5), arrowprops=dict(arrowstyle="->"), fontsize=10)
    ax.annotate("row = df.loc[1]", xy=(x0 + 7.4, 2.3), xytext=(8.0, 1.0),
                arrowprops=dict(arrowstyle="->"), fontsize=10)
    ax.text(5, 0.2, "df.shape = (rows, columns)", ha="center", style="italic")
    fig.savefig(OUT / "dataframe_anatomy.pdf", bbox_inches="tight")


def loading_workflow():
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.5); ax.axis("off")
    ax.set_title("Loading workflow", fontsize=15, weight="bold")
    steps = ["Source\nCSV / Excel / JSON", "pd.read_*()", "Inspect\nhead, info,\ndescribe",
             "Select &\nfilter", "Save\nto_csv()"]
    for i, s in enumerate(steps):
        x = 0.2 + i * 2.15
        box(ax, x, 1.0, 1.7, 1.3, s)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.1, 1.65), xytext=(x + 1.75, 1.65),
                        arrowprops=dict(arrowstyle="->", lw=2))
    fig.savefig(OUT / "loading_workflow.pdf", bbox_inches="tight")


if __name__ == "__main__":
    dataframe_anatomy()
    loading_workflow()
