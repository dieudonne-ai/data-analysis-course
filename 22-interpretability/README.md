# Module 22 – Model Interpretability (bonus)

In module 21 we built a gradient boosting model that predicts churn with 72% test accuracy. A manager will immediately ask: **"Why? Which customers, and what can we do about it?"** A model made of 50 trees is a black box – you cannot read it like a regression formula. This module shows four tools to open the box, all written from scratch with numpy on the same churn data and the same train/test split.

Run it: `python 22-interpretability/examples/interpret_demo.py` (numpy only, reuses `boost()` from module 21).
Rebuild the diagrams: `python 22-interpretability/diagrams/make_diagrams.py`.

## 1. Two families of questions
Diagram: [`diagrams/methods_map.pdf`](diagrams/methods_map.pdf)

| | Question | Tool |
|---|---|---|
| **Global** | Which features matter overall? | feature importance |
| **Global** | Does churn go up or down with tenure? Straight or curved? | partial dependence |
| **Local** | Is the effect the same for every customer? | ICE curves |
| **Local** | Why is *this* customer at 93%? | Shapley values |

Global answers are for strategy ("focus retention on new customers"); local answers are for action ("call customer #42 – their support calls are the problem").

## 2. Feature importance – and its trap
Diagram: [`diagrams/importance.pdf`](diagrams/importance.pdf)

**Split counts** (built into most tree libraries as `feature_importances_`): count how often each feature is used to split.
```
1) split-count importance: tenure 80 (53%), support_calls 70 (47%)
```
**Permutation importance**: take the *test* set, randomly shuffle one column (breaking its link with churn) and measure how much worse the model gets.
```python
base = log_loss(y_test, proba(X_test))
Xp = X_test.copy()
Xp[:, j] = rng.permutation(Xp[:, j])          # destroy feature j only
importance_j = log_loss(y_test, proba(Xp)) - base
```
```
shuffle tenure        -> loss +0.2140  (+/- 0.0502)
shuffle support_calls -> loss +0.0840  (+/- 0.0216)
```
Tenure is clearly the most useful feature – roughly 2.5× more than support calls.

**The trap.** Add a column of pure random noise and retrain:
```
   tenure        splits  46   permutation +0.2344
   support_calls splits  42   permutation +0.0700
   noise         splits  61   permutation +0.0070
```
The noise column gets the **most splits**! It has a different value on every one of the 450 training rows (tenure has 60 distinct values, support calls only 8), so the tree can always find a split on it that fits a few training rows by luck (over-fitting, module 20). Permutation importance on *test* data is not fooled: shuffling noise changes almost nothing.

Rule: **use permutation importance on held-out data**; treat split counts only as a rough hint.

## 3. Partial dependence and ICE curves
Diagram: [`diagrams/partial_dependence.pdf`](diagrams/partial_dependence.pdf)

Partial dependence answers "what if *everybody* had tenure = 12 months?": set the column to that value for all rows, predict, average. Repeat for a grid of values.
```python
def partial_dependence(proba, X, j, grid):
    ice = np.empty((len(X), len(grid)))
    for g, v in enumerate(grid):
        Xg = X.copy(); Xg[:, j] = v
        ice[:, g] = proba(Xg)                 # one prediction per customer
    return ice.mean(axis=0), ice              # average = PD, rows = ICE curves
```
```
tenure        1:0.72  6:0.64  12:0.62  24:0.34  48:0.18  72:0.10
support_calls 0:0.27  2:0.32  4:0.53  6:0.66  8:0.66
```
Reading it:
- Churn risk falls sharply around **2 years** of tenure – a step a linear model would smooth away.
- Support calls matter from **4 calls** onward, then plateau at 5–6.
- The grey **ICE** lines (one per customer) are mostly parallel: the effect of calls is similar for everybody, there is little interaction.

Business translation: "Customers in their first two years who call support 4+ times are the risk group – trigger a retention call after the 3rd support ticket."

Caution: partial dependence invents combinations (e.g. tenure 1 month *with* 70 months of history in other columns). When features are strongly correlated, those points may not exist in reality.

## 4. Shapley values: explaining one prediction
Diagram: [`diagrams/shapley_waterfall.pdf`](diagrams/shapley_waterfall.pdf)

Shapley values (from game theory) split one prediction into fair shares:

**prediction = base rate + contribution(tenure) + contribution(calls)**

With two features we can compute them exactly: a feature's share is the average change in prediction when we "reveal" it, over both orders (reveal it first, or second).
```python
def shapley_2(proba, x, X_background):
    def v(keep):                      # average prediction when only `keep` features are set to x
        Xk = X_background.copy()
        for j in keep: Xk[:, j] = x[j]
        return proba(Xk).mean()
    phi_tenure = 0.5 * ((v([0]) - v([])) + (v([0, 1]) - v([1])))
    phi_calls  = 0.5 * ((v([1]) - v([])) + (v([0, 1]) - v([0])))
```
```
new & unhappy  tenure= 3 calls=7: base 0.36 +0.31 (tenure) +0.25 (calls) = 0.93
loyal & quiet  tenure=60 calls=1: base 0.36 -0.25 (tenure) -0.06 (calls) = 0.06
average        tenure=30 calls=3: base 0.36 -0.08 (tenure) +0.07 (calls) = 0.35
```
The pieces always add up exactly to the prediction. For the first customer you can now say: *"93% risk: being new adds 31 points, 7 support calls add 25 points."* The calls part is the one you can act on.

With many features the exact formula needs 2ⁿ evaluations, so libraries approximate it; for trees, **TreeSHAP** computes it exactly and fast.

## 5. Interpretation ≠ causation
These tools explain **the model**, not the world. "Support calls push churn up" may mean unhappy customers call more – reducing calls by hiding the phone number will not keep them! To claim causation you need an experiment (module 12, A/B testing).

## 6. In practice with libraries
```python
from sklearn.inspection import permutation_importance, PartialDependenceDisplay
r = permutation_importance(model, X_test, y_test, n_repeats=20, scoring="neg_log_loss", random_state=0)
PartialDependenceDisplay.from_estimator(model, X_train, ["tenure", "support_calls"], kind="both")  # PD + ICE

import shap                                  # pip install shap
explainer = shap.TreeExplainer(model)
sv = explainer(X_test)
shap.plots.waterfall(sv[0])                  # one customer
shap.plots.beeswarm(sv)                      # all customers: global view built from local ones
```

## Exercises
1. Compute permutation importance on the **training** set instead of the test set. Does the noise column look more important? Why?
2. Draw a 2-D partial dependence (a heatmap over tenure × support_calls). Is there an interaction?
3. Check the Shapley "additivity" property: for 20 random test customers, verify `base + φ_tenure + φ_calls == prediction`.
4. Write a one-paragraph explanation for a manager of the 3 highest-risk customers in the test set, using their Shapley values.

## Git notes for this module
Diagram: [`diagrams/git_objects.pdf`](diagrams/git_objects.pdf)

See [git-notes](../git-notes/README.md#looking-inside-git-cat-file-ls-tree-rev-parse-and-gc): open git's own black box with `git cat-file`, `git ls-tree` and `git rev-parse`, and keep the repository healthy with `git count-objects`, `git gc` and `git fsck`.
