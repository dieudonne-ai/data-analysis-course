"""Decision trees and random forests from scratch (numpy only) on the churn data."""
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[2] / "data" / "churn.csv"
raw = np.genfromtxt(DATA, delimiter=",", names=True)
FEATURES = ["tenure", "support_calls"]
X = np.column_stack([raw[f] for f in FEATURES]).astype(float)
y = raw["churn"].astype(int)

rng = np.random.default_rng(20)
idx = rng.permutation(len(y))
tr, te = idx[:450], idx[450:]


def gini(labels):
    if len(labels) == 0:
        return 0.0
    p = np.bincount(labels, minlength=2) / len(labels)
    return 1.0 - np.sum(p ** 2)


def best_split(X, y, features=None):
    """Try every threshold on every feature; keep the one with lowest weighted Gini."""
    best = (None, None, gini(y))
    for f in (features if features is not None else range(X.shape[1])):
        for t in np.unique(X[:, f])[:-1]:
            left = X[:, f] <= t
            g = (left.sum() * gini(y[left]) + (~left).sum() * gini(y[~left])) / len(y)
            if g < best[2] - 1e-12:
                best = (f, t, g)
    return best


def build(X, y, depth, max_depth, min_leaf=5, rng=None, max_features=None):
    majority = int(np.bincount(y, minlength=2).argmax())
    if depth == max_depth or len(y) < 2 * min_leaf or gini(y) == 0:
        return {"leaf": majority, "p": y.mean(), "n": len(y)}
    feats = None
    if max_features:                                # random forest: random subset of features per split
        feats = rng.choice(X.shape[1], max_features, replace=False)
    f, t, _ = best_split(X, y, feats)
    if f is None:
        return {"leaf": majority, "p": y.mean(), "n": len(y)}
    left = X[:, f] <= t
    if left.sum() < min_leaf or (~left).sum() < min_leaf:
        return {"leaf": majority, "p": y.mean(), "n": len(y)}
    return {"f": f, "t": t,
            "L": build(X[left], y[left], depth + 1, max_depth, min_leaf, rng, max_features),
            "R": build(X[~left], y[~left], depth + 1, max_depth, min_leaf, rng, max_features)}


def predict_proba_one(node, x):
    while "leaf" not in node:
        node = node["L"] if x[node["f"]] <= node["t"] else node["R"]
    return node["p"]


def predict_proba(node, X):
    return np.array([predict_proba_one(node, x) for x in X])


def show(node, indent=""):
    if "leaf" in node:
        print(f"{indent}-> churn rate {node['p']:.0%} (n={node['n']})")
        return
    print(f"{indent}if {FEATURES[node['f']]} <= {node['t']:g}:")
    show(node["L"], indent + "    ")
    print(f"{indent}else:")
    show(node["R"], indent + "    ")


def acc(p, y):
    return float(np.mean((p >= .5).astype(int) == y))


print("== 1. Gini impurity of the whole training set ==")
print(f"churn rate = {y[tr].mean():.2f}, Gini = {gini(y[tr]):.3f}")
f, t, g = best_split(X[tr], y[tr])
print(f"best first split: {FEATURES[f]} <= {t:g}  (weighted Gini {g:.3f})")

print("\n== 2. A depth-2 tree you can read ==")
small = build(X[tr], y[tr], 0, max_depth=2)
show(small)

print("\n== 3. Depth controls over-fitting ==")
for d in (1, 2, 3, 5, 8, 12):
    tree = build(X[tr], y[tr], 0, max_depth=d, min_leaf=1)
    print(f"depth {d:>2}: train acc = {acc(predict_proba(tree, X[tr]), y[tr]):.3f}"
          f"   test acc = {acc(predict_proba(tree, X[te]), y[te]):.3f}")

print("\n== 4. Random forest = many trees on bootstrap samples, averaged ==")
forest = []
for b in range(50):
    boot = rng.choice(tr, len(tr), replace=True)
    forest.append(build(X[boot], y[boot], 0, max_depth=6, min_leaf=3, rng=rng, max_features=1))
p_rf = np.mean([predict_proba(t, X[te]) for t in forest], axis=0)
deep = build(X[tr], y[tr], 0, max_depth=12, min_leaf=1)
print(f"single deep tree test acc = {acc(predict_proba(deep, X[te]), y[te]):.3f}")
print(f"random forest (50 trees)   = {acc(p_rf, y[te]):.3f}")
print(f"baseline (always 'stay')   = {np.mean(y[te] == 0):.3f}")


def count_splits(node, counts):
    if "leaf" not in node:
        counts[node["f"]] += 1
        count_splits(node["L"], counts); count_splits(node["R"], counts)


counts = np.zeros(len(FEATURES))
for t in forest:
    count_splits(t, counts)
print("\nsplit counts per feature (a simple importance):")
for name, c in zip(FEATURES, counts):
    print(f"  {name:<14} {c / counts.sum():.0%}")
