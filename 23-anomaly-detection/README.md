# Module 23 – Anomaly Detection (bonus)

Every dataset hides a few rows that "don't look like the others": a 600 EUR coffee, a payment at 3 a.m., a month where revenue doubles. Some are **errors** (a typo, a duplicated invoice), some are **fraud**, and some are **real events** (a big client, a holiday). Anomaly detection is the art of finding them *before* they distort your averages or your business.

This module builds four detectors from scratch with numpy and compares them on 500 card transactions in which 15 anomalies were planted (so we can measure precision and recall, module 15).

Run it: `python 23-anomaly-detection/examples/anomaly_demo.py` (numpy only; it creates `data/transactions.csv` the first time).
Rebuild the diagrams: `python 23-anomaly-detection/diagrams/make_diagrams.py`.

## 1. The workflow
Diagram: [`diagrams/workflow.pdf`](diagrams/workflow.pdf)

1. **Define "normal"** – which columns, which period, which customers?
2. **Transform** – log of skewed amounts; residuals instead of raw values for time series.
3. **Score** every row – how far is it from normal?
4. **Threshold** – e.g. `|z| > 3`, or "the top 1% scores", sized to how many cases a human can review.
5. **Review** – a person decides: error, fraud or real event? Confirmed cases become labels you use to tune the thresholds.

Anomaly detection is usually **unsupervised**: you rarely have labels at the start. A detector is a *triage tool* that orders rows for review, not a judge.

## 2. One feature: z-score, robust z-score and IQR fences
Diagram: [`diagrams/detectors.pdf`](diagrams/detectors.pdf)

```python
def zscore(x):                       # distance from the mean, in standard deviations
    return (x - x.mean()) / x.std()

def robust_z(x):                     # same idea with median and MAD (median absolute deviation)
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return 0.6745 * (x - med) / mad  # 0.6745 rescales MAD to match a normal std

def iqr_fences(x, k=1.5):            # the box-plot rule from module 05
    q1, q3 = np.percentile(x, [25, 75])
    return q1 - k * (q3 - q1), q3 + k * (q3 - q1)
```
```
   z-score |z|>3                flagged   7  TP  7  FP  0  FN  8  precision 1.00  recall 0.47
   robust z |rz|>3.5            flagged  14  TP  7  FP  7  FN  8  precision 0.50  recall 0.47
   IQR fences [-7.0, 71.9]      flagged  17  TP  7  FP 10  FN  8  precision 0.41  recall 0.47
   robust z on log(amount)      flagged   8  TP  7  FP  1  FN  8  precision 0.88  recall 0.47
```
What this teaches:
- All four find the 7 **huge amounts** – and none finds the 8 other anomalies (recall 0.47). Those are night-time payments with a perfectly ordinary amount: **a one-column rule cannot see them** (section 3).
- Robust z and IQR raise false alarms because amounts are **skewed** (a long right tail of honest 80–120 EUR purchases). Taking the **log** first makes the distribution symmetric: precision jumps from 0.50 to 0.88.

### The masking effect
```
   std with anomalies 46.4  vs  without 16.1
   so a 120 EUR payment has z = 1.75 (looks normal) but robust z = 6.31
```
Only 3% of the rows are anomalies, but they almost **triple the standard deviation** – the very ruler we measure them with. Big outliers *mask* medium ones. The median and MAD barely move (right panel of the diagram), which is why robust statistics are the default for outlier hunting.

| Method | Uses | Good for | Weak when |
|---|---|---|---|
| z-score | mean, std | clean, bell-shaped data | outliers inflate the std (masking) |
| robust z | median, MAD | most real data | > 50% identical values (MAD = 0) |
| IQR fences | Q1, Q3 | quick checks, box plots | skewed data (use log first) |

## 3. Several features: Mahalanobis distance
Diagram: [`diagrams/mahalanobis.pdf`](diagrams/mahalanobis.pdf)

A 45 EUR payment is normal. A payment at 3 a.m. happens. But the **combination** is what we want to catch. Mahalanobis distance is the multi-column z-score: it measures distance from the centre *in units of the data's own spread and correlation*.

