"""SQL for analysts: load a CSV into SQLite, query it, and compare with pandas."""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "data" / "sales_clean.csv")
con = sqlite3.connect(":memory:")          # a throw-away database living in RAM
df.to_sql("sales", con, index=False)
print("columns:", list(df.columns), "\n")


def q(sql):
    print(sql.strip(), "\n", pd.read_sql(sql, con).to_string(index=False), "\n", sep="")


q("SELECT * FROM sales LIMIT 3")                                              # SELECT + LIMIT
q("SELECT COUNT(*) AS n_orders, ROUND(SUM(revenue), 2) AS revenue FROM sales")  # aggregates
q("""SELECT product, COUNT(*) AS orders, ROUND(AVG(revenue), 2) AS avg_revenue
     FROM sales GROUP BY product ORDER BY avg_revenue DESC""")                # GROUP BY
q("""SELECT product, ROUND(SUM(revenue), 2) AS total
     FROM sales WHERE quantity >= 3 GROUP BY product
     HAVING total > 10 ORDER BY total DESC""")                                # WHERE vs HAVING

# JOIN: a small lookup table of product categories
cats = pd.DataFrame({"product": df["product"].unique()})
cats["category"] = ["Stationery"] * len(cats)
cats.loc[cats.index % 2 == 1, "category"] = "Office"
cats.to_sql("categories", con, index=False)
q("""SELECT c.category, ROUND(SUM(s.revenue), 2) AS revenue
     FROM sales s JOIN categories c ON s.product = c.product
     GROUP BY c.category ORDER BY revenue DESC""")

# Same question as the GROUP BY above, in pandas: results must match
print(df.groupby("product")["revenue"].agg(orders="size", avg_revenue="mean").round(2)
        .sort_values("avg_revenue", ascending=False))
