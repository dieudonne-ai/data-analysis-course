# Module 07 — Statistics Fundamentals

Statistics lets us describe data and reason about a whole **population**
from a **sample**. Dataset: [`data/students.csv`](../data/students.csv).

Diagrams: [`diagrams/normal_distribution.pdf`](diagrams/normal_distribution.pdf),
[`diagrams/population_sample.pdf`](diagrams/population_sample.pdf)

## Descriptive statistics
| Idea | Measure | pandas |
|------|---------|--------|
| Center | mean, median | `s.mean()`, `s.median()` |
| Spread | std, IQR | `s.std()`, `s.quantile(.75) - s.quantile(.25)` |
| Shape | skewness | `s.skew()` |

Example: scores have mean 69.9, median 70.2, std 8.9 — mean ≈ median, so the shape is roughly symmetric.

## The normal distribution
Many measurements follow a bell curve. The **68-95-99.7 rule**: about 68% of values lie within
1 std of the mean, 95% within 2, 99.7% within 3. In our data, 68% of scores are within 1 std.

A **z-score** `(x - mean) / std` says how many standard deviations a value is from the mean.

## Population vs sample
We rarely observe everyone, so we take a sample and *estimate*.
The **standard error** `std / sqrt(n)` measures how much a sample mean varies.

## Confidence intervals
A 95% confidence interval gives a range likely to contain the true mean:
```python
from scipy import stats
se = s.std() / len(s) ** 0.5
stats.t.interval(0.95, len(s) - 1, loc=s.mean(), scale=se)   # (68.6, 71.1)
```
Meaning: if we repeated the study many times, about 95% of such intervals would contain the true mean.

## Central Limit Theorem
Means of random samples are approximately normal, even if the data is not,
and their spread shrinks as the sample grows. The script confirms this by simulation.

Script: [`examples/stats_demo.py`](examples/stats_demo.py)
