# Module 16 – Clustering & Customer Segmentation (bonus)

Classification (module 15) needs a labelled answer column. **Clustering** is *unsupervised*: no labels, the algorithm looks for natural groups. Typical use: customer segmentation for marketing.

Run it: `python 16-clustering/examples/segment_customers.py` — it generates `data/customers.csv` (300 customers) and runs k-means from scratch.

## 1. The idea
Diagram: [`diagrams/clusters.pdf`](diagrams/clusters.pdf)

Each customer is a point (visits per month, average basket). Customers close to each other form a **cluster**; the cluster centre is its **centroid**. Three groups appear: occasional small buyers, regular mid buyers, big spenders.

## 2. The k-means algorithm
Diagram: [`diagrams/kmeans_steps.pdf`](diagrams/kmeans_steps.pdf)

```python
cent = X[rng.choice(len(X), k, replace=False)]          # 1. random start
for _ in range(50):
    d = np.linalg.norm(X[:, None] - cent[None], axis=2)  # distance to each centroid
    lab = d.argmin(1)                                    # 2. assign
    cent = np.array([X[lab == j].mean(0) for j in range(k)])  # 3. update
```
Repeat until centroids stop moving. Result depends on the random start, so run several starts and keep the lowest **inertia** (sum of squared distances to the centroid).

## 3. Always scale first
Diagram: [`diagrams/scaling.pdf`](diagrams/scaling.pdf)

K-means uses distances. Basket (5–170 EUR) is far bigger than visits (1–30), so without scaling it would decide everything. Use z-scores: `(X - X.mean(0)) / X.std(0)`.

## 4. Choosing k: the elbow method
Diagram: [`diagrams/elbow.pdf`](diagrams/elbow.pdf)

| k | inertia |
|---|---|
| 1 | 600.0 |
| 2 | 271.7 |
| 3 | 20.8 |
| 4 | 17.4 |
| 6 | 11.3 |

Inertia always falls when k grows. Pick the **elbow**, where the gain suddenly shrinks: here k = 3. Also ask: *can the business act on this many segments?*

## 5. Profiling segments
A cluster is just a number until you describe it:

```python
df.groupby("segment").agg(size=("visits","size"), visits=("visits","mean"), basket=("basket","mean"))
```
| segment | size | visits | basket (EUR) | name |
|---|---|---|---|---|
| 1 | 100 | 5.0 | 20.1 | occasional small |
| 0 | 100 | 25.2 | 60.4 | regular mid |
| 2 | 100 | 12.0 | 149.3 | big spenders |

(Cluster numbers are arbitrary and can change between runs; names come from the profile.)

## 6. Limits
- You must choose k; there is no single correct answer.
- K-means assumes round, similar-sized groups.
- Outliers pull centroids: clean data first (module 04).

## 7. Exercises
1. Remove the scaling step and compare the segments. What changes?
2. Add a third feature (e.g. `returns`) and re-run the elbow.
3. Try k = 4: can you give each of the 4 segments a useful business name?

Next: the course is complete – pick your own dataset and publish a project!
