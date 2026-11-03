"""Generate PDF diagrams for module 08 (hypothesis testing)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from scipy import stats

OUT = Path(__file__).resolve().parent

# 1. p-value on the null distribution
x = np.linspace(-4, 4, 400); y = stats.norm.pdf(x)
t_obs = 2.2
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(x, y, color="#1e3a8a", lw=2)
for m in (x >= t_obs, x <= -t_obs):
    ax.fill_between(x[m], y[m], color="#ef4444", alpha=.7)
ax.axvline(t_obs, color="k", ls="--"); ax.text(t_obs + .1, .3, "observed\nt = 2.2", fontsize=10)
p = 2 * stats.norm.sf(t_obs)
ax.text(0, .15, f"if H0 is true, results this extreme\nhappen {p:.1%} of the time (p-value)", ha="center")
ax.set_title("The p-value: tail area of the null distribution", weight="bold")
ax.set_yticks([]); ax.set_xlabel("test statistic")
fig.savefig(OUT / "p_value.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Type I / Type II errors
fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.linspace(-4, 7, 500)
ax.plot(x, stats.norm.pdf(x), color="#1e3a8a", lw=2, label="H0 true")
ax.plot(x, stats.norm.pdf(x, 3), color="#15803d", lw=2, label="H1 true")
c = 1.645
ax.fill_between(x[x >= c], stats.norm.pdf(x[x >= c]), color="#ef4444", alpha=.7, label="Type I error (alpha)")
ax.fill_between(x[x <= c], stats.norm.pdf(x[x <= c], 3), color="#f59e0b", alpha=.6, label="Type II error (beta)")
ax.axvline(c, color="k", ls="--"); ax.text(c + .1, .42, "decision\nthreshold")
ax.set_yticks([]); ax.legend(); ax.set_title("Two ways to be wrong; power = 1 - beta", weight="bold")
fig.savefig(OUT / "errors.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Which test? decision flowchart
fig, ax = plt.subplots(figsize=(11, 6)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 6)


def box(xy, text, color):
    ax.add_patch(FancyBboxPatch((xy[0] - .8, xy[1] - .32), 1.6, .64, boxstyle="round,pad=.05", fc=color, ec="#334155"))
    ax.text(*xy, text, ha="center", va="center", fontsize=9)


def arrow(a, b, label=""):
    ax.annotate("", b, a, arrowprops=dict(arrowstyle="->", color="#334155"))
    if label:
        ax.text((a[0] + b[0]) / 2 + .1, (a[1] + b[1]) / 2, label, fontsize=8, color="#b91c1c")


box((5.5, 5.5), "What is your outcome?", "#dbeafe")
box((2.2, 4.1), "Numeric\n(revenue)", "#fef9c3"); box((8.8, 4.1), "Categories\n(product, month)", "#fef9c3")
arrow((5.5, 5.18), (2.2, 4.42)); arrow((5.5, 5.18), (8.8, 4.42))
box((8.8, 2.7), "Chi-square test\nof independence", "#bbf7d0"); arrow((8.8, 3.78), (8.8, 3.02))
box((0.9, 2.7), "1 group vs\na value", "#fef9c3"); box((3.0, 2.7), "2 groups", "#fef9c3"); box((5.1, 2.7), "3+ groups", "#fef9c3")
for xx in (0.9, 3.0, 5.1):
    arrow((2.2, 3.78), (xx, 3.02))
box((0.9, 1.3), "One-sample\nt-test", "#bbf7d0"); arrow((0.9, 2.38), (0.9, 1.62))
box((2.6, 1.3), "Welch t-test\n(normal-ish)", "#bbf7d0"); box((4.3, 1.3), "Mann-Whitney\n(skewed)", "#bbf7d0")
arrow((3.0, 2.38), (2.6, 1.62)); arrow((3.0, 2.38), (4.3, 1.62))
box((6.0, 1.3), "ANOVA\n(Kruskal-Wallis\nif skewed)", "#bbf7d0"); arrow((5.1, 2.38), (6.0, 1.62))
ax.set_title("Which test should I use?", weight="bold")
fig.savefig(OUT / "which_test.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Hypothesis testing steps
fig, ax = plt.subplots(figsize=(11, 2.6)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 2.6)
steps = ["1. State\nH0 and H1", "2. Choose\nalpha (0.05)", "3. Pick test\n& check assumptions", "4. Compute\nstatistic, p", "5. Decide &\nreport effect size"]
for i, s in enumerate(steps):
    cx = 1 + i * 2.25
    ax.add_patch(FancyBboxPatch((cx - .95, .8), 1.9, 1, boxstyle="round,pad=.05", fc="#dbeafe", ec="#1e3a8a"))
    ax.text(cx, 1.3, s, ha="center", va="center", fontsize=9)
    if i < 4:
        ax.annotate("", (cx + 1.3, 1.3), (cx + 1.0, 1.3), arrowprops=dict(arrowstyle="->"))
ax.set_title("The hypothesis-testing workflow", weight="bold")
fig.savefig(OUT / "workflow.pdf", bbox_inches="tight"); plt.close(fig)
