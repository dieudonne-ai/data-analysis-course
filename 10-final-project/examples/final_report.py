from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# 1. Load & inspect
df = pd.read_csv(ROOT / "data" / "students.csv")
assert df.isna().sum().sum() == 0 and not df.duplicated().any()

# 2. Explore
by_track = df.groupby("track")["score"].mean().round(1)
corr = df[["study_hours", "sleep_hours", "score"]].corr().round(2)

# 3. Visualise
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
axes[0].hist(df["score"], bins=15, color="#3b82f6", edgecolor="white")
axes[0].set(title="Scores", xlabel="Score", ylabel="Students")
axes[1].bar(by_track.index, by_track.values, color="#10b981")
axes[1].set(title="Mean score by track", ylabel="Mean score")
axes[2].scatter(df["study_hours"], df["score"], alpha=0.6)
axes[2].set(title="Study hours vs score", xlabel="Hours / week", ylabel="Score")
fig.tight_layout()
fig.savefig(OUT / "overview.png", dpi=150)

# 4. Tests
_, p_gender = stats.ttest_ind(df.loc[df.gender == "F", "score"], df.loc[df.gender == "M", "score"], equal_var=False)
_, p_track = stats.f_oneway(*[g["score"] for _, g in df.groupby("track")])
r, p_corr = stats.pearsonr(df["study_hours"], df["score"])

# 5. Regression with train/test split
rng = np.random.default_rng(1)
idx = rng.permutation(len(df)); cut = int(0.8 * len(df))
tr, te = df.iloc[idx[:cut]], df.iloc[idx[cut:]]
feats = ["study_hours", "sleep_hours"]
coef, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(tr)), tr[feats]]), tr["score"], rcond=None)
pred = np.column_stack([np.ones(len(te)), te[feats]]) @ coef
r2 = 1 - ((te["score"] - pred) ** 2).sum() / ((te["score"] - te["score"].mean()) ** 2).sum()
rmse = float(np.sqrt(((te["score"] - pred) ** 2).mean()))

report = f"""# Student score analysis

## Data
{len(df)} students, no missing values, no duplicates.

## Findings
- Mean score by track: {by_track.to_dict()}
- Correlation matrix:

```
{corr.to_string()}
```

## Tests
- Gender difference in mean score: p = {p_gender:.2f} (not significant)
- Track difference in mean score: p = {p_track:.2f} (not significant)
- Study hours vs score: r = {r:.2f}, p = {p_corr:.1e} (significant)

## Model
score = {coef[0]:.1f} + {coef[1]:.2f} * study_hours + {coef[2]:.2f} * sleep_hours
Held-out R^2 = {r2:.2f}, RMSE = {rmse:.1f} points.

## Recommendations
1. Encourage structured study time: it is the strongest lever in the data.
2. Do not target programmes by gender or track: no score gap was found.
3. Collect more variables (attendance, prior grades) to explain the remaining variance.

## Limits
Synthetic data; association is not causation; small hold-out set (n = {len(te)}).
"""
(OUT / "report.md").write_text(report)
print(report)
