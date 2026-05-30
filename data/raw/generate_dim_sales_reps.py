"""
Script 5/5 — dim_sales_reps
Generates 75 rows.
Injects: nulls, mixed boolean for is_active, mixed date formats,
         near-duplicate names, inconsistent rep_id prefixes, outlier hire dates.
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

N = 75

TEAMS    = ["Enterprise", "SMB", "Online", "Retail", "Partner"]
MANAGERS = [fake.name() for _ in range(8)]   # pool of 8 managers

def mixed_date(dt, style):
    ts = pd.Timestamp(dt)
    if style == 0:
        return ts.strftime("%m/%d/%Y")
    elif style == 1:
        return ts.strftime("%Y-%m-%d")
    else:
        return ts.strftime("%d-%b-%Y")

def mixed_bool(val):
    style = random.randint(0, 2)
    if style == 0:
        return "True" if val else "False"
    elif style == 1:
        return "YES" if val else "NO"
    else:
        return 1 if val else 0

records = []
for i in range(1, N + 1):
    hire_date = fake.date_between(start_date="-12y", end_date="today")
    is_act    = random.choices([True, False], [0.85, 0.15])[0]
    d_style   = random.randint(0, 2)

    records.append({
        "rep_id":    f"REP-{str(i).zfill(3)}",
        "rep_name":  fake.name(),
        "team":      random.choice(TEAMS),
        "manager":   random.choice(MANAGERS),
        "hire_date": mixed_date(hire_date, d_style),
        "is_active": mixed_bool(is_act),
    })

df = pd.DataFrame(records)

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — DATA QUALITY INJECTIONS
# ════════════════════════════════════════════════════════════════════════════

# (a) Nulls ───────────────────────────────────────────────────────────────────
for col, rate in [("manager", 0.10), ("team", 0.12),
                  ("hire_date", 0.11)]:
    null_idx = df.sample(frac=rate, random_state=42).index
    df.loc[null_idx, col] = np.nan

# (b) Near-duplicate: same rep, name spacing/casing tweaks ────────────────────
dup_idx = df.sample(frac=0.04, random_state=7).index
dups    = df.loc[dup_idx].copy()
dups["rep_name"] = dups["rep_name"].str.lower().apply(lambda x: "  " + x + "  ")
dups["rep_id"]   = dups["rep_id"].str.replace("REP-", "R-", regex=False)
df = pd.concat([df, dups], ignore_index=True)

# (g) Inconsistent rep_id prefixes ────────────────────────────────────────────
prefix_idx = df.sample(frac=0.06, random_state=55).index
df.loc[prefix_idx, "rep_id"] = (
    df.loc[prefix_idx, "rep_id"]
      .str.replace("REP-", "", regex=False)
      .str.lstrip("0")
      .apply(lambda x: f"SR{x}")
)

# (h) Outlier: future hire dates ──────────────────────────────────────────────
future_idx = df.sample(3, random_state=33).index
df.loc[future_idx, "hire_date"] = "2028-01-01"

# (c) Part 3 — 3-5 rows where end_date < start_date modelled as
#     hire_date > today (future dates above cover this pattern)
#     Additionally inject an "end_date" column with 4 rows violated
df["end_date"] = pd.NaT
active_idx = df[df["is_active"].isin(["False", "NO", 0])].sample(
    min(6, df[df["is_active"].isin(["False", "NO", 0])].shape[0]),
    random_state=42
).index
for idx in active_idx:
    h = df.loc[idx, "hire_date"]
    try:
        ts = pd.Timestamp(h)
        df.loc[idx, "end_date"] = ts + pd.Timedelta(days=random.randint(180, 1800))
    except Exception:
        pass

# Inject 4 violations: end_date < hire_date
violation_idx = df.dropna(subset=["end_date"]).sample(
    min(4, df.dropna(subset=["end_date"]).shape[0]), random_state=77
).index
for idx in violation_idx:
    h = df.loc[idx, "hire_date"]
    try:
        ts = pd.Timestamp(h)
        df.loc[idx, "end_date"] = ts - pd.Timedelta(days=random.randint(30, 365))
    except Exception:
        pass

# ── Shuffle & save ────────────────────────────────────────────────────────────
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
out_path = "data/raw/dim_sales_reps.csv"
df.to_csv(out_path, index=False)
print(f"✅ dim_sales_reps saved → {out_path}  |  shape: {df.shape}")
print(df.dtypes)
print(df.head(3))
print("\nend_date < hire_date violations:")
temp = df.dropna(subset=["end_date", "hire_date"]).copy()
temp["hire_dt"] = pd.to_datetime(temp["hire_date"], errors="coerce")
temp["end_dt"]  = pd.to_datetime(temp["end_date"],  errors="coerce")
print(temp[temp["end_dt"] < temp["hire_dt"]][["rep_id","hire_date","end_date"]])
