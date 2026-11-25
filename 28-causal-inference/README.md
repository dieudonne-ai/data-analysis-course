# Module 28 – Causal Inference Basics (bonus)

"Customers with the loyalty card spend 25 EUR more per month – the card works!" Does it? Most data you get as an analyst is **observational**: nobody decided at random who joined, who got which e-mail or which store changed its opening hours. In that data, a difference between two groups can come from the thing you care about **or** from the way the groups were formed. This module gives you the vocabulary and four tools to tell the two apart:

- **Causal diagrams** (confounder, mediator, collider) – decide *what* to adjust for.
- **Stratification and regression adjustment** – compare like with like.
- **Simpson's paradox and collider bias** – two classic traps.
- **Difference-in-differences** – estimate the effect of a change from before/after data with a control group.

All the data is fictional and simulated, so we know the *true* effects (+4 EUR for the card, +150 EUR/week for the opening hours) and can check which method finds them.

Run it: `python 28-causal-inference/examples/causal_demo.py` (numpy + pandas only; it creates `data/loyalty.csv` and `data/stores_weekly.csv` the first time).
Rebuild the diagrams: `python 28-causal-inference/diagrams/make_diagrams.py`.

## 1. Correlation is not causation: the naive comparison
```python
loyalty = pd.read_csv("data/loyalty.csv")     # customer_id, visits_before, member, spend_after
means = loyalty.groupby("member").spend_after.mean()
naive = means[1] - means[0]
```
```
1. The naive comparison: do loyalty members spend more?
   members 55.20 EUR/month vs non-members 29.86  -> naive 'effect' = +25.34 EUR
   but members visited more BEFORE the card existed: 6.6 vs 3.0 visits/month
   corr(visits_before, member) = 0.54, corr(visits_before, spend) = 0.96  -> a confounder
```
The members were **already** the regular customers before the card existed. Regular customers join more often *and* spend more – with or without a card. That third variable is a **confounder**. The +25 EUR mixes the effect of the card with the effect of "being a regular".

Three questions to ask before believing any group comparison:
1. **Who chose** to be in each group? (self-selection: members, users of a feature, customers who answered a survey)
2. Is there a variable that drives **both** the group and the outcome? (a confounder)
3. Could the outcome have caused the group instead? (**reverse causality**: big spenders are offered the card)

## 2. Draw the diagram first: confounder, mediator, collider
Diagram: [`diagrams/dag_types.pdf`](diagrams/dag_types.pdf)

A **causal diagram** (DAG, *directed acyclic graph*) is boxes and arrows: an arrow means "causes". You draw it from business knowledge, *before* looking at the numbers. Three shapes decide what to do with a third variable Z:

| Shape | Picture | Example | What to do |
|-------|---------|---------|------------|
| **Confounder** | X ← Z → Y | engagement → joins card; engagement → spend | **adjust** for Z (stratify, regression) |
| **Mediator** | X → Z → Y | card → more visits → spend | do **not** adjust if you want the total effect |
| **Collider** | X → Z ← Y | rating → featured ← downloads | **never** adjust for or filter on Z |

"Control for everything" is wrong advice: controlling for a mediator hides part of the real effect, and controlling for a collider *creates* a fake one (section 4).

## 3. Adjusting for a confounder: stratification and regression
Diagram: [`diagrams/confounding.pdf`](diagrams/confounding.pdf)

