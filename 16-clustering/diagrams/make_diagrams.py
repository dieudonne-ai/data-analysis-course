"""Generate PDF diagrams for module 16 (clustering)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(11)
COL = ["#1e3a8a", "#d97706", "#059669"]

# 1. Clusters found
cs = [(5, 20), (25, 60), (12, 150)]
fig, ax = plt.subplots(figsize=(7, 4.2))
for c, col, n in zip(cs, COL, ["occasional small", "regular mid", "big spenders"]):
    p = rng.normal(c, (2, 8), (100, 2))
    ax.scatter(p[:, 0], p[:, 1], s=14, color=col, alpha=.6, label=n)
    ax.scatter(*c, marker="X", s=180, color=col, ec="black", zorder=5)
ax.set_xlabel("visits per month"); ax.set_ylabel("average basket (EUR)")
ax.legend(frameon=False); ax.set_title("K-means finds 3 customer segments (X = centroid)", weight="bold", loc="left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.savefig(OUT / "clusters.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Algorithm loop
fig, ax = plt.subplots(figsize=(10, 3.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.2)
steps = ["1. Pick k\nrandom centroids", "2. Assign each point\nto nearest centroid", "3. Move centroid to\nmean of its points", "4. Stop when\nnothing moves"]
for i, t in enumerate(steps):
    x = .2 + i * 2.5
    ax.add_patch(FancyBboxPatch((x, 1.1), 2.0, 1.2, boxstyle="round,pad=.04", fc="#dbeafe" if i < 3 else "#dcfce7", ec="#334155"))
    ax.text(x + 1, 1.7, t, ha="center", va="center", fontsize=10)
    if i < 3: ax.annotate("", (x + 2.45, 1.7), (x + 2.05, 1.7), arrowprops=dict(arrowstyle="->"))
ax.annotate("", (3.4, 1.05), (6.0, 1.05), arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.4", color="#dc2626"))
ax.text(4.7, .25, "repeat steps 2-3", ha="center", color="#dc2626")
ax.set_title("The k-means loop", weight="bold")
fig.savefig(OUT / "kmeans_steps.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Elbow
k = np.arange(1, 7); inertia = [600, 271.7, 20.8, 17.4, 14.2, 11.3]
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(k, inertia, "o-", lw=2.5, color="#1e3a8a")
ax.annotate("elbow: k = 3", (3, 20.8), (3.8, 250), arrowprops=dict(arrowstyle="->"), fontsize=11, color="#dc2626")
ax.set_xlabel("number of clusters k"); ax.set_ylabel("inertia (within-cluster distance)")
ax.set_title("Elbow method: stop where the curve flattens", weight="bold", loc="left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.savefig(OUT / "elbow.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Scaling
fig, axs = plt.subplots(1, 2, figsize=(8, 3.4))
p = np.vstack([rng.normal(c, (2, 8), (60, 2)) for c in cs])
axs[0].scatter(p[:, 0], p[:, 1], s=10, color="#64748b"); axs[0].set_title("Raw: basket dominates distance")
axs[0].set_xlim(-50, 80); axs[0].set_xlabel("visits"); axs[0].set_ylabel("basket")
z = (p - p.mean(0)) / p.std(0)
axs[1].scatter(z[:, 0], z[:, 1], s=10, color="#1e3a8a"); axs[1].set_title("Scaled: both count equally"); axs[1].set_xlabel("visits (z)"); axs[1].set_ylabel("basket (z)")
fig.savefig(OUT / "scaling.pdf", bbox_inches="tight"); plt.close(fig)
