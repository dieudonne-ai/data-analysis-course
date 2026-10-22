# Module 04 — Data Cleaning

Real data is messy. Analysts spend a large share of their time cleaning it, because
wrong inputs give wrong conclusions ("garbage in, garbage out").

Diagrams: [`cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf) and
[`missing_strategies.pdf`](diagrams/missing_strategies.pdf).
Dataset: [`data/sales_dirty.csv`](../data/sales_dirty.csv) — the sales table with typical problems
(a duplicate row, `"notebook "` and `"PEN"` spellings, a missing quantity, `N/A` price, and an
absurd quantity of 600).

Runnable script: [`examples/clean_sales.py`](examples/clean_sales.py)

## 1. Detect missing values
```python
df = pd.read_csv("data/sales_dirty.csv", na_values=["N/A"])
df.isna().sum()
# quantity    1
# price       1
```

## 2. Remove duplicates
```python
df.duplicated().sum()        # 1
df = df.drop_duplicates()    # order 3 appeared twice
```

## 3. Fix inconsistent text
`"notebook "`, `"Notebook"` and `"PEN"` / `"Pen"` would be counted as different products.
```python
df["product"] = df["product"].str.strip().str.title()
```

## 4. Handle missing values
Choose a strategy (see the diagram):
```python
df["quantity"] = df["quantity"].fillna(df["quantity"].median())  # fill
df = df.dropna(subset=["price"])                                  # drop
```
Median is safer than mean when outliers exist. Whatever you choose, document it.

## 5. Treat outliers (IQR rule)
A value is suspicious if it lies outside `[Q1 - 1.5·IQR, Q3 + 1.5·IQR]`.
```python
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
mask = df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
df = df[mask]            # the 600-unit order is removed
```
Don't delete blindly: first check whether the value is a typo or a real extreme.

## 6. Fix data types
```python
df["quantity"] = df["quantity"].astype(int)
pd.to_numeric(df["price"], errors="coerce")   # bad strings -> NaN
pd.to_datetime(df["date"])                    # text -> datetime
```

## Result
9 raw rows become 6 clean rows (`Shape after cleaning: (6, 5)`).

## Exercises
1. Replace the median fill with the mean. How does the result change?
2. Instead of dropping the row with a missing price, fill it using the typical price of that product (`groupby`).
3. Add a `valid` boolean column instead of deleting outliers.
