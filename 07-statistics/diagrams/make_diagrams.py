"""Generate the PDF diagrams for module 07."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import diagram_utils  # noqa: F401  (sets the Agg backend)

OUT = Path(__file__).resolve().parent
x = pd.read_csv(OUT.parents[1] / "data" / "customers.csv")["spend"]


def normal_rule():
    g = np.linspace(-4, 4, 400)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(g, stats.norm.pdf(g), color="black")
    for k, c, p in [(3, "#dbeafe", "99.7%"), (2, "#93c5fd", "95%"), (1, "#3b82f6", "68%")]:
        m = np.abs(g) <= k
        ax.fill_between(g[m], stats.norm.pdf(g[m]), color=c, label=f"within {k} std: {p}")
    ax.set_title("The normal distribution and the 68-95-99.7 rule", weight="bold")
    ax.set_xlabel("standard deviations from the mean"); ax.set_yticks([]); ax.legend()
    fig.savefig(OUT / "normal_rule.pdf", bbox_inches="tight")


def central_limit():
    rng = np.random.default_rng(0)
    skewed = rng.exponential(1, 20000)
    means = [rng.choice(skewed, 30).mean() for _ in range(2000)]
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    axs[0].hist(skewed, bins=40, color="#f59e0b"); axs[0].set_title("Population (very skewed)")
    axs[1].hist(means, bins=40, color="#3b82f6"); axs[1].set_title("Means of samples of 30 (bell-shaped)")
    fig.suptitle("Central limit theorem", weight="bold")
    fig.savefig(OUT / "central_limit.pdf", bbox_inches="tight")


def confidence_interval():
    se = x.std() / np.sqrt(len(x))
    lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=se)
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.errorbar(x.mean(), 0, xerr=[[x.mean() - lo], [hi - x.mean()]], fmt="o", capsize=8, color="#1e3a8a")
    ax.text(x.mean(), 0.15, f"mean {x.mean():.1f}\n95% CI [{lo:.1f}, {hi:.1f}]", ha="center")
    ax.set_ylim(-0.5, 0.7); ax.set_yticks([]); ax.set_xlabel("spend")
    ax.set_title("95% confidence interval for mean spend", weight="bold")
    fig.savefig(OUT / "confidence_interval.pdf", bbox_inches="tight")


if __name__ == "__main__":
    normal_rule(); central_limit(); confidence_interval()
