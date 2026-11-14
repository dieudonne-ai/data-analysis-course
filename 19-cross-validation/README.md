# Module 19 – Cross-Validation & Hyperparameter Tuning (bonus)

A model that looks great on the data it was trained on may fail on new data. **Cross-validation (CV)** estimates how a model will perform on unseen data, and lets you **tune** its settings honestly. It builds on regression (09), classification (15) and feature engineering (18).

Run it: `python 19-cross-validation/examples/cv_demo.py` (numpy only).

## 1. Why one split is not enough
Diagram: [`diagrams/split.pdf`](diagrams/split.pdf)

With a single train/test split, the score depends on *which* rows landed in the test set. In our example three random splits give RMSE 0.33, 0.26 and 0.23 for the same model. Keep a final **test set** locked away, and use CV on the rest.

## 2. K-fold cross-validation
Diagram: [`diagrams/kfold.pdf`](diagrams/kfold.pdf)

Cut the training data into *k* folds (usually 5 or 10). Train on k-1 folds, validate on the remaining one, rotate, then average:
```python
folds = np.array_split(np.random.default_rng(0).permutation(n), 5)
for i in range(5):
    val = folds[i]
    train = np.concatenate([f for j, f in enumerate(folds) if j != i])
    ...fit on train, score on val...
```
Report **mean ± standard deviation**: `degree 5: RMSE = 0.310 ± 0.026`. The spread tells you how stable the estimate is.

Variants: *stratified* k-fold keeps class proportions (use for classification, module 15); *time-series split* always validates on the future (module 11); *leave-one-out* is k = n (slow).

## 3. Underfitting vs overfitting
Diagram: [`diagrams/complexity.pdf`](diagrams/complexity.pdf)

| | training error | validation error | fix |
|---|---|---|---|
| **Underfit** (too simple) | high | high | more features, more complex model |
| **Good fit** | low | low | keep it |
| **Overfit** (memorises noise) | very low | high | more data, simpler model, regularisation |

In the demo, degree 1 gives CV RMSE 0.467 (underfit); degrees 3-5 reach about 0.31; degree 15 climbs back to 0.325 (overfit).

## 4. Hyperparameters and grid search
Diagram: [`diagrams/grid_search.pdf`](diagrams/grid_search.pdf)

*Parameters* are learned from data (regression weights). *Hyperparameters* are chosen by you (polynomial degree, ridge strength λ, number of clusters k).

**Ridge regression** adds a penalty to keep weights small: `w = (XᵀX + λI)⁻¹ Xᵀy`. Bigger λ = simpler model.

**Grid search** tries every combination and scores each with CV:
```python
grid = [(d, lam) for d in (3, 5, 9, 15) for lam in (0, .01, .1, 1, 10)]
best = min((cv_score(d, lam)[0], d, lam) for d, lam in grid)
```
When the grid is large, **random search** samples combinations instead and is usually just as good.

## 5. Rules to avoid fooling yourself
1. Split first, then do everything else (scaling, imputing, encoding) **inside** each fold – see leakage in module 18.
2. Never tune on the test set. Look at it **once**, at the end: our final test RMSE is 0.377 versus a noise floor of about 0.35.
3. Prefer the simplest model whose CV score is within one standard deviation of the best ("one-standard-error rule").
4. Set a random seed so results are reproducible.

## Exercises
1. Change `k` from 5 to 10. How do the mean and std move?
2. Add degree 20 to the grid. Does the best choice change?
3. Re-run section 1 with 10 different seeds and plot the spread of test scores.

## Git notes for this module
See [git-notes](../git-notes/README.md#stash-patch-patch-mode-and-interactive-staging): `git add -p`, `git stash -p`, `git restore -p` and `git diff --stat`.
