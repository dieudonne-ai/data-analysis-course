# Module 09 — Regression & Prediction

Regression answers: *"How does an outcome change when other variables change, and can I predict it?"*
We use `data/sales_eda.csv` and plain numpy (no extra libraries needed).

## 1. Simple linear regression

Model: `y = intercept + slope * x + error`. **Least squares** picks the line that
minimises the sum of squared residuals (residual = actual - predicted).
Diagram: [`diagrams/fit_line.pdf`](diagrams/fit_line.pdf)

```python
slope, intercept = np.polyfit(df["quantity"], df["revenue"], 1)
```

Result: `revenue = 10.84 + 1.61 * quantity`. Each extra unit adds ~1.61 to revenue.
Interpretation: the **slope** is the average change in y per unit of x; it is an association, not proof of causation.

## 2. R-squared and RMSE

- **R²** = share of the variance in y explained by the model (0 to 1). Here 0.18: quantity alone explains little.
- **RMSE** = typical prediction error, in the units of y (here ~14.5).

## 3. Multiple regression

Add more features: `revenue ~ quantity + price`.
```python
X = np.column_stack([np.ones(len(df)), df["quantity"], df["price"]])
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
```
R² jumps to 0.73 — revenue is basically `quantity * price`, so both matter.
Diagram: [`diagrams/actual_vs_predicted.pdf`](diagrams/actual_vs_predicted.pdf)
Each coefficient is the effect of that feature **holding the others fixed**.

## 4. Don't fool yourself: train/test split

A model always looks good on the data it was fitted to. Fit on 70% of rows, evaluate on the held-out 30%.
If test error is much larger than train error, you are **overfitting**.
Diagram: [`diagrams/workflow.pdf`](diagrams/workflow.pdf)

## 5. Check the residuals

Residuals should average ~0, have no pattern against fitted values, and no extreme outliers.
Curves or funnels in a residual plot mean the linear model is missing something.

## 6. Assumptions (LINE)
**L**inear relationship, **I**ndependent errors, **N**ormal-ish errors, **E**qual variance.
Also beware of highly correlated features (multicollinearity) and extrapolating outside the observed range.

## Sample output (`examples/regression_demo.py`)

| Model | R² | Note |
|-------|----|------|
| quantity only | 0.182 | RMSE 14.45 |
| quantity + price | 0.728 | RMSE 8.33 (all data) |
| train / test RMSE | 8.22 / 8.64 | generalises well |
| quantity=4, price=25 | predicts 49.54 | |

## Exercises
1. Regress revenue on price only. Compare R² with quantity only.
2. Add one-hot encoded `product` to the multiple regression (`pd.get_dummies`). Does R² change?
3. Repeat the train/test split with 5 different seeds. How stable is the test RMSE?

## Git note (see [git-notes](../git-notes/README.md))
Pull requests and `git pull` keep `main` up to date: one branch per lesson, merged into `main`.
