"""Generate PDF diagrams for module 25 (cohort & retention analysis)."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT.parent / "examples"))
from cohort_demo import END, activity_log, cohort_table, durations, kaplan_meier, load  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
df = load()
log = activity_log(df)
counts, ret, size = cohort_table(df, log)
d, e = durations(df)


def box(ax, x, y, text, fc, w=2.4, h=1.0, fs=9, ec="#334155"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec=ec))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. From event log to cohort table (the pipeline)
fig, ax = plt.subplots(figsize=(12, 3.6)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 3.6)
steps = [("activity log\ncustomer_id, month", "#e2e8f0"),
         ("cohort = first month\nper customer", "#bfdbfe"),
         ("age = month - cohort\n(0, 1, 2, ...)", "#bfdbfe"),
         ("count unique customers\nby cohort x age", "#fde68a"),
         ("divide each row by\nits age-0 size", "#bbf7d0")]
for i, (t, c) in enumerate(steps):
    x = 1.2 + i * 2.4
    box(ax, x, 2.2, t, c, w=2.1, h=1.2, fs=9)
    if i:
        ax.annotate("", xy=(x - 1.08, 2.2), xytext=(x - 1.32, 2.2), arrowprops=dict(arrowstyle="->"))
code = ['log["cohort"] = log.customer_id.map(first_month)',
        'log["age"]    = (log.month - log.cohort).apply(lambda d: d.n)',
        'counts = log.groupby(["cohort", "age"]).customer_id.nunique().unstack()',
        'retention = counts.div(counts[0], axis=0)']
for i, c in enumerate(code):
    ax.text(0.2, 1.1 - i * 0.3, c, family="monospace", fontsize=8.5, color="#334155")
ax.set_title("Building a cohort retention table in four lines of pandas", loc="left", weight="bold")
fig.savefig(OUT / "cohort_pipeline.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Cohort heatmap with the three reading directions
R = ret.values * 100
fig, ax = plt.subplots(figsize=(11, 6.2))
m = np.ma.masked_invalid(R)
im = ax.imshow(m, cmap="Blues", vmin=40, vmax=100, aspect="auto")
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        if not np.isnan(R[i, j]):
            ax.text(j, i, f"{R[i, j]:.0f}", ha="center", va="center", fontsize=7.5,
                    color="white" if R[i, j] > 80 else "#0f172a")
ax.set_xticks(range(R.shape[1]), [f"M{j}" for j in range(R.shape[1])])
ax.set_yticks(range(R.shape[0]), [f"{p.strftime('%b')} (n={int(size[p])})" for p in ret.index])
ax.set_xlabel("months since signup (age)"); ax.set_ylabel("signup cohort")
ax.add_patch(plt.Rectangle((-.5, -.5), 7, 1, fill=False, ec=ORANGE, lw=2))
ax.text(11.6, -1.0, "row: one cohort ages", color=ORANGE, ha="right", fontsize=9, weight="bold")
ax.add_patch(plt.Rectangle((.5, -.5), 1, 11, fill=False, ec=RED, lw=2))
ax.text(1.6, 10.8, "column: same age, compare cohorts", color=RED, fontsize=9, weight="bold", va="center")
ax.plot([5.3, -0.3], [-0.3, 5.3], color=GREEN, lw=2, ls="--")
ax.text(6.0, 9.0, "dashed diagonal = one calendar month (Jun):\nevery cohort seen in the same month", color=GREEN, fontsize=9, weight="bold")
ax.axhline(5.5, color="#0f172a", lw=1.2, ls=":")
ax.text(11.6, 5.5, "new onboarding\n(from Jul)", fontsize=8, va="center", ha="right")
fig.colorbar(im, ax=ax, label="% still active", shrink=.8)
ax.set_title("Cohort retention table: the triangle shape is normal (young cohorts have no future yet)",
             loc="left", weight="bold", pad=22)
fig.savefig(OUT / "cohort_heatmap.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Retention curves: before vs after the onboarding change
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4))
for k, p in enumerate(ret.index[:11]):
    row = ret.loc[p].dropna() * 100
    col = GREY if p.month < 7 else BLUE
    a1.plot(row.index, row.values, color=col, alpha=.8, lw=1.4, marker="o", ms=2.5)
a1.plot([], [], color=GREY, label="Jan-Jun cohorts"); a1.plot([], [], color=BLUE, label="Jul-Nov cohorts")
a1.legend(frameon=False); a1.set_ylim(40, 102); a1.set_xlabel("months since signup"); a1.set_ylabel("% retained")
a1.set_title("One line per cohort", loc="left", weight="bold"); clean(a1)
active = log.groupby("month")["customer_id"].nunique()
new = df.groupby("signup").size().reindex(active.index, fill_value=0)
churned = df[df.churn_month != ""].groupby("churn").size().reindex(active.index, fill_value=0)
x = np.arange(len(active))
a2.bar(x, new, color=GREEN, label="new signups")
a2.bar(x, -churned, color=RED, label="churned")
a2.plot(x, active / 5, color=BLUE, marker="o", label="active customers / 5")
a2.axhline(0, color="#0f172a", lw=.8)
a2.set_xticks(x, [p.strftime("%b") for p in active.index]); a2.legend(frameon=False, fontsize=8)
a2.set_title("Calendar view: growth = new - churned", loc="left", weight="bold"); clean(a2)
fig.savefig(OUT / "retention_curves.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Censoring and Kaplan-Meier
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw=dict(width_ratios=[1, 1.15]))
sample = df.sample(10, random_state=3).sort_values("signup")
for i, r in enumerate(sample.itertuples()):
    s0 = r.signup.month - 1
    if r.churn is not pd.NaT:
        s1 = r.churn.month - 1 + (12 if r.churn.year > 2026 else 0)
        a1.plot([s0, s1], [i, i], color=RED, lw=3); a1.plot(s1, i, "x", color=RED, ms=9, mew=2)
    else:
        a1.plot([s0, 11], [i, i], color=BLUE, lw=3); a1.plot(11, i, ">", color=BLUE, ms=7)
a1.axvline(11, color="#0f172a", ls="--", lw=1); a1.text(11.15, -0.6, "today (Dec)", fontsize=8)
a1.set_xticks(range(12), [p.strftime("%b")[0] for p in pd.period_range("2026-01", periods=12, freq="M")])
a1.set_yticks([]); a1.set_xlim(-.5, 12.5); clean(a1)
a1.plot([], [], color=RED, lw=3, marker="x", label="churned (event observed)")
a1.plot([], [], color=BLUE, lw=3, marker=">", label="still active (censored)")
a1.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(.5, -.08), ncol=2)
a1.set_title("10 customers: we don't know when the blue ones will leave", loc="left", weight="bold", fontsize=10)
km = kaplan_meier(d, e)
a2.step(km.month, km.survival, where="post", color=BLUE, lw=2, label="Kaplan-Meier")
naive = [1 - ((e == 1) & (d <= t)).sum() / len(d) for t in km.month]
a2.step(km.month, naive, where="post", color=GREY, ls="--", label="naive: 1 - churned/all (too optimistic)")
a2.axhline(.5, color=ORANGE, lw=1, ls=":"); a2.text(0.2, .52, "median", color=ORANGE, fontsize=8)
a2.set_ylim(0, 1.02); a2.set_xlabel("months since signup"); a2.set_ylabel("P(still active)")
a2.text(3.2, .2, "S(t) = S(t-1) x (1 - churned_t / at_risk_t)\nat_risk = customers observed at least t months",
        family="monospace", fontsize=8, bbox=dict(fc="#f8fafc", ec=GREY))
a2.legend(frameon=False, fontsize=8); clean(a2)
a2.set_title("Survival curve that respects censoring", loc="left", weight="bold", fontsize=10)
fig.savefig(OUT / "kaplan_meier.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Survival by plan
fig, ax = plt.subplots(figsize=(8, 4.4))
for plan, col in (("monthly", ORANGE), ("annual", GREEN)):
    msk = (df.plan == plan).values
    k = kaplan_meier(d[msk], e[msk])
    ax.step(k.month, k.survival, where="post", color=col, lw=2, label=f"{plan} (n={msk.sum()})")
ax.set_ylim(0, 1.02); ax.set_xlabel("months since signup"); ax.set_ylabel("P(still active)")
ax.legend(frameon=False); clean(ax)
ax.set_title("Kaplan-Meier by segment: annual customers stay much longer", loc="left", weight="bold")
fig.savefig(OUT / "survival_by_plan.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Git corner: lifetime of each pull-request branch (first branch commit -> merge)
def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()

life = []
for line in git("log", "--merges", "--first-parent", "--format=%H %P %ct %s").splitlines():
    h, p1, p2, ct, *subj = line.split()
    first = git("log", "--format=%ct", f"{p1}..{p2}").split()
    if first:
        start = int(first[-1])
        life.append((datetime.fromtimestamp(start), (int(ct) - start) / 60, " ".join(subj)))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw=dict(width_ratios=[1, 1.2]))
a1.axis("off"); a1.set_xlim(0, 10); a1.set_ylim(0, 5)
cmds = [("git for-each-ref --sort=-committerdate refs/heads", "branches, most recent first"),
        ("git branch --merged main  /  --no-merged", "finished vs still open work"),
        ("git log --merges --first-parent main", "one line per merged PR")]
for i, (cmd, why) in enumerate(cmds):
    box(a1, 5, 4.2 - i * 1.5, f"{cmd}\n{why}", ["#e2e8f0", "#bfdbfe", "#bbf7d0"][i], w=9.6, h=1.0, fs=8.5)
a1.set_title("Branches have a birth and a death too", loc="left", weight="bold")
if life:
    life.sort()
    y = np.arange(len(life))
    mins = [max(m, .1) for _, m, _ in life]
    a2.barh(y, mins, color=BLUE); a2.set_xscale("log")
    for y_, m in zip(y, mins):
        a2.text(m * 1.1, y_, f"{m:.1f}", va="center", fontsize=6.5)
    a2.set_yticks(y, [t.strftime("%d %b") for t, _, _ in life], fontsize=7)
    a2.set_xlabel("minutes from first branch commit to merge (log scale)")
    a2.set_title(f"{len(life)} PR branches in this repo: all short-lived", loc="left", weight="bold")
clean(a2)
fig.savefig(OUT / "git_branch_lifetime.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
