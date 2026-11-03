"""Hypothesis tests on sales_eda.csv: t-test, Mann-Whitney, chi-square, ANOVA, effect size."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "sales_eda.csv")
ALPHA = 0.05


def verdict(p):
    return "reject H0" if p < ALPHA else "fail to reject H0"


print("== 1. One-sample t-test: is mean revenue different from 40? ==")
t, p = stats.ttest_1samp(df["revenue"], 40)
print(f"t={t:.2f} p={p:.4f} -> {verdict(p)}")

print("\n== 2. Two-sample (Welch) t-test: Notebook vs Bag revenue ==")
a = df.loc[df["product"] == "Notebook", "revenue"]
b = df.loc[df["product"] == "Bag", "revenue"]
t, p = stats.ttest_ind(a, b, equal_var=False)
d = (a.mean() - b.mean()) / np.sqrt((a.var() + b.var()) / 2)
print(f"Notebook mean={a.mean():.1f}, Bag mean={b.mean():.1f}; t={t:.2f} p={p:.4g} -> {verdict(p)}; Cohen d={d:.2f}")

print("\n== 3. Mann-Whitney U (no normality assumption) ==")
u, p = stats.mannwhitneyu(a, b)
print(f"U={u:.0f} p={p:.4g} -> {verdict(p)}")

print("\n== 4. ANOVA: does mean revenue differ across products? ==")
groups = [g["revenue"].values for _, g in df.groupby("product")]
f, p = stats.f_oneway(*groups)
print(f"F={f:.2f} p={p:.4g} -> {verdict(p)}")

print("\n== 5. Chi-square: are product and month independent? ==")
table = pd.crosstab(df["product"], df["month"])
chi2, p, dof, _ = stats.chi2_contingency(table)
print(f"chi2={chi2:.1f} dof={dof} p={p:.4f} -> {verdict(p)}")

print("\n== 6. Multiple testing: 20 tests on pure noise ==")
rng = np.random.default_rng(0)
ps = [stats.ttest_ind(rng.normal(size=30), rng.normal(size=30)).pvalue for _ in range(20)]
print(f"'significant' at 0.05: {sum(p < ALPHA for p in ps)} of 20; with Bonferroni (0.05/20): {sum(p < ALPHA / 20 for p in ps)}")
