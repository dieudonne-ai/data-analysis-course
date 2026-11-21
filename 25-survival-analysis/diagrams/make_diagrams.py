"""Build the PDF diagrams for module 25 (survival analysis)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from survival_demo import kaplan_meier, load, logrank, median_survival  # noqa: E402

BLUE, ORANGE, GREEN, RED, GREY = "#2563eb", "#ea580c", "#16a34a", "#dc2626", "#94a3b8"
plan, t, e = load()


def box(ax, x, y, text, fc, w=2.4, h=1.0, fs=9, ec="#334155"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec=ec))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. Censoring: calendar time vs time since signup
rng = np.random.default_rng(3)
idx = rng.choice(len(t), 10, replace=False)
raw = np.genfromtxt(OUT.parents[1] / "data" / "subscriptions.csv", delimiter=",", names=True,
                    dtype=None, encoding="utf-8")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
for row, i in enumerate(idx):
    s, m, ev = raw["signup_month"][i], raw["months"][i], raw["churned"][i]
    c = RED if ev else BLUE
    a1.plot([s, s + m], [row, row], color=c, lw=2.5)
    a1.plot(s + m, row, "x" if ev else "o", color=c, ms=8, mfc="white" if not ev else c, mew=2)
    a2.plot([0, m], [row, row], color=c, lw=2.5)
    a2.plot(m, row, "x" if ev else "o", color=c, ms=8, mfc="white" if not ev else c, mew=2)
a1.axvline(24, color="#334155", ls="--"); a1.text(24.3, 9.3, "analysis\ndate", fontsize=8)
a1.set_xlabel("calendar month"); a1.set_yticks(range(10)); a1.set_yticklabels([f"cust {k + 1}" for k in range(10)])
a1.set_title("1. Customers join at different times", loc="left", weight="bold")
a2.set_xlabel("months since signup")
a2.set_title("2. Re-align on time since signup", loc="left", weight="bold")
a2.plot([], [], "x", color=RED, mew=2, label="cancelled (event)")
a2.plot([], [], "o", color=BLUE, mfc="white", mew=2, label="still active (censored)")
a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=8, frameon=False)
for a in (a1, a2):
    clean(a)
fig.suptitle("Censoring: for open dots we only know the lifetime is AT LEAST this long", x=.02, y=1.03, ha="left", fontsize=10, color="#475569")
fig.savefig(OUT / "censoring.pdf", bbox_inches="tight"); plt.close(fig)

# 2. How the Kaplan-Meier estimator is built (step by step)
times, S, n, d = kaplan_meier(t, e)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw=dict(width_ratios=[1, 1.1]))
a1.axis("off"); a1.set_xlim(0, 10); a1.set_ylim(0, 8)
a1.set_title("S(t) = product of 'survived this month' probabilities", loc="left", weight="bold")
hdr = ["month", "at risk n", "cancel d", "1 - d/n", "S(t)"]
xs = [0.8, 2.6, 4.4, 6.3, 8.4]
for x, h in zip(xs, hdr):
    a1.text(x, 7.3, h, ha="center", weight="bold", fontsize=9)
for r in range(5):
    y = 6.3 - r * 1.1
    vals = [f"{times[r]}", f"{n[r]}", f"{d[r]}", f"{1 - d[r] / n[r]:.3f}", f"{S[r]:.3f}"]
    for x, v in zip(xs, vals):
        a1.text(x, y, v, ha="center", fontsize=9, family="monospace")
    if r:
        a1.text(8.4, y - .45, f"= {S[r - 1]:.3f} x {1 - d[r] / n[r]:.3f}", ha="center", fontsize=7, color="#475569")
a1.text(0.2, 0.3, "n shrinks because of cancellations AND censored customers:\n"
        "a censored customer counts while watched, then leaves the risk set.", fontsize=8, color="#475569")
a2.step(np.r_[0, times], np.r_[1, S], where="post", color=BLUE, lw=2)
for r in range(5):
    a2.annotate(f"x{1 - d[r] / n[r]:.3f}", (times[r], S[r]), xytext=(times[r] + .6, S[r] + .03), fontsize=7, color=ORANGE)
med = median_survival(times, S)
a2.axhline(.5, color=GREY, ls=":"); a2.axvline(med, color=GREY, ls=":")
a2.text(med + .3, .52, f"median = {med:.0f} months", fontsize=8)
a2.set_ylim(0, 1.02); a2.set_xlabel("months since signup"); a2.set_ylabel("S(t) = P(still subscribed)")
a2.set_title("The Kaplan-Meier curve: all 800 customers", loc="left", weight="bold"); clean(a2)
fig.savefig(OUT / "kaplan_meier.pdf", bbox_inches="tight"); plt.close(fig)

# 3. KM by plan + log-rank
fig, ax = plt.subplots(figsize=(9, 5))
for p, c in (("monthly", ORANGE), ("annual", GREEN)):
    m = plan == p
    tt, SS, nn, _ = kaplan_meier(t[m], e[m])
    ax.step(np.r_[0, tt], np.r_[1, SS], where="post", color=c, lw=2.2, label=f"{p} (n={m.sum()})")
    # censor ticks
    cens = np.unique(t[m][e[m] == 0])
    ax.plot(cens, [SS[np.where(tt <= u)[0][-1]] if (tt <= u).any() else 1 for u in cens], "|", color=c, ms=8)
    md = median_survival(tt, SS)
    if np.isfinite(md):
        ax.plot([md, md], [0, .5], ls=":", color=c)
        ax.text(md, .02, f" median {md:.0f}", color=c, fontsize=8)
ax.axhline(.5, color=GREY, ls=":")
_, _, stat, pv = logrank(t, e, plan == "monthly")
ax.text(13, .88, f"log-rank test\nchi2 = {stat:.1f}, p = {pv:.1g}\n-> the plans really differ", fontsize=9,
        bbox=dict(fc="#f8fafc", ec=GREY))
ax.set_ylim(0, 1.02); ax.set_xlabel("months since signup"); ax.set_ylabel("share still subscribed")
ax.set_title("Kaplan-Meier by plan  ( | = censored customer )", loc="left", weight="bold")
ax.legend(frameon=False, loc="lower left"); clean(ax)
fig.savefig(OUT / "km_by_plan.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Hazard: monthly cancellation rate among those still at risk
fig, ax = plt.subplots(figsize=(9, 4.4))
w = .4
for k, (p, c) in enumerate((("monthly", ORANGE), ("annual", GREEN))):
    m = plan == p
    tt, _, nn, dd = kaplan_meier(t[m], e[m])
    sel = tt <= 18
    ax.bar(tt[sel] + (k - .5) * w, dd[sel] / nn[sel], w, color=c, label=p)
    hz = e[m].sum() / t[m].sum()
    ax.axhline(hz, color=c, ls="--", lw=1)
    ax.text(18.6, hz, f"avg {hz:.3f}", color=c, fontsize=8, va="center")
ax.set_xlabel("month since signup"); ax.set_ylabel("hazard = d / n")
ax.set_title("Hazard: of those still here, what share cancels this month?", loc="left", weight="bold")
ax.legend(frameon=False); clean(ax)
fig.savefig(OUT / "hazard.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Git: the lifecycle of a branch (a branch is a "subject" that can be "censored")
fig, ax = plt.subplots(figsize=(12, 5))
ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6.2)
ax.set_title("Git corner: the life of a branch (merged = event, still open = censored)", loc="left", weight="bold")
steps = [(1.2, "git switch -c\nmodule-25", "#e2e8f0"), (3.6, "commits\ngit commit", "#bfdbfe"),
         (6.0, "git push -u\nopen a PR", "#fde68a"), (8.4, "review +\nmerge into main", "#bbf7d0"),
         (10.8, "git branch -d\ngit push --delete", "#fecaca")]
for x, s, c in steps:
    box(ax, x, 4.8, s, c, w=2.0, h=1.1, fs=8.5)
for (x1, *_), (x2, *_) in zip(steps, steps[1:]):
    ax.annotate("", (x2 - 1.05, 4.8), (x1 + 1.05, 4.8), arrowprops=dict(arrowstyle="->", color="#334155"))
ax.text(0.2, 3.5, "Branch lifetimes (days from first commit to merge)", fontsize=9, weight="bold")
life = [(1, True), (3, True), (2, True), (9, False), (1, True), (5, True), (14, False)]
for i, (L, merged) in enumerate(life):
    y = 3.0 - i * .38
    ax.plot([0.5, 0.5 + L * .45], [y, y], color=GREEN if merged else BLUE, lw=3)
    ax.plot(0.5 + L * .45, y, "x" if merged else "o", color=GREEN if merged else BLUE, ms=7, mew=2, mfc="white")
    ax.text(0.5 + L * .45 + .25, y, "merged" if merged else "still open (stale?)", fontsize=7, va="center")
cmds = ("git branch --merged main        # safe to delete\n"
        "git branch --no-merged main     # still 'at risk'\n"
        "git for-each-ref --sort=committerdate \\\n"
        "   --format='%(committerdate:short) %(refname:short)' refs/heads\n"
        "git fetch --prune               # forget deleted remote branches")
ax.text(6.9, 2.0, cmds, fontsize=8, family="monospace", va="center",
        bbox=dict(fc="#f8fafc", ec=GREY, boxstyle="round,pad=.5"))
fig.savefig(OUT / "git_branch_lifecycle.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
