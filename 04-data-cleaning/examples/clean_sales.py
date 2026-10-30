from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_dirty.csv"

df = pd.read_csv(DATA)
print("Missing values per column:")
print(df.isna().sum(), end="\n\n")
print("Duplicated rows:", df.duplicated().sum(), end="\n\n")

# 1. Duplicates
df = df.drop_duplicates()

# 2. Inconsistent text: "notebook ", "PEN" -> "Notebook", "Pen"
df["product"] = df["product"].str.strip().str.title()

# 3. Missing values: fill price by the product's typical price,
#    quantity by the median
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))
df["quantity"] = df["quantity"].fillna(df["quantity"].median())

# 4. Invalid values: negative quantity is impossible -> drop
df = df[df["quantity"] > 0]

# 5. Outliers: IQR rule
q1, q3 = df["quantity"].quantile([0.25, 0.75])
upper = q3 + 1.5 * (q3 - q1)
print(f"Outlier threshold: quantity > {upper:.1f}")
print(df[df["quantity"] > upper], end="\n\n")
df = df[df["quantity"] <= upper]

# 6. Correct types
df["quantity"] = df["quantity"].astype(int)

print(df)
df.to_csv(DATA.with_name("sales_clean.csv"), index=False)
