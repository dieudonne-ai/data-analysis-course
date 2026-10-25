# Module 07 - Statistics Fundamentals

Statistics lets us say something about a **population** from a **sample**.
Dataset: [`data/customers.csv`](../data/customers.csv), column `spend`.

Diagrams: [normal distribution](diagrams/normal_rule.pdf) - [central limit theorem](diagrams/central_limit.pdf) - [confidence interval](diagrams/confidence_interval.pdf)

## Describing a variable
| Measure | pandas | Meaning | spend |
|---------|--------|---------|-------|
| Mean | `x.mean()` | arithmetic average | 120.2 |
| Median | `x.median()` | middle value, robust to outliers | 120.3 |
| Std deviation | `x.std()` | typical distance from the mean | 28.8 |
| IQR | `q3 - q1` | spread of the middle 50 % | 38.0 |

## The normal distribution
Many variables look bell-shaped. For a normal variable, 68 % of values lie within 1 std of the mean, 95 % within 2, 99.7 % within 3.
In our data: 71.0 %, 94.5 %, 99.5 % - spend is close to normal.

## Sampling and the central limit theorem
Means of samples are approximately normal, **even if the population is not**, as long as samples are large enough (n >= 30 is a common rule).
The spread of sample means is the **standard error**: `SE = std / sqrt(n)`.
In the example, the std of 1000 sample means (n=30) is 4.82, close to the theory (5.27).

## Confidence interval
A 95 % CI gives a range likely to contain the true population mean.
```python
se = x.std() / np.sqrt(len(x))
lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=se)
# mean spend = 120.2, 95% CI = [116.1, 124.2]
```
Bigger sample -> smaller SE -> narrower interval.

## Probability from a model
`1 - stats.norm.cdf(150, x.mean(), x.std())` gives P(spend > 150) = 15.1 % under the normal model; 12.0 % observed. Models are approximations.

## Exercises
1. Compute the 95 % CI for mean `visits`.
2. What is the probability that a customer is younger than 25 (observed)?
3. Draw 500 samples of size 50 from `income`; verify the std of their means matches `std / sqrt(50)`.
4. Why does doubling the sample size not halve the confidence interval width?

Run the worked example: `python 07-statistics/examples/stats_demo.py`
