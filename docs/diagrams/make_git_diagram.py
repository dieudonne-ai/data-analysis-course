"""Generate docs/diagrams/git-workflow.pdf (the four areas of Git)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

out = Path(__file__).with_name("git-workflow.pdf")
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.set_xlim(0, 11); ax.set_ylim(0, 4.5); ax.axis("off")

boxes = [("Working\ndirectory", "#dbeafe"), ("Staging area\n(index)", "#fef9c3"),
         ("Local\nrepository", "#dcfce7"), ("Remote\n(GitHub)", "#fce7f3")]
for i, (label, color) in enumerate(boxes):
    x = 0.4 + i * 2.7
    ax.add_patch(FancyBboxPatch((x, 1.9), 2.0, 1.3, boxstyle="round,pad=0.05",
                                fc=color, ec="#334155", lw=1.5))
    ax.text(x + 1.0, 2.55, label, ha="center", va="center", fontsize=12, weight="bold")

arrows = [("git add", 0), ("git commit", 1), ("git push", 2)]
for cmd, i in arrows:
    x0 = 2.45 + i * 2.7
    ax.annotate("", xy=(x0 + 0.6, 2.75), xytext=(x0, 2.75),
                arrowprops=dict(arrowstyle="->", lw=2, color="#0f172a"))
    ax.text(x0 + 0.3, 2.95, cmd, ha="center", fontsize=10, family="monospace")
for cmd, i in [("git pull / fetch", 2)]:
    x0 = 2.45 + i * 2.7
    ax.annotate("", xy=(x0, 2.1), xytext=(x0 + 0.6, 2.1),
                arrowprops=dict(arrowstyle="->", lw=2, color="#b91c1c"))
    ax.text(x0 + 0.3, 1.7, cmd, ha="center", fontsize=9, family="monospace", color="#b91c1c")

ax.text(5.5, 4.0, "The four areas of Git", ha="center", fontsize=15, weight="bold")
ax.text(5.5, 0.9, "git status  shows where your changes are      "
        "git log  shows saved history      git diff  shows what changed",
        ha="center", fontsize=9, family="monospace")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
