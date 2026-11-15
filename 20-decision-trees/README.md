# Module 20 – Decision Trees & Random Forests (bonus)

A **decision tree** predicts by asking a short list of yes/no questions. It is easy to explain to a manager, needs no scaling, and handles non-linear patterns. A **random forest** averages many trees to get a more accurate, more stable model. This module reuses the churn data from module 15 and the cross-validation ideas from module 19.

Run it: `python 20-decision-trees/examples/tree_demo.py` (numpy only, the tree is written from scratch so you can see every step).

## 1. How a tree reads
Diagram: [`diagrams/tree_structure.pdf`](diagrams/tree_structure.pdf)

Our depth-2 tree, learned from 450 customers:
```
if tenure <= 22:
    if support_calls <= 3:  -> churn rate 61% (n=135)
    else:                   -> churn rate 95% (n=21)
else:
    if support_calls <= 2:  -> churn rate 13% (n=193)
    else:                   -> churn rate 35% (n=101)
```
Business reading: *new customers who call support a lot almost always leave* – a clear target for a retention campaign.

## 2. How a split is chosen: Gini impurity
A node is **pure** if all its rows have the same label. Gini impurity measures how mixed it is:

`Gini = 1 − Σ pₖ²`  (0 = pure, 0.5 = 50/50 for two classes)

```python
def gini(labels):
    p = np.bincount(labels, minlength=2) / len(labels)
    return 1 - np.sum(p ** 2)
```
The algorithm tries **every threshold on every feature** and keeps the split with the lowest *weighted* Gini of the two children. Here the whole training set has Gini 0.462 (36% churn); the best first split `tenure <= 22` brings it to 0.372. Then it repeats inside each child (recursion) until a stopping rule fires. An alternative criterion is *entropy* (information gain) – results are usually almost identical.

## 3. Trees cut the space into boxes
Diagram: [`diagrams/feature_space.pdf`](diagrams/feature_space.pdf)

Every split is a straight vertical or horizontal line. The leaves are rectangles, and every point in a rectangle gets the same prediction. That is why trees catch interactions ("short tenure **and** many calls") without you creating the feature by hand (compare module 18).

## 4. Depth and over-fitting
Diagram: [`diagrams/depth_overfit.pdf`](diagrams/depth_overfit.pdf)

| max depth | train acc | test acc |
|---|---|---|
| 1 | 0.744 | 0.680 |
| 3 | 0.753 | 0.700 |
| **5** | 0.784 | **0.760** |
| 8 | 0.847 | 0.700 |
| 12 | 0.871 | 0.673 |

A tree with no limit keeps splitting until every leaf is pure – it memorises noise. Control it with `max_depth`, `min_samples_leaf` (`min_leaf` in our code) or pruning, and **choose these hyperparameters with cross-validation** (module 19), not with the test set.

## 5. Random forests
Diagram: [`diagrams/random_forest.pdf`](diagrams/random_forest.pdf)

1. **Bagging**: draw a bootstrap sample (rows with replacement) for each tree.
2. **Random features**: at each split, only look at a random subset of features.
3. **Average** the predicted probabilities of all trees.

```python
for b in range(50):
    boot = rng.choice(tr, len(tr), replace=True)
    forest.append(build(X[boot], y[boot], 0, max_depth=6, rng=rng, max_features=1))
p = np.mean([predict_proba(t, X_test) for t in forest], axis=0)
```
Each tree is noisy, but their errors partly cancel: test accuracy goes from **0.673** (one deep tree) to **0.713** (forest), against a baseline of 0.633 ("nobody churns"). Always compare with a baseline!

**Feature importance**: counting how often each feature is used to split gives tenure 59%, support_calls 41%. (Libraries use the total Gini decrease; permutation importance is more reliable.)

## 6. In practice with scikit-learn
```python
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5).fit(X_train, y_train)
print(export_text(tree, feature_names=["tenure", "support_calls"]))
rf = RandomForestClassifier(n_estimators=300, random_state=0).fit(X_train, y_train)
rf.feature_importances_
```
Next steps: **gradient boosting** (XGBoost, LightGBM) builds trees one after another, each fixing the errors of the previous ones – often the best choice for tabular data.

| | Decision tree | Random forest |
|---|---|---|
| Explainable | very | less (many trees) |
| Accuracy | medium | high |
| Over-fitting risk | high | low |
| Needs scaling? | no | no |

## Exercises
1. Change `min_leaf` from 5 to 20 for the depth-2 tree. Do the leaves change?
2. Replace Gini with entropy `−Σ p log₂ p` in `best_split`. Is the first split the same?
3. Train forests with 5, 20, 50 and 200 trees and plot test accuracy against the number of trees.
4. Use 5-fold CV (module 19) to choose `max_depth` instead of looking at the test set.

## Git notes for this module
See [git-notes](../git-notes/README.md#revision-ranges-merge-base-and-custom-log-formats): `A..B` vs `A...B`, `git merge-base`, `git log --pretty=format` and `git range-diff`.
