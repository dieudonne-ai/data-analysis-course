"""Turn monthly sales into a one-chart story and a short Markdown report."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
df = pd.read_csv(ROOT / "data" / "monthly_sales.csv")
print(df.head(), "\n")
xcol, ycol = df.columns[0], df.select_dtypes("number").columns[0]

first, last = df[ycol].iloc[0], df[ycol].iloc[-1]
change = (last - first) / first * 100
headline = f"{ycol.capitalize()} {'grew' if change >= 0 else 'fell'} {abs(change):.0f}% over the period"

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df[xcol], df[ycol], color="#cbd5e1", lw=2)
ax.plot(df[xcol].iloc[-1], last, "o", color="#1e3a8a", ms=9)      # highlight the key point
ax.annotate(f"{last:,.0f}", (df[xcol].iloc[-1], last), xytext=(5, 8), textcoords="offset points")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_title(headline, loc="left", weight="bold")
fig.savefig(OUT / "story_chart.png", dpi=120, bbox_inches="tight")

report = f"""# Sales update

**Context:** monthly {ycol} from `data/monthly_sales.csv`.

**Insight:** {headline} ({first:,.0f} -> {last:,.0f}).

**Action:** keep the channels behind the latest months; investigate any dip before budgeting.

![chart](story_chart.png)
"""
(OUT / "report.md").write_text(report)
print(report)
