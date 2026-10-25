# Module 04 - Data Cleaning

Real data is messy. Analysts spend a large part of their time cleaning it.
Dataset: [`data/sales_messy.csv`](../data/sales_messy.csv) - the sales table with typical problems.

Diagrams: [pipeline](diagrams/cleaning_pipeline.pdf) - [missing values](diagrams/missing_values_decision.pdf) - [IQR rule](diagrams/iqr_rule.pdf)

## Typical problems in the messy file
| Problem | Example in the file | Fix |
|---------|--------------------|-----|
| Duplicate rows | order 5 appears twice | `drop_duplicates()` |
| Inconsistent text | `notebook `, `NOTEBOOK` | `str.strip().str.title()` |
| Missing values | empty quantity / price / email | `fillna`, `dropna` |
| Impossible values | price `-25.0` | set to missing, then fill |
| Outliers | quantity `300` | IQR rule |

## 1. Find the problems
```python
df.isna().sum()          # missing per column
df.duplicated().sum()    # number of duplicate rows
df.describe()            # min/max reveal impossible values
df["product"].value_counts()  # reveals 'Notebook' vs 'NOTEBOOK'
```

## 2. Duplicates and text
```python
df = df.drop_duplicates()
df["product"] = df["product"].str.strip().str.title()
```

## 3. Missing values
```python
df.dropna(subset=["price"])                       # drop rows
df["quantity"].fillna(df["quantity"].median())    # fill with median
df["price"].fillna(df.groupby("product")["price"].transform("median"))  # per group
```
Median is safer than mean when outliers exist.

## 4. Outliers - the IQR rule
A value is an outlier if it is below `Q1 - 1.5*IQR` or above `Q3 + 1.5*IQR`, where `IQR = Q3 - Q1`.
```python
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
df = df[df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
```
An outlier is not always an error: check whether it is real (a big wholesale order) before removing it.

## 5. Fix types
```python
df["month"] = pd.Categorical(df["month"], ["Jan", "Feb", "Mar", "Apr"], ordered=True)
df["quantity"] = df["quantity"].astype(int)
```

## Exercises
1. How many rows does `sales_messy.csv` have before and after cleaning?
2. Replace missing emails with `"unknown"` instead of leaving `NaN`.
3. Remove outliers from `price` too. What changes?
4. Why is dropping every row with a missing value a bad default?

Run the worked example: `python 04-data-cleaning/examples/clean_sales.py`
