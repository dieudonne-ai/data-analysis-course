"""Generate the PDF diagram for module 10."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from diagram_utils import arrow, box, canvas

OUT = Path(__file__).resolve().parent

fig, ax = canvas(12, 5, "Anatomy of an analysis project", (12, 5))
steps = [("Question", "#fde68a"), ("Load", "#dbeafe"), ("Clean", "#dbeafe"), ("Explore", "#dbeafe"),
         ("Test /\nModel", "#dbeafe"), ("Report", "#bbf7d0")]
mods = ["module 01", "03", "04", "05-06", "07-09", "this module"]
for i, ((s, c), m) in enumerate(zip(steps, mods)):
    x = 0.2 + i * 1.95
    box(ax, x, 2.2, 1.5, 1.2, s, c)
    ax.text(x + 0.75, 1.8, m, ha="center", fontsize=9, style="italic")
    if i < 5:
        arrow(ax, x + 1.55, 2.8, x + 1.95, 2.8)
ax.annotate("", xy=(1.0, 3.6), xytext=(10.7, 3.6), arrowprops=dict(arrowstyle="->", ls="--", color="gray"))
ax.text(5.85, 3.8, "iterate: every step can send you back", ha="center", color="gray")
ax.text(6, 0.7, "Commit after each step: git log tells the story of your analysis.", ha="center", style="italic")
fig.savefig(OUT / "project_flow.pdf", bbox_inches="tight")
