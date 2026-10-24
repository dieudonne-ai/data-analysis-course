from pathlib import Path

import numpy as np
import pandas as pd

df = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "students.csv")

# Train / test split (80 / 20), reproducible
rng = np.random.default_rng(1)
idx = rng.permutation(len(df))
cut = int(0.8 * len(df))
train, test = df.iloc[idx[:cut]], df.iloc[idx[cut:]]

features = ["study_hours", "sleep_hours"]
X = np.column_stack([np.ones(len(train)), train[features]])
coef, *_ = np.linalg.lstsq(X, train["score"], rcond=None)
print("Intercept and slopes:", {k: round(float(v), 2) for k, v in zip(["intercept"] + features, coef)})

pred_tr = X @ coef
r2_tr = 1 - ((train["score"] - pred_tr) ** 2).sum() / ((train["score"] - train["score"].mean()) ** 2).sum()
print(f"Train R^2 = {r2_tr:.2f}")

Xt = np.column_stack([np.ones(len(test)), test[features]])
pred = Xt @ coef
resid = test["score"] - pred
ss_res = (resid**2).sum()
ss_tot = ((test["score"] - test["score"].mean()) ** 2).sum()
print(f"Test R^2 = {1 - ss_res / ss_tot:.2f}")
print(f"Test RMSE = {np.sqrt((resid**2).mean()):.2f} points")

new = np.array([1, 12, 8])  # 12 h study, 8 h sleep
print(f"Predicted score for 12h study + 8h sleep: {new @ coef:.1f}")
