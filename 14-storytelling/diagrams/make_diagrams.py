"""Generate PDF diagrams for module 14 (data storytelling)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, fc="#dbeafe", fs=10, color="k"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.04", fc=fc, ec="#334155"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color)


# 1. Story structure: context -> insight -> action
fig, ax = plt.subplots(figsize=(10, 3.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.2)
for i, (t, d, c) in enumerate([("1. Context", "who cares?\nwhat question?", "#dbeafe"),
                               ("2. Insight", "the ONE number\nor trend", "#fef3c7"),
                               ("3. Action", "what should we\ndo next?", "#dcfce7")]):
    x = .3 + i * 3.3
    box(ax, x, 1.2, 2.8, 1, t, fc=c, fs=13); ax.text(x + 1.4, .6, d, ha="center", fontsize=10, color="#475569")
    if i < 2: ax.annotate("", (x + 3.25, 1.7), (x + 2.85, 1.7), arrowprops=dict(arrowstyle="->", lw=2))
ax.set_title("A data story in three steps", weight="bold")
fig.savefig(OUT / "story_structure.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Before / after: declutter a chart
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]; vals = [10, 11, 12, 11, 18, 19]
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.8))
a.bar(months, vals, color=["r", "g", "b", "y", "m", "c"], edgecolor="k"); a.grid(True)
a.set_title("BEFORE: rainbow, grid, vague title")
b.bar(months, vals, color=["#cbd5e1"] * 4 + ["#1e3a8a"] * 2)
for s in ("top", "right", "left"): b.spines[s].set_visible(False)
b.set_yticks([]); b.bar_label(b.containers[0])
b.set_title("AFTER: Sales jumped 60% in May", loc="left", weight="bold")
fig.savefig(OUT / "declutter.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Report workflow
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
for i, t in enumerate(["Data", "Analysis\n(script)", "Charts\n(PNG/PDF)", "Report\n(Markdown)", "Share\n(git push)"]):
    x = .2 + i * 2.1; box(ax, x, 1, 1.7, 1, t, fc="#dbeafe" if i < 4 else "#dcfce7")
    if i < 4: ax.annotate("", (x + 2.05, 1.5), (x + 1.75, 1.5), arrowprops=dict(arrowstyle="->"))
ax.text(5.5, .4, "One script regenerates everything: reproducible report", ha="center", color="#475569")
fig.savefig(OUT / "report_workflow.pdf", bbox_inches="tight"); plt.close(fig)
