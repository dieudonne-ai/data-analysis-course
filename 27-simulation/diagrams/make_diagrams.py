"""Generate PDF diagrams for module 27 (Monte Carlo simulation and the bootstrap)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from simulation_demo import CAPACITY, DAYS, FIXED_COST, MARGIN, SEED, bootstrap, croissant_profit, load, simulate_month  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
rng = np.random.default_rng(SEED)


def box(ax, x, y, text, fc, w=2.4, h=1.0, fs=9, family=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, family=family)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. The Monte Carlo recipe
fig, ax = plt.subplots(figsize=(12.5, 4.6)); ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 4.6)
inputs = [("visitors / day\nPoisson(420)", 3.9), ("conversion\nBeta(30, 70)", 2.8), ("basket (EUR)\nNormal(7.5, 1)", 1.7)]
for t, y in inputs:
    box(ax, 1.4, y, t, "#bfdbfe", w=2.3, h=.85, fs=8.5)
    ax.annotate("", xy=(3.7, 2.8), xytext=(2.6, y), arrowprops=dict(arrowstyle="->", color="#334155"))
ax.text(1.4, .9, "1. describe each uncertain\n    input as a distribution", ha="center", fontsize=8.5, color="#334155")
box(ax, 4.9, 2.8, "model\nprofit = min(buyers, 140)\n x basket x 55% - 12,000", "#fde68a", w=2.5, h=1.4, fs=8.5)
ax.text(4.9, .9, "2. the same formula you\n    would put in a spreadsheet", ha="center", fontsize=8.5, color="#334155")
ax.annotate("", xy=(6.9, 2.8), xytext=(6.2, 2.8), arrowprops=dict(arrowstyle="->"))
box(ax, 8.0, 2.8, "repeat 100,000 x\n(one row = one\npossible month)", "#e2e8f0", w=2.0, h=1.4, fs=8.5)
ax.text(8.0, .9, "3. draw, compute, store;\n    vectorised with numpy", ha="center", fontsize=8.5, color="#334155")
ax.annotate("", xy=(9.75, 2.8), xytext=(9.05, 2.8), arrowprops=dict(arrowstyle="->"))
ins = fig.add_axes([0.79, 0.37, 0.19, 0.42])
sims = simulate_month(50_000, rng)
ins.hist(sims.profit, bins=60, color=BLUE, alpha=.8); ins.axvline(0, color=RED, lw=1.2)
ins.set_yticks([]); ins.tick_params(labelsize=7); clean(ins); ins.spines["left"].set_visible(False)
ins.set_title("distribution of outcomes", fontsize=8.5)
ax.text(11.25, .9, "4. answer with probabilities:\n    mean, P(loss), 5%-95%", ha="center", fontsize=8.5, color="#334155")
ax.set_title("The Monte Carlo recipe: replace every single guess by a distribution, then simulate", loc="left", weight="bold")
fig.savefig(OUT / "monte_carlo_recipe.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Law of large numbers / convergence
exact = 0.22477
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.4))
for k, col in zip(range(5), [BLUE, ORANGE, GREEN, RED, GREY]):
    hits = ((rng.integers(1, 7, size=(20_000, 10)) == 6).sum(axis=1) >= 3)
    run = hits.cumsum() / np.arange(1, len(hits) + 1)
    a1.plot(np.arange(1, len(hits) + 1), run, color=col, lw=1, alpha=.85)
a1.axhline(exact, color="black", ls="--", lw=1); a1.text(25_000 * .55, exact + .006, f"exact = {exact:.4f}", fontsize=8.5)
a1.set_xscale("log"); a1.set_ylim(0, .5); a1.set_xlabel("number of simulations (log)"); a1.set_ylabel("running estimate")
a1.set_title("P(at least 3 sixes in 10 rolls): 5 independent runs\nall converge to the true value", loc="left", weight="bold", fontsize=10)
clean(a1)
ns = np.array([100, 300, 1_000, 3_000, 10_000, 30_000])
errs = [np.std([((rng.integers(1, 7, size=(n, 10)) == 6).sum(axis=1) >= 3).mean() for _ in range(200)]) for n in ns]
a2.loglog(ns, errs, "o-", color=BLUE, label="observed spread of the estimate")
a2.loglog(ns, np.sqrt(exact * (1 - exact) / ns), "--", color=GREY, label=r"theory: $\sqrt{p(1-p)/n}$")
a2.set_xlabel("number of simulations n (log)"); a2.set_ylabel("standard error (log)"); a2.legend(frameon=False, fontsize=8.5)
a2.set_title("Error shrinks like 1/sqrt(n):\n100x more simulations = 10x more precise", loc="left", weight="bold", fontsize=10)
clean(a2)
fig.tight_layout(); fig.savefig(OUT / "convergence.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Profit distribution + flaw of averages
sims = simulate_month(100_000, rng)
p = sims.profit
single = min(420 * .30, CAPACITY) * DAYS * 7.5 * MARGIN - FIXED_COST
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw=dict(width_ratios=[1.35, 1]))
bins = np.linspace(p.min(), p.max(), 90)
a1.hist(p[p < 0], bins=bins, color=RED, alpha=.8, label=f"loss: {(p < 0).mean():.1%} of months")
a1.hist(p[p >= 0], bins=bins, color=BLUE, alpha=.8, label="profit")
for q, lab in ((p.quantile(.05), "5%"), (p.quantile(.95), "95%")):
    a1.axvline(q, color="#334155", ls=":", lw=1); a1.text(q, a1.get_ylim()[1] * .92, f" {lab}\n {q:,.0f}", fontsize=8)
a1.axvline(p.mean(), color=GREEN, lw=2, label=f"simulated mean {p.mean():,.0f}")
a1.axvline(single, color=ORANGE, lw=2, ls="--", label=f"single 'average' guess {single:,.0f}")
a1.set_xlabel("monthly profit (EUR)"); a1.set_yticks([]); a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.set_title("100,000 simulated months: a range, not a number", loc="left", weight="bold", fontsize=10); clean(a1)
a1.spines["left"].set_visible(False)
x = np.linspace(60, 200, 200)
a2.plot(x, np.minimum(x, CAPACITY), color=BLUE, lw=2, label="buyers served = min(demand, 140)")
a2.plot(x, x, color=GREY, ls=":", lw=1)
d = rng.binomial(rng.poisson(420, 20_000), .30)
tw = a2.twinx(); tw.hist(d, bins=40, color=ORANGE, alpha=.3); tw.set_yticks([]); tw.set_ylim(0, tw.get_ylim()[1] * 2.2)
tw.text(126, tw.get_ylim()[1] * .47, "daily demand", color=ORANGE, ha="center", fontsize=8.5); clean(tw)
a2.set_ylim(55, 205)
a2.annotate("busy days lose sales\nquiet days gain nothing", xy=(165, 140), xytext=(105, 175), fontsize=8.5,
            arrowprops=dict(arrowstyle="->"))
a2.set_xlabel("customers who want to buy (one day)"); a2.set_ylabel("customers served"); a2.legend(frameon=False, fontsize=8.5, loc="lower right")
a2.set_title("Why the average guess is wrong: f(average) != average of f(x)\nwhen the model is not a straight line", loc="left", weight="bold", fontsize=10)
clean(a2)
fig.tight_layout(); fig.savefig(OUT / "profit_distribution.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Newsvendor: choose the stock
demand = rng.poisson(lam=rng.gamma(shape=20, scale=4, size=50_000))
stocks = np.arange(30, 161, 2)
mp = np.array([croissant_profit(s, demand).mean() for s in stocks])
lo = np.array([np.percentile(croissant_profit(s, demand), 10) for s in stocks])
hi = np.array([np.percentile(croissant_profit(s, demand), 90) for s in stocks])
best = stocks[mp.argmax()]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.4))
a1.hist(demand, bins=50, color=GREY); a1.axvline(demand.mean(), color=BLUE, lw=2, label=f"mean demand {demand.mean():.0f}")
a1.axvline(best, color=GREEN, lw=2, ls="--", label=f"best stock {best}")
a1.set_xlabel("croissants wanted on a day"); a1.set_yticks([]); a1.legend(frameon=False, fontsize=8.5); clean(a1)
a1.spines["left"].set_visible(False)
a1.set_title("Simulated daily demand (uncertain average + Poisson noise)", loc="left", weight="bold", fontsize=10)
a2.fill_between(stocks, lo, hi, color=BLUE, alpha=.15, label="10%-90% of days")
a2.plot(stocks, mp, color=BLUE, lw=2, label="mean daily profit")
a2.axvline(best, color=GREEN, ls="--"); a2.axvline(demand.mean(), color=GREY, ls=":")
a2.annotate(f"best = {best}\n(sell at 2.80, cost 0.90:\nrunning out costs more\nthan throwing away)", xy=(best, mp.max()),
            xytext=(best + 18, mp.max() - 70), fontsize=8.5, arrowprops=dict(arrowstyle="->"))
a2.set_xlabel("croissants baked (decision)"); a2.set_ylabel("profit per day (EUR)"); a2.legend(frameon=False, fontsize=8.5, loc="lower right")
a2.set_title("Try every decision on the same simulated days, keep the best", loc="left", weight="bold", fontsize=10)
clean(a2)
fig.tight_layout(); fig.savefig(OUT / "newsvendor.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Bootstrap
orders = load()
v = orders.value.to_numpy()
fig = plt.figure(figsize=(13.5, 4.8))
ax = fig.add_axes([0, 0, .4, 1]); ax.axis("off"); ax.set_xlim(0, 6); ax.set_ylim(0, 6)
sample = np.array([12, 25, 31, 33, 48, 90])
box(ax, 3, 5.2, "original sample (n = 6)\n" + "  ".join(map(str, sample)), "#bfdbfe", w=5.0, h=.9, fs=8.5, family="monospace")
r = np.random.default_rng(3)
for i, y in enumerate((3.75, 2.75, 1.75)):
    s = np.sort(r.choice(sample, 6))
    box(ax, 2.4, y, "  ".join(map(str, s)), "#e2e8f0", w=3.8, h=.7, fs=8.5, family="monospace")
    ax.text(4.55, y, f"median {np.median(s):g}", va="center", fontsize=8.5, color=BLUE)
ax.text(2.4, .95, "... x 10,000  (draw n values WITH replacement:\nsome repeat, some are left out)", ha="center", fontsize=8.5)
ax.text(.2, .2, "Spread of the 10,000 medians = uncertainty of the median", fontsize=9, style="italic")
ax.set_title("  The bootstrap: resample your own data", loc="left", weight="bold", y=.97)
a1 = fig.add_axes([.45, .14, .25, .7]); a2 = fig.add_axes([.75, .14, .23, .7])
a1.hist(v, bins=40, color=GREY); a1.axvline(np.median(v), color=BLUE, lw=2, label=f"median {np.median(v):.1f}")
a1.axvline(v.mean(), color=ORANGE, lw=2, ls="--", label=f"mean {v.mean():.1f}")
a1.set_xlabel("order value (EUR)"); a1.set_yticks([]); a1.legend(frameon=False, fontsize=8); clean(a1); a1.spines["left"].set_visible(False)
a1.set_title(f"{len(v)} orders: skewed, so no\nsimple formula for the median CI", loc="left", weight="bold", fontsize=10)
bm = bootstrap(v, np.median, 10_000, rng)
l, h = np.percentile(bm, [2.5, 97.5])
a2.hist(bm, bins=40, color=BLUE, alpha=.8)
a2.axvspan(l, h, color=GREEN, alpha=.15, label=f"95% CI [{l:.1f}, {h:.1f}]")
a2.set_xlabel("median of a resample (EUR)"); a2.set_yticks([]); a2.legend(frameon=False, fontsize=8); clean(a2); a2.spines["left"].set_visible(False)
a2.set_title("10,000 bootstrap medians:\nkeep the middle 95%", loc="left", weight="bold", fontsize=10)
fig.savefig(OUT / "bootstrap.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Bootstrap vs permutation for a difference
app, web = (orders.loc[orders.channel == c, "value"].to_numpy() for c in ("app", "web"))
diff = bootstrap(web, np.median, 10_000, rng) - bootstrap(app, np.median, 10_000, rng)
obs = np.median(web) - np.median(app)
both = np.concatenate([app, web])
perm = np.array([np.median(s[:len(web)]) - np.median(s[len(web):]) for s in (rng.permutation(both) for _ in range(5_000))])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.3))
l, h = np.percentile(diff, [2.5, 97.5])
a1.hist(diff, bins=50, color=BLUE, alpha=.8); a1.axvspan(l, h, color=GREEN, alpha=.15, label=f"95% CI [{l:.1f}, {h:.1f}]")
a1.axvline(0, color=RED, lw=1.5, label="0 = no difference"); a1.legend(frameon=False, fontsize=8.5)
a1.set_xlabel("median(web) - median(app), EUR"); a1.set_yticks([]); clean(a1); a1.spines["left"].set_visible(False)
a1.set_title("Bootstrap: how big is the gap? (CI contains 0)", loc="left", weight="bold", fontsize=10)
pv = (np.abs(perm) >= abs(obs)).mean()
a2.hist(perm, bins=50, color=GREY); a2.axvline(obs, color=ORANGE, lw=2, label=f"observed gap {obs:.2f}  (p = {pv:.2f})")
a2.axvline(-obs, color=ORANGE, lw=1, ls=":"); a2.legend(frameon=False, fontsize=8.5)
a2.set_xlabel("gap after shuffling the channel labels, EUR"); a2.set_yticks([]); clean(a2); a2.spines["left"].set_visible(False)
a2.set_title("Permutation test: is the gap bigger than chance?", loc="left", weight="bold", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "bootstrap_vs_permutation.pdf", bbox_inches="tight"); plt.close(fig)

# 7. Git corner: reproducible runs
fig, ax = plt.subplots(figsize=(12.5, 4.8)); ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 4.8)
box(ax, 1.5, 3.6, "code\n(commit a1b2c3d)", "#bfdbfe", w=2.3, h=.9)
box(ax, 1.5, 2.3, "data\n(version / date)", "#bfdbfe", w=2.3, h=.9)
box(ax, 1.5, 1.0, "random seed\n(SEED = 27)", "#fde68a", w=2.3, h=.9)
for y in (3.6, 2.3, 1.0):
    ax.annotate("", xy=(4.0, 2.3), xytext=(2.7, y), arrowprops=dict(arrowstyle="->"))
box(ax, 5.0, 2.3, "run the\nsimulation", "#e2e8f0", w=1.9, h=1.0)
ax.annotate("", xy=(6.7, 2.3), xytext=(6.0, 2.3), arrowprops=dict(arrowstyle="->"))
box(ax, 8.0, 2.3, "result\nP(loss) = 12.7%\nseed 27 @ a1b2c3d", "#bbf7d0", w=2.4, h=1.3, fs=8.5)
ax.text(9.5, 4.2, "Before running:", fontsize=9, weight="bold")
ax.text(9.5, 3.95, "git status --porcelain       # empty?\n"
        "git diff --quiet || echo dirty\n"
        "git rev-parse --short HEAD   # stamp\n\n"
        "Keep big outputs out of git:\n"
        "git check-ignore -v out/run.csv\n"
        "git ls-files --others --ignored \\\n   --exclude-standard",
        fontsize=7.8, family="monospace", va="top")
ax.text(.2, .1, "Same code + same data + same seed = the same numbers, on any computer. "
        "If the tree is 'dirty' (uncommitted changes), the stamp cannot point to the code that ran.",
        fontsize=8.8, style="italic", color="#334155")
ax.set_title("Git corner: make every random result reproducible", loc="left", weight="bold")
fig.savefig(OUT / "git_reproducible_runs.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
