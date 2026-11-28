# Module 30 – Survival Analysis: Time Until Churn (bonus)

"How long does a customer stay?" sounds like a simple average. It is not: on the day you pull the data, many customers are **still active**, so you do not know how long they will stay – only that it is *at least* as long as you have watched them. Survival analysis is the toolkit built for exactly this. In this module you will:

- understand **censoring** and why the usual averages are wrong;
- compute a **Kaplan-Meier** survival curve by hand, with a confidence band;
- read a median lifetime and "share still here after 12 months";
- compare two groups with the **log-rank test**;
- look at the **hazard** – *when* people leave – to time retention actions;
- turn the curve into an **expected lifetime** and a revenue per customer.

The data is a fictional gym with 2,000 members on two plans: **monthly** (39 EUR/month, can cancel any month) and **annual** (29 EUR/month, can only leave at the yearly renewal). Members joined at different times over 36 months. It is simulated, so we know the truth (monthly members leave with a 7.5 % chance each month; 35 % of annual members do not renew each year).

Run it: `python 30-survival-analysis/examples/survival_demo.py` (numpy, pandas, scipy; it creates `data/gym_members.csv` the first time).
Rebuild the diagrams: `python 30-survival-analysis/diagrams/make_diagrams.py`.

Same idea, other words: *time-to-event*, *duration*, *reliability* (engineering), *life tables* (insurance). The event can be anything: churn, first purchase, loan default, machine failure, a job offer accepted, a pull request merged.

## 1. Censoring: the data you do not have yet
Diagram: [`diagrams/censoring_timeline.pdf`](diagrams/censoring_timeline.pdf)

Each member is one row with two numbers:
- `duration` – how many months we watched them (until they left, or until today);
- `churned` – **1** if we saw them leave, **0** if they are still active (**censored**).

```
 member_id    plan  join_month  duration  churned
         1 monthly          32         4        0     <- joined 4 months ago, still here
         2 monthly          27         1        1     <- left after 1 month
```
Member 1 will stay 11 months in total (we know because we simulated it), but in real life we only know "≥ 4". The two shortcuts people take are both wrong:
```
1. Censoring: many members have NOT churned yet - we only know they lasted 'at least' duration
   censored (still active): 46% of members
   monthly plan, true mean lifetime          = 13.3 months
   mean over churned members only           = 8.1  (too short: long-lived members are dropped)
   mean over everyone, active counted as end = 9.2  (too short: active members are cut off)
```
- **Dropping active customers** keeps only the ones who left – by definition the shorter lifetimes.
- **Treating "today" as their end** pretends loyal customers churned today.
- Recent sign-ups make it worse: they are almost all censored. A growing business always looks like it has "short" lifetimes with these shortcuts.

Survival methods use censored rows correctly: a member censored at month 4 *does* tell us "survived months 1-4", and nothing after.

## 2. Kaplan-Meier: the survival curve by hand
Diagram: [`diagrams/km_by_hand.pdf`](diagrams/km_by_hand.pdf)

**S(t)** = probability of still being a member after t months. Kaplan-Meier builds it month by month: to survive to month 3, you must survive month 1, *then* month 2, *then* month 3. Each step uses only the people **at risk** (still a member at the start of that month):

  S(t) = Π over months ≤ t of (1 − churned / at risk)

