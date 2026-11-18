"""Generate PDF diagrams for module 23 (anomaly detection)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from anomaly_demo import df, iqr_flags, mahalanobis, orders, robust_z, seasonal_residual, truth  # noqa: E402

RED, BLUE, GREY = "#dc2626", "#2563eb", "#94a3b8"


def box(ax, x, y_, text, fc, w=2.4, h=1.0, fs=9):
    ax.add_patch(FancyBboxPatch((x - w / 2, y_ - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y_, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b, label=None):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#334155"))
    if label:
        ax.text((a[0] + b[0]) / 2 + .1, (a[1] + b[1]) / 2, label, fontsize=8, color="#475569")


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. Which method? a small decision map
fig, ax = plt.subplots(figsize=(11, 5)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6)
box(ax, 6, 5.4, "Is this value unusual?", "#e2e8f0", w=3.2, h=.7, fs=10)
box(ax, 2.2, 3.9, "one column,\nno time pattern", "#fef3c7", w=2.6)
box(ax, 6, 3.9, "time series with\ntrend / weekly cycle", "#fef3c7", w=2.6)
box(ax, 9.8, 3.9, "several columns\nthat move together", "#fef3c7", w=2.6)
for x in (2.2, 6, 9.8):
    arrow(ax, (6, 5.05), (x, 4.45))
box(ax, 2.2, 2.1, "z-score (|z|>3)\nIQR fences\nrobust z (median/MAD)", "#bfdbfe", w=2.8, h=1.3)
box(ax, 6, 2.1, "remove trend + season\nthen robust z on\nthe residuals", "#bfdbfe", w=2.8, h=1.3)
box(ax, 9.8, 2.1, "Mahalanobis distance\n(isolation forest,\nautoencoders...)", "#bfdbfe", w=2.8, h=1.3)
for x in (2.2, 6, 9.8):
    arrow(ax, (x, 3.35), (x, 2.8))
ax.text(6, .55, "always: compare flags with known incidents -> precision (how many alarms were real?)"
        " and recall (how many incidents did we catch?)", ha="center", fontsize=9, style="italic")
ax.set_title("Anomaly detection: pick the method that matches the shape of 'normal'", weight="bold", loc="left")
fig.savefig(OUT / "methods_map.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Fences on the histogram: z-score vs IQR vs robust
fig, ax = plt.subplots(figsize=(10, 4.2)); clean(ax)
ax.hist(orders[~truth], bins=40, color=GREY, label="normal days")
ax.hist(orders[truth], bins=40, range=(orders.min(), orders.max()), color=RED, label="known incidents")
m, s = orders.mean(), orders.std()
_, (lo, hi) = iqr_flags(orders)
med = np.median(orders); mad = 1.4826 * np.median(np.abs(orders - med))
for (a, b), c, lab, ls in [((m - 3 * s, m + 3 * s), BLUE, "z-score: mean ± 3 std", "-"),
                          ((lo, hi), "#16a34a", "IQR: Q1-1.5·IQR, Q3+1.5·IQR", "--"),
                          ((med - 3.5 * mad, med + 3.5 * mad), "#9333ea", "robust: median ± 3.5 MAD", ":")]:
    ax.axvline(a, color=c, ls=ls, lw=2); ax.axvline(b, color=c, ls=ls, lw=2, label=lab)
ax.set_xlabel("orders per day"); ax.set_ylabel("number of days"); ax.legend(fontsize=8, frameon=False)
ax.set_title("Three fences on one column: all catch the 3 obvious days, none sees the Monday spike",
             weight="bold", loc="left", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / "fences.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Seasonal residuals
res = seasonal_residual(df); rres = robust_z(res); flag = np.abs(rres) > 3.5
fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
for a in (a1, a2):
    clean(a)
a1.plot(df["date"], orders, color=GREY, lw=.8, label="daily orders")
a1.plot(df["date"], df["orders"].rolling(29, center=True, min_periods=1).median(), color=BLUE, lw=2, label="trend (29-day rolling median)")
a1.scatter(df["date"][truth], orders[truth], color=RED, zorder=3, label="known incidents")
a1.legend(fontsize=8, frameon=False, loc="upper left"); a1.set_ylabel("orders")
a1.set_title("Raw series: the weekend zig-zag hides the Monday spike and the bot day", weight="bold", loc="left", fontsize=11)
a2.bar(df["date"][~flag], rres[~flag], color=GREY, width=1)
a2.bar(df["date"][flag], rres[flag], color=RED, width=2)
for t in (-3.5, 3.5):
    a2.axhline(t, color="#334155", ls="--", lw=1)
a2.set_ylabel("robust z of residual")
a2.set_title("Residual = orders - trend - weekday effect: now 5 of 6 incidents stand out", weight="bold", loc="left", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / "seasonal_residuals.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Mahalanobis: ellipses vs circles
X = df[["orders", "avg_basket"]].to_numpy(float)
md = mahalanobis(X)
mu = X.mean(0); cov = np.cov(X, rowvar=False)
vals, vecs = np.linalg.eigh(cov); angle = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
fig, ax = plt.subplots(figsize=(9, 5.5)); clean(ax)
ax.scatter(X[~truth, 0], X[~truth, 1], s=12, color=GREY, label="normal days")
ax.scatter(X[truth, 0], X[truth, 1], s=50, color=RED, label="known incidents")
for k, ls in [(2, ":"), (3.5, "--")]:
    ax.add_patch(Ellipse(mu, 2 * k * np.sqrt(vals[1]), 2 * k * np.sqrt(vals[0]), angle=angle,
                         fill=False, ec=BLUE, ls=ls, lw=1.5, label=f"Mahalanobis distance = {k}"))
offsets = {"Jun 09": (-70, 10), "Aug 20": (8, -12)}
for i in np.where(truth)[0]:
    lab = df['date'][i].strftime('%b %d')
    ax.annotate(f"{lab} ({md[i]:.1f})", X[i], textcoords="offset points",
                xytext=offsets.get(lab, (6, 4)), fontsize=8)
ax.set_xlabel("orders per day"); ax.set_ylabel("average basket (EUR)"); ax.legend(fontsize=8, frameon=False)
ax.set_title("Correlated columns: 'normal' is a tilted ellipse, not a box", weight="bold", loc="left")
fig.tight_layout(); fig.savefig(OUT / "mahalanobis.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Threshold trade-off
bres = (df["avg_basket"] - df["avg_basket"].rolling(29, center=True, min_periods=1).median()).to_numpy()
score = np.maximum(np.abs(rres) / 3.5, mahalanobis(np.column_stack([res, bres])) / 4)
ts = np.linspace(.4, 2, 81)
prec = [((score > t) & truth).sum() / max((score > t).sum(), 1) for t in ts]
rec = [((score > t) & truth).sum() / truth.sum() for t in ts]
alarms = [(score > t).sum() for t in ts]
fig, ax = plt.subplots(figsize=(10, 4.2)); clean(ax)
ax.plot(ts, prec, color=BLUE, lw=2, label="precision (share of alarms that are real)")
ax.plot(ts, rec, color=RED, lw=2, label="recall (share of incidents caught)")
ax2 = ax.twinx(); ax2.plot(ts, alarms, color=GREY, ls="--", label="alarms per year"); ax2.set_ylabel("alarms per year")
ax.axvline(1.0, color="#334155", lw=1); ax.text(1.02, .05, "default\nthreshold", fontsize=8)
ax.set_xlabel("threshold multiplier"); ax.set_ylabel("rate")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=8, frameon=False, loc="center right")
ax.set_title("Lower threshold = more incidents caught, but more false alarms to investigate", weight="bold", loc="left", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / "threshold_tradeoff.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Git: bisect run finds the anomalous commit
fig, ax = plt.subplots(figsize=(11, 3.8)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 4.2)
n = 11; bad = 7
xs = np.linspace(.7, 11.3, n)
ax.plot(xs, [2.5] * n, color="#334155", zorder=1)
for i, x in enumerate(xs):
    c = "#bbf7d0" if i < bad else "#fecaca"
    ax.scatter(x, 2.5, s=420, color=c, ec="#334155", zorder=2)
    ax.text(x, 2.5, f"c{i}", ha="center", va="center", fontsize=8)
ax.text(xs[0], 3.2, "good\n(test passes)", ha="center", fontsize=8)
ax.text(xs[-1], 3.2, "bad\n(test fails)", ha="center", fontsize=8)
for step, (i, txt) in enumerate([(5, "1: test c5 -> pass"), (8, "2: test c8 -> fail"), (6, "3: test c6 -> pass"),
                                  (7, "4: test c7 -> fail => c7 is the first bad commit")]):
    ax.annotate(txt, (xs[i], 2.2), xytext=(xs[i] - .3, 1.6 - .38 * step), fontsize=8,
                arrowprops=dict(arrowstyle="->", color=GREY))
ax.text(.2, .0, "git bisect run python check.py   ->  git runs the script at each step: exit 0 = good, 1 = bad, 125 = skip",
        fontsize=9, family="monospace")
ax.set_title("git bisect run: an automatic 'anomaly detector' for history (log2(n) tests instead of n)",
             weight="bold", loc="left")
fig.savefig(OUT / "git_bisect_run.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
