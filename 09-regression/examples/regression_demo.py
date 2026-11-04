"""Simple and multiple linear regression on sales_eda.csv, with numpy only (no sklearn)."""
from pathlib import Path

import numpy as np
import pandas as pd

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "sales_eda.csv")

print("== 1. Simple regression: revenue ~ quantity ==")
x, y = df["quantity"].to_numpy(float), df["revenue"].to_numpy(float)
slope, intercept = np.polyfit(x, y, 1)
pred = intercept + slope * x
ss_res, ss_tot = ((y - pred) ** 2).sum(), ((y - y.mean()) ** 2).sum()
r2 = 1 - ss_res / ss_tot
print(f"revenue = {intercept:.2f} + {slope:.2f} * quantity   R^2 = {r2:.3f}")
print(f"RMSE = {np.sqrt(ss_res / len(y)):.2f}")

print("\n== 2. Multiple regression: revenue ~ quantity + price ==")
X = np.column_stack([np.ones(len(df)), df["quantity"], df["price"]])
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
pred2 = X @ beta
r2b = 1 - ((y - pred2) ** 2).sum() / ss_tot
print(f"intercept={beta[0]:.2f}, quantity={beta[1]:.2f}, price={beta[2]:.2f}   R^2 = {r2b:.3f}")

print("\n== 3. Train/test split: does it generalise? ==")
rng = np.random.default_rng(42)
idx = rng.permutation(len(df)); cut = int(.7 * len(df))
tr, te = idx[:cut], idx[cut:]
b, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
rmse = lambda i: np.sqrt(((y[i] - X[i] @ b) ** 2).mean())
print(f"train RMSE = {rmse(tr):.2f}   test RMSE = {rmse(te):.2f}")

print("\n== 4. Residual check ==")
res = y - pred2
print(f"mean residual = {res.mean():.4f}, std = {res.std():.2f}")
print("Corr(residual, fitted) =", round(float(np.corrcoef(res, pred2)[0, 1]), 4), "(should be ~0)")

print("\n== 5. Predict a new order: quantity=4, price=25 ==")
print(f"predicted revenue = {beta @ [1, 4, 25]:.2f}")
