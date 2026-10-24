from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "students.csv")
s = df["score"]

print(f"mean={s.mean():.1f} median={s.median():.1f} std={s.std():.1f}")
z = (s - s.mean()) / s.std()
print("Share within 1 std:", round((z.abs() <= 1).mean(), 2), "(normal: 0.68)")
print("Share within 2 std:", round((z.abs() <= 2).mean(), 2), "(normal: 0.95)")

se = s.std() / np.sqrt(len(s))
lo, hi = stats.t.interval(0.95, len(s) - 1, loc=s.mean(), scale=se)
print(f"95% CI for the mean: [{lo:.1f}, {hi:.1f}]")

# Central limit theorem: means of samples are ~normal
rng = np.random.default_rng(0)
means = [rng.choice(df["study_hours"], 30).mean() for _ in range(1000)]
print(f"Sample means of 30: mean={np.mean(means):.2f}, std={np.std(means):.2f}, "
      f"theory={df['study_hours'].std() / np.sqrt(30):.2f}")
