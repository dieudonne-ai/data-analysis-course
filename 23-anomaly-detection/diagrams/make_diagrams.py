"""Generate PDF diagrams for module 23 (anomaly detection)."""
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from anomaly_demo import (X, amount, hour, iqr_fences, load_sales_with_glitch, mahalanobis,  # noqa: E402
                          robust_z, rolling_anomalies, y)

BLUE, RED, GREY, GREEN = "#2563eb", "#dc2626", "#94a3b8", "#059669"


def box(ax, x, y_, text, fc, w=2.4, h=1.0, fs=9):
    ax.add_patch(FancyBboxPatch((x - w / 2, y_ - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y_, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#334155"))


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. Workflow
fig, ax = plt.subplots(figsize=(11, 3.6)); ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 4)
steps = [("1. define 'normal'\n(which features,\nwhich period?)", "#e2e8f0"),
         ("2. transform\n(log for skewed\namounts, residuals\nfor time series)", "#bfdbfe"),
         ("3. score each row\n(z, robust z, IQR,\nMahalanobis)", "#bfdbfe"),
         ("4. threshold\n(e.g. |z|>3 or\ntop 1% scores)", "#fde68a"),
         ("5. human review\nerror? fraud?\nreal event?", "#bbf7d0")]
for i, (t, c) in enumerate(steps):
    box(ax, 1.3 + i * 2.5, 2.3, t, c, w=2.2, h=1.6)
    if i:
        arrow(ax, (2.4 + (i - 1) * 2.5 + 0.08, 2.3), (0.2 + i * 2.5 - 0.08, 2.3))
ax.annotate("", xy=(1.3, 1.35), xytext=(11.3, 1.35),
            arrowprops=dict(arrowstyle="->", color=GREEN, connectionstyle="arc3,rad=-.12"))
ax.text(6.3, 0.35, "feedback: confirmed cases become labels -> tune thresholds, measure precision & recall",
        ha="center", fontsize=9, color=GREEN)
ax.set_title("Anomaly detection workflow", weight="bold", loc="left")
fig.savefig(OUT / "workflow.pdf", bbox_inches="tight"); plt.close(fig)

# 2. One-feature detectors on the amount histogram + masking
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.3))
bins = np.linspace(0, 620, 63)
a1.hist(amount[y == 0], bins=bins, color=GREY, label="normal", log=True)
a1.hist(amount[y == 1], bins=bins, color=RED, label="planted anomaly", log=True)
z3 = amount.mean() + 3 * amount.std()
med = np.median(amount); mad = np.median(np.abs(amount - med))
rz = med + 3.5 * mad / 0.6745
lo, hi = iqr_fences(amount)
for v, c, t, yt in [(z3, BLUE, f"mean+3·std = {z3:.0f}", 60), (rz, "#7c3aed", f"robust z 3.5 = {rz:.0f}", 20),
                   (hi, "#ea580c", f"IQR fence = {hi:.0f}", 7)]:
    a1.axvline(v, color=c, ls="--"); a1.text(max(v, 180) + 8, yt, t, color=c, fontsize=8)
    if v < 180:
        a1.plot([v, 186], [yt * 1.1, yt * 1.1], color=c, lw=.6)
a1.set_xlabel("amount (EUR)"); a1.set_ylabel("transactions (log scale)"); a1.legend(loc="upper right"); clean(a1)
a1.set_title("Three thresholds on one feature", loc="left", weight="bold")

clean_amt = amount[y == 0]
labels = ["mean", "std", "median", "MAD×1.48"]
with_a = [amount.mean(), amount.std(), med, mad / 0.6745]
without = [clean_amt.mean(), clean_amt.std(), np.median(clean_amt), np.median(np.abs(clean_amt - np.median(clean_amt))) / 0.6745]
xx = np.arange(4)
a2.bar(xx - .2, without, .4, color=GREY, label="without the 15 anomalies")
a2.bar(xx + .2, with_a, .4, color=RED, label="with them (3% of rows)")
for i in range(4):
    a2.text(xx[i] + .2, with_a[i] + 1, f"{with_a[i]:.1f}", ha="center", fontsize=8)
    a2.text(xx[i] - .2, without[i] + 1, f"{without[i]:.1f}", ha="center", fontsize=8)
