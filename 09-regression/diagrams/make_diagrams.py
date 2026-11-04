"""Generate PDF diagrams for module 09 (regression)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
df = pd.read_csv(OUT.parents[1] / "data" / "sales_eda.csv")

# 1. Fit line with residuals
x, y = df["quantity"].to_numpy(float), df["revenue"].to_numpy(float)
m, c = np.polyfit(x, y, 1)
fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(x, y, s=18, color="#1e3a8a", alpha=.6, label="orders")
xs = np.array([x.min(), x.max()]); ax.plot(xs, c + m * xs, color="#ef4444", lw=2.5, label=f"fit: y = {c:.1f} + {m:.2f}x")
for xi, yi in list(zip(x, y))[:25]:
    ax.plot([xi, xi], [yi, c + m * xi], color="#94a3b8", lw=.8)
ax.annotate("residual = actual - predicted", (x[3], y[3]), (x.min() + .2, y.max() * .9), arrowprops=dict(arrowstyle="->"))
ax.set_xlabel("quantity"); ax.set_ylabel("revenue"); ax.legend()
ax.set_title("Least squares: the line that minimises squared residuals", weight="bold")
fig.savefig(OUT / "fit_line.pdf", bbox_inches="tight"); plt.close(fig)

# 2. Actual vs predicted, two models
X1 = np.column_stack([np.ones(len(df)), df["quantity"]])
X2 = np.column_stack([np.ones(len(df)), df["quantity"], df["price"]])
fig, axs = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True)
for ax, X, t in zip(axs, (X1, X2), ("quantity only", "quantity + price")):
    b, *_ = np.linalg.lstsq(X, y, rcond=None); p = X @ b
    r2 = 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    ax.scatter(p, y, s=14, color="#15803d", alpha=.6); lim = [0, y.max()]
    ax.plot(lim, lim, "k--", lw=1); ax.set_title(f"{t}\nR$^2$ = {r2:.2f}"); ax.set_xlabel("predicted")
axs[0].set_ylabel("actual")
fig.suptitle("Actual vs predicted: closer to the dashed line is better", weight="bold")
fig.savefig(OUT / "actual_vs_predicted.pdf", bbox_inches="tight"); plt.close(fig)

# 3. Workflow flowchart
fig, ax = plt.subplots(figsize=(11, 3)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3)
steps = ["1. Define\ntarget y", "2. Choose\nfeatures X", "3. Split\ntrain / test", "4. Fit\nmodel", "5. Check\nresiduals", "6. Evaluate\non test set"]
for i, s in enumerate(steps):
    xx = .9 + i * 1.84
    ax.add_patch(FancyBboxPatch((xx - .8, 1.1), 1.6, .9, boxstyle="round,pad=.05", fc="#dbeafe", ec="#334155"))
    ax.text(xx, 1.55, s, ha="center", va="center", fontsize=9)
    if i < len(steps) - 1:
        ax.annotate("", (xx + 1.04, 1.55), (xx + .84, 1.55), arrowprops=dict(arrowstyle="->"))
ax.text(5.5, .5, "If test error >> train error: overfitting. Simplify the model or add data.", ha="center", color="#b91c1c")
ax.set_title("Regression workflow", weight="bold")
fig.savefig(OUT / "workflow.pdf", bbox_inches="tight"); plt.close(fig)
