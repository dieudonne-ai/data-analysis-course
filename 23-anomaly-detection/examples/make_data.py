"""Create data/daily_orders.csv: one year of daily orders for an online shop, with known incidents."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(23)
days = pd.date_range("2025-01-01", periods=365, freq="D")
weekday = days.day_of_week.to_numpy()
trend = np.linspace(200, 240, len(days))
weekly = np.where(weekday >= 5, 60, 0)                      # weekends are busier: +60 orders
orders = trend + weekly + rng.normal(0, 12, len(days))
basket = 40 + 0.08 * (orders - 220) + rng.normal(0, 1.5, len(days))   # busy (weekend) days: bigger family baskets

incident = np.zeros(len(days), int)
events = {
    "2025-02-14": ("orders", +150),     # Valentine's promo spike
    "2025-04-03": ("orders", -170),     # payment provider outage
    "2025-06-09": ("orders", +75),      # Monday spike: normal for a Saturday, odd for a Monday
    "2025-08-20": ("bot", None),        # bot traffic: weekend-like orders but a weekday-sized basket
    "2025-10-07": ("basket", +14),      # pricing bug: baskets too expensive
    "2025-11-28": ("orders", +210),     # Black Friday
}
for d, (kind, size) in events.items():
    i = days.get_loc(pd.Timestamp(d))
    incident[i] = 1
    if kind == "orders":
        orders[i] += size
    elif kind == "basket":
        basket[i] += size
    else:
        orders[i] += 55; basket[i] = 38.0      # each value alone looks plausible, the combination does not

out = pd.DataFrame({"date": days.strftime("%Y-%m-%d"), "weekday": days.day_name().str[:3],
                    "orders": orders.round().astype(int), "avg_basket": basket.round(2), "incident": incident})
out.to_csv(Path(__file__).resolve().parents[2] / "data" / "daily_orders.csv", index=False)
print(out.describe().round(1))
