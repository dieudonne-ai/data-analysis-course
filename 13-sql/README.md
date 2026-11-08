# Module 13 – SQL for Analysts (bonus)

Most company data lives in databases, and you talk to databases with **SQL**.
We use **SQLite** (built into Python, no server needed) and the sales table from earlier modules.

Run it: `python 13-sql/examples/sql_basics.py` — the script prints every query and its result.

## 1. The five clauses you use every day
```sql
SELECT product, SUM(revenue) AS total   -- which columns / calculations
FROM sales                              -- which table
WHERE quantity >= 3                     -- filter ROWS before grouping
GROUP BY product                        -- make one row per product
HAVING total > 10                       -- filter GROUPS after aggregating
ORDER BY total DESC                     -- sort
LIMIT 5;                                -- keep the first 5 rows
```
Result on our data: `Pen 19.5`, `Notebook 12.0`.
Diagram: [`diagrams/query_order.pdf`](diagrams/query_order.pdf) — SQL *runs* in a different order than you *write* it
(FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY). That is why `WHERE` cannot use an aggregate but `HAVING` can.

## 2. Aggregates and GROUP BY
`COUNT`, `SUM`, `AVG`, `MIN`, `MAX` collapse many rows into one value.
```sql
SELECT product, COUNT(*) AS orders, ROUND(AVG(revenue), 2) AS avg_revenue
FROM sales GROUP BY product ORDER BY avg_revenue DESC;
```
| product | orders | avg_revenue |
|---|---|---|
| Bag | 1 | 25.00 |
| Notebook | 2 | 10.00 |
| Pen | 2 | 9.75 |

The pandas equivalent is `df.groupby("product")["revenue"].agg(...)` — the script checks both give the same numbers.
Diagram: [`diagrams/group_by.pdf`](diagrams/group_by.pdf) (split → aggregate → combine).

## 3. JOIN: combining tables
Real data is spread over several tables linked by a **key**.
```sql
SELECT c.category, SUM(s.revenue) AS revenue
FROM sales s JOIN categories c ON s.product = c.product
GROUP BY c.category;
```
`JOIN` (inner) keeps only matching rows; `LEFT JOIN` keeps every row of the left table and fills `NULL` when there is no match.
Diagram: [`diagrams/join.pdf`](diagrams/join.pdf). pandas equivalent: `df.merge(cats, on="product")`.

## 4. SQL vs pandas
| Task | SQL | pandas |
|---|---|---|
| filter rows | `WHERE x > 3` | `df[df.x > 3]` |
| aggregate | `GROUP BY` | `df.groupby()` |
| combine tables | `JOIN` | `df.merge()` |
| sort | `ORDER BY` | `df.sort_values()` |

Use SQL to pull and summarise big data *inside* the database; use pandas for cleaning, stats and plots afterwards.

## 5. Pitfalls
- `NULL` is not equal to anything: use `IS NULL`, never `= NULL`.
- `COUNT(*)` counts rows, `COUNT(col)` skips NULLs.
- Joining on a non-unique key **multiplies rows** and inflates sums — check row counts before and after a JOIN.
- Never build queries by pasting user input into strings; use placeholders: `con.execute("... WHERE product = ?", (name,))`.

## Exercises
1. Total revenue per month (`GROUP BY month`). Which month is best?
2. List products whose average quantity is above 5.
3. Write a `LEFT JOIN` from `sales` to `categories` after deleting one category row; what appears in the `category` column?
4. Reproduce exercise 1 with `df.groupby` and compare.

## Run it
```bash
python 13-sql/examples/sql_basics.py
python 13-sql/diagrams/make_diagrams.py
```

## Git for this module
See "Recovering lost work and saving time" in [git-notes](../git-notes/README.md).
