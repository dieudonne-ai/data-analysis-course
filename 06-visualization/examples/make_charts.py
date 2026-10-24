from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "data" / "students.csv")

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(df["score"], bins=15, color="#3b82f6", edgecolor="white")
ax.set(xlabel="Score", ylabel="Students", title="Most students score 60-80")
fig.savefig(OUT / "hist.png", dpi=150, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(6, 4))
means = df.groupby("track")["score"].mean()
ax.bar(means.index, means.values, color="#10b981")
ax.set(ylabel="Mean score", title="Mean score by track")
fig.savefig(OUT / "bar.png", dpi=150, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(6, 4))
tracks = sorted(df["track"].unique())
ax.boxplot([df.loc[df["track"] == t, "score"] for t in tracks], tick_labels=tracks)
ax.set(ylabel="Score", title="Score spread by track")
fig.savefig(OUT / "box.png", dpi=150, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(df["study_hours"], df["score"], alpha=0.6)
m, b = np.polyfit(df["study_hours"], df["score"], 1)
xs = np.sort(df["study_hours"])
ax.plot(xs, m * xs + b, color="red")
ax.set(xlabel="Study hours / week", ylabel="Score", title="More study, higher score")
fig.savefig(OUT / "scatter.png", dpi=150, bbox_inches="tight")
print("Saved 4 charts to", OUT)
