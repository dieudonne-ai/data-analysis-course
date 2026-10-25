"""Generate the PDF diagrams for module 09."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "customers.csv")


def regression_line():
    r = stats.linregress(df["income"], df["spend"])
    xs = np.array([df["income"].min(), df["income"].max()])
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["income"], df["spend"], s=14, alpha=.5, label="customers")
    ax.plot(xs, r.intercept + r.slope * xs, color="red", lw=2, label=f"fit: spend = {r.intercept:.0f} + {r.slope:.3f}*income")
    i = 100
    px, py = df.loc[i, "income"], df.loc[i, "spend"]
    ax.plot([px, px], [py, r.intercept + r.slope * px], color="green", lw=2)
    ax.annotate("residual = actual - predicted", xy=(px, (py + r.intercept + r.slope * px) / 2),
                xytext=(px + 120, py + 35), arrowprops=dict(arrowstyle="->"))
    ax.set_xlabel("income"); ax.set_ylabel("spend"); ax.legend()
    ax.set_title(f"Linear regression (R2 = {r.rvalue**2:.2f})", weight="bold")
    fig.savefig(OUT / "regression_line.pdf", bbox_inches="tight")


def train_test():
    fig, ax = canvas(10, 4, "Train / test split", (10, 3.6))
    box(ax, 0.3, 2.3, 9.4, 0.9, "All data (200 customers)", "#f1f5f9")
    box(ax, 0.3, 0.8, 7.4, 0.9, "Train 80 %: fit the model", "#bbf7d0")
    box(ax, 7.8, 0.8, 1.9, 0.9, "Test 20 %:\nevaluate", "#fecaca", 10)
    arrow(ax, 4, 2.3, 4, 1.75); arrow(ax, 8.7, 2.3, 8.7, 1.75)
    fig.savefig(OUT / "train_test.pdf", bbox_inches="tight")


def residual_check():
    r = stats.linregress(df["income"], df["spend"])
    res = df["spend"] - (r.intercept + r.slope * df["income"])
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    axs[0].scatter(r.intercept + r.slope * df["income"], res, s=12, alpha=.6)
    axs[0].axhline(0, color="red"); axs[0].set_title("Residuals vs predicted\n(want: random cloud)")
    axs[1].hist(res, bins=20, color="#3b82f6"); axs[1].set_title("Residual histogram\n(want: bell shape)")
    fig.savefig(OUT / "residual_check.pdf", bbox_inches="tight")


if __name__ == "__main__":
    regression_line(); train_test(); residual_check()