a2.set_xticks(xx, labels); a2.legend(); clean(a2)
a2.set_title("Masking: 3% outliers nearly triple the std,\nbut barely move median & MAD", loc="left", weight="bold")
fig.tight_layout(); fig.savefig(OUT / "detectors.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Mahalanobis in 2-D
d = mahalanobis(X)
fig, ax = plt.subplots(figsize=(8.5, 5.2))
mu = X.mean(axis=0); cov = np.cov(X, rowvar=False)
vals, vecs = np.linalg.eigh(cov)
ang = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
for k, ls in [(1, ":"), (2, "--"), (3, "-")]:
    ax.add_patch(Ellipse(mu, 2 * k * np.sqrt(vals[1]), 2 * k * np.sqrt(vals[0]), angle=ang, fill=False, ec=BLUE, ls=ls))
    ax.text(mu[0] + k * np.sqrt(vals[1]) + 3, mu[1], f"d={k}", color=BLUE, fontsize=8)
flag = d > 3
ax.scatter(amount[~flag], hour[~flag], s=10, c=GREY, label="d ≤ 3 (normal)")
ax.scatter(amount[flag & (y == 1)], hour[flag & (y == 1)], s=40, c=RED, marker="x", label="d > 3, real anomaly")
ax.scatter(amount[flag & (y == 0)], hour[flag & (y == 0)], s=40, c="#ea580c", marker="o", label="d > 3, false alarm")
ax.annotate("night payments with an ordinary amount:\ninvisible to an amount-only rule", xy=(50, 2.5), xytext=(170, 4),
            arrowprops=dict(arrowstyle="->", color="#334155"), fontsize=9)
ax.annotate("huge amounts", xy=(400, 14), xytext=(430, 19), arrowprops=dict(arrowstyle="->", color="#334155"), fontsize=9)
ax.set_xlabel("amount (EUR)"); ax.set_ylabel("hour of day"); ax.legend(loc="upper right", fontsize=8); clean(ax)
ax.set_title("Mahalanobis distance: how many 'standard deviations' from the centre, in 2-D", loc="left", weight="bold")
fig.savefig(OUT / "mahalanobis.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Rolling detector on monthly revenue
months, rev = load_sales_with_glitch()
flags, centre, band = rolling_anomalies(rev)
t = np.arange(len(rev))
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.fill_between(t, centre - band, centre + band, color="#dbeafe", label="expected ± 3.5 robust z")
ax.plot(t, centre, color=BLUE, lw=1, label="median of 4 neighbours")
ax.plot(t, rev, "o-", color="#334155", ms=3, lw=1, label="revenue (with 2 simulated glitches)")
ax.scatter(t[flags], rev[flags], s=120, facecolors="none", edgecolors=RED, lw=2, label="flagged")
for i in t[flags]:
    ax.text(i + .4, rev[i], months[i], color=RED, fontsize=9)
ax.set_xticks(t[::3], months[::3], rotation=45, fontsize=8); ax.legend(fontsize=8, loc="upper left"); clean(ax)
ax.set_title("Time series: compare each month with its neighbours, not with the global mean", loc="left", weight="bold")
fig.tight_layout(); fig.savefig(OUT / "rolling.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Git: unusual commits by size (lines changed, from git log --numstat)
log = subprocess.run(["git", "log", "--no-merges", "--numstat", "--pretty=format:@%h"], cwd=OUT,
                     capture_output=True, text=True).stdout
sizes, hashes = [], []
for chunk in log.split("@")[1:]:
    lines = chunk.strip().splitlines()
    tot = sum(int(a) + int(b) for a, b, *_ in (l.split("\t") for l in lines[1:]) if a != "-")
    hashes.append(lines[0]); sizes.append(tot)
sizes = np.array(sizes[::-1]); hashes = hashes[::-1]
rzc = robust_z(np.log1p(sizes))
fig, ax = plt.subplots(figsize=(11, 4))
cols = [RED if abs(r) > 2.5 else BLUE for r in rzc]
ax.bar(range(len(sizes)), sizes, color=cols)
for i, r in enumerate(rzc):
    if abs(r) > 2.5:
        ax.text(i, sizes[i] + 60, hashes[i], ha="center", fontsize=8, color=RED)
ax.set_xlabel("commit (oldest -> newest, merges excluded)"); ax.set_ylabel("lines added + deleted"); clean(ax)
ax.set_title("Git: spot unusual commits with `git log --numstat` + robust z on log(size)   (red = |rz| > 2.5)",
             loc="left", weight="bold", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "git_commit_outliers.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
