# Retail & E-Commerce Dataset — Reference Document

---

## PART 6.2 — Entity Relationship Summary

```
fact_orders
  ├── customer_id  ──→  dim_customers.cust_id        ⚠ KEY MISMATCH (name differs)
  ├── product_id   ──→  dim_products.product_id       ✓ name matches
  ├── location_id  ──→  dim_locations.location_id     ✓ name matches
  └── rep_id       ──→  dim_sales_reps.rep_id         ✓ name matches
```

### Known Join Mismatches & Hazards

| # | Type | Detail |
|---|------|--------|
| 1 | **Key name mismatch** | `fact_orders.customer_id` must join to `dim_customers.cust_id` — column names differ |
| 2 | **Orphaned FK — customers** | ~4% of `fact_orders.customer_id` values (e.g. `CUST-9001`) have no matching row in `dim_customers` |
| 3 | **Orphaned FK — all dims** | ~4% of all FK columns in `fact_orders` have no match in any dimension table |
| 4 | **Prefix inconsistency** | IDs appear as `CUST-001`, `C1`, `001`; `PROD-001`, `PRD-001`, `P1`; `LOC-001`, `LO-01`, `L1`; `REP-001`, `R-01`, `SR1` — must be normalised before joining |
| 5 | **Inactive products in orders** | `dim_products.is_active = False/NO/0` rows still referenced in recent 2024 orders |
| 6 | **Region mismatch** | 6 rows in `fact_orders.region` disagree with the same customer's `dim_customers.region` |
| 7 | **end_date < hire_date** | 4 rows in `dim_sales_reps` where `end_date` precedes `hire_date` |
| 8 | **ship_date < order_date** | 5 rows in `fact_orders` — logical impossibility |

---

## PART 6.3 — Data Dictionary

### Table: fact_orders (~5,200 rows after injected dupes)

| Column | Data Type | Description | Injected Issues |
|--------|-----------|-------------|-----------------|
| order_id | string | Unique order identifier (`ORD-XXXXX`) | 4 duplicate IDs with different revenue; near-dupes with lowercase `ord-` prefix |
| customer_id | string | FK → dim_customers.cust_id | ⚠ Key name mismatch; 6% inconsistent prefixes (C1, 001); 4% orphaned (CUST-9000+) |
| product_id | string | FK → dim_products.product_id | 4% orphaned records |
| location_id | string | FK → dim_locations.location_id | 11% nulls; 4% orphaned |
| rep_id | string | FK → dim_sales_reps.rep_id | 12% nulls; 4% orphaned |
| order_date | string | Date order was placed | Mixed formats: MM/DD/YYYY, YYYY-MM-DD, DD-Mon-YYYY |
| ship_date | string | Date order was shipped | Mixed formats; 5 rows where ship_date < order_date; 0.5% future dates (2026-07-15) |
| quantity | integer | Number of units ordered | 0.5% zero-quantity on Completed orders (outlier) |
| unit_price | string | Price per unit at time of order | Mixed currency: `$1,200.00`, `1200`, `1,200.000` |
| revenue | float | Gross revenue = qty × unit_price × (1−discount) | 3 rows = 0 where status=Completed; 1% negative values; 4 duplicate IDs with different amounts |
| cost | float | Cost of goods for this order | 10–15% range; can be used for profit calculation |
| discount_pct | float | Decimal discount applied (0–0.40) | 10% nulls |
| status | string | Order status | Values: Completed, Pending, Returned, Cancelled |
| region | string | Sales region at order time | 13% nulls; 6 rows intentionally mismatched vs dim_customers.region |
| _region_mismatch_flag | boolean | Internal traceability flag | Should be dropped before loading to BI tool |

---

### Table: dim_customers (~1,040 rows after injected dupes)

