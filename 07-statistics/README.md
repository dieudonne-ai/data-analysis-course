# Module 07 — Statistics Fundamentals

Statistics turns a pile of numbers into a few reliable statements. This lesson uses
`data/sales_eda.csv` (module 05) with pandas, numpy and scipy.

## 1. Descriptive statistics: summarize what you have

| Idea | Measures | Example |
|------|----------|---------|
| Center | mean, median, mode | typical order revenue |
| Spread | variance, std, IQR | how much revenue varies |
| Shape | skewness | a few huge orders pull the mean up |

```python
import pandas as pd
df = pd.read_csv("data/sales_eda.csv")
r = df["revenue"]
print(r.mean(), r.median(), r.std())   # mean > median => right-skewed
print(r.quantile([.25, .75]))          # IQR = Q3 - Q1
```

**Rule of thumb:** with outliers or skew, report the **median** and IQR; for symmetric data use mean and std.
Diagram: [`diagrams/center_spread.pdf`](diagrams/center_spread.pdf)

## 2. The normal distribution and the 68-95-99.7 rule

For bell-shaped data, about 68% of values lie within 1 std of the mean, 95% within 2, 99.7% within 3.
A **z-score** `z = (x - mean) / std` tells how many stds a value is from the mean;
`|z| > 3` is a common outlier flag. Diagram: [`diagrams/normal_rule.pdf`](diagrams/normal_rule.pdf)

```python
z = (r - r.mean()) / r.std()
outliers = df[z.abs() > 3]
```

## 3. Correlation is not causation

Pearson's `r` ranges from -1 to +1 and measures **linear** association.

```python
df["quantity"].corr(df["revenue"])      # strong positive: more units, more revenue
df[["quantity", "price", "revenue"]].corr()
```

Two variables moving together does not mean one causes the other (ice-cream sales and sunburn
both rise with summer heat). Diagram: [`diagrams/correlation.pdf`](diagrams/correlation.pdf)

## 4. Samples, populations and the Central Limit Theorem

We rarely see the whole **population**; we study a **sample** and estimate. The **Central Limit
Theorem**: the means of many samples are approximately normal, even if the data are skewed, and
their spread (the **standard error**, `std / sqrt(n)`) shrinks as n grows.
Diagram: [`diagrams/clt.pdf`](diagrams/clt.pdf)

```python
se = r.std() / len(r) ** 0.5
ci = (r.mean() - 1.96 * se, r.mean() + 1.96 * se)   # ~95% confidence interval for the mean
```

Runnable script: [`examples/stats_demo.py`](examples/stats_demo.py).

## Exercises
1. Compute mean, median and IQR of `revenue` per product. Which product is most skewed?
2. List orders with `|z| > 2.5` for `revenue`. Are they errors or real big orders?
3. Compute a 95% confidence interval for mean `quantity`.

## Git note (see [git-notes](../git-notes/README.md))
Undo safely: `git stash` shelves unfinished work, `git restore` discards edits, and `git revert`
undoes a pushed commit without rewriting history.
