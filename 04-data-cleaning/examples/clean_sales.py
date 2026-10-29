from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_messy.csv"

df = pd.read_csv(DATA)
print("Raw data:", df.shape)
print("Missing values:\n", df.isna().sum(), end="\n\n")
print("Duplicated rows:", df.duplicated().sum(), end="\n\n")

# 1. Duplicates
df = df.drop_duplicates()

# 2. Inconsistent text: " notebook " / "PEN" -> "Notebook" / "Pen"
df["product"] = df["product"].str.strip().str.title()

# 3. Missing values: fill quantity with the median, price with the product's usual price
df["quantity"] = df["quantity"].fillna(df["quantity"].median())
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))

# 4. Outliers: IQR rule
q1, q3 = df["quantity"].quantile([0.25, 0.75])
upper = q3 + 1.5 * (q3 - q1)
print(f"Outlier threshold (IQR): quantity > {upper:.1f}")
print(df[df["quantity"] > upper], end="\n\n")
df = df[df["quantity"] <= upper]

# 5. Fix types
df["quantity"] = df["quantity"].astype(int)

print("Clean data:", df.shape)
print(df)
