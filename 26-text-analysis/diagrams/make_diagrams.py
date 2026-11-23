"""Generate PDF diagrams for module 26 (text analysis basics)."""
import subprocess
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT.parent / "examples"))
from text_demo import NEGATIVE, POSITIVE, STOPWORDS, load, raw_words, sentiment, tfidf, tokenize  # noqa: E402

BLUE, RED, GREY, GREEN, ORANGE = "#2563eb", "#dc2626", "#94a3b8", "#059669", "#ea580c"
df = load()
df["tokens"] = df.text.map(tokenize)
df["sentiment"] = df.text.map(lambda t: sentiment(raw_words(t)))


def box(ax, x, y, text, fc, w=2.4, h=1.0, fs=9, ec="#334155", family=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=.05", fc=fc, ec=ec))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, family=family)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1. Text -> numbers pipeline
fig, ax = plt.subplots(figsize=(12.5, 4.2)); ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 4.2)
steps = [('"The grinder is NOT\ngreat, it\'s noisy!"', "#e2e8f0", "raw text"),
         ('"the grinder is not\ngreat its noisy"', "#bfdbfe", "lowercase +\nremove punctuation"),
         ("[the, grinder, is,\nnot, great, its, noisy]", "#bfdbfe", "split into tokens"),
         ("[grinder, not,\ngreat, noisy]", "#fde68a", "remove stopwords\n(keep 'not'!)"),
         ("grinder:1 not:1\ngreat:1 noisy:1", "#bbf7d0", "count = bag of words\n(one row per doc)")]
for i, (t, c, lab) in enumerate(steps):
    x = 1.25 + i * 2.5
    box(ax, x, 2.8, t, c, w=2.2, h=1.1, fs=8.5, family="monospace")
    ax.text(x, 1.95, lab, ha="center", va="top", fontsize=8.5, color="#334155")
    if i:
        ax.annotate("", xy=(x - 1.13, 2.8), xytext=(x - 1.37, 2.8), arrowprops=dict(arrowstyle="->"))
ax.text(0.15, 0.55, 'tokens = re.findall(r"[a-z]+", text.lower());  tokens = [w for w in tokens if w not in STOPWORDS]',
        family="monospace", fontsize=8.5, color="#334155")
ax.text(0.15, 0.15, "Order matters: a model never sees words, only the counts in the last box.",
        fontsize=9, style="italic", color="#334155")
ax.set_title("Turning text into numbers: the tokenization pipeline", loc="left", weight="bold")
fig.savefig(OUT / "text_pipeline.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Word frequencies: with vs without stopwords + Zipf
raw = Counter(w for t in df.text for w in raw_words(t))
cleaned = Counter(w for ts in df.tokens for w in ts)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.5, 4.4))
for ax, cnt, title, col in ((a1, raw, "raw words: stopwords dominate", GREY),
                            (a2, cleaned, "after removing stopwords", BLUE)):
    w, c = zip(*cnt.most_common(12))
    ax.barh(range(len(w))[::-1], c, color=col); ax.set_yticks(range(len(w))[::-1], w, fontsize=8)
    ax.set_title(title, loc="left", weight="bold", fontsize=10); clean(ax); ax.set_xlabel("count")
freqs = np.array(sorted(raw.values(), reverse=True))
a3.loglog(np.arange(1, len(freqs) + 1), freqs, "o", ms=3, color=ORANGE)
a3.set_xlabel("rank of the word (log)"); a3.set_ylabel("count (log)"); clean(a3)
a3.set_title("Zipf's law: a few words are everywhere,\nmost words are rare", loc="left", weight="bold", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "word_frequencies.pdf", bbox_inches="tight"); plt.close(fig)

# 3. TF-IDF heatmap
docs = df.groupby("category").tokens.sum().to_dict()
tf = tfidf(docs)
terms = list(dict.fromkeys(t for c in tf.columns for t in tf[c].sort_values(ascending=False).head(5).index))
terms += ["good", "not", "slow", "great"]
M = tf.loc[terms].values
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 6.4), gridspec_kw=dict(width_ratios=[1.3, 1]))
im = a1.imshow(M, cmap="Blues", aspect="auto")
a1.set_xticks(range(len(tf.columns)), tf.columns, rotation=20, fontsize=8.5)
a1.set_yticks(range(len(terms)), terms, fontsize=8.5)
a1.axhline(len(terms) - 4.5, color=RED, lw=1.5)
a2_note = "below the red line: common words, low TF-IDF everywhere"
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        a1.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center", fontsize=6.5,
                color="white" if M[i, j] > M.max() * .6 else "#334155")
