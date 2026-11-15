"""Generate PDF diagrams for module 20 (decision trees & random forests)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent
DATA = Path(__file__).resolve().parents[2] / "data" / "churn.csv"
raw = np.genfromtxt(DATA, delimiter=",", names=True)


def box(ax, x, y, text, fc, w=2.6, h=.9):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y, text, ha="center", va="center", fontsize=9)


def line(ax, a, b, label):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#334155"))
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + .1, label, ha="center", fontsize=8, color="#475569")


# 1. The tree itself (numbers from examples/tree_demo.py, depth 2)
fig, ax = plt.subplots(figsize=(10, 4.6)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6)
box(ax, 6, 5.2, "tenure <= 22 ?\n450 customers, 36% churn", "#e2e8f0", w=3.4)
box(ax, 3, 3.3, "support_calls <= 3 ?", "#e2e8f0")
box(ax, 9, 3.3, "support_calls <= 2 ?", "#e2e8f0")
leaves = [(1.5, "61% churn\nn=135", "#fdba74"), (4.5, "95% churn\nn=21", "#f87171"),
          (7.5, "13% churn\nn=193", "#86efac"), (10.5, "35% churn\nn=101", "#fde68a")]
for x, t, c in leaves:
    box(ax, x, 1.2, t, c, w=2.2)
line(ax, (6, 4.7), (3, 3.8), "yes"); line(ax, (6, 4.7), (9, 3.8), "no")
for p, xs in ((3, (1.5, 4.5)), (9, (7.5, 10.5))):
    line(ax, (p, 2.85), (xs[0], 1.7), "yes"); line(ax, (p, 2.85), (xs[1], 1.7), "no")
ax.set_title("A decision tree is a list of yes/no questions (depth 2, churn data)", weight="bold", loc="left")
fig.savefig(OUT / "tree_structure.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Splits as rectangles in feature space
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.add_patch(Rectangle((0, -.5), 22.5, 4, fc="#fdba74", alpha=.35))
ax.add_patch(Rectangle((0, 3.5), 22.5, 10, fc="#f87171", alpha=.35))
ax.add_patch(Rectangle((22.5, -.5), 60, 3, fc="#86efac", alpha=.35))
ax.add_patch(Rectangle((22.5, 2.5), 60, 10, fc="#fde68a", alpha=.35))
jit = np.random.default_rng(0).uniform(-.25, .25, len(raw))
for c, col, lab in ((0, "#2563eb", "stayed"), (1, "#dc2626", "churned")):
    m = raw["churn"] == c
    ax.scatter(raw["tenure"][m], raw["support_calls"][m] + jit[m], s=8, color=col, alpha=.6, label=lab)
ax.axvline(22.5, color="#0f172a", lw=2)
ax.set_xlim(0, raw["tenure"].max() + 2); ax.set_ylim(-.5, raw["support_calls"].max() + .5)
ax.set_xlabel("tenure (months)"); ax.set_ylabel("support calls")
ax.legend(frameon=False, loc="upper right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title("Each split cuts the space into boxes; each box predicts one rate", weight="bold", loc="left")
fig.savefig(OUT / "feature_space.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Depth vs accuracy (numbers from the demo)
d = [1, 2, 3, 5, 8, 12]
train = [.744, .744, .753, .784, .847, .871]
test = [.680, .680, .700, .760, .700, .673]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(d, train, "o-", color="#2563eb", label="train accuracy")
ax.plot(d, test, "o-", color="#dc2626", label="test accuracy")
ax.axvline(5, color="#059669", ls="--"); ax.text(5.2, .85, "best depth = 5", color="#059669")
ax.set_xlabel("max depth"); ax.set_ylabel("accuracy"); ax.legend(frameon=False, loc="lower right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title("Deeper trees memorise the training data (over-fitting)", weight="bold", loc="left")
fig.savefig(OUT / "depth_overfit.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Random forest pipeline
fig, ax = plt.subplots(figsize=(10, 4)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5)
box(ax, 1.3, 2.5, "training\ndata", "#bfdbfe", w=1.8, h=1.2)
for i, y in enumerate((4.2, 2.5, 0.8)):
    lab = "..." if i == 1 else ""
    box(ax, 4.4, y, f"bootstrap\nsample {['1', '2', 'B'][i]}", "#e0e7ff", w=2, h=.9)
    box(ax, 7.4, y, f"tree {['1', '2', 'B'][i]}\n(random features)", "#bbf7d0", w=2.2, h=.9)
    ax.annotate("", xy=(3.4, y), xytext=(2.2, 2.5), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(6.3, y), xytext=(5.4, y), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(9.6, 2.5), xytext=(8.5, y), arrowprops=dict(arrowstyle="->"))
box(ax, 10.7, 2.5, "average the\nvotes", "#fde68a", w=2, h=1.2)
ax.text(6, .0, "many noisy trees, averaged = one stable model (test acc 0.67 -> 0.71)", ha="center", style="italic")
ax.set_title("Random forest: bagging + random feature choice", weight="bold", loc="left")
fig.savefig(OUT / "random_forest.pdf", bbox_inches="tight"); plt.close(fig)
