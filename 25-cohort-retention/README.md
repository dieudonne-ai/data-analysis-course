# Module 25 – Cohort & Retention Analysis (bonus)

"We gained 100 customers this month!" – but how many of last month's customers are still here? Growth numbers hide **churn** (customers who leave). **Cohort analysis** groups customers by *when they started* and follows each group over time, so you can see whether the product keeps people better or worse than before. **Survival analysis** (Kaplan-Meier) then answers "how long does a customer stay?" without being fooled by customers who simply haven't left *yet*.

The example uses 1,200 customers of a fictional subscription app, signing up between January and December 2026.

Run it: `python 25-cohort-retention/examples/cohort_demo.py` (pandas + numpy; it creates `data/subscriptions.csv` the first time).
Rebuild the diagrams: `python 25-cohort-retention/diagrams/make_diagrams.py`.

## 1. The data: one row per customer, one row per active month
```
customer_id,signup_month,plan,churn_month
1,2026-07,monthly,
2,2026-02,annual,2026-05
```
An empty `churn_month` means "still active in December 2026", the last month we can observe. Most products store an **activity log** instead (one row per user per active day or month); the script builds one:
```
1. Data: 1200 customers, 5549 active customer-months, 35% have churned by 2026-12
 customer_id   month
           1 2026-07
           1 2026-08
```

## 2. Building the cohort table
Diagram: [`diagrams/cohort_pipeline.pdf`](diagrams/cohort_pipeline.pdf)

Two new columns do all the work: the **cohort** (first month of the customer) and the **age** (months since that first month).
```python
first = log.groupby("customer_id")["month"].min()            # or the signup month
log["cohort"] = log["customer_id"].map(first)
log["age"] = (log["month"] - log["cohort"]).apply(lambda d: d.n)  # Period difference -> integer
counts = log.groupby(["cohort", "age"])["customer_id"].nunique().unstack()
retention = counts.div(counts[0], axis=0)                    # divide each row by its starting size
```
```
2. Cohort retention (% of the signup cohort still active, by months since signup)
age      size   0  1  2  3  4  5  6
cohort
2026-01   102 100 75 73 68 65 59 51
2026-02   103 100 76 73 68 65 61 60
...
2026-06    92 100 82 77 76 73 71 70
2026-07   109 100 91 83 75 73 71  .
2026-08   100 100 89 85 80 70  .  .
...
2026-12   103 100  .  .  .  .  .  .
```
The table is a **triangle**: the December cohort has existed for zero months, so its future is unknown. That is normal, not missing data to fill in.

## 3. Reading a cohort table three ways
Diagrams: [`diagrams/cohort_heatmap.pdf`](diagrams/cohort_heatmap.pdf), [`diagrams/retention_curves.pdf`](diagrams/retention_curves.pdf)

| Direction | Question | Our data |
|---|---|---|
| **Row** | How does one cohort decay over time? | Jan cohort: 75% after 1 month, 51% after 6 |
| **Column** | At the same age, are newer cohorts better? | Month-1 retention: 75% for Jan–Jun, **87% for Jul–Nov** |
| **Diagonal** | What happened in one calendar month (for everybody)? | A drop along a diagonal = an outage, a price change, a holiday |

The column view is the one that judges product changes: a new onboarding flow went live in July, and every cohort from July on loses far fewer customers in its first month. A simple "active customers" chart (102 in Jan → 782 in Dec) would never show this – it only goes up because new signups outnumber churners.

Typical shape: a **big drop in month 1** (people who tried and left), then a slower, flatter decline. A curve that flattens is good news: those customers have found value. A curve that keeps falling to zero means the product does not retain anyone in the long run.

## 4. The censoring trap
Diagram: [`diagrams/kaplan_meier.pdf`](diagrams/kaplan_meier.pdf)
```
4. The naive churn rate is biased
   'share churned' for Oct-Dec signups: 13% (they had only 0-2 months to churn!)
   naive average lifetime of churned customers only: 2.8 months (ignores survivors)
```
A customer who signed up in October and is still active in December is **censored**: we know they stayed *at least* 2 months, but not how long in total. Two classic mistakes:
- **Dividing churners by all customers** mixes old customers (who had 11 months to leave) with new ones (who had 0). Recent signups make churn look low.
- **Averaging the lifetime of churned customers only** throws away everyone who stayed, so the average is far too short (2.8 months here).

