"""Basic statistics on data/sales.csv, by hand and with `statistics`."""
import csv
import statistics
from pathlib import Path

path = Path(__file__).resolve().parents[2] / "data" / "sales.csv"
with open(path) as f:
    rows = list(csv.DictReader(f))

quantities = [int(r["quantity"]) for r in rows]

# By hand
manual_mean = sum(quantities) / len(quantities)
print("mean (manual):", manual_mean)

# With the standard library
print("mean:  ", statistics.mean(quantities))
print("median:", statistics.median(quantities))
print("min/max:", min(quantities), max(quantities))
print("stdev: ", round(statistics.stdev(quantities), 2))
