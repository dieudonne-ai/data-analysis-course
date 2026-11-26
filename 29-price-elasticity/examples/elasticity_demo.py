"""Module 29 - Price elasticity & demand analysis.

A fictional online coffee shop sells three products over 104 weeks:
espresso beans, coffee capsules (a substitute for beans) and paper filters.
The manager raises prices in the busy winter season and runs 15%-off promotions,
so price and demand move together for reasons other than price itself.
We estimate elasticities with log-log regression, show the seasonal confounding
trap, add a cross-price elasticity, find the profit-maximising price and put a
bootstrap interval around it. data/weekly_prices.csv is created if missing.
Only numpy + pandas.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WEEKLY = ROOT / "data" / "weekly_prices.csv"
SEED = 29
N_WEEKS = 104
# product: (base price EUR, unit cost EUR, TRUE own-price elasticity, base units/week)
PRODUCTS = {
    "beans":    (12.0, 6.0, -2.2, 400),
    "capsules": (9.0, 4.5, -1.5, 600),
    "filters":  (4.0, 1.5, -0.6, 300),
}
TRUE_CROSS = 0.4      # +1% on capsule price -> +0.4% bean units (substitutes)
SEASON_EFFECT = 0.25  # winter lifts log-demand by up to 0.25 (about +28%)


def season(week):
    """+1 in mid-winter, -1 in mid-summer (week 1 = early January)."""
    return np.cos(2 * np.pi * (week - 2) / 52)


def make_weekly(path=WEEKLY, seed=SEED):
    """One row per product and week: price, promo flag, units sold."""
    rng = np.random.default_rng(seed)
    week = np.arange(1, N_WEEKS + 1)
    s = season(week)
    prices = {}
    promo = {}
    for name, (base, _, _, _) in PRODUCTS.items():
        promo[name] = rng.random(N_WEEKS) < 0.15                              # promotion in ~15% of weeks
        p = base * (1 + 0.10 * s) * np.where(promo[name], 0.85, 1.0)          # higher prices in winter (!)
        prices[name] = (p * rng.normal(1, 0.03, N_WEEKS)).round(2)
    rows = []
    for name, (base, _, elast, units0) in PRODUCTS.items():
        log_q = (np.log(units0) + elast * np.log(prices[name] / base) + SEASON_EFFECT * s
                 + rng.normal(0, 0.08, N_WEEKS))
        if name == "beans":
            log_q += TRUE_CROSS * np.log(prices["capsules"] / PRODUCTS["capsules"][0])
        units = rng.poisson(np.exp(log_q))
        rows += [(w, name, pr, int(pm), u) for w, pr, pm, u in zip(week, prices[name], promo[name], units)]
    df = pd.DataFrame(rows, columns=["week", "product", "price", "promo", "units"])
    df.to_csv(path, index=False)
    return df


def load(path=WEEKLY):
    return pd.read_csv(path) if path.exists() else make_weekly(path)


def ols(y, X, names):
    """Least squares with standard errors and 95% CIs (module 09 recipe)."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    se = np.sqrt(np.diag(resid @ resid / dof * np.linalg.inv(X.T @ X)))
    return pd.DataFrame({"coef": beta, "se": se, "ci_low": beta - 1.96 * se, "ci_high": beta + 1.96 * se}, index=names)


def design(d, with_season=True, cross=None):
    """Columns for log(units) ~ log(price) [+ season] [+ log(other price)]."""
    cols, names = [np.ones(len(d)), np.log(d.price.to_numpy())], ["const", "log_price"]
    if with_season:
        cols.append(season(d.week.to_numpy())); names.append("season")
    if cross is not None:
        cols.append(np.log(cross)); names.append("log_price_other")
    return np.column_stack(cols), names


def fit(d, **kw):
    X, names = design(d, **kw)
    return ols(np.log(d.units), X, names)


def optimal_price(elasticity, cost):
    """Profit-maximising price for constant elasticity e < -1:  p* = c * e / (1 + e)."""
    return cost * elasticity / (1 + elasticity) if elasticity < -1 else np.inf


def profit_curve(prices, elasticity, cost, p_ref, q_ref):
    q = q_ref * (prices / p_ref) ** elasticity
    return prices * q, (prices - cost) * q, q


