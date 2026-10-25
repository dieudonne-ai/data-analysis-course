from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_messy.csv"
df = pd.read_csv(DATA)
print("Raw shape:", df.shape)
print("Missing per column:\n", df.isna().sum(), sep="")

# 1. duplicates
df = df.drop_duplicates()

# 2. inconsistent text
df["product"] = df["product"].str.strip().str.title()

# 3. impossible values: negative price -> missing
df.loc[df["price"] < 0, "price"] = pd.NA

# 4. missing values: fill with a sensible statistic per product
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))
df["quantity"] = df["quantity"].fillna(df["quantity"].median())

# 5. outliers with the IQR rule
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
mask = df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
print("Outliers removed:\n", df[~mask], sep="")
df = df[mask]

print("\nClean shape:", df.shape)
print(df)
