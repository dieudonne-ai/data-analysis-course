"""Module 27 - Monte Carlo simulation and the bootstrap.

Part A simulates the monthly profit of a fictional coffee pop-up stand whose
inputs (visitors, conversion, basket size) are uncertain, then uses the same
simulation to choose how many croissants to bake (the "newsvendor" problem).
Part B uses the bootstrap on data/order_values.csv (created if missing:
400 fictional online orders, app vs web) to get confidence intervals for a
median and for a difference between two groups - no formula needed.
Only numpy + pandas.
"""
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "order_values.csv"
SEED = 27

# Pop-up stand assumptions (one month = 30 days)
DAYS, FIXED_COST = 30, 12_000           # rent + staff for the month, in EUR
CAPACITY = 140                          # max customers the stand can serve per day
MARGIN = 0.55                           # share of each sale that is gross margin


def make_orders(path=DATA, seed=SEED):
    """400 orders: right-skewed values (a few big baskets), web slightly higher than app."""
    rng = np.random.default_rng(seed)
    channel = rng.choice(["app", "web"], size=400, p=[.55, .45])
    value = np.where(channel == "app", rng.lognormal(3.30, .55, 400), rng.lognormal(3.42, .60, 400))
    df = pd.DataFrame({"order_id": np.arange(1, 401), "channel": channel, "value": value.round(2)})
    df.to_csv(path, index=False)
    return df


def load():
    return pd.read_csv(DATA) if DATA.exists() else make_orders()


def simulate_month(n_sims, rng):
    """One row per simulated month. Each input is a random draw, not a single guess."""
    visitors = rng.poisson(lam=420, size=(n_sims, DAYS))                    # daily visitors
    conversion = rng.beta(a=30, b=70, size=(n_sims, 1))                     # ~30% buy, unknown exactly
    buyers = np.minimum(rng.binomial(visitors, conversion), CAPACITY)        # queue too long -> lost sales
    basket = rng.normal(7.5, 1.0, size=(n_sims, 1)).clip(4)                 # average basket in EUR
    revenue = (buyers * basket).sum(axis=1)
    return pd.DataFrame({"buyers": buyers.sum(axis=1), "conversion": conversion[:, 0],
                         "basket": basket[:, 0], "revenue": revenue,
                         "profit": revenue * MARGIN - FIXED_COST})


def croissant_profit(stock, demand, price=2.8, cost=0.9):
    """Profit of baking `stock` croissants when `demand` customers want one. Leftovers are thrown away."""
    sold = np.minimum(stock, demand)
    return sold * price - stock * cost


def bootstrap(values, stat, n_boot, rng):
    """Resample with replacement n_boot times and compute the statistic each time."""
    values = np.asarray(values)
    idx = rng.integers(0, len(values), size=(n_boot, len(values)))
    return stat(values[idx], axis=1)


