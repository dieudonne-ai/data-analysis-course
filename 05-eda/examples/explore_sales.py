"""Exploratory data analysis on data/sales_eda.csv."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "data" / "sales_eda.csv")

print("Shape:", df.shape)
print(df.dtypes, "\n")
print(df.describe(), "\n")                      # count, mean, std, quartiles

# Univariate: one variable at a time
print(df["product"].value_counts(), "\n")
print("Skewness of revenue:", round(df["revenue"].skew(), 2))

# Outliers with the IQR rule
q1, q3 = df["revenue"].quantile([0.25, 0.75])
iqr = q3 - q1
outliers = df[(df["revenue"] < q1 - 1.5 * iqr) | (df["revenue"] > q3 + 1.5 * iqr)]
print(f"IQR outliers: {len(outliers)} of {len(df)} rows\n")

# Bivariate: relationships between variables
print(df.groupby("product")["revenue"].agg(["count", "sum", "mean"]).round(1), "\n")
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
print(df.groupby("month")["revenue"].sum().reindex(month_order), "\n")
print(df[["quantity", "price", "revenue"]].corr().round(2))
