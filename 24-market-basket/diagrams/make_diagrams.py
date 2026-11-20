"""Generate PDF diagrams for module 24 (market basket analysis)."""
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT.parent / "examples"))
from basket_demo import apriori, load_baskets, rules, support  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
items, X = load_baskets()


def box(ax, x, y, text, fc, w=2.4, h=1.0, fs=9, ec="#334155"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec=ec))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. The three metrics, illustrated with bread -> butter
b, u = items.index("bread"), items.index("butter")
sb, su, sbu = support(X, [b]), support(X, [u]), support(X, [b, u])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw=dict(width_ratios=[1, 1.15]))
a1.set_xlim(0, 10); a1.set_ylim(0, 7); a1.axis("off"); a1.set_aspect("equal")
a1.add_patch(FancyBboxPatch((0.2, 0.3), 9.6, 6.2, boxstyle="round,pad=.05", fc="#f8fafc", ec=GREY))
a1.text(0.5, 6.1, f"all {len(X)} receipts", fontsize=9, color="#475569")
a1.add_patch(Circle((4.0, 3.4), 2.3, fc=BLUE, alpha=.25, ec=BLUE))
a1.add_patch(Circle((6.2, 3.4), 1.8, fc=ORANGE, alpha=.25, ec=ORANGE))
a1.text(2.9, 3.4, f"bread\n{sb:.3f}", ha="center", va="center", color=BLUE, weight="bold")
a1.text(7.2, 3.4, f"butter\n{su:.3f}", ha="center", va="center", color=ORANGE, weight="bold")
a1.text(5.15, 3.4, f"both\n{sbu:.3f}", ha="center", va="center", fontsize=9, weight="bold")
a1.set_title("Supports of the rule bread -> butter", loc="left", weight="bold")
a2.axis("off"); a2.set_xlim(0, 10); a2.set_ylim(0, 7)
rows = [("support", "P(A and B)", f"{sbu:.3f}", "how common is the pair?\n(is it worth acting on?)", "#e2e8f0"),
        ("confidence", "P(B | A) = supp(A,B) / supp(A)", f"{sbu:.3f} / {sb:.3f} = {sbu / sb:.2f}",
         "of baskets with bread,\nhow many have butter?", "#bfdbfe"),
        ("lift", "confidence / supp(B)", f"{sbu / sb:.2f} / {su:.3f} = {sbu / sb / su:.2f}",
         "> 1 together more than by chance\n= 1 independent   < 1 avoid each other", "#bbf7d0")]
for i, (t, f, v, why, c) in enumerate(rows):
    y = 5.8 - i * 2.2
    box(a2, 1.3, y, t, c, w=2.2, h=1.5, fs=10)
    a2.text(2.7, y + .35, f, fontsize=9, family="monospace")
    a2.text(2.7, y - .05, v, fontsize=9, weight="bold")
    a2.text(2.7, y - .65, why, fontsize=8, color="#475569", va="center")
