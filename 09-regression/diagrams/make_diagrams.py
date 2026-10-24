"""Generate the PDF diagrams for module 09 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
DATA = Path(__file__).resolve().parents[2] / "data" / "students.csv"


def regression_line():
    df = pd.read_csv(DATA).sample(40, random_state=0)
    x, y = df["study_hours"].to_numpy(), df["score"].to_numpy()
    m, b = np.polyfit(x, y, 1)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(x, y, color="#1e3a8a", zorder=3, label="students")
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, m * xs + b, color="red", lw=2, label=f"fit: score = {b:.1f} + {m:.1f} * hours")
    ax.vlines(x[:8], y[:8], m * x[:8] + b, color="gray", ls="--", label="residuals")
    ax.set(xlabel="Study hours / week", ylabel="Score")
    ax.set_title("Linear regression and residuals", fontsize=14, weight="bold")
    ax.legend()
    fig.savefig(OUT / "regression_line.pdf", bbox_inches="tight")


def train_test():
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.8); ax.axis("off")
    ax.set_title("Train / test split", fontsize=14, weight="bold")
    for x, w, t, c in [(0.2, 6.4, "Train (80%)\nfit the model here", "#bfdbfe"),
                       (6.6, 1.6, "Test (20%)\nevaluate here", "#fde68a")]:
        ax.add_patch(FancyBboxPatch((x, 2.0), w, 1.0, boxstyle="round,pad=0.02", fc=c, ec="#1e3a8a"))
        ax.text(x + w / 2, 2.5, t, ha="center", va="center")
    ax.text(0.2, 3.3, "All data (200 rows)", weight="bold")
    ax.annotate("coefficients", xy=(3.4, 2.0), xytext=(3.4, 0.9), ha="center", arrowprops=dict(arrowstyle="<-", lw=1.5))
    ax.annotate("R², RMSE", xy=(7.4, 2.0), xytext=(7.4, 0.9), ha="center", arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(5.4, 0.4, "Model learned on train is scored on rows it has never seen", ha="center", style="italic")
    fig.savefig(OUT / "train_test.pdf", bbox_inches="tight")


if __name__ == "__main__":
    regression_line()
    train_test()
