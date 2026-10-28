"""Generate the cleaning pipeline diagram for module 04."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
steps = [("Raw data", "#fecaca"), ("Remove\nduplicates", "#dbeafe"),
         ("Fix text\n(strip, case)", "#dbeafe"), ("Fix types\n(dates, numbers)", "#dbeafe"),
         ("Handle invalid\n& outliers", "#dbeafe"), ("Handle\nmissing values", "#dbeafe"),
         ("Clean data", "#bbf7d0")]

fig, ax = plt.subplots(figsize=(13, 3))
ax.set_xlim(0, 13); ax.set_ylim(0, 3); ax.axis("off")
ax.set_title("The data cleaning pipeline", fontsize=15, weight="bold")
for i, (t, c) in enumerate(steps):
    x = 0.2 + i * 1.85
    ax.add_patch(FancyBboxPatch((x, 0.9), 1.5, 1.0, boxstyle="round,pad=0.03",
                                fc=c, ec="#1e3a8a", lw=1.5))
    ax.text(x + 0.75, 1.4, t, ha="center", va="center", fontsize=9)
    if i < len(steps) - 1:
        ax.annotate("", xy=(x + 1.85, 1.4), xytext=(x + 1.55, 1.4),
                    arrowprops=dict(arrowstyle="->", lw=1.5))
ax.text(6.5, 0.35, "Always re-check df.info() and df.isna().sum() after each step",
        ha="center", style="italic")
fig.savefig(OUT / "cleaning_pipeline.pdf", bbox_inches="tight")