a1.set_title("TF-IDF per category (top-5 terms of each)", loc="left", weight="bold", fontsize=10)
a2.axis("off"); a2.set_xlim(0, 10); a2.set_ylim(0, 10)
box(a2, 5, 8.6, "TF = count of term in doc / words in doc\n\"how much does THIS doc use it?\"", "#bfdbfe", w=9.4, h=1.5, fs=9)
box(a2, 5, 6.4, "IDF = log((1 + N docs) / (1 + docs with term)) + 1\n\"how rare is it across ALL docs?\"", "#fde68a", w=9.4, h=1.5, fs=9)
box(a2, 5, 4.2, "TF-IDF = TF x IDF\nhigh = frequent HERE and rare ELSEWHERE", "#bbf7d0", w=9.4, h=1.5, fs=9)
a2.text(.3, 2.3, "'burr' : only in grinder reviews -> high IDF\n'good' : in all 4 categories -> lowest IDF\n"
        "Below the red line: common words,\nlow TF-IDF in every category.\n"
        "Use it for: keywords, search ranking,\nfeatures for a classifier (module 15)", fontsize=9, va="top")
fig.tight_layout(); fig.savefig(OUT / "tfidf.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Sentiment: negation + score vs stars
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.6), gridspec_kw=dict(width_ratios=[1, 1.15]))
a1.axis("off"); a1.set_xlim(0, 10); a1.set_ylim(0, 6)
words = ["the", "crema", "was", "not", "great", ",", "noisy"]
scores = ["", "", "", "flip!", "+1 -> -1", "", "-1"]
cols = ["#f1f5f9"] * 3 + ["#fde68a", "#fecaca", "#f1f5f9", "#fecaca"]
for i, (w, s, c) in enumerate(zip(words, scores, cols)):
    box(a1, .8 + i * 1.38, 4.3, w, c, w=1.2, h=.8, fs=9)
    a1.text(.8 + i * 1.38, 3.55, s, ha="center", fontsize=8, color=RED if "-" in s else "#334155")
a1.text(.2, 2.4, "naive lexicon:  great(+1) + noisy(-1) = 0   (neutral?!)", family="monospace", fontsize=8.5)
a1.text(.2, 1.7, "with negation:  not great(-1) + noisy(-1) = -2", family="monospace", fontsize=8.5, color=RED)
a1.text(.2, .7, f"Lexicon: {len(POSITIVE)} positive and {len(NEGATIVE)} negative words.\n"
        "Simple, explainable, no training data needed.", fontsize=8.5, style="italic")
a1.set_title("Lexicon sentiment: count good and bad words", loc="left", weight="bold", fontsize=10)
data = [df.sentiment[df.stars == s] for s in range(1, 6)]
bp = a2.boxplot(data, positions=range(1, 6), widths=.5, patch_artist=True)
for patch, c in zip(bp["boxes"], [RED, RED, GREY, GREEN, GREEN]):
    patch.set_facecolor(c); patch.set_alpha(.5)
a2.axhline(0, color="#334155", lw=.8, ls=":")
r = np.corrcoef(df.sentiment, df.stars)[0, 1]
a2.set_xlabel("star rating given by the customer"); a2.set_ylabel("sentiment score from the text")
a2.set_title(f"Text score vs stars: correlation {r:.2f}\n(outliers = text and stars disagree)", loc="left", weight="bold", fontsize=10)
clean(a2)
fig.tight_layout(); fig.savefig(OUT / "sentiment.pdf", bbox_inches="tight"); plt.close(fig)


# 5. Git corner: commit messages are text too
def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout


subjects = [s for s in git("log", "--no-merges", "--format=%s").splitlines() if s]
words = Counter(w for s in subjects for w in raw_words(s) if w not in STOPWORDS and len(w) > 2)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw=dict(width_ratios=[1.15, 1]))
a1.axis("off"); a1.set_xlim(0, 10); a1.set_ylim(0, 6)
msg = ("Add module 26: text analysis basics        <- subject: imperative, < 72 chars\n"
       "                                           <- blank line\n"
       "Tokenize reviews, compare raw counts and   <- body: WHAT and WHY\n"
       "TF-IDF, score sentiment with negation.\n\n"
       "Co-Authored-By: Name <mail@example.com>    <- trailers: key: value")
a1.add_patch(FancyBboxPatch((.1, 2.2), 9.8, 3.4, boxstyle="round,pad=.05", fc="#f8fafc", ec="#334155"))
a1.text(.3, 3.9, msg, ha="left", va="center", fontsize=7.6, family="monospace")
a1.text(.1, 1.4, 'git log --format=%s | tr " " "\\n" | sort | uniq -c | sort -rn | head\n'
        "git log --format='%(trailers:key=Co-Authored-By)'\n"
        "git log --grep='^fix' -i --oneline", family="monospace", fontsize=8, va="top")
a1.set_title("Anatomy of a good commit message", loc="left", weight="bold")
if words:
    w, c = zip(*words.most_common(15))
    a2.barh(range(len(w))[::-1], c, color=BLUE); a2.set_yticks(range(len(w))[::-1], w, fontsize=8)
    a2.set_xlabel("count in commit subjects")
    a2.set_title(f"Word counts in this repo's {len(subjects)} commit subjects", loc="left", weight="bold", fontsize=10)
clean(a2)
fig.tight_layout(); fig.savefig(OUT / "git_commit_messages.pdf", bbox_inches="tight"); plt.close(fig)
print("diagrams written to", OUT)
