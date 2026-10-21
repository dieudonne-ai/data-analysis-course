from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales.csv"

df = pd.read_csv(DATA)
print("Shape:", df.shape)
print(df.dtypes, end="\n\n")

df["revenue"] = df["quantity"] * df["price"]
print("Orders with quantity >= 6:")
print(df[df["quantity"] >= 6], end="\n\n")

print("Top 3 orders by revenue:")
print(df.sort_values("revenue", ascending=False).head(3))
