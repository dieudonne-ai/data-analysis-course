# Module 05 - Exploratory Data Analysis (EDA)

EDA means looking at the data *before* modelling: what is in it, what is unusual, what relates to what.
Dataset: [`data/customers.csv`](../data/customers.csv) - 200 synthetic customers (age, city, A/B group, visits, income, spend).
Regenerate it with `python data/make_customers.py` (seeded, so always identical).

Diagrams: [EDA loop](diagrams/eda_loop.pdf) - [univariate vs bivariate](diagrams/univariate_bivariate.pdf) - [correlation heatmap](diagrams/correlation_heatmap.pdf)

## Step 1 - Structure
```python
df.shape; df.dtypes; df.head()
```

## Step 2 - One variable at a time (univariate)
```python
df["spend"].describe()                       # mean 120.2, median 120.3
df["city"].value_counts(normalize=True)      # Kampala = 39 % of customers
```
Compare mean and median: if they differ a lot, the distribution is skewed.

## Step 3 - Two variables (bivariate)
```python
df.groupby("city")["spend"].agg(["count", "mean", "median"])
df.pivot_table(values="spend", index="city", columns="group", aggfunc="mean")
df[["age", "income", "spend"]].corr()
```
What the example output shows:
- Kigali customers spend the most (126.6 on average), Dar es Salaam the least (112.1).
- Group B spends more than group A in *every* city - a hint for module 08.
- `age` and `income` are strongly correlated (0.79); `income` and `spend` moderately (0.49).

## Correlation: how to read it
| r | Meaning |
|---|---------|
| close to +1 | both rise together |
| close to 0 | no linear relation |
| close to -1 | one rises, the other falls |

**Correlation is not causation.** Older customers have higher income *and* spend more - age may drive both.

## Exercises
1. Which city has the highest median `visits`?
2. Is the distribution of `income` symmetric? Compare mean and median.
3. Build a pivot table of mean `visits` by city and group.
4. Find the five customers with the highest spend. What do they have in common?

Run the worked example: `python 05-eda/examples/explore_customers.py`
