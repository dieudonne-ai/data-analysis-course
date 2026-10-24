"""Generate git_collaboration.pdf (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 4.5); ax.axis("off")
ax.set_title("Working with a remote", fontsize=15, weight="bold")


def box(x, y, w, h, t, c):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=c, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center")


box(0.2, 1.5, 2.4, 1.4, "Your computer\n(local repo)", "#dbeafe")
box(3.8, 1.5, 2.4, 1.4, "GitHub\n(origin)", "#fde68a")
box(7.4, 1.5, 2.4, 1.4, "Teammate's\ncomputer", "#dbeafe")
for (a, b, t, dy) in [((2.6, 2.6), (3.8, 2.6), "git push", 0.15), ((3.8, 1.8), (2.6, 1.8), "git pull / fetch", -0.3),
                      ((7.4, 2.6), (6.2, 2.6), "git push", 0.15), ((6.2, 1.8), (7.4, 1.8), "git pull", -0.3)]:
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", lw=1.6))
    ax.text((a[0] + b[0]) / 2, a[1] + dy, t, ha="center", fontsize=9)
ax.text(5, 0.6, "git clone: create the first local copy from origin", ha="center", style="italic")
fig.savefig(OUT / "git_collaboration.pdf", bbox_inches="tight")
