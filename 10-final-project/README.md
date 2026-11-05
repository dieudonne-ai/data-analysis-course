# Module 10 — Final Project

Time to combine everything. We run one complete analysis on `data/sales_eda.csv`
and write a short report. Run it with `python 10-final-project/examples/final_project.py`.
Diagram: [`diagrams/pipeline.pdf`](diagrams/pipeline.pdf)

## 1. Start with a question
A good question is specific and answerable: *"Does product mix drive revenue, and can we predict an order's revenue?"*
Write it down first, plus what a useful answer looks like (e.g. a difference test and a prediction error).

## 2. Load and clean (modules 03-04)
Check shape, missing values and duplicates **before** analysing. Script every fix so it is repeatable.
```python
raw = pd.read_csv("data/sales_messy.csv")
raw.isna().sum().sum(), raw.duplicated().sum()   # 2 missing cells, 1 duplicate
```

## 3. Explore (modules 05-07)
Group, summarise, correlate.
```python
df.groupby("product")["revenue"].agg(["count", "mean", "sum"])
```
Result: Notebook brings the most revenue in total (1948), Bag has the highest average order (40.2).
Notice the difference: *total* depends on how often a product sells; *mean* does not.

## 4. Test (module 08)
Are the product means really different, or is it noise? One-way ANOVA: `F = 55.3, p < 0.001` → reject H0.
Always add an effect size or a plot, not just a p-value.

## 5. Model (module 09)
`revenue ~ quantity + price`, fitted on 70% of rows. Test RMSE 8.64 vs train 8.22 (close → no overfitting), test R² = 0.73.

## 6. Communicate
One figure per finding, plain words, and honest limits.
Diagram: [`diagrams/summary.pdf`](diagrams/summary.pdf) — a one-page summary.
Report template:

1. **Question** 2. **Data** (source, size, cleaning) 3. **Findings** (3 bullets, each with a number)
4. **Method** (test/model used and why) 5. **Limits** 6. **Next steps**

Self-check with [`diagrams/checklist.pdf`](diagrams/checklist.pdf).

## Exercises
1. Repeat the analysis asking about `month` instead of `product`.
2. Replace ANOVA with Kruskal-Wallis (`stats.kruskal`). Do conclusions change?
3. Add `product` as dummy variables in the regression. Does test R² improve?
4. Pick your own dataset, put it in `data/`, and write the six-section report in a new branch.

## Git for this module
See the new "Rebase, cherry-pick and releases" section in [git-notes](../git-notes/README.md).
