"""Module 26 - Text analysis basics: tokens, word counts, TF-IDF and lexicon sentiment.

Creates data/reviews.csv (if missing): 900 fictional customer reviews of a
coffee-machine shop, with a star rating (1-5), a product category and the text.
Everything is done with pandas + numpy so you can see every step.
"""
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "reviews.csv"

STOPWORDS = set("""a an the and or but if so of to in on at for with from by is are was were be been
it its this that these those i me my we our you your they them he she his her very really just
than then there here too also as about after before again all any can could do does did have has had
would will shall should am into out up down over under more most some such only own same one""".split())

POSITIVE = {"great", "love", "excellent", "perfect", "fast", "easy", "delicious", "quiet", "recommend",
            "happy", "good", "amazing", "reliable", "friendly", "best", "smooth", "fresh", "worth"}
NEGATIVE = {"broken", "slow", "noisy", "leaks", "leak", "late", "bad", "terrible", "disappointed",
            "refund", "expensive", "cheap", "stopped", "rude", "worst", "bitter", "damaged", "waste"}
NEGATORS = {"not", "never", "no", "dont", "didnt", "isnt", "wasnt"}

CATEGORIES = {
    "espresso machine": (["pressure", "crema", "espresso", "steam", "milk", "frother", "portafilter"],
                         ["leaks", "noisy", "stopped", "broken"]),
    "grinder":          (["grind", "burr", "beans", "settings", "fine", "coarse", "hopper"],
                         ["noisy", "cheap", "stopped", "slow"]),
    "coffee beans":     (["beans", "roast", "aroma", "flavor", "taste", "acidity", "chocolate"],
                         ["bitter", "stale", "expensive", "bad"]),
    "delivery":         (["delivery", "package", "courier", "box", "tracking", "shipping", "arrived"],
                         ["late", "damaged", "rude", "slow"]),
}
POS_T = ["{p} {n} and the {w} is {p2}.", "I {love} the {w}, {p} {n}!", "the {w} is {p}, would recommend.",
         "{p} {w}, {p2} {n}. happy customer.", "really {p} {w} for the price, worth it."]
NEG_T = ["the {w} {neg} after two weeks, {bad}.", "{bad} {n}, the {w} {neg}. I want a refund.",
         "not good at all: the {w} is {neg2}.", "disappointed, the {w} {neg} and support was slow.",
         "the {w} was not great, {neg2} and {bad}."]
MID_T = ["the {w} is ok but the {n} could be better.", "average {n}, the {w} is fine.",
         "not bad, the {w} works but it is a bit {neg2}."]


def make_data(path=DATA, n=900, seed=26):
    rng = np.random.default_rng(seed)
    pos_adj = ["great", "excellent", "perfect", "amazing", "good", "reliable", "smooth", "fast", "easy"]
    bad_adj = ["terrible", "bad", "worst purchase", "a waste of money"]
    rows = []
    for rid in range(1, n + 1):
        cat = list(CATEGORIES)[rng.integers(0, len(CATEGORIES))]
        words, negs = CATEGORIES[cat]
        stars = int(rng.choice([1, 2, 3, 4, 5], p=[.12, .10, .14, .30, .34]))
        tmpl = POS_T if stars >= 4 else NEG_T if stars <= 2 else MID_T
        if rng.random() < 0.15:                  # real people are inconsistent: text and stars disagree
            tmpl = [POS_T, NEG_T, MID_T][rng.integers(0, 3)]
        parts = []
        for _ in range(rng.integers(1, 3)):
            t = tmpl[rng.integers(0, len(tmpl))]
            parts.append(t.format(p=rng.choice(pos_adj), p2=rng.choice(pos_adj), n=cat,
                                  w=rng.choice(words), love=rng.choice(["love", "really like"]),
                                  neg=rng.choice(negs), neg2=rng.choice(negs), bad=rng.choice(bad_adj)))
        text = " ".join(parts)
        rows.append(dict(review_id=rid, category=cat, stars=stars, text=text[0].upper() + text[1:]))
    pd.DataFrame(rows).to_csv(path, index=False)


def load():
    if not DATA.exists():
        make_data()
    return pd.read_csv(DATA)


def tokenize(text):
    """lowercase -> keep letters only -> split -> drop stopwords."""
    text = text.lower().replace("'", "")
    return [w for w in re.findall(r"[a-z]+", text) if w not in STOPWORDS]


