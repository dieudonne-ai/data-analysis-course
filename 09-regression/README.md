# Module 09 - Regression & Prediction

Regression models how an outcome (`spend`) depends on one or more predictors.

Diagrams: [fitted line & residual](diagrams/regression_line.pdf) - [train/test split](diagrams/train_test.pdf) - [residual check](diagrams/residual_check.pdf)

## Simple linear regression
`y = intercept + slope * x`. The line minimises the sum of squared **residuals** (actual - predicted).
```python
res = stats.linregress(df["income"], df["spend"])
# spend = 61.3 + 0.073 * income     R^2 = 0.24
```
Reading it: each extra 100 of income is associated with about +7.3 spend.
**R^2** is the share of the variance explained (0 to 1). Here 24 %.

## Multiple regression
Add predictors: income, visits and the A/B group (coded 0/1).
```python
X = np.column_stack([np.ones(len(df)), df["income"], df["visits"], (df["group"] == "B").astype(int)])
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
```
| Term | Coefficient | Meaning (others held fixed) |
|------|-------------|-----------------------------|
| intercept | 32.2 | baseline |
| income | 0.076 | +100 income -> +7.6 spend |
| visits | 3.43 | each visit -> +3.4 spend |
| group B | 7.83 | B customers spend 7.8 more |

R^2 rises from 0.24 to 0.37. Prediction: income 900, 8 visits, group B -> about 135.6.

## Evaluate honestly
A model must be judged on data it has **not** seen.
```python
idx = rng.permutation(len(df)); cut = int(.8 * len(df))
# fit on idx[:cut], test on idx[cut:]
```
Test RMSE = 24.3 (typical error) versus a std of 28.8 for spend: better than guessing the mean, but far from perfect.

## Check the assumptions
- Relationship roughly linear (look at the scatter).
- Residuals look like random noise around 0 (see the residual diagram).
- Beware **extrapolation** (predicting outside the range of the data) and **correlation vs causation**.

## Exercises
1. Regress `spend` on `age`. Is R^2 higher or lower than with `income`? Why?
2. Add `age` to the multiple regression. Does the `income` coefficient change? (hint: age and income are correlated, r = 0.79)
3. Compute RMSE of the simple model on the same train/test split.
4. Predict spend for a customer with income 500, 3 visits, group A.

Run the worked example: `python 09-regression/examples/regression.py`
