# Module 18 – Feature Engineering (bonus)

Models and charts only see the columns you give them. **Feature engineering** is turning raw columns into informative, model-ready ones. Good features often beat fancier algorithms (modules 09, 15, 16, 17).

Run it: `python 18-feature-engineering/examples/features_demo.py` (numpy/pandas only).

## 1. The pipeline
Diagram: [`diagrams/pipeline.pdf`](diagrams/pipeline.pdf)

raw data → clean & impute → transform → encode categories → scale → features.

## 2. Dates become parts
A raw timestamp is useless to most models; its parts are not:
```python
df["month"] = df["signup"].dt.month
df["is_weekend"] = (df["signup"].dt.day_of_week >= 5).astype(int)
df["days_since"] = (pd.Timestamp("2026-01-01") - df["signup"]).dt.days   # "tenure"
```

## 3. Encoding categories
Diagram: [`diagrams/encoding.pdf`](diagrams/encoding.pdf)

- **Ordered** categories (free < basic < pro): map to integers, `df["plan"].map({...})`.
- **Unordered** categories (country): **one-hot**, `pd.get_dummies(df, columns=["country"])`. Integers would invent a fake order (CD=2 > BE=1).

## 4. Missing values: impute and flag
```python
df["income_missing"] = df["income"].isna().astype(int)   # missingness itself can be a signal
df["income"] = df["income"].fillna(df["income"].median())
```
Median is robust to outliers (module 04).

## 5. Skewed numbers: log transform
Diagram: [`diagrams/log_transform.pdf`](diagrams/log_transform.pdf)

Incomes, prices and counts have long right tails. `np.log1p(x)` reduces skew from 2.2 to about 0 in our example and makes linear models behave.

## 6. Creating new features
```python
df["avg_order_value"] = df["spend"] / df["orders"].replace(0, np.nan)   # ratio
df["spend_band"] = pd.qcut(df["spend"], 4, labels=["Q1","Q2","Q3","Q4"]) # binning
```
Ratios, differences, counts and bins encode domain knowledge: "how much per order?" is more meaningful than raw spend.

## 7. Scaling
| method | formula | use when |
|---|---|---|
| min-max | (x-min)/(max-min) | you need 0–1 (neural nets, distances) |
| z-score | (x-mean)/std | k-means, PCA, regression (modules 16, 17) |

## 8. Avoid leakage
Diagram: [`diagrams/leakage.pdf`](diagrams/leakage.pdf)

**Split first, then fit transformations (mean, std, median) on the training set only** and reuse them on the test set. Computing them on all data lets test information leak into training and inflates your scores. Same rule for imputation and encoding.

## Exercise
Add a `signup_quarter` feature and a `is_pro_and_weekend` interaction. Do they correlate with `spend`? Check with `df.corr(numeric_only=True)`.
