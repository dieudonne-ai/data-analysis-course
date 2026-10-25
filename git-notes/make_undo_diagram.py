"""Generate git_undo.pdf: which command undoes what."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent
fig, ax = canvas(12, 5, "How to undo things in Git", (12, 5))
areas = ["Working\ndirectory", "Staging\narea", "Local\nrepository", "Remote\n(GitHub)"]
for i, a in enumerate(areas):
    box(ax, 0.3 + i * 3, 3.2, 2.4, 1.0, a, "#dbeafe")
for i in range(3):
    arrow(ax, 2.75 + i * 3, 3.9, 3.25 + i * 3, 3.9)
    ax.text(3.0 + i * 3, 4.35, ["add", "commit", "push"][i], ha="center", fontsize=10, weight="bold")
rows = [(1.5, "git restore <file>", "discard edits in the\nworking directory"),
        (4.5, "git restore --staged <file>", "unstage,\nkeep the edits"),
        (7.5, "git revert <commit>", "new commit that cancels an\nold one (safe after push)")]
for x, c, d in rows:
    ax.text(x, 2.5, c, ha="center", fontsize=9, family="monospace", weight="bold")
    ax.text(x, 1.7, d, ha="center", fontsize=9)
ax.text(6, 0.9, "Avoid `git reset --hard` and force-push: they destroy history others may rely on.",
        ha="center", color="#b91c1c", style="italic")
fig.savefig(OUT / "git_undo.pdf", bbox_inches="tight")
