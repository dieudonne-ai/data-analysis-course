"""Module 23 - Anomaly detection from scratch with numpy.

Creates data/transactions.csv (if missing): 500 card transactions with
amount and hour of day, 15 of them planted as fraud-like anomalies.
Then compares four detectors: z-score, robust z-score (median/MAD),
IQR fences and Mahalanobis distance (2-D), plus a rolling detector for
the monthly sales time series.
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "transactions.csv"
SALES = ROOT / "data" / "monthly_sales.csv"


def make_data(path=DATA, n=500, n_anom=15, seed=23):
    rng = np.random.default_rng(seed)
    amount = np.round(rng.lognormal(mean=3.4, sigma=0.45, size=n), 2)   # typical ~30 EUR
    hour = np.clip(np.round(rng.normal(14, 3.2, size=n)), 6, 23).astype(int)
    label = np.zeros(n, int)
    idx = rng.choice(n, n_anom, replace=False)
    half = n_anom // 2
    amount[idx[:half]] = np.round(rng.uniform(250, 600, half), 2)        # huge amounts
    hour[idx[half:]] = rng.integers(1, 5, n_anom - half)                 # 1-4 a.m. ...
    amount[idx[half:]] = np.round(rng.uniform(35, 65, n_anom - half), 2)   # ... with an ordinary amount
    label[idx] = 1
    rows = ["amount,hour,is_anomaly"] + [f"{a},{h},{l}" for a, h, l in zip(amount, hour, label)]
    path.write_text("\n".join(rows) + "\n")


def load():
    if not DATA.exists():
        make_data()
    d = np.genfromtxt(DATA, delimiter=",", names=True)
    return d["amount"], d["hour"], d["is_anomaly"].astype(int)


def zscore(x):
    return (x - x.mean()) / x.std()


def robust_z(x):
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return 0.6745 * (x - med) / mad          # 0.6745 makes it comparable to a normal z


def iqr_fences(x, k=1.5):
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def mahalanobis(X):
    mu = X.mean(axis=0)
    cov_inv = np.linalg.inv(np.cov(X, rowvar=False))
    D = X - mu
    return np.sqrt(np.einsum("ij,jk,ik->i", D, cov_inv, D))


def score(flag, y):
    tp = int((flag & (y == 1)).sum()); fp = int((flag & (y == 0)).sum()); fn = int((~flag & (y == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn)
    return tp, fp, fn, prec, rec


def rolling_anomalies(values, window=5, k=3.5):
    """Residual = value - centred rolling median; flag residuals with |robust z| > k.

    The median of the neighbours follows trend and seasonality, so only sudden one-off
    jumps are left in the residual."""
    half = window // 2
    centre = np.array([np.median(np.r_[values[max(0, i - half):i], values[i + 1:i + 1 + half]])
                       for i in range(len(values))])          # neighbours only, not the point itself
    resid = values - centre
    rz = robust_z(resid)
    band = k * np.median(np.abs(resid - np.median(resid))) / 0.6745
    return np.abs(rz) > k, centre, band


def load_sales_with_glitch():
    d = np.genfromtxt(SALES, delimiter=",", names=True, dtype=None, encoding=None)
    rev = d["revenue"].astype(float).copy()
    rev[14] *= 1.6     # simulated data-entry glitch (extra zero / duplicated invoice)
    rev[27] *= 0.45    # simulated outage month
    return d["month"], rev


amount, hour, y = load()
X = np.column_stack([amount, hour])

if __name__ == "__main__":
    print(f"{len(y)} transactions, {y.sum()} planted anomalies ({y.mean():.1%})\n")
    print(f"amount: mean {amount.mean():.1f}  std {amount.std():.1f}  median {np.median(amount):.1f}")

    print("\n1) one-feature detectors on `amount`")
    z = zscore(amount); rz = robust_z(amount); lo, hi = iqr_fences(amount)
    for name, flag in [("z-score |z|>3", np.abs(z) > 3),
                       ("robust z |rz|>3.5", np.abs(rz) > 3.5),
                       (f"IQR fences [{lo:.1f}, {hi:.1f}]", (amount < lo) | (amount > hi)),
                       ("robust z on log(amount)", np.abs(robust_z(np.log(amount))) > 3.5)]:
        tp, fp, fn, p, r = score(flag, y)
        print(f"   {name:28s} flagged {flag.sum():3d}  TP {tp:2d}  FP {fp:2d}  FN {fn:2d}  precision {p:.2f}  recall {r:.2f}")

    print("\n2) the masking effect: outliers inflate the std they are measured with")
    clean = amount[y == 0]
    print(f"   std with anomalies {amount.std():.1f}  vs  without {clean.std():.1f}")
    print(f"   so a 120 EUR payment has z = {(120 - amount.mean()) / amount.std():.2f} (looks normal) "
          f"but robust z = {0.6745 * (120 - np.median(amount)) / np.median(np.abs(amount - np.median(amount))):.2f}")

    print("\n3) two features: night-time payments are only odd in combination")
    night = y.astype(bool) & (hour < 5)
    print(f"   night anomalies caught by amount-IQR alone: {((amount > hi) & night).sum()} of {night.sum()}")
    lo_h, hi_h = iqr_fences(hour)
    print(f"   night anomalies caught by hour-IQR alone [{lo_h:.0f}h, {hi_h:.0f}h]: {(((hour < lo_h) | (hour > hi_h)) & night).sum()} of {night.sum()}")
    Xl = np.column_stack([np.log(amount), hour])           # log makes the amount roughly normal
    for name, d, t in [("Mahalanobis(amount, hour)", mahalanobis(X), 3.0),
                       ("Mahalanobis(log amount, hour)", mahalanobis(Xl), 3.0)]:
        tp, fp, fn, p, r = score(d > t, y)
        print(f"   {name:30s} > {t}: flagged {(d > t).sum():3d}  TP {tp:2d}  FP {fp:2d}  FN {fn:2d}  precision {p:.2f}  recall {r:.2f}")

    print("\n4) rolling detector on monthly revenue (with 2 simulated glitches)")
    months, rev = load_sales_with_glitch()
    flags, centre, band = rolling_anomalies(rev)
    for m, v, c in zip(months[flags], rev[flags], centre[flags]):
        print(f"   {m}: revenue {v:7.1f}  expected ~{c:6.1f}  -> investigate")
