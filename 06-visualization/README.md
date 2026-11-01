# Module 06 — Data Visualization

A chart turns numbers into something the eye can read in seconds. This lesson uses
`data/sales_eda.csv` (from module 05) and **matplotlib** through pandas.

## 1. Choose the chart from your goal

See [`diagrams/chart_chooser.pdf`](diagrams/chart_chooser.pdf)

| Goal | Chart | Example question |
|------|-------|------------------|
| Compare categories | Bar | Which product earns the most? |
| Distribution | Histogram, boxplot | Are most orders small? |
| Relationship | Scatter | Does quantity drive revenue? |
| Trend | Line | How does revenue change by month? |

## 2. The four essential charts

```python
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv("data/sales_eda.csv")

df.groupby("product")["revenue"].sum().plot.bar()         # bar
df["revenue"].plot.hist(bins=15)                          # histogram
df.plot.scatter(x="quantity", y="revenue")                # scatter
df.groupby("month")["revenue"].sum().plot(marker="o")     # line
plt.show()
```

Full runnable script: [`examples/plot_sales.py`](examples/plot_sales.py).
Result on real data: [`diagrams/chart_types.pdf`](diagrams/chart_types.pdf).

## 3. Good practice

1. **Title and label axes** (with units): `ax.set_title(...)`, `ax.set_ylabel("Revenue ($)")`.
2. **Bars start at zero** — a truncated axis exaggerates differences
   ([`diagrams/honest_axes.pdf`](diagrams/honest_axes.pdf)): 100 vs 104 looks like a 4x gap.
3. **Sort categories** by value so the ranking is obvious.
4. **Few colors, used with meaning** — highlight what matters, grey the rest.
5. **No pie charts** with more than 3 slices; a bar chart is easier to compare.

## 4. Anatomy of a matplotlib figure

```python
fig, ax = plt.subplots(figsize=(8, 4))   # Figure = canvas, Axes = one plot
ax.bar(["A", "B"], [3, 5])
ax.set_title("Title"); ax.set_xlabel("X"); ax.set_ylabel("Y")
fig.savefig("chart.png", dpi=150, bbox_inches="tight")
```

## Exercises
1. Plot average revenue (not total) per product, sorted. Does the ranking change?
2. Draw a boxplot of revenue per product (`df.boxplot("revenue", by="product")`).
3. Add a horizontal line at the mean revenue with `ax.axhline`.

## Git note (see [git-notes](../git-notes/README.md))
Generated PNGs are build outputs: add `*.png` under `examples/` to `.gitignore` instead of
committing them — commit the script that produces them.
