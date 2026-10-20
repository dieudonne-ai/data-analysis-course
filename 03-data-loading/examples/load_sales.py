"""Load data/sales.csv with pandas and inspect it."""
from pathlib import Path
import pandas as pd

path = Path(__file__).resolve().parents[2] / "data" / "sales.csv"
df = pd.read_csv(path)

print(df.head(3))
print(df.dtypes)
print(df.describe())

# Selecting
print(df["price"].mean())
print(df[df["quantity"] > 5])

# New column and grouping
df["revenue"] = df["quantity"] * df["price"]
print(df.groupby("product")["revenue"].sum().sort_values(ascending=False))
