"""Generate PDF diagrams for module 05 (EDA)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "sales_eda.csv")

# 1. EDA loop
fig, ax = plt.subplots(figsize=(9, 4)); ax.set_xlim(0, 9); ax.set_ylim(0, 4); ax.axis("off")
ax.set_title("The EDA loop", fontsize=15, weight="bold")
steps = [(0.3, "1. Ask a\nquestion"), (3.3, "2. Summarize\n& visualize"), (6.3, "3. Find patterns\n& anomalies")]
for x, s in steps:
    ax.add_patch(FancyBboxPatch((x, 1.6), 2.4, 1.2, boxstyle="round,pad=0.05", fc="#dbeafe", ec="#1e3a8a", lw=1.5))
    ax.text(x + 1.2, 2.2, s, ha="center", va="center")
for x in (2.8, 5.8):
    ax.annotate("", xy=(x + 0.45, 2.2), xytext=(x, 2.2), arrowprops=dict(arrowstyle="->"))
ax.annotate("", xy=(1.5, 1.5), xytext=(7.5, 1.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.35", color="#b91c1c"))
ax.text(4.5, 0.4, "refine the question and repeat", ha="center", color="#b91c1c", style="italic")
fig.savefig(OUT / "eda_loop.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Boxplot anatomy + real data
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.5))
a.boxplot(df["revenue"], widths=0.5)
a.set_title("Revenue boxplot"); a.set_ylabel("Revenue")
for y, t in [(df.revenue.median(), "median"), (df.revenue.quantile(.75), "Q3"),
             (df.revenue.quantile(.25), "Q1")]:
    a.annotate(t, (1.3, y), fontsize=9)
b.hist(df["revenue"], bins=15, color="#60a5fa", ec="white")
b.axvline(df.revenue.mean(), color="red", ls="--", label="mean")
b.axvline(df.revenue.median(), color="green", ls="-", label="median")
b.set_title("Revenue histogram (right-skewed: mean > median)"); b.set_xlabel("Revenue"); b.legend()
fig.suptitle("Reading distributions", fontsize=14, weight="bold")
fig.savefig(OUT / "distributions.pdf", bbox_inches="tight"); plt.close(fig)
