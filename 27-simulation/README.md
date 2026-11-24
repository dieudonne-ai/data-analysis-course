# Module 27 – Monte Carlo Simulation & the Bootstrap (bonus)

Most business questions hide uncertain inputs: *How many visitors next month? What share will buy? How precise is this median?* Instead of plugging in one "best guess", you can let the computer **draw thousands of random scenarios** and look at the whole range of outcomes. Two techniques do this:

- **Monte Carlo simulation**: you describe the uncertain inputs with distributions, run the model many times, and read probabilities off the results ("12.7 % chance of a loss").
- **The bootstrap**: you resample *your own data* to see how much a statistic (median, difference, ratio...) would move with a different sample – a confidence interval without any formula.

The examples use a fictional coffee pop-up stand (Part A) and 400 fictional online orders from an app and a website (Part B).

Run it: `python 27-simulation/examples/simulation_demo.py` (numpy + pandas only; it creates `data/order_values.csv` the first time).
Rebuild the diagrams: `python 27-simulation/diagrams/make_diagrams.py`.

## 1. Simulation in one minute: estimate a probability by counting
Diagram: [`diagrams/convergence.pdf`](diagrams/convergence.pdf)

*What is the probability of rolling at least three sixes with 10 dice?* You can use the binomial formula (module 07) – or just roll 100,000 times and count:
```python
rng = np.random.default_rng(27)                 # a seeded generator = reproducible results
rolls = rng.integers(1, 7, size=(n, 10))        # n experiments of 10 dice, all at once
estimate = ((rolls == 6).sum(axis=1) >= 3).mean()
```
```
1. Estimating a probability by simulation: P(at least 3 sixes in 10 dice rolls)
   n =     100  estimate = 0.2400   error = +0.0152
   n =   1,000  estimate = 0.2260   error = +0.0012
   n =  10,000  estimate = 0.2263   error = +0.0015
   n = 100,000  estimate = 0.2259   error = +0.0012
   exact answer      = 0.2248   (error shrinks like 1/sqrt(n))
```
- **Law of large numbers**: the more simulations, the closer the estimate gets to the true value.
- The error shrinks like **1 / √n**: 100 × more simulations give only 10 × more precision. A few times 10,000 is usually enough for business decisions.
- Always use **numpy arrays** (one row per scenario) instead of a Python loop – it is 50–100 × faster.
- Use `np.random.default_rng(seed)`: same seed, same numbers. Without a seed, your report changes every time you run it.

## 2. Monte Carlo for a business plan
Diagrams: [`diagrams/monte_carlo_recipe.pdf`](diagrams/monte_carlo_recipe.pdf), [`diagrams/profit_distribution.pdf`](diagrams/profit_distribution.pdf)

The pop-up stand rents a spot for a month (12,000 EUR fixed costs). Nobody knows exactly how many people will walk by, how many will buy, or how much they will spend. **The recipe**:

1. Describe each uncertain input with a distribution (pick one that matches its shape):

| Input | Distribution | Why |
|-------|--------------|-----|
| visitors per day | `rng.poisson(420)` | counts of independent arrivals |
| conversion rate | `rng.beta(30, 70)` | a share between 0 and 1, around 30 % |
| average basket | `rng.normal(7.5, 1.0)` | a symmetric amount around 7.50 EUR |
| buyers | `rng.binomial(visitors, conversion)` | each visitor buys or not |

