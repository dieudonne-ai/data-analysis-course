# Module 24 – Market Basket Analysis (bonus)

"Customers who bought pasta also bought tomato sauce." Supermarkets, online shops and streaming services all use this idea to decide **what to place side by side, what to bundle and what to recommend**. The technique is called **market basket analysis** or **association rule mining**, and it works on any data made of *sets*: receipts, shopping carts, playlists, symptoms of a patient – or files changed in a commit (see the Git corner).

This module builds everything from scratch with numpy on 1,000 shop receipts.

Run it: `python 24-market-basket/examples/basket_demo.py` (numpy only; it creates `data/baskets.csv` the first time).
Rebuild the diagrams: `python 24-market-basket/diagrams/make_diagrams.py`.

## 1. From receipts to a 0/1 matrix
Transaction data usually arrives in **long format**, one line per item sold:
```
receipt_id,item
1,bread
1,butter
2,coffee
```
For counting we turn it into a **one-hot basket matrix**: one row per receipt, one column per product, `True` if the product is in the basket.
```python
import pandas as pd
df = pd.read_csv("data/baskets.csv")
X = pd.crosstab(df["receipt_id"], df["item"]).astype(bool)   # receipts x products
```
(The example script does the same with plain numpy.) Our data: 1,000 receipts, 13 products, 3.03 items per basket on average.

## 2. Three numbers for every rule
Diagram: [`diagrams/metrics.pdf`](diagrams/metrics.pdf)

A rule is written **A → B** ("if the basket contains A, it also contains B").

| Metric | Formula | Question it answers |
|---|---|---|
| **support** | P(A and B) | How common is the pair? Is it worth acting on? |
| **confidence** | support(A,B) / support(A) = P(B \| A) | When A is bought, how often is B bought too? |
| **lift** | confidence / support(B) | Is that more often than chance? (> 1 yes, = 1 independent, < 1 they avoid each other) |

```python
def support(X, cols):                     # share of receipts containing ALL these items
    return X[:, list(cols)].all(axis=1).mean()
```
```
2. One rule by hand: bread -> butter
   support(bread)        = 0.455
   support(butter)       = 0.275
   support(bread+butter) = 0.222
   confidence = 0.222 / 0.455 = 0.488
   lift       = 0.488 / 0.275 = 1.77
```
Half the bread buyers also take butter, and that is **1.77 times** more than the 27.5% of all customers who buy butter.

### The popularity trap
```
3. The popularity trap: bread -> milk
   confidence 0.418 looks high, but support(milk) = 0.408 -> lift 1.02
```
42% confidence sounds like a strong rule, but 41% of *all* customers buy milk anyway. Lift ≈ 1 means bread tells us nothing about milk. **Always read confidence next to lift**: confidence alone rewards popular products.

## 3. Apriori: don't count everything
Diagram: [`diagrams/apriori.pdf`](diagrams/apriori.pdf)

With 13 products there are 78 pairs and 286 triples; with 10,000 products there are 50 million pairs. The **Apriori principle** saves us: *if a set is rare, every bigger set that contains it is also rare* (a basket with pasta + diapers + cheese also contains pasta + diapers). So we grow itemsets level by level and never count a candidate that has a rare subset.

```python
def apriori(X, min_support=0.03, max_len=3):
    freq = {}
    level = [(j,) for j in range(X.shape[1]) if X[:, j].mean() >= min_support]
    for s in level:
        freq[s] = support(X, s)
    k = 1
    while level and k < max_len:
        k += 1
        cands = {tuple(sorted(set(a) | set(b))) for a in level for b in level if len(set(a) | set(b)) == k}
        cands = [c for c in cands if all(sub in freq for sub in combinations(c, k - 1))]   # prune
        level = []
        for c in sorted(cands):
            s = support(X, c)
            if s >= min_support:
                freq[c] = s; level.append(c)
    return freq
```
```
4. Apriori (min_support = 0.03): 13 items, 58 pairs (of 78 possible), 35 triples
```
In the diagram, pasta + diapers (PD) is rare (0.010), so the triples PTD and PCD are **pruned without being counted**. On big catalogues this is the difference between seconds and days.

Choosing `min_support` is a business decision: too high and you only rediscover bestsellers; too low and you get thousands of rules based on 3 receipts.

