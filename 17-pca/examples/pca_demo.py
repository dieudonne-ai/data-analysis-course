"""PCA from scratch (numpy/pandas only): compress correlated features.

Dimensionality reduction: keep the directions that carry the most variance.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(5)

print("== 1. The data: 4 correlated features driven by 2 hidden factors ==")
n = 200
size = rng.normal(0, 1, n)       # hidden factor 1: how big the customer is
loyal = rng.normal(0, 1, n)      # hidden factor 2: how loyal
df = pd.DataFrame({
    "visits":   2.0 * loyal + 0.3 * size + rng.normal(0, .3, n),
    "orders":   1.8 * loyal + 0.2 * size + rng.normal(0, .3, n),
    "spend":    2.5 * size + 0.4 * loyal + rng.normal(0, .3, n),
    "items":    2.2 * size + 0.3 * loyal + rng.normal(0, .3, n),
}).round(2)
print(df.corr().round(2))

print("\n== 2. Standardize, then covariance matrix ==")
X = (df - df.mean()) / df.std()
cov = np.cov(X.to_numpy(), rowvar=False)

print("\n== 3. Eigen-decomposition: eigenvectors = components ==")
vals, vecs = np.linalg.eigh(cov)
order = vals.argsort()[::-1]
vals, vecs = vals[order], vecs[:, order]
ratio = vals / vals.sum()
for i, (v, r) in enumerate(zip(vals, ratio), 1):
    print(f"PC{i}: eigenvalue={v:.2f}  explained={r:.1%}  cumulative={ratio[:i].sum():.1%}")

print("\n== 4. Loadings (what each component means) ==")
load = pd.DataFrame(vecs[:, :2], index=df.columns, columns=["PC1", "PC2"]).round(2)
print(load)

print("\n== 5. Project data on 2 components (4 columns -> 2) ==")
scores = X.to_numpy() @ vecs[:, :2]
print(pd.DataFrame(scores, columns=["PC1", "PC2"]).head().round(2))

print("\n== 6. Reconstruction error ==")
back = scores @ vecs[:, :2].T
err = ((X.to_numpy() - back) ** 2).mean()
print(f"mean squared error after compressing 4 -> 2 features: {err:.3f}")
