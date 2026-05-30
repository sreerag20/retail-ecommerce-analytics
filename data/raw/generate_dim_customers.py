"""
Script 2/5 — dim_customers
Generates 1,000 rows.
Key name: cust_id (intentional mismatch vs fact_orders.customer_id).
Injects: nulls, duplicates, mixed phone/date formats, boolean chaos,
         inconsistent ID prefixes, outliers.
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

N = 1000
SEGMENTS  = ["B2B", "B2C", "Guest"]
SEG_W     = [0.25, 0.60, 0.15]
STATUSES  = ["Active", "Inactive", "Churned"]
STAT_W    = [0.65, 0.20, 0.15]
REGIONS   = ["North", "South", "East", "West", "Central"]
US_STATES = [
    "CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA",
    "NC", "MI", "WA", "AZ", "CO", "MA", "TN"
]

# ── Helper: mixed date format ────────────────────────────────────────────────
def mixed_date(dt, style):
    ts = pd.Timestamp(dt)
    if style == 0:
        return ts.strftime("%m/%d/%Y")
    elif style == 1:
        return ts.strftime("%Y-%m-%d")
    else:
        return ts.strftime("%d-%b-%Y")

# ── Helper: mixed phone format ───────────────────────────────────────────────
def mixed_phone(style):
    d = [str(random.randint(2,9))] + [str(random.randint(0,9)) for _ in range(9)]
    p = "".join(d)
    if style == 0:
        return f"({p[:3]}) {p[3:6]}-{p[6:]}"
    elif style == 1:
        return f"{p[:3]}-{p[3:6]}-{p[6:]}"
    elif style == 2:
        return f"+1{p}"
    else:
        return p

# ── Helper: boolean as mixed repr ────────────────────────────────────────────
BOOL_STYLES = ["True", "False", "YES", "NO", "1", "0"]

# ── Base records ─────────────────────────────────────────────────────────────
records = []
for i in range(1, N + 1):
    join_date = fake.date_between(start_date="-6y", end_date="today")
    phone_style = random.randint(0, 3)
    date_style  = random.randint(0, 2)

    records.append({
        "cust_id":   f"CUST-{str(i).zfill(3)}",
        "full_name": fake.name(),
        "email":     fake.email(),
        "phone":     mixed_phone(phone_style),
        "region":    random.choice(REGIONS),
        "state":     random.choice(US_STATES),
        "segment":   random.choices(SEGMENTS, SEG_W)[0],
        "join_date": mixed_date(join_date, date_style),
        "status":    random.choices(STATUSES, STAT_W)[0],
    })

df = pd.DataFrame(records)

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — DATA QUALITY INJECTIONS
# ════════════════════════════════════════════════════════════════════════════

# (a) Nulls in 4 columns ──────────────────────────────────────────────────────
for col, rate in [("phone", 0.12), ("state", 0.10),
                  ("segment", 0.11), ("email", 0.13)]:
    null_idx = df.sample(frac=rate, random_state=42).index
    df.loc[null_idx, col] = np.nan

# (b) Near-duplicates: same record, name casing / spacing tweaks ──────────────
dup_idx = df.sample(frac=0.04, random_state=7).index
dups    = df.loc[dup_idx].copy()
dups["full_name"] = dups["full_name"].str.upper()        # ALL CAPS variant
dups["cust_id"]   = dups["cust_id"].str.replace("CUST-0", "CUST-00")  # extra zero
df = pd.concat([df, dups], ignore_index=True)

# (g) Inconsistent cust_id prefixes ───────────────────────────────────────────
prefix_idx = df.sample(frac=0.06, random_state=55).index
df.loc[prefix_idx, "cust_id"] = (
    df.loc[prefix_idx, "cust_id"]
      .str.replace("CUST-", "", regex=False)
      .str.lstrip("0")
      .apply(lambda x: f"C{x}")
)

# (f) Mixed boolean for "is_active" derived from status ───────────────────────
def status_to_bool(s):
    style = random.randint(0, 2)
    active = (s == "Active")
    if style == 0:
        return "True" if active else "False"
    elif style == 1:
        return "YES" if active else "NO"
    else:
        return 1 if active else 0

df["is_active"] = df["status"].apply(status_to_bool)

# (h) Outlier: age=999 injected as a synthetic "customer_age" column ──────────
df["customer_age"] = [random.randint(18, 75) for _ in range(len(df))]
outlier_idx = df.sample(frac=0.02, random_state=33).index
df.loc[outlier_idx, "customer_age"] = 999

# ── Shuffle & save ────────────────────────────────────────────────────────────
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
out_path = "data/raw/dim_customers.csv"
df.to_csv(out_path, index=False)
print(f"✅ dim_customers saved → {out_path}  |  shape: {df.shape}")
print(df.dtypes)
print(df.head(3))
