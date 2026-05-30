"""
Script 1/5 — fact_orders
Generates 5,000 rows for the Retail & E-Commerce dataset.
Injects: nulls, duplicates, mixed date formats, outliers,
         join challenges (orphaned FKs, wrong regions),
         and validation violations (ship < order, zero-revenue, dup IDs).
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

# ── Constants ────────────────────────────────────────────────────────────────
N = 5000

CUSTOMER_IDS  = [f"CUST-{str(i).zfill(3)}" for i in range(1, 1001)]
PRODUCT_IDS   = [f"PROD-{str(i).zfill(3)}" for i in range(1, 201)]
LOCATION_IDS  = [f"LOC-{str(i).zfill(3)}" for i in range(1, 101)]
REP_IDS       = [f"REP-{str(i).zfill(3)}" for i in range(1, 76)]
STATUSES      = ["Completed", "Pending", "Returned", "Cancelled"]
STATUS_WEIGHTS = [0.60, 0.20, 0.12, 0.08]
REGIONS        = ["North", "South", "East", "West", "Central"]

# ── Helper: random date between two dates ────────────────────────────────────
def rand_date(start, end):
    delta = (end - start).days
    return start + pd.Timedelta(days=random.randint(0, delta))

START = pd.Timestamp("2023-01-01")
END   = pd.Timestamp("2024-12-31")

# ── Base generation ──────────────────────────────────────────────────────────
records = []
for i in range(1, N + 1):
    order_date  = rand_date(START, END)
    ship_date   = order_date + pd.Timedelta(days=random.randint(1, 14))
    qty         = random.randint(1, 50)
    unit_price  = round(random.uniform(5, 500), 2)
    discount    = round(random.uniform(0, 0.40), 4)
    revenue     = round(qty * unit_price * (1 - discount), 2)
    cost        = round(revenue * random.uniform(0.40, 0.80), 2)
    status      = random.choices(STATUSES, STATUS_WEIGHTS)[0]
    region      = random.choice(REGIONS)

    records.append({
        "order_id":     f"ORD-{str(i).zfill(5)}",
        "customer_id":  random.choice(CUSTOMER_IDS),
        "product_id":   random.choice(PRODUCT_IDS),
        "location_id":  random.choice(LOCATION_IDS),
        "rep_id":       random.choice(REP_IDS),
        "order_date":   order_date,
        "ship_date":    ship_date,
        "quantity":     qty,
        "unit_price":   unit_price, 
        "revenue":      revenue,
        "cost":         cost,
        "discount_pct": discount,
        "status":       status,
        "region":       region,
    })

df = pd.DataFrame(records)

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — DATA QUALITY INJECTIONS
# ════════════════════════════════════════════════════════════════════════════

# (a) 10-15% nulls across 4 columns ─────────────────────────────────────────
for col, rate in [("rep_id", 0.12), ("discount_pct", 0.10),
                  ("location_id", 0.11), ("region", 0.13)]:
    null_idx = df.sample(frac=rate, random_state=42).index
    df.loc[null_idx, col] = np.nan

# (b) 3-5% near-duplicates ───────────────────────────────────────────────────
dup_idx = df.sample(frac=0.04, random_state=7).index
dups    = df.loc[dup_idx].copy()
# mutate order_id slightly so they look like near-dupes
dups["order_id"] = dups["order_id"].str.replace("ORD-", "ord-")
df = pd.concat([df, dups], ignore_index=True)

# (c) Mixed date formats ──────────────────────────────────────────────────────
def mixed_date_format(dt, style):
    if pd.isna(dt):
        return dt
    ts = pd.Timestamp(dt)
    if style == 0:
        return ts.strftime("%m/%d/%Y")          # MM/DD/YYYY
    elif style == 1:
        return ts.strftime("%Y-%m-%d")           # YYYY-MM-DD
    else:
        return ts.strftime("%d-%b-%Y")           # DD-Mon-YYYY

styles_order = np.random.choice([0, 1, 2], size=len(df))
styles_ship  = np.random.choice([0, 1, 2], size=len(df))
df["order_date"] = [mixed_date_format(d, s) for d, s in zip(df["order_date"], styles_order)]
df["ship_date"]  = [mixed_date_format(d, s) for d, s in zip(df["ship_date"],  styles_ship)]

# (e) Mixed currency strings for unit_price ──────────────────────────────────
def mixed_currency(val, style):
    if pd.isna(val):
        return val
    if style == 0:
        return f"${val:,.2f}"
    elif style == 1:
        return str(int(val))
    else:
        return f"{val:,.2f}".replace("$", "")

price_styles = np.random.choice([0, 1, 2], size=len(df))
df["unit_price"] = [mixed_currency(v, s) for v, s in zip(df["unit_price"], price_styles)]

# (g) Inconsistent customer_id prefixes ───────────────────────────────────────
prefix_idx = df.sample(frac=0.06, random_state=99).index
df.loc[prefix_idx, "customer_id"] = (
    df.loc[prefix_idx, "customer_id"]
      .str.replace("CUST-", "C", regex=False)
      .str.lstrip("0")
)

# (h) Outliers ────────────────────────────────────────────────────────────────
# Negative revenue (1%)
neg_idx = df.sample(frac=0.01, random_state=11).index
df.loc[neg_idx, "revenue"] = df.loc[neg_idx, "revenue"].apply(lambda x: -abs(float(str(x).replace("$","").replace(",",""))) if pd.notna(x) else x)

# Future ship dates (0.5%)
future_idx = df.sample(frac=0.005, random_state=22).index
df.loc[future_idx, "ship_date"] = "2026-07-15"

# Zero-quantity completed orders (0.5%)
zq_idx = df[df["status"] == "Completed"].sample(frac=0.007, random_state=33).index
df.loc[zq_idx, "quantity"] = 0

# ════════════════════════════════════════════════════════════════════════════
# PART 3 — JOIN CHALLENGES
# ════════════════════════════════════════════════════════════════════════════

# (b) 4% orphaned customer_id (IDs that won't exist in dim_customers) ─────────
orphan_idx = df.sample(frac=0.04, random_state=55).index
df.loc[orphan_idx, "customer_id"] = [f"CUST-{random.randint(9000, 9999)}" for _ in orphan_idx]

# (c) 3-5 rows where ship_date < order_date (already injected via Part 5 below)

# ════════════════════════════════════════════════════════════════════════════
# PART 5 — VALIDATION VIOLATIONS
# ════════════════════════════════════════════════════════════════════════════

# (a) 5 rows ship_date < order_date ──────────────────────────────────────────
bad_ship_idx = df.sample(5, random_state=77).index
df.loc[bad_ship_idx, "ship_date"]  = "2022-12-01"   # clearly before any order_date
df.loc[bad_ship_idx, "order_date"] = "2023-06-15"

# (b) 3 rows revenue=0 where status=Completed ────────────────────────────────
zero_rev_idx = df[df["status"] == "Completed"].sample(3, random_state=88).index
df.loc[zero_rev_idx, "revenue"] = 0
  
# (c) 4 duplicate order_id pairs with different revenue ───────────────────────
dup_pairs = df.sample(4, random_state=66).copy()
dup_pairs["revenue"] = dup_pairs["revenue"].apply(
    lambda x: round(float(str(x).replace("$","").replace(",","")) * 1.15, 2)
    if pd.notna(x) else x
)
# Keep same order_id but restore ORD- prefix
dup_pairs["order_id"] = df.sample(4, random_state=66)["order_id"].values
df = pd.concat([df, dup_pairs], ignore_index=True)

# (d) 6 rows region mismatch vs dim_customers (we tag them for traceability) ──
mismatch_idx = df.sample(6, random_state=44).index
other_regions = ["North", "South", "East", "West", "Central"]
df.loc[mismatch_idx, "region"] = [
    random.choice([r for r in other_regions if r != str(df.loc[i, "region"])])
    for i in mismatch_idx
]
df.loc[mismatch_idx, "_region_mismatch_flag"] = True   # will be dropped before BI

# ── Final shuffle & save ─────────────────────────────────────────────────────
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
out_path = "data/raw/fact_orders.csv"
df.to_csv(out_path, index=False)
print(f"✅ fact_orders saved → {out_path}  |  shape: {df.shape}")
print(df.dtypes)
print(df.head(3))
