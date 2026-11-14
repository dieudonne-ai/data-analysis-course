"""Cross-validation and hyperparameter tuning with numpy only (ridge polynomial regression)."""
import numpy as np

rng = np.random.default_rng(19)
n = 120
x = np.sort(rng.uniform(-3, 3, n))
y = np.sin(x) + rng.normal(0, .35, n)          # true signal + noise


def design(x, degree):
    return np.vander(x, degree + 1, increasing=True)


def fit_ridge(X, y, lam):
    I = np.eye(X.shape[1]); I[0, 0] = 0          # do not penalise the intercept
    return np.linalg.solve(X.T @ X + lam * I, X.T @ y)


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


print("== 1. One train/test split is a noisy estimate ==")
for seed in range(3):
    idx = np.random.default_rng(seed).permutation(n)
    tr, te = idx[:90], idx[90:]
    w = fit_ridge(design(x[tr], 5), y[tr], 0)
    print(f"split {seed}: test RMSE = {rmse(design(x[te], 5) @ w, y[te]):.3f}")


def kfold_indices(n, k, seed=0):
    idx = np.random.default_rng(seed).permutation(n)
    return np.array_split(idx, k)


def cv_score(degree, lam, k=5):
    scores = []
    folds = kfold_indices(n, k)
    for i in range(k):
        te = folds[i]
        tr = np.concatenate([f for j, f in enumerate(folds) if j != i])
        w = fit_ridge(design(x[tr], degree), y[tr], lam)
        scores.append(rmse(design(x[te], degree) @ w, y[te]))
    return np.mean(scores), np.std(scores)


print("\n== 2. 5-fold CV: mean and spread ==")
m, s = cv_score(5, 0)
print(f"degree 5: RMSE = {m:.3f} +/- {s:.3f}")

print("\n== 3. Choosing model complexity (degree) ==")
for d in (1, 3, 5, 9, 15):
    m, s = cv_score(d, 1e-6)
    print(f"degree {d:>2}: CV RMSE = {m:.3f} +/- {s:.3f}")

print("\n== 4. Grid search over (degree, lambda) ==")
grid = [(d, lam) for d in (3, 5, 9, 15) for lam in (0, .01, .1, 1, 10)]
results = sorted((cv_score(d, lam)[0], d, lam) for d, lam in grid)
for score, d, lam in results[:3]:
    print(f"degree={d:>2} lambda={lam:<5} CV RMSE={score:.3f}")
best = results[0]
print(f"best: degree={best[1]}, lambda={best[2]}")

print("\n== 5. Final check on an untouched test set ==")
idx = np.random.default_rng(99).permutation(n)
tr, te = idx[:96], idx[96:]
w = fit_ridge(design(x[tr], best[1]), y[tr], best[2])
print(f"test RMSE = {rmse(design(x[te], best[1]) @ w, y[te]):.3f} (noise floor is about 0.35)")
