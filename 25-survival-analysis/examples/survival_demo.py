"""Module 25 - Survival analysis: how long until customers churn?

Creates data/subscriptions.csv (if missing): 800 subscribers observed for
at most 24 months, with their plan, how many months we watched them and
whether they cancelled (1) or were still active at the end (0 = censored).
Then builds Kaplan-Meier curves by hand, reads median lifetimes and runs a
log-rank test between the monthly and the annual plan.
"""
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "subscriptions.csv"
PLANS = {"monthly": 11.0, "annual": 30.0}   # true median lifetime in months


def make_data(path=DATA, n=800, seed=25):
    rng = np.random.default_rng(seed)
    rows = ["customer_id,plan,signup_month,months,churned"]
    for c in range(1, n + 1):
        plan = "monthly" if rng.random() < .6 else "annual"
        lifetime = rng.exponential(PLANS[plan] / np.log(2))       # months until cancel
        signup = int(rng.integers(0, 24))                         # joined during the 2 years
        follow = 24 - signup                                      # months we could watch
        months = max(1, int(np.ceil(min(lifetime, follow))))
        churned = int(lifetime <= follow)
        rows.append(f"{c},{plan},{signup},{months},{churned}")
    path.write_text("\n".join(rows) + "\n")


def load():
    if not DATA.exists():
        make_data()
    raw = np.genfromtxt(DATA, delimiter=",", names=True, dtype=None, encoding="utf-8")
    return raw["plan"], raw["months"].astype(int), raw["churned"].astype(int)


def kaplan_meier(t, e):
    """Return event times, S(t), numbers at risk and events at each time."""
    times = np.unique(t[e == 1])
    S, s, at_risk, events = [], 1.0, [], []
    for u in times:
        n = (t >= u).sum()                 # still being watched just before u
        d = ((t == u) & (e == 1)).sum()    # cancelled at u
        s *= 1 - d / n
        S.append(s); at_risk.append(n); events.append(d)
    return times, np.array(S), np.array(at_risk), np.array(events)


def median_survival(times, S):
    below = np.where(S <= .5)[0]
    return times[below[0]] if len(below) else np.inf


def survival_at(times, S, m):
    idx = np.where(times <= m)[0]
    return 1.0 if len(idx) == 0 else S[idx[-1]]


def logrank(t, e, g):
    """Log-rank test: are the two survival curves the same?"""
    O = E = V = 0.0
    for u in np.unique(t[e == 1]):
        n = (t >= u).sum(); n1 = ((t >= u) & g).sum()
        d = ((t == u) & (e == 1)).sum(); d1 = ((t == u) & (e == 1) & g).sum()
        O += d1; E += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    stat = (O - E) ** 2 / V
    return O, E, stat, chi2.sf(stat, 1)


def main():
    plan, t, e = load()
    print(f"1. Data: {len(t)} subscribers, {e.sum()} cancelled, {len(t) - e.sum()} still active (censored)")
    print(f"   monthly: {(plan == 'monthly').sum()}   annual: {(plan == 'annual').sum()}")

    print("\n2. The naive (wrong) averages")
    print(f"   mean months of churners only      = {t[e == 1].mean():5.1f}  (ignores the loyal ones)")
    print(f"   mean months of everybody          = {t.mean():5.1f}  (treats 'still active' as 'left')")

    times, S, n, d = kaplan_meier(t, e)
    print("\n3. Kaplan-Meier table (first 6 months, all customers)")
    print("   month  at_risk  cancelled  S(t)")
    for i in range(6):
        print(f"   {times[i]:5d}  {n[i]:7d}  {d[i]:9d}  {S[i]:.3f}")

    print("\n4. Reading the curves")
    for p in ("monthly", "annual"):
        m = plan == p
        tt, SS, _, _ = kaplan_meier(t[m], e[m])
        med = median_survival(tt, SS)
        med_s = f"{med:.0f} months" if np.isfinite(med) else "not reached (> 24 months)"
        print(f"   {p:8s} S(6) = {survival_at(tt, SS, 6):.2f}   S(12) = {survival_at(tt, SS, 12):.2f}"
              f"   median lifetime = {med_s}")

    O, E, stat, p = logrank(t, e, plan == "monthly")
    print("\n5. Log-rank test monthly vs annual")
    print(f"   monthly cancellations observed = {O:.0f}, expected if plans were equal = {E:.1f}")
    print(f"   chi2 = {stat:.1f}, p-value = {p:.2g}")

    m = plan == "monthly"
    hz = e[m].sum() / t[m].sum(), e[~m].sum() / t[~m].sum()
    print("\n6. Hazard: cancellations per customer-month")
    print(f"   monthly {hz[0]:.3f}  annual {hz[1]:.3f}  -> hazard ratio {hz[0] / hz[1]:.2f}")


if __name__ == "__main__":
    main()
