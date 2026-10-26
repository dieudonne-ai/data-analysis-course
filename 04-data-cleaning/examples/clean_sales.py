"""Clean data/sales_dirty.csv step by step (run from the repo root)."""
import pandas as pd

df = pd.read_csv("data/sales_dirty.csv", na_values=["N/A"])
print("Raw shape:", df.shape)
print(df.isna().sum(), "\n")

# 1. Remove exact duplicate rows
df = df.drop_duplicates()

# 2. Fix text: strip spaces, unify case
df["customer"] = df["customer"].str.strip().str.title()
df["product"] = df["product"].str.strip().str.title()

# 3. Fix types: invalid dates become NaT instead of crashing
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# 4. Invalid values: quantity must be positive -> treat others as missing
df.loc[df["quantity"] <= 0, "quantity"] = pd.NA

# 5. Missing values: fill price with the median price of the same product
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))
df["quantity"] = df["quantity"].fillna(df["quantity"].median())

# 6. Outliers: IQR rule
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
mask = df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
print("Outliers removed:\n", df[~mask][["order_id", "quantity"]], "\n")
df = df[mask]

# 7. Drop rows still missing a date, then save
df = df.dropna(subset=["order_date"])
df.to_csv("data/sales_clean.csv", index=False)
print("Clean shape:", df.shape)
print(df)
