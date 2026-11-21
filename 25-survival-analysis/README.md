# Module 25 – Survival Analysis (bonus)

"How long will a customer stay?" is a different question from "will this customer churn?" (module 15). **Survival analysis** answers *how long until an event happens*: a subscriber cancels, a machine breaks, a patient relapses, an employee resigns, a loan defaults – or a Git branch gets merged (see the Git corner). Its key idea is to use **every** customer correctly, including the ones who have *not* left yet.

This module builds the Kaplan-Meier estimator and the log-rank test from scratch on 800 subscribers.

Run it: `python 25-survival-analysis/examples/survival_demo.py` (numpy + scipy; it creates `data/subscriptions.csv` the first time).
Rebuild the diagrams: `python 25-survival-analysis/diagrams/make_diagrams.py`.

## 1. The data: duration + event flag
Each row is one subscriber:
```
customer_id,plan,signup_month,months,churned
1,monthly,5,1,1
7,annual,3,21,0
```
- `months` = how long we **observed** the customer (from signup to cancellation *or* to today).
- `churned` = 1 if they cancelled (the **event**), 0 if they are still active (**censored**).

```
1. Data: 800 subscribers, 330 cancelled, 470 still active (censored)
   monthly: 479   annual: 321
```

## 2. Censoring – why ordinary averages lie
Diagram: [`diagrams/censoring.pdf`](diagrams/censoring.pdf)

Customers join at different times, so on the analysis date some have been watched for 2 months, others for 20. For an active customer we don't know the lifetime, only that it is **at least** `months`. That is called **right censoring**. The two "obvious" averages are both wrong:
```
2. The naive (wrong) averages
   mean months of churners only      =   7.2  (ignores the loyal ones)
   mean months of everybody          =   8.8  (treats 'still active' as 'left')
```
Both answers are far too low: the real median lifetime is 14 months (below). Dropping the censored customers throws away exactly the loyal ones; counting them as "left" cuts their lifetime short. Survival analysis keeps them in the calculation for as long as we watched them.

## 3. The Kaplan-Meier estimator
Diagram: [`diagrams/kaplan_meier.pdf`](diagrams/kaplan_meier.pdf)

**S(t)** is the probability of still being subscribed after t months. Kaplan-Meier builds it month by month: of the customers still being watched at month t (**at risk**, n), d cancel, so the chance of surviving that month is `1 − d/n`. Multiply the monthly chances together:

S(t) = ∏ (1 − dᵢ / nᵢ) over all months tᵢ ≤ t

```python
def kaplan_meier(t, e):
    times = np.unique(t[e == 1])
    S, s = [], 1.0
    for u in times:
        n = (t >= u).sum()                 # still being watched just before u
        d = ((t == u) & (e == 1)).sum()    # cancelled at u
        s *= 1 - d / n
        S.append(s)
    return times, np.array(S)
```
```
3. Kaplan-Meier table (first 6 months, all customers)
   month  at_risk  cancelled  S(t)
       1      800         38  0.953
       2      723         38  0.902
       3      655         23  0.871
```
Notice that the risk set drops from 800 to 723 although only 38 cancelled: the other 39 were customers who signed up recently and were censored after 1 month. **A censored customer counts in n while observed, then quietly leaves the risk set** – no guessing about their future.

The **median lifetime** is where the curve crosses 0.5: 14 months for all customers – much more than the naive 7–9 months.

## 4. Comparing groups: curves and the log-rank test
Diagram: [`diagrams/km_by_plan.pdf`](diagrams/km_by_plan.pdf)
```
4. Reading the curves
   monthly  S(6) = 0.69   S(12) = 0.44   median lifetime = 11 months
   annual   S(6) = 0.85   S(12) = 0.70   median lifetime = 24 months
```
After a year 70% of annual subscribers are still here versus 44% of monthly ones. (The annual median of 24 sits on the very last month, where only a handful of customers are still at risk: the tail of a KM curve is always uncertain. Report S(12) rather than a median the data barely reaches.)

Is the gap real or noise? The **log-rank test** (a chi-square test, module 08) compares, month by month, how many monthly customers cancelled with how many we would *expect* if both plans had the same survival:
```
5. Log-rank test monthly vs annual
   monthly cancellations observed = 242, expected if plans were equal = 177.2
   chi2 = 54.5, p-value = 1.6e-13
```
In Python libraries: `lifelines.KaplanMeierFitter` and `lifelines.statistics.logrank_test` give the same numbers with confidence bands.

## 5. Hazard – the risk *right now*
Diagram: [`diagrams/hazard.pdf`](diagrams/hazard.pdf)

The **hazard** is the share of customers still present who leave in a given month: `d / n`. It answers "how dangerous is month 3?" and shows *when* to act (e.g. an onboarding email before the first renewal).
```
6. Hazard: cancellations per customer-month
   monthly 0.064  annual 0.027  -> hazard ratio 2.40
```
A monthly subscriber is **2.4 times** as likely to cancel in any given month. The **Cox proportional hazards model** (`lifelines.CoxPHFitter`) is the regression version of this idea (module 09): it estimates a hazard ratio for each feature (plan, support calls, country…) at once.

## 6. Pitfalls
- **Never drop censored rows**, and never replace their duration with a guess.
- Censoring must be **non-informative**: customers you stop watching must not be leaving *because* they are about to churn (e.g. people who downgraded to a free plan you no longer track).
- Define the **start (time 0)** and the **event** precisely: signup or first payment? cancellation or end of the paid period?
- Don't read the far right of the curve too seriously – look at the "at risk" numbers.
- Customer **lifetime value** ≈ monthly revenue × area under S(t). Survival curves feed directly into finance.

## Git corner: the lifetime of a branch
Diagram: [`diagrams/git_branch_lifecycle.pdf`](diagrams/git_branch_lifecycle.pdf)

Every lesson in this course lives on a branch: created, committed to, pushed, reviewed in a pull request and **merged into `main`**. A merged branch is an "event"; a branch that is still open is "censored" – it may be merged tomorrow or abandoned. Long-lived branches drift away from `main` and cause painful conflicts, so teams track this survival curve too.
```bash
git branch --merged main            # branches already in main: safe to delete
git branch --no-merged main         # still "at risk": open work
git for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short)' refs/heads
                                    # branches with their last commit date, newest first
git log main..feature --oneline     # what the branch has that main does not
git branch -d feature               # delete a merged branch (-D forces, careful!)
git push origin --delete feature    # delete it on GitHub too
git fetch --prune                   # drop local copies of branches deleted on the remote
```
More commands are in the [Git notes](../git-notes/README.md#branch-lifecycle-merged-branches-and-pruning).

## Exercises
1. Plot S(t) separately for customers who signed up in the first and the second year. Do the curves differ?
2. Compute the **restricted mean lifetime** up to 24 months (the area under the KM curve) for each plan. How much longer does an annual customer stay on average?
3. Add a 95% confidence band with Greenwood's formula: Var(S) = S² · Σ dᵢ / (nᵢ(nᵢ − dᵢ)).
4. Run `git for-each-ref` on a repository you know. How many branches are not merged and older than one month?
