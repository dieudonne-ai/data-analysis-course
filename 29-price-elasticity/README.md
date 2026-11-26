# Module 29 – Price Elasticity & Demand Analysis (bonus)

"If we lower the price by 10 %, will we sell enough extra units to make up for it?" That is the question behind every promotion, price list and discount code. The number that answers it is the **price elasticity of demand**. In this module you will:

- compute an elasticity by hand and read it (elastic vs inelastic);
- estimate it from sales data with a **log-log regression**;
- avoid the classic trap: prices that are set *because* demand is high (a confounder, module 28);
- measure a **cross-price elasticity** (substitutes and complements);
- turn an elasticity into a **profit-maximising price** – and put a bootstrap interval around it (module 27).

The data is a fictional online coffee shop with three products over 104 weeks: espresso **beans**, coffee **capsules** (a substitute for beans) and paper **filters**. It is simulated, so we know the true elasticities (−2.2, −1.5, −0.6) and can check every method.

Run it: `python 29-price-elasticity/examples/elasticity_demo.py` (numpy + pandas only; it creates `data/weekly_prices.csv` the first time).
Rebuild the diagrams: `python 29-price-elasticity/diagrams/make_diagrams.py`.

## 1. What is elasticity?
Diagram: [`diagrams/elastic_vs_inelastic.pdf`](diagrams/elastic_vs_inelastic.pdf)

**Elasticity e = % change in units sold / % change in price.** An elasticity of −2 means "+1 % on the price → about −2 % units".

| Value | Name | A 10 % price cut... | Typical products |
|-------|------|---------------------|------------------|
| e < −1 | **elastic** | raises units by more than 10 % → **revenue goes up** | products with many alternatives, brands, treats |
| −1 < e < 0 | **inelastic** | raises units by less than 10 % → **revenue goes down** | necessities, cheap add-ons, no alternative |
| e = −1 | unit elastic | revenue unchanged | – |

A first estimate needs only two price points. The **arc** (mid-point) formula divides each change by the average of the two values, so the answer is the same whichever point you start from:
```python
beans = df[df["product"] == "beans"]
normal, promo = beans[beans.promo == 0], beans[beans.promo == 1]
p0, p1 = normal.price.mean(), promo.price.mean()
q0, q1 = normal.units.mean(), promo.units.mean()
arc = ((q1 - q0) / ((q1 + q0) / 2)) / ((p1 - p0) / ((p1 + p0) / 2))
```
```
1. Elasticity in one sentence: % change in units for a 1% change in price
   beans, normal weeks: 11.91 EUR -> 393 units;  promo weeks: 10.63 EUR -> 562 units
   arc elasticity = %dQ / %dP = +35.4% / -11.3% = -3.14
   |e| > 1 elastic (price cut raises revenue), |e| < 1 inelastic (price cut lowers revenue)
```
−3.14 is further from the truth (−2.2) than you might like: promo weeks are not a fair comparison – they fall in different seasons, and a promotion also brings extra visibility (banner, newsletter), not only a lower price. Two-point estimates are a rough first look; use all the weeks and a model.

## 2. Log-log regression: the slope is the elasticity
Diagram: [`diagrams/loglog_fits.pdf`](diagrams/loglog_fits.pdf)

Take the log of both units and price. A straight line in log-log space is a **constant-elasticity** demand curve, and its slope is the elasticity:

  log(units) = a + **e** · log(price) + b · season

```python
def fit(d, with_season=True, cross=None):
    X, names = design(d, with_season=with_season, cross=cross)   # const, log_price, season, ...
    return ols(np.log(d.units), X, names)                         # module 09 least squares
```
```
2. Log-log regression: the slope IS the elasticity
             naive  with_season  ci_low  ci_high  truth
   product                                             
   beans     -0.54        -2.30   -2.62    -1.98   -2.2
   capsules  -0.29        -1.62   -1.86    -1.37   -1.5
   filters    0.68        -0.81   -1.16    -0.46   -0.6
```
- With the season in the model, all three 95 % intervals contain the true value.
- Why logs? Units and prices are on different scales; logs turn "percent changes" into "differences", so the coefficient reads directly as "% per %". They also tame big promo spikes.
- Units of 0 break `log`. With many zeros (slow products) use `log(units + 1)` carefully, aggregate to a coarser level (week → month, product → category) or use a Poisson regression.

