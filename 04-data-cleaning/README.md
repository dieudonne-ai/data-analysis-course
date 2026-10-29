# Module 04 — Data Cleaning

Real data is messy. Typical problems: duplicate rows, inconsistent text,
missing values, outliers and wrong types. Cleaning typically takes most of an analyst's time.

Diagrams: [`cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf) and
[`outlier_iqr.pdf`](diagrams/outlier_iqr.pdf).

We use [`data/sales_messy.csv`](../data/sales_messy.csv): a copy of the sales data with
a duplicated order, `" notebook "` / `"PEN"` spelling, two blanks and one absurd quantity (500).

## 1. Spot the problems
```python
df = pd.read_csv("data/sales_messy.csv")
df.isna().sum()          # quantity: 1, price: 1
df.duplicated().sum()    # 1
df["product"].unique()   # ['Pen' 'notebook ' 'Bag' 'Notebook' 'PEN']
```

## 2. Duplicates
```python
df = df.drop_duplicates()                       # whole row identical
df = df.drop_duplicates(subset="order_id")      # same id only
```

## 3. Inconsistent text
```python
df["product"] = df["product"].str.strip().str.title()
# 'notebook ' -> 'Notebook', 'PEN' -> 'Pen'
```

## 4. Missing values
Three strategies — pick based on meaning, not convenience:
```python
df.dropna(subset=["quantity"])                       # drop rows
df["quantity"].fillna(df["quantity"].median())       # constant / statistic
df["price"].fillna(df.groupby("product")["price"].transform("median"))  # smart fill
```
Example: the missing price of a `Bag` is filled with 25.0, the usual Bag price.

## 5. Outliers (IQR rule)
A value is suspicious if it lies beyond `Q3 + 1.5·IQR` or below `Q1 − 1.5·IQR`.
```python
q1, q3 = df["quantity"].quantile([0.25, 0.75])
upper = q3 + 1.5 * (q3 - q1)
df[df["quantity"] > upper]      # the 500 row
```
Investigate before deleting: it may be a typo (5.00) or a real bulk order.

## 6. Types
```python
df["quantity"] = df["quantity"].astype(int)
df["date"] = pd.to_datetime(df["date"])
```

## Full example
[`examples/clean_sales.py`](examples/clean_sales.py): 10 raw rows -> 8 clean rows.

## Exercises
1. Replace `fillna(median)` by `dropna` and compare the totals.
2. Use the z-score instead of IQR to detect the outlier.
3. Save the result with `df.to_csv("data/sales_clean.csv", index=False)`.
