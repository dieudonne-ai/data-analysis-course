# Module 05 — Exploratory Data Analysis (EDA)

EDA means *looking at the data before modelling it*: summarise, compare groups,
find relationships and surprises. Dataset: [`data/students.csv`](../data/students.csv)
(200 synthetic students: `gender`, `track`, `study_hours`, `sleep_hours`, `score`).

Diagram: [`diagrams/eda_loop.pdf`](diagrams/eda_loop.pdf)

## 1. Overview
```python
df = pd.read_csv("data/students.csv")
df.describe()                 # numeric summary
df["track"].value_counts()    # categorical counts
```

## 2. Univariate: one variable
Mean vs median tells you about skew. Standard deviation tells you about spread.
```python
df["score"].mean(), df["score"].median(), df["score"].std()
```

## 3. Grouping and comparing
```python
df.groupby("track")["score"].agg(["count", "mean", "median"])
df.pivot_table(values="score", index="track", columns="gender", aggfunc="mean")
```
`groupby` = split the table by a category, apply a function, combine the results.
See [`diagrams/groupby.pdf`](diagrams/groupby.pdf).

## 4. Relationships between numbers
```python
df[["study_hours", "sleep_hours", "score"]].corr()
```
Correlation ranges from -1 to 1. In this dataset `study_hours` vs `score` is about 0.70:
students who study more tend to score higher.

> **Correlation is not causation.** A third factor (motivation, prior level)
> might drive both variables.

## 5. Questions to ask every time
1. How many rows/columns? Any missing values?
2. What does each variable look like (range, typical value, outliers)?
3. How do groups differ?
4. Which variables move together?
5. Does anything look wrong or surprising?

Script: [`examples/explore_students.py`](examples/explore_students.py)