a2.set_title("Three numbers per rule", loc="left", weight="bold")
fig.savefig(OUT / "metrics.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Apriori lattice and pruning on 4 items
sel = ["pasta", "tomato_sauce", "cheese", "diapers"]
idx = [items.index(s) for s in sel]
short = dict(pasta="P", tomato_sauce="T", cheese="C", diapers="D")
MS = 0.03
fig, ax = plt.subplots(figsize=(12, 5.2)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(-0.9, 5.6)
pos, status = {}, {}
for k in range(1, 5):
    combos = list(combinations(range(4), k))
    for n_, c in enumerate(combos):
        x = 6 + (n_ - (len(combos) - 1) / 2) * (1.8 if k < 3 else 2.6)
        y = 5 - (k - 1) * 1.45
        pos[c] = (x, y)
        parents_ok = all(status.get(sub) == "freq" for sub in combinations(c, k - 1)) if k > 1 else True
        if not parents_ok:
            status[c] = "pruned"
        else:
            status[c] = "freq" if support(X, [idx[i] for i in c]) >= MS else "rare"
for c, (x, y) in pos.items():
    for sub in combinations(c, len(c) - 1) if len(c) > 1 else []:
        ax.plot([x, pos[sub][0]], [y + .28, pos[sub][1] - .28], color="#cbd5e1", lw=.8, zorder=0)
colors = dict(freq="#bbf7d0", rare="#fecaca", pruned="#f1f5f9")
for c, (x, y) in pos.items():
    label = "".join(short[sel[i]] for i in c)
    if status[c] == "pruned":
        txt = f"{label}\nnot counted"
    else:
        txt = f"{label}\n{support(X, [idx[i] for i in c]):.3f}"
    box(ax, x, y, txt, colors[status[c]], w=1.25, h=.62, fs=8,
        ec=GREY if status[c] == "pruned" else "#334155")
ax.text(0.1, 5.4, "P = pasta, T = tomato_sauce, C = cheese, D = diapers   |   min_support = 0.03",
        fontsize=9, color="#475569")
for i, (t, c) in enumerate([("frequent (kept)", "#bbf7d0"), ("counted, too rare", "#fecaca"),
                            ("pruned: a subset is rare,\nso it cannot be frequent", "#f1f5f9")]):
    box(ax, 2.0 + i * 4.0, -0.45, t, c, w=2.6, h=.7, fs=8)
ax.set_title("Apriori: grow itemsets level by level, skip any set with a rare subset", loc="left", weight="bold")
fig.savefig(OUT / "apriori.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Lift heatmap for all item pairs
p = X.mean(axis=0)
co = (X.T.astype(float) @ X) / len(X)
lift = co / np.outer(p, p)
np.fill_diagonal(lift, np.nan)
order = np.argsort(-p)
L = lift[np.ix_(order, order)]
fig, ax = plt.subplots(figsize=(8.5, 7))
im = ax.imshow(np.log2(L), cmap="RdBu_r", vmin=-2, vmax=2)
names = [items[i] for i in order]
ax.set_xticks(range(len(names)), names, rotation=60, ha="right"); ax.set_yticks(range(len(names)), names)
for i in range(len(names)):
    for j in range(len(names)):
        if i != j and (L[i, j] > 1.6 or L[i, j] < .7):
            ax.text(j, i, f"{L[i, j]:.1f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(np.log2(L[i, j])) > 1.2 else "black")
cb = fig.colorbar(im, ax=ax, shrink=.8, ticks=[-2, -1, 0, 1, 2])
cb.ax.set_yticklabels(["0.25", "0.5", "1 (independent)", "2", "4"]); cb.set_label("lift (log scale)")
ax.set_title("Lift for every pair of products (sorted by popularity)", loc="left", weight="bold")
fig.savefig(OUT / "lift_heatmap.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Rules: support vs confidence, size/colour = lift
freq = apriori(X, 0.03)
R = rules(freq, min_conf=0.0)
fig, ax = plt.subplots(figsize=(10, 5.5))
s_ = np.array([r[2] for r in R]); c_ = np.array([r[3] for r in R]); l_ = np.array([r[4] for r in R])
sc = ax.scatter(s_, c_, c=l_, s=20 + 25 * l_, cmap="viridis", alpha=.8, ec="white", lw=.4)
fig.colorbar(sc, ax=ax, label="lift")
ax.axhline(.3, color=GREY, ls="--"); ax.text(.205, .31, "min_confidence 0.3", color="#475569", fontsize=8)
def lab(a, b_):
    return " + ".join(items[i] for i in a) + " -> " + " + ".join(items[i] for i in b_)
for a, b_, s, c, l in R:
    tag = lab(a, b_)
    if tag in {"tomato_sauce -> pasta", "diapers -> beer", "coffee -> sugar", "chips -> soda",
               "bread -> milk", "cheese + tomato_sauce -> pasta", "bread -> butter"}:
        ax.annotate(f"{tag} (lift {l:.1f})", (s, c), xytext=(6, 4), textcoords="offset points", fontsize=8)
ax.set_xlabel("support (how often)"); ax.set_ylabel("confidence (how reliable)"); clean(ax)
ax.set_title(f"All {len(R)} rules from Apriori (min_support 0.03): look for high lift, not just high confidence",
             loc="left", weight="bold", fontsize=10)
fig.savefig(OUT / "rules_scatter.pdf", bbox_inches="tight"); plt.close(fig)

# 5. Git: folders that change together (market basket on commit history)
log = subprocess.run(["git", "-C", str(ROOT), "log", "--no-merges", "--name-only", "--pretty=format:@"],
                     capture_output=True, text=True).stdout
baskets = []
for block in log.split("@"):
    tops = {f.split("/")[0] if "/" in f else "(root)" for f in block.split() if f}
    if tops:
        baskets.append(tops)
cnt = Counter(t for bk in baskets for t in bk)
pair = Counter(pr for bk in baskets for pr in combinations(sorted(bk), 2))
top_pairs = pair.most_common(6)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw=dict(width_ratios=[1, 1.2]))
a1.axis("off"); a1.set_xlim(0, 10); a1.set_ylim(0, 5)
cmds = [("git log --name-only --pretty=format:@", "one 'receipt' per commit"),
        ("awk / Python: split on @", "receipt = set of folders touched"),
        ("count pairs", "support, confidence, lift")]
for i, (cmd, why) in enumerate(cmds):
    y = 4.2 - i * 1.5
    box(a1, 5, y, f"{cmd}\n{why}", ["#e2e8f0", "#bfdbfe", "#bbf7d0"][i], w=9, h=1.0, fs=9)
    if i:
        a1.annotate("", xy=(5, y + .52), xytext=(5, y + .98), arrowprops=dict(arrowstyle="->"))
a1.set_title("Commits are baskets, files are items", loc="left", weight="bold")
n = len(baskets)
labels, conf_vals, lifts = [], [], []
for (x_, y_), k in top_pairs:
    a, b_ = (x_, y_) if cnt[x_] >= cnt[y_] else (y_, x_)
    labels.append(f"{b_} -> {a}"); conf_vals.append(k / cnt[b_]); lifts.append(k * n / (cnt[a] * cnt[b_]))
yy = np.arange(len(labels))[::-1]
a2.barh(yy, conf_vals, color=BLUE)
for y_, c, l in zip(yy, conf_vals, lifts):
    a2.text(c + .01, y_, f"conf {c:.2f}  lift {l:.1f}", va="center", fontsize=8)
a2.set_yticks(yy, labels, fontsize=8); a2.set_xlim(0, 1.35); a2.set_xlabel("confidence"); clean(a2)
a2.set_title(f"Most frequent co-changes in this repo ({n} commits)", loc="left", weight="bold")
fig.savefig(OUT / "git_cochange.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
