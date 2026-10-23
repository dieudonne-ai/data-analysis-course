# Module 04 — Data Cleaning

Real data is messy. Analysts commonly spend most of their time cleaning, because
wrong inputs give wrong conclusions ("garbage in, garbage out").

Diagrams: [`cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf),
[`missing_strategies.pdf`](diagrams/missing_strategies.pdf),
[`iqr_rule.pdf`](diagrams/iqr_rule.pdf)

Dataset: [`data/sales_messy.csv`](../data/sales_messy.csv) — the sales table with typical problems:
a duplicated row, extra spaces, inconsistent case (`uk`/`UK`), `N/A`, an empty quantity,
a negative quantity, mixed date formats, a missing date and a suspicious price (150.0 for a pen).
Full script: [`examples/clean_sales.py`](examples/clean_sales.py).

## 1. Detect problems first
```python
df = pd.read_csv("data/sales_messy.csv", na_values=["N/A"])
df.isna().sum()            # missing values per column
df.duplicated().sum()      # number of duplicated rows (1 here)
df["country"].unique()     # ['UK' 'uk' 'Kenya' 'KENYA' 'Uganda'] -> inconsistent
df.describe()              # min quantity = -6 -> impossible
```

## 2. Duplicates
```python
df = df.drop_duplicates()                       # identical rows
df = df.drop_duplicates(subset="order_id")      # same key = same order
```

## 3. Text cleaning
```python
df["customer"] = df["customer"].str.strip().str.title()   # "  alice " -> "Alice"
df["country"] = df["country"].str.upper().replace({"UK": "United Kingdom"}).str.title()
```
Without this, `groupby("country")` would treat `UK` and `uk` as different groups.

## 4. Dates
```python
iso = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
uk = pd.to_datetime(df["order_date"], format="%d/%m/%Y", errors="coerce")
df["order_date"] = iso.fillna(uk)
```
`errors="coerce"` turns bad values into `NaT` instead of crashing.
Pitfall: `dayfirst=True` on ISO dates swaps day and month (`2026-01-03` becomes 1 March) —
always check a few parsed values.

## 5. Invalid and missing values
```python
df.loc[df["quantity"] < 0, "quantity"] = pd.NA            # impossible -> missing
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))
```
Strategies (see diagram): drop, fill with a statistic, or fill with a label such as `"Unknown"`.
Prefer the **median** for numbers with outliers. Always document what you changed.

## 6. Outliers: the IQR rule
```python
q1, q3 = s.quantile([0.25, 0.75])
outlier = (s < q1 - 1.5 * (q3 - q1)) | (s > q3 + 1.5 * (q3 - q1))
```
Flag outliers (`price_outlier` column) rather than deleting them blindly: a 150.0 pen is
probably a typo, but only the data owner can confirm.

## Exercises
1. Count how many rows changed during cleaning (compare raw and clean shapes).
2. Fill the missing `order_date` with the most common month instead of leaving `NaT`. Is that wise?
3. Make the cleaning a function `clean(df) -> df` so it can be reused on next month's file.
