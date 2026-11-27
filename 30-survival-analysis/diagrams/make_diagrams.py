"""Generate PDF diagrams for module 30 (survival analysis)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from survival_demo import CUTOFF, PLANS, SHAPE, kaplan_meier, life_table, load, logrank, median_survival, rmst  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
COLORS = {"weekly": ORANGE, "flex": BLUE}
df = load()


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def box(ax, x, y, text, fc, w=2.0, h=.8, fs=9, family=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, family=family, multialignment="left" if family else "center")


def step(ax, km, color, label, band=True):
    t = np.r_[0, km.t]
    ax.step(t, np.r_[1, km.surv], where="post", color=color, lw=2, label=label)
    if band:
        ax.fill_between(t, np.r_[1, km.lo], np.r_[1, km.hi], step="post", color=color, alpha=.18, lw=0)


# 1. Censoring: calendar time vs tenure
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
cust = [("A", 20, 140, 1), ("B", 60, 305, 0), ("C", 150, 40, 1), ("D", 210, 155, 0), ("E", 270, 60, 1), ("F", 320, 45, 0)]
for i, (name, start, dur, ev) in enumerate(cust):
    y = len(cust) - i
    for ax, x0 in [(axes[0], start), (axes[1], 0)]:
        ax.plot([x0, x0 + dur], [y, y], color=RED if ev else BLUE, lw=3)
        ax.plot(x0 + dur, y, "x" if ev else "o", color=RED if ev else BLUE, ms=9, mfc="white" if not ev else None, mew=2)
        ax.text(x0 - 6, y, name, ha="right", va="center", fontsize=9, weight="bold")
axes[0].axvline(365, color="#334155", ls="--"); axes[0].text(362, 6.6, f"analysis date\n{CUTOFF.date()}", ha="right", fontsize=8.5)
axes[0].set_xlabel("calendar day of 2025 (signup -> leave or today)"); axes[0].set_xlim(-25, 400)
axes[0].set_title("Calendar time: everyone still active at the line is CENSORED", loc="left", fontsize=10, weight="bold")
axes[1].set_xlabel("tenure in days (all customers start at 0)"); axes[1].set_xlim(-25, 330)
axes[1].set_title("Tenure time: what survival analysis uses", loc="left", fontsize=10, weight="bold")
axes[1].text(170, 0.25, "x = churned (event)    o = still active (censored: stayed AT LEAST this long)", fontsize=8.5, ha="center")
for ax in axes:
    ax.set_yticks([]); ax.set_ylim(0, 7.2); clean(ax); ax.spines["left"].set_visible(False)
fig.suptitle("Censoring: for B, D and F we know a minimum tenure, not the real one. Dropping them or treating them as churned biases tenure down.",
             x=.02, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "censoring_timeline.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Kaplan-Meier curve with CI and the naive mistakes
fig, ax = plt.subplots(figsize=(9.5, 5))
km = kaplan_meier(df.days, df.churned)
step(ax, km, BLUE, "Kaplan-Meier S(t) with 95% Greenwood band")
naive = np.r_[1, 1 - np.cumsum(np.bincount(df.days[df.churned == 1], minlength=366)[1:366]) / len(df)]
ax.plot(np.arange(366), naive, color=GREY, ls="--", lw=1.6, label="naive: 1 - churned so far / all customers")
med = median_survival(km)
ax.plot([0, med, med], [.5, .5, 0], color="#334155", ls=":", lw=1)
ax.text(med + 4, .52, f"median = {med} days", fontsize=9)
for t in (30, 90, 180):
    s = km[km.t <= t].surv.iloc[-1]
    ax.plot(t, s, "o", color=BLUE); ax.text(t + 4, s + .025, f"S({t}) = {s:.0%}", fontsize=8.5)
ax.annotate("censored customers leave the risk set\nwithout counting as churn -> curve keeps falling\n"
            "below the naive line, and the band widens\nas fewer customers are still observed",
            xy=(320, km[km.t <= 320].surv.iloc[-1]), xytext=(200, .72), fontsize=8.5, arrowprops=dict(arrowstyle="->", color="#334155"))
ax.set_xlim(0, 365); ax.set_ylim(0, 1.02); ax.set_xlabel("days since signup"); ax.set_ylabel("share still subscribed")
ax.legend(frameon=False, loc="lower left", fontsize=9); clean(ax)
ax.set_title("S(t) = product over event times of (1 - churned / at risk)", loc="left", fontsize=10, weight="bold")
fig.tight_layout(); fig.savefig(OUT / "kaplan_meier.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Two plans + RMST areas
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for p in PLANS:
    sub = df[df.plan == p]
    k = kaplan_meier(sub.days, sub.churned)
    step(axes[0], k, COLORS[p], f"{p} (n={len(sub)}, median {median_survival(k):.0f} d)")
    t = np.r_[0, k.t[k.t < 365], 365]; s = np.r_[1, k.surv[k.t < 365], k.surv[k.t < 365].iloc[-1]]
    axes[1].fill_between(t, s, step="post", color=COLORS[p], alpha=.25)
    axes[1].step(t, s, where="post", color=COLORS[p], lw=2, label=f"{p}: RMST(365) = {rmst(k, 365):.0f} days")
_, _, chi2, pval = logrank(df.days, df.churned, df.plan.to_numpy())
axes[0].text(200, .8, f"log-rank test:\nchi2 = {chi2:.1f}, p = {pval:.0e}", fontsize=9, bbox=dict(fc="white", ec="#cbd5e1"))
axes[0].set_title("Kaplan-Meier by plan (bands = 95% CI)", loc="left", fontsize=10, weight="bold")
axes[1].set_title("RMST = area under the curve up to 365 days", loc="left", fontsize=10, weight="bold")
for ax in axes:
    ax.set_xlim(0, 365); ax.set_ylim(0, 1.02); ax.set_xlabel("days since signup"); ax.legend(frameon=False, fontsize=9, loc="lower left"); clean(ax)
axes[0].set_ylabel("share still subscribed")
fig.suptitle("Compare groups with the whole curve (log-rank) and summarise it with RMST - a mean that is valid with censoring",
             x=.02, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "plans_rmst.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Hazard (life table)
fig, ax = plt.subplots(figsize=(9.5, 4.6))
lt = life_table(df.days.to_numpy(), df.churned.to_numpy())
lt = lt[lt.at_risk >= 80]
bars = ax.bar((lt["from"] + 15) / 30, lt.hazard, width=.8, color=[RED if i == 0 else ORANGE for i in range(len(lt))], alpha=.8)
for b, (_, r) in zip(bars, lt.iterrows()):
    ax.text(b.get_x() + b.get_width() / 2, r.hazard + .004, f"{r.hazard:.0%}\nn={int(r.at_risk)}", ha="center", fontsize=7.5)
ax.set_xticks((lt["from"] + 15) / 30, [f"m{i + 1}" for i in range(len(lt))])
ax.set_xlabel("month of tenure"); ax.set_ylabel("hazard = churned in month / at risk at start")
ax.set_ylim(0, .23); clean(ax)
ax.set_title(f"The hazard falls with tenure (Weibull shape {SHAPE} < 1): month 1 is where retention is won or lost",
             loc="left", fontsize=10, weight="bold")
ax.text(len(lt) - .5, .19, "n = customers at risk: late months rest on\nfew customers, so treat them as noisy",
        ha="right", fontsize=8.5, bbox=dict(fc="white", ec="#cbd5e1"))
fig.tight_layout(); fig.savefig(OUT / "hazard_life_table.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Cheat sheet
fig, ax = plt.subplots(figsize=(12, 6.8)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 7)
ax.text(.1, 6.7, "Survival analysis cheat sheet", fontsize=14, weight="bold")
cards = [
    (2.9, 5.4, "Data you need, one row per subject\nduration = time from start to event or to today\nevent = 1 churned, 0 still active (censored)", "#dbeafe"),
    (9.0, 5.4, "Censoring rule\nCensored subjects count in 'at risk' until their last\nday, then leave quietly. Never drop them,\nnever treat them as events.", "#fee2e2"),
    (2.9, 3.6, "Kaplan-Meier  S(t) = prod (1 - d_i / n_i)\nd = events at t_i,  n = at risk just before t_i\nGreenwood -> 95% band;  median = first t with S <= 0.5", "#dcfce7"),
    (9.0, 3.6, "Hazard  h(t) = P(leave at t | still here)\nfalling: early churn (onboarding!)\nflat: random churn   rising: wear-out / contract end", "#fef3c7"),
    (2.9, 1.8, "Compare groups\nlog-rank test (whole curve), S(t) at fixed t,\nmedian, RMST difference. Groups that chose\nthemselves are NOT a causal comparison.", "#ede9fe"),
    (9.0, 1.8, "RMST(T) = area under S(t) from 0 to T\n= expected days in the first T days\n-> x monthly price = revenue per signup\n(valid with censoring, unlike a raw mean)", "#e0f2fe"),
]
for x, y, t, fc in cards:
    box(ax, x, y, t, fc, w=5.6, h=1.45, fs=9.5)
ax.text(.1, .45, "Next steps: Cox proportional-hazards regression (several covariates at once), parametric models (Weibull) "
        "to extrapolate past the data,\ncompeting risks (cancel vs pause vs payment failure). Python library: lifelines.", fontsize=9, color="#334155")
fig.savefig(OUT / "survival_cheatsheet.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Git corner: time in git
fig, ax = plt.subplots(figsize=(12.5, 5.2)); ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 5.2)
ax.text(.1, 4.95, "Time in git: date filters, date formats and how long lines of code survive", fontsize=12, weight="bold")
days = [0, 1.5, 3, 4.6, 6.2, 7.6, 9.2, 10.8]
labels = ["Nov 20", "Nov 21", "Nov 22", "Nov 23", "Nov 24", "Nov 25", "Nov 26", "Nov 27"]
ax.plot([.6, 11.6], [3.7, 3.7], color=GREY, lw=2)
for i, (x, lab) in enumerate(zip(days, labels)):
    inside = 3 <= x <= 7.6
    ax.plot(x + .8, 3.7, "o", ms=13, color=GREEN if inside else GREY, mec="#334155")
    ax.text(x + .8, 3.25, lab, ha="center", fontsize=8)
ax.add_patch(plt.Rectangle((3.55, 3.4), 5.1, .65, fc="none", ec=GREEN, ls="--", lw=1.5))
ax.text(6.1, 4.25, 'git log --since="2026-11-22" --until="2026-11-25"', ha="center", fontsize=9, family="monospace", color=GREEN)
box(ax, 3.1, 1.6,
    "git log --date=short --format='%ad %h %s'\ngit log --date=relative -3     # '2 days ago'\n"
    "git log --since='2 weeks ago' --oneline\ngit rev-list --count --since='1 month ago' HEAD\n"
    "git show main@{yesterday}      # reflog: where\n                               # main was locally", "#f1f5f9", w=5.9, h=2.1, fs=8.5, family="monospace")
box(ax, 9.4, 1.6,
    "Code-line survival (blame = 'birth date' of each line)\n"
    "git blame --date=short README.md\ngit blame --line-porcelain README.md \\\n  | grep '^author-time' | sort | uniq -c\n"
    "%ad author date  vs  %cd committer date:\nrebase / cherry-pick keep %ad, change %cd", "#f1f5f9", w=5.9, h=2.1, fs=8.5, family="monospace")
fig.savefig(OUT / "git_dates.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
