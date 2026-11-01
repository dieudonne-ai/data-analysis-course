"""Basic charts on data/sales_eda.csv. Saves PNGs next to this script."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE.parents[1] / "data" / "sales_eda.csv")

# Bar chart: categories -> compare totals
by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
ax = by_product.plot.bar(color="#2563eb", title="Revenue by product")
ax.set_ylabel("Revenue")
plt.tight_layout(); plt.savefig(HERE / "bar_revenue.png"); plt.close()

# Histogram: distribution of one numeric variable
df["revenue"].plot.hist(bins=15, color="#60a5fa", edgecolor="white", title="Revenue distribution")
plt.xlabel("Revenue"); plt.tight_layout(); plt.savefig(HERE / "hist_revenue.png"); plt.close()

# Scatter: relationship between two numeric variables
df.plot.scatter(x="quantity", y="revenue", alpha=0.6, title="Quantity vs revenue")
plt.tight_layout(); plt.savefig(HERE / "scatter_qty_rev.png"); plt.close()

# Line: trend over ordered time
order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
monthly = df.groupby("month")["revenue"].sum().reindex(order).dropna()
monthly.plot(marker="o", title="Monthly revenue"); plt.ylabel("Revenue")
plt.tight_layout(); plt.savefig(HERE / "line_monthly.png"); plt.close()

print("Saved 4 charts in", HERE)