**Stratification** = compare members and non-members *inside* groups of similar engagement, then average the differences. **Regression adjustment** = put the confounder in the model next to the treatment (module 09); the treatment coefficient is the difference *at equal engagement*.
```python
loyalty["band"] = pd.cut(loyalty.visits_before, [-1, 1, 3, 5, 8, 15])
g = loyalty.groupby(["band", "member"]).spend_after.mean().unstack()
by_band = g[1] - g[0]                                   # difference inside each band

X = np.column_stack([np.ones(len(loyalty)), loyalty.member, loyalty.visits_before])
beta, *_ = np.linalg.lstsq(X, loyalty.spend_after, rcond=None)   # beta[1] = effect of member
```
```
2. Adjusting for the confounder
   member - non-member difference INSIDE each engagement band:
   0-1: +5.42  2-3: +5.19  4-5: +4.12  6-8: +5.64  9+: +9.14
   stratified estimate (weighted by band size) = +5.56 EUR
   regression  spend_after ~ member + visits_before:
                   coef    se  ci_low  ci_high
   const          11.93  0.23   11.49    12.38
   member          3.81  0.32    3.18     4.43
   visits_before   6.01  0.05    5.91     6.10
   naive +25.34  |  stratified +5.56  |  regression +3.81  |  truth +4.00 (known only because the data is simulated)
```
- The naive +25 EUR shrinks to about **+4 EUR** once we compare like with like. The card helps – but six times less than the first slide said.
- Stratification is easy to explain but bands are coarse: inside "9+" there are still differences in engagement, so a bit of confounding is left (+5.56). Finer bands or regression get closer.
- Adjustment only removes confounders **you measured**. If something unmeasured (income, distance from the shop) drives both joining and spending, the estimate is still biased. Say so in the report.
- Other methods built on the same idea: **matching** (pair each member with a similar non-member) and **propensity scores** (model the probability of joining, then compare people with the same probability).

## 4. Two classic traps
### Simpson's paradox
Diagram: [`diagrams/simpsons_paradox.pdf`](diagrams/simpsons_paradox.pdf)
```
3. Simpson's paradox: which e-mail converts better?
   email          A      B
   segment                
   new        10.0%   8.0%
   returning  30.0%  28.0%
   overall: A 14.0%  vs  B 24.0%
   A wins in BOTH segments but loses overall: A was mostly sent to new customers, who rarely buy.
```
E-mail A is better for new customers **and** for returning customers, yet worse overall – because 400 of its 500 sends went to new customers, who rarely buy. The segment is a confounder: it affects both "which e-mail" and "buys". Here the within-segment comparison is the right one. (It is not always: if the third variable is a *mediator*, the overall number is the right one. The diagram decides, not the data.)

### Collider (selection) bias
Diagram: [`diagrams/collider_bias.pdf`](diagrams/collider_bias.pdf)
```python
rating, downloads = rng.normal(0, 1, 5_000), rng.normal(0, 1, 5_000)   # independent
featured = (rating + downloads) > 1.5                                   # good OR popular
```
```
4. Collider bias: 'featured' apps look like a trade-off that does not exist
   corr(rating, downloads), all apps      = -0.03
   corr(rating, downloads), featured only = -0.70
```
An app is featured if it is good **or** popular. Among featured apps, the less popular ones *must* be well rated (otherwise they would not be there), so a strong negative correlation appears from nothing. The same trap hides in "among customers who complained...", "among hired candidates...", "among loans that were approved...": **filtering on an outcome of the variables you study** distorts their relationship.

## 5. Difference-in-differences (DiD)
Diagram: [`diagrams/difference_in_differences.pdf`](diagrams/difference_in_differences.pdf)

From week 14, 8 of the 20 stores open two hours later in the evening. Did it raise sales? The 8 stores were chosen by management (the bigger ones), not at random, and all stores follow a common seasonal trend. Two simple comparisons are both wrong:

- **after only, treated vs control** – includes the fact that treated stores were bigger anyway;
- **before vs after, treated only** – includes the trend that every store had.

DiD subtracts both: **(treated after − treated before) − (control after − control before)**. The control group's change is the estimate of what *would* have happened to the treated stores without the change.
```python
t = stores.groupby(["treated", "post"]).sales.mean().unstack()   # the 2 x 2 table
did = (t.loc[1, 1] - t.loc[1, 0]) - (t.loc[0, 1] - t.loc[0, 0])

# same thing as a regression: the interaction coefficient is the DiD
X = np.column_stack([np.ones(n), stores.treated, stores.post, stores.treated * stores.post])
```
```
5. Difference-in-differences: did the later opening hours raise sales?
            before   after  change
   control  4519.7  4610.1    90.4
   treated  5525.3  5762.2   236.9
   after-only comparison (treated - control) = +1152.1  <- includes 'bigger stores' bias
   before/after in treated stores only     = +236.9  <- includes the common trend
   difference-in-differences               = +146.5  (truth +150)
   regression sales ~ treated + post + treated:post -> effect +146.5, 95% CI [44.2, 248.8]
   + store and week fixed effects (two-way FE)       -> effect +146.5, 95% CI [114.4, 178.5]
```
- The regression form gives the same number **plus a confidence interval**, and lets you add controls.
- Adding a dummy for every store and every week (**two-way fixed effects**) removes the store-size differences and the weekly ups and downs from the noise: same estimate, much narrower interval.
- (Real projects: rows of the same store are not independent, so use *clustered* standard errors by store – e.g. `statsmodels` with `cov_type="cluster"`.)

