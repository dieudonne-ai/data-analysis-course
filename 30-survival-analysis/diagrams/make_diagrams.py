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
from survival_demo import STUDY_MONTHS, kaplan_meier, load, median_lifetime  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
COLORS = {"monthly": BLUE, "annual": ORANGE}
df = load()
km = {p: kaplan_meier(df[df.plan == p].duration, df[df.plan == p].churned) for p in ("monthly", "annual")}


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def box(ax, x, y, text, fc, w=2.0, h=.8, fs=9, family=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, family=family,
            multialignment="left" if family else "center")


def steps(km_df):
    x = np.concatenate([[0], km_df.month.to_numpy()])
    y = np.concatenate([[1], km_df.survival.to_numpy()])
    lo = np.concatenate([[1], km_df.ci_low.to_numpy()])
    hi = np.concatenate([[1], km_df.ci_high.to_numpy()])
    return x, y, lo, hi


# 1. Censoring timeline: calendar time vs time since joining
sample = df.groupby("churned").sample(6, random_state=4).sort_values("join_month").reset_index(drop=True)
fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
for i, r in sample.iterrows():
    end = r.join_month + r.duration
    for ax, start in [(axes[0], r.join_month), (axes[1], 0)]:
        stop = start + r.duration
        ax.plot([start, stop], [i, i], color=RED if r.churned else GREEN, lw=2.5)
        if r.churned:
            ax.plot(stop, i, "x", color=RED, ms=9, mew=2.5)
        else:
            ax.plot(stop, i, ">", color=GREEN, ms=8)
    axes[0].text(-0.5, i, f"#{r.member_id}", ha="right", va="center", fontsize=8)
axes[0].axvline(STUDY_MONTHS, color="#334155", ls="--")
axes[0].text(STUDY_MONTHS, len(sample) - .3, " data pulled\n (month 36)", fontsize=8.5, va="top")
axes[0].set_title("Calendar time: members join at different dates", loc="left", fontsize=10, weight="bold")
axes[0].set_xlabel("calendar month"); axes[0].set_xlim(-4, 41)
axes[1].set_title("Time since joining: all start at 0 (what the analysis uses)", loc="left", fontsize=10, weight="bold")
axes[1].set_xlabel("months as a member (duration)")
for ax in axes:
    ax.set_yticks([]); clean(ax); ax.spines["left"].set_visible(False)
axes[1].plot([], [], "x", color=RED, mew=2.5, label="churned = 1 (event seen)")
axes[1].plot([], [], ">", color=GREEN, label="churned = 0 (censored: still active, lifetime is AT LEAST this)")
axes[1].legend(loc="upper center", bbox_to_anchor=(.5, -.14), fontsize=8.5, frameon=False, ncol=2)
fig.suptitle("Censoring: for still-active members we only know a lower bound. Dropping them or treating them as churned both bias the answer.",
             x=.02, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "censoring_timeline.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Kaplan-Meier by hand on 8 members
toy_t = np.array([2, 3, 3, 5, 6, 8, 8, 9]); toy_e = np.array([1, 1, 0, 1, 0, 1, 1, 0])
toy = kaplan_meier(toy_t, toy_e)
fig, (a0, a1) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw=dict(width_ratios=[1.1, 1]))
a0.axis("off")
lines = ["8 members: durations 2 3 3+ 5 6+ 8 8 9+   (+ = censored)", "",
         "month  at risk  churned   1 - churned/at risk    S(t)"]
s = 1.0
for r in toy.itertuples():
    s_prev, s = s, r.survival
    lines.append(f"  {r.month:>2}      {r.at_risk}        {r.churned}       1 - {r.churned}/{r.at_risk} = {1 - r.churned / r.at_risk:.3f}"
                 f"     {s_prev:.3f} x {1 - r.churned / r.at_risk:.3f} = {s:.3f}")
lines += ["", "- 'at risk' = still a member at the start of the month", "- censored members count in 'at risk' until they leave the data,",
          "  then simply drop out: they never count as a churn", f"- median = first month where S(t) <= 0.5  ->  month {median_lifetime(toy):.0f}"]
