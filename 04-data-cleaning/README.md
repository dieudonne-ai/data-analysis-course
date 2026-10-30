# Module 04 — Data Cleaning

Real data is messy. Cleaning typically takes more time than analysis itself.
Diagram: [`diagrams/cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf)

Dataset: [`data/sales_messy.csv`](../data/sales_messy.csv) — it contains a duplicate row,
a missing quantity, a missing price (`N/A`), inconsistent text (`notebook `, `PEN`)
and an impossible quantity (`-1`).

## 1. Find the problems
```python
df = pd.read_csv("data/sales_messy.csv", na_values=["N/A"])
df.isna().sum()          # missing values per column
df.duplicated().sum()    # -> 1
df.describe()            # min quantity = -1 -> suspicious
```

## 2. Duplicates
```python
df = df.drop_duplicates()
```

## 3. Inconsistent text
```python
df["product"] = df["product"].str.strip().str.title()
# "notebook " -> "Notebook", "PEN" -> "Pen"
```

## 4. Missing values — three choices
| Strategy | Code | When |
|----------|------|------|
| Drop the row | `df.dropna(subset=["price"])` | value is essential and cannot be guessed |
| Fill with a statistic | `df["quantity"].fillna(df["quantity"].median())` | numeric, few gaps |
| Fill with a constant | `df["month"].fillna("Unknown")` | categories |

Median is safer than mean when outliers exist.

## 5. Impossible values and dtypes
```python
df = df[df["quantity"] > 0]
df["quantity"] = df["quantity"].astype(int)
```

## Run the example
```bash
python 04-data-cleaning/examples/clean_sales.py
```
Result: 8 raw rows -> 5 clean rows saved to `data/sales_clean.csv`.

## Exercise
Add a rule that flags any price above 20 as "premium" using `df["price"] > 20`.
