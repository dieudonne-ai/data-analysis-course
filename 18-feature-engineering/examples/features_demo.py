"""Feature engineering with pandas/numpy: turn raw columns into model-ready features."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)
n = 300
df = pd.DataFrame({
    "signup": pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
    "plan": rng.choice(["free", "basic", "pro"], n, p=[.5, .3, .2]),
    "country": rng.choice(["FR", "BE", "CD", "CA"], n),
    "income": rng.lognormal(10, .8, n).round(0),
    "orders": rng.poisson(4, n),
    "spend": rng.gamma(3, 40, n).round(2),
})
df.loc[rng.choice(n, 20, replace=False), "income"] = np.nan

print("== 1. Dates -> useful parts ==")
df["month"] = df["signup"].dt.month
df["is_weekend"] = (df["signup"].dt.day_of_week >= 5).astype(int)
df["days_since"] = (pd.Timestamp("2026-01-01") - df["signup"]).dt.days
print(df[["signup", "month", "is_weekend", "days_since"]].head(3))

print("\n== 2. Categories: ordinal vs one-hot ==")
df["plan_rank"] = df["plan"].map({"free": 0, "basic": 1, "pro": 2})   # ordered -> integers
df = pd.get_dummies(df, columns=["country"], prefix="c", dtype=int)  # unordered -> one-hot
print(df.filter(like="c_").head(3))

print("\n== 3. Missing values: impute + flag ==")
df["income_missing"] = df["income"].isna().astype(int)
df["income"] = df["income"].fillna(df["income"].median())
print("missing flags:", df["income_missing"].sum())

print("\n== 4. Skewed numbers: log transform ==")
print("skew before:", round(df["income"].skew(), 2))
df["log_income"] = np.log1p(df["income"])
print("skew after: ", round(df["log_income"].skew(), 2))

print("\n== 5. New features from combining columns ==")
df["avg_order_value"] = (df["spend"] / df["orders"].replace(0, np.nan)).fillna(0).round(2)
df["spend_band"] = pd.qcut(df["spend"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
print(df[["orders", "spend", "avg_order_value", "spend_band"]].head(3))

print("\n== 6. Scaling: min-max and z-score ==")
for c in ["orders", "spend"]:
    df[c + "_mm"] = (df[c] - df[c].min()) / (df[c].max() - df[c].min())
    df[c + "_z"] = (df[c] - df[c].mean()) / df[c].std()
print(df[["orders_mm", "spend_z"]].describe().loc[["min", "max", "mean"]].round(2))

print("\n== 7. Avoid leakage: fit scaler on train only ==")
train, test = df.iloc[:240], df.iloc[240:]
mu, sd = train["spend"].mean(), train["spend"].std()
test_z = (test["spend"] - mu) / sd          # reuse TRAIN statistics
print("train mean/std:", round(mu, 1), round(sd, 1), "| test z mean:", round(test_z.mean(), 2))
print("\nFinal shape:", df.shape)
