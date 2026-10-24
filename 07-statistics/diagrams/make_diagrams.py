"""Generate the PDF diagrams for module 07 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def normal_distribution():
    x = np.linspace(-4, 4, 400)
    y = np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(x, y, color="black")
    for k, c, p in [(3, "#dbeafe", "99.7%"), (2, "#93c5fd", "95%"), (1, "#3b82f6", "68%")]:
        m = np.abs(x) <= k
        ax.fill_between(x[m], y[m], color=c)
        ax.annotate(f"within {k} std: {p}", xy=(k, np.exp(-k**2 / 2) / np.sqrt(2 * np.pi)),
                    xytext=(k + 0.3, 0.30 - 0.07 * (k - 1)), arrowprops=dict(arrowstyle="->"))
    ax.set_xticks(range(-4, 5))
    ax.set_xticklabels(["-4", "-3σ", "-2σ", "-1σ", "mean", "+1σ", "+2σ", "+3σ", "+4"])
    ax.set_yticks([]); ax.set_title("Normal distribution: 68-95-99.7 rule", fontsize=14, weight="bold")
    fig.savefig(OUT / "normal_distribution.pdf", bbox_inches="tight")


def population_sample():
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 9); ax.set_ylim(0, 4); ax.axis("off")
    ax.set_title("Population vs sample", fontsize=14, weight="bold")
    ax.add_patch(plt.Circle((2.2, 2), 1.7, fc="#dbeafe", ec="#1e3a8a"))
    ax.text(2.2, 3.4, "Population (all students)\nparameter: μ", ha="center", fontsize=10)
    rng = np.random.default_rng(3)
    pts = rng.normal(0, 0.6, (60, 2)) + [2.2, 1.9]
    ax.scatter(*pts.T, s=8, c="#1e3a8a")
    ax.add_patch(plt.Circle((6.8, 2), 0.9, fc="#fde68a", ec="#b45309"))
    ax.text(6.8, 3.2, "Sample (n = 200)\nstatistic: x̄", ha="center", fontsize=10)
    ax.text(6.8, 2, "x̄ ≈ 69.9", ha="center", weight="bold")
    ax.annotate("random sampling", xy=(5.9, 2.2), xytext=(3.9, 2.2), arrowprops=dict(arrowstyle="->", lw=1.5), va="center")
    ax.annotate("inference (estimate μ)", xy=(3.9, 1.4), xytext=(5.9, 1.4), arrowprops=dict(arrowstyle="->", lw=1.5), va="center", ha="right")
    fig.savefig(OUT / "population_sample.pdf", bbox_inches="tight")


if __name__ == "__main__":
    normal_distribution()
    population_sample()
