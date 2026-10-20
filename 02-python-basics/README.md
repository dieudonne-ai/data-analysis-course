# Module 02 — Python Basics for Analysts

## Variables and types
```python
name = "Amina"      # str
age = 29            # int
height = 1.68       # float
is_member = True    # bool
```

## Lists and dictionaries
```python
prices = [1.5, 4.0, 25.0]            # list: ordered, indexable
prices[0]                            # 1.5
product = {"name": "Pen", "price": 1.5}   # dict: key -> value
product["price"]                     # 1.5
```

## Loops and comprehensions
```python
doubled = [p * 2 for p in prices]            # [3.0, 8.0, 50.0]
expensive = [p for p in prices if p > 3]     # [4.0, 25.0]
```

## Functions
```python
def mean(values):
    return sum(values) / len(values)

mean([2, 4, 6])   # 4.0
```

## Reading a CSV with the standard library
```python
import csv
with open("data/sales.csv") as f:
    rows = list(csv.DictReader(f))
```
Note: every value is read as a **string** — convert with `float(...)` or `int(...)`.

## Example
[`examples/stats_basics.py`](examples/stats_basics.py) computes mean, median, min and max
by hand and with the `statistics` module, using `data/sales.csv`.

## Exercises
1. Write a function returning the largest value in a list without using `max`.
2. From `data/sales.csv`, list the products with quantity above 5.
