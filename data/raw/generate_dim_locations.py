"""
Script 4/5 — dim_locations
Generates 100 rows.
Injects: nulls, mixed postal code formats, near-duplicates,
         inconsistent state/region values, outlier postal codes.
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

N = 100

REGIONS     = ["North", "South", "East", "West", "Central"]
TERRITORIES = ["Territory-A", "Territory-B", "Territory-C",
                "Territory-D", "Territory-E", "Territory-F"]
US_STATES = {
    "North":   ["NY", "PA", "NJ", "CT", "MA", "VT", "NH", "ME"],
    "South":   ["TX", "FL", "GA", "NC", "SC", "AL", "MS", "LA"],
    "East":    ["VA", "MD", "DE", "WV", "KY", "TN"],
    "West":    ["CA", "OR", "WA", "NV", "AZ", "CO", "UT", "ID"],
    "Central": ["IL", "OH", "MI", "IN", "WI", "MN", "MO", "IA"],
}

def mixed_postal(style):
    base = str(random.randint(10000, 99999))
    if style == 0:
        return base                        # 5-digit
    elif style == 1:
        return f"{base}-{random.randint(1000,9999)}"   # ZIP+4
    else:
        return f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=2))}{random.randint(10,99)} {random.randint(1,9)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=2))}"  # UK-style postal

records = []
for i in range(1, N + 1):
    region  = random.choice(REGIONS)
    state   = random.choice(US_STATES[region])
    city    = fake.city()
    postal  = mixed_postal(random.randint(0, 2))
    terr    = random.choice(TERRITORIES)

    records.append({
        "location_id": f"LOC-{str(i).zfill(3)}",
        "city":        city,
        "state":       state,
        "region":      region,
        "country":     "USA",
        "postal_code": postal,
        "territory":   terr,
    })

df = pd.DataFrame(records)

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — DATA QUALITY INJECTIONS
# ════════════════════════════════════════════════════════════════════════════

# (a) Nulls ───────────────────────────────────────────────────────────────────
for col, rate in [("city", 0.11), ("postal_code", 0.10),
                  ("territory", 0.12), ("state", 0.10)]:
    null_idx = df.sample(frac=rate, random_state=42).index
    df.loc[null_idx, col] = np.nan

# (b) Near-duplicates: same city/state, slightly different casing ─────────────
dup_idx = df.sample(frac=0.04, random_state=7).index
dups    = df.loc[dup_idx].copy()
dups["city"]        = dups["city"].str.lower()
dups["location_id"] = dups["location_id"].str.replace("LOC-", "LO-", regex=False)
df = pd.concat([df, dups], ignore_index=True)

# (g) Inconsistent location_id prefixes ───────────────────────────────────────
prefix_idx = df.sample(frac=0.05, random_state=55).index
df.loc[prefix_idx, "location_id"] = (
    df.loc[prefix_idx, "location_id"]
      .str.replace("LOC-", "L", regex=False)
      .str.lstrip("0")
)

# (h) Outlier: a few rows with state/region mismatch (South state in North region)
mismatch_idx = df.sample(5, random_state=33).index
df.loc[mismatch_idx, "state"]  = "TX"
df.loc[mismatch_idx, "region"] = "North"   # TX is South — clear mismatch

# ── Shuffle & save ────────────────────────────────────────────────────────────
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
out_path = "data/raw/dim_locations.csv"
df.to_csv(out_path, index=False)
print(f"✅ dim_locations saved → {out_path}  |  shape: {df.shape}")
print(df.dtypes)
print(df.head(3))
