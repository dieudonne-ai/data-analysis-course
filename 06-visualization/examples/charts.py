"""Create five basic charts from customers.csv and save them as PDF in output/."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent / "output"
out.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "data" / "customers.csv")

# 1. bar chart - compare categories
fig, ax = plt.subplots()
df.groupby("city")["spend"].mean().sort_values().plot.barh(ax=ax, color="#3b82f6")
ax.set_title("Average spend by city"); ax.set_xlabel("spend")
fig.savefig(out / "bar_spend_by_city.pdf", bbox_inches="tight")

# 2. histogram - distribution
fig, ax = plt.subplots()
ax.hist(df["age"], bins=10, color="#10b981", ec="white")
ax.set_title("Age distribution"); ax.set_xlabel("age"); ax.set_ylabel("customers")
fig.savefig(out / "hist_age.pdf", bbox_inches="tight")

# 3. scatter - relationship
fig, ax = plt.subplots()
ax.scatter(df["income"], df["spend"], s=14, alpha=.6)
ax.set_title("Income vs spend"); ax.set_xlabel("income"); ax.set_ylabel("spend")
fig.savefig(out / "scatter_income_spend.pdf", bbox_inches="tight")

# 4. box plot - compare distributions
fig, ax = plt.subplots()
df.boxplot(column="spend", by="group", ax=ax, grid=False)
ax.set_title("Spend by A/B group"); fig.suptitle("")
fig.savefig(out / "box_spend_by_group.pdf", bbox_inches="tight")

# 5. line chart - trend over time (monthly sales from sales.csv)
sales = pd.read_csv(ROOT / "data" / "sales.csv")
sales["revenue"] = sales["quantity"] * sales["price"]
monthly = sales.groupby("month", sort=False)["revenue"].sum()
fig, ax = plt.subplots()
monthly.plot(marker="o", ax=ax)
ax.set_title("Monthly revenue"); ax.set_ylabel("revenue")
fig.savefig(out / "line_monthly_revenue.pdf", bbox_inches="tight")

print("Saved:", *sorted(p.name for p in out.glob("*.pdf")), sep="\n  ")
