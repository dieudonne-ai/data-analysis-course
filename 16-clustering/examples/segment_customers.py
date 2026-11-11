"""K-means clustering from scratch (numpy/pandas only): customer segmentation.

Unsupervised learning: there is no 'right answer' column, we look for groups.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(11)

print("== 1. The data: 3 hidden customer types ==")
centers = [(5, 20), (25, 60), (12, 150)]          # (visits/month, avg basket in EUR)
parts = [rng.normal(c, (2, 8), (100, 2)) for c in centers]
df = pd.DataFrame(np.vstack(parts), columns=["visits", "basket"]).round(1)
df.to_csv(Path(__file__).resolve().parents[2] / "data" / "customers.csv", index=False)
print(df.describe().round(1))

print("\n== 2. Scale features (otherwise 'basket' dominates distances) ==")
X = df.to_numpy()
X = (X - X.mean(0)) / X.std(0)


def kmeans(X, k, iters=50, seed=0):
    r = np.random.default_rng(seed)
    cent = X[r.choice(len(X), k, replace=False)]
    for _ in range(iters):
        d = np.linalg.norm(X[:, None] - cent[None], axis=2)   # distance to each centroid
        lab = d.argmin(1)                                      # assign step
        new = np.array([X[lab == j].mean(0) if (lab == j).any() else cent[j] for j in range(k)])
        if np.allclose(new, cent):
            break
        cent = new                                             # update step
    inertia = ((X - cent[lab]) ** 2).sum()
    return lab, cent, inertia


print("== 3. Choosing k with the elbow method ==")
for k in range(1, 7):
    best = min(kmeans(X, k, seed=s)[2] for s in range(5))      # several starts, keep the best
    print(f"k={k}  inertia={best:7.1f}")
print("-> the curve bends at k=3: more clusters barely help")

print("\n== 4. Fit k=3 and profile each segment ==")
lab, cent, _ = min((kmeans(X, 3, seed=s) for s in range(5)), key=lambda r: r[2])
df["segment"] = lab
print(df.groupby("segment").agg(size=("visits", "size"), visits=("visits", "mean"), basket=("basket", "mean")).round(1))
print("-> name them: 'occasional small', 'regular mid', 'big spenders'")
