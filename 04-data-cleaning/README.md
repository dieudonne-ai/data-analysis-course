# Module 04 — Data Cleaning

Real data is messy. Analysts spend a large part of their time cleaning it.
We work on [`data/sales_messy.csv`](../data/sales_messy.csv), which contains typical problems:

| Problem | Example in the file |
|---------|---------------------|
| Missing values | `quantity` empty for order 3, `price` = `N/A` for order 5, empty `city` |
| Duplicate rows | order 4 appears twice |
| Inconsistent text | `"bob "` (trailing space), `kampala` vs `Kampala` |
| Mixed date formats | `03/15/2024` vs `2024-03-15` |
| Outliers | quantity `200` for order 7 |

Diagram: [`diagrams/cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf)

## 1. Find the problems
```python
df = pd.read_csv("data/sales_messy.csv", na_values=["N/A"])
df.isna().sum()          # missing values per column
df.duplicated().sum()    # 1 duplicated row
```

## 2. Missing values — three strategies
```python
df.dropna(subset=["price"])                     # drop rows
df["quantity"] = df["quantity"].fillna(df["quantity"].median())   # impute
df["city"] = df["city"].fillna("Unknown")       # label as unknown
```
Rule of thumb: drop when few rows are affected, impute numbers with the median
(robust to outliers), and use a label for categories.

## 3. Duplicates
```python
df = df.drop_duplicates()
```

## 4. Text cleaning
```python
df["customer"] = df["customer"].str.strip().str.title()   # "bob " -> "Bob"
df["city"] = df["city"].str.title()                       # "kampala" -> "Kampala"
```

## 5. Types and dates
```python
df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
```

## 6. Outliers (IQR rule)
A value is suspicious if it lies outside `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]`.
```python
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
mask = df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
df[~mask]      # order 7 (200 bags) is flagged
```
Do not delete outliers blindly: check whether it is a typo (20 or 2?) or a real event.

## Exercise
Clean the file, then compute total revenue per city. Compare to the raw file.
Script: [`examples/clean_sales.py`](examples/clean_sales.py)
