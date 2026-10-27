from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_messy.csv"

df = pd.read_csv(DATA, na_values=["N/A"])
print("Missing values per column:")
print(df.isna().sum(), end="\n\n")

df = df.drop_duplicates()
df["product"] = df["product"].str.strip().str.title()
df["quantity"] = df["quantity"].fillna(df["quantity"].median())
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))
df = df[df["quantity"] > 0]

print("Clean data:")
print(df)
df.to_csv(DATA.with_name("sales_clean.csv"), index=False)
