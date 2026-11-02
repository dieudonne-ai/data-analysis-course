"""Generate PDF diagrams for module 07 (statistics)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "sales_eda.csv")
r = df["revenue"]

# 1. Center & spread
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.hist(r, bins=20, color="#93c5fd", ec="white")
ax.axvline(r.mean(), color="red", ls="--", lw=2, label=f"mean = {r.mean():.1f}")
ax.axvline(r.median(), color="green", lw=2, label=f"median = {r.median():.1f}")
q1, q3 = r.quantile([.25, .75])
ax.axvspan(q1, q3, color="orange", alpha=.2, label=f"IQR = {q1:.1f}-{q3:.1f}")
ax.set_title("Center and spread: mean is pulled right by large orders", weight="bold")
ax.set_xlabel("Revenue"); ax.set_ylabel("Orders"); ax.legend()
fig.savefig(OUT / "center_spread.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Normal 68-95-99.7
x = np.linspace(-4, 4, 400); y = stats.norm.pdf(x)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(x, y, color="#1e3a8a", lw=2)
for k, c, lab in [(3, "#dbeafe", "99.7%"), (2, "#93c5fd", "95%"), (1, "#3b82f6", "68%")]:
    m = np.abs(x) <= k
    ax.fill_between(x[m], y[m], color=c, alpha=.9)
    ax.annotate(lab + f" within ±{k} std", (0, 0.05 + 0.08 * (3 - k)), ha="center", fontsize=10)
ax.set_xticks(range(-3, 4)); ax.set_xlabel("z-score (std from the mean)"); ax.set_yticks([])
ax.set_title("The normal distribution: 68-95-99.7 rule", weight="bold")
fig.savefig(OUT / "normal_rule.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Correlation
rng = np.random.default_rng(1)
fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
n = 120
base = rng.normal(size=n)
sets = [("r ≈ +0.9", base + rng.normal(scale=.4, size=n)), ("r ≈ 0", rng.normal(size=n)),
        ("r ≈ -0.9", -base + rng.normal(scale=.4, size=n)),
        ("r ≈ 0 but a pattern", None)]
for a, (t, yv) in zip(axes, sets):
    if yv is None:
        xx = rng.uniform(-2, 2, n); yy = xx**2 + rng.normal(scale=.15, size=n)
    else:
        xx, yy = base, yv
    a.scatter(xx, yy, s=12, alpha=.7, color="#2563eb")
    a.set_title(f"{t}\n(measured {np.corrcoef(xx, yy)[0, 1]:+.2f})", fontsize=10)
    a.set_xticks([]); a.set_yticks([])
fig.suptitle("Correlation measures LINEAR association only", weight="bold")
fig.savefig(OUT / "correlation.pdf", bbox_inches="tight"); plt.close(fig)

# 4. CLT
fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharex=True)
axes[0].hist(r, bins=25, color="#93c5fd", ec="white"); axes[0].set_title("Raw data (skewed)")
for a, n in zip(axes[1:], (5, 50)):
    m = [r.sample(n, replace=True, random_state=i).mean() for i in range(1000)]
    a.hist(m, bins=25, color="#60a5fa", ec="white")
    a.set_title(f"Means of samples of n={n}\nstd = {np.std(m):.1f}")
fig.suptitle("Central Limit Theorem: sample means become normal and tighter as n grows", weight="bold")
fig.savefig(OUT / "clt.pdf", bbox_inches="tight"); plt.close(fig)
