from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "customers.csv")

# --- simple linear regression: spend ~ income ---
res = stats.linregress(df["income"], df["spend"])
print(f"spend = {res.intercept:.1f} + {res.slope:.3f} * income")
print(f"R^2 = {res.rvalue**2:.2f}, p-value of slope = {res.pvalue:.2g}")
print(f"-> +100 income is associated with +{res.slope * 100:.1f} spend\n")

# --- multiple regression with numpy least squares ---
X = np.column_stack([np.ones(len(df)), df["income"], df["visits"], (df["group"] == "B").astype(int)])
y = df["spend"].to_numpy()
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
pred = X @ beta
r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
for name, b in zip(["intercept", "income", "visits", "group B"], beta):
    print(f"{name:>10}: {b:8.3f}")
print(f"R^2 (multiple) = {r2:.2f}")

# --- honest evaluation: train/test split ---
rng = np.random.default_rng(1)
idx = rng.permutation(len(df)); cut = int(.8 * len(df))
tr, te = idx[:cut], idx[cut:]
b_tr, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
rmse = np.sqrt(((y[te] - X[te] @ b_tr) ** 2).mean())
print(f"\nTest RMSE = {rmse:.1f} (std of spend is {y.std():.1f})")

# --- predict a new customer ---
new = np.array([1, 900, 8, 1])
print(f"Predicted spend: income 900, 8 visits, group B -> {new @ beta:.1f}")
