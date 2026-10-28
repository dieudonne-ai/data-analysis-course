# Module 04 — Data Cleaning

Real data is messy. Analysts commonly spend most of their time cleaning it. Bad input gives
bad conclusions ("garbage in, garbage out").

Diagram: [`diagrams/cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf)

Dataset: [`data/messy_sales.csv`](../data/messy_sales.csv) — it contains a duplicate row,
inconsistent text (`alice `, `PEN`), a bad date, a missing quantity, a negative price,
an `N/A` price and an extreme outlier (a bag at 2500.0).
Full script: [`examples/clean_sales.py`](examples/clean_sales.py).

## 1. Find the problems first
```python
df = pd.read_csv("data/messy_sales.csv", na_values=["N/A"])
df.isna().sum()          # missing values per column
df.duplicated().sum()    # number of duplicate rows (1 here)
df.describe()            # impossible minimums / huge maximums
df["product"].value_counts()   # 'Pen' vs 'PEN' show up as separate values
```

## 2. Remove duplicates
```python
df = df.drop_duplicates()                       # identical rows
df = df.drop_duplicates(subset=["order_id"])    # same key
```

## 3. Fix text
```python
df["customer"] = df["customer"].str.strip().str.title()   # 'alice ' -> 'Alice'
df["product"] = df["product"].str.lower()                  # 'PEN' -> 'pen'
df["product"] = df["product"].replace({"nb": "notebook"})  # known aliases
```

## 4. Fix types
```python
df["date"] = pd.to_datetime(df["date"], errors="coerce")   # 'not a date' -> NaT
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["order_id"] = df["order_id"].astype(str)
```
`errors="coerce"` turns unparseable values into missing values instead of raising an error.

## 5. Invalid values and outliers
A negative price is impossible: decide whether to fix it, mark it missing, or drop the row.
```python
df.loc[df["price"] < 0, "price"] = pd.NA
```
The **IQR rule** flags statistical outliers: anything below `Q1 - 1.5·IQR` or above
`Q3 + 1.5·IQR`.
```python
q1, q3 = df["price"].quantile([0.25, 0.75])
iqr = q3 - q1
outlier = (df["price"] < q1 - 1.5 * iqr) | (df["price"] > q3 + 1.5 * iqr)
```
An outlier is not automatically an error — investigate before deleting. Here 2500.0 is
probably a typo for 25.0, but only the data owner can confirm.

## 6. Missing values
| Strategy | Code | When |
|----------|------|------|
| Drop rows | `df.dropna(subset=["price"])` | few rows affected, column essential |
| Fill with a constant | `df["x"].fillna(0)` | 0 is a meaningful value |
| Fill with median/mean | `df["x"].fillna(df["x"].median())` | numeric, roughly random gaps |
| Fill with previous value | `df["x"].ffill()` | time series |

Prefer the **median** over the mean when outliers are present.

## Result
Our script goes from 9 rows with 6 problems to 6 clean rows, saved in `data/clean_sales.csv`.
Never overwrite the raw file: keep raw and clean data separate so the cleaning is reproducible.

## Exercises
1. Instead of dropping the `N/A` price row, fill it with the median price of the same product.
2. Replace the outlier 2500.0 by 25.0 and document why in a comment.
3. Add a check that fails (`assert`) if any `quantity` is negative after cleaning.
