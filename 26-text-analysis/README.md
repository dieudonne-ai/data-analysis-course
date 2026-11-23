# Module 26 – Text Analysis Basics (bonus)

Ratings tell you *how much* customers like something; the comments tell you *why*. But nobody can read 10,000 reviews. **Text analysis** turns free text into numbers – word counts, keyword scores, sentiment – so you can use everything you learned in the previous modules (groupby, charts, correlation, classification) on it.

The example uses 900 fictional reviews of an online coffee-machine shop: each has a category (espresso machine, grinder, coffee beans, delivery), a star rating from 1 to 5, and the text.

Run it: `python 26-text-analysis/examples/text_demo.py` (pandas + numpy only; it creates `data/reviews.csv` the first time).
Rebuild the diagrams: `python 26-text-analysis/diagrams/make_diagrams.py`.

## 1. The data
```
review_id,category,stars,text
2,espresso machine,4,"The pressure is fast, would recommend. I really like the crema, ..."
3,grinder,5,"Really great hopper for the price, worth it. smooth grinder and ..."
```
One row per document (a review, an email, a support ticket, a tweet...). The collection of documents is called a **corpus**.

## 2. Tokenization: from text to a list of words
Diagram: [`diagrams/text_pipeline.pdf`](diagrams/text_pipeline.pdf)
```python
import re
STOPWORDS = {"the", "a", "is", "and", "it", ...}           # very common words with little meaning

def tokenize(text):
    text = text.lower().replace("'", "")                    # "It's" -> "its"
    return [w for w in re.findall(r"[a-z]+", text) if w not in STOPWORDS]
```
```
text  : Disappointed, the box slow and support was slow.
tokens: ['disappointed', 'box', 'slow', 'support', 'slow']
```
Four decisions hide in these two lines: **lowercase** ("Great" = "great"), **remove punctuation**, **split** into words (**tokens**), **remove stopwords**. Each one is a choice:
- Never remove **negations** ("not", "never") if you care about sentiment: "not good" ≠ "good".
- Real projects often add **stemming/lemmatization** ("leaks", "leaked", "leaking" → "leak") with libraries like `nltk` or `spaCy`.
- For other languages, use a stopword list for that language (and keep accents: `[a-zà-ÿ]+`).

With pandas you can tokenize a whole column at once: `df["tokens"] = df["text"].map(tokenize)`.

## 3. Counting words (bag of words)
Diagram: [`diagrams/word_frequencies.pdf`](diagrams/word_frequencies.pdf)
```python
from collections import Counter
counts = Counter(t for tokens in df["tokens"] for t in tokens)
counts.most_common(10)
```
```
3. Most frequent words (after removing stopwords)
   beans         263
   not           217
   good          214
   delivery      214
   ...
   top bigrams      : 'price worth' (187), 'coffee beans' (161), 'espresso machine' (158), 'happy customer' (153), ...
   negated bigrams  : 'not good' (79), 'not great' (69), 'not bad' (69)
```
- Without stopword removal, "the" and "is" win by far. Word counts follow **Zipf's law**: a handful of words are everywhere, most words appear once or twice.
- The **bag of words** model forgets word order and keeps only counts. Each document becomes a row, each word a column – a (very wide, mostly zero) table that any model can use.
- **Bigrams** (pairs of consecutive words) keep a bit of order back: "espresso machine" is one idea, and "not good" means the opposite of "good".

## 4. TF-IDF: which words make a document special?
Diagram: [`diagrams/tfidf.pdf`](diagrams/tfidf.pdf)

Raw counts favour words that are common everywhere. For the grinder reviews, raw counts rank `grinder, fine, not, good, slow` – but "good" and "not" appear in every category. **TF-IDF** rewards words that are frequent *in this document* and rare *in the others*:

- **TF** (term frequency) = count of the word in the document / number of words in the document
- **IDF** (inverse document frequency) = log((1 + N) / (1 + number of documents containing the word)) + 1
- **TF-IDF** = TF × IDF

```python
tf = pd.DataFrame({cat: Counter(tokens) for cat, tokens in docs.items()}).fillna(0)
tf = tf / tf.sum()                                  # share of each word in each document
n_docs_with = (tf > 0).sum(axis=1)
idf = np.log((1 + len(docs)) / (1 + n_docs_with)) + 1
tfidf = tf.mul(idf, axis=0)
```
```
4. TF-IDF: the words that make each category special
   coffee beans      beans, coffee, flavor, acidity, roast
   delivery          delivery, box, package, tracking, arrived
   espresso machine  espresso, machine, milk, frother, steam
   grinder           grinder, hopper, grind, coarse, burr
```
Here each category is one "document". TF-IDF is the classic way to find **keywords**, rank **search results**, and build features for a text **classifier** (module 15). In practice: `sklearn.feature_extraction.text.TfidfVectorizer` does all of this (and bigrams with `ngram_range=(1, 2)`).

