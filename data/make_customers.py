"""Generate data/customers.csv - a synthetic dataset (seeded, reproducible)."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 200
age = rng.integers(18, 70, n)
city = rng.choice(["Kampala", "Nairobi", "Kigali", "Dar es Salaam"], n, p=[.35, .3, .2, .15])
group = rng.choice(["A", "B"], n)                      # A/B test group
visits = rng.poisson(6, n) + (group == "B") * 1
income = 300 + 12 * age + rng.normal(0, 120, n)
spend = 20 + 0.08 * income + 4 * visits + (group == "B") * 15 + rng.normal(0, 25, n)

df = pd.DataFrame({"customer_id": range(1, n + 1), "age": age, "city": city,
                   "group": group, "visits": visits, "income": income.round(0),
                   "spend": spend.round(2)})
df.to_csv(Path(__file__).with_name("customers.csv"), index=False)
print(df.head())
