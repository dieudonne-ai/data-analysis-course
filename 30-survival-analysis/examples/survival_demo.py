"""Module 30 - Survival analysis: time-to-event data and churn.

A fictional meal-kit company tracks 1,500 subscribers who signed up during 2025.
The analysis is done on 2026-01-01: customers who are still subscribed are
"censored" - we know they stayed AT LEAST this long, not when they will leave.
We compare naive averages with the Kaplan-Meier estimator, add Greenwood
confidence intervals, compare two plans with a log-rank test, look at the
hazard (when do people leave?) and compute the restricted mean survival time.
data/survival.csv is created if missing. numpy + pandas + scipy only.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
SURVIVAL = ROOT / "data" / "survival.csv"
SEED = 30
N = 1_500
CUTOFF = pd.Timestamp("2026-01-01")
# plan: (share of customers, Weibull scale in days, monthly price EUR)
PLANS = {"weekly": (0.6, 160, 60.0), "flex": (0.4, 420, 45.0)}
SHAPE = 0.8  # < 1: the risk of leaving is highest at the start and falls over time


def make_survival(path=SURVIVAL, seed=SEED):
    """One row per customer: signup date, plan, observed days, churned flag (1) or censored (0)."""
    rng = np.random.default_rng(seed)
    signup = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, N), unit="D")
    plan = rng.choice(list(PLANS), N, p=[v[0] for v in PLANS.values()])
    scale = np.array([PLANS[p][1] for p in plan])
    true_days = np.ceil(scale * rng.weibull(SHAPE, N)).astype(int)         # when they WOULD leave
    follow_up = (CUTOFF - signup).days.to_numpy()                           # how long we could watch them
    churned = (true_days <= follow_up).astype(int)
    days = np.where(churned == 1, true_days, follow_up)
    df = pd.DataFrame({"customer_id": np.arange(1, N + 1), "signup": signup.date, "plan": plan,
                       "days": days, "churned": churned})
    df.to_csv(path, index=False)
    return df


def load(path=SURVIVAL):
    return pd.read_csv(path) if path.exists() else make_survival(path)


def kaplan_meier(days, event):
    """Kaplan-Meier table: at each event time t, S(t) = product of (1 - d/n) so far.

    n = at risk just before t (still observed), d = churned at t.
    Greenwood's formula gives the variance; the 95% band uses the log(-log) transform
    so it stays between 0 and 1.
    """
    d = pd.DataFrame({"t": days, "e": event})
    g = d.groupby("t").agg(d=("e", "sum"), c=("e", lambda x: (x == 0).sum())).reset_index()
    g["n"] = len(d) - g["d"].shift(fill_value=0).cumsum() - g["c"].shift(fill_value=0).cumsum()
    g = g[g.d > 0].copy()
    g["surv"] = (1 - g.d / g.n).cumprod()
    var_term = (g.d / (g.n * (g.n - g.d))).cumsum()                         # Greenwood
    se = np.sqrt(var_term) / np.abs(np.log(g.surv))
    g["lo"] = g.surv ** np.exp(1.96 * se)
    g["hi"] = g.surv ** np.exp(-1.96 * se)
    return g[["t", "n", "d", "surv", "lo", "hi"]].reset_index(drop=True)


def surv_at(km, t):
    """S(t) read from a KM table (a step function: last value at or before t)."""
    before = km[km.t <= t]
    return 1.0 if before.empty else before.surv.iloc[-1]


def median_survival(km):
    """First time S(t) drops to 0.5 or below (NaN if it never does)."""
    below = km[km.surv <= 0.5]
    return below.t.iloc[0] if len(below) else np.nan


def rmst(km, horizon):
    """Restricted mean survival time = area under S(t) from 0 to horizon (expected days, capped)."""
    t = np.r_[0, km.t[km.t < horizon], horizon]
    s = np.r_[1, km.surv[km.t < horizon]]
    return float(np.sum(np.diff(t) * s))


def logrank(days, event, group):
    """Log-rank test: at each event time compare observed vs expected churns in group A."""
    d = pd.DataFrame({"t": days, "e": event, "g": group})
    a = d.g == d.g.unique()[0]
    times = np.sort(d.t[d.e == 1].unique())
    obs = exp = var = 0.0
    for t in times:
        at_risk = d.t >= t
        n, n_a = at_risk.sum(), (at_risk & a).sum()
        dt = ((d.t == t) & (d.e == 1)).sum()
        dt_a = ((d.t == t) & (d.e == 1) & a).sum()
        obs += dt_a
        exp += dt * n_a / n
        if n > 1:
            var += dt * (n_a / n) * (1 - n_a / n) * (n - dt) / (n - 1)
    chi2 = (obs - exp) ** 2 / var
    return obs, exp, chi2, stats.chi2.sf(chi2, df=1)


def life_table(days, event, width=30, max_t=360):
    """Monthly hazard: share of customers at risk at the start of each 30-day window who leave in it."""
    rows = []
    for start in range(0, max_t, width):
        at_risk = days > start
        left = at_risk & (days <= start + width) & (event == 1)
        censored = at_risk & (days <= start + width) & (event == 0)
        n_eff = at_risk.sum() - censored.sum() / 2                          # actuarial correction
        rows.append((start, start + width, at_risk.sum(), left.sum(), left.sum() / n_eff))
    return pd.DataFrame(rows, columns=["from", "to", "at_risk", "churned", "hazard"])


def main():
    df = load()
    days, ev = df.days.to_numpy(), df.churned.to_numpy()

    print("1. Censoring: why the simple average is wrong")
    print(f"   {len(df)} subscribers, {ev.sum()} churned, {(ev == 0).sum()} still active on {CUTOFF.date()} (censored)")
    print(f"   mean tenure of churned customers only : {days[ev == 1].mean():6.0f} days  (ignores everyone who stayed)")
    print(f"   mean of all observed days             : {days.mean():6.0f} days  (treats 'still active' as 'left today')")
    print(f"   share churned                         : {ev.mean():6.1%}      (depends on WHEN you look)")
    print("   All three are biased DOWN: the longest customers are exactly the ones we have not seen leave yet.")

    print("\n2. Kaplan-Meier: S(t) = product of (1 - churned / at risk) at each event time")
    km = kaplan_meier(days, ev)
    first = km.head(4).copy()
    first["1 - d/n"] = 1 - first.d / first.n
    print(first[["t", "n", "d", "1 - d/n", "surv"]].round(4).to_string(index=False).replace("\n", "\n   ").join(["   ", ""]))
    for t in (30, 90, 180, 365):
        row = km[km.t <= t].iloc[-1]
        print(f"   S({t:3d}) = {row.surv:.1%}  95% CI [{row.lo:.1%}, {row.hi:.1%}]")
    print(f"   median survival = {median_survival(km)} days (half the customers have left by then)")

    print("\n3. Compare plans: Kaplan-Meier per group + log-rank test")
    res = {}
    for p in PLANS:
        sub = df[df.plan == p]
        k = kaplan_meier(sub.days, sub.churned)
        res[p] = k
        print(f"   {p:6s}: n={len(sub):4d}  S(90)={surv_at(k, 90):.1%}  S(365)={surv_at(k, 365):.1%}  "
              f"median={median_survival(k):.0f} days")
    obs, exp, chi2, pval = logrank(days, ev, df.plan.to_numpy())
    grp = df.plan.unique()[0]
    print(f"   log-rank: {grp} churned {obs:.0f} vs {exp:.1f} expected if the plans were equal; "
          f"chi2 = {chi2:.1f}, p = {pval:.1e}")
    print("   The plans differ. Careful: customers CHOSE their plan, so this is not (yet) a causal effect (module 28).")

    print("\n4. The hazard: WHEN do customers leave?")
    lt = life_table(days, ev)
    print(lt.head(6).assign(hazard=lambda x: x.hazard.map("{:.1%}".format)).to_string(index=False)
          .replace("\n", "\n   ").join(["   ", ""]))
    late = lt[lt.at_risk >= 150].iloc[-1]                                  # last window with enough data
    print(f"   month 1 hazard {lt.hazard.iloc[0]:.1%} vs month {late['to'] // 30:.0f} hazard {late.hazard:.1%} "
          f"({late.at_risk:.0f} at risk): the risk FALLS with tenure -> invest in onboarding (the first 30 days).")
    print("   Few customers are followed for a full year, so late windows are noisy: always show 'at risk'.")

    print("\n5. Restricted mean survival time (RMST) and first-year revenue")
    for p, (_, _, price) in PLANS.items():
        r = rmst(res[p], 365)
        print(f"   {p:6s}: RMST(365) = {r:5.0f} days = {r / 30.4:4.1f} months  x {price:.0f} EUR "
              f"= {r / 30.4 * price:5.0f} EUR first-year revenue per signup")
    print("   RMST = area under the KM curve up to a horizon: a mean that is valid with censoring.")

    print("\n6. Sanity check against the truth (we simulated the data)")
    for p, (_, scale, _) in PLANS.items():
        true_med = scale * np.log(2) ** (1 / SHAPE)
        print(f"   {p:6s}: true median {true_med:4.0f} days, KM median {median_survival(res[p]):4.0f} days")


if __name__ == "__main__":
    main()
