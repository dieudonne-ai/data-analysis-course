from pathlib import Path

import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_messy.csv"

df = pd.read_csv(DATA, na_values=["N/A"])
print("Raw shape:", df.shape)
print("Missing per column:\n", df.isna().sum(), end="\n\n")

# 1. Duplicates
df = df.drop_duplicates()

# 2. Text: trim spaces, unify case
for col in ["customer", "product", "country"]:
    df[col] = df[col].str.strip()
df["customer"] = df["customer"].str.title()
df["product"] = df["product"].str.title()
df["country"] = df["country"].str.upper().replace({"UK": "United Kingdom"}).str.title()

# 3. Dates: parse each known format separately (dayfirst=True would corrupt ISO dates)
iso = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
uk = pd.to_datetime(df["order_date"], format="%d/%m/%Y", errors="coerce")
df["order_date"] = iso.fillna(uk)  # still NaT if neither format matches

# 4. Invalid values: negative quantity is impossible
df.loc[df["quantity"] < 0, "quantity"] = pd.NA

# 5. Missing values: fill numeric with the median per product
for col in ["quantity", "price"]:
    df[col] = df[col].astype("float64")
    df[col] = df[col].fillna(df.groupby("product")[col].transform("median"))

# 6. Outliers: IQR rule on price within each product
def iqr_flag(s):
    q1, q3 = s.quantile([0.25, 0.75])
    fence = 1.5 * (q3 - q1)
    return (s < q1 - fence) | (s > q3 + fence)

df["price_outlier"] = df.groupby("product")["price"].transform(iqr_flag)

print(df)
print("\nClean shape:", df.shape)
df.to_csv(DATA.with_name("sales_clean.csv"), index=False)
