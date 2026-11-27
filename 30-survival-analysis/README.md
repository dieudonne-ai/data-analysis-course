# Module 30 – Survival Analysis: Time-to-Event Data (bonus)

"How long do customers stay?" sounds like a simple average. It is not: on the day you run the analysis, many customers have **not left yet**, so you do not know their real tenure. Survival analysis is the toolbox for this kind of *time-to-event* data – churn, time to first purchase, time to machine failure, time to hire. In this module you will:

- understand **censoring** and why simple averages are biased;
- compute the **Kaplan-Meier** survival curve by hand, with a confidence band;
- compare two groups with the **log-rank test**;
- read the **hazard** – *when* do customers leave?
- summarise a curve with the **restricted mean survival time (RMST)** and turn it into revenue.

The data is a fictional meal-kit company: 1,500 subscribers who signed up during 2025, on a **weekly** plan (a box every week) or a **flex** plan (skip weeks freely). The analysis date is 2026-01-01. The data is simulated, so we know the true medians and can check the method.

Run it: `python 30-survival-analysis/examples/survival_demo.py` (numpy, pandas, scipy; it creates `data/survival.csv` the first time).
Rebuild the diagrams: `python 30-survival-analysis/diagrams/make_diagrams.py`.

## 1. Censoring: the heart of the problem
Diagram: [`diagrams/censoring_timeline.pdf`](diagrams/censoring_timeline.pdf)

Each customer gives you one row with two columns:

| column | meaning |
|--------|---------|
| `days` | days from signup until they left **or until today** |
| `churned` | 1 = we saw them leave (the *event*), 0 = still active (**censored**) |

A censored customer with `days = 300` tells us "this person stayed **at least** 300 days". Look at what the usual shortcuts do:
```
1. Censoring: why the simple average is wrong
   1500 subscribers, 763 churned, 737 still active on 2026-01-01 (censored)
   mean tenure of churned customers only :     77 days  (ignores everyone who stayed)
   mean of all observed days             :    108 days  (treats 'still active' as 'left today')
   share churned                         :  50.9%      (depends on WHEN you look)
   All three are biased DOWN: the longest customers are exactly the ones we have not seen leave yet.
```
- **Dropping censored rows** keeps only customers who left – the short ones by definition.
- **Treating them as churned today** cuts every loyal customer's story short.
- The **churn rate** mixes customers watched for 10 days with customers watched for a year.

Censoring is also everywhere outside marketing: patients still alive at the end of a study, machines still running, job offers still open.

## 2. The Kaplan-Meier estimator
Diagram: [`diagrams/kaplan_meier.pdf`](diagrams/kaplan_meier.pdf)

Idea: staying 3 days = staying day 1, **and** day 2 given day 1, **and** day 3 given day 2. At each day *t* where someone leaves:

  **S(t) = S(previous) × (1 − d / n)**   with d = customers who left at t, n = customers **at risk** just before t.

A censored customer counts in *n* until their last observed day, then quietly leaves the risk set – never as a churn.
```python
def kaplan_meier(days, event):
    d = pd.DataFrame({"t": days, "e": event})
    g = d.groupby("t").agg(d=("e", "sum"), c=("e", lambda x: (x == 0).sum())).reset_index()
    g["n"] = len(d) - g["d"].shift(fill_value=0).cumsum() - g["c"].shift(fill_value=0).cumsum()
    g = g[g.d > 0].copy()
    g["surv"] = (1 - g.d / g.n).cumprod()
    ...  # + Greenwood variance for the 95% band
```
```
2. Kaplan-Meier: S(t) = product of (1 - churned / at risk) at each event time
    t    n  d  1 - d/n   surv
    1 1500 19   0.9873 0.9873
    2 1480 22   0.9851 0.9727
    3 1456 13   0.9911 0.9640
    4 1440 12   0.9917 0.9559
   S( 30) = 81.8%  95% CI [79.7%, 83.7%]
   S( 90) = 62.3%  95% CI [59.6%, 64.9%]
   S(180) = 44.1%  95% CI [41.1%, 47.0%]
   S(365) = 26.8%  95% CI [23.1%, 30.7%]
   median survival = 146 days (half the customers have left by then)
```
- Read *n* in the table: on day 2 there are 1,480 at risk = 1,500 − 19 churned − 1 censored on day 1.
- **Median survival** = first day where S(t) ≤ 50 %. Prefer it to a mean: the mean needs to know the very long tenures, which censoring hides.
- **Greenwood's formula** gives the confidence band. It gets wider at the right because few customers have been observed that long. Do not over-read the tail of a KM curve.
- In practice you can use the `lifelines` library (`KaplanMeierFitter`), which does the same thing in two lines. Writing it once by hand shows you what it really computes.

## 3. Comparing groups: the log-rank test
Diagram: [`diagrams/plans_rmst.pdf`](diagrams/plans_rmst.pdf)
```
3. Compare plans: Kaplan-Meier per group + log-rank test
   weekly: n= 885  S(90)=53.8%  S(365)=14.1%  median=100 days
   flex  : n= 615  S(90)=74.7%  S(365)=45.0%  median=256 days
   log-rank: weekly churned 535 vs 404.1 expected if the plans were equal; chi2 = 91.7, p = 9.9e-22
   The plans differ. Careful: customers CHOSE their plan, so this is not (yet) a causal effect (module 28).
```
The **log-rank test** walks through every churn day and asks: given how many weekly and flex customers were at risk on that day, how many weekly churns would we expect if both plans had the same survival? It adds up *observed − expected* over the whole curve and gives a chi² statistic with 1 degree of freedom (module 08).

