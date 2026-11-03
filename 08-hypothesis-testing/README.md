# Module 08 — Hypothesis Testing

Hypothesis testing answers: *"Is the difference I see real, or just random noise?"*
We use `data/sales_eda.csv` (200 orders, 4 products, 6 months) with pandas and scipy.

## 1. The workflow

Diagram: [`diagrams/workflow.pdf`](diagrams/workflow.pdf)

1. **State hypotheses.** H0 (null) = "no effect / no difference". H1 = "there is one".
2. **Choose alpha**, the false-alarm rate you accept (usually 0.05).
3. **Pick a test** and check its assumptions.
4. **Compute** the test statistic and the **p-value**.
5. **Decide**: if `p < alpha`, reject H0. Always report an **effect size** too.

Example: *H0: Notebook and Bag orders have the same mean revenue.*

## 2. What a p-value is (and is not)

The p-value is the probability of seeing a result **at least this extreme if H0 were true**.
It is **not** the probability that H0 is true, and a small p does not mean a big effect.
Diagram: [`diagrams/p_value.pdf`](diagrams/p_value.pdf)

## 3. Two kinds of error

| | H0 true | H0 false |
|---|---|---|
| Reject H0 | **Type I** error (false alarm, prob = alpha) | correct (power = 1 - beta) |
| Keep H0 | correct | **Type II** error (miss, prob = beta) |

Larger samples increase power. Diagram: [`diagrams/errors.pdf`](diagrams/errors.pdf)

## 4. Which test?

Diagram: [`diagrams/which_test.pdf`](diagrams/which_test.pdf)

```python
from scipy import stats

stats.ttest_1samp(df["revenue"], 40)                 # one group vs a known value
stats.ttest_ind(a, b, equal_var=False)               # two groups (Welch t-test)
stats.mannwhitneyu(a, b)                             # two groups, skewed data
stats.f_oneway(*groups)                              # 3+ groups (ANOVA)
stats.chi2_contingency(pd.crosstab(df["product"], df["month"]))   # two categorical variables
```

Revenue is right-skewed (module 07), so for small groups prefer Mann-Whitney or
check that the t-test and Mann-Whitney agree.

## 5. Effect size: significance is not importance

With enough data, tiny differences become "significant". Report the size of the difference,
e.g. **Cohen's d** = difference in means / pooled std (0.2 small, 0.5 medium, 0.8 large),
or a confidence interval for the difference.

```python
d = (a.mean() - b.mean()) / ((a.var() + b.var()) / 2) ** 0.5
```

## 6. Multiple testing trap

Run 20 tests on pure noise and about one will be "significant" at 0.05 by luck.
When testing many hypotheses, tighten alpha (**Bonferroni**: `alpha / number_of_tests`)
or decide your hypotheses *before* looking at the data.

## Sample output (`examples/tests_demo.py`)

| Test | Result |
|------|--------|
| Notebook vs Bag (Welch) | p = 0.008, Cohen d = -0.62 (medium) |
| Mann-Whitney, same groups | p = 0.020 — agrees |
| ANOVA across 4 products | p ~ 6e-26 — products differ strongly |
| Chi-square product x month | p = 0.106 — no evidence of dependence |

## Exercises
1. Test whether mean `quantity` differs between Pen and Marker orders. Report d.
2. Is revenue in Jan-Mar different from Apr-Jun? Use both t-test and Mann-Whitney.
3. Run 50 t-tests on random noise; count false positives with and without Bonferroni.

## Git note (see [git-notes](../git-notes/README.md))
`git blame` and `git diff main..branch` show who changed what and what a branch would merge.
