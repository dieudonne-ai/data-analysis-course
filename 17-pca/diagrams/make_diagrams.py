"""Generate PDF diagrams for module 17 (PCA)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(3)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. Principal axes on a 2-D cloud
pts = rng.multivariate_normal([0, 0], [[3, 2.2], [2.2, 2]], 200)
vals, vecs = np.linalg.eigh(np.cov(pts, rowvar=False))
vals, vecs = vals[::-1], vecs[:, ::-1]
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(*pts.T, s=14, alpha=.5, color="#1e3a8a")
for i, (c, n) in enumerate(zip(["#dc2626", "#059669"], ["PC1 (most variance)", "PC2"])):
    v = vecs[:, i] * np.sqrt(vals[i]) * 2.5
    ax.annotate("", v, (0, 0), arrowprops=dict(arrowstyle="->", lw=2.5, color=c))
    ax.text(*(v * 1.12), n, color=c, weight="bold", ha="center")
ax.set_aspect("equal"); ax.set_xlabel("feature A"); ax.set_ylabel("feature B")
ax.set_title("PCA finds the direction of greatest spread", weight="bold", loc="left"); clean(ax)
fig.savefig(OUT / "principal_axes.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Pipeline
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
steps = ["1. Standardize\n(z-scores)", "2. Covariance\nmatrix", "3. Eigenvectors &\neigenvalues", "4. Sort, keep\ntop k", "5. Project:\nX @ components"]
for i, t in enumerate(steps):
    x = .15 + i * 2.17
    ax.add_patch(FancyBboxPatch((x, 1), 1.8, 1.1, boxstyle="round,pad=.04", fc="#dbeafe" if i < 4 else "#dcfce7", ec="#334155"))
    ax.text(x + .9, 1.55, t, ha="center", va="center", fontsize=9.5)
    if i < 4: ax.annotate("", (x + 2.1, 1.55), (x + 1.85, 1.55), arrowprops=dict(arrowstyle="->"))
ax.set_title("The PCA recipe", weight="bold")
fig.savefig(OUT / "pca_pipeline.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Scree plot (values from pca_demo.py)
ratio = np.array([65.4, 33.6, 0.6, 0.4])
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.bar(range(1, 5), ratio, color="#93c5fd", label="per component")
ax.plot(range(1, 5), np.cumsum(ratio), "o-", color="#1e3a8a", lw=2.5, label="cumulative")
ax.axhline(95, ls="--", color="#dc2626"); ax.text(3.2, 90, "95% rule", color="#dc2626")
ax.set_xticks(range(1, 5)); ax.set_xticklabels([f"PC{i}" for i in range(1, 5)])
ax.set_ylabel("explained variance (%)"); ax.legend(frameon=False, loc="center right")
ax.set_title("Scree plot: 2 components keep 99% of the information", weight="bold", loc="left"); clean(ax)
fig.savefig(OUT / "scree.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Before / after
fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.6))
a.scatter(pts[:, 0], pts[:, 1], s=12, color="#1e3a8a", alpha=.5); a.set_title("Original axes", weight="bold")
sc = (pts - pts.mean(0)) @ vecs
b.scatter(sc[:, 0], sc[:, 1], s=12, color="#059669", alpha=.5); b.set_title("After PCA: uncorrelated axes", weight="bold")
b.set_xlabel("PC1"); b.set_ylabel("PC2"); a.set_xlabel("A"); a.set_ylabel("B")
for x in (a, b): clean(x); x.set_aspect("equal")
fig.savefig(OUT / "before_after.pdf", bbox_inches="tight"); plt.close(fig)