```python
def mahalanobis(X):
    mu = X.mean(axis=0)
    cov_inv = np.linalg.inv(np.cov(X, rowvar=False))
    D = X - mu
    return np.sqrt(np.einsum("ij,jk,ik->i", D, cov_inv, D))   # sqrt(d' Σ⁻¹ d) for every row
```
```
   night anomalies caught by amount-IQR alone: 0 of 8
   night anomalies caught by hour-IQR alone [4h, 24h]: 8 of 8
   Mahalanobis(amount, hour)      > 3.0: flagged  15  TP 15  FP  0  FN  0  precision 1.00  recall 1.00
   Mahalanobis(log amount, hour)  > 3.0: flagged  18  TP 15  FP  3  FN  0  precision 0.83  recall 1.00
```
Each single-column rule sees only one kind of anomaly; **one Mahalanobis score catches both kinds**. The ellipses in the diagram are the lines of equal distance (d = 1, 2, 3).

Honest caveat: our planted anomalies are very clean, so 100% recall is optimistic. On real data expect a trade-off, and remember that Mahalanobis assumes a roughly elliptical cloud – for complex shapes, tools like *Isolation Forest* or *Local Outlier Factor* (`sklearn.ensemble.IsolationForest`, `sklearn.neighbors.LocalOutlierFactor`) follow the same score → threshold → review workflow.

## 4. Time series: compare with the neighbours
Diagram: [`diagrams/rolling.pdf`](diagrams/rolling.pdf)

Monthly revenue (module 11) has a trend and a seasonal pattern, so the global mean is useless: every recent month would look "high". Instead compare each month with its **neighbours**, then run a robust z-score on the residuals.

```python
def rolling_anomalies(values, window=5, k=3.5):
    half = window // 2
    centre = np.array([np.median(np.r_[values[max(0, i - half):i], values[i + 1:i + 1 + half]])
                       for i in range(len(values))])   # 2 months before + 2 after, not the month itself
    resid = values - centre
    return np.abs(robust_z(resid)) > k, centre
```
We simulated two glitches (a duplicated invoice ×1.6 and an outage ×0.45):
```
   2024-03: revenue   215.8  expected ~ 134.6  -> investigate
   2025-04: revenue    71.7  expected ~ 160.2  -> investigate
```
Both are found, with no false alarms, even though 215.8 is *not* the highest value in the series. Excluding the month itself from its own baseline matters: otherwise the anomaly pulls the "expected" value towards itself (masking again). For live monitoring, use only *past* months (a trailing window) since the future is not known yet.

## 5. What to do with an anomaly
- **Never delete automatically.** Flag, investigate, then decide.
- **Error** → fix at the source and document it (module 04).
- **Fraud / incident** → escalate; keep the row as a labelled example.
- **Real but rare event** → keep it, maybe analyse it separately (a key account can be 30% of revenue).
- Report how many rows you flagged and why – "we excluded 7 transactions above 250 EUR" is part of an honest analysis (module 14).

## Git corner: spotting unusual commits
Diagram: [`diagrams/git_commit_outliers.pdf`](diagrams/git_commit_outliers.pdf)

The same idea works on a repository's history. `git log --numstat` prints lines added/deleted per file for every commit:
```bash
git log --no-merges --numstat --pretty=format:@%h%x09%s \
  | awk -F'\t' '/^@/{if(h)print t, h; h=$0; t=0; next} NF==3 && $1!="-"{t+=$1+$2} END{print t,h}' \
  | sort -n | tail -3
```
In this course the outlier is module 12 (≈ 4,200 lines) – not a mistake, it added the 4,000-row `ab_test.csv`. A real event, not an error: exactly the review step from section 1. More commands are in the [Git notes](../git-notes/README.md#filtering-history-and-finding-unusual-commits).

## Exercises
1. Change the threshold of the robust z-score from 3.5 to 3 and to 5. Plot precision and recall against the threshold.
2. Add a third column `merchant_distance_km` (normally ~5 km, 2% of rows at 500+ km) and extend the Mahalanobis detector.
3. Make the time-series detector use only the **previous** 6 months. Which glitch is found later, and why?
4. Run the commit-size pipeline on another repository you know. Is its biggest commit an error, a data file or a big refactor?
