"""Generate PDF diagrams for module 15 (classification)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent

# 1. Sigmoid + threshold
z = np.linspace(-6, 6, 200)
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(z, 1 / (1 + np.exp(-z)), lw=3, color="#1e3a8a")
ax.axhline(.5, ls="--", color="#dc2626"); ax.text(-5.8, .53, "threshold 0.5", color="#dc2626")
ax.fill_between(z, 0, 1, where=z >= 0, color="#fecaca", alpha=.4); ax.fill_between(z, 0, 1, where=z < 0, color="#dcfce7", alpha=.5)
ax.text(-4, .15, "predict: stay (0)", ha="center"); ax.text(4, .85, "predict: churn (1)", ha="center")
ax.set_xlabel("score z = w0 + w1*x1 + w2*x2"); ax.set_ylabel("probability = 1/(1+e^-z)")
ax.set_title("Logistic regression turns a score into a probability", weight="bold")
fig.savefig(OUT / "sigmoid.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Confusion matrix
fig, ax = plt.subplots(figsize=(6, 4.6)); ax.axis("off"); ax.set_xlim(0, 6); ax.set_ylim(0, 4.6)
cells = [("TP\ncorrect alarm", 2.5, 1.6, "#bbf7d0"), ("FP\nfalse alarm", 4.2, 1.6, "#fecaca"),
         ("FN\nmissed churn", 2.5, 0.2, "#fecaca"), ("TN\ncorrect calm", 4.2, 0.2, "#bbf7d0")]
for t, x, y, c in cells:
    ax.add_patch(FancyBboxPatch((x, y), 1.5, 1.2, boxstyle="round,pad=.03", fc=c, ec="#334155"))
    ax.text(x + .75, y + .6, t, ha="center", va="center", fontsize=11)
ax.text(3.25, 3.2, "PREDICTED", ha="center", weight="bold"); ax.text(3.25, 2.95, "churn              stay", ha="center", fontsize=10, color="#475569")
ax.text(1.5, 2.2, "ACTUAL\nchurn", ha="center", va="center", fontsize=10); ax.text(1.5, .8, "ACTUAL\nstay", ha="center", va="center", fontsize=10)
ax.text(3, 4.2, "Confusion matrix", ha="center", weight="bold", fontsize=13)
ax.text(3, -.1, "precision = TP/(TP+FP)    recall = TP/(TP+FN)", ha="center", fontsize=10, color="#334155")
fig.savefig(OUT / "confusion_matrix.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Threshold trade-off
rng = np.random.default_rng(1)
th = np.linspace(.05, .95, 50)
prec = 0.45 + 0.5 * th ** 1.5; rec = 1 - th ** 1.8
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(th, prec, label="precision", color="#1e3a8a", lw=2.5); ax.plot(th, rec, label="recall", color="#d97706", lw=2.5)
ax.set_xlabel("decision threshold"); ax.set_ylabel("score"); ax.legend(frameon=False)
ax.annotate("lower threshold:\ncatch more churners,\nmore false alarms", (.15, rec[7]), (.28, .3), arrowprops=dict(arrowstyle="->"))
ax.set_title("Precision vs recall: pick the threshold that fits the cost", weight="bold", loc="left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.savefig(OUT / "threshold_tradeoff.pdf", bbox_inches="tight"); plt.close(fig)

# 4. Workflow
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
for i, t in enumerate(["Data", "Train/test\nsplit", "Fit model\n(train only)", "Predict\n(test)", "Evaluate\n(metrics)"]):
    x = .2 + i * 2.1
    ax.add_patch(FancyBboxPatch((x, 1), 1.7, 1, boxstyle="round,pad=.04", fc="#dbeafe" if i < 4 else "#dcfce7", ec="#334155"))
    ax.text(x + .85, 1.5, t, ha="center", va="center")
    if i < 4: ax.annotate("", (x + 2.05, 1.5), (x + 1.75, 1.5), arrowprops=dict(arrowstyle="->"))
ax.text(5.5, .4, "Never evaluate on the data you trained on", ha="center", color="#dc2626")
fig.savefig(OUT / "classification_workflow.pdf", bbox_inches="tight"); plt.close(fig)
