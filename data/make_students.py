"""Generate data/students.csv (synthetic, reproducible)."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 200
study = rng.normal(10, 3, n).clip(0, 20).round(1)
sleep = rng.normal(7, 1, n).clip(4, 10).round(1)
score = (35 + 2.5 * study + 1.5 * sleep + rng.normal(0, 6, n)).clip(0, 100).round(1)
df = pd.DataFrame({
    "student_id": range(1, n + 1),
    "gender": rng.choice(["F", "M"], n),
    "track": rng.choice(["Science", "Arts", "Business"], n, p=[0.4, 0.3, 0.3]),
    "study_hours": study,
    "sleep_hours": sleep,
    "score": score,
})
df.to_csv(Path(__file__).with_name("students.csv"), index=False)
