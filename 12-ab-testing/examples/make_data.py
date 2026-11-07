"""Generate data/ab_test.csv: 4000 visitors, control (A) vs new checkout button (B)."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(12)
n = 4000
group = rng.permutation(np.repeat(["A", "B"], n // 2))
p = np.where(group == "A", 0.10, 0.125)
converted = rng.random(n) < p
df = pd.DataFrame({"user_id": np.arange(1, n + 1), "group": group, "converted": converted.astype(int)})
df.to_csv(Path(__file__).resolve().parents[2] / "data" / "ab_test.csv", index=False)
print(df.groupby("group")["converted"].agg(["size", "sum", "mean"]))
