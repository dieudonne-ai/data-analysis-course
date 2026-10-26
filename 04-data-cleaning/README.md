# Module 04 — Data Cleaning

Real data is messy. Analysts spend a large part of their time cleaning it, because
wrong inputs give wrong conclusions ("garbage in, garbage out").

Diagrams: [`cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf),
[`missing_strategies.pdf`](diagrams/missing_strategies.pdf),
[`outlier_iqr.pdf`](diagrams/outlier_iqr.pdf).
Full script: [`examples/clean_sales.py`](examples/clean_sales.py) on [`data/sales_dirty.csv`](../data/sales_dirty.csv).

## Typical problems in `sales_dirty.csv`
| Problem | Example row | Fix |
|---------|-------------|-----|
| Duplicate row | order 4 appears twice | `drop_duplicates()` |
| Inconsistent text | `alice`, `Bob `, `notebook` | `str.strip()`, `str.title()` |
| Missing value | quantity empty (order 3), price `N/A` (order 5) | `fillna()` / `dropna()` |
| Invalid value | quantity `-2` (order 6) | treat as missing |
| Bad date | `not a date` (order 7) | `to_datetime(errors="coerce")` |
| Outlier | quantity `400` (order 8) | IQR rule |

## 1. Duplicates
```python
df = df.drop_duplicates()                       # identical rows
df = df.drop_duplicates(subset=["order_id"])    # same key
```

## 2. Text and types
```python
df["customer"] = df["customer"].str.strip().str.title()   # "alice " -> "Alice"
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")  # bad -> NaT
```

## 3. Missing values
Detect first: `df.isna().sum()`. Then choose a strategy (see the diagram):
```python
df.dropna(subset=["order_date"])                 # drop rows missing a key field
df["quantity"].fillna(df["quantity"].median())   # numeric -> median (robust)
df["price"].fillna(df.groupby("product")["price"].transform("median"))  # per group
```
Example: the `Pen` price is 1.5 everywhere else, so the missing price of order 5 becomes 1.5.

## 4. Invalid values
Use domain knowledge: a quantity cannot be negative.
```python
df.loc[df["quantity"] <= 0, "quantity"] = pd.NA
```

## 5. Outliers (IQR rule)
Values outside `[Q1 - 1.5·IQR, Q3 + 1.5·IQR]` are suspicious, where `IQR = Q3 - Q1`.
```python
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
df = df[df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
```
An outlier may be an error (typo `400` for `4`) or a real extreme value — check before deleting.

## Result
Running the script: 10 raw rows → 7 clean rows (1 duplicate, 1 outlier, 1 bad date removed).
Never overwrite the raw file: save to `data/sales_clean.csv` so the process is reproducible.

## Exercises
1. Replace the median fill for `quantity` by the mean. How does the result change?
2. Keep the row with the bad date by filling it with the previous valid date (`ffill`).
3. Count how many values each step modified and print a cleaning report.
