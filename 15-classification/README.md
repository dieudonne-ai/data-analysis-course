# Module 15 – Classification & Model Evaluation (bonus)

Regression predicts a **number** (module 09). Classification predicts a **category**: will this customer churn? is this email spam? This module builds a logistic regression from scratch and shows how to judge it honestly.

Run it: `python 15-classification/examples/churn_model.py` — it generates `data/churn.csv` (600 customers), trains a model and prints the metrics.

## 1. From a score to a probability
Diagram: [`diagrams/sigmoid.pdf`](diagrams/sigmoid.pdf)

Logistic regression computes a score `z = w0 + w1*tenure + w2*calls`, then squashes it with the **sigmoid** into a probability between 0 and 1:

```python
sigmoid = lambda z: 1 / (1 + np.exp(-z))
sigmoid(0)    # 0.5  -> on the fence
sigmoid(3)    # 0.95 -> very likely churn
sigmoid(-3)   # 0.05 -> very likely stay
```
Predict "churn" when the probability is at least the **threshold** (0.5 by default).

## 2. The workflow
Diagram: [`diagrams/classification_workflow.pdf`](diagrams/classification_workflow.pdf)

1. Split the data: 70% train / 30% test (as in module 09).
2. Scale the features using the **train** mean and std only.
3. Fit the weights by gradient descent on the train set.
4. Predict on the test set and evaluate there. Never grade a model on data it has already seen.

## 3. The confusion matrix
Diagram: [`diagrams/confusion_matrix.pdf`](diagrams/confusion_matrix.pdf)

Example output on the test set:

| | predicted churn | predicted stay |
|---|---|---|
| **actual churn** | TP = 32 | FN = 25 |
| **actual stay** | FP = 20 | TN = 103 |

| Metric | Formula | Example | Meaning |
|---|---|---|---|
| Accuracy | (TP+TN)/all | 0.75 | share of correct predictions |
| Precision | TP/(TP+FP) | 0.62 | when we say "churn", how often are we right? |
| Recall | TP/(TP+FN) | 0.56 | of the real churners, how many did we catch? |
| F1 | 2PR/(P+R) | 0.59 | one number balancing both |

**Beware accuracy.** Only 36% of customers churn, so a model that always says "stay" scores 64–68% accuracy while catching nobody. Always compare to this **baseline**.

## 4. Choosing the threshold
Diagram: [`diagrams/threshold_tradeoff.pdf`](diagrams/threshold_tradeoff.pdf)

| Threshold | Precision | Recall |
|---|---|---|
| 0.3 | 0.50 | 0.82 |
| 0.5 | 0.62 | 0.56 |
| 0.7 | 0.68 | 0.26 |

Lowering the threshold catches more churners (higher recall) but sends more false alarms (lower precision). Choose from the business cost:
- Retention offer costs 5 EUR, a lost customer costs 200 EUR -> favour **recall**.
- Each alarm triggers an expensive manual call -> favour **precision**.

## 5. Reading the weights
With scaled features, the sign of a weight gives the direction: `tenure` is negative (loyal customers stay), `support_calls` is positive (frustrated customers leave). A prediction for a 6-month customer with 5 calls: **93% churn probability**.

## 6. Exercises
1. Change the threshold to 0.2 and 0.9. How do precision and recall move?
2. Add a feature (e.g. `monthly_fee`) to the data generator and see if F1 improves.
3. Compute the baseline accuracy and write one sentence explaining why accuracy alone is misleading here.

Next: the course now covers analysis, statistics, SQL, storytelling and prediction – pick your own dataset and publish a project!
