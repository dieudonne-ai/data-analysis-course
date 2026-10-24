# Module 06 — Data Visualization

A good chart answers one question quickly. Library: `matplotlib`.
Dataset: [`data/students.csv`](../data/students.csv).

Diagram: [`diagrams/choose_chart.pdf`](diagrams/choose_chart.pdf) — which chart for which question.

## The basic pattern
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(df["score"], bins=15)
ax.set_xlabel("Score"); ax.set_ylabel("Number of students")
ax.set_title("Distribution of scores")
fig.savefig("hist.png", dpi=150, bbox_inches="tight")
```

## Chart types
| Question | Chart | Code |
|----------|-------|------|
| How is one number distributed? | Histogram | `ax.hist(x, bins=15)` |
| Compare groups? | Bar chart | `ax.bar(names, values)` |
| Spread per group, outliers? | Box plot | `ax.boxplot([a, b, c], tick_labels=[...])` |
| Relationship of two numbers? | Scatter | `ax.scatter(x, y)` |
| Change over time? | Line | `ax.plot(dates, values)` |

## Example: scatter with trend line
```python
import numpy as np
m, b = np.polyfit(df["study_hours"], df["score"], 1)
ax.scatter(df["study_hours"], df["score"], alpha=0.6)
ax.plot(df["study_hours"].sort_values(), m * df["study_hours"].sort_values() + b, color="red")
```

## Rules of thumb
- Always label axes and give a title that states the finding.
- Bar charts start at zero; scatter plots need not.
- Avoid 3D and pie charts with many slices.
- Use color to carry meaning, not decoration.

Script (produces 4 PNG files in `examples/output/`): [`examples/make_charts.py`](examples/make_charts.py)
