# Module 04 — Data Cleaning

Real data is messy. Cleaning typically takes most of an analyst's time.
Diagram: [`diagrams/cleaning_pipeline.pdf`](diagrams/cleaning_pipeline.pdf)

We use [`data/sales_messy.csv`](../data/sales_messy.csv), which contains a missing quantity,
`N/A` as a price, a duplicated row, inconsistent product names (`notebook `, `PEN`) and a negative quantity.

## 1. Find the problems
```python
df = pd.read_csv("data/sales_messy.csv", na_values=["N/A"])
df.isna().sum()          # quantity 1, price 1
df.duplicated().sum()    # 1
```

## 2. Missing values
```python
df.dropna(subset=["price"])                      # drop rows
df["quantity"].fillna(df["quantity"].median())   # fill with a statistic
df["price"].fillna(df.groupby("product")["price"].transform("median"))
```
Drop when few rows are affected; fill when the data is precious. Median is robust to outliers.

## 3. Duplicates
```python
df = df.drop_duplicates()                        # whole-row duplicates
df = df.drop_duplicates(subset=["order_id"])     # by key
```

## 4. Text and types
```python
df["product"] = df["product"].str.strip().str.title()   # " PEN" -> "Pen"
df["quantity"] = df["quantity"].astype(int)
df["date"] = pd.to_datetime(df["date"])
```

## 5. Invalid values
```python
df = df[df["quantity"] > 0]      # remove impossible quantities
```
Always document what you removed and why.

## Exercises
1. How many rows does the messy file have before and after cleaning?
2. Replace missing prices with the mean instead of the median. Does the result change?
3. Instead of removing the negative quantity, treat it as a return and keep it in a `returns` DataFrame.

Run the worked example: `python 04-data-cleaning/examples/clean_sales.py`
