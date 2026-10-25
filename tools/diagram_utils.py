"""Tiny helpers shared by the diagram scripts (boxes and arrows in matplotlib)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def canvas(w, h, title, size=(10, 5)):
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    ax.set_title(title, fontsize=15, weight="bold")
    return fig, ax


def box(ax, x, y, w, h, text, color="#dbeafe", fontsize=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec="#1e3a8a", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#1e3a8a"))