def git_stamp():
    """Short commit hash + '-dirty' if there are uncommitted changes: say WHICH code made a result."""
    def run(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    sha = run("rev-parse", "--short", "HEAD") or "no-git"
    return sha + ("-dirty" if run("status", "--porcelain", "--untracked-files=no") else "")


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    pd.set_option("display.width", 120)

    print("1. Estimating a probability by simulation: P(at least 3 sixes in 10 dice rolls)")
    exact = 1 - sum(__import__("math").comb(10, k) * (1 / 6) ** k * (5 / 6) ** (10 - k) for k in range(3))
    for n in (100, 1_000, 10_000, 100_000):
        rolls = rng.integers(1, 7, size=(n, 10))
        est = ((rolls == 6).sum(axis=1) >= 3).mean()
        print(f"   n = {n:>7,}  estimate = {est:.4f}   error = {est - exact:+.4f}")
    print(f"   exact answer      = {exact:.4f}   (error shrinks like 1/sqrt(n))")

    print("\n2. Monte Carlo: profit of the pop-up stand next month (100,000 simulated months)")
    sims = simulate_month(100_000, rng)
    p = sims.profit
    print(sims[["buyers", "conversion", "basket", "revenue", "profit"]].describe(percentiles=[.05, .5, .95])
          .loc[["mean", "5%", "50%", "95%"]].round(2).to_string())
    single = min(420 * 0.30, CAPACITY) * DAYS * 7.5 * MARGIN - FIXED_COST
    print(f"   single 'average' guess : {single:,.0f} EUR   (420 visitors x 30% x 7.50 EUR, every day)")
    print(f"   simulated mean profit  : {p.mean():,.0f} EUR   90% interval: [{p.quantile(.05):,.0f}, {p.quantile(.95):,.0f}]")
    print(f"   P(loss)                : {(p < 0).mean():.1%}")
    print(f"   P(profit > 5,000 EUR)  : {(p > 5_000).mean():.1%}")
    print(f"   flaw of averages       : busy days are capped at {CAPACITY} buyers, quiet days are not,"
          f"\n                            so the single guess is {single - p.mean():,.0f} EUR too optimistic")
    driver = sims[["conversion", "basket"]].corrwith(sims.profit).round(2)
    top = driver.idxmax()
    print(f"   correlation with profit: conversion {driver['conversion']}, basket {driver['basket']}  -> {top} drives the risk most")

    print("\n3. A decision under uncertainty: how many croissants to bake each morning?")
    demand = rng.poisson(lam=rng.gamma(shape=20, scale=4, size=50_000))      # ~80 a day, varies a lot
    stocks = np.arange(40, 141, 10)
    res = pd.DataFrame({"stock": stocks,
                        "mean_profit": [croissant_profit(s, demand).mean() for s in stocks],
                        "P(sold out)": [(demand >= s).mean() for s in stocks],
                        "mean_wasted": [np.maximum(s - demand, 0).mean() for s in stocks]}).round(2)
    print(res.to_string(index=False))
    best = res.loc[res.mean_profit.idxmax()]
    print(f"   best stock = {best.stock:.0f} (mean demand is {demand.mean():.0f}): baking for the average is not optimal,"
          f"\n   because a missed sale costs {2.8 - 0.9:.1f} EUR and a wasted croissant only 0.9 EUR")

    print("\n4. The bootstrap: a confidence interval for the MEDIAN order value")
    orders = load()
    v = orders.value.to_numpy()
    boot_med = bootstrap(v, np.median, 10_000, rng)
    lo, hi = np.percentile(boot_med, [2.5, 97.5])
    print(f"   {len(v)} orders, mean = {v.mean():.2f}, median = {np.median(v):.2f} EUR (skewed: mean > median)")
    print(f"   bootstrap 95% CI for the median: [{lo:.2f}, {hi:.2f}]  (percentile method, 10,000 resamples)")
    boot_mean = bootstrap(v, np.mean, 10_000, rng)
    se = v.std(ddof=1) / np.sqrt(len(v))
    print(f"   check on the mean: bootstrap SE = {boot_mean.std():.2f}, formula s/sqrt(n) = {se:.2f}  -> they agree")

    print("\n5. Bootstrap a difference: web vs app median order value")
    app, web = (orders.loc[orders.channel == c, "value"].to_numpy() for c in ("app", "web"))
    diff = bootstrap(web, np.median, 10_000, rng) - bootstrap(app, np.median, 10_000, rng)
    lo, hi = np.percentile(diff, [2.5, 97.5])
    print(f"   app n = {len(app)}, median {np.median(app):.2f}  |  web n = {len(web)}, median {np.median(web):.2f}")
    print(f"   difference (web - app) = {np.median(web) - np.median(app):.2f} EUR, 95% CI [{lo:.2f}, {hi:.2f}]")
    print(f"   share of resamples where web <= app: {(diff <= 0).mean():.1%}  ->",
          "CI excludes 0: the gap is probably real" if lo > 0 else "CI includes 0: not conclusive")

    print("\n6. Permutation test: same question, 'what if the channel label did not matter?'")
    obs = np.median(web) - np.median(app)
    both, n_web = np.concatenate([app, web]), len(web)
    perm = np.empty(10_000)
    for i in range(10_000):
        shuffled = rng.permutation(both)
        perm[i] = np.median(shuffled[:n_web]) - np.median(shuffled[n_web:])
    print(f"   observed gap {obs:.2f}; p-value = share of shuffles with a gap at least as big = {(np.abs(perm) >= abs(obs)).mean():.4f}")

    print(f"\n7. Reproducibility: seed = {SEED}, code version = {git_stamp()}")
    print("   Same seed + same commit = exactly the same numbers. Write both next to every result you share.")
