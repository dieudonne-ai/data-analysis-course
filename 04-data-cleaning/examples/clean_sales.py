"""Clean data/messy_sales.csv step by step (run from the repo root)."""
import pandas as pd

df = pd.read_csv("data/messy_sales.csv", na_values=["N/A"])
print("Raw shape:", df.shape)
print(df.isna().sum(), end="\n\n")

# 1. Duplicates
df = df.drop_duplicates()

# 2. Text: trim spaces and unify case
df["customer"] = df["customer"].str.strip().str.title()
df["product"] = df["product"].str.strip().str.title()

# 3. Types: invalid dates become NaT instead of crashing
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# 4. Invalid values: a negative price is impossible -> missing
df.loc[df["price"] < 0, "price"] = pd.NA

# 5. Outliers with the IQR rule
q1, q3 = df["price"].quantile([0.25, 0.75])
iqr = q3 - q1
df["price_outlier"] = (df["price"] < q1 - 1.5 * iqr) | (df["price"] > q3 + 1.5 * iqr)

# 6. Missing values: fill quantity with the median, drop rows without price
df["quantity"] = df["quantity"].fillna(df["quantity"].median())
df = df.dropna(subset=["price"])

print("Clean shape:", df.shape)
print(df)
df.to_csv("data/clean_sales.csv", index=False)
