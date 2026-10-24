"""Generate the PDF diagram for module 10 (run from anywhere)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent


def project_workflow():
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.5); ax.axis("off")
    ax.set_title("End-to-end analysis workflow", fontsize=15, weight="bold")
    steps = [("Question", "01"), ("Load", "03"), ("Clean", "04"), ("Explore", "05"),
             ("Visualise", "06"), ("Test", "07-08"), ("Model", "09"), ("Report", "10")]
    for i, (s, m) in enumerate(steps):
        x = 0.15 + i * 1.33
        ax.add_patch(FancyBboxPatch((x, 1.8), 1.15, 1.2, boxstyle="round,pad=0.02",
                                    fc="#dbeafe" if i not in (0, 7) else "#fde68a", ec="#1e3a8a", lw=1.5))
        ax.text(x + 0.575, 2.6, s, ha="center", va="center", weight="bold", fontsize=10)
        ax.text(x + 0.575, 2.1, f"module {m}", ha="center", va="center", fontsize=7)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.33, 2.4), xytext=(x + 1.17, 2.4), arrowprops=dict(arrowstyle="->", lw=1.4))
    ax.annotate("", xy=(0.7, 1.7), xytext=(10.2, 1.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.25", ls="--", color="gray"))
    ax.text(5.5, 0.1, "Iterate: results raise new questions. Commit to Git at every step.",
            ha="center", style="italic")
    fig.savefig(OUT / "project_workflow.pdf", bbox_inches="tight")


if __name__ == "__main__":
    project_workflow()
