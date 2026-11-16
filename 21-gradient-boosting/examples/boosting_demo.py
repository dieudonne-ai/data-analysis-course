"""Gradient boosting from scratch (numpy only) on the churn data from modules 15 and 20."""
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[2] / "data" / "churn.csv"
raw = np.genfromtxt(DATA, delimiter=",", names=True)
X = np.column_stack([raw["tenure"], raw["support_calls"]]).astype(float)
y = raw["churn"].astype(float)

rng = np.random.default_rng(20)                     # same split as module 20, so results compare
idx = rng.permutation(len(y))
tr, te = idx[:450], idx[450:]


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def log_loss(y, p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))


def best_split(X, r, min_leaf):
    """Regression split: minimise the squared error of the residuals r."""
    best = (None, None, np.sum((r - r.mean()) ** 2))
    for f in range(X.shape[1]):
        for t in np.unique(X[:, f])[:-1]:
            left = X[:, f] <= t
            if left.sum() < min_leaf or (~left).sum() < min_leaf:
                continue
            sse = np.sum((r[left] - r[left].mean()) ** 2) + np.sum((r[~left] - r[~left].mean()) ** 2)
            if sse < best[2] - 1e-12:
                best = (f, t, sse)
    return best


def build(X, r, hess, depth, max_depth, min_leaf=10):
    """Small regression tree on residuals. Leaf value = Newton step sum(r) / sum(p(1-p))."""
    f, t, _ = best_split(X, r, min_leaf) if depth < max_depth else (None, None, None)
    if f is None:
        return {"v": r.sum() / (hess.sum() + 1e-9)}
    left = X[:, f] <= t
    return {"f": f, "t": t,
            "L": build(X[left], r[left], hess[left], depth + 1, max_depth, min_leaf),
            "R": build(X[~left], r[~left], hess[~left], depth + 1, max_depth, min_leaf)}


def predict(node, X):
    out = np.empty(len(X))
    for i, x in enumerate(X):
        n = node
        while "v" not in n:
            n = n["L"] if x[n["f"]] <= n["t"] else n["R"]
        out[i] = n["v"]
    return out


def boost(X, y, n_trees, lr, max_depth, X_eval=None):
    f0 = np.log(y.mean() / (1 - y.mean()))          # start: log-odds of the base churn rate
    F = np.full(len(y), f0)
    F_eval = np.full(len(X_eval), f0) if X_eval is not None else None
    trees, history = [], []
    for m in range(n_trees):
        p = sigmoid(F)
        r = y - p                                    # residuals = negative gradient of log-loss
        tree = build(X, r, p * (1 - p), 0, max_depth)
        F += lr * predict(tree, X)
        trees.append(tree)
        if X_eval is not None:
            F_eval += lr * predict(tree, X_eval)
            history.append((log_loss(y, sigmoid(F)), sigmoid(F_eval)))
    return f0, trees, history


if __name__ == "__main__":
    base = 1 - y[te].mean()
    print(f"train churn rate {y[tr].mean():.2f} | baseline test accuracy ('nobody churns') {base:.3f}")

    # 1. The first few rounds, step by step
    f0, trees, hist = boost(X[tr], y[tr], 3, lr=0.3, max_depth=2, X_eval=X[te])
    print(f"\nstart prediction: log-odds {f0:.3f} -> p = {sigmoid(f0):.2f} for everybody")
    for m, (loss, _) in enumerate(hist, 1):
        print(f"after tree {m}: train log-loss {loss:.4f}")

    # 2. Learning rate x number of trees
    print("\nlr    trees  train-loss  test-loss  test-acc")
    for lr in (1.0, 0.3, 0.1):
        _, _, hist = boost(X[tr], y[tr], 200, lr=lr, max_depth=2, X_eval=X[te])
        for n in (10, 50, 200):
            loss, p = hist[n - 1]
            print(f"{lr:<5} {n:>5}  {loss:10.4f}  {log_loss(y[te], p):9.4f}  {np.mean((p > .5) == y[te]):8.3f}")

    # 3. Early stopping on a validation slice of the training data (never the test set!)
    fit, val = tr[:360], tr[360:]
    _, _, hist = boost(X[fit], y[fit], 300, lr=0.1, max_depth=2, X_eval=X[val])
    val_loss = [log_loss(y[val], p) for _, p in hist]
    best_n = int(np.argmin(val_loss)) + 1
    print(f"\nearly stopping: best number of trees on validation = {best_n} (val log-loss {min(val_loss):.4f})")
    _, _, hist = boost(X[tr], y[tr], best_n, lr=0.1, max_depth=2, X_eval=X[te])
    p = hist[-1][1]
    print(f"final model ({best_n} trees, lr 0.1, depth 2): test log-loss {log_loss(y[te], p):.4f}, "
          f"test accuracy {np.mean((p > .5) == y[te]):.3f}")
