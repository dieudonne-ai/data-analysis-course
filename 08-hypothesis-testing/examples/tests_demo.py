from pathlib import Path

import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "students.csv")

# 1. Two groups: do girls and boys score differently?
f = df.loc[df["gender"] == "F", "score"]
m = df.loc[df["gender"] == "M", "score"]
t, p = stats.ttest_ind(f, m, equal_var=False)
print(f"t-test F vs M: t={t:.2f}, p={p:.3f}")

# 2. Three groups: does the mean score differ by track?
groups = [g["score"] for _, g in df.groupby("track")]
F, p = stats.f_oneway(*groups)
print(f"ANOVA by track: F={F:.2f}, p={p:.3f}")

# 3. Two categorical variables: is track related to gender?
table = pd.crosstab(df["track"], df["gender"])
chi2, p, dof, _ = stats.chi2_contingency(table)
print(f"Chi-square track x gender: chi2={chi2:.2f}, p={p:.3f}")

# 4. Correlation test
r, p = stats.pearsonr(df["study_hours"], df["score"])
print(f"Pearson study_hours vs score: r={r:.2f}, p={p:.2g}")
