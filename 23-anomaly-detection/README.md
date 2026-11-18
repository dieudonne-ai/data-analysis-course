# Module 23 – Anomaly Detection (bonus)

Every analyst eventually gets the message *"the numbers look weird today – is something broken?"*. Anomaly detection turns that gut feeling into a rule a computer can check every morning. In this module we look at one year of daily orders of an online shop (`data/daily_orders.csv`) in which six real incidents happened, and we compare five detectors – all in a few lines of numpy/pandas.

Run it: `python 23-anomaly-detection/examples/anomaly_demo.py`
Rebuild the data: `python 23-anomaly-detection/examples/make_data.py` · the diagrams: `python 23-anomaly-detection/diagrams/make_diagrams.py`

| date | what happened | why it is tricky |
|---|---|---|
| Feb 14 | Valentine's promo: +150 orders | easy – very large |
| Apr 03 | payment outage: orders collapse to 22 | easy – very small |
| Jun 09 | spike on a **Monday** (293 orders) | 293 is a normal **Saturday** |
| Aug 20 | bot traffic on a Wednesday | each column alone looks normal |
| Oct 07 | pricing bug: baskets 14 EUR too expensive | orders are normal, only the basket moved |
| Nov 28 | Black Friday | easy – very large |

The `incident` column holds these labels, so we can **measure** each detector with precision and recall (module 15).

## 1. Choosing a method
Diagram: [`diagrams/methods_map.pdf`](diagrams/methods_map.pdf)

An anomaly is a point that does not fit the model of "normal". So the real question is: **what does normal look like?** A single bell-shaped column, a series with a weekly rhythm, or several columns that move together – each needs a different tool.

## 2. One column: z-score, IQR and robust z
Diagram: [`diagrams/fences.pdf`](diagrams/fences.pdf)

```python
z = (x - x.mean()) / x.std()                  # classic z-score, flag |z| > 3

q1, q3 = np.percentile(x, [25, 75])           # Tukey / box-plot fences
lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)

med = np.median(x)                            # robust z: median and MAD
mad = np.median(np.abs(x - med))
rz = (x - med) / (1.4826 * mad)               # flag |rz| > 3.5
```
```
z-score |z|>3       flagged 3  caught 3/6  false alarms 0  precision 1.00  recall 0.50
IQR k=1.5           flagged 3  caught 3/6  false alarms 0  precision 1.00  recall 0.50
robust z |z|>3.5    flagged 3  caught 3/6  false alarms 0  precision 1.00  recall 0.50
   std WITHOUT the incidents would be 31.7 (with them: 36.7): outliers inflate the std (masking)
```
All three find Valentine's day, the outage and Black Friday – and nothing else.

- **Masking**: the outliers themselves make the mean and std bigger, so the fence moves away and smaller anomalies hide behind it. With many outliers the z-score can miss *all* of them.
- **Median and MAD** (median absolute deviation) barely move when a few points are extreme – that is why the robust z is the safe default. The 1.4826 factor makes MAD equal to the std for normal data, so thresholds stay comparable.
- **IQR fences** are what a box plot draws (module 06). They do not assume a bell shape.

## 3. Time series: remove the pattern first
Diagram: [`diagrams/seasonal_residuals.pdf`](diagrams/seasonal_residuals.pdf)

On a Monday, 293 orders is extraordinary; on a Saturday it is routine. A fence on the raw column cannot know that. The fix (module 11): **subtract what you expect**, then look for outliers in what is left.
```python
trend = df["orders"].rolling(29, center=True, min_periods=1).median()   # slow movement
detrended = df["orders"] - trend
weekday_effect = detrended.groupby(df["weekday"]).transform("median")   # typical Mon, Tue, ...
residual = detrended - weekday_effect
flags = np.abs(robust_z(residual)) > 3.5
```
```
seasonal robust z |z|>3.5   flagged 6  caught 5/6  false alarms 1  precision 0.83  recall 0.83
     2025-03-12 Wed orders=161   [normal]     <- a genuinely slow day, worth a look anyway
     2025-06-09 Mon orders=293   [INCIDENT]   <- now visible
     2025-08-20 Wed orders=291   [INCIDENT]   <- now visible
```
Medians (not means) are used for the trend and the weekday effect so that the anomalies do not leak into the "expected" value.

Still missing: the **pricing bug** – orders were normal that day, only the basket was wrong.

## 4. Several columns: Mahalanobis distance
Diagram: [`diagrams/mahalanobis.pdf`](diagrams/mahalanobis.pdf)

