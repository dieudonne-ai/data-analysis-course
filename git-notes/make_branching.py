"""Generate git_branching.pdf (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
ax.set_title("Branch and merge", fontsize=15, weight="bold")
main = [(1, 3), (3, 3), (5, 3), (8, 3)]
feat = [(3, 1), (4.5, 1), (6, 1)]
ax.plot([p[0] for p in main], [p[1] for p in main], "-", color="#1e3a8a", lw=2, zorder=1)
ax.plot([3] + [p[0] for p in feat], [3] + [p[1] for p in feat], "-", color="#b45309", lw=2, zorder=1)
ax.plot([6, 8], [1, 3], "-", color="#b45309", lw=2, zorder=1)
ax.scatter(*zip(*main), s=500, c="#dbeafe", ec="#1e3a8a", zorder=2)
ax.scatter(*zip(*feat), s=500, c="#fde68a", ec="#b45309", zorder=2)
for i, p in enumerate(main): ax.text(*p, f"M{i+1}", ha="center", va="center")
for i, p in enumerate(feat): ax.text(*p, f"F{i+1}", ha="center", va="center")
ax.text(0.1, 3, "main", color="#1e3a8a", weight="bold", va="center")
ax.text(0.1, 1, "feature", color="#b45309", weight="bold", va="center")
ax.annotate("git switch -c feature", xy=(3.2, 1.2), xytext=(0.5, 2.0), arrowprops=dict(arrowstyle="->"))
ax.annotate("git merge feature", xy=(8, 2.75), xytext=(8.0, 1.2), ha="center", arrowprops=dict(arrowstyle="->"))
fig.savefig(OUT / "git_branching.pdf", bbox_inches="tight")
