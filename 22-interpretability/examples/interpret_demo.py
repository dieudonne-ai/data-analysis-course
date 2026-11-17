"""Opening the black box: interpreting the gradient boosting churn model from module 21 (numpy only)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "21-gradient-boosting" / "examples"))
from boosting_demo import X, boost, log_loss, predict, sigmoid, te, tr, y  # noqa: E402

FEATURES = ["tenure", "support_calls"]


def fit_model(n_trees=50, lr=0.1, max_depth=2):
    """Train the module-21 model on the training rows and return a predict_proba function."""
    f0, trees, _ = boost(X[tr], y[tr], n_trees, lr=lr, max_depth=max_depth, X_eval=X[tr[:1]])

    def proba(Xn):
        F = np.full(len(Xn), f0)
        for t in trees:
            F += lr * predict(t, Xn)
        return sigmoid(F)

    return f0, trees, proba


def split_counts(trees):
    """Built-in importance: how many splits use each feature."""
    counts = np.zeros(len(FEATURES), int)

    def walk(n):
        if "v" in n:
            return
        counts[n["f"]] += 1
        walk(n["L"]); walk(n["R"])

    for t in trees:
        walk(t)
    return counts


def permutation_importance(proba, Xe, ye, n_repeats=20, seed=0):
    """Shuffle one column at a time; importance = how much the test log-loss gets worse."""
    rng = np.random.default_rng(seed)
    base = log_loss(ye, proba(Xe))
    out = np.zeros((len(FEATURES), n_repeats))
    for j in range(len(FEATURES)):
        for k in range(n_repeats):
            Xp = Xe.copy()
            Xp[:, j] = rng.permutation(Xp[:, j])
            out[j, k] = log_loss(ye, proba(Xp)) - base
    return base, out


def partial_dependence(proba, Xb, j, grid):
    """Average prediction when everybody's feature j is set to each grid value. Also returns ICE lines."""
    ice = np.empty((len(Xb), len(grid)))
    for g, v in enumerate(grid):
        Xg = Xb.copy()
        Xg[:, j] = v
        ice[:, g] = proba(Xg)
    return ice.mean(axis=0), ice


def shapley_2(proba, x, Xb):
    """Exact Shapley values for a 2-feature model, measured in probability, against background data Xb."""
    def v(keep):                     # expected prediction when only features in `keep` are fixed to x
        Xk = Xb.copy()
        for j in keep:
            Xk[:, j] = x[j]
        return proba(Xk).mean()
    base, full = v([]), v([0, 1])
    phi0 = 0.5 * ((v([0]) - base) + (full - v([1])))
    phi1 = 0.5 * ((v([1]) - base) + (full - v([0])))
    return base, np.array([phi0, phi1]), full


if __name__ == "__main__":
    f0, trees, proba = fit_model()
    p_te = proba(X[te])
    print(f"model: 50 trees, lr 0.1, depth 2 | test log-loss {log_loss(y[te], p_te):.4f}, "
          f"test accuracy {np.mean((p_te > .5) == y[te]):.3f}")

    # 1. Built-in importance (split counts)
    c = split_counts(trees)
    print("\n1) split-count importance:", ", ".join(f"{f} {n} ({n / c.sum():.0%})" for f, n in zip(FEATURES, c)))

    # 2. Permutation importance on the TEST set
    base, imp = permutation_importance(proba, X[te], y[te])
    print(f"\n2) permutation importance (test log-loss {base:.4f} before shuffling)")
    for f, row in zip(FEATURES, imp):
        print(f"   shuffle {f:<13} -> loss +{row.mean():.4f}  (+/- {row.std():.4f})")

    # 3. Partial dependence
    print("\n3) partial dependence (average churn probability)")
    for j, grid in ((0, [1, 6, 12, 24, 48, 72]), (1, [0, 2, 4, 6, 8])):
        pd, _ = partial_dependence(proba, X[tr], j, np.array(grid, float))
        print(f"   {FEATURES[j]:<13}", "  ".join(f"{g}:{p:.2f}" for g, p in zip(grid, pd)))

    # 4. Explaining single customers with Shapley values
    print("\n4) local explanations (Shapley values, in probability points)")
    customers = {"new & unhappy": [3, 7], "loyal & quiet": [60, 1], "average": [30, 3]}
    for name, x in customers.items():
        b, phi, full = shapley_2(proba, np.array(x, float), X[tr])
        print(f"   {name:<14} tenure={x[0]:>2} calls={x[1]}: base {b:.2f} "
              f"{phi[0]:+.2f} (tenure) {phi[1]:+.2f} (calls) = {full:.2f}")

    # 5. Sanity check: importance on noise
    rng = np.random.default_rng(1)
    Xn = np.column_stack([X, rng.normal(size=len(y))])
    print("\n5) sanity check: a random 'noise' column added to the data")
    f0n, tn, _ = boost(Xn[tr], y[tr], 50, lr=0.1, max_depth=2, X_eval=Xn[tr[:1]])

    def proba_n(Xq):
        F = np.full(len(Xq), f0n)
        for t in tn:
            F += 0.1 * predict(t, Xq)
        return sigmoid(F)

    counts = np.zeros(3, int)

    def walk(n):
        if "v" not in n:
            counts[n["f"]] += 1; walk(n["L"]); walk(n["R"])

    for t in tn:
        walk(t)
    base_n = log_loss(y[te], proba_n(Xn[te]))
    perm = []
    for j in range(3):
        Xp = Xn[te].copy(); Xp[:, j] = rng.permutation(Xp[:, j])
        perm.append(log_loss(y[te], proba_n(Xp)) - base_n)
    for name, cnt, pi in zip(FEATURES + ["noise"], counts, perm):
        print(f"   {name:<13} splits {cnt:>3}   permutation +{pi:.4f}")
