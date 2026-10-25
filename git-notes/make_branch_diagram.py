"""Generate git_branching.pdf: branch, commit, merge."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import diagram_utils  # noqa: F401

OUT = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(11, 4))
ax.set_xlim(0, 11); ax.set_ylim(0, 4); ax.axis("off")
ax.set_title("Branching and merging", fontsize=15, weight="bold")


def commit(x, y, label, color):
    ax.scatter(x, y, s=500, color=color, ec="black", zorder=3)
    ax.text(x, y - 0.5, label, ha="center", fontsize=9)


main = [(1, "A"), (3, "B"), (5, "C"), (9, "M")]
feat = [(4, "D"), (6.5, "E")]
ax.plot([1, 9], [3, 3], color="#1e3a8a", lw=2)
ax.plot([3, 4, 6.5, 9], [3, 1.4, 1.4, 3], color="#16a34a", lw=2)
for x, l in main:
    commit(x, 3, l, "#dbeafe" if l != "M" else "#fde68a")
for x, l in feat:
    commit(x, 1.4, l, "#bbf7d0")
ax.text(0.2, 3.0, "main", weight="bold", color="#1e3a8a", va="center")
ax.text(4.9, 0.55, "feature/cleaning", weight="bold", color="#16a34a")
ax.text(3.0, 3.65, "git switch -c feature/cleaning", fontsize=9, style="italic")
ax.text(8.2, 3.65, "git merge feature/cleaning\n(merge commit M)", fontsize=9, style="italic", ha="center")
fig.savefig(OUT / "git_branching.pdf", bbox_inches="tight")
