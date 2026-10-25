# Module 08 - Hypothesis Testing

Is a difference real, or just random noise? Hypothesis tests answer this.
Scenario: customers were randomly split into group A (old page) and group B (new page). Does B spend more?

Diagrams: [5 steps](diagrams/test_steps.pdf) - [p-value](diagrams/p_value.pdf) - [error types](diagrams/errors_table.pdf)

## The logic
1. **H0 (null)**: no difference. **H1**: there is a difference.
2. Choose a significance level `alpha` (usually 0.05).
3. Pick the test that fits the data (table below).
4. Compute the **p-value**: the probability of a result at least this extreme *if H0 were true*.
5. If `p < alpha`, reject H0. Otherwise, you *cannot reject* it (that is not proof that H0 is true).

## Which test?
| Question | Test | scipy |
|----------|------|-------|
| Compare 2 group means | Welch t-test | `stats.ttest_ind(b, a, equal_var=False)` |
| Same subjects before/after | Paired t-test | `stats.ttest_rel` |
| Compare 3+ group means | ANOVA | `stats.f_oneway` |
| Two categorical variables | Chi-square | `stats.chi2_contingency` |
| Not normal, small sample | Mann-Whitney U | `stats.mannwhitneyu` |

## Worked example (A/B test)
```python
a = df.loc[df["group"] == "A", "spend"]
b = df.loc[df["group"] == "B", "spend"]
t, p = stats.ttest_ind(b, a, equal_var=False)
```
Result: A mean 113.6, B mean 125.5, `t = 2.95`, `p = 0.0036` -> reject H0: B spends significantly more.

**Significant is not the same as important.** Report the effect size too: Cohen's d = 0.42 (a small-to-medium effect), and the difference itself (about 12 per customer).

Chi-square test of city vs group: `p = 0.368` -> no evidence that the random split was unbalanced across cities (good sign for the experiment).

## Pitfalls
- **p-hacking**: running many tests until one is significant. With 20 tests at alpha 0.05, one is expected to be a false alarm.
- Small samples have low *power* (risk of Type II errors).
- p-value is **not** the probability that H0 is true.

## Exercises
1. Test whether `visits` differs between groups A and B.
2. Use ANOVA to compare `spend` across the four cities.
3. Run `mannwhitneyu` on spend instead of the t-test. Do conclusions agree?
4. Explain in plain words what `p = 0.0036` means.

Run the worked example: `python 08-hypothesis-testing/examples/ab_test.py`
