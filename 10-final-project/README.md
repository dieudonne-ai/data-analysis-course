# Module 10 - Final Project

Put everything together: from a question to a written recommendation.
Diagram: [project flow](diagrams/project_flow.pdf)

## The brief
> The company tested a new checkout page (group B) against the old one (group A).
> Should it roll the new page out? Which customers matter most?

## Steps (each one = one commit in your own repository)
1. **Question** - write the question and the metric (`spend`) in `NOTES.md`.
2. **Load** - `pd.read_csv("data/customers.csv")`, check shape and types.
3. **Clean** - duplicates, missing values, text consistency (module 04).
4. **Explore** - summary by city and group, correlation matrix, 3 charts (modules 05-06).
5. **Test** - A/B t-test and effect size (module 08).
6. **Model** - regression of spend on income, visits, group (module 09).
7. **Report** - a short Markdown report with numbers, charts and a recommendation.

## Template
[`examples/report.py`](examples/report.py) runs the whole pipeline and writes `examples/output/report.md`:
```bash
python 10-final-project/examples/report.py
```
Output (excerpt): *Group B spends 11.9 more than A (t = 2.95, p = 0.0036). The difference is statistically significant.*

## Grading checklist
- [ ] Question and metric stated
- [ ] Cleaning steps documented
- [ ] At least 3 charts with titles and labelled axes
- [ ] Test with H0/H1, p-value **and** effect size
- [ ] Limits mentioned (synthetic data, correlation is not causation)
- [ ] Clear recommendation
- [ ] Clean Git history (see [Git notes](../git-notes/README.md))

## Going further
Try your own dataset (open data portals, Kaggle), then learn `seaborn`, `scikit-learn` and SQL.
