"""Generate git_branches.pdf: branch and merge."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 3.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
ax.set_title("Branch and merge", fontsize=15, weight="bold")
main = [(1, 3), (3, 3), (5, 3), (8, 3)]
feat = [(3, 1.2), (5, 1.2), (6.5, 1.2)]
ax.plot([x for x, _ in main], [y for _, y in main], "-", color="#1e3a8a", lw=2, zorder=1)
ax.plot([1, 3], [3, 1.2], "-", color="#166534", lw=2, zorder=1)
ax.plot([x for x, _ in feat], [y for _, y in feat], "-", color="#166534", lw=2, zorder=1)
ax.plot([6.5, 8], [1.2, 3], "--", color="#166534", lw=2, zorder=1)
ax.scatter(*zip(*main), s=500, c="#dbeafe", ec="#1e3a8a", zorder=2)
ax.scatter(*zip(*feat), s=500, c="#bbf7d0", ec="#166534", zorder=2)
ax.text(0.2, 3, "main", weight="bold", va="center")
ax.text(0.2, 1.2, "feature", weight="bold", va="center", color="#166534")
ax.text(8, 3.5, "merge commit", ha="center", fontsize=9)
ax.text(2, 2.3, "git switch -c feature", fontsize=9, rotation=0)
ax.text(8.4, 2.0, "git switch main\ngit merge feature", fontsize=9)
fig.savefig(Path(__file__).resolve().parent / "git_branches.pdf", bbox_inches="tight")
