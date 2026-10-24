"""Generate the PDF diagrams for module 08 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def box(ax, x, y, w, h, text, color="#dbeafe", fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", lw=1.5))


def hypothesis_flow():
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.5); ax.axis("off")
    ax.set_title("Hypothesis testing step by step", fontsize=15, weight="bold")
    box(ax, 0.1, 2.5, 2.0, 1.2, "1. State H0 and H1")
    box(ax, 2.5, 2.5, 2.0, 1.2, "2. Choose α\n(e.g. 0.05)")
    box(ax, 4.9, 2.5, 2.0, 1.2, "3. Compute test\nstatistic & p-value")
    box(ax, 7.3, 2.5, 1.7, 1.2, "4. p < α ?", "#fde68a")
    box(ax, 9.4, 3.3, 1.5, 0.9, "Reject H0", "#bbf7d0")
    box(ax, 9.4, 1.8, 1.5, 0.9, "Fail to\nreject H0", "#fecaca")
    for a, b in [((2.1, 3.1), (2.5, 3.1)), ((4.5, 3.1), (4.9, 3.1)), ((6.9, 3.1), (7.3, 3.1)),
                 ((9.0, 3.4), (9.4, 3.7)), ((9.0, 2.8), (9.4, 2.3))]:
        arrow(ax, a, b)
    ax.text(9.1, 3.9, "yes", fontsize=9); ax.text(9.1, 2.2, "no", fontsize=9)
    ax.text(5.5, 0.8, "Rejecting H0 = evidence of an effect.   Not rejecting = not enough evidence.",
            ha="center", style="italic")
    fig.savefig(OUT / "hypothesis_flow.pdf", bbox_inches="tight")


def choose_test():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("Which test?", fontsize=15, weight="bold")
    box(ax, 3.7, 3.9, 2.6, 0.8, "What are you comparing?", "#fde68a", 12)
    cols = [("2 group\nmeans", "t-test"), ("3+ group\nmeans", "ANOVA"),
            ("2 categorical\nvariables", "Chi-square"), ("2 numeric\nvariables", "Pearson r")]
    for i, (q, t) in enumerate(cols):
        x = 0.3 + i * 2.45
        box(ax, x, 2.2, 2.2, 1.0, q)
        box(ax, x, 0.6, 2.2, 1.0, t, "#bbf7d0")
        arrow(ax, (5.0, 3.9), (x + 1.1, 3.2)); arrow(ax, (x + 1.1, 2.2), (x + 1.1, 1.6))
    fig.savefig(OUT / "choose_test.pdf", bbox_inches="tight")


if __name__ == "__main__":
    hypothesis_flow()
    choose_test()
