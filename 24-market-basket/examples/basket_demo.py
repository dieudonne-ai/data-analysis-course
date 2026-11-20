"""Module 24 - Market basket analysis (association rules) from scratch.

Creates data/baskets.csv (if missing): 1,000 shop receipts, one row per
(receipt_id, item). Then computes support, confidence and lift, runs a
small Apriori to find frequent itemsets, and ranks the rules.
"""
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "baskets.csv"

ITEMS = ["bread", "butter", "milk", "coffee", "sugar", "pasta", "tomato_sauce",
         "cheese", "wine", "chips", "soda", "diapers", "beer"]
BASE = dict(bread=.45, butter=.10, milk=.40, coffee=.25, sugar=.08, pasta=.20, tomato_sauce=.06,
            cheese=.18, wine=.10, chips=.15, soda=.20, diapers=.06, beer=.15)


def make_data(path=DATA, n=1000, seed=24):
    rng = np.random.default_rng(seed)
    rows = ["receipt_id,item"]
    for r in range(1, n + 1):
        b = {i for i in ITEMS if rng.random() < BASE[i]}
        # planted patterns (what a real shop would discover)
        if "bread" in b and rng.random() < .45: b.add("butter")
        if "coffee" in b and rng.random() < .40: b.add("sugar")
        if "pasta" in b and rng.random() < .55: b.add("tomato_sauce")
        if "pasta" in b and rng.random() < .35: b.add("cheese")
        if "wine" in b and rng.random() < .45: b.add("cheese")
        if "chips" in b and rng.random() < .50: b.add("soda")
        if "diapers" in b and rng.random() < .45: b.add("beer")
        if not b:
            b = {rng.choice(ITEMS)}
        rows += [f"{r},{i}" for i in sorted(b)]
    path.write_text("\n".join(rows) + "\n")


def load_baskets():
    """Return (items, X) where X is a receipts x items 0/1 matrix (one-hot)."""
    if not DATA.exists():
        make_data()
    raw = np.genfromtxt(DATA, delimiter=",", names=True, dtype=None, encoding="utf-8")
    items = sorted(set(raw["item"]))
    ids = np.unique(raw["receipt_id"])
    X = np.zeros((len(ids), len(items)), dtype=bool)
    rpos = {r: k for k, r in enumerate(ids)}
    ipos = {it: k for k, it in enumerate(items)}
    for r, it in zip(raw["receipt_id"], raw["item"]):
        X[rpos[r], ipos[it]] = True
    return items, X


def support(X, cols):
    """Share of receipts containing ALL the items in cols."""
    return X[:, list(cols)].all(axis=1).mean()


def apriori(X, min_support=0.03, max_len=3):
    """Frequent itemsets {tuple(col indices): support}. Apriori rule: a set can
    only be frequent if every subset is frequent, so we grow from frequent sets."""
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


def rules(freq, min_conf=0.3):
    """All rules A -> B from frequent itemsets, with confidence and lift."""
    out = []
    for s, sup in freq.items():
        if len(s) < 2:
            continue
        for r in range(1, len(s)):
            for a in combinations(s, r):
                b = tuple(x for x in s if x not in a)
                conf = sup / freq[a]
                lift = conf / freq[b]
                if conf >= min_conf:
                    out.append((a, b, sup, conf, lift))
    return sorted(out, key=lambda t: -t[4])


def name(items, cols):
    return " + ".join(items[c] for c in cols)


def main():
    items, X = load_baskets()
    n = len(X)
    print(f"{n} receipts, {len(items)} products, {X.sum()} lines, "
          f"{X.sum(axis=1).mean():.2f} items per basket on average\n")

    print("1. Item popularity (support of single items)")
    for j in np.argsort(-X.mean(axis=0))[:5]:
        print(f"   {items[j]:<13} {X[:, j].mean():.3f}")

    print("\n2. One rule by hand: bread -> butter")
    b, u = items.index("bread"), items.index("butter")
    s_b, s_u, s_bu = support(X, [b]), support(X, [u]), support(X, [b, u])
    print(f"   support(bread)        = {s_b:.3f}")
    print(f"   support(butter)       = {s_u:.3f}")
    print(f"   support(bread+butter) = {s_bu:.3f}")
    print(f"   confidence = {s_bu:.3f} / {s_b:.3f} = {s_bu / s_b:.3f}")
    print(f"   lift       = {s_bu / s_b:.3f} / {s_u:.3f} = {s_bu / s_b / s_u:.2f}")

    print("\n3. The popularity trap: bread -> milk")
    m = items.index("milk")
    c = support(X, [b, m]) / s_b
    print(f"   confidence {c:.3f} looks high, but support(milk) = {support(X, [m]):.3f} -> lift {c / support(X, [m]):.2f}")

    freq = apriori(X, min_support=0.03)
    by_len = {k: sum(len(s) == k for s in freq) for k in (1, 2, 3)}
    all_pairs = len(items) * (len(items) - 1) // 2
    print(f"\n4. Apriori (min_support = 0.03): {by_len[1]} items, {by_len[2]} pairs "
          f"(of {all_pairs} possible), {by_len[3]} triples")

    all_rules = rules(freq)
    print("\n5. Top one-to-one rules by lift (min_confidence = 0.3)")
    print(f"   {'rule':<28}{'support':>8}{'conf':>7}{'lift':>7}")
    pairs = [r for r in all_rules if len(r[0]) == len(r[1]) == 1]
    for a, bb, sup, conf, lift in pairs[:7]:
        print(f"   {name(items, a) + ' -> ' + name(items, bb):<28}{sup:>8.3f}{conf:>7.2f}{lift:>7.2f}")

    print(f"\n   {len(all_rules)} rules in total; the best one with 2 items on the left:")
    a, bb, sup, conf, lift = next(r for r in all_rules if len(r[0]) == 2)
    print(f"   {name(items, a)} -> {name(items, bb)}: support {sup:.3f}, conf {conf:.2f}, lift {lift:.2f}")
    ts, pa = items.index("tomato_sauce"), items.index("pasta")
    print(f"   compare tomato_sauce -> pasta alone: conf {support(X, [ts, pa]) / support(X, [ts]):.2f}")

    print("\n6. Direction matters")
    for a, bb in [("diapers", "beer"), ("beer", "diapers")]:
        i, j = items.index(a), items.index(bb)
        conf = support(X, [i, j]) / support(X, [i])
        print(f"   {a} -> {bb:<8} confidence {conf:.2f}  lift {conf / support(X, [j]):.2f}")


if __name__ == "__main__":
    main()
