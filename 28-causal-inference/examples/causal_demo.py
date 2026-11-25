"""Module 28 - Causal inference basics: correlation is not causation.

Part A: a fictional coffee chain launches a loyalty card. Members spend more -
but engaged customers were more likely to join anyway (confounding). We compare
the naive difference with stratified and regression-adjusted estimates.
Part B: Simpson's paradox in an e-mail campaign, and collider (selection) bias.
Part C: difference-in-differences: 8 of 20 stores open later in the evening
from week 14. data/stores_weekly.csv and data/loyalty.csv are created if missing.
Only numpy + pandas.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LOYALTY = ROOT / "data" / "loyalty.csv"
STORES = ROOT / "data" / "stores_weekly.csv"
SEED = 28
TRUE_CARD_EFFECT = 4.0       # EUR per month: what the card REALLY adds (known only because we simulate)
TRUE_HOURS_EFFECT = 150.0    # EUR per store-week: what the late opening REALLY adds
N_WEEKS, START_WEEK = 26, 14


def make_loyalty(path=LOYALTY, seed=SEED):
    """2,000 customers. visits_before (engagement) drives BOTH joining and spending: a confounder."""
    rng = np.random.default_rng(seed)
    n = 2_000
    visits = rng.poisson(lam=rng.gamma(3, 1.5, n)).clip(0, 15)              # visits per month before launch
    p_join = 1 / (1 + np.exp(-(-2.2 + 0.45 * visits)))                       # engaged customers join more often
    member = rng.binomial(1, p_join)
    spend = 12 + 6.0 * visits + TRUE_CARD_EFFECT * member + rng.normal(0, 6, n)
    df = pd.DataFrame({"customer_id": np.arange(1, n + 1), "visits_before": visits,
                       "member": member, "spend_after": spend.clip(0).round(2)})
    df.to_csv(path, index=False)
    return df


def make_stores(path=STORES, seed=SEED):
    """20 stores x 26 weeks. Treated stores are bigger; all stores share a common trend + seasonality."""
    rng = np.random.default_rng(seed + 1)
    rows = []
    for store in range(1, 21):
        treated = int(store <= 8)                                            # stores 1-8 open later
        level = rng.normal(5_200 if treated else 4_300, 250)                # treated stores are bigger
        for week in range(1, N_WEEKS + 1):
            trend = 18 * week + 120 * np.sin(week / 4)                        # shared by every store
            post = int(week >= START_WEEK)
            sales = level + trend + TRUE_HOURS_EFFECT * treated * post + rng.normal(0, 90)
            rows.append((store, week, treated, post, round(sales, 2)))
    df = pd.DataFrame(rows, columns=["store", "week", "treated", "post", "sales"])
    df.to_csv(path, index=False)
    return df


def load(path, maker):
    return pd.read_csv(path) if path.exists() else maker()


def ols(y, X, names):
    """Least squares with classic standard errors. X must already include a constant column."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sigma2 = resid @ resid / (len(y) - X.shape[1])
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))
    return pd.DataFrame({"coef": beta, "se": se, "ci_low": beta - 1.96 * se, "ci_high": beta + 1.96 * se}, index=names)


def stratified_effect(df, treat, outcome, strata):
    """Compare treated vs untreated INSIDE each stratum, then average weighted by stratum size."""
    g = df.groupby([strata, treat])[outcome].mean().unstack()
    sizes = df.groupby(strata).size()
    diff = (g[1] - g[0]).dropna()
    return diff, (diff * sizes[diff.index]).sum() / sizes[diff.index].sum()


def campaign_table():
    """Simpson's paradox: e-mail A wins in every segment but loses overall."""
    return pd.DataFrame({"segment": ["new", "new", "returning", "returning"],
                         "email": ["A", "B", "A", "B"],
                         "sent": [400, 100, 100, 400],
                         "bought": [40, 8, 30, 112]})


def did_table(df):
    """2 x 2 table of mean sales: (control/treated) x (before/after)."""
    t = df.groupby(["treated", "post"]).sales.mean().unstack()
    t.index, t.columns = ["control", "treated"], ["before", "after"]
    t["change"] = t.after - t.before
    return t


