"""Module 30 - Survival analysis: time until churn, with censored customers.

Run: python 30-survival-analysis/examples/survival_demo.py
Creates data/gym_members.csv the first time (simulated, so the truth is known).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parents[2] / "data" / "gym_members.csv"
SEED = 30
N = 2_000
STUDY_MONTHS = 36                      # we look at the data at the end of month 36
# Monthly churn probability ("hazard") of each plan. Annual members can only leave at renewal (month 12, 24, ...).
HAZARD = {"monthly": 0.075, "annual_renewal": 0.35}
MONTHLY_FEE, ANNUAL_FEE_PER_MONTH = 39.0, 29.0
pd.set_option("display.width", 120)


def true_lifetime(plan, rng):
    """Simulate the full lifetime (months) of one member, ignoring the end of the study."""
    if plan == "monthly":
        return int(rng.geometric(HAZARD["monthly"]))          # month in which the member leaves
    years = int(rng.geometric(HAZARD["annual_renewal"]))     # number of years before not renewing
    return 12 * years


def make_members(seed=SEED):
    rng = np.random.default_rng(seed)
    plan = rng.choice(["monthly", "annual"], size=N, p=[0.6, 0.4])
    join = rng.integers(0, STUDY_MONTHS, size=N)              # month of joining (0..35)
    life = np.array([true_lifetime(p, rng) for p in plan])
    observed_for = STUDY_MONTHS - join                         # months we could watch each member
    churned = (life <= observed_for).astype(int)               # 1 = we SAW the churn, 0 = still active (censored)
    duration = np.where(churned == 1, life, observed_for)
    return pd.DataFrame({"member_id": np.arange(1, N + 1), "plan": plan, "join_month": join,
                         "duration": duration, "churned": churned, "true_lifetime": life})


def load():
    if not DATA.exists():
        DATA.parent.mkdir(exist_ok=True)
        make_members().to_csv(DATA, index=False)
    return pd.read_csv(DATA)


def kaplan_meier(duration, event):
    """Kaplan-Meier table: one row per month with at least one churn."""
    d = pd.DataFrame({"t": duration, "e": event})
    times = np.sort(d.loc[d.e == 1, "t"].unique())
    rows, s, var_sum = [], 1.0, 0.0
    for t in times:
        n_risk = int((d.t >= t).sum())                         # still a member at the start of month t
        n_event = int(((d.t == t) & (d.e == 1)).sum())         # left in month t
        s *= 1 - n_event / n_risk                              # survive this month, given you reached it
        if n_risk > n_event:
            var_sum += n_event / (n_risk * (n_risk - n_event))  # Greenwood's formula
        se = s * np.sqrt(var_sum)
        rows.append((t, n_risk, n_event, s, max(s - 1.96 * se, 0), min(s + 1.96 * se, 1)))
    return pd.DataFrame(rows, columns=["month", "at_risk", "churned", "survival", "ci_low", "ci_high"])


def survival_at(km, t):
    """S(t): step function, 1 before the first churn."""
    before = km[km.month <= t]
    return 1.0 if before.empty else float(before.survival.iloc[-1])


def median_lifetime(km):
    below = km[km.survival <= 0.5]
    return float(below.month.iloc[0]) if len(below) else np.nan   # NaN: half the members never left in the window


def rmst(km, horizon):
    """Restricted mean survival time = area under S(t) from 0 to horizon (months)."""
    return sum(survival_at(km, m) for m in range(horizon))        # S is constant within each whole month


def logrank(duration, event, group):
    """Log-rank test: do two groups have the same survival curve?"""
    d = pd.DataFrame({"t": duration, "e": event, "g": group})
    g1 = d.g.unique()[0]
    obs = exp = var = 0.0
    for t in np.sort(d.loc[d.e == 1, "t"].unique()):
        at_risk = d[d.t >= t]
        n, n1 = len(at_risk), int((at_risk.g == g1).sum())
        events = at_risk[(at_risk.t == t) & (at_risk.e == 1)]
        k, k1 = len(events), int((events.g == g1).sum())
        obs += k1
        exp += k * n1 / n                                         # expected churns in group 1 if curves were equal
        if n > 1:
            var += k * (n1 / n) * (1 - n1 / n) * (n - k) / (n - 1)
    chi2 = (obs - exp) ** 2 / var
    return g1, obs, exp, chi2, float(stats.chi2.sf(chi2, df=1))


def main():
    df = load()
    print(f"{len(df):,} gym members, joined between month 0 and 35, data taken at the end of month {STUDY_MONTHS}")
    print(df.head(4).to_string(index=False))

    # 1. Why censoring matters
    print("\n1. Censoring: many members have NOT churned yet - we only know they lasted 'at least' duration")
    print(f"   censored (still active): {1 - df.churned.mean():.0%} of members")
    m = df[df.plan == "monthly"]
    naive_drop = m.loc[m.churned == 1, "duration"].mean()
    naive_all = m.duration.mean()
    print(f"   monthly plan, true mean lifetime          = {1 / HAZARD['monthly']:.1f} months")
    print(f"   mean over churned members only           = {naive_drop:.1f}  (too short: long-lived members are dropped)")
    print(f"   mean over everyone, active counted as end = {naive_all:.1f}  (too short: active members are cut off)")

    # 2. Kaplan-Meier
    km_m = kaplan_meier(m.duration, m.churned)
    print("\n2. Kaplan-Meier: S(t) = product over months of (1 - churned / at risk)")
    print(km_m.head(6).round(3).to_string(index=False))
    true_s12 = (1 - HAZARD["monthly"]) ** 12
    print(f"   S(12) = {survival_at(km_m, 12):.3f}  (truth {true_s12:.3f})  -> chance a monthly member is still here after 1 year")

    # 3. Median and comparison with annual
    a = df[df.plan == "annual"]
    km_a = kaplan_meier(a.duration, a.churned)
    print("\n3. Reading the curves: median lifetime and survival at fixed dates")
    for name, km in [("monthly", km_m), ("annual", km_a)]:
        row = km[km.month <= 24].iloc[-1]
        print(f"   {name:8s} median = {median_lifetime(km):4.0f} months | S(6) = {survival_at(km, 6):.2f} | "
              f"S(13) = {survival_at(km, 13):.2f} | S(24) = {row.survival:.2f} [{row.ci_low:.2f}, {row.ci_high:.2f}]")
    print("   annual members cannot leave before month 12: flat curve, then a cliff at each renewal")

    # 4. Log-rank test
    g1, obs, exp, chi2, p = logrank(df.duration, df.churned, df.plan)
    print("\n4. Log-rank test: are the two curves different?")
    print(f"   {g1}: observed churns {obs:.0f}, expected if curves were equal {exp:.1f}")
    print(f"   chi2 = {chi2:.1f}, p = {p:.2g}  -> the plans really differ")
    print("   the test says THAT the curves differ, not HOW: always look at the plot as well")

    # 5. Hazard
    print("\n5. Hazard = churned / at risk in each month (risk of leaving NOW, given you are still here)")
    h_m = km_m[km_m.at_risk >= 100].set_index("month").eval("churned / at_risk")
    print(f"   monthly: months {int(h_m.index.min())}-{int(h_m.index.max())} (>= 100 at risk): hazard between "
          f"{h_m.min():.1%} and {h_m.max():.1%}, mean {h_m.mean():.1%} (truth {HAZARD['monthly']:.1%} every month)")
    rate = m.churned.sum() / m.duration.sum()                    # churns per member-month of exposure
    print(f"   constant-hazard shortcut: churns / member-months = {m.churned.sum()} / {m.duration.sum():,} = {rate:.3f}"
          f" -> mean lifetime 1 / h = {1 / rate:.1f} months (truth {1 / HAZARD['monthly']:.1f})")
    h_a = km_a.set_index("month").eval("churned / at_risk")
    print("   annual: hazard 0 in every month except renewals -> "
          + ", ".join(f"month {int(t)}: {v:.0%}" for t, v in h_a.items() if t < STUDY_MONTHS))
    print("   -> plan retention campaigns for annual members in month 11, for monthly members from day 1")

    # 6. Expected lifetime and value
    print("\n6. From survival to value: restricted mean lifetime (area under S up to 36 months)")
    for name, km, fee in [("monthly", km_m, MONTHLY_FEE), ("annual", km_a, ANNUAL_FEE_PER_MONTH)]:
        life = rmst(km, STUDY_MONTHS)
        print(f"   {name:8s} expected months in first 3 years = {life:5.1f}  x {fee:.0f} EUR = {life * fee:6.0f} EUR per member")
    print("   annual members pay less per month but stay much longer -> more revenue per member")


if __name__ == "__main__":
    main()
