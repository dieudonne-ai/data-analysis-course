# Module 06 - Data Visualization

A good chart answers one question quickly. Library: `matplotlib` (with pandas' `.plot`).

Diagrams: [chart chooser](diagrams/chart_chooser.pdf) - [figure anatomy](diagrams/figure_anatomy.pdf)

## Choose the chart from the question
| Question | Chart | Example |
|----------|-------|---------|
| Compare categories | Bar | average spend by city |
| Distribution of one variable | Histogram, box plot | age of customers |
| Relationship of two numbers | Scatter | income vs spend |
| Change over time | Line | monthly revenue |

## The matplotlib pattern
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()          # a canvas (fig) and a plotting area (ax)
ax.scatter(df["income"], df["spend"], s=14, alpha=.6)
ax.set_title("Income vs spend")
ax.set_xlabel("income"); ax.set_ylabel("spend")
fig.savefig("scatter.pdf", bbox_inches="tight")
```

## One example per chart type
```python
df.groupby("city")["spend"].mean().sort_values().plot.barh()   # bar
plt.hist(df["age"], bins=10)                                    # histogram
df.boxplot(column="spend", by="group")                          # box plot
sales.groupby("month", sort=False)["revenue"].sum().plot(marker="o")  # line
```
The script `examples/charts.py` produces all five as PDF files in `examples/output/` (not committed - it is in `.gitignore`).

## Rules of good charts
1. **Title and axis labels** - always, with units.
2. **Start bars at zero** - truncated bars exaggerate differences.
3. **Sort bars** by value unless the categories have a natural order (months).
4. **Few colours**, and never rely on colour alone.
5. **No 3D, no pie charts with more than 4 slices.**
6. Use `alpha` on scatter plots to show overlapping points.

## Exercises
1. Plot a histogram of `income` with 15 bins. Is it symmetric?
2. Make a bar chart of mean `visits` by group.
3. Draw a scatter of `age` vs `income`, coloured by `city` (hint: loop over `df.groupby("city")`).
4. Save every figure as PDF and open it.

Run the worked example: `python 06-visualization/examples/charts.py`