## 3. The confounding trap: prices are set when demand is high
Diagram: [`diagrams/confounded_price.pdf`](diagrams/confounded_price.pdf)
```
3. The confounding trap: prices are HIGHER when demand is high
   corr(bean price, season) = +0.73  -> winter = high price AND high demand
   naive beans elasticity -0.54 looks far less price-sensitive than the truth -2.2; for filters it even looks positive (+0.68)
   fix: add the confounder (season) to the model, or use only the promo variation within a season
```
The manager raises prices in winter, when people drink more coffee anyway. Season pushes **both** price and units up, so the naive regression credits part of the winter boost to the high price. For filters the naive line even slopes *upwards* – "higher prices sell more" – which is nonsense.

This is exactly the confounder of module 28 (season → price, season → units). What to do:
- put the drivers of price-setting in the model: season or month dummies, holidays, trend, competitor prices, marketing spend;
- rely on variation that is *not* caused by demand: promotions decided in advance, price changes forced by costs, different prices in different regions;
- best of all, **randomise** the price (an A/B price test, module 12) – then no confounder can sneak in.

An elasticity > 0 for a normal product is almost always a warning sign, not a discovery.

## 4. Cross-price elasticity: substitutes and complements
Diagram: [`diagrams/elasticity_cheatsheet.pdf`](diagrams/elasticity_cheatsheet.pdf)

Demand for beans also depends on the price of **other** products. Add log(price of capsules) to the bean model:
```python
caps_price = wide.loc[beans.week, "capsules"].to_numpy()       # capsule price in the same weeks
cross_fit = fit(beans, with_season=True, cross=caps_price)
```
```
4. Cross-price elasticity: capsules are a substitute for beans
                      coef     se  ci_low  ci_high
   const            10.945  0.551   9.864   12.025
   log_price        -2.241  0.162  -2.559   -1.924
   season            0.276  0.026   0.225    0.327
   log_price_other   0.268  0.144  -0.014    0.551
   cross elasticity +0.27 (truth +0.4): +10% on capsules -> about +2.7% bean units
   > 0 substitutes, < 0 complements (e.g. filters and filter coffee), about 0 unrelated
```
- **Substitutes** (cross e > 0): a capsule price increase pushes some buyers to beans. Discounting one steals from the other (**cannibalisation**).
- **Complements** (cross e < 0): printers and ink, consoles and games. Discounting one sells more of both.
- The interval here is wide and just touches 0: cross effects are usually smaller and harder to measure than own-price effects. Report the uncertainty, not only the point estimate.

## 5. From elasticity to the best price
Diagram: [`diagrams/profit_curve.pdf`](diagrams/profit_curve.pdf)

Revenue is price × units; **profit** is (price − unit cost) × units. With constant elasticity e < −1, calculus gives a simple rule:

  **p\* = cost · e / (1 + e)**  — equivalently, markup over cost = 1 / (1 + 1/e)

```python
def optimal_price(elasticity, cost):
    return cost * elasticity / (1 + elasticity) if elasticity < -1 else np.inf
```
```
5. From elasticity to price: revenue and profit
   beans: elasticity -2.24, unit cost 6.00 EUR, current list price 12.00 EUR
   rule for constant elasticity: p* = cost * e / (1 + e) = 6.00 * -2.24 / -1.24 = 10.83 EUR
   grid search over 7-20 EUR: best profit at 10.80 EUR (2,390 EUR/week vs 2,359 today)
   markup over cost = 1 / (1 + 1/e) = 1.81x  -> the more elastic, the smaller the markup
   filters: e = -0.81 (inelastic) -> the formula says 'raise the price forever'.
   Do not trust it: we only saw prices 2.98-4.55 EUR. Test a moderate increase instead.
```
- **Maximise profit, not revenue.** Revenue keeps rising as the price falls when demand is elastic; profit does not.
- The grid search (try many prices, keep the best) gives the same answer as the formula and works for **any** demand model, including ones with no formula.
- For inelastic products the constant-elasticity model has no optimum: it says "raise prices without limit". In reality demand becomes more elastic at high prices (customers find alternatives). A model is only valid **inside the price range you observed** – never extrapolate far beyond it.

