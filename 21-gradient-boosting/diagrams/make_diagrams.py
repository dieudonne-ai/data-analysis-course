"""Generate PDF diagrams for module 21 (gradient boosting)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from boosting_demo import X, boost, log_loss, predict, sigmoid, te, tr, y  # noqa: E402


def box(ax, x, y_, text, fc, w=2.2, h=1.0):
    ax.add_patch(FancyBboxPatch((x - w / 2, y_ - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y_, text, ha="center", va="center", fontsize=9)


def arrow(ax, a, b, label=""):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#334155"))
    if label:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + .25, label, ha="center", fontsize=8, color="#475569")


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. The boosting idea: a chain of small trees, each fixing the previous errors
fig, ax = plt.subplots(figsize=(11, 3.8)); ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 4.5)
box(ax, 1.2, 3.2, "start\nF0 = log-odds\nof base rate", "#bfdbfe", w=2, h=1.2)
for i, x in enumerate((4.0, 7.0, 10.0)):
    name = ["tree 1", "tree 2", "tree M"][i]
    box(ax, x, 3.2, f"{name}\nfits residuals\ny - p", "#bbf7d0", w=2.1, h=1.2)
    box(ax, x, 1.0, f"F += lr x {name}", "#fde68a", w=2.1, h=.7)
    arrow(ax, (x, 2.6), (x, 1.35))
arrow(ax, (2.2, 3.2), (2.95, 3.2), "errors")
arrow(ax, (5.05, 3.2), (5.95, 3.2), "new errors")
arrow(ax, (8.05, 3.2), (8.95, 3.2), "...")
box(ax, 12.3, 1.0, "p = sigmoid(F)", "#fecaca", w=1.4, h=.7)
arrow(ax, (11.05, 1.0), (11.6, 1.0))
ax.set_title("Boosting: trees are built one after another, each one corrects the previous ones",
             weight="bold", loc="left")
fig.savefig(OUT / "boosting_idea.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Residuals shrink as trees are added
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
for ax, m in zip(axes, (0, 5, 50)):
    if m == 0:
        p = np.full(len(tr), y[tr].mean())
    else:
        _, _, h = boost(X[tr], y[tr], m, lr=0.3, max_depth=2, X_eval=X[tr])
        p = h[-1][1]
    r = y[tr] - p
    ax.scatter(X[tr, 0], r, s=8, c=np.where(y[tr] == 1, "#dc2626", "#2563eb"), alpha=.6)
    ax.axhline(0, color="#0f172a", lw=1)
    ax.set_title(f"after {m} trees: mean |residual| = {np.abs(r).mean():.2f}", fontsize=10)
    ax.set_xlabel("tenure (months)"); clean(ax)
axes[0].set_ylabel("residual  y - p")
fig.suptitle("Residuals = what the model still gets wrong (red = churned, blue = stayed)",
             weight="bold", x=.02, ha="left")
fig.tight_layout(); fig.savefig(OUT / "residuals.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Learning rate vs number of trees (train vs test log-loss)
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
for ax, lr in zip(axes, (1.0, 0.3, 0.1)):
    _, trees, h = boost(X[tr], y[tr], 200, lr=lr, max_depth=2, X_eval=X[te])
    test = [log_loss(y[te], p) for _, p in h]
    ax.plot(range(1, 201), [l for l, _ in h], color="#2563eb", label="train")
    ax.plot(range(1, 201), test, color="#dc2626", label="test")
    b = int(np.argmin(test)) + 1
    ax.axvline(b, color="#059669", ls="--"); ax.text(b + 3, .62, f"best ~{b}", color="#059669", fontsize=8)
    ax.set_title(f"learning rate {lr}", fontsize=10); ax.set_xlabel("number of trees"); clean(ax)
axes[0].set_ylabel("log-loss"); axes[0].legend(frameon=False)
fig.suptitle("Small learning rate = slower but safer; too many trees over-fit", weight="bold", x=.02, ha="left")
fig.tight_layout(); fig.savefig(OUT / "learning_rate.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Bagging (random forest) vs boosting
fig, ax = plt.subplots(figsize=(11, 4.4)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5.5)
ax.text(.2, 5.1, "Random forest (bagging): parallel", weight="bold", color="#1e40af")
for x in (1.2, 3.2, 5.2):
    box(ax, x, 4.0, "deep tree\n(own sample)", "#bfdbfe", w=1.6, h=.9)
    arrow(ax, (x, 3.5), (3.2, 2.95))
box(ax, 3.2, 2.6, "average", "#e0e7ff", w=1.6, h=.6)
ax.text(.2, 1.5, "goal: reduce VARIANCE\n(many over-fit trees,\nerrors cancel out)", fontsize=9)
ax.text(6.6, 5.1, "Gradient boosting: sequential", weight="bold", color="#065f46")
for i, x in enumerate((7.4, 9.2, 11.0)):
    box(ax, x, 4.0, "small tree\n(depth 1-3)", "#bbf7d0", w=1.5, h=.9)
    if i:
        arrow(ax, (x - 1.8 + .75, 4.0), (x - .75, 4.0))
    arrow(ax, (x, 3.5), (9.2, 2.95))
box(ax, 9.2, 2.6, "weighted sum", "#d1fae5", w=1.8, h=.6)
ax.text(6.8, 1.5, "goal: reduce BIAS\n(weak trees, each fixes\nthe last one's errors)", fontsize=9)
ax.plot([6.3, 6.3], [.5, 5.3], color="#cbd5e1")
ax.set_title("Two ways to combine trees", weight="bold", loc="left")
fig.savefig(OUT / "bagging_vs_boosting.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
