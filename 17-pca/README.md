# Module 17 – Dimensionality Reduction with PCA (bonus)

Real datasets often have dozens of columns, many of them saying the same thing (visits and orders, spend and items). **Principal Component Analysis (PCA)** compresses them into a few new columns, the **principal components**, that keep most of the information. Uses: visualising high-dimensional data, speeding up models, removing redundancy before clustering (module 16).

Run it: `python 17-pca/examples/pca_demo.py` (numpy/pandas only).

## 1. The idea
Diagram: [`diagrams/principal_axes.pdf`](diagrams/principal_axes.pdf)

If two features are correlated, the cloud of points is a tilted ellipse. PCA draws a new axis along the longest direction (**PC1**), then a second one perpendicular to it (**PC2**), and so on. Each component is a weighted mix of the original columns.

## 2. The recipe
Diagram: [`diagrams/pca_pipeline.pdf`](diagrams/pca_pipeline.pdf)

```python
X = (df - df.mean()) / df.std()                 # 1. standardize
cov = np.cov(X.to_numpy(), rowvar=False)        # 2. covariance matrix
vals, vecs = np.linalg.eigh(cov)                # 3. eigenvalues / eigenvectors
order = vals.argsort()[::-1]                    # 4. biggest first
vals, vecs = vals[order], vecs[:, order]
scores = X.to_numpy() @ vecs[:, :2]             # 5. project on the top 2
```
- **Eigenvector** = a direction (a component).
- **Eigenvalue** = how much variance lies along it.

Always standardize first, for the same reason as k-means: otherwise the column with the biggest units wins.

## 3. How many components? The scree plot
Diagram: [`diagrams/scree.pdf`](diagrams/scree.pdf)

Our example has 4 correlated columns driven by 2 hidden factors:

| component | explained variance | cumulative |
|---|---|---|
| PC1 | 65.4 % | 65.4 % |
| PC2 | 33.6 % | 99.0 % |
| PC3 | 0.6 % | 99.6 % |
| PC4 | 0.4 % | 100 % |

Common rules: keep enough components to reach 90–95 % cumulative variance, or stop at the "elbow" of the scree plot. Here 2 is clearly enough.

## 4. Reading the loadings
| feature | PC1 | PC2 |
|---|---|---|
| visits | -0.51 | -0.49 |
| orders | -0.49 | -0.52 |
| spend | -0.50 | 0.50 |
| items | -0.50 | 0.50 |

PC1 mixes all four equally: an overall "activity level". PC2 opposes (visits, orders) to (spend, items): "frequent small buyers vs rare big buyers". The **sign of a whole component is arbitrary**; only the pattern matters. Naming components is how you make them explainable.

## 5. Before and after
Diagram: [`diagrams/before_after.pdf`](diagrams/before_after.pdf)

After PCA the new axes are **uncorrelated**. Compressing 4 columns to 2 and rebuilding the data gives a mean squared error of just 0.010 (in z-score units): little was lost.

## 6. Limits
- Components are linear mixes, so they are harder to explain than raw columns.
- PCA is sensitive to scale and to outliers (clean first, module 04).
- High variance is not always high importance: a useful but low-variance signal can be dropped.
- Only linear structure is captured.

## Exercise
Add a fifth column `discount_use` correlated with `loyal`. Does the number of components needed change? Which loadings move?