2. Write the model – the same formula you would put in a spreadsheet.
3. Run it for 100,000 simulated months.
4. Answer with probabilities.
```python
visitors   = rng.poisson(lam=420, size=(n_sims, 30))                 # 30 days per simulated month
conversion = rng.beta(a=30, b=70, size=(n_sims, 1))                  # one rate per month
buyers     = np.minimum(rng.binomial(visitors, conversion), 140)     # the stand serves max 140/day
basket     = rng.normal(7.5, 1.0, size=(n_sims, 1)).clip(4)
profit     = (buyers * basket).sum(axis=1) * 0.55 - 12_000
(profit < 0).mean()                                                  # probability of a loss
```
```
2. Monte Carlo: profit of the pop-up stand next month (100,000 simulated months)
       buyers  conversion  basket   revenue   profit
mean  3668.85        0.30    7.51  27537.70  3145.74
5%    2855.00        0.23    5.86  19487.89 -1281.66
50%   3747.00        0.30    7.50  27518.61  3135.23
95%   4192.00        0.38    9.16  35648.37  7606.60
   single 'average' guess : 3,593 EUR   (420 visitors x 30% x 7.50 EUR, every day)
   simulated mean profit  : 3,146 EUR   90% interval: [-1,282, 7,607]
   P(loss)                : 12.7%
   P(profit > 5,000 EUR)  : 25.1%
   flaw of averages       : busy days are capped at 140 buyers, quiet days are not,
                            so the single guess is 447 EUR too optimistic
   correlation with profit: conversion 0.63, basket 0.75  -> basket drives the risk most
```
- The single "average" plan says **+3,593 EUR**. The simulation says: on average +3,146, but **one month in eight is a loss**, and 90 % of months land between −1,282 and +7,607. That is the information a decision-maker needs.
- **Flaw of averages**: because of the capacity limit, busy days lose sales but quiet days gain nothing. When the model is not a straight line, *the result of the average input is not the average result*. Simulation handles this automatically.
- **Sensitivity**: the correlation between each input and the profit shows which uncertainty matters most. That tells you where better information (a market study, a pilot week) is worth paying for.
- Garbage in, garbage out: the distributions are assumptions. Base them on past data where you can, and say clearly which ones are guesses.

## 3. Choosing a decision by simulation (the "newsvendor" problem)
Diagram: [`diagrams/newsvendor.pdf`](diagrams/newsvendor.pdf)

Each morning the stand bakes croissants (cost 0.90 EUR, price 2.80 EUR). Leftovers are thrown away. How many should it bake? Simulate many possible days once, then **try every decision on the same simulated days**:
```python
demand = rng.poisson(lam=rng.gamma(shape=20, scale=4, size=50_000))   # ~80/day, but the average itself is uncertain
def croissant_profit(stock, demand, price=2.8, cost=0.9):
    return np.minimum(stock, demand) * price - stock * cost
results = {s: croissant_profit(s, demand).mean() for s in range(40, 141, 10)}
```
```
3. A decision under uncertainty: how many croissants to bake each morning?
 stock  mean_profit  P(sold out)  mean_wasted
    40        75.87         0.99         0.05
    50        94.09         0.95         0.32
    60       110.33         0.85         1.31
    70       122.62         0.68         3.71
    80       129.57         0.48         8.01
    90       131.00         0.29        14.28
   100       128.06         0.16        22.12
   110       122.21         0.08        31.00
   120       114.67         0.03        40.48
   130       106.28         0.01        50.26
   140        97.53         0.01        60.17
   best stock = 90 (mean demand is 80): baking for the average is not optimal,
   because a missed sale costs 1.9 EUR and a wasted croissant only 0.9 EUR
```
Baking for the average day (80) is **not** optimal: a missed sale loses 1.90 EUR of margin, a wasted croissant only 0.90 EUR, so it pays to bake a bit more. (Theory agrees: the best stock is the demand quantile at (price − cost) / price = 68 %.) The same pattern works for inventory, staffing ("how many people at the call centre on Monday?") or overbooking.

## 4. The bootstrap: a confidence interval for (almost) anything
Diagram: [`diagrams/bootstrap.pdf`](diagrams/bootstrap.pdf)

Module 07 gave you a formula for the confidence interval of a **mean**. But what about a **median**, a percentile, a ratio, a correlation? The bootstrap idea: *your sample is the best picture you have of the population, so draw new samples from it.*
```python
def bootstrap(values, stat, n_boot, rng):
    idx = rng.integers(0, len(values), size=(n_boot, len(values)))  # n values WITH replacement, n_boot times
    return stat(values[idx], axis=1)

boot = bootstrap(orders.value.to_numpy(), np.median, 10_000, rng)
low, high = np.percentile(boot, [2.5, 97.5])                        # percentile 95 % interval
```
```
4. The bootstrap: a confidence interval for the MEDIAN order value
   400 orders, mean = 36.06, median = 31.31 EUR (skewed: mean > median)
   bootstrap 95% CI for the median: [28.96, 33.94]  (percentile method, 10,000 resamples)
   check on the mean: bootstrap SE = 1.08, formula s/sqrt(n) = 1.08  -> they agree
```
- Each resample has the same size as the original, drawn **with replacement**: some orders appear twice, others not at all.
- For the mean, the bootstrap agrees with the formula s/√n – a good sanity check. For the median it is the easy way.
- Limits: the bootstrap cannot invent information. With a tiny sample (n < 20), or for extremes like the maximum, the interval is unreliable. Rows must be independent (for time series, resample whole blocks or customers).

