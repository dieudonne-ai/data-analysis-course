"""Generate the PDF diagram for module 04."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
steps = ["Raw data", "Remove\nduplicates", "Fix text\n(strip, title)", "Handle\nmissing values",
         "Drop invalid\nvalues", "Fix dtypes", "Clean data"]

fig, ax = plt.subplots(figsize=(13, 3.2))
ax.set_xlim(0, 13); ax.set_ylim(0, 3.2); ax.axis("off")
ax.set_title("Data cleaning pipeline", fontsize=15, weight="bold")
for i, s in enumerate(steps):
    x = 0.2 + i * 1.85
    color = "#fecaca" if i == 0 else "#bbf7d0" if i == len(steps) - 1 else "#dbeafe"
    ax.add_patch(FancyBboxPatch((x, 1.0), 1.5, 1.2, boxstyle="round,pad=0.03",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + 0.75, 1.6, s, ha="center", va="center", fontsize=9)
    if i < len(steps) - 1:
        ax.annotate("", xy=(x + 1.85, 1.6), xytext=(x + 1.55, 1.6),
                    arrowprops=dict(arrowstyle="->"))
ax.text(6.5, 0.4, "Always inspect (isna().sum(), duplicated().sum()) before and after.",
        ha="center", style="italic")
fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")
