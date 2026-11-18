"""Anomaly detection on one year of daily orders: z-score, IQR, robust MAD, seasonal residuals, Mahalanobis."""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "daily_orders.csv"
df = pd.read_csv(DATA, parse_dates=["date"])
orders = df["orders"].to_numpy(float)
truth = df["incident"].to_numpy(bool)


def zscore(x):
    return (x - x.mean()) / x.std()


def iqr_flags(x, k=1.5):
    q1, q3 = np.percentile(x, [25, 75])
    lo, hi = q1 - k * (q3 - q1), q3 + k * (q3 - q1)
    return (x < lo) | (x > hi), (lo, hi)


def robust_z(x):
    """Like a z-score, but with median and MAD, which a few outliers cannot drag around."""
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return (x - med) / (1.4826 * mad)          # 1.4826 makes MAD comparable to a std for normal data


def seasonal_residual(df, window=29):
    """Remove the trend (rolling median) and the weekday pattern, keep what is left."""
    trend = df["orders"].rolling(window, center=True, min_periods=1).median()
    detrended = df["orders"] - trend
    weekday_effect = detrended.groupby(df["weekday"]).transform("median")
    return (detrended - weekday_effect).to_numpy()


def mahalanobis(X):
    """Distance from the centre that accounts for the correlation between columns."""
    mu = X.mean(axis=0)
    cov_inv = np.linalg.inv(np.cov(X, rowvar=False))
    d = X - mu
    return np.sqrt(np.einsum("ij,jk,ik->i", d, cov_inv, d))


def score(flags, name):
    tp = int((flags & truth).sum()); fp = int((flags & ~truth).sum()); fn = int((~flags & truth).sum())
    prec = tp / max(tp + fp, 1); rec = tp / (tp + fn)
    print(f"{name:<32} flagged {flags.sum():>3}  caught {tp}/{truth.sum()}  false alarms {fp:>2}"
          f"  precision {prec:.2f}  recall {rec:.2f}")
    return prec, rec


def show(flags):
    for _, r in df[flags].iterrows():
        tag = "INCIDENT" if r["incident"] else "normal"
        print(f"     {r['date'].date()} {r['weekday']} orders={r['orders']:>3} basket={r['avg_basket']:.2f}  [{tag}]")


if __name__ == "__main__":
    print(f"{len(df)} days, {truth.sum()} known incidents\n")

    print("1) classic z-score on orders, |z| > 3")
    z = zscore(orders)
    print(f"   mean {orders.mean():.1f}, std {orders.std():.1f}")
    score(np.abs(z) > 3, "z-score |z|>3"); show(np.abs(z) > 3)
    clean = orders[~truth]
    print(f"   std WITHOUT the incidents would be {clean.std():.1f}: outliers inflate the std (masking)\n")

    print("2) IQR fences (Tukey's box-plot rule)")
    f, (lo, hi) = iqr_flags(orders)
    print(f"   fences [{lo:.0f}, {hi:.0f}]")
    score(f, "IQR k=1.5"); show(f)
    print()

    print("3) robust z-score (median / MAD), |z| > 3.5")
    rz = robust_z(orders)
    score(np.abs(rz) > 3.5, "robust z |z|>3.5"); show(np.abs(rz) > 3.5)
    print()

    print("4) seasonal residuals: remove trend + weekday pattern, then robust z")
    res = seasonal_residual(df)
    rres = robust_z(res)
    score(np.abs(rres) > 3.5, "seasonal robust z |z|>3.5"); show(np.abs(rres) > 3.5)
    print()

    print("5) multivariate: orders AND basket together (Mahalanobis distance)")
    X = df[["orders", "avg_basket"]].to_numpy(float)
    zb = np.abs(zscore(X[:, 1]))
    i_bot = np.where(df["date"] == "2025-08-20")[0][0]
    print(f"   bot day 2025-08-20: z(orders) {z[i_bot]:+.2f}, z(basket) {zscore(X[:, 1])[i_bot]:+.2f} -> unremarkable one column at a time")
    md = mahalanobis(X)
    print(f"   Mahalanobis distance of the bot day: {md[i_bot]:.2f}  (99th percentile of all days: {np.percentile(md, 99):.2f})")
    score(md > 3.5, "Mahalanobis > 3.5"); show(md > 3.5)
    print()

    print("6) combine: seasonal residual of orders + Mahalanobis on (residual, basket residual)")
    bres = (df["avg_basket"] - df["avg_basket"].rolling(29, center=True, min_periods=1).median()).to_numpy()
    md2 = mahalanobis(np.column_stack([res, bres]))
    combo = (np.abs(rres) > 3.5) | (md2 > 4)
    score(combo, "combined detector"); show(combo)
    print()

    print("7) threshold trade-off for the combined score")
    s = np.maximum(np.abs(rres) / 3.5, md2 / 4)
    for t in [0.6, 0.8, 1.0, 1.2, 1.5]:
        score(s > t, f"   threshold x{t}")
