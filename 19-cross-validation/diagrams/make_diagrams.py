"""Generate PDF diagrams for module 19 (cross-validation & tuning)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(19)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. K-fold
fig, ax = plt.subplots(figsize=(9, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5.2)
for i in range(5):
    y = 4.2 - i * .85
    ax.text(0, y + .2, f"Round {i+1}", va="center", fontsize=10)
    for j in range(5):
        val = j == i
        ax.add_patch(Rectangle((1.5 + j * 1.5, y), 1.4, .6, fc="#fb923c" if val else "#93c5fd", ec="#334155"))
        ax.text(2.2 + j * 1.5, y + .3, "validate" if val else "train", ha="center", va="center", fontsize=9)
ax.text(5, .05, "score = average of the 5 validation scores", ha="center", style="italic")
ax.set_title("5-fold cross-validation: every row is validated exactly once", weight="bold", loc="left")
fig.savefig(OUT / "kfold.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Under/over-fitting curve
d = np.arange(1, 16)
train = 0.55 * np.exp(-d / 3) + .28 - 0.002 * d
val = 0.55 * np.exp(-d / 2.2) + .30 + 0.0035 * (d - 4).clip(0) ** 1.6
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(d, train, "o-", color="#2563eb", label="training error")
ax.plot(d, val, "o-", color="#dc2626", label="validation error (CV)")
b = d[val.argmin()]
ax.axvline(b, color="#059669", ls="--"); ax.text(b + .3, val.max() * .95, f"sweet spot\n(degree {b})", color="#059669")
ax.text(1.2, .4, "underfit", color="#64748b"); ax.text(11.5, .4, "overfit", color="#64748b")
ax.set_xlabel("model complexity (polynomial degree)"); ax.set_ylabel("error"); clean(ax); ax.legend(frameon=False)
ax.set_title("Pick the complexity where validation error is lowest", weight="bold", loc="left")
fig.savefig(OUT / "complexity.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Grid search heatmap
degs, lams = [3, 5, 9, 15], [0, .01, .1, 1, 10]
Z = np.array([[.31, .31, .31, .33, .45], [.31, .31, .31, .33, .45], [.32, .32, .31, .33, .45], [.33, .32, .32, .33, .46]])
fig, ax = plt.subplots(figsize=(7, 3.6))
im = ax.imshow(Z, cmap="YlGn_r", aspect="auto")
ax.set_xticks(range(5), [str(l) for l in lams]); ax.set_yticks(range(4), [str(x) for x in degs])
ax.set_xlabel("lambda (regularisation)"); ax.set_ylabel("degree")
for i in range(4):
    for j in range(5):
        ax.text(j, i, f"{Z[i, j]:.2f}", ha="center", va="center", fontsize=9)
fig.colorbar(im, label="CV RMSE (lower = better)")
ax.set_title("Grid search: try every combination, keep the best", weight="bold", loc="left")
fig.savefig(OUT / "grid_search.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Three-way split
fig, ax = plt.subplots(figsize=(10, 3)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3)
parts = [(0, 6, "Train + CV\n(fit and tune here)", "#bfdbfe"), (6, 4, "Test set\n(touch ONCE, at the end)", "#fecaca")]
for x0, w, t, c in parts:
    ax.add_patch(FancyBboxPatch((x0 + .05, 1), w - .1, 1.2, boxstyle="round,pad=.03", fc=c, ec="#334155"))
    ax.text(x0 + w / 2, 1.6, t, ha="center", va="center", fontsize=10)
ax.text(3, .5, "inside: k folds rotate as validation", ha="center", style="italic")
ax.set_title("Keep a final test set that tuning never sees", weight="bold", loc="left")
fig.savefig(OUT / "split.pdf", bbox_inches="tight"); plt.close(fig)
