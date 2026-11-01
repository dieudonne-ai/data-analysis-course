"""Generate PDF diagrams for module 06 (visualization)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "sales_eda.csv")

# 1. Chart chooser (decision diagram)
fig, ax = plt.subplots(figsize=(10, 5)); ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
ax.set_title("Which chart should I use?", fontsize=15, weight="bold")
def box(x, y, w, t, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, 0.8, boxstyle="round,pad=0.05", fc=fc, ec="#1e3a8a"))
    ax.text(x + w / 2, y + 0.4, t, ha="center", va="center", fontsize=10)
box(3.5, 3.9, 3, "What is your goal?", "#fde68a")
goals = [(0.2, "Compare\ncategories", "Bar chart"), (2.7, "Show\ndistribution", "Histogram / boxplot"),
         (5.2, "Show\nrelationship", "Scatter plot"), (7.7, "Show trend\nover time", "Line chart")]
for x, g, c in goals:
    box(x, 2.2, 2.1, g, "#dbeafe"); box(x, 0.6, 2.1, c, "#bbf7d0")
    ax.annotate("", xy=(x + 1.05, 3.0), xytext=(5, 3.85), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(x + 1.05, 1.45), xytext=(x + 1.05, 2.15), arrowprops=dict(arrowstyle="->"))
fig.savefig(OUT / "chart_chooser.pdf", bbox_inches="tight"); plt.close(fig)

# 2. The four chart types on real data
fig, axs = plt.subplots(2, 2, figsize=(11, 8))
df.groupby("product")["revenue"].sum().sort_values(ascending=False).plot.bar(ax=axs[0, 0], color="#2563eb")
axs[0, 0].set_title("Bar: compare categories"); axs[0, 0].set_ylabel("Revenue")
axs[0, 1].hist(df["revenue"], bins=15, color="#60a5fa", ec="white")
axs[0, 1].set_title("Histogram: distribution"); axs[0, 1].set_xlabel("Revenue")
axs[1, 0].scatter(df["quantity"], df["revenue"], alpha=.6, color="#dc2626")
axs[1, 0].set_title("Scatter: relationship"); axs[1, 0].set_xlabel("Quantity"); axs[1, 0].set_ylabel("Revenue")
order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
m = df.groupby("month")["revenue"].sum().reindex(order).dropna()
axs[1, 1].plot(m.index, m.values, marker="o", color="#059669")
axs[1, 1].set_title("Line: trend over time")
fig.suptitle("Four essential charts", fontsize=15, weight="bold"); fig.tight_layout()
fig.savefig(OUT / "chart_types.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Misleading vs honest axis
fig, (a, b) = plt.subplots(1, 2, figsize=(9, 4))
vals = [100, 104]
a.bar(["A", "B"], vals, color="#dc2626"); a.set_ylim(98, 105); a.set_title("Misleading: truncated axis")
b.bar(["A", "B"], vals, color="#059669"); b.set_ylim(0, 120); b.set_title("Honest: axis starts at 0")
fig.suptitle("Bars must start at zero", fontsize=14, weight="bold")
fig.savefig(OUT / "honest_axes.pdf", bbox_inches="tight"); plt.close(fig)