def main():
    df = load()
    wide = df.pivot(index="week", columns="product", values="price")

    print("1. Elasticity in one sentence: % change in units for a 1% change in price")
    beans = df[df["product"] == "beans"]
    normal, promo = beans[beans.promo == 0], beans[beans.promo == 1]
    p0, p1 = normal.price.mean(), promo.price.mean()
    q0, q1 = normal.units.mean(), promo.units.mean()
    arc = ((q1 - q0) / ((q1 + q0) / 2)) / ((p1 - p0) / ((p1 + p0) / 2))
    print(f"   beans, normal weeks: {p0:.2f} EUR -> {q0:.0f} units;  promo weeks: {p1:.2f} EUR -> {q1:.0f} units")
    print(f"   arc elasticity = %dQ / %dP = {(q1 - q0) / ((q1 + q0) / 2):+.1%} / {(p1 - p0) / ((p1 + p0) / 2):+.1%} = {arc:.2f}")
    print("   |e| > 1 elastic (price cut raises revenue), |e| < 1 inelastic (price cut lowers revenue)")

    print("\n2. Log-log regression: the slope IS the elasticity")
    rows = []
    for name, (_, cost, true_e, _) in PRODUCTS.items():
        d = df[df["product"] == name]
        naive = fit(d, with_season=False).loc["log_price"]
        adj = fit(d, with_season=True).loc["log_price"]
        rows.append((name, naive.coef, adj.coef, adj.ci_low, adj.ci_high, true_e))
    tab = pd.DataFrame(rows, columns=["product", "naive", "with_season", "ci_low", "ci_high", "truth"]).set_index("product")
    print(tab.round(2).to_string().replace("\n", "\n   ").join(["   ", ""]))
    print("   log(units) = a + e*log(price) + b*season;  'truth' is known only because the data is simulated")

    print("\n3. The confounding trap: prices are HIGHER when demand is high")
    corr = np.corrcoef(beans.price, season(beans.week))[0, 1]
    print(f"   corr(bean price, season) = {corr:+.2f}  -> winter = high price AND high demand")
    print(f"   naive beans elasticity {tab.loc['beans', 'naive']:.2f} looks far less price-sensitive than the truth "
          f"{PRODUCTS['beans'][2]:.1f}; for filters it even looks positive ({tab.loc['filters', 'naive']:+.2f})")
    print("   fix: add the confounder (season) to the model, or use only the promo variation within a season")

    print("\n4. Cross-price elasticity: capsules are a substitute for beans")
    caps_price = wide.loc[beans.week, "capsules"].to_numpy()
    cross_fit = fit(beans, with_season=True, cross=caps_price)
    print(cross_fit.round(3).to_string().replace("\n", "\n   ").join(["   ", ""]))
    c = cross_fit.loc["log_price_other"]
    print(f"   cross elasticity {c.coef:+.2f} (truth {TRUE_CROSS:+.1f}): +10% on capsules -> about {c.coef * 10:+.1f}% bean units")
    print("   > 0 substitutes, < 0 complements (e.g. filters and filter coffee), about 0 unrelated")

    print("\n5. From elasticity to price: revenue and profit")
    e_beans = cross_fit.loc["log_price", "coef"]
    base, cost = PRODUCTS["beans"][0], PRODUCTS["beans"][1]
    q_ref = beans[beans.promo == 0].units.mean()
    grid = np.linspace(7, 20, 131)
    rev, prof, _ = profit_curve(grid, e_beans, cost, base, q_ref)
    p_star = optimal_price(e_beans, cost)
    print(f"   beans: elasticity {e_beans:.2f}, unit cost {cost:.2f} EUR, current list price {base:.2f} EUR")
    print(f"   rule for constant elasticity: p* = cost * e / (1 + e) = {cost:.2f} * {e_beans:.2f} / {1 + e_beans:.2f} = {p_star:.2f} EUR")
    print(f"   grid search over {grid[0]:.0f}-{grid[-1]:.0f} EUR: best profit at {grid[prof.argmax()]:.2f} EUR "
          f"({prof.max():,.0f} EUR/week vs {(base - cost) * q_ref:,.0f} today)")
    print(f"   markup over cost = 1 / (1 + 1/e) = {1 / (1 + 1 / e_beans):.2f}x  -> the more elastic, the smaller the markup")
    e_f = tab.loc["filters", "with_season"]
    print(f"   filters: e = {e_f:.2f} (inelastic) -> the formula says 'raise the price forever'.")
    lo, hi = df[df["product"] == "filters"].price.agg(["min", "max"])
    print(f"   Do not trust it: we only saw prices {lo:.2f}-{hi:.2f} EUR. Test a moderate increase instead.")

    print("\n6. How sure are we? Bootstrap the weeks (module 27)")
    rng = np.random.default_rng(SEED)
    boot_e, boot_p = [], []
    for _ in range(1_000):
        idx = rng.integers(0, len(beans), len(beans))
        b = beans.iloc[idx]
        e = fit(b, with_season=True, cross=caps_price[idx]).loc["log_price", "coef"]
        boot_e.append(e); boot_p.append(optimal_price(e, cost))
    boot_e, boot_p = np.array(boot_e), np.array(boot_p)
    print(f"   elasticity 95% interval [{np.percentile(boot_e, 2.5):.2f}, {np.percentile(boot_e, 97.5):.2f}]")
    print(f"   optimal price 95% interval [{np.percentile(boot_p, 2.5):.2f}, {np.percentile(boot_p, 97.5):.2f}] EUR")
    print("   The profit curve is flat near the top: a price anywhere in that interval earns almost the same,")
    _, lo_prof, _ = profit_curve(np.percentile(boot_p, [2.5, 97.5]), e_beans, cost, base, q_ref)
    print(f"   (profit at the interval ends: {lo_prof[0]:,.0f} and {lo_prof[1]:,.0f} EUR/week vs max {prof.max():,.0f})")
    print("   so move towards it step by step and measure with an A/B price test (module 12).")


if __name__ == "__main__":
    main()
