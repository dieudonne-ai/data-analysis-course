"""A first analysis with the standard library: revenue per product."""
from collections import defaultdict

orders = [
    {"product": "Pen", "quantity": 10, "price": 1.5},
    {"product": "Notebook", "quantity": 3, "price": 4.0},
    {"product": "Pen", "quantity": 5, "price": 1.5},
    {"product": "Bag", "quantity": 1, "price": 25.0},
]

revenue = defaultdict(float)
for o in orders:
    revenue[o["product"]] += o["quantity"] * o["price"]

for product, total in sorted(revenue.items(), key=lambda kv: -kv[1]):
    print(f"{product:10s} {total:8.2f}")
print("Total revenue:", sum(revenue.values()))
