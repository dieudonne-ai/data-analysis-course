# Module 09 — Regression & Prediction

**Linear regression** fits a line (or plane) that predicts a number from other variables:

`score = intercept + b1 * study_hours + b2 * sleep_hours`

Dataset: [`data/students.csv`](../data/students.csv).

Diagrams: [`diagrams/regression_line.pdf`](diagrams/regression_line.pdf),
[`diagrams/train_test.pdf`](diagrams/train_test.pdf)

## Simple regression
Least squares picks the line that minimises the sum of squared **residuals**
(the vertical gaps between points and the line).
```python
import numpy as np
slope, intercept = np.polyfit(df["study_hours"], df["score"], 1)
```
Interpretation: each extra study hour is associated with `slope` more points.

## Multiple regression
```python
X = np.column_stack([np.ones(len(df)), df[["study_hours", "sleep_hours"]]])
coef, *_ = np.linalg.lstsq(X, df["score"], rcond=None)
```
On the training data we get roughly: intercept 31.8, +2.5 points per study hour,
+1.9 points per sleep hour. Prediction for 12 h study + 8 h sleep: about 76.8.

## How good is the model?
- **R²**: share of the variance explained (0 = useless, 1 = perfect).
- **RMSE**: typical prediction error, in the units of the target (here points).

## Train / test split
Never judge a model on the data it was fitted on. Hold out 20% of rows,
fit on the other 80%, and evaluate on the held-out part.

Our run: train R² = 0.56, test R² = 0.30, test RMSE ≈ 6.1 points.
The drop from train to test is expected (the model fits noise in the training set, and the
test set has only 40 rows, so the estimate is noisy). A different random split gives a different value —
this is why analysts use cross-validation on larger projects.

## Cautions
- Association is not causation.
- Do not extrapolate far beyond the range of your data.
- Check residuals: they should look like random noise, not a pattern.

Script: [`examples/regression_demo.py`](examples/regression_demo.py)