a0.text(0, 1, "\n".join(lines), family="monospace", fontsize=9, va="top")
a0.set_title("Kaplan-Meier step by step", loc="left", fontsize=10, weight="bold")
x, y, _, _ = steps(toy)
a1.step(np.append(x, 9), np.append(y, y[-1]), where="post", color=BLUE, lw=2.2)
for t, e in zip(toy_t, toy_e):
    if not e:
        a1.plot(t, float(toy[toy.month <= t].survival.iloc[-1]) if (toy.month <= t).any() else 1, "|", color=GREEN, ms=14, mew=2)
a1.axhline(.5, color=GREY, ls=":"); a1.text(.2, .52, "S = 0.5", fontsize=8, color="#475569")
a1.set_ylim(0, 1.05); a1.set_xlabel("months as a member"); a1.set_ylabel("S(t) = share still a member")
a1.set_title("The curve drops only at churns; | marks a censored member", loc="left", fontsize=10); clean(a1)
fig.tight_layout(); fig.savefig(OUT / "km_by_hand.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Kaplan-Meier curves for both plans with 95% bands
fig, ax = plt.subplots(figsize=(10.5, 5))
for plan, k in km.items():
    x, y, lo, hi = steps(k)
    ax.step(x, y, where="post", color=COLORS[plan], lw=2.2, label=f"{plan} plan (median {median_lifetime(k):.0f} months)")
    ax.fill_between(x, lo, hi, step="post", color=COLORS[plan], alpha=.18)
    med = median_lifetime(k)
    ax.plot([med, med], [0, .5], color=COLORS[plan], ls=":", lw=1.2)
ax.axhline(.5, color=GREY, ls=":")
ax.annotate("annual: nobody can leave\nbefore the 1st renewal", xy=(8, 1), xytext=(14, .88), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#475569"))
ax.annotate("cliff at each renewal", xy=(24, .42), xytext=(27, .62), fontsize=9, arrowprops=dict(arrowstyle="->", color="#475569"))
ax.annotate("monthly: smooth, steady decline\n(same risk every month)", xy=(6, .64), xytext=(1, .25), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#475569"))
ax.set_xlim(0, 36); ax.set_ylim(0, 1.03); ax.set_xticks(range(0, 37, 6))
ax.set_xlabel("months since joining"); ax.set_ylabel("S(t) = share still a member"); clean(ax)
ax.legend(frameon=False, loc="upper right")
ax.set_title("Kaplan-Meier survival curves with 95% bands (Greenwood). Log-rank test: p < 0.001", loc="left", weight="bold")
fig.tight_layout(); fig.savefig(OUT / "km_curves.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Hazard per month
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2), sharey=True)
for ax, (plan, k) in zip(axes, km.items()):
    full = k.set_index("month").reindex(range(1, 36))
    at_risk = np.array([(df[df.plan == plan].duration >= t).sum() for t in full.index])
    hz = full.churned.fillna(0).to_numpy() / at_risk
    ax.bar(full.index, hz, color=[COLORS[plan] if n >= 100 else GREY for n in at_risk])
    ax.set_xlabel("month since joining"); clean(ax)
    ax.set_title(f"{plan}: hazard = churned / at risk", loc="left", fontsize=10, weight="bold")
axes[0].axhline(.075, color="#334155", ls="--"); axes[0].text(1, .085, "truth 7.5% every month", fontsize=8.5)
axes[0].set_ylabel("monthly hazard")
axes[1].text(25.5, .25, "35% of members do not\nrenew at month 12 and\nat month 24. Zero risk\nin other months.", fontsize=9)
axes[0].text(22, .2, "grey = fewer than 100 at risk:\nnoisy, do not over-read", fontsize=8.5, color="#475569")
fig.suptitle("The hazard tells you WHEN members leave - and therefore when to act", x=.02, ha="left", weight="bold")
fig.tight_layout(); fig.savefig(OUT / "hazard.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Cheat sheet
fig, ax = plt.subplots(figsize=(12, 6.4)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6.6)
cards = [
    (2.0, 5.4, "duration + event", "one row per subject:\nhow long we watched,\nand did the event happen?\n(0 = censored)", "#dbeafe"),
    (6.0, 5.4, "S(t) survival", "share still 'alive' after t\nKaplan-Meier: product of\n(1 - churned / at risk)", "#dcfce7"),
    (10.0, 5.4, "h(t) hazard", "risk of the event now,\ngiven survival so far\nflat = memoryless", "#fde68a"),
    (2.0, 3.2, "median lifetime", "first t with S(t) <= 0.5\nundefined if the curve\nnever gets that low", "#fee2e2"),
    (6.0, 3.2, "log-rank test", "do 2+ groups share one curve?\nobserved vs expected events\nchi2 with (groups - 1) df", "#ede9fe"),
    (10.0, 3.2, "RMST", "area under S(t) up to a horizon\n= expected time 'alive'\n-> lifetime value x price", "#e0f2fe"),
]
for x, y, title, body, fc in cards:
    box(ax, x, y, "", fc, w=3.6, h=1.7)
    ax.text(x, y + .55, title, ha="center", fontsize=11, weight="bold")
    ax.text(x, y - .15, body, ha="center", va="center", fontsize=9)
ax.text(.3, 1.6, "Use it for: churn, time to first purchase, time to repay a loan, machine failure, time to hire, how long a PR stays open.",
        fontsize=9.5)
ax.text(.3, 1.05, "Pitfalls: dropping censored rows | 'mean of observed durations' | reading the tail where few are at risk |"
        "\n               censoring that is NOT random (people who leave the study because they are about to churn)", fontsize=9.5)
ax.text(.3, .25, "Next steps: Cox proportional-hazards regression (lifelines: CoxPHFitter) to add several drivers at once.", fontsize=9.5,
        color="#475569")
ax.set_title("Survival analysis cheat sheet", loc="left", fontsize=13, weight="bold")
fig.savefig(OUT / "survival_cheatsheet.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Git corner: time in git
fig, (a0, a1) = plt.subplots(1, 2, figsize=(13.5, 4.8), gridspec_kw=dict(width_ratios=[1.15, 1]))
a0.set_xlim(0, 10); a0.set_ylim(-.6, 2.6); a0.axis("off")
a0.plot([0.3, 9.7], [0, 0], color="#334155", lw=2); a0.text(9.8, 0, "main", va="center", fontsize=9)
for xc in (1, 9):
    a0.plot(xc, 0, "o", color="#334155", ms=10)
a0.plot([1, 2, 4, 6.5, 9], [0, 1.0, 1.0, 1.0, 0], color=BLUE, lw=2)
for xc, lab in [(2, "first commit\n(author date)"), (4, "more work"), (6.5, "rebased:\nnew committer date")]:
    a0.plot(xc, 1.0, "o", color=BLUE, ms=10); a0.text(xc, 1.25, lab, ha="center", fontsize=8.5)
a0.text(9, -.45, "merge commit", ha="center", fontsize=8.5)
a0.annotate("", xy=(9, 2.4), xytext=(2, 2.4), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.6))
a0.text(5.5, 2.5, "time to merge = event; open branches = censored", ha="center", fontsize=9, color=RED)
a0.set_title("Every commit has TWO dates: author (%ad / %at) and committer (%cd / %ct)", loc="left", fontsize=10, weight="bold")
cmds = """git log --format='%h %ad %cd %s' --date=short   # both dates
git log --since='2 weeks ago' --until=yesterday   # date window
git rev-list --count --since=2026-11-01 main      # commits since
git log -1 --format=%cr main                       # '3 hours ago'
git show main@{yesterday}:README.md                # file as main was
git diff main@{1.week.ago} main --stat             # change in a week
git log --merges --first-parent main \\
    --format='%ct %s'          # merge times -> time-to-merge data
git commit --date='2026-11-27 18:00'   # set author date"""
a1.axis("off"); a1.text(0, 1, cmds, family="monospace", fontsize=8.6, va="top")
a1.text(0, .05, "main@{...} uses YOUR reflog (local, ~90 days),\nnot the shared history. Dates are text in commits: not proof.",
        fontsize=8.5, color="#475569")
a1.set_title("Asking git 'when?'", loc="left", fontsize=10, weight="bold")
fig.tight_layout(); fig.savefig(OUT / "git_time_travel.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
