from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "customers.csv")
x = df["spend"]

print("--- Central tendency & spread ---")
print(f"mean={x.mean():.1f} median={x.median():.1f} std={x.std():.1f} "
      f"IQR={x.quantile(.75) - x.quantile(.25):.1f}")

print("\n--- Normal distribution: the 68-95-99.7 rule ---")
for k in (1, 2, 3):
    share = x.between(x.mean() - k * x.std(), x.mean() + k * x.std()).mean()
    print(f"within {k} std: {share:.1%}")

print("\n--- Standard error & 95% confidence interval for the mean ---")
se = x.std() / np.sqrt(len(x))
lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=se)
print(f"mean = {x.mean():.1f}, SE = {se:.2f}, 95% CI = [{lo:.1f}, {hi:.1f}]")

print("\n--- Central limit theorem: means of 30-customer samples ---")
rng = np.random.default_rng(0)
means = [x.sample(30, random_state=int(s)).mean() for s in rng.integers(0, 10**6, 1000)]
print(f"mean of sample means = {np.mean(means):.1f}, std of sample means = {np.std(means):.2f} "
      f"(theory: {x.std() / np.sqrt(30):.2f})")

print("\n--- Probability: P(spend > 150) ---")
print(f"observed: {(x > 150).mean():.1%}   normal model: {1 - stats.norm.cdf(150, x.mean(), x.std()):.1%}")
