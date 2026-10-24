from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_messy.csv"

df = pd.read_csv(DATA, na_values=["N/A"])
print("Missing values:\n", df.isna().sum(), sep="")
print("Duplicates:", df.duplicated().sum(), end="\n\n")

df = df.drop_duplicates()
df["customer"] = df["customer"].str.strip().str.title()
df["city"] = df["city"].str.title().fillna("Unknown")
df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
df["quantity"] = df["quantity"].fillna(df["quantity"].median())
df["price"] = df["price"].fillna(df.groupby("product")["price"].transform("median"))

q1, q3 = df["quantity"].quantile([0.25, 0.75])
iqr = q3 - q1
outliers = ~df["quantity"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
print("Outliers:\n", df[outliers], sep="", end="\n\n")

df["revenue"] = df["quantity"] * df["price"]
print(df.groupby("city")["revenue"].sum())
