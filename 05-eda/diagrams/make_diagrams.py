"""Generate the PDF diagrams for module 05."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "customers.csv")


def eda_loop():
    fig, ax = canvas(10, 6, "The EDA loop", (9, 6))
    pts = [("Ask a\nquestion", 4, 4.6), ("Look at\nthe data", 7, 2.9), ("Find a\npattern", 4, 1.0), ("Refine the\nquestion", 1, 2.9)]
    for t, x, y in pts:
        box(ax, x - 1, y, 2, 1.1, t, "#dbeafe", 11)
    arrow(ax, 5.2, 4.7, 6.4, 4.0); arrow(ax, 6.9, 2.8, 5.6, 2.0)
    arrow(ax, 3.4, 1.4, 1.6, 2.6); arrow(ax, 1.4, 4.1, 3.0, 5.0)
    fig.savefig(OUT / "eda_loop.pdf", bbox_inches="tight")


def univariate_bivariate():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))
    axs[0].hist(df["spend"], bins=20, color="#3b82f6", ec="white")
    axs[0].set_title("Univariate: histogram of spend")
    df.boxplot(column="spend", by="city", ax=axs[1], grid=False)
    axs[1].set_title("Bivariate: spend by city"); axs[1].set_xlabel("")
    axs[1].tick_params(axis="x", rotation=20)
    axs[2].scatter(df["income"], df["spend"], s=12, alpha=.6)
    axs[2].set_title("Bivariate: income vs spend")
    axs[2].set_xlabel("income"); axs[2].set_ylabel("spend")
    fig.suptitle("")
    fig.savefig(OUT / "univariate_bivariate.pdf", bbox_inches="tight")


def correlation_heatmap():
    c = df[["age", "visits", "income", "spend"]].corr()
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(c, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(c))); ax.set_xticklabels(c.columns)
    ax.set_yticks(range(len(c))); ax.set_yticklabels(c.columns)
    for i in range(len(c)):
        for j in range(len(c)):
            ax.text(j, i, f"{c.iloc[i, j]:.2f}", ha="center", va="center")
    fig.colorbar(im); ax.set_title("Correlation matrix", weight="bold")
    fig.savefig(OUT / "correlation_heatmap.pdf", bbox_inches="tight")


if __name__ == "__main__":
    eda_loop(); univariate_bivariate(); correlation_heatmap()
