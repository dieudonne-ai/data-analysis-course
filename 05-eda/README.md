# Module 05 — Exploratory Data Analysis (EDA)

**Goal:** understand a dataset *before* modelling it: its shape, distributions, outliers and relationships.

Diagrams: [`diagrams/eda_loop.pdf`](diagrams/eda_loop.pdf) and
[`diagrams/distributions.pdf`](diagrams/distributions.pdf).

Dataset: [`data/sales_eda.csv`](../data/sales_eda.csv) — 200 orders (product, quantity, price, month, revenue).
Script: [`examples/explore_sales.py`](examples/explore_sales.py).

## 1. First look
```python
df.shape        # (200, 6)
df.dtypes       # are numbers really numeric?
df.describe()   # count, mean, std, min, quartiles, max
```
Example result: mean revenue = 21.53, median = 17.0.

## 2. Univariate analysis (one variable)
- **Categorical:** `df["product"].value_counts()` → Pen 79, Notebook 63, Marker 35, Bag 23.
- **Numeric:** histogram + boxplot. If **mean > median**, the distribution is right-skewed
  (here skewness = 0.78: many small orders, a few big ones).

## 3. Outliers — the IQR rule
`IQR = Q3 − Q1`. A value is suspicious if it is below `Q1 − 1.5·IQR` or above `Q3 + 1.5·IQR`.
In this dataset no row is flagged (0 of 200). An outlier is not automatically an error:
check whether it is a typo (clean it) or a real extreme (keep it, report it).

## 4. Bivariate analysis (two variables)
```python
df.groupby("product")["revenue"].agg(["count", "sum", "mean"])
df[["quantity", "price", "revenue"]].corr()
```
| Product | Orders | Total revenue | Avg order |
|---------|-------:|--------------:|----------:|
| Notebook | 63 | 1948.0 | 30.9 |
| Bag | 23 | 925.0 | 40.2 |
| Pen | 79 | 865.5 | 11.0 |
| Marker | 35 | 567.5 | 16.2 |

Insight: pens sell the most *often* but notebooks bring the most *money*.
Correlation of quantity and price is −0.42: expensive items (bags) are bought in smaller quantities.

> **Correlation ≠ causation.** A correlation near 0 means no *linear* relationship; always plot it.

## 5. Time patterns
Group by month (`reindex` to keep calendar order). Revenue peaks in January (974.5) and
June (929.0) and dips in May (520.0) — a question for the next iteration of the EDA loop.

## Exercises
1. Which month has the most orders (not revenue)?
2. Compute the IQR outliers for `quantity`.
3. Add a column `size` = "big" if revenue > 32 else "small" and compare the average price of each group.

## Git corner
Work on a branch, then merge: `git switch -c module-05`, commit, `git switch main`,
`git merge module-05`. See [git-notes](../git-notes/README.md).
