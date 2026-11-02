"""Descriptive statistics, z-scores, correlation and a confidence interval on sales_eda.csv."""
from pathlib import Path

import numpy as np
import pandas as pd

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "sales_eda.csv")
r = df["revenue"]

print("== Center & spread ==")
print(f"mean={r.mean():.2f} median={r.median():.2f} std={r.std():.2f}")
q1, q3 = r.quantile([.25, .75])
print(f"IQR={q3 - q1:.2f}  skew={r.skew():.2f}  (mean>median and skew>0 => right-skewed)")

print("\n== Z-scores ==")
z = (r - r.mean()) / r.std()
print("share within 1/2/3 std:", [round((z.abs() <= k).mean(), 3) for k in (1, 2, 3)])
print("outliers (|z|>3):", int((z.abs() > 3).sum()))

print("\n== Correlation ==")
print(df[["quantity", "price", "revenue"]].corr().round(2))

print("\n== 95% confidence interval for mean revenue ==")
se = r.std() / np.sqrt(len(r))
print(f"{r.mean():.2f} +/- {1.96 * se:.2f}  ->  ({r.mean() - 1.96 * se:.2f}, {r.mean() + 1.96 * se:.2f})")

print("\n== CLT demo: means of 30-order samples ==")
rng = np.random.default_rng(0)
means = [r.sample(30, random_state=int(s)).mean() for s in rng.integers(0, 10**6, 500)]
print(f"std of raw data={r.std():.2f}; std of sample means={np.std(means):.2f} (~ std/sqrt(30)={r.std()/np.sqrt(30):.2f})")
