from pathlib import Path

import pandas as pd

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "customers.csv")

print("--- Shape & types ---")
print(df.shape); print(df.dtypes, end="\n\n")

print("--- Univariate: numeric ---")
print(df[["age", "visits", "income", "spend"]].describe().round(1), end="\n\n")

print("--- Univariate: categorical ---")
print(df["city"].value_counts(normalize=True).round(2), end="\n\n")

print("--- Bivariate: spend by city ---")
print(df.groupby("city")["spend"].agg(["count", "mean", "median"]).round(1), end="\n\n")

print("--- Correlation matrix ---")
print(df[["age", "visits", "income", "spend"]].corr().round(2), end="\n\n")

print("--- Pivot: mean spend, city x group ---")
print(df.pivot_table(values="spend", index="city", columns="group", aggfunc="mean").round(1))
