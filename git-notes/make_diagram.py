"""Generate git_workflow.pdf."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(11, 4))
ax.set_xlim(0, 11); ax.set_ylim(0, 4); ax.axis("off")
ax.set_title("Git workflow: the three areas and the remote", fontsize=15, weight="bold")
names = ["Working\ndirectory", "Staging\narea", "Local\nrepository", "Remote\n(GitHub)"]
colors = ["#fde68a", "#bbf7d0", "#dbeafe", "#fbcfe8"]
for i, (n, c) in enumerate(zip(names, colors)):
    x = 0.3 + i * 2.75
    ax.add_patch(FancyBboxPatch((x, 1.4), 2.0, 1.4, boxstyle="round,pad=0.03", fc=c, ec="black"))
    ax.text(x + 1.0, 2.1, n, ha="center", va="center", fontsize=12)
for i, cmd in enumerate(["git add", "git commit", "git push"]):
    x = 2.35 + i * 2.75
    ax.annotate("", xy=(x + 0.65, 2.1), xytext=(x, 2.1), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(x + 0.33, 2.3, cmd, ha="center", fontsize=9)
ax.annotate("", xy=(8.5, 1.1), xytext=(8.5 + 0.0, 1.1))
ax.text(5.5, 0.6, "git pull / git fetch bring remote changes back down", ha="center", style="italic")
fig.savefig(Path(__file__).resolve().parent / "git_workflow.pdf", bbox_inches="tight")
