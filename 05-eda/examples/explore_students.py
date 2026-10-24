from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data" / "students.csv"
df = pd.read_csv(DATA)

print(df.describe().round(1), end="\n\n")
print(df["track"].value_counts(), end="\n\n")
print(df.groupby("track")["score"].agg(["count", "mean", "median"]).round(1), end="\n\n")
print(df.pivot_table(values="score", index="track", columns="gender", aggfunc="mean").round(1), end="\n\n")
print(df[["study_hours", "sleep_hours", "score"]].corr().round(2))