| Column | Data Type | Description | Injected Issues |
|--------|-----------|-------------|-----------------|
| cust_id | string | PK — customer identifier | ⚠ Named `cust_id`, not `customer_id`; 6% inconsistent prefixes (C1, 001) |
| full_name | string | Customer full name | Near-dupes in ALL CAPS; 3–5% duplication |
| email | string | Email address | 13% nulls |
| phone | string | Contact phone number | Mixed formats: `(555) 123-4567`, `555-123-4567`, `+15551234567`, `5551234567`; 12% nulls |
| region | string | Customer's sales region | Used to validate against fact_orders.region |
| state | string | US state abbreviation | 10% nulls |
| segment | string | Customer segment | Values: B2B, B2C, Guest; 11% nulls |
| join_date | string | Date customer registered | Mixed formats: MM/DD/YYYY, YYYY-MM-DD, DD-Mon-YYYY |
| status | string | Account status | Values: Active, Inactive, Churned |
| is_active | mixed | Derived active flag | Mixed boolean: `True/False`, `YES/NO`, `1/0` |
| customer_age | integer | Customer age in years | 2% outliers set to 999 |

---

### Table: dim_products (~208 rows after injected dupes)

| Column | Data Type | Description | Injected Issues |
|--------|-----------|-------------|-----------------|
| product_id | string | PK — product identifier | Near-dupes with `PRD-` prefix; 5% inconsistent (P1, P23) |
| product_name | string | Display name of product | 5% nulls; near-dupes with extra spaces and lowercase |
| category | string | Top-level category | 6 categories: Electronics, Apparel, Home & Garden, Sports, Office, Beauty |
| subcategory | string | Sub-level category | 10% nulls |
| unit_price | string | Standard list price | Mixed currency: `$1,200.00`, `1200`, `1,200.000` |
| unit_cost | string | Standard cost to produce/acquire | 12% nulls; 2% negative values (`-99.99`); mixed currency formats |
| is_active | mixed | Whether product is currently sold | Mixed boolean: `True/False`, `YES/NO`, `1/0`; inactive products appear in recent orders |
| launch_date | string | Date product was launched | 11% nulls; mixed formats: MM/DD/YYYY, YYYY-MM-DD, DD-Mon-YYYY |

---

### Table: dim_locations (~104 rows after injected dupes)

| Column | Data Type | Description | Injected Issues |
|--------|-----------|-------------|-----------------|
| location_id | string | PK — location identifier | Near-dupes with `LO-` prefix; 5% inconsistent (L1, L23) |
| city | string | City name | 11% nulls; near-dupes with lowercase casing |
| state | string | US state abbreviation | 10% nulls; 5 rows: TX assigned to "North" region (should be South) |
| region | string | Sales region | 5 rows intentionally mismatched to state |
| country | string | Country code | All USA in base; UK-style postal codes on some rows (inconsistency) |
| postal_code | string | Postal / ZIP code | 10% nulls; mixed formats: `90210`, `90210-1234`, `AB12 3CD` |
| territory | string | Sales territory designation | 12% nulls; values: Territory-A through Territory-F |

---

### Table: dim_sales_reps (~78 rows after injected dupes)

| Column | Data Type | Description | Injected Issues |
|--------|-----------|-------------|-----------------|
| rep_id | string | PK — sales rep identifier | Near-dupes with `R-` prefix; 6% inconsistent (SR1, SR23) |
| rep_name | string | Full name of sales rep | Near-dupes with lowercase + extra whitespace |
| team | string | Sales team | Values: Enterprise, SMB, Online, Retail, Partner; 12% nulls |
| manager | string | Manager's full name | 10% nulls |
| hire_date | string | Date rep was hired | 11% nulls; mixed formats; 3 future dates (2028-01-01) — outliers |
| is_active | mixed | Whether rep is currently active | Mixed boolean: `True/False`, `YES/NO`, `1/0` |
| end_date | datetime | Date rep left (if applicable) | 4 rows where end_date < hire_date — logical violation |

---

## PART 6.4 — Analyst Exercise List

> 10 tasks the analyst must complete **before** building the Power BI dashboard.

---

### Task 1 — Standardise All ID Prefixes (Join Enablement)
**Tables:** All 5  
**Problem:** IDs exist in 3+ formats (`CUST-001`, `C1`, `001`; `PROD-001`, `PRD-001`, `P1`; etc.)  
**Action:** Strip all prefixes, left-pad numerics to a uniform width (e.g. 4 digits), re-apply a single canonical prefix per table. Apply the same normalisation to `fact_orders` FK columns before joining.

