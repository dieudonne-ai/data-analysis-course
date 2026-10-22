from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_dirty.csv"

df = pd.read_csv(DATA, na_values=["N/A"])
print("Missing values per column:")
print(df.isna().sum(), end="\n\n")

# 1. Duplicates
df = df.drop_duplicates()

# 2. Inconsistent text
df["product"] = df["product"].str.strip().str.title()

# 3. Missing values: fill quantity with the median, drop rows with no price
df["quantity"] = df["quantity"].fillna(df["quantity"].median())
df = df.dropna(subset=["price"])

# 4. Outliers: IQR rule
q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
mask = df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
print("Outliers removed:")
print(df[~mask], end="\n\n")
df = df[mask]

# 5. Fix types
df["quantity"] = df["quantity"].astype(int)

print(df)
print("\nShape after cleaning:", df.shape)
