"""Generate PDF diagrams for module 29 (price elasticity & demand analysis)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent / "examples"))
from elasticity_demo import PRODUCTS, SEED, fit, load, optimal_price, profit_curve, season  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
COLORS = {"beans": BLUE, "capsules": ORANGE, "filters": GREEN}
df = load()
wide = df.pivot(index="week", columns="product", values="price")


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def box(ax, x, y, text, fc, w=2.0, h=.8, fs=9, family=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec="#334155"))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, family=family, multialignment="left" if family else "center")


# 1. Elastic vs inelastic demand, and what a price cut does to revenue
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
p = np.linspace(6, 18, 200)
for ax, e, title in [(axes[0], -2.2, "Elastic demand (e = -2.2): beans"), (axes[1], -0.6, "Inelastic demand (e = -0.6): filters")]:
    q = 400 * (p / 12) ** e
    ax.plot(q, p, color=BLUE if e < -1 else GREEN, lw=2.2)
    for price, fc in [(12, "#bfdbfe"), (10.8, "#fde68a")]:
        qq = 400 * (price / 12) ** e
        ax.add_patch(plt.Rectangle((0, 0), qq, price, fc=fc, ec="#334155", alpha=.55))
    q12, q108 = 400 * (12 / 12) ** e, 400 * (10.8 / 12) ** e
    ax.text(q12 * .5, 6.2, f"revenue at 12 EUR\n= {12 * q12:,.0f}", ha="center", fontsize=8.5)
    ax.text(560, 15.5, f"-10% price -> {q108 / q12 - 1:+.0%} units\nrevenue {10.8 * q108:,.0f} "
            f"({10.8 * q108 / (12 * q12) - 1:+.0%})", fontsize=9, va="center",
            bbox=dict(fc="white", ec="#cbd5e1"))
    ax.set_xlim(0, 1000); ax.set_ylim(0, 19)
    ax.set_xlabel("units per week"); ax.set_ylabel("price (EUR)"); clean(ax)
    ax.set_title(title, loc="left", fontsize=10, weight="bold")
fig.suptitle("Elasticity e = % change in units / % change in price.  |e| > 1: a cut raises revenue.  |e| < 1: a cut lowers it.",
             x=.02, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "elastic_vs_inelastic.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Log-log fits per product (season-adjusted)
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
for ax, (name, (_, _, true_e, _)) in zip(axes, PRODUCTS.items()):
    d = df[df["product"] == name]
    c = fit(d).coef
    adj_units = np.log(d.units) - c.season * season(d.week)            # remove the seasonal part
    ax.scatter(np.log(d.price), adj_units, s=14, alpha=.6, color=COLORS[name])
    xs = np.linspace(np.log(d.price).min(), np.log(d.price).max(), 2)
    ax.plot(xs, c.const + c.log_price * xs, color="#334155", lw=2)
    ax.set_title(f"{name}: slope = elasticity = {c.log_price:.2f}\n(truth {true_e})", fontsize=10, loc="left")
    ax.set_xlabel("log(price)"); ax.set_ylabel("log(units), season removed"); clean(ax)
fig.suptitle("log(units) = a + e * log(price) + b * season  ->  a straight line whose slope is the elasticity", x=.02, ha="left", weight="bold")
fig.tight_layout(); fig.savefig(OUT / "loglog_fits.pdf", bbox_inches="tight"); plt.close(fig)

# 3. The confounding trap: season drives both price and demand
fig = plt.figure(figsize=(13.5, 4.8))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.5, 1.2])
a0, a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
a0.axis("off"); a0.set_xlim(-1.8, 1.8); a0.set_ylim(-1.6, 1.6)
box(a0, 0, 1, "season\n(winter)", "#fde68a", w=1.4, h=.7)
box(a0, -1, -.3, "price", "#e2e8f0", w=1.2, h=.6)
box(a0, 1, -.3, "units sold", "#e2e8f0", w=1.2, h=.6)
for a, b, col in [((0, 1), (-1, -.3), "#334155"), ((0, 1), (1, -.3), "#334155"), ((-1, -.3), (1, -.3), RED)]:
    a0.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5, shrinkA=20, shrinkB=20))
a0.text(0, -1.15, "Manager raises prices in winter,\nwhen people buy more anyway.\nSeason is a CONFOUNDER (module 28).",
        ha="center", fontsize=8.5)
a0.set_title("Why the naive slope lies", fontsize=10, weight="bold")
beans = df[df["product"] == "beans"].set_index("week")
a1.plot(beans.index, beans.price, color=BLUE, lw=1.6, label="bean price (EUR)")
a1b = a1.twinx()
a1b.plot(beans.index, beans.units, color=GREY, lw=1.2, label="bean units")
a1.set_xlabel("week"); a1.set_ylabel("price (EUR)", color=BLUE); a1b.set_ylabel("units", color="#475569")
promo = beans[beans.promo == 1]
a1.scatter(promo.index, promo.price, s=18, color=RED, zorder=3, label="promo week (-15%)")
a1.legend(loc="upper center", frameon=False, fontsize=8, ncol=2)
a1.set_title("Price and units peak together each winter; promos dip the price", fontsize=10, loc="left")
b = df[df["product"] == "beans"]
naive, adj = fit(b, with_season=False).coef, fit(b).coef
s = season(b.week)
sc = a2.scatter(np.log(b.price), np.log(b.units), c=s, cmap="coolwarm", s=16)
xs = np.linspace(np.log(b.price).min(), np.log(b.price).max(), 2)
a2.plot(xs, naive.const + naive.log_price * xs, color="#334155", ls="--", lw=2, label=f"naive slope {naive.log_price:.2f}")
for sv, ls in [(-1, ":"), (1, "-")]:
    a2.plot(xs, adj.const + adj.season * sv + adj.log_price * xs, color=RED if sv > 0 else BLUE, lw=1.8, ls=ls,
            label=f"{'winter' if sv > 0 else 'summer'}, slope {adj.log_price:.2f}")
a2.legend(frameon=False, fontsize=8); clean(a2)
fig.colorbar(sc, ax=a2, label="season (-1 summer, +1 winter)")
a2.set_xlabel("log(price)"); a2.set_ylabel("log(units)")
a2.set_title("Within a season, demand clearly falls with price", fontsize=10, loc="left")
fig.tight_layout(); fig.savefig(OUT / "confounded_price.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Profit curve with bootstrap uncertainty
b = df[df["product"] == "beans"].reset_index(drop=True)
caps = wide.loc[b.week, "capsules"].to_numpy()
base, cost = PRODUCTS["beans"][0], PRODUCTS["beans"][1]
q_ref = b[b.promo == 0].units.mean()
e_hat = fit(b, cross=caps).loc["log_price", "coef"]
rng = np.random.default_rng(SEED)
grid = np.linspace(7, 20, 131)
curves, stars = [], []
for _ in range(300):
    idx = rng.integers(0, len(b), len(b))
    e = fit(b.iloc[idx], cross=caps[idx]).loc["log_price", "coef"]
    curves.append(profit_curve(grid, e, cost, base, q_ref)[1]); stars.append(optimal_price(e, cost))
curves = np.array(curves)
rev, prof, _ = profit_curve(grid, e_hat, cost, base, q_ref)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6))
a1.plot(grid, rev, color=GREY, lw=2, label="revenue = price x units")
a1.plot(grid, prof, color=BLUE, lw=2.4, label="profit = (price - cost) x units")
a1.fill_between(grid, np.percentile(curves, 5, axis=0), np.percentile(curves, 95, axis=0), color=BLUE, alpha=.15,
                label="profit, 90% bootstrap band")
p_star = optimal_price(e_hat, cost)
a1.axvline(p_star, color=RED, ls="--"); a1.axvline(base, color="#334155", ls=":")
a1.text(p_star - .15, prof.max() * 1.6, f"p* = {p_star:.2f}", color=RED, ha="right", fontsize=9)
a1.text(base, prof.max() * .6, f" today {base:.2f}", fontsize=9)
a1.axvline(cost, color=GREY, lw=.8); a1.text(cost, 8800, " unit cost", fontsize=8, color="#475569")
a1.set_xlabel("bean price (EUR)"); a1.set_ylabel("EUR per week"); a1.legend(frameon=False, fontsize=8.5); clean(a1)
a1.set_title(f"Beans, e = {e_hat:.2f}: p* = cost x e / (1 + e)", loc="left", fontsize=10, weight="bold")
stars = np.array(stars)
a2.hist(stars, bins=30, color=BLUE, alpha=.75)
lo, hi = np.percentile(stars, [2.5, 97.5])
a2.axvspan(lo, hi, color=RED, alpha=.08)
a2.axvline(p_star, color=RED, ls="--")
a2.set_title(f"Bootstrap of the optimal price: 95% in [{lo:.2f}, {hi:.2f}] EUR", loc="left", fontsize=10)
a2.set_xlabel("optimal price (EUR)"); a2.set_ylabel("bootstrap samples"); clean(a2)
fig.tight_layout(); fig.savefig(OUT / "profit_curve.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Own- and cross-price elasticity cheat sheet
fig, ax = plt.subplots(figsize=(12, 5.2))
ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6)
ax.text(.2, 5.6, "Reading elasticities", fontsize=13, weight="bold")
cells = [
    (2.2, 4.2, "own e < -1\nELASTIC\nbeans -2.2", "#bfdbfe", "price cut -> revenue UP\nsmall markup, promos work"),
    (6.0, 4.2, "-1 < own e < 0\nINELASTIC\nfilters -0.6", "#bbf7d0", "price cut -> revenue DOWN\nroom to raise (test it!)"),
    (9.8, 4.2, "own e > 0 ?\nalmost always\na CONFOUNDER", "#fecaca", "check season, promos,\nreverse causality"),
    (2.2, 1.6, "cross e > 0\nSUBSTITUTES\ncapsules -> beans +0.4", "#fde68a", "raise capsule price ->\nsome buyers switch to beans"),
    (6.0, 1.6, "cross e < 0\nCOMPLEMENTS\ne.g. printer & ink", "#e9d5ff", "discount one ->\nsell more of both"),
    (9.8, 1.6, "cross e ~ 0\nINDEPENDENT", "#e2e8f0", "price each product\non its own"),
]
for x, y, t, fc, note in cells:
    box(ax, x, y, t, fc, w=3.2, h=1.25, fs=9.5)
    ax.text(x, y - 1.05, note, ha="center", va="center", fontsize=8.5, color="#334155")
ax.text(.2, 3.0, "OWN price", fontsize=9, rotation=90, color="#475569")
ax.text(.2, .5, "CROSS price", fontsize=9, rotation=90, color="#475569")
fig.savefig(OUT / "elasticity_cheatsheet.pdf", bbox_inches="tight"); plt.close(fig)

# 6. Git corner: diffing a CSV price list (line diff vs cell diff vs textconv)
fig, ax = plt.subplots(figsize=(13, 5.6))
ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 7)
ax.text(.1, 6.65, "Diffing a data file: three views of the same change (filters 4.00 -> 4.40)", fontsize=12, weight="bold")
panels = [
    (2.2, "git diff (default: whole lines)", "#fee2e2",
     " product,price,cost\n-filters,4.00,1.50\n+filters,4.40,1.50\n beans,12.00,6.00"),
    (6.5, "git diff --word-diff\n--word-diff-regex='[^,]+'", "#fef9c3",
     "product,price,cost\nfilters,[-4.00-]{+4.40+},1.50\nbeans,12.00,6.00"),
    (10.8, "*.csv diff=csv  +  textconv\n(aligned columns)", "#dcfce7",
     " product  price  cost\n-filters  4.00   1.50\n+filters  4.40   1.50\n beans    12.00  6.00"),
]
for x, title, fc, text in panels:
    box(ax, x, 4.2, text, fc, w=3.9, h=2.4, fs=9.5, family="monospace")
    ax.text(x, 6.0, title, ha="center", fontsize=9.5, weight="bold")
ax.text(.2, 1.9, "echo '*.csv diff=csv' >> .gitattributes\n"
        "git config diff.csv.wordRegex '[^,]+'          # cell = word for --word-diff\n"
        "git config diff.csv.textconv 'column -s, -t'   # show CSVs as aligned tables in diffs\n"
        "git diff --no-index old.csv new.csv            # compare two files that are NOT in the repo\n"
        "git diff --exit-code -- data/price_list.csv    # exit 1 if it changed (use in checks)",
        fontsize=9, family="monospace", va="center")
ax.text(.2, .35, "textconv changes only what you SEE: the stored file and merges stay raw CSV.  --no-textconv shows the raw diff.",
        fontsize=9, color="#475569")
fig.savefig(OUT / "git_csv_diff.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
