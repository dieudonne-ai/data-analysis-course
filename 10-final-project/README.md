# Module 10 — Final Project

Put the whole course together in one reproducible analysis.

## Brief
A school wants to know **what drives student scores** and whether it can
predict them. Using [`data/students.csv`](../data/students.csv), deliver a short report that:

1. **Loads and inspects** the data (Module 03) and **cleans** it if needed (Module 04).
2. **Explores** it: summary statistics, group comparisons, correlations (Module 05).
3. **Visualises** at least three findings (Module 06).
4. **Tests** at least two hypotheses and states the conclusions (Modules 07-08).
5. **Fits a regression**, evaluated on held-out data (Module 09).
6. Ends with **three recommendations** and the **limits** of the analysis.

Diagram of the full workflow: [`diagrams/project_workflow.pdf`](diagrams/project_workflow.pdf)

## Git requirements
- Work on a branch, commit after each step with a clear message, and open a pull request.
- Include a `requirements.txt` and a `README.md` explaining how to rerun everything.

## Rubric
| Criterion | Points |
|-----------|--------|
| Data inspection & cleaning | 15 |
| EDA quality | 20 |
| Charts (labels, titles, right chart type) | 20 |
| Statistical tests (correct choice, correct interpretation) | 20 |
| Regression with train/test evaluation | 15 |
| Clear conclusions and limits | 10 |

## Reference solution
[`examples/final_report.py`](examples/final_report.py) runs the full pipeline and writes
`output/report.md` plus a figure. Run it, then try to improve it (for example add `track` to the
model with dummy variables, or use cross-validation).

Key results from the reference solution: study hours is by far the strongest driver of score
(r = 0.70); gender and track show no significant difference in mean score; the two-variable
linear model reaches R² ≈ 0.56 on training data but only ≈ 0.30 on a 40-row hold-out set
(RMSE ≈ 6 points), so a large share of the variation comes from factors not in the dataset.
