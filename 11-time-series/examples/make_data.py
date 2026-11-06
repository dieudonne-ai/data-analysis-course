"""Create data/monthly_sales.csv: 36 months of synthetic sales (trend + yearly season + noise)."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
months = pd.date_range("2023-01-01", periods=36, freq="MS")
t = np.arange(36)
season = 12 * np.sin(2 * np.pi * (t - 8) / 12)          # peak in November/December
revenue = 100 + 2.5 * t + season + rng.normal(0, 4, 36)
out = pd.DataFrame({"month": months.strftime("%Y-%m"), "revenue": revenue.round(1)})
out.to_csv(Path(__file__).resolve().parents[2] / "data" / "monthly_sales.csv", index=False)
print(out.head())
