"""Generate PDF diagrams for module 18 (feature engineering)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(11)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def boxes(ax, items, y=1.0, w=1.8, gap=2.17, colors=None):
    for i, t in enumerate(items):
        x = .15 + i * gap
        ax.add_patch(FancyBboxPatch((x, y), w, 1.1, boxstyle="round,pad=.04",
                                    fc=(colors or ["#dbeafe"] * len(items))[i], ec="#334155"))
        ax.text(x + w / 2, y + .55, t, ha="center", va="center", fontsize=9.5)
        if i < len(items) - 1:
            ax.annotate("", (x + gap - .05, y + .55), (x + w + .05, y + .55), arrowprops=dict(arrowstyle="->"))


# 1. Pipeline
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
boxes(ax, ["Raw data", "Clean &\nimpute", "Transform\n(log, dates)", "Encode\ncategories", "Scale", "Model-ready\nfeatures"],
      gap=1.8, w=1.5, colors=["#fee2e2"] + ["#dbeafe"] * 4 + ["#dcfce7"])
ax.set_title("The feature engineering pipeline", weight="bold")
fig.savefig(OUT / "pipeline.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Encoding table
fig, ax = plt.subplots(figsize=(9, 3.2)); ax.axis("off")
tab = ax.table(cellText=[["pro", "2", "0", "0", "1"], ["free", "0", "1", "0", "0"], ["basic", "1", "0", "1", "0"]],
               colLabels=["plan", "ordinal", "is_free", "is_basic", "is_pro"], loc="center", cellLoc="center")
tab.scale(1, 1.8); tab.auto_set_font_size(False); tab.set_fontsize(11)
for (r, c), cell in tab.get_celld().items():
    if r == 0: cell.set_facecolor("#1e3a8a"); cell.set_text_props(color="white", weight="bold")
ax.set_title("Ordinal (ordered) vs one-hot (unordered) encoding", weight="bold")
fig.savefig(OUT / "encoding.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Log transform
x = rng.lognormal(10, .8, 1000)
fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.4))
a.hist(x, bins=40, color="#93c5fd"); a.set_title("income: skew = 2.2", weight="bold")
b.hist(np.log1p(x), bins=40, color="#86efac"); b.set_title("log(income): skew ≈ 0", weight="bold")
for ax_ in (a, b): clean(ax_)
fig.suptitle("Log transform tames long right tails", weight="bold", x=.02, ha="left")
fig.savefig(OUT / "log_transform.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Leakage
fig, ax = plt.subplots(figsize=(10, 3.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.4)
for y, ok, title in [(2.0, True, "Correct"), (0.4, False, "Leakage")]:
    ax.text(0, y + .55, title, weight="bold", color="#059669" if ok else "#dc2626", fontsize=11)
    ax.add_patch(FancyBboxPatch((1.4, y), 3, 1.1, boxstyle="round,pad=.04", fc="#dbeafe", ec="#334155"))
    ax.text(2.9, y + .55, "Split train/test first" if ok else "Scale ALL data first", ha="center", va="center")
    ax.add_patch(FancyBboxPatch((5.2, y), 4.2, 1.1, boxstyle="round,pad=.04", fc="#dcfce7" if ok else "#fee2e2", ec="#334155"))
    ax.text(7.3, y + .55, "fit on train, apply to test" if ok else "split afterwards:\ntest info leaked in", ha="center", va="center")
    ax.annotate("", (5.15, y + .55), (4.5, y + .55), arrowprops=dict(arrowstyle="->"))
ax.set_title("Fit transformations on the training set only", weight="bold", loc="left")
fig.savefig(OUT / "leakage.pdf", bbox_inches="tight"); plt.close(fig)
