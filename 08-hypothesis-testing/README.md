# Module 08 — Hypothesis Testing

A hypothesis test asks: *could the pattern I see in my sample be just random noise?*
Dataset: [`data/students.csv`](../data/students.csv).

Diagrams: [`diagrams/hypothesis_flow.pdf`](diagrams/hypothesis_flow.pdf),
[`diagrams/choose_test.pdf`](diagrams/choose_test.pdf)

## The logic
1. **H0 (null hypothesis)**: nothing is going on (e.g. girls and boys have the same mean score).
2. **H1 (alternative)**: there is a difference.
3. Pick a significance level, usually **α = 0.05**.
4. Compute a test statistic and its **p-value** = probability of seeing data at least this extreme *if H0 were true*.
5. If `p < α` reject H0; otherwise **fail to reject** H0 (this is not proof that H0 is true).

> A p-value is **not** the probability that H0 is true, and "significant" does not mean "important".
> Always report the effect size (the actual difference) too.

## Choosing a test
| Question | Test | scipy |
|----------|------|-------|
| 2 group means | t-test | `stats.ttest_ind(a, b, equal_var=False)` |
| 3+ group means | ANOVA | `stats.f_oneway(a, b, c)` |
| 2 categorical variables | Chi-square | `stats.chi2_contingency(table)` |
| 2 numeric variables | Pearson correlation | `stats.pearsonr(x, y)` |

## Results on our data
| Test | Result | Conclusion |
|------|--------|------------|
| F vs M scores | p = 0.58 | no evidence of a difference |
| Score by track (ANOVA) | p = 0.82 | no evidence of a difference |
| Track vs gender (chi²) | p = 0.27 | no evidence of association |
| Study hours vs score | r = 0.70, p ≈ 1e-30 | strong, significant relationship |

## Errors
- **Type I** (false positive): rejecting a true H0. Probability = α.
- **Type II** (false negative): missing a real effect. Larger samples reduce it.
- Running many tests inflates false positives (multiple comparisons) — be careful.

Script: [`examples/tests_demo.py`](examples/tests_demo.py)
