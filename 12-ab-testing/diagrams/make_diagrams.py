"""Generate PDF diagrams for module 12 (A/B testing)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from scipy import stats

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "ab_test.csv")
g = df.groupby("group")["converted"].agg(n="size", k="sum", rate="mean")

# 1. Conversion rates with 95% CI
fig, ax = plt.subplots(figsize=(6, 4.5))
for i, (name, r) in enumerate(g.iterrows()):
    se = np.sqrt(r.rate * (1 - r.rate) / r.n)
    ax.bar(i, r.rate, color=["#94a3b8", "#1e3a8a"][i], width=.5)
    ax.errorbar(i, r.rate, yerr=1.96 * se, color="k", capsize=6)
    ax.text(i, r.rate / 2, f"{r.rate:.1%}", ha="center", color="w", weight="bold")
ax.set_xticks([0, 1], ["A (control)", "B (new button)"]); ax.set_ylabel("conversion rate")
ax.set_title("Error bars overlap: the gap may be noise", weight="bold")
fig.savefig(OUT / "conversion_ci.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Null distribution of the z statistic with observed z
a, b = g.loc["A"], g.loc["B"]
pool = (a.k + b.k) / (a.n + b.n)
z = (b.rate - a.rate) / np.sqrt(pool * (1 - pool) * (1 / a.n + 1 / b.n))
x = np.linspace(-4, 4, 400)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, stats.norm.pdf(x), color="#334155")
for sl in (x >= abs(z), x <= -abs(z)):
    ax.fill_between(x[sl], stats.norm.pdf(x[sl]), color="#ef4444", alpha=.5)
ax.axvline(z, color="#1e3a8a", lw=2, label=f"observed z = {z:.2f}")
ax.axvline(1.96, color="k", ls=":"); ax.axvline(-1.96, color="k", ls=":", label="5% threshold (±1.96)")
ax.set_title(f"p-value = red area = {2 * (1 - stats.norm.cdf(abs(z))):.3f}  (> 0.05, not significant)", weight="bold")
ax.legend(); ax.set_xlabel("z if A and B were identical")
fig.savefig(OUT / "z_test.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Power curve: sample size vs minimum detectable lift
n = np.arange(200, 6001, 50)
fig, ax = plt.subplots(figsize=(8, 4))
for p2, c in ((0.125, "#1e3a8a"), (0.14, "#15803d"), (0.11, "#ef4444")):
    p1 = .10; se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    ax.plot(n, stats.norm.cdf(abs(p2 - p1) / se - 1.96), color=c, lw=2, label=f"10% → {p2:.1%}")
ax.axhline(.8, color="k", ls=":"); ax.text(5000, .82, "80% power")
ax.set_xlabel("visitors per group"); ax.set_ylabel("power"); ax.legend()
ax.set_title("Small lifts need many visitors", weight="bold")
fig.savefig(OUT / "power_curve.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Workflow
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
steps = ["1. Hypothesis\n& one metric", "2. Sample size\n(power)", "3. Randomize\nusers", "4. Run full\nduration", "5. z-test\n+ CI", "6. Decide\n& document"]
for i, st in enumerate(steps):
    x = .9 + i * 1.84
    ax.add_patch(FancyBboxPatch((x - .8, 1.1), 1.6, .9, boxstyle="round,pad=.05", fc="#dbeafe", ec="#334155"))
    ax.text(x, 1.55, st, ha="center", va="center", fontsize=9)
    if i < 5: ax.annotate("", (x + 1.04, 1.55), (x + .86, 1.55), arrowprops=dict(arrowstyle="->"))
ax.text(5.5, .5, "Don't peek and stop early: it inflates false positives", ha="center", style="italic")
ax.set_title("A/B testing workflow", weight="bold")
fig.savefig(OUT / "workflow.pdf", bbox_inches="tight"); plt.close(fig)
