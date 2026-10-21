# Module 03 — Data Loading with pandas

pandas is the standard Python library for tabular data. Its two core objects are:

- **Series** — one labeled column of values.
- **DataFrame** — a table of Series sharing the same row index.

See the diagram: [`diagrams/dataframe_anatomy.pdf`](diagrams/dataframe_anatomy.pdf)
and the loading workflow [`diagrams/loading_workflow.pdf`](diagrams/loading_workflow.pdf).

## Reading a CSV
```python
import pandas as pd

df = pd.read_csv("data/sales.csv")
df.head(3)
#    order_id   product  quantity  price month
# 0         1       Pen        10    1.5   Jan
# 1         2  Notebook         3    4.0   Jan
# 2         3       Pen         5    1.5   Feb
```

Useful options:
```python
pd.read_csv("file.csv", sep=";")                 # other separators
pd.read_csv("file.csv", usecols=["product", "price"])
pd.read_csv("file.csv", dtype={"order_id": str})
pd.read_csv("file.csv", na_values=["N/A", "-"])
pd.read_csv("file.csv", parse_dates=["date"])
```

## Other formats
```python
pd.read_excel("file.xlsx", sheet_name="Sheet1")   # needs openpyxl
pd.read_json("file.json")
df.to_csv("out.csv", index=False)                 # saving
```

## First inspection (always do this!)
```python
df.shape        # (8, 5)  -> rows, columns
df.dtypes       # type of each column
df.info()       # types + non-null counts
df.describe()   # count, mean, std, min, quartiles, max
df.isna().sum() # missing values per column
```

## Selecting data
```python
df["product"]                      # one column -> Series
df[["product", "price"]]           # several columns -> DataFrame
df.loc[0]                          # row by label
df.iloc[0:3]                       # rows by position
df[df["quantity"] > 5]             # filter rows
df[(df["product"] == "Pen") & (df["month"] == "Mar")]
```

## New columns and sorting
```python
df["revenue"] = df["quantity"] * df["price"]
df.sort_values("revenue", ascending=False).head(3)
```

## Exercises
1. Load `data/sales.csv` and print its shape and dtypes.
2. How many orders have a quantity of at least 6?
3. Add a `revenue` column and find the order with the highest revenue.
4. Save only the `Pen` orders to `pens.csv`.

Run the worked example: `python 03-data-loading/examples/load_sales.py`
