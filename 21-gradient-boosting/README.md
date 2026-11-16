# Module 21 – Gradient Boosting (bonus)

Module 20 ended with a teaser: **gradient boosting** builds trees *one after another*, each fixing the mistakes of the ones before. It is the method behind XGBoost, LightGBM and CatBoost, and it wins most competitions on tabular data (spreadsheets, SQL tables). Here we write it from scratch on the same churn data and the same train/test split as module 20, so you can compare directly.

Run it: `python 21-gradient-boosting/examples/boosting_demo.py` (numpy only).
Rebuild the diagrams: `python 21-gradient-boosting/diagrams/make_diagrams.py`.

## 1. The idea in one picture
Diagram: [`diagrams/boosting_idea.pdf`](diagrams/boosting_idea.pdf)

1. Start with a dumb prediction for everyone: the base churn rate (36%).
2. Compute what is still wrong: the **residuals** `y − p`.
3. Fit a **small** tree (depth 1–3) that predicts those residuals.
4. Add a *fraction* of it to the model: `F = F + learning_rate × tree`.
5. Repeat from step 2.

Analogy: a student takes a practice exam, studies only the questions they got wrong, takes the exam again, studies the new mistakes... Each round is a small correction.

## 2. Why "gradient"? Residuals for classification
For churn (yes/no) we work in **log-odds** `F`, and turn it into a probability with the sigmoid `p = 1 / (1 + e^−F)` – exactly like logistic regression in module 15.

```python
f0 = np.log(y.mean() / (1 - y.mean()))   # log-odds of 36% = -0.566
F = np.full(len(y), f0)
for m in range(n_trees):
    p = sigmoid(F)
    r = y - p                            # residual = negative gradient of the log-loss
    tree = build(X, r, p * (1 - p), 0, max_depth)
    F += lr * predict(tree, X)
```
`y − p` is the slope (gradient) of the log-loss with a minus sign, so each tree takes one step *downhill* – gradient descent, but in "function space". Each leaf predicts `Σr / Σp(1−p)` (a Newton step) instead of a plain average, which keeps the steps well-sized.

Output of the first rounds:
```
start prediction: log-odds -0.566 -> p = 0.36 for everybody
after tree 1: train log-loss 0.5924
after tree 2: train log-loss 0.5619
after tree 3: train log-loss 0.5427
```
(The constant model has log-loss 0.655.) The loss drops quickly at first, then more slowly.

## 3. Watching the residuals shrink
Diagram: [`diagrams/residuals.pdf`](diagrams/residuals.pdf)

| trees | mean \|residual\| |
|---|---|
| 0 | 0.46 |
| 5 | 0.37 |
| 50 | 0.31 |

At round 0 every churner has residual +0.64 and every loyal customer −0.36. As trees are added, the points move toward zero: the model "explains" more and more of the pattern (short tenure + many calls = churn). They never all reach zero, because part of churn is pure noise.

## 4. Learning rate × number of trees
Diagram: [`diagrams/learning_rate.pdf`](diagrams/learning_rate.pdf)

| lr | trees | train loss | test loss | test acc |
|---|---|---|---|---|
| 1.0 | 10 | 0.478 | 0.549 | 0.720 |
| 1.0 | 200 | 0.358 | **0.652** | 0.673 |
| 0.3 | 50 | 0.456 | **0.532** | 0.720 |
| 0.1 | 50 | 0.488 | **0.528** | 0.720 |
| 0.1 | 200 | 0.454 | 0.538 | 0.713 |

- **Train loss always goes down** with more trees – boosting can memorise anything.
- **Test loss goes down then up** – that is over-fitting (module 20, section 4, again).
- A **big learning rate** (1.0) over-fits after ~8 trees; a **small one** (0.1) needs ~50 trees but its best point is better and the curve is flatter, so it is less sensitive to the exact number.

Rule of thumb: pick a small learning rate (0.05–0.1) and let **early stopping** choose the number of trees.

## 5. Early stopping (the right way)
We must not choose the number of trees with the test set (module 19!). Instead split the training data again:
```python
fit, val = tr[:360], tr[360:]
_, _, hist = boost(X[fit], y[fit], 300, lr=0.1, max_depth=2, X_eval=X[val])
best_n = np.argmin([log_loss(y[val], p) for _, p in hist]) + 1
```
```
early stopping: best number of trees on validation = 193
final model (193 trees, lr 0.1, depth 2): test log-loss 0.5367, test accuracy 0.713
```
With such a small data set (90 validation rows) the validation curve is very flat, so the chosen number is noisy – cross-validation (5 folds) would give a more stable answer.

## 6. Bagging vs boosting
Diagram: [`diagrams/bagging_vs_boosting.pdf`](diagrams/bagging_vs_boosting.pdf)

| | Random forest (bagging) | Gradient boosting |
|---|---|---|
| Trees built | in parallel, independent | in sequence, each fixes the last |
| Tree size | deep | small (depth 1–6) |
| Mainly reduces | variance | bias |
| Key settings | n_trees, max_features | learning_rate, n_trees, max_depth |
| Over-fits with more trees? | almost never | **yes** – use early stopping |
| Tuning effort | low | medium |

On our churn data, test accuracies: baseline 0.633 → one deep tree 0.673 → random forest 0.713 → boosting 0.713–0.720. With only two features there is little left to gain; on real tables with dozens of columns, boosting usually comes out on top.

## 7. In practice with libraries
```python
from sklearn.ensemble import HistGradientBoostingClassifier
gb = HistGradientBoostingClassifier(learning_rate=0.1, max_depth=3, max_iter=500,
                                    early_stopping=True, validation_fraction=0.2, random_state=0)
gb.fit(X_train, y_train)
print(gb.n_iter_)                       # trees actually kept after early stopping
gb.predict_proba(X_test)[:, 1]

# XGBoost / LightGBM have the same ideas and names:
# xgboost.XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=4, subsample=0.8)
```
Extra tricks they add: `subsample` (each tree sees a random 80% of rows – "stochastic boosting"), L2 penalty on leaf values, and histogram binning to make split search very fast on millions of rows.

## Exercises
1. Set `max_depth=1` (stumps). How many trees does it take to reach the same test loss as depth 2?
2. Add `subsample`: in `boost`, fit each tree on a random 80% of the rows. Does the test curve get smoother?
3. Replace the 360/90 split in section 5 with 5-fold cross-validation and report the average best number of trees.
4. Compute feature importance: count how often each feature is used for a split across all trees. Compare with the random forest in module 20.

## Git notes for this module
See [git-notes](../git-notes/README.md#tracing-history-log--l-blame--c-and-show-revpath): follow one function through history with `git log -L`, `git blame -C`, view an old file with `git show <rev>:<path>` and restore it with `git restore --source`.