Orders and basket size are correlated (r = 0.73): busy weekend days bring families with big baskets. Normal days form a **tilted ellipse**. The Mahalanobis distance measures how many "standard deviations" a point is from the centre *along the shape of that ellipse*:
```python
def mahalanobis(X):
    mu = X.mean(axis=0)
    cov_inv = np.linalg.inv(np.cov(X, rowvar=False))
    d = X - mu
    return np.sqrt(np.einsum("ij,jk,ik->i", d, cov_inv, d))   # sqrt(d' Σ⁻¹ d) for every row
```
```
bot day 2025-08-20: z(orders) +1.45, z(basket) -1.13 -> unremarkable one column at a time
Mahalanobis distance of the bot day: 3.48
Mahalanobis > 3.5   flagged 5  caught 5/6  false alarms 0  precision 1.00  recall 0.83
```
The pricing bug (distance 7.4) is now caught. The bot day (busy like a weekend, basket like a quiet weekday) sits just at the edge: 3.48 – it is *off the diagonal*, which is exactly what Mahalanobis looks for, but the weekly cycle still blurs it.

## 5. Combine and tune the threshold
Diagram: [`diagrams/threshold_tradeoff.pdf`](diagrams/threshold_tradeoff.pdf)

Use both ideas: seasonal residuals for orders **and** Mahalanobis on the (order residual, basket residual) pair.
```
combined detector   flagged 7  caught 6/6  false alarms 1  precision 0.86  recall 1.00
```
Every detector ends with a **threshold**, and the threshold is a business decision:
```
threshold x0.6   flagged 25  caught 6/6  false alarms 19  precision 0.24  recall 1.00
threshold x0.8   flagged 10  caught 6/6  false alarms  4  precision 0.60  recall 1.00
threshold x1.0   flagged  7  caught 6/6  false alarms  1  precision 0.86  recall 1.00
threshold x1.2   flagged  6  caught 6/6  false alarms  0  precision 1.00  recall 1.00
threshold x1.5   flagged  4  caught 4/6  false alarms  0  precision 1.00  recall 0.67
```
- A missed outage costs money; a false alarm costs 10 minutes of someone's time. Choose the threshold from those costs, and from how many alerts per week the team will really read (alert fatigue is real).
- **Careful:** x1.2 looks perfect, but we chose it on the very same 6 incidents we score it on – that is over-fitting (module 19). Tune on one period, check on the next.

## 6. In practice with libraries
```python
from scipy import stats
stats.zscore(x); stats.median_abs_deviation(x, scale="normal")

from statsmodels.tsa.seasonal import STL          # robust trend + seasonal decomposition
res = STL(series, period=7, robust=True).fit().resid

from sklearn.ensemble import IsolationForest       # many columns, no shape assumptions
from sklearn.covariance import EllipticEnvelope   # robust Mahalanobis
iso = IsolationForest(contamination=0.02, random_state=0).fit(X)
flags = iso.predict(X) == -1
```
**Isolation forest** builds random trees (module 20) and measures how *few* splits are needed to isolate a point: anomalies get isolated quickly.

## 7. Anomaly ≠ error
An outlier is a question, not an answer. Black Friday is an anomaly but completely legitimate; deleting it would make next year's forecast wrong. Always: **flag → investigate → decide** (fix data, keep and annotate, or exclude with a written reason – module 04).

## Exercises
1. Add a 7th incident: a slow, gradual drop of 3% per day over two weeks. Which detector catches it? Why is a slow drift hard (hint: the rolling trend follows it)?
2. Replace the 29-day rolling median by a 29-day rolling **mean**. Does the Feb 14 spike leak into its neighbours' residuals?
3. Compute the Mahalanobis distance with a robust centre and covariance (exclude points above distance 3, recompute, repeat twice). Does the bot day cross 3.5?
4. Split the year into Jan–Jun (tune) and Jul–Dec (test). Choose the threshold on the first half and report precision/recall on the second.

## Git notes for this module
Diagram: [`diagrams/git_bisect_run.pdf`](diagrams/git_bisect_run.pdf)

See [git-notes](../git-notes/README.md#finding-the-anomalous-commit-bisect-run-log---grep-and-safe-clean-up): let `git bisect run` find the commit where a check started failing, search messages with `git log --grep`, and tidy branches safely with `git branch --merged`, `git fetch --prune` and `git push --force-with-lease`.
