"""Generate PDF diagrams for module 22 (model interpretability)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from interpret_demo import (FEATURES, X, boost, fit_model, log_loss, partial_dependence,  # noqa: E402
                            permutation_importance, predict, shapley_2, sigmoid, split_counts, te, tr, y)


def box(ax, x, y_, text, fc, w=2.4, h=1.0, fs=9):
    ax.add_patch(FancyBboxPatch((x - w / 2, y_ - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y_, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#334155"))


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


f0, trees, proba = fit_model()

# 1. Map of interpretation methods: global vs local
fig, ax = plt.subplots(figsize=(11, 4.6)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5.6)
box(ax, 6, 5.0, "trained model (black box)\np = f(tenure, support_calls)", "#e2e8f0", w=4, h=.9)
ax.text(3, 3.85, "GLOBAL: how does the model behave overall?", ha="center", weight="bold", color="#1e40af")
ax.text(9, 3.85, "LOCAL: why THIS prediction?", ha="center", weight="bold", color="#065f46")
arrow(ax, (5, 4.5), (3, 4.1)); arrow(ax, (7, 4.5), (9, 4.1))
box(ax, 1.6, 2.6, "feature importance\n(split counts,\npermutation)", "#bfdbfe", w=2.5, h=1.3)
box(ax, 4.4, 2.6, "partial dependence\n(average effect of\none feature)", "#bfdbfe", w=2.5, h=1.3)
box(ax, 7.6, 2.6, "ICE curves\n(effect for each\ncustomer)", "#bbf7d0", w=2.5, h=1.3)
box(ax, 10.4, 2.6, "Shapley values\n(split one prediction\ninto contributions)", "#bbf7d0", w=2.5, h=1.3)
ax.text(3, .9, "answers: 'which features matter?'\n'is the effect up, down, or curved?'", ha="center", fontsize=9)
ax.text(9, .9, "answers: 'why is customer #42 at 93%?'\n'what would change their score?'", ha="center", fontsize=9)
ax.plot([6, 6], [.3, 3.9], color="#cbd5e1")
ax.set_title("Model interpretability: two families of questions", weight="bold", loc="left")
fig.savefig(OUT / "methods_map.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Split-count vs permutation importance, with a pure-noise column
rng = np.random.default_rng(1)
Xn = np.column_stack([X, rng.normal(size=len(y))])
f0n, tn, _ = boost(Xn[tr], y[tr], 50, lr=0.1, max_depth=2, X_eval=Xn[tr[:1]])


def proba_n(Xq):
    F = np.full(len(Xq), f0n)
    for t in tn:
        F += 0.1 * predict(t, Xq)
    return sigmoid(F)


names = FEATURES + ["noise"]
counts = np.zeros(3, int)


def walk(n):
    if "v" not in n:
        counts[n["f"]] += 1; walk(n["L"]); walk(n["R"])


for t in tn:
    walk(t)
base = log_loss(y[te], proba_n(Xn[te]))
perm = []
for j in range(3):
    vals = []
    for _ in range(20):
        Xp = Xn[te].copy(); Xp[:, j] = rng.permutation(Xp[:, j])
        vals.append(log_loss(y[te], proba_n(Xp)) - base)
    perm.append(vals)
perm = np.array(perm)
fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
colors = ["#2563eb", "#2563eb", "#9ca3af"]
axes[0].barh(names, counts, color=colors); axes[0].invert_yaxis()
axes[0].set_title("split counts (training data)\nnoise looks MOST important!", fontsize=10)
axes[1].barh(names, perm.mean(1), xerr=perm.std(1), color=colors, capsize=3); axes[1].invert_yaxis()
axes[1].set_title("permutation importance (test data)\nnoise is correctly ~0", fontsize=10)
axes[1].set_xlabel("increase in test log-loss when shuffled")
for ax in axes:
    clean(ax)
fig.suptitle("Two importance measures, one trap: split counts reward features with many unique values",
             weight="bold", x=.02, ha="left")
fig.tight_layout(); fig.savefig(OUT / "importance.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Partial dependence + ICE
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
sample = X[tr][np.random.default_rng(0).choice(len(tr), 40, replace=False)]
for ax, j, grid in ((axes[0], 0, np.arange(1, 73, 1.0)), (axes[1], 1, np.arange(0, 9, 1.0))):
    pd, _ = partial_dependence(proba, X[tr], j, grid)
    _, ice = partial_dependence(proba, sample, j, grid)
    for line in ice:
        ax.plot(grid, line, color="#94a3b8", lw=.6, alpha=.6)
    ax.plot(grid, pd, color="#dc2626", lw=2.5, label="partial dependence (average)")
    ax.set_xlabel(FEATURES[j]); clean(ax)
axes[0].plot([], [], color="#94a3b8", label="ICE: one line per customer")
axes[0].set_ylabel("predicted churn probability"); axes[0].legend(frameon=False, fontsize=8)
fig.suptitle("What happens to the prediction if we change only one feature?", weight="bold", x=.02, ha="left")
fig.tight_layout(); fig.savefig(OUT / "partial_dependence.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Shapley "waterfall" for three customers
customers = {"new & unhappy\n(tenure 3, calls 7)": [3, 7], "average\n(tenure 30, calls 3)": [30, 3],
             "loyal & quiet\n(tenure 60, calls 1)": [60, 1]}
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
for ax, (name, x) in zip(axes, customers.items()):
    b, phi, full = shapley_2(proba, np.array(x, float), X[tr])
    steps = [("base rate", 0, b), ("tenure", b, phi[0]), ("calls", b + phi[0], phi[1]), ("prediction", 0, full)]
    for i, (lab, start, h) in enumerate(steps):
        c = "#64748b" if lab in ("base rate", "prediction") else ("#dc2626" if h > 0 else "#2563eb")
        ax.bar(i, h, bottom=start, color=c, width=.6)
        top = start + h if h > 0 else start
        ax.text(i, max(top, start + h) + .02, f"{h:+.2f}" if lab in ("tenure", "calls") else f"{h:.2f}",
                ha="center", fontsize=8)
    ax.set_xticks(range(4), [s[0] for s in steps], fontsize=8); ax.set_title(name, fontsize=10)
    ax.set_ylim(0, 1.05); clean(ax)
axes[0].set_ylabel("churn probability")
fig.suptitle("Shapley values: base rate + contribution of each feature = this customer's prediction "
             "(red pushes up, blue pushes down)", weight="bold", x=.02, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "shapley_waterfall.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Inside git: commit -> tree -> blobs (git notes for this module)
fig, ax = plt.subplots(figsize=(11, 4.2)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5)
box(ax, 1.6, 4.0, "commit a1b2c3\nauthor, date, message\nparent: 9f8e7d", "#fde68a", w=2.8, h=1.2)
box(ax, 1.6, 1.8, "commit 9f8e7d\n(previous lesson)", "#fef3c7", w=2.8, h=.9)
arrow(ax, (1.6, 3.4), (1.6, 2.25))
box(ax, 5.2, 4.0, "tree (root folder)\nREADME.md\n22-interpretability/", "#bfdbfe", w=2.8, h=1.2)
arrow(ax, (3.0, 4.0), (3.8, 4.0))
box(ax, 5.2, 1.8, "tree 22-interpretability/\nREADME.md, examples/,\ndiagrams/", "#bfdbfe", w=2.8, h=1.2)
arrow(ax, (5.2, 3.4), (5.2, 2.4))
for yy, txt in ((4.2, "blob: README.md\n(file content)"), (2.6, "blob: interpret_demo.py"),
                (1.0, "blob: importance.pdf")):
    box(ax, 9.6, yy, txt, "#bbf7d0", w=2.8, h=.9)
arrow(ax, (6.6, 4.1), (8.2, 4.2)); arrow(ax, (6.6, 1.9), (8.2, 2.6)); arrow(ax, (6.6, 1.6), (8.2, 1.0))
ax.text(.2, .2, "every box is an object named by its SHA hash: `git cat-file -p <hash>` opens any of them",
        fontsize=9, color="#475569")
ax.set_title("Opening git's black box: commits point to trees, trees point to blobs", weight="bold", loc="left")
fig.savefig(OUT / "git_objects.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
