"""A/B test analysis: conversion rates, z-test, confidence interval, required sample size."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "ab_test.csv")

print("== 1. Conversion rate per group ==")
g = df.groupby("group")["converted"].agg(n="size", conversions="sum", rate="mean")
print(g.round(4))

a, b = g.loc["A"], g.loc["B"]
diff = b.rate - a.rate
print(f"\nabsolute lift = {diff:.4f}  relative lift = {diff / a.rate:.1%}")

print("\n== 2. Two-proportion z-test ==")
pooled = (a.conversions + b.conversions) / (a.n + b.n)
se = np.sqrt(pooled * (1 - pooled) * (1 / a.n + 1 / b.n))
z = diff / se
p_value = 2 * (1 - stats.norm.cdf(abs(z)))
print(f"z = {z:.2f}  p-value = {p_value:.4f}  -> {'significant' if p_value < 0.05 else 'not significant'} at 5%")

print("\n== 3. 95% confidence interval for the lift ==")
se_diff = np.sqrt(a.rate * (1 - a.rate) / a.n + b.rate * (1 - b.rate) / b.n)
print(f"lift in [{diff - 1.96 * se_diff:.4f}, {diff + 1.96 * se_diff:.4f}]")

print("\n== 4. Sample size per group to detect 10% -> 12.5% (power 80%, alpha 5%) ==")
p1, p2 = 0.10, 0.125
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
n_req = ((za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))) / (p2 - p1) ** 2
print(f"about {int(np.ceil(n_req))} visitors per group")
