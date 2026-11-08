"""Generate PDF diagrams for module 13 (SQL for analysts)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, fc="#dbeafe", fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.04", fc=fc, ec="#334155"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


# 1. Logical order of a SELECT query
fig, ax = plt.subplots(figsize=(11, 3.4)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3.4)
steps = [("FROM / JOIN", "pick tables"), ("WHERE", "filter rows"), ("GROUP BY", "make groups"),
         ("HAVING", "filter groups"), ("SELECT", "choose columns"), ("ORDER BY\nLIMIT", "sort & cut")]
for i, (k, v) in enumerate(steps):
    x = .15 + i * 1.8
    box(ax, x, 1.4, 1.5, .9, k, fc="#1e3a8a" if k == "SELECT" else "#dbeafe")
    if k == "SELECT": ax.texts[-1].set_color("w")
    ax.text(x + .75, 1.0, v, ha="center", fontsize=9, color="#475569")
    if i < 5: ax.annotate("", (x + 1.75, 1.85), (x + 1.5, 1.85), arrowprops=dict(arrowstyle="->"))
ax.set_title("SQL runs in this order, not the order you write it", weight="bold")
fig.savefig(OUT / "query_order.pdf", bbox_inches="tight"); plt.close(fig)

# 2. JOIN: two tables matched on a key
fig, ax = plt.subplots(figsize=(10, 4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
ax.text(1.6, 3.6, "sales", weight="bold", ha="center"); ax.text(8.4, 3.6, "categories", weight="bold", ha="center")
sales = ["Pen", "Notebook", "Pen", "Stapler"]; cats = [("Pen", "Stationery"), ("Notebook", "Office"), ("Stapler", "Office")]
for i, p in enumerate(sales): box(ax, .6, 2.7 - i * .75, 2, .55, p)
for i, (p, c) in enumerate(cats): box(ax, 6.4, 2.7 - i * .75, 4 - .6 - .2 + .2, .55, f"{p} | {c}", fc="#dcfce7")
links = [(0, 0), (1, 1), (2, 0), (3, 2)]
for s, c in links: ax.annotate("", (6.4, 2.97 - c * .75), (2.6, 2.97 - s * .75), arrowprops=dict(arrowstyle="->", color="#1e3a8a"))
ax.text(4.5, .3, "JOIN ... ON sales.product = categories.product", ha="center", family="monospace", fontsize=10)
fig.savefig(OUT / "join.pdf", bbox_inches="tight"); plt.close(fig)

# 3. GROUP BY: split - aggregate - combine
fig, ax = plt.subplots(figsize=(10, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.6)
box(ax, .2, 1, 2, 1.6, "all rows\nPen 15\nBook 12\nPen 9\nBook 8", fc="#f1f5f9")
box(ax, 3.4, 1.9, 2.2, .9, "Pen: 15, 9", fc="#fef3c7"); box(ax, 3.4, .8, 2.2, .9, "Book: 12, 8", fc="#fce7f3")
box(ax, 7, 1.9, 2.6, .9, "Pen  → SUM = 24", fc="#fef3c7"); box(ax, 7, .8, 2.6, .9, "Book → SUM = 20", fc="#fce7f3")
for y in (2.35, 1.25):
    ax.annotate("", (3.4, y), (2.2, 1.8), arrowprops=dict(arrowstyle="->")); ax.annotate("", (7, y), (5.6, y), arrowprops=dict(arrowstyle="->"))
ax.text(2.8, 3.1, "split", ha="center", color="#475569"); ax.text(6.3, 3.1, "aggregate", ha="center", color="#475569")
ax.set_title("GROUP BY = split → aggregate → combine (like pandas groupby)", weight="bold")
fig.savefig(OUT / "group_by.pdf", bbox_inches="tight"); plt.close(fig)