```python
# Example
df['customer_id'] = (
    df['customer_id']
      .str.upper()
      .str.replace(r'^(CUST-?|C)', '', regex=True)
      .str.zfill(4)
      .apply(lambda x: f"CUST-{x}")
)
```

---

### Task 2 — Resolve the customer_id / cust_id Key Name Mismatch (Join Enablement)
**Tables:** `fact_orders` ↔ `dim_customers`  
**Problem:** `fact_orders` uses `customer_id`; `dim_customers` uses `cust_id`. A naive merge on identical column names will fail or produce a cross-join.  
**Action:** Rename one side before merging, or specify `left_on` / `right_on` explicitly. Document the rename in a mapping table.

```python
merged = fact_orders.merge(
    dim_customers,
    left_on='customer_id',
    right_on='cust_id',
    how='left'
)
```

---

### Task 3 — Normalise All Date Columns to ISO-8601 (Transformation)
**Tables:** `fact_orders` (order_date, ship_date), `dim_customers` (join_date), `dim_products` (launch_date), `dim_sales_reps` (hire_date, end_date)  
**Problem:** Three mixed formats in every date column; `pd.to_datetime` will silently misparse MM/DD/YYYY as DD/MM/YYYY in some locales.  
**Action:** Use `dateutil.parser.parse` with error handling, then cast to `datetime64[ns]`. Flag rows where parsing fails as `NaT` and log them.

```python
from dateutil import parser as dparser

def safe_parse(val):
    try:
        return pd.Timestamp(dparser.parse(str(val), dayfirst=False))
    except Exception:
        return pd.NaT

df['order_date'] = df['order_date'].apply(safe_parse)
```

---

### Task 4 — Parse & Standardise Numeric Currency Columns (Cleansing)
**Tables:** `fact_orders` (unit_price), `dim_products` (unit_price, unit_cost)  
**Problem:** Values stored as `$1,200.00`, `1200`, `1,200.000` — all as strings; cannot be aggregated.  
**Action:** Strip `$`, remove `,`, cast to `float64`. Validate that all prices are positive; flag negative unit_cost rows as outliers.

```python
def parse_currency(val):
    if pd.isna(val):
        return np.nan
    return float(str(val).replace('$', '').replace(',', '').strip())

df['unit_price'] = df['unit_price'].apply(parse_currency)
```

---

### Task 5 — Normalise Boolean Columns (Cleansing)
**Tables:** `dim_customers` (is_active), `dim_products` (is_active), `dim_sales_reps` (is_active)  
**Problem:** Booleans stored as `True/False`, `YES/NO`, `1/0` — mixed object dtype; cannot be used in filters.  
**Action:** Map all representations to Python `bool`. Create a lookup dict and apply uniformly across all three tables.

```python
BOOL_MAP = {
    'true': True, 'yes': True, '1': True,
    'false': False, 'no': False, '0': False
}
df['is_active'] = df['is_active'].astype(str).str.strip().str.lower().map(BOOL_MAP)
```

---

### Task 6 — Validate & Quarantine Logical Violations (Validation)
**Tables:** `fact_orders`, `dim_sales_reps`  
**Problem (a):** 5 rows where `ship_date < order_date`  
**Problem (b):** 3 rows where `revenue = 0` and `status = Completed`  
**Problem (c):** 4 duplicate `order_id` pairs with different `revenue` amounts  
**Problem (d):** 4 rows in `dim_sales_reps` where `end_date < hire_date`  
**Action:** Write a validation function for each rule. Route violating rows to a `quarantine/` folder with an error code column. Never silently drop them.

```python
violations = df[df['ship_date'] < df['order_date']].copy()
violations['error_code'] = 'SHIP_BEFORE_ORDER'
violations.to_csv('data/quarantine/ship_date_violations.csv', index=False)
df_clean = df[df['ship_date'] >= df['order_date']]
```

---

### Task 7 — Deduplicate All Tables (Cleansing)
**Tables:** All 5  
**Problem:** 3–5% exact and near-duplicates (lowercase names, extra whitespace, alternate ID prefixes).  
**Action:**  
1. After ID normalisation (Task 1), drop exact duplicate primary keys keeping the first occurrence.  
2. For near-dupes (name variants), use fuzzy matching (`rapidfuzz`) or sort + `shift()` comparison to find string similarity ≥ 95%. Resolve to canonical form.  
3. For `order_id` dupes with different revenue (Task 6c), do not blindly deduplicate — investigate and quarantine.

