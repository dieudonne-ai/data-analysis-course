"""Generate the PDF diagrams for module 04."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent


def cleaning_pipeline():
    fig, ax = canvas(12, 4, "Data cleaning pipeline", (12, 4))
    steps = ["Raw data", "Remove\nduplicates", "Fix text\n& types", "Handle\nmissing", "Treat\noutliers", "Clean data"]
    colors = ["#fecaca", "#dbeafe", "#dbeafe", "#dbeafe", "#dbeafe", "#bbf7d0"]
    for i, (s, c) in enumerate(zip(steps, colors)):
        x = 0.2 + i * 1.95
        box(ax, x, 1.4, 1.5, 1.2, s, c, 10)
        if i < len(steps) - 1:
            arrow(ax, x + 1.55, 2.0, x + 1.95, 2.0)
    ax.text(6, 0.5, "Always keep the raw file untouched - write the result to a new file.",
            ha="center", style="italic")
    fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")


def missing_decision():
    fig, ax = canvas(10, 6, "What to do with missing values?", (10, 6))
    box(ax, 3.5, 4.8, 3, 0.8, "Value missing?", "#fde68a")
    box(ax, 0.2, 2.9, 2.8, 1.0, "Few rows, random\n-> drop rows\n(dropna)", "#dbeafe", 10)
    box(ax, 3.6, 2.9, 2.8, 1.0, "Numeric column\n-> fill median/mean\n(fillna)", "#dbeafe", 10)
    box(ax, 7.0, 2.9, 2.8, 1.0, "Category column\n-> fill mode or\n'Unknown'", "#dbeafe", 10)
    box(ax, 3.0, 0.7, 4.0, 1.0, "Column mostly empty?\n-> drop the column", "#fecaca", 10)
    for x in (1.6, 5.0, 8.4):
        arrow(ax, 5, 4.8, x, 3.95)
    arrow(ax, 5, 2.9, 5, 1.75)
    fig.savefig(OUT / "missing_values_decision.pdf", bbox_inches="tight")


def iqr_rule():
    import numpy as np
    import matplotlib.pyplot as plt
    data = [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 300]
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.boxplot(data, orientation="horizontal", whis=1.5)
    q1, q3 = np.percentile(data, [25, 75])
    ax.axvline(q1 - 1.5 * (q3 - q1), color="red", ls="--")
    ax.axvline(q3 + 1.5 * (q3 - q1), color="red", ls="--", label="Q1-1.5*IQR / Q3+1.5*IQR")
    ax.set_title("Outlier detection with the IQR rule", weight="bold")
    ax.set_xlabel("quantity"); ax.legend(loc="center right")
    fig.savefig(OUT / "iqr_rule.pdf", bbox_inches="tight")


if __name__ == "__main__":
    cleaning_pipeline(); missing_decision(); iqr_rule()
