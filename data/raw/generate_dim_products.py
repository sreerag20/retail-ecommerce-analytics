"""
Script 3/5 — dim_products
Generates 200 rows.
Injects: nulls, mixed boolean for is_active, mixed date formats,
         mixed currency for unit_price/unit_cost, near-duplicates,
         inactive products that will still appear in recent fact_orders (Part 3d).
"""

import os, random
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()
random.seed(42)
np.random.seed(42)
Faker.seed(42)

os.makedirs("data/raw", exist_ok=True)

N = 200

CATEGORIES = {
    "Electronics":   ["Laptops", "Tablets", "Smartphones", "Accessories", "Wearables"],
    "Apparel":       ["Men's Clothing", "Women's Clothing", "Footwear", "Sportswear"],
    "Home & Garden": ["Furniture", "Kitchen", "Decor", "Outdoor"],
    "Sports":        ["Fitness", "Team Sports", "Outdoor Recreation"],
    "Office":        ["Stationery", "Furniture", "Supplies"],
    "Beauty":        ["Skincare", "Haircare", "Fragrance"],
}

# ── Helper: mixed date ────────────────────────────────────────────────────────
def mixed_date(dt, style):
    ts = pd.Timestamp(dt)
    if style == 0:
        return ts.strftime("%m/%d/%Y")
    elif style == 1:
        return ts.strftime("%Y-%m-%d")
    else:
        return ts.strftime("%d-%b-%Y")

# ── Helper: mixed boolean ─────────────────────────────────────────────────────
def mixed_bool(val):
    style = random.randint(0, 2)
    if style == 0:
        return "True" if val else "False"
    elif style == 1:
        return "YES" if val else "NO"
    else:
        return 1 if val else 0

# ── Helper: mixed currency ────────────────────────────────────────────────────
def mixed_currency(val, style):
    if style == 0:
        return f"${val:,.2f}"
    elif style == 1:
        return str(int(val))
    else:
        return f"{val:,.3f}"

# ── Base records ──────────────────────────────────────────────────────────────
records = []
for i in range(1, N + 1):
    cat      = random.choice(list(CATEGORIES.keys()))
    subcat   = random.choice(CATEGORIES[cat])
    u_price  = round(random.uniform(5, 1200), 2)
    u_cost   = round(u_price * random.uniform(0.35, 0.75), 2)
    is_act   = random.choices([True, False], [0.85, 0.15])[0]
    launch   = fake.date_between(start_date="-8y", end_date="today")
    d_style  = random.randint(0, 2)
    p_style  = random.randint(0, 2)
    c_style  = random.randint(0, 2)
    name     = f"{fake.word().capitalize()} {subcat.split()[0]} {random.choice(['Pro','Plus','Lite','Elite','X','']).strip()}"

    records.append({
        "product_id":   f"PROD-{str(i).zfill(3)}",
        "product_name": name.strip(),
        "category":     cat,
        "subcategory":  subcat,
        "unit_price":   mixed_currency(u_price, p_style),
        "unit_cost":    mixed_currency(u_cost,  c_style),
        "is_active":    mixed_bool(is_act),
        "launch_date":  mixed_date(launch, d_style),
    })

df = pd.DataFrame(records)

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — DATA QUALITY INJECTIONS
# ════════════════════════════════════════════════════════════════════════════

# (a) Nulls ───────────────────────────────────────────────────────────────────
for col, rate in [("subcategory", 0.10), ("unit_cost", 0.12),
                  ("launch_date", 0.11), ("product_name", 0.05)]:
    null_idx = df.sample(frac=rate, random_state=42).index
    df.loc[null_idx, col] = np.nan

# (b) Near-duplicates: spacing & casing in product_name ───────────────────────
dup_idx = df.sample(frac=0.04, random_state=7).index
dups    = df.loc[dup_idx].copy()
dups["product_name"] = dups["product_name"].apply(
    lambda x: ("  " + str(x).lower() + "  ") if pd.notna(x) else x
)
dups["product_id"] = dups["product_id"].str.replace("PROD-", "PRD-", regex=False)
df = pd.concat([df, dups], ignore_index=True)

# (g) Inconsistent product_id prefixes ────────────────────────────────────────
prefix_idx = df.sample(frac=0.05, random_state=55).index
df.loc[prefix_idx, "product_id"] = (
    df.loc[prefix_idx, "product_id"]
      .str.replace("PROD-", "P", regex=False)
      .str.lstrip("0")
)

# (h) Outlier: negative unit_cost for a few rows ──────────────────────────────
neg_idx = df.sample(frac=0.02, random_state=22).index
df.loc[neg_idx, "unit_cost"] = "-99.99"

# ── Shuffle & save ────────────────────────────────────────────────────────────
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
out_path = "data/raw/dim_products.csv"
df.to_csv(out_path, index=False)
print(f"✅ dim_products saved → {out_path}  |  shape: {df.shape}")
print(df.dtypes)
print(df.head(3))
