"""Logistic regression + classification metrics, numpy/pandas only (no sklearn).

Predict whether a customer churns (leaves) from tenure and monthly support calls.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
n = 600
tenure = rng.integers(1, 61, n)            # months as a customer
calls = rng.poisson(2, n)                  # support calls last month
logit = 0.5 - 0.07 * tenure + 0.6 * calls
churn = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
df = pd.DataFrame({"tenure": tenure, "support_calls": calls, "churn": churn})
df.to_csv(Path(__file__).resolve().parents[2] / "data" / "churn.csv", index=False)

print("== 1. The data ==")
print(df.head(), f"\nChurn rate: {df.churn.mean():.1%}")

print("\n== 2. Train/test split ==")
idx = rng.permutation(n); cut = int(.7 * n)
tr, te = idx[:cut], idx[cut:]
X = df[["tenure", "support_calls"]].to_numpy(float)
mu, sd = X[tr].mean(0), X[tr].std(0)
X = np.column_stack([np.ones(n), (X - mu) / sd])   # scale features, add intercept
y = df["churn"].to_numpy()

print("== 3. Logistic regression by gradient descent ==")
sigmoid = lambda z: 1 / (1 + np.exp(-z))
w = np.zeros(3)
for _ in range(2000):
    p = sigmoid(X[tr] @ w)
    w -= 0.1 * X[tr].T @ (p - y[tr]) / len(tr)
print("weights (intercept, tenure, calls):", w.round(2))
print("-> negative tenure weight: longer customers churn less; positive calls weight: more calls, more churn")

print("\n== 4. Confusion matrix on the TEST set (threshold 0.5) ==")
prob = sigmoid(X[te] @ w); pred = (prob >= .5).astype(int); t = y[te]
tp = int(((pred == 1) & (t == 1)).sum()); tn = int(((pred == 0) & (t == 0)).sum())
fp = int(((pred == 1) & (t == 0)).sum()); fn = int(((pred == 0) & (t == 1)).sum())
print(f"TP={tp}  FP={fp}\nFN={fn}  TN={tn}")

print("\n== 5. Metrics ==")
accuracy = (tp + tn) / len(t)
precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
print(f"accuracy={accuracy:.2f} precision={precision:.2f} recall={recall:.2f} F1={f1:.2f}")
print(f"baseline (always predict 'stay') accuracy = {1 - t.mean():.2f}  <- beat this!")

print("\n== 6. Changing the threshold trades precision for recall ==")
for th in (0.3, 0.5, 0.7):
    pr = (prob >= th).astype(int)
    p_ = ((pr == 1) & (t == 1)).sum() / max((pr == 1).sum(), 1)
    r_ = ((pr == 1) & (t == 1)).sum() / max((t == 1).sum(), 1)
    print(f"threshold {th}: precision={p_:.2f} recall={r_:.2f}")

print("\n== 7. Predict one customer: tenure=6 months, 5 calls ==")
x_new = np.r_[1, (np.array([6, 5]) - mu) / sd]
print(f"churn probability = {sigmoid(x_new @ w):.1%}")