## 5. Kaplan-Meier: a survival curve that handles censoring
At each month *t*, only look at customers we could actually observe for *t* months (the **at-risk** group), and multiply the probabilities of surviving each step:

S(t) = S(t−1) × (1 − churned at t / at risk at t)

```python
def kaplan_meier(durations, observed):          # observed: 1 = churned, 0 = still active
    s, curve = 1.0, [(0, 1.0)]
    for t in np.unique(durations[observed == 1]):
        at_risk = (durations >= t).sum()
        churned = ((durations == t) & (observed == 1)).sum()
        s *= 1 - churned / at_risk
        curve.append((t, s))
    return curve
```
```
5. Kaplan-Meier survival (uses censored customers correctly)
 month  survival  at_risk
     0     1.000     1200
     1     0.808     1097
     2     0.757      799
     3     0.710      681
     6     0.601      362
   median lifetime: 10 months
```
- Censored customers count in the "at risk" group for every month they were observed, then quietly leave the calculation. Nobody is thrown away and nobody is assumed to have churned.
- The **median lifetime** is where the curve crosses 50%: 10 months, much longer than the naive 2.8.
- Multiply by monthly revenue and you get a first estimate of **customer lifetime value (LTV)**: area under the survival curve × price per month.

### Comparing segments
Diagram: [`diagrams/survival_by_plan.pdf`](diagrams/survival_by_plan.pdf)
```
6. Survival by plan
   monthly  n= 835   still active after 6 months: 52%
   annual   n= 365   still active after 6 months: 77%
```
Annual customers stay much longer – but be careful: people who choose a yearly plan were probably more committed from the start (selection, not causation – module 08). To know whether *pushing* annual plans reduces churn, run an A/B test (module 12). To test whether two curves differ more than chance, use the **log-rank test** (`lifelines.statistics.logrank_test`); the `lifelines` library also provides `KaplanMeierFitter` with confidence bands.

## 6. Practical checklist
- **Define "active"** before you start: logged in? paid? made a purchase? Different definitions give different retention.
- **Pick the period**: daily cohorts for apps, weekly for e-commerce, monthly or yearly for subscriptions.
- **Show cohort sizes** next to percentages: 80% of 5 customers is noise.
- **Retention vs revenue retention**: also build the table with revenue instead of customer counts (expansions can push revenue retention above 100%).
- In SQL (module 13) the same table is a `GROUP BY cohort_month, age` with `COUNT(DISTINCT user_id)`.

## Git corner: branches are born and die too
Diagram: [`diagrams/git_branch_lifetime.pdf`](diagrams/git_branch_lifetime.pdf)

A feature branch has a "signup" (first commit) and a "churn" (merge or deletion). Long-lived branches drift away from `main` and cause painful conflicts; this course keeps every lesson branch alive for only a few minutes before its pull request is merged.
```bash
git for-each-ref --sort=-committerdate refs/heads --format='%(refname:short) %(committerdate:relative)'
                                          # branches, most recently active first ("last seen")
git branch --merged main                  # branches already merged -> safe to delete
git branch --no-merged main               # work still open ("censored": not finished yet!)
git fetch --prune                         # forget remote branches that were deleted on GitHub
git log --merges --first-parent main --format='%ad %s' --date=short   # one line per merged PR
git log --date=format:'%Y-%m' --format=%ad | sort | uniq -c           # commits per month (activity cohorts)
```
A branch listed by `--no-merged` is like a censored customer: you cannot say it "failed" – it just isn't finished yet. More commands are in the [Git notes](../git-notes/README.md#branch-housekeeping-for-each-ref-merged-and-prune).

## Exercises
1. Build the same cohort table with **revenue** instead of customer counts (monthly plan = 10 €/month, annual = 8 €/month). Is revenue retention higher or lower than customer retention?
2. Compute the cohort table by **quarter** instead of month. What is gained and what is lost?
3. Plot the Kaplan-Meier curve for the Jan–Jun and Jul–Dec signups separately. Does it confirm what the cohort column showed?
4. Estimate the average lifetime as the area under the Kaplan-Meier curve up to month 11 (sum of survival × 1 month). Why is this a *restricted* mean?
5. Run `git for-each-ref` on a repository you work on. How many branches are older than 30 days and not merged?
