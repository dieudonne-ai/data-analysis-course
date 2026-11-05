"""End-to-end mini project on sales data: question -> clean -> explore -> test -> model -> conclude."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parents[2] / "data"

print("== 0. Question ==")
print("Does product mix drive revenue, and can we predict an order's revenue?")

print("\n== 1. Load and clean (module 03-04) ==")
raw = pd.read_csv(DATA / "sales_messy.csv")
print("raw shape:", raw.shape, "| missing cells:", int(raw.isna().sum().sum()), "| duplicates:", int(raw.duplicated().sum()))
df = pd.read_csv(DATA / "sales_eda.csv")
print("analysis dataset:", df.shape, "| missing:", int(df.isna().sum().sum()))

print("\n== 2. Explore (module 05-07) ==")
print(df[["quantity", "price", "revenue"]].describe().round(2).loc[["mean", "std", "min", "max"]])
by_prod = df.groupby("product")["revenue"].agg(["count", "mean", "sum"]).round(1).sort_values("sum", ascending=False)
print(by_prod)
print("Correlation with revenue:\n", df[["quantity", "price"]].corrwith(df["revenue"]).round(2))

print("\n== 3. Test (module 08): do products differ in mean revenue? ==")
groups = [g["revenue"].to_numpy() for _, g in df.groupby("product")]
f, p = stats.f_oneway(*groups)
print(f"ANOVA F={f:.2f}, p={p:.4g} ->", "reject H0" if p < .05 else "fail to reject H0")

print("\n== 4. Model (module 09): revenue ~ quantity + price ==")
y = df["revenue"].to_numpy(float)
X = np.column_stack([np.ones(len(df)), df["quantity"], df["price"]])
rng = np.random.default_rng(42)
idx = rng.permutation(len(df)); cut = int(.7 * len(df)); tr, te = idx[:cut], idx[cut:]
b, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
rmse = lambda i: np.sqrt(((y[i] - X[i] @ b) ** 2).mean())
r2 = 1 - ((y[te] - X[te] @ b) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum()
print(f"train RMSE={rmse(tr):.2f} test RMSE={rmse(te):.2f} test R^2={r2:.2f}")

print("\n== 5. Conclusion ==")
top = by_prod.index[0]
print(f"- Top product by total revenue: {top}.")
print(f"- Product means differ significantly: {p < .05}.")
print(f"- Quantity and price together explain {r2:.0%} of revenue variance on unseen orders.")
print("- Limits: one dataset, association not causation; next step = collect more months.")
