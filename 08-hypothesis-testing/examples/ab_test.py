from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "customers.csv")
a = df.loc[df["group"] == "A", "spend"]
b = df.loc[df["group"] == "B", "spend"]

print("H0: mean spend is the same in groups A and B")
print("H1: mean spend differs\n")
print(f"A: n={len(a)} mean={a.mean():.1f}   B: n={len(b)} mean={b.mean():.1f}")

# Welch two-sample t-test
t, p = stats.ttest_ind(b, a, equal_var=False)
print(f"\nt-test: t={t:.2f}, p-value={p:.4f}")
print("Reject H0 at alpha=0.05" if p < 0.05 else "Cannot reject H0 at alpha=0.05")

# effect size (Cohen's d) - how big, not just whether
pooled = np.sqrt((a.var() + b.var()) / 2)
print(f"Cohen's d = {(b.mean() - a.mean()) / pooled:.2f}")

# chi-square test: are city and group independent?
table = pd.crosstab(df["city"], df["group"])
chi2, p2, dof, _ = stats.chi2_contingency(table)
print(f"\nchi-square (city vs group): chi2={chi2:.2f}, dof={dof}, p-value={p2:.3f}")
