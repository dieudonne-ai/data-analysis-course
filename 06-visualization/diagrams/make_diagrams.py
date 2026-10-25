"""Generate the PDF diagrams for module 06."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent


def chart_chooser():
    fig, ax = canvas(12, 6.5, "Which chart should I use?", (12, 6.5))
    box(ax, 4.5, 5.3, 3, 0.9, "What is my question?", "#fde68a")
    rows = [("Compare\ncategories", "Bar chart", 0.2), ("Distribution of\none variable", "Histogram / box plot", 3.2),
            ("Relationship\nbetween two numbers", "Scatter plot", 6.2), ("Change\nover time", "Line chart", 9.2)]
    for q, c, x in rows:
        box(ax, x, 3.1, 2.6, 1.2, q, "#dbeafe", 10)
        box(ax, x, 0.8, 2.6, 1.2, c, "#bbf7d0", 10)
        arrow(ax, 6, 5.3, x + 1.3, 4.35); arrow(ax, x + 1.3, 3.1, x + 1.3, 2.05)
    fig.savefig(OUT / "chart_chooser.pdf", bbox_inches="tight")


def figure_anatomy():
    fig, ax = canvas(10, 6, "Anatomy of a matplotlib figure", (9, 6))
    box(ax, 0.5, 0.5, 9, 4.9, "", "#f1f5f9")
    box(ax, 1.8, 1.4, 6.4, 3.0, "Axes  (ax)\nthe plotting area", "#dbeafe", 12)
    ax.text(5, 4.85, "Title  ax.set_title()", ha="center")
    ax.text(5, 0.85, "X label  ax.set_xlabel()", ha="center")
    ax.text(1.1, 2.9, "Y label\nax.set_ylabel()", ha="center", rotation=90, va="center")
    ax.text(0.6, 5.65, "Figure (fig) = the whole canvas  ->  fig.savefig('chart.pdf')", fontsize=10)
    fig.savefig(OUT / "figure_anatomy.pdf", bbox_inches="tight")


if __name__ == "__main__":
    chart_chooser(); figure_anatomy()