if __name__ == "__main__":
    pd.set_option("display.width", 120)
    rng = np.random.default_rng(SEED)
    loyalty = load(LOYALTY, make_loyalty)
    stores = load(STORES, make_stores)

    print("1. The naive comparison: do loyalty members spend more?")
    means = loyalty.groupby("member").spend_after.mean()
    naive = means[1] - means[0]
    print(f"   members {means[1]:.2f} EUR/month vs non-members {means[0]:.2f}  -> naive 'effect' = {naive:+.2f} EUR")
    print(f"   but members visited more BEFORE the card existed: "
          f"{loyalty[loyalty.member == 1].visits_before.mean():.1f} vs {loyalty[loyalty.member == 0].visits_before.mean():.1f} visits/month")
    print(f"   corr(visits_before, member) = {loyalty.visits_before.corr(loyalty.member):.2f}, "
          f"corr(visits_before, spend) = {loyalty.visits_before.corr(loyalty.spend_after):.2f}  -> a confounder")

    print("\n2. Adjusting for the confounder")
    loyalty["band"] = pd.cut(loyalty.visits_before, [-1, 1, 3, 5, 8, 15], labels=["0-1", "2-3", "4-5", "6-8", "9+"])
    by_band, strat = stratified_effect(loyalty, "member", "spend_after", "band")
    print("   member - non-member difference INSIDE each engagement band:")
    print("   " + "  ".join(f"{b}: {d:+.2f}" for b, d in by_band.items()))
    print(f"   stratified estimate (weighted by band size) = {strat:+.2f} EUR")
    X = np.column_stack([np.ones(len(loyalty)), loyalty.member, loyalty.visits_before])
    reg = ols(loyalty.spend_after, X, ["const", "member", "visits_before"])
    print("   regression  spend_after ~ member + visits_before:")
    print(reg.round(2).to_string().replace("\n", "\n   ").join(["   ", ""]))
    print(f"   naive {naive:+.2f}  |  stratified {strat:+.2f}  |  regression {reg.coef['member']:+.2f}  |  "
          f"truth {TRUE_CARD_EFFECT:+.2f} (known only because the data is simulated)")

    print("\n3. Simpson's paradox: which e-mail converts better?")
    camp = campaign_table()
    camp["rate"] = camp.bought / camp.sent
    print(camp.pivot(index="segment", columns="email", values="rate").map("{:.1%}".format).to_string()
          .replace("\n", "\n   ").join(["   ", ""]))
    overall = camp.groupby("email")[["sent", "bought"]].sum()
    overall["rate"] = overall.bought / overall.sent
    print(f"   overall: A {overall.rate['A']:.1%}  vs  B {overall.rate['B']:.1%}")
    print("   A wins in BOTH segments but loses overall: A was mostly sent to new customers, who rarely buy.")
    print("   The segment (a confounder) decides which table to trust: here, compare within segments.")

    print("\n4. Collider bias: 'featured' apps look like a trade-off that does not exist")
    rating, downloads = rng.normal(0, 1, 5_000), rng.normal(0, 1, 5_000)   # independent by construction
    featured = (rating + downloads) > 1.5                                   # featured if good OR popular
    print(f"   corr(rating, downloads), all apps      = {np.corrcoef(rating, downloads)[0, 1]:+.2f}")
    print(f"   corr(rating, downloads), featured only = {np.corrcoef(rating[featured], downloads[featured])[0, 1]:+.2f}")
    print("   Selecting on a common EFFECT creates a fake negative link. Do not 'control' for a collider.")

    print("\n5. Difference-in-differences: did the later opening hours raise sales?")
    t = did_table(stores)
    print(t.round(1).to_string().replace("\n", "\n   ").join(["   ", ""]))
    after_only = t.after["treated"] - t.after["control"]
    before_after = t.change["treated"]
    did = t.change["treated"] - t.change["control"]
    print(f"   after-only comparison (treated - control) = {after_only:+.1f}  <- includes 'bigger stores' bias")
    print(f"   before/after in treated stores only     = {before_after:+.1f}  <- includes the common trend")
    print(f"   difference-in-differences               = {did:+.1f}  (truth {TRUE_HOURS_EFFECT:+.0f})")
    X = np.column_stack([np.ones(len(stores)), stores.treated, stores.post, stores.treated * stores.post])
    did_reg = ols(stores.sales, X, ["const", "treated", "post", "treated_x_post"])
    r = did_reg.loc["treated_x_post"]
    print(f"   regression sales ~ treated + post + treated:post -> effect {r.coef:+.1f}, 95% CI [{r.ci_low:.1f}, {r.ci_high:.1f}]")
    fe = pd.get_dummies(stores[["store", "week"]].astype(str), drop_first=True).astype(float)
    X = np.column_stack([np.ones(len(stores)), stores.treated * stores.post, fe])
    r = ols(stores.sales, X, ["const", "treated_x_post", *fe.columns]).loc["treated_x_post"]
    print(f"   + store and week fixed effects (two-way FE)       -> effect {r.coef:+.1f}, 95% CI [{r.ci_low:.1f}, {r.ci_high:.1f}]")

    print("\n6. Checking the parallel-trends assumption")
    pre = stores[stores.week < START_WEEK]
    gap = pre.groupby(["week", "treated"]).sales.mean().unstack()
    gap = gap[1] - gap[0]
    slope = np.polyfit(gap.index, gap.values, 1)[0]
    print(f"   pre-period gap treated - control: week 1 {gap.iloc[0]:.0f}, week {START_WEEK - 1} {gap.iloc[-1]:.0f}, "
          f"slope {slope:+.1f} EUR/week (close to 0 = parallel)")
    placebo = pre.assign(post=(pre.week >= 7).astype(int))
    Xp = np.column_stack([np.ones(len(placebo)), placebo.treated, placebo.post, placebo.treated * placebo.post])
    p = ols(placebo.sales, Xp, ["const", "treated", "post", "treated_x_post"]).loc["treated_x_post"]
    print(f"   placebo test (fake start at week 7, pre-period only): effect {p.coef:+.1f}, 95% CI [{p.ci_low:.1f}, {p.ci_high:.1f}]")
    print("   The placebo CI includes 0: no 'effect' before the real change -> the design is credible.")
