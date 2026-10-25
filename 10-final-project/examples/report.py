"""End-to-end template: load -> clean -> explore -> test -> model -> report.md"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent / "output"
out.mkdir(exist_ok=True)

# 1. Load
df = pd.read_csv(ROOT / "data" / "customers.csv")

# 2. Clean
df = df.drop_duplicates("customer_id").dropna()
df["city"] = df["city"].str.strip().str.title()

# 3. Explore
by_city = df.groupby("city")["spend"].mean().round(1).sort_values(ascending=False)

# 4. Test
a, b = (df.loc[df["group"] == g, "spend"] for g in ("A", "B"))
t, p = stats.ttest_ind(b, a, equal_var=False)

# 5. Model
r = stats.linregress(df["income"], df["spend"])

# 6. Report
lines = [
    "# Customer spend report", "",
    f"- Customers analysed: **{len(df)}**",
    f"- Mean spend: **{df['spend'].mean():.1f}**", "",
    "## Spend by city", "", "| city | mean spend |", "|---|---|", *[f"| {c} | {v} |" for c, v in by_city.items()], "",
    "## A/B test", "",
    f"Group B spends {b.mean() - a.mean():.1f} more than A (t = {t:.2f}, p = {p:.4f}).",
    "The difference is " + ("statistically significant." if p < .05 else "not significant."), "",
    "## Model", "",
    f"spend = {r.intercept:.1f} + {r.slope:.3f} x income (R^2 = {r.rvalue**2:.2f}).", "",
    "## Recommendation", "",
    "Roll out the new page (group B) and focus acquisition on higher-income segments.",
]
(out / "report.md").write_text("\n".join(lines))
print("\n".join(lines))