```python
# Exact dupe by PK
df = df.drop_duplicates(subset=['order_id'], keep='first')

# Near-dupe by normalised name
df['name_key'] = df['full_name'].str.strip().str.lower().str.replace(r'\s+', ' ', regex=True)
df = df.drop_duplicates(subset=['name_key'], keep='first').drop(columns='name_key')
```

---

### Task 8 — Handle Nulls Strategically (Cleansing)
**Tables:** All 5  
**Problem:** 10–15% nulls in 3–4 columns per table; naive `.dropna()` would lose ~15% of orders.  
**Action:** Triage nulls by column impact:
- **FK nulls** (`rep_id`, `location_id`): join will produce `NaN` attributes — acceptable if noted in the report, or impute with an `"Unknown"` sentinel.
- **Metric nulls** (`discount_pct`): impute with 0 (no discount).
- **Dimension attribute nulls** (`email`, `state`, `phone`): leave as `NULL` in the model; do not impute PII.
- Flag imputed rows with a boolean `_imputed` column for audit.

```python
df['discount_pct'] = df['discount_pct'].fillna(0)
df['rep_id']       = df['rep_id'].fillna('UNKNOWN')
```

---

### Task 9 — Build Derived Transformation Columns (Transformation)
**Tables:** `fact_orders` (after Tasks 1–8 complete)  
**Columns to create:**

| New Column | Formula | Purpose |
|------------|---------|---------|
| `profit` | `revenue − cost` | Margin analysis |
| `days_to_ship` | `(ship_date − order_date).dt.days` | Fulfilment KPI |
| `order_year` | `order_date.dt.year` | Time slicing |
| `order_month` | `order_date.dt.month` | Time slicing |
| `order_quarter` | `order_date.dt.quarter` | Time slicing |
| `order_weekday` | `order_date.dt.day_name()` | DoW analysis |
| `revenue_tier` | `pd.cut(revenue, bins, labels=['Low','Medium','High','Premium'])` | Segmentation |
| `rolling_revenue_30d` | `df.set_index('order_date')['revenue'].rolling('30D').sum()` | Trend |

```python
df['profit']       = df['revenue'] - df['cost']
df['days_to_ship'] = (df['ship_date'] - df['order_date']).dt.days
bins   = [0, 500, 2000, 10000, float('inf')]
labels = ['Low', 'Medium', 'High', 'Premium']
df['revenue_tier'] = pd.cut(df['revenue'], bins=bins, labels=labels)
```

---

### Task 10 — Build Analytical Models: RFM + Cohort (Aggregation)
**Tables:** `fact_orders` joined with `dim_customers`  
**RFM Scoring:**
```python
snapshot = pd.Timestamp('2025-01-01')
rfm = (
    df[df['status'] == 'Completed']
    .groupby('customer_id')
    .agg(
        recency   = ('order_date', lambda x: (snapshot - x.max()).days),
        frequency = ('order_id',   'nunique'),
        monetary  = ('revenue',    'sum')
    )
    .reset_index()
)
# Quintile-score each dimension 1–5
for col in ['recency', 'frequency', 'monetary']:
    rfm[f'{col}_score'] = pd.qcut(rfm[col], 5, labels=[5,4,3,2,1] if col=='recency' else [1,2,3,4,5])
rfm['rfm_segment'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)
```

**Cohort Analysis:**
```python
# Cohort = month of first order; activity = month of each subsequent order
df['cohort_month']   = df.groupby('customer_id')['order_date'].transform('min').dt.to_period('M')
df['activity_month'] = df['order_date'].dt.to_period('M')
df['cohort_index']   = (df['activity_month'] - df['cohort_month']).apply(lambda x: x.n)

cohort_table = (
    df.groupby(['cohort_month', 'cohort_index'])['customer_id']
      .nunique()
      .unstack()
      .fillna(0)
)
```

---

*Generated with `random.seed(42)` and `Faker.seed(42)` — fully reproducible.*
