"""Generate PDF diagrams for module 11 (time series)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "monthly_sales.csv", parse_dates=["month"])
s = df.set_index("month")["revenue"]
t = np.arange(len(s))
slope, intercept = np.polyfit(t, s.to_numpy(), 1)
trend = intercept + slope * t
seasonal_by_month = (s - trend).groupby(s.index.month).mean()
season = seasonal_by_month.reindex(s.index.month).to_numpy()
resid = s.to_numpy() - trend - season

# 1. Raw series with moving average and trend line
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(s.index, s, color="#94a3b8", marker="o", ms=4, label="monthly revenue")
ax.plot(s.index, s.rolling(12, center=True).mean(), color="#1e3a8a", lw=2.5, label="12-month moving average")
ax.plot(s.index, trend, color="#ef4444", ls="--", lw=2, label=f"linear trend (+{slope:.2f}/month)")
ax.set_ylabel("revenue"); ax.legend()
ax.set_title("Trend: the moving average smooths out the seasonal wave", weight="bold")
fig.savefig(OUT / "trend_ma.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Decomposition: observed = trend + season + residual
fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
for ax, y, name, c in zip(axs, (s.to_numpy(), trend, season, resid),
                          ("observed", "trend", "seasonal", "residual"),
                          ("#334155", "#ef4444", "#15803d", "#a16207")):
    ax.plot(s.index, y, color=c, lw=2); ax.set_ylabel(name)
axs[0].set_title("Decomposition: observed = trend + seasonal + residual", weight="bold")
fig.savefig(OUT / "decomposition.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Forecast vs naive on the last 6 months
train, test = s.iloc[:-6], s.iloc[-6:]
tt = np.arange(len(train)); b, a = np.polyfit(tt, train.to_numpy(), 1)
seas = (train - (a + b * tt)).groupby(train.index.month).mean()
ft = np.arange(len(train), len(s))
model = a + b * ft + seas.reindex(test.index.month).to_numpy()
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(train.index, train, color="#94a3b8", label="train")
ax.plot(test.index, test, color="#0f172a", marker="o", label="actual (held out)")
ax.plot(test.index, model, color="#15803d", marker="s", label="trend + season")
ax.plot(test.index, np.full(6, train.iloc[-1]), color="#ef4444", ls="--", label="naive: last value")
ax.axvline(test.index[0], color="k", lw=.8, ls=":"); ax.legend(); ax.set_ylabel("revenue")
ax.set_title("Forecast check: always compare with a naive baseline", weight="bold")
fig.savefig(OUT / "forecast.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Workflow
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
steps = ["1. Parse dates\n& sort", "2. Plot the\nseries", "3. Trend\n(rolling mean)", "4. Seasonality\n(group by month)", "5. Forecast\nvs baseline", "6. Split by\ntime, not random"]
for i, st in enumerate(steps):
    x = .9 + i * 1.84
    ax.add_patch(FancyBboxPatch((x - .8, 1.1), 1.6, .9, boxstyle="round,pad=.05", fc="#dbeafe", ec="#334155"))
    ax.text(x, 1.55, st, ha="center", va="center", fontsize=9)
    if i < len(steps) - 1:
        ax.annotate("", (x + 1.04, 1.55), (x + .84, 1.55), arrowprops=dict(arrowstyle="->"))
ax.text(5.5, .5, "Never shuffle time-ordered data: train on the past, test on the future.", ha="center", color="#b91c1c")
ax.set_title("Time series workflow", weight="bold")
fig.savefig(OUT / "workflow.pdf", bbox_inches="tight"); plt.close(fig)
