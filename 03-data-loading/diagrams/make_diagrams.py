"""Generate the PDF diagrams for module 03."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

here = Path(__file__).parent


def anatomy():
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.set_xlim(0, 9); ax.set_ylim(0, 4.8); ax.axis("off")
    ax.text(4.5, 4.5, "Anatomy of a pandas DataFrame", ha="center", fontsize=15, weight="bold")
    cols = ["order_id", "product", "quantity", "price", "month"]
    rows = [[1, "Pen", 10, 1.5, "Jan"], [2, "Notebook", 3, 4.0, "Jan"], [3, "Pen", 5, 1.5, "Feb"]]
    x0, y0, w, h = 1.4, 2.6, 1.4, 0.55
    for j, c in enumerate(cols):
        ax.add_patch(Rectangle((x0 + j * w, y0 + h), w, h, fc="#bfdbfe", ec="#334155"))
        ax.text(x0 + j * w + w / 2, y0 + 1.5 * h, c, ha="center", va="center", weight="bold", fontsize=9)
    for i, r in enumerate(rows):
        ax.add_patch(Rectangle((0.2, y0 - i * h), 1.2, h, fc="#fde68a", ec="#334155"))
        ax.text(0.8, y0 - i * h + h / 2, str(i), ha="center", va="center", fontsize=9)
        for j, v in enumerate(r):
            ax.add_patch(Rectangle((x0 + j * w, y0 - i * h), w, h, fc="white", ec="#334155"))
            ax.text(x0 + j * w + w / 2, y0 - i * h + h / 2, str(v), ha="center", va="center", fontsize=9)
    ax.annotate("columns = Series\n(df['price'])", xy=(x0 + 3.5 * w, y0 + 2 * h), xytext=(6.2, 4.1),
                arrowprops=dict(arrowstyle="->"), fontsize=9, ha="center")
    ax.annotate("index = row labels\n(df.loc[0])", xy=(0.8, y0 - 1.5 * h + h), xytext=(0.8, 0.5),
                arrowprops=dict(arrowstyle="->"), fontsize=9, ha="center")
    ax.annotate("one cell\n(df.loc[0,'price'])", xy=(x0 + 3.5 * w, y0 + h / 2), xytext=(7.6, 0.8),
                arrowprops=dict(arrowstyle="->"), fontsize=9, ha="center")
    fig.savefig(here / "dataframe-anatomy.pdf", bbox_inches="tight")


def pipeline():
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3); ax.axis("off")
    steps = [("CSV / Excel /\nJSON file", "#dbeafe"), ("pd.read_csv()", "#fef9c3"),
             ("DataFrame\nin memory", "#dcfce7"), ("head() info()\ndescribe()", "#fce7f3")]
    for i, (t, c) in enumerate(steps):
        x = 0.3 + i * 2.7
        ax.add_patch(FancyBboxPatch((x, 0.9), 2.0, 1.2, boxstyle="round,pad=0.05", fc=c, ec="#334155", lw=1.5))
        ax.text(x + 1, 1.5, t, ha="center", va="center", fontsize=10, weight="bold")
        if i < 3:
            ax.annotate("", xy=(x + 2.65, 1.5), xytext=(x + 2.1, 1.5), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(5.5, 2.7, "Loading data: from file to first inspection", ha="center", fontsize=14, weight="bold")
    fig.savefig(here / "loading-pipeline.pdf", bbox_inches="tight")


anatomy(); pipeline(); print("done")
