"""Clean data/sales_messy.csv step by step."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

df = pd.read_csv(ROOT / "data" / "sales_messy.csv", na_values=["N/A"])
print("Missing values per column:\n", df.isna().sum(), "\n")

df = df.drop_duplicates()                                   # 1. duplicates
df["product"] = df["product"].str.strip().str.title()       # 2. inconsistent text
df = df[df["quantity"].isna() | (df["quantity"] > 0)]    # 3. impossible values (keep NaN)
df["quantity"] = df["quantity"].fillna(df["quantity"].median())  # 4. missing numbers
df = df.dropna(subset=["price"])                            # 5. unusable rows
df["quantity"] = df["quantity"].astype(int)                 # 6. correct dtype
df["revenue"] = df["quantity"] * df["price"]

print(df)
df.to_csv(ROOT / "data" / "sales_clean.csv", index=False)