- It compares **whole curves**, not one point. Comparing only "S(90)" throws information away and invites cherry-picking the day.
- It is most powerful when one group is at higher risk all the time (curves that do not cross). When curves cross, compare RMST (section 5) or S(t) at a horizon chosen **before** looking.
- Groups that choose themselves are a comparison, not an experiment: flex customers may simply be less busy or less price-sensitive. To know what *moving* customers to flex would do, run an A/B test (module 12).

## 4. The hazard: when do customers leave?
Diagram: [`diagrams/hazard_life_table.pdf`](diagrams/hazard_life_table.pdf)

The **hazard** h(t) is the risk of leaving at time *t* **for those still here**. A life table estimates it month by month:
```
4. The hazard: WHEN do customers leave?
    from  to  at_risk  churned hazard
       0  30     1500      264  18.3%
      30  60     1118      147  13.8%
      60  90      868       97  11.6%
      90 120      703       76  11.5%
     120 150      547       53  10.4%
     150 180      423       42  10.6%
   month 1 hazard 18.3% vs month 9 hazard 8.3% (191 at risk): the risk FALLS with tenure -> invest in onboarding (the first 30 days).
   Few customers are followed for a full year, so late windows are noisy: always show 'at risk'.
```
The shape of the hazard is the business story:

| hazard shape | meaning | typical action |
|--------------|---------|----------------|
| **falling** | most people leave early, survivors are loyal | better onboarding, first-box experience |
| **flat** | constant risk, "random" churn | general product and price work |
| **rising** | wear-out, contracts ending, product fatigue | renewal offers, novelty, maintenance |

Note the **actuarial correction** in the code: customers censored during a month count as half a month at risk.

## 5. RMST: a mean you can trust, and money
```
5. Restricted mean survival time (RMST) and first-year revenue
   weekly: RMST(365) =   145 days =  4.8 months  x 60 EUR =   286 EUR first-year revenue per signup
   flex  : RMST(365) =   228 days =  7.5 months  x 45 EUR =   337 EUR first-year revenue per signup
   RMST = area under the KM curve up to a horizon: a mean that is valid with censoring.
```
The **restricted mean survival time** RMST(T) is the area under S(t) between 0 and T: "on average, how many of the first T days does a customer stay?" Unlike a raw mean it handles censoring, and unlike the median it uses the whole curve.

Multiplying by the monthly price gives **first-year revenue per signup** – the cheaper flex plan earns *more* per signup because customers stay longer. This is the bridge to customer lifetime value (CLV); add margin and acquisition cost for a full CLV.

```
6. Sanity check against the truth (we simulated the data)
   weekly: true median  101 days, KM median  100 days
   flex  : true median  266 days, KM median  256 days
```

## Summary and pitfalls
Diagram: [`diagrams/survival_cheatsheet.pdf`](diagrams/survival_cheatsheet.pdf)

- **Define start and event precisely.** "Churn" = cancellation date? last paid box? 60 days without an order? Write it down; different definitions give different curves.
- **Informative censoring** breaks KM: censoring must be unrelated to the risk of leaving. If customers whose card expired are removed from the data, they were probably about to churn – that biases S(t) up.
- **Immortal time bias**: "customers who used the app ≥ 5 times survive longer" – of course, they had to survive long enough to use it 5 times. Measure the feature in a fixed early window (e.g. first 14 days) and start the clock after it.
- **Tail**: do not report S(t) where fewer than ~50 customers are still at risk.
- Next steps: **Cox regression** (effect of several variables on the hazard at once), **parametric models** (Weibull) to extrapolate beyond the data, **competing risks** (cancel vs pause vs payment failure).

## Git corner: time in git
Diagram: [`diagrams/git_dates.pdf`](diagrams/git_dates.pdf)

Survival analysis is about time; git stores two dates for every commit and lets you filter and format them.
```bash
git log --since="2026-11-22" --until="2026-11-25" --oneline   # commits in a date window
git log --since="2 weeks ago" --author="Ada" --oneline         # relative dates work too
git log --date=short --format='%ad %h %s' -5                   # 2026-11-26 e0cd947 Add module 29 ...
git log --date=relative -3                                     # "2 days ago"
git rev-list --count --since="1 month ago" HEAD                # how many commits this month?
git show main@{yesterday} --stat                               # where YOUR main pointed yesterday (reflog)
git blame --date=short README.md                               # "birth date" of every line
git blame --line-porcelain README.md | grep '^author-time' | wc -l   # one timestamp per line, ready for analysis
```
- **Author date (`%ad`) vs committer date (`%cd`)**: the author date is when the change was written; the committer date changes when a commit is rebased, cherry-picked or amended. `--since` filters on the committer date.
- `main@{yesterday}` uses your **local reflog**, so it shows where *your* copy of `main` was, not what was on GitHub.
- Code-line ages from `git blame` are survival data too: a line is "born" in one commit and "dies" when it is changed or deleted. Lines that still exist today are censored!

More commands are in the [Git notes](../git-notes/README.md#time-in-git-since-date-formats-and-reflog-dates).

## Exercises
1. Change the analysis date (`CUTOFF`) to 2025-07-01, regenerate the data and compare the naive averages and the KM median. Which methods change the most?
2. Compute S(t) with the "drop the censored rows" approach and plot it next to the KM curve. How far apart are they at 180 days?
3. Add a third plan with a **rising** hazard (`SHAPE = 1.5` for that plan only). What does its life table look like?
4. Write a function that returns the KM median **and** a bootstrap 95 % interval for it (module 27).
5. Compute RMST(180) for both plans and the difference with a bootstrap interval. Is the difference significant?
6. In this repository, run `git blame --line-porcelain` on the main `README.md` and build a small table of line "birth dates". How many lines were written each day?
