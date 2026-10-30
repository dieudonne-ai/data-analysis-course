# Module 04 — Data Cleaning

Real data is messy. Cleaning typically takes most of an analyst's time, and
every later result depends on it.

Diagrams: [`cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf) and
[`outlier_iqr.pdf`](diagrams/outlier_iqr.pdf).

We use `data/sales_dirty.csv`, a copy of the sales data with typical problems:
a duplicated row, missing values, inconsistent text (`"notebook "`, `"PEN"`),
a negative quantity and an extreme value (400).

## 1. Find the problems
```python
df = pd.read_csv("data/sales_dirty.csv")
df.isna().sum()        # missing values per column
df.duplicated().sum()  # duplicated rows -> 1
df["product"].unique() # reveals 'notebook ', 'PEN'
df.describe()          # reveals negative / huge values
```

## 2. Duplicates
```python
df = df.drop_duplicates()
df = df.drop_duplicates(subset="order_id")   # same key only
```

## 3. Inconsistent text
```python
df["product"] = df["product"].str.strip().str.title()
# 'notebook ' -> 'Notebook', 'PEN' -> 'Pen'
```

## 4. Missing values
Options: drop, fill with a constant, or fill with a statistic.
```python
df.dropna(subset=["price"])                  # drop rows
df["quantity"].fillna(0)                     # constant
df["quantity"].fillna(df["quantity"].median())
# fill by group: price of a missing Notebook = median Notebook price
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))
```
Prefer the median over the mean when the data has outliers.

## 5. Invalid values
Use domain rules: a quantity cannot be negative.
```python
df = df[df["quantity"] > 0]
```

## 6. Outliers (IQR rule)
A value is an outlier if it lies beyond `Q3 + 1.5 * IQR` (or below `Q1 - 1.5 * IQR`).
```python
q1, q3 = df["quantity"].quantile([0.25, 0.75])
upper = q3 + 1.5 * (q3 - q1)
df = df[df["quantity"] <= upper]
```
Check each outlier before removing it: it can be a typo (400 instead of 4) or a real, important event.

## 7. Fix types
```python
df["quantity"] = df["quantity"].astype(int)
```

## Exercises
1. Run the example and explain each row that was removed or changed.
2. Replace the median fill for `quantity` with `0`. How does the average change?
3. Use `drop_duplicates(subset="order_id")` instead. Same result? Why?
4. Detect outliers in `price` with the IQR rule.

Run the worked example: `python 04-data-cleaning/examples/clean_sales.py`
(writes `data/sales_clean.csv`).