## 4. Generating and ranking rules
Diagrams: [`diagrams/rules_scatter.pdf`](diagrams/rules_scatter.pdf), [`diagrams/lift_heatmap.pdf`](diagrams/lift_heatmap.pdf)

Every frequent itemset gives rules: {pasta, tomato_sauce} gives *pasta → tomato_sauce* and *tomato_sauce → pasta*. Keep those above a minimum confidence, then sort by lift.
```
5. Top one-to-one rules by lift (min_confidence = 0.3)
   rule                         support   conf   lift
   pasta -> tomato_sauce          0.110   0.52   3.55
   tomato_sauce -> pasta          0.110   0.75   3.55
   diapers -> beer                0.033   0.51   2.88
   coffee -> sugar                0.129   0.48   2.50
   sugar -> coffee                0.129   0.66   2.50
   chips -> soda                  0.103   0.66   2.24
   soda -> chips                  0.103   0.35   2.24

   125 rules in total; the best one with 2 items on the left:
   cheese + tomato_sauce -> pasta: support 0.048, conf 0.89, lift 4.21
   compare tomato_sauce -> pasta alone: conf 0.75
```
- **Lift is symmetric** (A → B and B → A have the same lift), **confidence is not**:
```
6. Direction matters
   diapers -> beer     confidence 0.51  lift 2.88
   beer -> diapers  confidence 0.19  lift 2.88
```
  Half of diaper buyers take beer, but only 1 beer buyer in 5 takes diapers. Put the beer promotion near the diapers, not the other way round.
- Longer rules can be sharper (cheese + tomato sauce → pasta: 89%) but cover fewer customers (4.8%). The scatter plot shows this trade-off: the interesting rules are top-left with a bright colour (reliable *and* surprising), not just the ones on the right.
- The **lift heatmap** is the quickest overview for a few dozen products: red cells are "bought together", blue cells (e.g. diapers & coffee, lift 0.6) are "different customers".

## 5. From rules to decisions – and their limits
- **Placement & bundles**: pasta next to tomato sauce, a "movie night" bundle of chips + soda.
- **Recommendations**: "you added coffee – sugar?" (high confidence for the direction you show).
- **Correlation, not causation** (module 08): beer and diapers may both be bought by young parents on Friday evening. Test the action with an **A/B test** (module 12) before rolling it out.
- **Many rules = many false discoveries.** With hundreds of rules, some high-lift ones are chance. Prefer rules with enough support, check them on another month of data (the idea of a train/test split, module 15).
- Libraries: `mlxtend.frequent_patterns.apriori` / `association_rules` (pandas input) and `fpgrowth` (faster, no candidate generation) give the same numbers.

## Git corner: files that change together
Diagram: [`diagrams/git_cochange.pdf`](diagrams/git_cochange.pdf)

A commit is a basket and the files are the items. Files with high co-change lift are *coupled*: when you edit one you will probably have to edit the other (or you forgot to!).
```bash
git log --no-merges --name-only --pretty=format:@ > baskets.txt   # one "receipt" per commit, separated by @
git log --stat -3                         # files and +/- per commit, as a quick visual
git diff --word-diff HEAD~1 -- README.md  # show changed WORDS instead of whole lines (great for prose)
git diff --color-moved HEAD~1             # moved code in a different colour than added/removed code
```
In this course almost every lesson commit also touches `README.md` and `git-notes/README.md` (confidence 1.0, lift ≈ 1.1: they change in nearly *every* commit, so there is little surprise – the popularity trap again). The real signal is `23-anomaly-detection → data` with lift 3.1: modules that generate a CSV always commit it with their lesson. More commands are in the [Git notes](../git-notes/README.md#co-change-analysis-word-diff-and-maintenance).

## Exercises
1. Re-run Apriori with `min_support` 0.01, 0.05 and 0.10. How many itemsets and rules do you get each time? Which rules survive at 0.10?
2. Add a metric **leverage** = support(A,B) − support(A)·support(B). Which rule has the highest leverage, and why is it different from the top lift rule?
3. Split the receipts in two halves (1–500, 501–1000). Do the top 5 rules by lift stay the same in both halves?
4. Build the co-change analysis on a repository you know with Python: which pair of files has the highest lift (with at least 5 commits together)?