def bigrams(tokens):
    return [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]


def tfidf(docs):
    """docs: dict name -> list of tokens. Returns a DataFrame (terms x docs)."""
    tf = pd.DataFrame({k: Counter(v) for k, v in docs.items()}).fillna(0)
    tf = tf / tf.sum()                                   # term frequency (share of the document)
    df_ = (tf > 0).sum(axis=1)                           # in how many documents does the term appear?
    idf = np.log((1 + len(docs)) / (1 + df_)) + 1        # smoothed idf, like scikit-learn
    return tf.mul(idf, axis=0)


def sentiment(tokens_with_stop):
    """+1 per positive word, -1 per negative word, flipped after a negator ("not good")."""
    score, flip = 0, False
    for w in tokens_with_stop:
        if w in NEGATORS:
            flip = True
            continue
        s = (w in POSITIVE) - (w in NEGATIVE)
        if s:
            score += -s if flip else s
        flip = False
    return score


def raw_words(text):
    return re.findall(r"[a-z]+", text.lower().replace("'", ""))


def main():
    df = load()
    print(f"1. Data: {len(df)} reviews, {df.category.nunique()} categories")
    print(df.head(3).to_string(index=False, max_colwidth=70))

    df["tokens"] = df.text.map(tokenize)
    df["n_words"] = df.text.str.split().str.len()
    ex = df.text.iloc[0]
    print("\n2. Tokenizing one review")
    print("   text  :", ex)
    print("   tokens:", tokenize(ex))
    print(f"   average review length: {df.n_words.mean():.1f} words")

    all_tokens = Counter(t for ts in df.tokens for t in ts)
    print("\n3. Most frequent words (after removing stopwords)")
    for w, c in all_tokens.most_common(10):
        print(f"   {w:<12}{c:>5}")
    bi = Counter(b for ts in df.text.map(raw_words) for b in bigrams(ts))
    content = [(b, c) for b, c in bi.most_common() if not set(b.split()) & (STOPWORDS | NEGATORS)]
    negated = [(b, c) for b, c in bi.most_common() if b.split()[0] in NEGATORS]
    print("   top bigrams      :", ", ".join(f"'{b}' ({c})" for b, c in content[:5]))
    print("   negated bigrams  :", ", ".join(f"'{b}' ({c})" for b, c in negated[:4]))

    docs = df.groupby("category").tokens.sum().to_dict()
    tf = tfidf(docs)
    print("\n4. TF-IDF: the words that make each category special")
    for cat in tf.columns:
        top = tf[cat].sort_values(ascending=False).head(5)
        print(f"   {cat:<17}", ", ".join(top.index))
    raw = pd.DataFrame({k: Counter(v) for k, v in docs.items()}).fillna(0)
    print("   (raw counts would rank:", ", ".join(raw["grinder"].sort_values(ascending=False).head(5).index), "for grinder)")

    df["sentiment"] = df.text.map(lambda t: sentiment(raw_words(t)))
    naive = df.text.map(lambda t: sum((w in POSITIVE) - (w in NEGATIVE) for w in raw_words(t)))
    print("\n5. Lexicon sentiment vs star rating")
    print(df.groupby("stars").sentiment.mean().round(2).to_frame("mean score").T.to_string())
    r = np.corrcoef(df.sentiment, df.stars)[0, 1]
    r0 = np.corrcoef(naive, df.stars)[0, 1]
    print(f"   correlation with stars: {r:.2f} with negation handling, {r0:.2f} without")
    df["predicted"] = np.select([df.sentiment > 0, df.sentiment < 0], ["positive", "negative"], "neutral")
    df["actual"] = np.select([df.stars >= 4, df.stars <= 2], ["positive", "negative"], "neutral")
    print("   confusion table (rows = actual, columns = predicted):")
    print(pd.crosstab(df.actual, df.predicted).to_string())
    print(f"   accuracy: {(df.actual == df.predicted).mean():.0%}")

    neg = df[df.stars <= 2]
    complaints = Counter(t for ts in neg.tokens for t in ts if t in NEGATIVE)
    print("\n6. What do unhappy customers complain about?")
    print(neg.groupby("category").size().rename("1-2 star reviews").to_frame().T.to_string())
    print("   top complaint words:", ", ".join(f"{w} ({c})" for w, c in complaints.most_common(6)))
    return df


if __name__ == "__main__":
    main()