## 5. Comparing two groups: bootstrap CI and permutation test
Diagram: [`diagrams/bootstrap_vs_permutation.pdf`](diagrams/bootstrap_vs_permutation.pdf)
```python
diff = bootstrap(web, np.median, 10_000, rng) - bootstrap(app, np.median, 10_000, rng)
np.percentile(diff, [2.5, 97.5])                     # how big is the gap, with uncertainty

for i in range(10_000):                              # permutation test: shuffle the labels
    shuffled = rng.permutation(np.concatenate([app, web]))
    perm[i] = np.median(shuffled[:len(web)]) - np.median(shuffled[len(web):])
p_value = (np.abs(perm) >= abs(observed)).mean()
```
```
5. Bootstrap a difference: web vs app median order value
   app n = 191, median 31.05  |  web n = 209, median 32.76
   difference (web - app) = 1.71 EUR, 95% CI [-3.81, 5.48]
   share of resamples where web <= app: 31.0%  -> CI includes 0: not conclusive

6. Permutation test: same question, 'what if the channel label did not matter?'
   observed gap 1.71; p-value = share of shuffles with a gap at least as big = 0.6024
```
- The **bootstrap** answers "how big is the difference, and how sure are we?" Here the interval includes 0.
- The **permutation test** answers "could this gap appear by chance if the channel did not matter?" Here p = 0.60: very likely by chance. Both agree: **no evidence** that web orders are bigger. Report it that way – not as "web is 1.71 EUR higher".
- These are the simulation versions of the t-test and A/B tests of modules 08 and 12, and they work for any statistic.

## 6. Practical checklist
- **Seed** every random generator and write the seed next to the result.
- **Start small** (1,000 runs) while you build the model, then scale up. Check that the result is stable: run twice with different seeds.
- **Validate the model**: simulate a past month and compare with what really happened.
- **Report a range** (5 %–95 %) and probabilities, not only the mean.
- **Name your assumptions**: every distribution is a choice that someone can challenge.

## Git corner: reproducible runs
Diagram: [`diagrams/git_reproducible_runs.pdf`](diagrams/git_reproducible_runs.pdf)

A random result is reproducible only if you know **the code, the data and the seed**. Git gives you the first one – if you check it before running:
```bash
git status --porcelain                    # empty output = clean working tree (easy to test in scripts)
git diff --quiet || echo "uncommitted changes!"   # exit code 1 when tracked files changed
git rev-parse --short HEAD                # the commit to write next to the result: 229f926
git describe --always --dirty             # same, with a "-dirty" suffix when not committed
git check-ignore -v results/run_042.csv   # which .gitignore rule ignores this output file?
git ls-files --others --ignored --exclude-standard   # list every ignored file (outputs, caches)
git update-index --skip-worktree config/local.yaml   # keep a tracked file's LOCAL edits out of commits
git update-index --no-skip-worktree config/local.yaml    # ...and undo it
```
The example does it in Python: `git_stamp()` prints `229f926` or `229f926-dirty`. A good habit: **commit first, then run**, and save outputs with the seed and commit in the file name (`profit_seed27_229f926.csv`). Keep big simulation outputs out of the repository with `.gitignore` (they can always be regenerated from the code + seed). More commands are in the [Git notes](../git-notes/README.md#reproducible-runs-status---porcelain-check-ignore-and-skip-worktree).

## Exercises
1. Change the conversion prior to `beta(15, 35)` (same average, more uncertainty). What happens to P(loss)? And to the mean?
2. The owner can pay 1,500 EUR for a second barista, which raises capacity to 200 per day. Simulate both options: is it worth it?
3. Croissants not sold can be sold the next day at 1.00 EUR instead of being thrown away. How does the best stock change?
4. Bootstrap a 95 % CI for the **90th percentile** of order values (`lambda x, axis: np.percentile(x, 90, axis=axis)`).
5. Add `if git_stamp().endswith("-dirty"): raise SystemExit("commit first!")` to the example. Edit the file without committing and run it.