## 5. Sentiment analysis with a lexicon
Diagram: [`diagrams/sentiment.pdf`](diagrams/sentiment.pdf)

The simplest sentiment model: a list of positive words (+1) and negative words (−1), and add them up. Handle negation by flipping the next word:
```python
def sentiment(words):
    score, flip = 0, False
    for w in words:
        if w in NEGATORS:              # "not", "never", "no", ...
            flip = True
            continue
        s = (w in POSITIVE) - (w in NEGATIVE)
        if s:
            score += -s if flip else s
        flip = False
    return score
```
```
5. Lexicon sentiment vs star rating
stars          1     2    3     4    5
mean score -3.25 -3.18 -0.1  2.71  2.7
   correlation with stars: 0.74 with negation handling, 0.69 without
   confusion table (rows = actual, columns = predicted):
predicted  negative  neutral  positive
negative        192       12        16
neutral          11      104        11
positive         26       30       498
   accuracy: 88%
```
- **Validate** the score against something you trust (here the stars). Never publish a sentiment number you have not checked.
- The errors are informative: some customers give 5 stars and write a complaint, or 1 star with a neutral text. Read a sample of the disagreements – they are often the most interesting reviews.
- Lexicons fail on sarcasm ("great, it broke after a day"), domain words ("bitter" is bad for a coffee, fine for chocolate) and mixed opinions. Next steps: a classifier trained on TF-IDF features with the stars as labels (module 15), or a pre-trained language model.

## 6. Putting it to work: what do unhappy customers complain about?
```
6. What do unhappy customers complain about?
category          coffee beans  delivery  espresso machine  grinder
1-2 star reviews            57        50                58       55
   top complaint words: slow (101), bad (69), disappointed (62), refund (52), worst (47), waste (41)
```
Filter the bad reviews, count the negative words, split by category – plain pandas once the text has become tokens. The same pattern works for support tickets ("which problem is growing this month?") or survey answers.

## 7. Practical checklist
- **Look at raw examples first** (module 05): encoding problems, HTML tags, emojis, several languages?
- **Write down every cleaning choice** (lowercase, stopwords, negations, stemming): they change the results.
- **Count documents, not just words**: "refund" 52 times could be 52 reviews or one very angry one.
- **Privacy**: free text often contains names, emails, phone numbers. Remove them before sharing data.
- **Validate** any automatic score on a hand-labelled sample.

## Git corner: commit messages are text data too
Diagram: [`diagrams/git_commit_messages.pdf`](diagrams/git_commit_messages.pdf)

Your history is a corpus you can analyse – if the messages are good. A good commit message has a short **subject** in the imperative ("Add module 26", not "added stuff"), a blank line, a **body** that explains *what* and *why*, and optional **trailers** (`Key: value` lines at the end).
```bash
git commit -m "Add module 26: text analysis" -m "Tokenize reviews, TF-IDF, lexicon sentiment."
                                            # each -m is a paragraph: subject, then body
git commit --trailer "Reviewed-by: Ana <ana@example.com>"   # add a trailer (git >= 2.32)
git log --format=%s                         # subjects only
git log --format=%B -1                      # full message (subject + body) of the last commit
git log --format='%(trailers:key=Co-Authored-By)'           # read trailers
git log -i --grep='^fix' --oneline          # find commits whose message starts with "fix"
git log --format=%s | tr ' ' '\n' | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn | head
                                            # word counts of your subjects (bag of words in the shell!)
```
Teams often follow **Conventional Commits** (`feat: ...`, `fix: ...`, `docs: ...`): with a fixed first word, `git log --grep` and changelog tools can sort the history automatically. More commands are in the [Git notes](../git-notes/README.md#commit-messages-as-data-format-grep-and-trailers).

## Exercises
1. Add stemming by hand: strip a final `s` from tokens longer than 4 letters. How do the top-10 words change?
2. Compute TF-IDF with **each review** as a document (not each category). Which review has the highest TF-IDF for "refund"?
3. Add "bitter" and "stale" to the lexicon only for coffee beans. Does the accuracy for that category improve?
4. Print 10 reviews where the sentiment score is positive but the rating is 1 or 2. Is the text wrong, or the rating?
5. Run the commit-subject word count on a repository you know. Do the messages follow a convention?