## 6. Check the key assumption: parallel trends
DiD only works if, **without** the change, both groups would have moved in parallel. You cannot test the "without" directly, but you can check the period before:
```
6. Checking the parallel-trends assumption
   pre-period gap treated - control: week 1 1072, week 13 959, slope -1.5 EUR/week (close to 0 = parallel)
   placebo test (fake start at week 7, pre-period only): effect +4.4, 95% CI [-135.8, 144.7]
   The placebo CI includes 0: no 'effect' before the real change -> the design is credible.
```
- **Plot both groups over time** (the diagram). Before week 14 the lines should be parallel – a gap is fine, a growing or shrinking gap is not.
- **Placebo test**: pretend the change happened earlier, using only the before-period. A real "effect" there means the groups were already drifting apart.
- Watch out for other events at the same time (a competitor closing near the treated stores) and for **spillovers** (control customers moving to the late-opening stores).

## 7. The ladder of evidence
From strongest to weakest:
1. **Randomised experiment** (A/B test, module 12) – randomisation balances *all* confounders, measured or not. Use it whenever you can.
2. **Natural experiments**: DiD, before/after with a control group, regression discontinuity (a rule like "free shipping above 50 EUR" creates comparable groups just below/above 50).
3. **Adjusted observational comparisons**: regression, stratification, matching – only as good as the list of confounders you measured.
4. **Raw comparisons and correlations** – describe, do not conclude.

How to write it up: say which rung you are on, name the assumption ("we assume treated and control stores would have followed the same trend"), show the check (the pre-period plot), and use careful words: "is associated with" for rung 4, "caused / increased" only when the design supports it.

## Git corner: merge conflicts
Diagram: [`diagrams/git_merge_conflict.pdf`](diagrams/git_merge_conflict.pdf)

Two branches are like two groups that changed after a common starting point (the *merge-base*). Git combines them line by line; when both sides changed the **same lines**, it cannot decide – that is a conflict, and you are the analyst who looks at both versions:
```bash
git config --global merge.conflictStyle diff3   # also show the merge-base version between ||||||| and =======
git merge my-branch                             # CONFLICT (content): Merge conflict in config.py
git status                                      # "both modified: config.py"
git diff                                        # see the conflicting hunks
git checkout --ours   config.py                 # keep main's version of the whole file...
git checkout --theirs config.py                 # ...or the branch's version
git merge -X ours my-branch                     # auto-resolve every conflicting hunk in favour of ours
git mergetool                                   # open a 3-way merge tool, if configured
git add config.py && git commit                 # mark as resolved and finish the merge
git merge --abort                               # or give up and go back to before the merge
git log --merge --oneline                       # during a conflict: the commits that touched the conflicting files
```
- With `diff3`, you see three versions: **ours** (HEAD), the **merge-base**, and **theirs**. Comparing each side with the base tells you *who changed what* – exactly the before/after logic of DiD.
- Never commit the `<<<<<<<`, `=======`, `>>>>>>>` markers. `git diff --check` warns about leftover markers.
- After resolving, **re-run the analysis**: a merge without text conflicts can still break the logic.
- Data files (CSV) conflict easily. Keep them generated by scripts (like `make_loyalty()` here) and regenerate them instead of merging them by hand.

More commands are in the [Git notes](../git-notes/README.md#merge-conflicts-diff3---ours--theirs-and-abort).

## Exercises
1. In `make_loyalty`, add an unmeasured confounder (`income`) that raises both `p_join` and `spend`, but do not include it in the regression. How far is the estimate from +4?
2. Add `visits_after` as a mediator (`card → visits_after → spend`) and put it in the regression. What happens to the member coefficient, and why?
3. Change `make_stores` so treated stores grow 15 EUR/week faster even before week 14. What do the DiD estimate and the placebo test show now?
4. Simpson's paradox: change the campaign table so both e-mails are sent 250/250 in each segment. Does the paradox survive?
5. On a test branch, change the same line of `causal_demo.py` as on `main`, merge, and resolve the conflict with `diff3` turned on.