```python
def kaplan_meier(duration, event):
    d = pd.DataFrame({"t": duration, "e": event})
    rows, s = [], 1.0
    for t in np.sort(d.loc[d.e == 1, "t"].unique()):         # every month with a churn
        n_risk = int((d.t >= t).sum())                         # still here at the start of month t
        n_event = int(((d.t == t) & (d.e == 1)).sum())         # left in month t
        s *= 1 - n_event / n_risk
        rows.append((t, n_risk, n_event, s))
    ...                                                        # + Greenwood's formula for a 95% band
```
```
2. Kaplan-Meier: S(t) = product over months of (1 - churned / at risk)
 month  at_risk  churned  survival  ci_low  ci_high
     1     1189       77     0.935   0.921    0.949
     2     1088       83     0.864   0.844    0.884
     3      980       74     0.799   0.776    0.822
   ...
   S(12) = 0.389  (truth 0.392)  -> chance a monthly member is still here after 1 year
```
- The curve **only drops at churns**. A censored member never causes a drop; they just leave the "at risk" count afterwards.
- The confidence band (Greenwood's formula) gets **wider to the right**: fewer and fewer members are still being watched.
- In practice, the `lifelines` package does this in two lines: `KaplanMeierFitter().fit(df.duration, df.churned).plot()`. Writing it once by hand is the best way to trust it.

## 3. Reading the curves
Diagram: [`diagrams/km_curves.pdf`](diagrams/km_curves.pdf)
```
3. Reading the curves: median lifetime and survival at fixed dates
   monthly  median =    9 months | S(6) = 0.64 | S(13) = 0.36 | S(24) = 0.17 [0.14, 0.20]
   annual   median =   24 months | S(6) = 1.00 | S(13) = 0.65 | S(24) = 0.42 [0.37, 0.47]
```
- **Median lifetime** = first month where S(t) ≤ 0.5. Prefer it to the mean: the mean needs the whole tail, which you have not observed yet. If the curve never falls below 0.5, the median is simply "more than X months" – say so.
- **S at fixed dates** ("64 % are still here after 6 months") is the easiest number for a business audience, and it is what a retention chart (module 25) shows – but corrected for censoring.
- The shape tells a story: the monthly curve falls smoothly; the annual curve is flat, then drops in **cliffs** at months 12 and 24.

## 4. Comparing groups: the log-rank test
```python
for t in event_months:
    at_risk = d[d.t >= t]
    expected_in_group1 += churns_at_t * share_of_group1_at_risk    # if both curves were the same
chi2 = (observed - expected) ** 2 / variance                        # compare with chi2(1)
```
```
4. Log-rank test: are the two curves different?
   monthly: observed churns 807, expected if curves were equal 490.4
   chi2 = 428.2, p = 4e-95  -> the plans really differ
```
- The idea is the same as the chi-square test of module 08: at each churn month, split the churns between the groups in proportion to how many of each are at risk, and add up "observed − expected".
- With k groups the statistic has k − 1 degrees of freedom.
- The test answers *whether* the curves differ, not *how*. Curves that cross (one group leaves early, the other late) can give a weak log-rank result although they are very different. Always plot.
- **Careful with causality** (module 28): annual members may simply be more motivated people. The plan is not proven to *cause* the longer lifetime; a randomised offer (module 12) would be needed.

## 5. The hazard: when do people leave?
Diagram: [`diagrams/hazard.pdf`](diagrams/hazard.pdf)

The **hazard** h(t) is the risk of leaving in month t *given you were still a member at its start* = churned / at risk. The survival curve shows *how many are left*; the hazard shows *when the danger is*.
```
5. Hazard = churned / at risk in each month (risk of leaving NOW, given you are still here)
   monthly: months 1-21 (>= 100 at risk): hazard between 5.5% and 9.1%, mean 7.3% (truth 7.5% every month)
   constant-hazard shortcut: churns / member-months = 807 / 10,953 = 0.074 -> mean lifetime 1 / h = 13.6 months (truth 13.3)
   annual: hazard 0 in every month except renewals -> month 12: 35%, month 24: 35%
   -> plan retention campaigns for annual members in month 11, for monthly members from day 1
```
- **Flat hazard** = "memoryless": the risk is the same in month 2 and month 20. Then a quick estimate works: hazard = churns / total months watched, and mean lifetime = 1 / hazard (an exponential model).
- Other typical shapes: **falling** hazard (risky first weeks, then loyal – onboarding matters), **rising** hazard (wear-out, contracts ending), **spikes** (renewals, price increases, end of a free trial).
- The tail is noisy: with few members at risk, one churn moves the hazard a lot. Ignore months with a small risk set (grey bars in the diagram).

## 6. From survival to value
Diagram: [`diagrams/survival_cheatsheet.pdf`](diagrams/survival_cheatsheet.pdf)

The area under S(t) is the expected number of months a member stays. Because the tail is unknown, we stop at a horizon (here 36 months): the **restricted mean survival time (RMST)**.
```python
def rmst(km, horizon):
    return sum(survival_at(km, m) for m in range(horizon))     # one term per month
```
```
6. From survival to value: restricted mean lifetime (area under S up to 36 months)
   monthly  expected months in first 3 years =  12.8  x 39 EUR =    498 EUR per member
   annual   expected months in first 3 years =  24.8  x 29 EUR =    718 EUR per member
   annual members pay less per month but stay much longer -> more revenue per member
```
(Truth: 12.5 and 24.9 months.) Multiply by monthly margin instead of price for a **customer lifetime value**, and compare it with what it costs to acquire a member. Put a bootstrap interval around it (module 27) before you present it.

## 7. Checklist for a survival analysis
1. Define the **start** (sign-up, first purchase), the **event** (cancellation, 60 days inactive...) and the **end of observation** clearly – write them down.
2. Build one row per subject: `duration`, `event` (1/0), plus the groups or drivers you care about.
3. Never drop censored rows, never treat them as events.
4. Plot Kaplan-Meier curves with bands; report the median and S at business dates (30 days, 1 year).
5. Compare groups with the log-rank test – and look at the plot for crossing curves.
6. Look at the hazard to decide *when* to act.
7. Check that censoring is "uninformative": if people disappear from the data *because* they are about to churn (e.g. they stop logging in), the curve will be too optimistic.
8. Next step: **Cox regression** (`lifelines.CoxPHFitter`) models the hazard with several drivers at once – age, plan, channel – like a regression for survival data.

## Git corner: asking git "when?"
Diagram: [`diagrams/git_time_travel.pdf`](diagrams/git_time_travel.pdf)

Every commit stores **two** timestamps: the **author date** (when the change was first written) and the **committer date** (when it was last applied – a rebase, cherry-pick or amend updates it). Git can filter, count and travel by date:
```bash
git log --format='%h %ad %cd %s' --date=short     # author date and committer date side by side
git log --since='2 weeks ago' --until=yesterday   # commits in a date window (--after/--before are aliases)
git rev-list --count --since=2026-11-01 main      # how many commits since 1 November
git log -1 --format=%cr main                      # last commit on main, relative: "3 hours ago"
git show main@{yesterday}:README.md               # the file as YOUR main pointed to yesterday
git diff main@{1.week.ago} main --stat            # what changed on your main in a week
git log --merges --first-parent main --format='%ct %s'   # merge times (Unix seconds) - one per pull request
GIT_AUTHOR_DATE='2026-11-27T18:00' git commit -m "..."   # set the author date (or git commit --date=...)
```
- `main@{yesterday}` uses your local **reflog** (see "Recovering lost work" in the git notes): it means "where *my* main pointed yesterday", not "the shared history as of yesterday", and it only goes back ~90 days. For the shared history use `git rev-list -1 --before=2026-11-27 main`.
- Dates in commits are written by the committer's machine – they can be wrong or set by hand. Use them for analysis, not as proof.
- Survival thinking applies to your repository too: "time from first commit to merge" is a duration, and **branches still open are censored** – not "never merged". A Kaplan-Meier curve of time-to-merge is a fair way to see whether reviews are getting slower.

More commands are in the [Git notes](../git-notes/README.md#time-in-git-author-vs-committer-date---since-and-refdate).

## Exercises
1. Remove the censored rows and fit a Kaplan-Meier curve anyway. How much too pessimistic is S(12) for monthly members?
2. Change the study end from 36 to 18 months in `survival_demo.py` (delete `data/gym_members.csv` first). Can you still estimate the median for annual members? What does the code return, and how would you report it?
3. Simulate a **falling** hazard for monthly members (e.g. 15 % in months 1-3, then 5 %). Draw the hazard plot. Is the constant-hazard shortcut still close to the truth?
4. Split monthly members into two random halves and run the log-rank test 200 times. In what share of runs is p < 0.05? (Answer you should expect: about 5 %.)
5. Compute a bootstrap 95 % interval (module 27) for the RMST of each plan.
6. In this repository, list the merge commit times of the last pull requests with `git log --merges --first-parent main --format='%ct %s'` and the time of the first commit of each branch. Build `duration` and `event` columns and plot a Kaplan-Meier curve of "hours until merged".
