# Module 03 — Data Loading with pandas

pandas is the main Python library for tabular data. Its core object is the **DataFrame**.

![Loading pipeline](diagrams/loading-pipeline.pdf) — [`diagrams/loading-pipeline.pdf`](diagrams/loading-pipeline.pdf)
· [`diagrams/dataframe-anatomy.pdf`](diagrams/dataframe-anatomy.pdf)

## Reading files
```python
import pandas as pd

df = pd.read_csv("data/sales.csv")        # CSV
# pd.read_excel("file.xlsx")              # Excel (needs openpyxl)
# pd.read_json("file.json")               # JSON
# pd.read_csv("file.csv", sep=";", encoding="latin-1")   # other separators / encodings
```
Compared with module 02, pandas converts types for you (`quantity` becomes an integer, `price` a float).

## First inspection
```python
df.head()       # first 5 rows
df.shape        # (8, 5) -> rows, columns
df.dtypes       # type of each column
df.info()       # types + missing values
df.describe()   # count, mean, std, min, quartiles, max
```

## Selecting data
```python
df["price"]                         # one column (a Series)
df[["product", "price"]]            # several columns
df.loc[0, "product"]                # by label -> 'Pen'
df.iloc[0:3]                        # by position
df[df["quantity"] > 5]              # filter rows
```

## New columns and grouping
```python
df["revenue"] = df["quantity"] * df["price"]
df.groupby("product")["revenue"].sum()
# Bag 75.0 | Notebook 68.0 | Pen 40.5
```

## Useful read_csv options
| Option | Use |
|--------|-----|
| `usecols=[...]` | load only some columns |
| `nrows=100` | load only the first rows (quick peek at big files) |
| `dtype={"order_id": str}` | force a type |
| `parse_dates=["date"]` | parse date columns |
| `na_values=["?", "n/a"]` | extra markers for missing values |

## Example
[`examples/load_sales.py`](examples/load_sales.py) loads `data/sales.csv`, inspects it, filters and groups.
Run it with `python 03-data-loading/examples/load_sales.py`.

## Exercises
1. Load `data/sales.csv` and print the number of rows and columns.
2. Find the most expensive product using `df.loc[df["price"].idxmax()]`.
3. Compute the total revenue per month.
