"""Generate PDF diagrams for module 10 (final project)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "sales_eda.csv")

# 1. Project pipeline mapped to modules
steps = [("Question", "01"), ("Load", "03"), ("Clean", "04"), ("Explore", "05-07"),
         ("Test", "08"), ("Model", "09"), ("Communicate", "06 + 10")]
fig, ax = plt.subplots(figsize=(12, 3)); ax.axis("off"); ax.set_xlim(0, 7); ax.set_ylim(0, 1)
for i, (name, mod) in enumerate(steps):
    ax.add_patch(FancyBboxPatch((i + .06, .3), .88, .4, boxstyle="round,pad=0.02", fc="#1e3a8a" if i < 6 else "#15803d", ec="none"))
    ax.text(i + .5, .53, name, ha="center", va="center", color="white", weight="bold", fontsize=10)
    ax.text(i + .5, .15, f"module {mod}", ha="center", fontsize=8, color="#475569")
    if i < 6: ax.annotate("", (i + 1.06, .5), (i + .94, .5), arrowprops=dict(arrowstyle="->", lw=1.5))
ax.set_title("A data analysis project, end to end", weight="bold")
fig.savefig(OUT / "pipeline.pdf", bbox_inches="tight"); plt.close(fig)

# 2. One-page results summary
fig, axs = plt.subplots(1, 3, figsize=(14, 4))
tot = df.groupby("product")["revenue"].sum().sort_values()
axs[0].barh(tot.index, tot.values, color="#1e3a8a"); axs[0].set_title("Total revenue by product"); axs[0].set_xlabel("revenue")
df.boxplot(column="revenue", by="product", ax=axs[1], grid=False); axs[1].set_title("Revenue spread by product"); axs[1].set_xlabel("")
X = np.column_stack([np.ones(len(df)), df["quantity"], df["price"]]); y = df["revenue"].to_numpy(float)
b, *_ = np.linalg.lstsq(X, y, rcond=None); p = X @ b
axs[2].scatter(p, y, s=12, alpha=.6, color="#15803d"); axs[2].plot([0, y.max()], [0, y.max()], "k--", lw=1)
axs[2].set_title("Model: predicted vs actual"); axs[2].set_xlabel("predicted"); axs[2].set_ylabel("actual")
fig.suptitle("Final project summary: one figure per finding", weight="bold", y=1.03)
fig.savefig(OUT / "summary.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Checklist
items = ["Clear question and success metric", "Data source and date documented", "Cleaning steps scripted, not manual",
         "Plots have titles, labels, honest axes", "Test chosen to match the data; effect size reported",
         "Model checked on held-out data", "Limits and next steps stated", "Code runs top-to-bottom; committed to Git"]
fig, ax = plt.subplots(figsize=(8, 4.5)); ax.axis("off")
for i, t in enumerate(items):
    ax.text(0, 1 - i * .12, "☑  " + t, fontsize=12, va="top", family="DejaVu Sans")
ax.set_title("Before you share your analysis", weight="bold", loc="left")
fig.savefig(OUT / "checklist.pdf", bbox_inches="tight"); plt.close(fig)
