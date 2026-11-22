"""Module 25 - Cohort & retention analysis, plus a Kaplan-Meier survival curve.

Creates data/subscriptions.csv (if missing): 1,200 customers of a fictional
subscription app, with signup month, plan, and the month they cancelled
(empty if still active on 2026-12, the end of observation).
Builds an activity log, a cohort retention table, and a Kaplan-Meier curve
that correctly handles customers who have not churned *yet* (censoring).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "subscriptions.csv"
END = pd.Period("2026-12", "M")          # last month we can observe
MONTHS = pd.period_range("2026-01", "2026-12", freq="M")


def make_data(path=DATA, n=1200, seed=25):
    rng = np.random.default_rng(seed)
    rows = []
    for cid in range(1, n + 1):
        signup = MONTHS[rng.integers(0, 12)]
        plan = "annual" if rng.random() < 0.3 else "monthly"
        # monthly churn hazard: high in the first month, lower later; annual plan stays longer;
        # cohorts from Jul onward benefit from a new onboarding flow (lower early churn)
        better = signup >= pd.Period("2026-07", "M")
        churn = None
        for age in range(1, (END - signup).n + 1):
            h = (0.30 if age == 1 else 0.08) * (0.35 if plan == "annual" else 1.0)
            if better and age == 1:
                h *= 0.55
            if rng.random() < h:
                churn = signup + age
                break
        rows.append(dict(customer_id=cid, signup_month=str(signup), plan=plan,
                         churn_month="" if churn is None else str(churn)))
    pd.DataFrame(rows).to_csv(path, index=False)


def load():
    if not DATA.exists():
        make_data()
    df = pd.read_csv(DATA, dtype={"churn_month": str}, keep_default_na=False)
    df["signup"] = pd.PeriodIndex(df["signup_month"], freq="M")
    df["churn"] = [pd.Period(m, "M") if m else pd.NaT for m in df["churn_month"]]
    return df


def activity_log(df):
    """One row per (customer, active month): the typical 'events' table of a product."""
    rows = []
    for r in df.itertuples():
        last = (r.churn - 1) if r.churn is not pd.NaT else END
        for m in pd.period_range(r.signup, last, freq="M"):
            rows.append((r.customer_id, m))
    return pd.DataFrame(rows, columns=["customer_id", "month"])


def cohort_table(df, log):
    first = df.set_index("customer_id")["signup"]
    log = log.assign(cohort=log["customer_id"].map(first))
    log["age"] = (log["month"] - log["cohort"]).apply(lambda d: d.n)   # months since signup
    counts = log.groupby(["cohort", "age"])["customer_id"].nunique().unstack()
    size = counts[0].astype(int)
    return counts, counts.div(size, axis=0), size


def kaplan_meier(durations, observed):
    """durations: months survived; observed: 1 = churned, 0 = still active (censored)."""
    d = np.asarray(durations); e = np.asarray(observed)
    times = np.unique(d[e == 1])
    s, curve = 1.0, [(0, 1.0, len(d))]
    for t in times:
        at_risk = (d >= t).sum()
        deaths = ((d == t) & (e == 1)).sum()
        s *= 1 - deaths / at_risk
        curve.append((int(t), s, int(at_risk)))
    return pd.DataFrame(curve, columns=["month", "survival", "at_risk"])


def durations(df):
    dur = [(r.churn - r.signup).n if r.churn is not pd.NaT else (END - r.signup).n for r in df.itertuples()]
    obs = [int(r.churn is not pd.NaT) for r in df.itertuples()]
    return np.array(dur), np.array(obs)


def main():
    df = load()
    log = activity_log(df)
    print(f"1. Data: {len(df)} customers, {len(log)} active customer-months, "
          f"{(df.churn_month != '').mean():.0%} have churned by {END}")
    print(log.head(4).to_string(index=False))

    counts, ret, size = cohort_table(df, log)
    print("\n2. Cohort retention (% of the signup cohort still active, by months since signup)")
    show = ret.iloc[:, :7] * 100
    show.insert(0, "size", size)
    print(show.to_string(na_rep=".", float_format=lambda v: f"{v:.0f}"))

    print("\n3. Read it three ways")
    print(f"   row    (one cohort over time):  Jan cohort {ret.iloc[0, 1]:.0%} after 1 month, "
          f"{ret.iloc[0, 6]:.0%} after 6")
    print(f"   column (same age, compare cohorts): month-1 retention Jan-Jun avg "
          f"{ret.iloc[:6, 1].mean():.0%}, Jul-Nov avg {ret.iloc[6:11, 1].mean():.0%}")
    active = log.groupby("month")["customer_id"].nunique()
    print(f"   diagonal (calendar month): active customers {active.iloc[0]} in Jan -> {active.iloc[-1]} in Dec")

    print("\n4. The naive churn rate is biased")
    recent = df[df.signup >= pd.Period("2026-10", "M")]
    print(f"   'share churned' for Oct-Dec signups: {(recent.churn_month != '').mean():.0%} "
          f"(they had only 0-2 months to churn!)")
    d, e = durations(df)
    print(f"   naive average lifetime of churned customers only: {d[e == 1].mean():.1f} months (ignores survivors)")

    km = kaplan_meier(d, e)
    print("\n5. Kaplan-Meier survival (uses censored customers correctly)")
    print(km.head(8).round(3).to_string(index=False))
    med = km.loc[km.survival <= 0.5, "month"]
    print(f"   median lifetime: {med.iloc[0] if len(med) else '> 11'} months")

    print("\n6. Survival by plan")
    for plan in ("monthly", "annual"):
        m = df.plan == plan
        k = kaplan_meier(d[m], e[m]).set_index("month")["survival"]
        s6 = k[k.index <= 6].iloc[-1]
        print(f"   {plan:<8} n={m.sum():4d}   still active after 6 months: {s6:.0%}")


if __name__ == "__main__":
    main()