## 6. How sure are we? Bootstrap the optimum
```python
for _ in range(1_000):
    idx = rng.integers(0, len(beans), len(beans))                  # resample weeks with replacement
    e = fit(beans.iloc[idx], cross=caps_price[idx]).loc["log_price", "coef"]
    boot_p.append(optimal_price(e, cost))
```
```
6. How sure are we? Bootstrap the weeks (module 27)
   elasticity 95% interval [-2.54, -1.94]
   optimal price 95% interval [9.89, 12.39] EUR
   The profit curve is flat near the top: a price anywhere in that interval earns almost the same,
   (profit at the interval ends: 2,359 and 2,338 EUR/week vs max 2,390)
   so move towards it step by step and measure with an A/B price test (module 12).
```
- The current price (12.00) is **inside** the interval: the data cannot prove that 10.83 is better. The expected gain (~30 EUR/week, about 1 %) is small compared with the uncertainty.
- Profit curves are flat near the top, so being "roughly right" costs little, and being far off (e.g. 7 EUR or 20 EUR) costs a lot. Good recommendation: "a small cut towards 11 EUR, tested on a random half of customers for 4 weeks".
- (Weeks are not fully independent – seasons, trends – so a **block bootstrap** that resamples runs of consecutive weeks gives more honest intervals.)

## 7. Checklist for a pricing analysis
1. Plot price and units over time. Look for seasons, promos, stock-outs (0 units because nothing was in stock is not low demand!).
2. Estimate a log-log model **with** the drivers of price-setting (season, holidays, trend, promo, competitor prices).
3. Sanity-check signs: own elasticity < 0, cross elasticity of obvious substitutes > 0.
4. Recommend prices **within** the observed range, optimise **profit**, and show the uncertainty.
5. Confirm with a randomised price test before rolling out to everyone.
6. Remember what the data does not show: long-term effects (customers learning to wait for promos), brand perception, competitors' reactions.

## Git corner: diffing data files
Diagram: [`diagrams/git_csv_diff.pdf`](diagrams/git_csv_diff.pdf)

A price list is a CSV file under version control. Git's default diff works line by line, so changing one cell shows the whole row as removed and added. Three tools make data diffs readable:
```bash
echo '*.csv diff=csv' >> .gitattributes          # use a custom "csv" diff driver for CSV files
git config diff.csv.wordRegex '[^,]+'            # with --word-diff, one cell = one word
git diff --word-diff HEAD~1 -- data/price_list.csv   # filters,[-4.00-]{+4.40+},1.50
git config diff.csv.textconv 'column -s, -t'     # show CSVs as aligned tables in diff/log -p
git log -p -- data/price_list.csv                # full price history, readable
git diff --no-textconv HEAD~1 -- data/price_list.csv   # the raw diff when you need it
git diff --no-index old_prices.csv new_prices.csv      # compare any two files, even outside a repo
git diff --exit-code -- data/price_list.csv; echo $?   # 0 = unchanged, 1 = changed (for scripts and CI)
```
- `.gitattributes` is committed, so the whole team gets the same rule; the `git config` part is per machine (add `--global` to set it for all your repositories).
- `column` ships with most Linux and macOS systems; if it is missing, any command that prints the file works as textconv (e.g. a 3-line Python script).
- **textconv only changes what you see**: the stored file, `git apply` patches and merges still use the raw CSV.
- `--no-index` is a handy general "compare two files" tool with word-diff, colour and `--stat`, even when the files are not in git.
- For big tables, compare in pandas instead: `old.merge(new, on="product", suffixes=("_old", "_new"))` and keep the rows where the price changed.

More commands are in the [Git notes](../git-notes/README.md#diffing-data-files-gitattributes-textconv-and---no-index).

## Exercises
1. Fit the naive model (no season) and the seasonal model for capsules on **winter weeks only** (season > 0.5). Is the naive estimate still biased? Why?
2. Replace the `season` curve with 12 month dummies. Do the elasticities change?
3. Set the true cross elasticity in `make_weekly` to −0.3 (complements). Does the regression detect it? How wide is the interval?
4. Raise the unit cost of beans from 6.00 to 8.00 EUR. What is the new optimal price? By how much does it move compared with the cost increase?
5. Implement a block bootstrap (resample blocks of 4 consecutive weeks). Is the interval for the optimal price wider than the simple bootstrap?
6. In a test repository, commit a small price list CSV, change one price, and compare `git diff`, `git diff --word-diff` with the `csv` driver, and the `textconv` view.
