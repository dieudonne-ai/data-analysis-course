"""Generate the PDF diagrams for module 08."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent


def test_steps():
    fig, ax = canvas(12, 4, "Hypothesis testing in 5 steps", (12, 4))
    steps = ["1. State\nH0 and H1", "2. Choose\nalpha (0.05)", "3. Pick the\ntest", "4. Compute\np-value", "5. p < alpha?\nReject H0"]
    for i, s in enumerate(steps):
        x = 0.2 + i * 2.35
        box(ax, x, 1.3, 1.9, 1.4, s, "#fde68a" if i == 4 else "#dbeafe", 10)
        if i < 4:
            arrow(ax, x + 1.95, 2.0, x + 2.35, 2.0)
    fig.savefig(OUT / "test_steps.pdf", bbox_inches="tight")


def p_value():
    g = np.linspace(-4.5, 4.5, 500)
    t = 2.95
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(g, stats.norm.pdf(g), color="black")
    for sign in (1, -1):
        m = sign * g >= t
        ax.fill_between(g[m], stats.norm.pdf(g[m]), color="#ef4444")
    ax.axvline(t, ls="--", color="#ef4444"); ax.axvline(-t, ls="--", color="#ef4444")
    ax.text(0, 0.18, "If H0 is true,\nmost results fall here", ha="center")
    ax.annotate("p-value = red area\n(chance of a result this extreme)", xy=(3.3, 0.005), xytext=(2.0, 0.15),
                arrowprops=dict(arrowstyle="->"))
    ax.set_title("What the p-value means (t = 2.95 from our A/B test)", weight="bold")
    ax.set_yticks([]); ax.set_xlabel("test statistic")
    fig.savefig(OUT / "p_value.pdf", bbox_inches="tight")


def errors_table():
    fig, ax = canvas(8, 4.5, "Type I and Type II errors", (8, 4.5))
    ax.text(3.7, 3.9, "H0 true", ha="center", weight="bold"); ax.text(6.2, 3.9, "H0 false", ha="center", weight="bold")
    ax.text(1.0, 2.9, "Reject H0", ha="center", weight="bold"); ax.text(1.0, 1.3, "Keep H0", ha="center", weight="bold")
    box(ax, 2.6, 2.4, 2.2, 1.2, "Type I error\n(false alarm)\nprob = alpha", "#fecaca", 10)
    box(ax, 5.1, 2.4, 2.2, 1.2, "Correct\n(power = 1 - beta)", "#bbf7d0", 10)
    box(ax, 2.6, 0.8, 2.2, 1.2, "Correct", "#bbf7d0", 10)
    box(ax, 5.1, 0.8, 2.2, 1.2, "Type II error\n(missed effect)\nprob = beta", "#fecaca", 10)
    fig.savefig(OUT / "errors_table.pdf", bbox_inches="tight")


if __name__ == "__main__":
    test_steps(); p_value(); errors_table()
