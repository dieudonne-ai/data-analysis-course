"""Generate PDF diagrams for module 28 (causal inference basics)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from causal_demo import (LOYALTY, START_WEEK, STORES, TRUE_CARD_EFFECT, TRUE_HOURS_EFFECT, campaign_table,  # noqa: E402
                         load, make_loyalty, make_stores, ols)

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
loyalty = load(LOYALTY, make_loyalty)
stores = load(STORES, make_stores)


def box(ax, x, y, text, fc, w=2.0, h=.8, fs=9, family=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, family=family)


def arrow(ax, a, b, color="#334155", ls="-", lw=1.4):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=color, ls=ls, lw=lw, shrinkA=22, shrinkB=22))


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. Three basic causal diagrams (DAGs)
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
specs = [
    ("Confounder: ADJUST for it", "engagement\n(visits before)", "loyalty card", "spend",
     [((0, 1), (-1, 0)), ((0, 1), (1, 0)), ((-1, 0), (1, 0))], "#fde68a",
     "Z causes both X and Y.\nIgnore it -> X looks more\npowerful than it is."),
    ("Mediator: do NOT adjust (for the total effect)", "loyalty card", "more visits", "spend",
     [((-1, 0), (0, 1)), ((0, 1), (1, 0)), ((-1, 0), (1, 0))], "#bbf7d0",
     "X works THROUGH M.\nControlling for M removes\npart of the real effect."),
    ("Collider: NEVER adjust or select on it", "rating", "featured in store", "downloads",
     [((-1, 0), (0, 1)), ((1, 0), (0, 1))], "#fecaca",
     "X and Y both cause C.\nFiltering on C creates a\nfake link between X and Y."),
]
for ax, (title, a, mid, b, edges, fc, note) in zip(axes, specs):
    ax.axis("off"); ax.set_xlim(-1.8, 1.8); ax.set_ylim(-1.6, 1.6)
    if title.startswith("Confounder"):
        pos = {(0, 1): a, (-1, 0): mid, (1, 0): b}
    elif title.startswith("Mediator"):
        pos = {(-1, 0): a, (0, 1): mid, (1, 0): b}
    else:
        pos = {(-1, 0): a, (0, 1): mid, (1, 0): b}
    for (x, y), t in pos.items():
        box(ax, x, y, t, fc if (x, y) == (0, 1) else "#e2e8f0", w=1.45, h=.7, fs=8.5)
    for s, e in edges:
        arrow(ax, s, e, color=RED if title.startswith("Collider") else "#334155")
    ax.text(0, -1.15, note, ha="center", va="center", fontsize=8.5, color="#334155")
    ax.set_title(title, fontsize=10, weight="bold")
fig.suptitle("Three shapes every analyst should recognise (arrows = 'causes')", x=.02, ha="left", weight="bold")
fig.savefig(OUT / "dag_types.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Confounding in the loyalty data
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.6, 1]})
jit = np.random.default_rng(1).uniform(-.3, .3, len(loyalty))
for m, col, lab in [(0, GREY, "non-members"), (1, BLUE, "members")]:
    d = loyalty[loyalty.member == m]
    a1.scatter(d.visits_before + jit[d.index], d.spend_after, s=5, alpha=.35, color=col, label=lab)
X = np.column_stack([np.ones(len(loyalty)), loyalty.member, loyalty.visits_before])
c = ols(loyalty.spend_after, X, ["const", "member", "visits"]).coef
xs = np.linspace(0, 15, 2)
a1.plot(xs, c.const + c.visits * xs, color="#334155", lw=2)
a1.plot(xs, c.const + c.member + c.visits * xs, color=BLUE, lw=2)
a1.text(13.2, c.const + c.visits * 13 - 9, f"gap at equal visits\n= {c.member:+.1f} EUR", fontsize=8.5, color=BLUE)
a1.set_xlabel("visits per month BEFORE the card (engagement)"); a1.set_ylabel("spend per month after launch (EUR)")
a1.legend(frameon=False, markerscale=3); clean(a1)
a1.set_title("Members were already the engaged customers", loc="left", fontsize=10)
means = loyalty.groupby("member").spend_after.mean()
vals = [means[1] - means[0], c.member, TRUE_CARD_EFFECT]
a2.bar(["naive\ndifference", "adjusted for\nengagement", "true effect\n(simulated)"], vals, color=[RED, BLUE, GREEN])
for i, v in enumerate(vals):
    a2.text(i, v + .5, f"{v:+.1f}", ha="center", fontsize=9)
a2.set_ylabel("effect of the card (EUR / month)"); clean(a2)
a2.set_title("Naive comparison is 6x too big", loc="left", fontsize=10)
fig.suptitle("Confounding: engagement drives both joining and spending", x=.02, ha="left", weight="bold")
fig.savefig(OUT / "confounding.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Simpson's paradox
camp = campaign_table(); camp["rate"] = camp.bought / camp.sent
tot = camp.groupby("email")[["sent", "bought"]].sum(); tot["rate"] = tot.bought / tot.sent
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.4), gridspec_kw={"width_ratios": [1.6, 1]})
w = .38
for i, seg in enumerate(["new", "returning"]):
    for j, (em, col) in enumerate([("A", BLUE), ("B", ORANGE)]):
        r = camp[(camp.segment == seg) & (camp.email == em)].iloc[0]
        a1.bar(i + (j - .5) * w, r.rate, w, color=col, label=f"e-mail {em}" if i == 0 else None)
        a1.text(i + (j - .5) * w, r.rate + .006, f"{r.rate:.0%}\n({r.sent} sent)", ha="center", fontsize=8)
for j, (em, col) in enumerate([("A", BLUE), ("B", ORANGE)]):
    a1.bar(2.3 + (j - .5) * w, tot.rate[em], w, color=col, hatch="//", alpha=.8)
    a1.text(2.3 + (j - .5) * w, tot.rate[em] + .006, f"{tot.rate[em]:.0%}", ha="center", fontsize=8)
a1.set_xticks([0, 1, 2.3], ["new customers", "returning customers", "OVERALL"])
a1.set_ylabel("conversion rate"); a1.set_ylim(0, .38); a1.legend(frameon=False); clean(a1)
a1.set_title("A wins in each segment ... and loses overall", loc="left", fontsize=10)
a2.axis("off")
a2.text(0, .95, "Why?", weight="bold", fontsize=10, va="top")
a2.text(0, .82, "• A was sent mostly to NEW customers (400 of 500),\n   who rarely buy (~10%).\n"
        "• B was sent mostly to RETURNING customers (400 of 500),\n   who often buy (~28%).\n"
        "• The overall rate mixes 'which e-mail' with\n   'which customers got it'.\n\n"
        "Rule: when groups differ in a variable that also\n"
        "affects the outcome (a confounder), compare\n"
        "WITHIN levels of that variable, or randomise\n"
        "who gets what (module 12).", fontsize=9, va="top")
fig.suptitle("Simpson's paradox: the aggregate can point the opposite way", x=.02, ha="left", weight="bold")
fig.savefig(OUT / "simpsons_paradox.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Collider bias
rng = np.random.default_rng(28)
rating, downloads = rng.normal(0, 1, 5_000), rng.normal(0, 1, 5_000)
feat = rating + downloads > 1.5
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), sharex=True, sharey=True)
a1.scatter(rating, downloads, s=4, alpha=.3, color=GREY)
a1.set_title(f"all apps: corr = {np.corrcoef(rating, downloads)[0, 1]:+.2f}", loc="left", fontsize=10)
a2.scatter(rating[~feat], downloads[~feat], s=4, alpha=.12, color=GREY)
a2.scatter(rating[feat], downloads[feat], s=5, alpha=.6, color=RED, label="featured (rating + downloads > 1.5)")
m, b = np.polyfit(rating[feat], downloads[feat], 1)
xs = np.linspace(-1, 3.5, 2); a2.plot(xs, m * xs + b, color=RED, lw=2)
a2.set_title(f"featured apps only: corr = {np.corrcoef(rating[feat], downloads[feat])[0, 1]:+.2f}", loc="left", fontsize=10)
a2.legend(frameon=False, loc="lower left", fontsize=8)
for a in (a1, a2):
    a.set_xlabel("rating (standardised)"); clean(a)
a1.set_ylabel("downloads (standardised)")
fig.suptitle("Collider bias: looking only at selected cases creates a trade-off that does not exist", x=.02, ha="left", weight="bold")
fig.savefig(OUT / "collider_bias.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Difference-in-differences
wk = stores.groupby(["week", "treated"]).sales.mean().unstack()
pre_gap = (wk[1] - wk[0])[wk.index < START_WEEK].mean()
fig, ax = plt.subplots(figsize=(12, 4.8))
ax.plot(wk.index, wk[0], color=GREY, lw=2, marker="o", ms=3, label="control stores (12)")
ax.plot(wk.index, wk[1], color=BLUE, lw=2, marker="o", ms=3, label="treated stores (8): later opening from week 14")
post = wk.index >= START_WEEK
ax.plot(wk.index[post], wk[0][post] + pre_gap, color=BLUE, ls="--", lw=1.5, label="counterfactual: treated WITHOUT the change")
ax.axvline(START_WEEK - .5, color="#334155", ls=":", lw=1)
ax.text(START_WEEK - .3, wk.values.min(), "change starts", fontsize=8.5)
x = 22
ax.annotate("", xy=(x, wk[1][x]), xytext=(x, wk[0][x] + pre_gap), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.6))
ax.text(x + .3, (wk[1][x] + wk[0][x] + pre_gap) / 2, f"effect ≈ +{TRUE_HOURS_EFFECT:.0f}", color=RED, fontsize=9)
ax.annotate("", xy=(4, wk[1][4]), xytext=(4, wk[0][4]), arrowprops=dict(arrowstyle="<->", color="#334155"))
ax.text(4.3, (wk[1][4] + wk[0][4]) / 2, "level gap (bigger stores):\nNOT an effect, removed by DiD", fontsize=8.5)
ax.set_xlabel("week"); ax.set_ylabel("mean weekly sales per store (EUR)")
ax.legend(frameon=False, loc="center right", fontsize=8.5, bbox_to_anchor=(1, .5)); clean(ax)
ax.set_title("DiD = (treated after - treated before) - (control after - control before)\n"
             "assumption: without the change, both groups would have moved in parallel", loc="left", fontsize=10)
fig.suptitle("Difference-in-differences: use the control group as the 'what if' line", x=.02, ha="left", weight="bold", y=1.04)
fig.savefig(OUT / "difference_in_differences.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Git corner: resolving a merge conflict
fig, ax = plt.subplots(figsize=(13, 5.4)); ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 5.4)
ax.plot([.6, 3.0], [4.4, 4.4], color="#334155", lw=2)
ax.plot([3.0, 5.6], [4.4, 4.4], color="#334155", lw=2)
ax.plot([3.0, 5.6], [4.4, 3.4], color=ORANGE, lw=2)
for x, y, lab, col in [(.6, 4.4, "base", GREY), (3.0, 4.4, "merge-base", GREY), (5.6, 4.4, "main\n(ours)", BLUE),
                       (5.6, 3.4, "my-branch\n(theirs)", ORANGE)]:
    ax.plot(x, y, "o", ms=11, color=col, mec="#334155")
    ax.text(x, y + .32 if y > 4 else y - .55, lab, ha="center", fontsize=8.5)
ax.text(.6, 2.7, "main:      threshold = 0.05\nmy-branch: threshold = 0.01\n-> both edited the SAME line",
        fontsize=8.5, family="monospace", va="top")
box(ax, 9.4, 3.9, "<<<<<<< HEAD\nthreshold = 0.05\n||||||| merge-base\nthreshold = 0.10\n=======\n"
    "threshold = 0.01\n>>>>>>> my-branch", "#fef3c7", w=3.6, h=2.4, fs=8.5, family="monospace")
ax.text(9.4, 5.25, "the file after  git merge my-branch  (with merge.conflictStyle=diff3)", ha="center", fontsize=8.5)
ax.annotate("", xy=(7.5, 3.9), xytext=(6.3, 3.9), arrowprops=dict(arrowstyle="->"))
steps = ["1. git status            -> 'both modified: config.py'",
         "2. edit the file, keep the right value, delete the <<< ||| === >>> lines",
         "   or take one side:  git checkout --ours config.py   /   --theirs",
         "3. re-run the analysis / tests",
         "4. git add config.py && git commit      (or  git merge --abort  to start again)"]
for i, s in enumerate(steps):
    ax.text(.6, 1.75 - i * .36, s, fontsize=9, family="monospace")
ax.set_title("Git corner: a merge conflict is two edits to the same lines - git asks YOU to decide", loc="left", weight="bold")
fig.savefig(OUT / "git_merge_conflict.pdf", bbox_inches="tight"); plt.close(fig)

print("Diagrams written to", OUT)
