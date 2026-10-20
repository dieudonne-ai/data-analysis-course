# Module 01 — Introduction to Data Analysis

## What is data analysis?
Data analysis is the process of inspecting, cleaning, transforming and modelling data
to discover useful information and support decisions.

**Example:** A shop owner has a year of sales records. Analysis answers:
*Which product sells best? Which month is slowest? Do discounts increase revenue?*

## The analysis workflow
1. **Ask** a clear question ("Why did sales drop in March?")
2. **Collect** data (CSV files, databases, APIs)
3. **Clean** it (missing values, duplicates, wrong types)
4. **Explore** it (summaries, charts)
5. **Model / test** ideas (statistics)
6. **Communicate** results (charts, reports)

## Types of analysis
| Type | Question | Example |
|------|----------|---------|
| Descriptive | What happened? | Total sales per month |
| Diagnostic | Why did it happen? | Sales fell because stock ran out |
| Predictive | What will happen? | Forecast next month's sales |
| Prescriptive | What should we do? | Reorder 200 units of product A |

## Types of data
- **Numerical**: continuous (price = 12.5) or discrete (items sold = 3)
- **Categorical**: nominal (colour: red/blue) or ordinal (size: S < M < L)
- **Time series**: values ordered in time (daily temperature)
- **Text**: reviews, comments

## Structured data: rows and columns
Each **row** is an observation, each **column** a variable.

| order_id | product | quantity | price |
|---------:|---------|---------:|------:|
| 1 | Pen | 10 | 1.5 |
| 2 | Notebook | 3 | 4.0 |

## Example
Run [`examples/first_analysis.py`](examples/first_analysis.py) — it computes revenue
per product from a small dataset using only the standard library.

## Exercises
1. Name the type (numerical/categorical) of: age, country, rating (1–5 stars), temperature.
2. Write one descriptive and one diagnostic question for a restaurant's sales data.
