"""Time series basics on data/monthly_sales.csv: trend, moving average, seasonality, naive forecast."""
from pathlib import Path

import numpy as np
import pandas as pd

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "monthly_sales.csv", parse_dates=["month"])
s = df.set_index("month")["revenue"]

print("== 1. Moving average (window=12) ==")
ma = s.rolling(12, center=True).mean()
print(ma.dropna().round(1).iloc[[0, 12, -1]])

print("\n== 2. Trend: linear fit on time index ==")
t = np.arange(len(s))
slope, intercept = np.polyfit(t, s.to_numpy(), 1)
print(f"revenue = {intercept:.1f} + {slope:.2f} * month_index   (about +{slope:.1f} per month)")

print("\n== 3. Seasonality: average detrended value per calendar month ==")
detrended = s - (intercept + slope * t)
seasonal = detrended.groupby(s.index.month).mean()
print(seasonal.round(1).to_string())
resid = detrended - seasonal.reindex(s.index.month).to_numpy()
print(f"residual std = {resid.std():.2f}  (noise left after trend + season)")

print("\n== 4. Forecast next 6 months: trend + season, vs naive 'same as last month' ==")
train, test = s.iloc[:-6], s.iloc[-6:]
tt = np.arange(len(train))
b, a = np.polyfit(tt, train.to_numpy(), 1)
seas = (train - (a + b * tt)).groupby(train.index.month).mean()
ft = np.arange(len(train), len(s))
model = a + b * ft + seas.reindex(test.index.month).to_numpy()
naive = np.full(6, train.iloc[-1])
mae = lambda p: np.abs(test.to_numpy() - p).mean()
print(f"MAE trend+season = {mae(model):.2f}   MAE naive = {mae(naive):.2f}")
