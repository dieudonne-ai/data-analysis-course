# Module 14 – Data Storytelling & Reporting (bonus)

A correct analysis nobody understands changes nothing. This module turns numbers into a **message** and a **reproducible report**.

Run it: `python 14-storytelling/examples/build_report.py` — it reads `data/monthly_sales.csv`, draws one focused chart and writes `examples/report.md`.

## 1. Context → Insight → Action
Diagram: [`diagrams/story_structure.pdf`](diagrams/story_structure.pdf)

| Step | Question | Example |
|---|---|---|
| Context | Who is the audience, what do they need to decide? | "Should we raise the Q3 marketing budget?" |
| Insight | What is the single most important finding? | "Revenue grew 78% since January (110 -> 196)." |
| Action | What do you recommend? | "Investigate the spring drop before approving budget." |

Bad: "Here are 12 charts." Good: "Revenue is down 9%; here is the one chart that shows why, and what to do."

## 2. Choosing the right chart
| You want to show | Use | Avoid |
|---|---|---|
| change over time | line chart | pie chart |
| compare categories | bar chart (sorted) | 3D bars |
| relationship of two numbers | scatter plot | dual y-axes |
| distribution | histogram / box plot | averages only |

## 3. Declutter: make the insight impossible to miss
Diagram: [`diagrams/declutter.pdf`](diagrams/declutter.pdf)
1. **Title = the conclusion** ("Sales jumped 60% in May"), not the topic ("Sales by month").
2. **Grey for context, one strong colour for the point** you want people to see.
3. Remove gridlines, borders and legends you do not need; label values directly.
4. Start bar charts at zero; never truncate the axis to exaggerate.

```python
ax.plot(x, y, color="#cbd5e1")                 # context in light grey
ax.plot(x[-1], y[-1], "o", color="#1e3a8a")    # the key point in a strong colour
ax.set_title("Revenue grew 78% since January", loc="left", weight="bold")
```

## 4. A reproducible report
Diagram: [`diagrams/report_workflow.pdf`](diagrams/report_workflow.pdf)
Never paste numbers by hand. Let the script compute them and write the text (f-strings), so re-running on new data updates the whole report.
```python
headline = f"Revenue {'grew' if change >= 0 else 'fell'} {abs(change):.0f}% over the period"
```
Example numbers: `110.4 -> last value`, change = `(last - first) / first * 100`.

## 5. Exercises
1. Change the script to highlight the *lowest* month instead of the last one.
2. Add a second insight (best month) to `report.md`.
3. Rewrite three chart titles from your earlier modules so each states a conclusion.

Next: the course is complete – re-run everything and publish your own project!
