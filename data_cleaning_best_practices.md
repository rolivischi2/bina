# Data Cleaning Best Practices

A comprehensive guide to data cleaning for BI and data science projects — from raw data to analysis-ready datasets.

---

## Table of Contents

1. [Why Data Cleaning Matters](#1-why-data-cleaning-matters)
2. [The Data Cleaning Workflow](#2-the-data-cleaning-workflow)
3. [Phase 1: Profiling — Know Your Data Before You Touch It](#3-phase-1-profiling--know-your-data-before-you-touch-it)
4. [Phase 2: Structural Issues](#4-phase-2-structural-issues)
5. [Phase 3: Missing Data](#5-phase-3-missing-data)
6. [Phase 4: Data Type Integrity](#6-phase-4-data-type-integrity)
7. [Phase 5: Validity & Range Checks](#7-phase-5-validity--range-checks)
8. [Phase 6: Consistency Across Sources](#8-phase-6-consistency-across-sources)
9. [Phase 7: Outliers & Anomalies](#9-phase-7-outliers--anomalies)
10. [Phase 8: Documentation & Reproducibility](#10-phase-8-documentation--reproducibility)
11. [Cleaning Patterns for Common Data Types](#11-cleaning-patterns-for-common-data-types)
12. [Anti-Patterns — What NOT To Do](#12-anti-patterns--what-not-to-do)
13. [Validation Checklist](#13-validation-checklist)

---

## 1. Why Data Cleaning Matters

Data cleaning is typically 60–80% of the work in any data project. It's unglamorous but critical: **every downstream analysis, visualization, and decision inherits the quality of the input data.** The principle is simple — garbage in, garbage out.

Poorly cleaned data leads to:
- Wrong statistical conclusions (e.g., inflated means from duplicate rows)
- Broken joins and merges (e.g., trailing whitespace in keys)
- Silent errors that surface only in final results (e.g., timezone mismatches)
- Wasted time debugging analyses that were correct but fed bad data

The goal of data cleaning is NOT to make data "perfect." It's to make data **fit for purpose** — clean enough to reliably answer your specific research questions.

---

## 2. The Data Cleaning Workflow

Data cleaning is not a single step. It's a sequence of phases, each building on the previous one:

```
Raw Data
  │
  ▼
① Profile → understand shape, types, distributions, issues
  │
  ▼
② Fix Structure → column names, duplicates, format consistency
  │
  ▼
③ Handle Missing Data → identify patterns, choose strategy per column
  │
  ▼
④ Fix Data Types → dates as datetime, numbers as numeric, categories as category
  │
  ▼
⑤ Validate Ranges → domain-specific constraints (no negative counts, temp between -30 and 45°C)
  │
  ▼
⑥ Cross-Source Consistency → align timezones, units, naming across merged datasets
  │
  ▼
⑦ Handle Outliers → detect, investigate, decide (keep / flag / remove / cap)
  │
  ▼
⑧ Document → log every decision, make it reproducible
  │
  ▼
Clean Data (analysis-ready)
```

**Key principle:** Don't jump to fixing things before you understand the data. Profile first, always.

---

## 3. Phase 1: Profiling — Know Your Data Before You Touch It

Before changing anything, build a complete picture of what you're working with.

### Structural profiling

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")

# Dimensions
print(f"Rows: {df.shape[0]:,}, Columns: {df.shape[1]}")

# Column names and types
print(df.dtypes)

# Memory footprint
print(f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# First and last rows (catch header/footer junk)
print(df.head(3))
print(df.tail(3))
```

### Completeness profiling

```python
# Missing values: count and percentage
missing = pd.DataFrame({
    "count": df.isnull().sum(),
    "pct": (df.isnull().mean() * 100).round(1)
})
print(missing[missing["count"] > 0].sort_values("pct", ascending=False))
```

This tells you immediately which columns are problematic and how severe the gaps are.

### Distribution profiling

```python
# Numeric columns: check for unexpected ranges, concentrations, impossible values
print(df.describe())

# Look for suspicious values
for col in df.select_dtypes(include="number").columns:
    print(f"\n--- {col} ---")
    print(f"  Min: {df[col].min()}, Max: {df[col].max()}")
    print(f"  Zeros: {(df[col] == 0).sum()} ({(df[col] == 0).mean()*100:.1f}%)")
    print(f"  Negatives: {(df[col] < 0).sum()}")
```

### Categorical profiling

```python
# Check unique values, spot inconsistencies
for col in df.select_dtypes(include="object").columns:
    n_unique = df[col].nunique()
    print(f"\n--- {col} ({n_unique} unique) ---")
    if n_unique < 30:
        print(df[col].value_counts())
    else:
        print(df[col].value_counts().head(10))
        print(f"  ... and {n_unique - 10} more")
```

### Automated profiling (for convenience)

```python
# Quick one-liner profile (generates an HTML report)
# pip install ydata-profiling
from ydata_profiling import ProfileReport

profile = ProfileReport(df, title="Data Profile", minimal=True)
profile.to_file("data_profile.html")
```

---

## 4. Phase 2: Structural Issues

### Column names

Inconsistent or messy column names cause bugs and make code hard to read.

```python
# Standardize: lowercase, underscores, no spaces or special characters
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[^a-z0-9_]", "_", regex=True)
    .str.replace(r"_+", "_", regex=True)       # Collapse multiple underscores
    .str.strip("_")
)

# Rename specific columns for clarity
df = df.rename(columns={
    "fk_standort": "station_id",
    "datum": "datetime",
})
```

### Duplicate rows

```python
# Exact duplicates
n_dupes = df.duplicated().sum()
print(f"Exact duplicates: {n_dupes}")

# Key-based duplicates (same station + timestamp = should be unique)
n_key_dupes = df.duplicated(subset=["station_id", "datetime"]).sum()
print(f"Key duplicates: {n_key_dupes}")

# Investigate before dropping — are they true duplicates or data issues?
if n_key_dupes > 0:
    dupes = df[df.duplicated(subset=["station_id", "datetime"], keep=False)]
    print(dupes.sort_values(["station_id", "datetime"]).head(20))

# Drop only after investigation
df = df.drop_duplicates(subset=["station_id", "datetime"], keep="first")
```

**Best practice:** Never blindly `drop_duplicates()`. Always check whether duplicates are identical (safe to drop) or conflicting (need investigation).

### Header and footer junk

Some CSV exports include metadata rows at the top or bottom.

```python
# Check if first/last rows look like data or junk
print(df.head(3))
print(df.tail(3))

# Skip header rows during read
df = pd.read_csv("data.csv", skiprows=2)

# Remove footer rows
df = df.iloc[:-3]  # Remove last 3 rows
```

### Empty rows and columns

```python
# Drop completely empty rows
df = df.dropna(how="all")

# Drop completely empty columns
df = df.dropna(axis=1, how="all")

# Drop columns that are constant (no information)
nunique = df.nunique()
constant_cols = nunique[nunique <= 1].index.tolist()
print(f"Constant columns (can drop): {constant_cols}")
df = df.drop(columns=constant_cols)
```

---

## 5. Phase 3: Missing Data

Missing data is rarely random. Understanding the *pattern* of missingness is as important as choosing a fill strategy.

### Types of missingness

| Type | Meaning | Example | Implication |
|------|---------|---------|-------------|
| **MCAR** (Missing Completely At Random) | Missingness has no relationship to any variable | Sensor randomly loses power | Safe to drop or fill; no bias introduced |
| **MAR** (Missing At Random) | Missingness depends on another *observed* variable | Night hours have more missing data (sensor turns off at night) | Filling is possible if you condition on the observed variable |
| **MNAR** (Missing Not At Random) | Missingness depends on the *missing value itself* | High-traffic hours overflow the counter → NaN exactly when counts are highest | Dangerous: any fill strategy introduces bias. Must acknowledge the limitation |

### Diagnosing missingness patterns

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Missingness by column (overview)
missing_pct = df.isnull().mean() * 100
missing_pct[missing_pct > 0].sort_values(ascending=False).plot(kind="barh")
plt.xlabel("% Missing")
plt.title("Missing data by column")
plt.tight_layout()
plt.show()

# Missingness over time (is it concentrated in certain periods?)
df["is_missing"] = df["velo_in"].isnull().astype(int)
daily_missing = df.resample("D")["is_missing"].mean() * 100
daily_missing.plot(figsize=(14, 3), title="% missing per day")
plt.ylabel("% missing")
plt.tight_layout()
plt.show()

# Missingness correlation (do columns go missing together?)
missing_corr = df.isnull().corr()
sns.heatmap(missing_corr, cmap="YlOrRd", annot=True)
plt.title("Missing data correlation")
plt.tight_layout()
plt.show()
```

### Choosing a missing data strategy

| Situation | Strategy | Code |
|-----------|----------|------|
| < 5% missing, MCAR | Drop rows | `df.dropna(subset=["col"])` |
| Continuous variable, small gaps | Linear interpolation | `df["col"].interpolate(method="linear")` |
| Time series, small gaps (< 1 hour) | Forward fill with limit | `df["col"].fillna(method="ffill", limit=4)` |
| Structural zero (no bikes at 3 AM) | Fill with 0 | `df["col"].fillna(0)` |
| Categorical variable | Fill with mode or "Unknown" | `df["col"].fillna("Unknown")` |
| Large gaps (days/weeks) | Leave as NaN, exclude from analysis | Document the gap, don't fabricate data |
| > 50% missing | Consider dropping the column | Only if the column isn't critical |

**Key principles:**
- **Never fill what you can't justify.** Every fill introduces assumptions. Document them.
- **Respect the gap size.** Interpolating across a 2-hour gap is reasonable. Interpolating across a 2-week gap is fiction.
- **Limit forward/backward fill.** Always use the `limit` parameter to prevent fills from spanning unreasonable distances.

```python
# Good: interpolate small gaps, leave large ones
df["velo_in"] = df["velo_in"].interpolate(method="linear", limit=4, limit_direction="both")
# This fills gaps of up to 4 consecutive NaNs (= 1 hour at 15-min intervals)
# Larger gaps remain NaN — they'll be excluded from analysis

# Good: fill zeros only where it's semantically correct
night_mask = df["hour"].between(0, 4)
df.loc[night_mask, "velo_in"] = df.loc[night_mask, "velo_in"].fillna(0)
```

### Documenting missing data decisions

Always create a log of what you did:

```python
cleaning_log = []

# Example entry
n_before = df["velo_in"].isnull().sum()
df["velo_in"] = df["velo_in"].interpolate(method="linear", limit=4)
n_after = df["velo_in"].isnull().sum()
cleaning_log.append({
    "column": "velo_in",
    "action": "linear interpolation (limit=4)",
    "filled": n_before - n_after,
    "remaining_nan": n_after,
    "justification": "15-min sensor data; gaps <= 1h are plausible to interpolate"
})

pd.DataFrame(cleaning_log)
```

---

## 6. Phase 4: Data Type Integrity

Wrong data types are one of the most common sources of silent bugs.

### The consequences of wrong types

| What happens | Example |
|-------------|---------|
| String "12" + "3" = "123" instead of 15 | Columns read as string instead of numeric |
| Sorting goes wrong ("9" > "10" alphabetically) | IDs or codes stored as strings |
| Date arithmetic fails | Dates stored as strings, can't compute differences |
| Memory wasted | Categories stored as full strings instead of category dtype |
| Groupby creates unexpected groups | "Zürich" vs "Zürich " (trailing space) treated as different |

### Fixing numeric columns

```python
# Check for non-numeric values hiding in a "numeric" column
def check_numeric(series):
    non_numeric = pd.to_numeric(series, errors="coerce")
    problem_rows = series[non_numeric.isnull() & series.notnull()]
    if len(problem_rows) > 0:
        print(f"Non-numeric values found: {problem_rows.unique()[:10]}")
    return problem_rows

check_numeric(df["velo_in"])

# Convert, turning non-parsable values to NaN
df["velo_in"] = pd.to_numeric(df["velo_in"], errors="coerce")
```

Common culprits: values like `"N/A"`, `"-"`, `"."`, `""`, `"null"`, `"#REF!"`, or comma as decimal separator (`"12,5"`).

```python
# Handle European decimal commas
df["value"] = df["value"].str.replace(",", ".").astype(float)

# Handle thousands separators
df["population"] = df["population"].str.replace("'", "").str.replace(".", "").astype(int)
```

### Fixing datetime columns

```python
# Parse with explicit format (faster and safer than letting pandas guess)
df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%dT%H:%M")

# Handle mixed formats
df["datetime"] = pd.to_datetime(df["datetime"], format="mixed", dayfirst=True)

# Check for parsing failures
failed = df[df["datetime"].isnull() & df["raw_date"].notnull()]
if len(failed) > 0:
    print(f"Failed to parse {len(failed)} dates:")
    print(failed["raw_date"].unique()[:10])
```

### Fixing categorical columns

```python
# Convert low-cardinality strings to category (saves memory, enables ordering)
for col in df.select_dtypes(include="object"):
    if df[col].nunique() < 50:
        df[col] = df[col].astype("category")

# Ordered categories (useful for seasons, ratings, etc.)
season_order = ["winter", "spring", "summer", "autumn"]
df["season"] = pd.Categorical(df["season"], categories=season_order, ordered=True)
```

### Boolean columns

```python
# Convert string booleans
df["active"] = df["active"].map({"yes": True, "no": False, "1": True, "0": False})

# Create explicit boolean from condition
df["has_rain"] = df["precipitation"] > 0
```

---

## 7. Phase 5: Validity & Range Checks

Domain knowledge is essential here. Define what is *valid* for each column and enforce it.

### Define constraints

```python
# Create a validation schema for your data
CONSTRAINTS = {
    "velo_in":       {"min": 0, "max": 5000, "type": "int"},
    "velo_out":      {"min": 0, "max": 5000, "type": "int"},
    "temperature":   {"min": -30, "max": 45, "type": "float"},
    "precipitation": {"min": 0, "max": 100, "type": "float"},
    "wind_speed":    {"min": 0, "max": 200, "type": "float"},
    "hour":          {"min": 0, "max": 23, "type": "int"},
}
```

### Check constraints systematically

```python
def validate_column(df, col, constraints):
    """Check a column against defined constraints. Returns problem rows."""
    issues = []
    c = constraints.get(col, {})

    if "min" in c:
        below = df[df[col] < c["min"]]
        if len(below) > 0:
            issues.append(f"  {len(below)} values below min ({c['min']})")

    if "max" in c:
        above = df[df[col] > c["max"]]
        if len(above) > 0:
            issues.append(f"  {len(above)} values above max ({c['max']})")

    if issues:
        print(f"\n{col}:")
        for issue in issues:
            print(issue)
    return issues

# Run validation
for col in CONSTRAINTS:
    if col in df.columns:
        validate_column(df, col, CONSTRAINTS)
```

### Handling invalid values

```python
# Option 1: Set to NaN (safest — treat as missing)
df.loc[df["velo_in"] < 0, "velo_in"] = np.nan
df.loc[df["temperature"] > 45, "temperature"] = np.nan

# Option 2: Clip to valid range (if slight exceedances are measurement noise)
df["wind_speed"] = df["wind_speed"].clip(lower=0)

# Option 3: Flag for review
df["velo_in_suspicious"] = (df["velo_in"] > 3000) | (df["velo_in"] < 0)
```

### Temporal validity

```python
# Check for gaps in time series
df = df.set_index("datetime").sort_index()
time_diffs = df.index.to_series().diff()
expected_freq = pd.Timedelta("15min")

gaps = time_diffs[time_diffs > expected_freq]
print(f"Found {len(gaps)} gaps in the time series:")
print(gaps.head(10))

# Check for duplicated timestamps (same station, same time)
ts_dupes = df.index.duplicated()
print(f"Duplicate timestamps: {ts_dupes.sum()}")

# Check date range makes sense
print(f"Date range: {df.index.min()} to {df.index.max()}")
```

### Cross-column consistency

```python
# Total should equal in + out
df["calc_total"] = df["velo_in"] + df["velo_out"]
mismatch = df[df["total"] != df["calc_total"]]
if len(mismatch) > 0:
    print(f"In + Out ≠ Total for {len(mismatch)} rows")

# End date should be after start date
if "start" in df.columns and "end" in df.columns:
    invalid = df[df["end"] < df["start"]]
    print(f"End before start: {len(invalid)} rows")

# Coordinates should be in Switzerland (rough bbox)
if "lon" in df.columns:
    outside = df[(df["lon"] < 5.9) | (df["lon"] > 10.5) |
                 (df["lat"] < 45.8) | (df["lat"] > 47.8)]
    print(f"Coordinates outside Switzerland: {len(outside)} rows")
```

---

## 8. Phase 6: Consistency Across Sources

When merging data from different sources, inconsistencies are the norm.

### Timezone alignment

This is one of the most dangerous issues because it produces plausible-looking but wrong results.

```python
# Problem: bike counts in local time, weather data in UTC
# Switzerland is UTC+1 (winter) / UTC+2 (summer)

# Make timezone explicit
velo_df.index = velo_df.index.tz_localize("Europe/Zurich")
weather_df.index = weather_df.index.tz_localize("UTC")

# Convert to same timezone before merging
weather_df.index = weather_df.index.tz_convert("Europe/Zurich")

# Now merge
merged = pd.merge_asof(
    velo_df.sort_index(),
    weather_df.sort_index(),
    left_index=True,
    right_index=True,
    direction="nearest",
    tolerance=pd.Timedelta("30min"),
)
```

### Unit alignment

```python
# Check: is precipitation in mm, cm, or mm/h?
# Check: is temperature in °C or °F?
# Check: is wind in m/s, km/h, or knots?

# Always document and convert to consistent units
weather_df["wind_kmh"] = weather_df["wind_ms"] * 3.6
weather_df["temp_c"] = (weather_df["temp_f"] - 32) * 5 / 9
```

### Temporal granularity alignment

```python
# Bike data: 15-min intervals
# Weather data: hourly
# → Aggregate bike data to hourly before joining

velo_hourly = velo_df.resample("h").agg(
    velo_in=("velo_in", "sum"),
    velo_out=("velo_out", "sum"),
)

# OR: forward-fill hourly weather to 15-min (weather stays constant within the hour)
weather_15min = weather_df.resample("15min").ffill()
```

### Naming conventions

```python
# Different sources may name the same station differently
# Station "Mythenquai" in one source, "ZH_Mythenquai" in another, "2741" in a third

# Create a mapping table
station_map = pd.DataFrame({
    "velo_id": [2741, 3927, 4012],
    "station_name": ["Mythenquai", "Langstrasse", "Binz"],
    "weather_station": ["SMA", "SMA", "SMA"],  # All use Fluntern
})

# Merge through the mapping
velo_df = velo_df.merge(station_map, left_on="station_id", right_on="velo_id")
```

---

## 9. Phase 7: Outliers & Anomalies

### The golden rule: investigate before you act

Outliers in real-world data often represent the most interesting events:
- A sudden spike in bike counts → festival, protest, or construction detour
- A drop to zero for a week → sensor maintenance
- An extreme weather reading → actual storm

**Never remove outliers automatically without understanding what caused them.**

### Detection methods

```python
from scipy import stats

# 1. Visual detection (always start here)
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Box plot
axes[0].boxplot(df["total"].dropna())
axes[0].set_title("Box plot")

# Histogram with tails highlighted
axes[1].hist(df["total"], bins=100, alpha=0.7)
axes[1].axvline(df["total"].quantile(0.99), color="red", linestyle="--", label="99th pct")
axes[1].legend()
axes[1].set_title("Histogram")

# Time series with outliers marked
q99 = df["total"].quantile(0.99)
axes[2].plot(df.index, df["total"], linewidth=0.3, alpha=0.5)
outlier_mask = df["total"] > q99
axes[2].scatter(df.index[outlier_mask], df["total"][outlier_mask],
                color="red", s=10, label="Outliers")
axes[2].legend()
axes[2].set_title("Time series")

plt.tight_layout()
plt.show()

# 2. IQR method (robust, works for skewed data)
Q1 = df["total"].quantile(0.25)
Q3 = df["total"].quantile(0.75)
IQR = Q3 - Q1
lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR

# 3. Z-score (assumes roughly symmetric data)
df["zscore"] = np.abs(stats.zscore(df["total"].fillna(0)))

# 4. Rolling statistics (contextual outliers — unusual for that time of day/year)
df["rolling_mean"] = df.groupby("station_id")["total"].transform(
    lambda x: x.rolling(window=96*7, center=True, min_periods=96).mean()  # 7-day window
)
df["rolling_std"] = df.groupby("station_id")["total"].transform(
    lambda x: x.rolling(window=96*7, center=True, min_periods=96).std()
)
df["contextual_zscore"] = (df["total"] - df["rolling_mean"]) / df["rolling_std"]
```

### Decision framework for outliers

```
Detected outlier
  │
  ├─ Is there a known cause? (holiday, event, sensor error, maintenance)
  │   ├─ Yes, sensor error → Set to NaN (it's not real data)
  │   ├─ Yes, real event → Keep, but flag/annotate
  │   └─ Yes, maintenance → Set to NaN for the maintenance period
  │
  ├─ Is it physically impossible? (negative counts, 50°C in Zürich)
  │   └─ Yes → Set to NaN (measurement error)
  │
  ├─ Does it affect your analysis?
  │   ├─ Using means → Consider winsorizing or using median instead
  │   ├─ Using regression → Check influence (Cook's distance)
  │   └─ Using rank-based methods → Outliers have limited impact, keep them
  │
  └─ Unsure
      └─ Flag but keep. Run analysis with and without. Report both.
```

### Handling strategies

```python
# Flag (safest — keep data, mark for transparency)
df["is_outlier"] = (df["total"] > upper_fence) | (df["total"] < lower_fence)

# Cap / Winsorize (keep the row, limit the value)
from scipy.stats import mstats
df["total_winsorized"] = mstats.winsorize(df["total"], limits=[0.01, 0.01])

# Replace sensor errors with NaN
sensor_error_mask = df["total"] < 0
df.loc[sensor_error_mask, "total"] = np.nan

# Use robust statistics instead of removing outliers
robust_mean = df["total"].median()  # Unaffected by outliers
robust_spread = stats.median_abs_deviation(df["total"].dropna())
```

---

## 10. Phase 8: Documentation & Reproducibility

### Why documentation matters

Your future self (and your teammates) will not remember why you dropped 3,412 rows or filled NaN with zeros. Document every decision.

### The cleaning notebook pattern

Structure your cleaning as a dedicated notebook or script that reads raw data and outputs clean data:

```
01_data_acquisition.ipynb    → downloads raw data to data/raw/
02_data_cleaning.ipynb       → reads raw, outputs clean to data/clean/
03_analysis.ipynb            → reads only from data/clean/
```

**Never modify raw files.** Always read from raw, transform in code, write to a separate clean location.

### Cleaning log

```python
# Maintain a structured log of all cleaning steps
cleaning_log = []

def log_step(step, column, description, rows_affected, rows_remaining):
    cleaning_log.append({
        "step": step,
        "column": column,
        "description": description,
        "rows_affected": rows_affected,
        "rows_remaining": rows_remaining,
    })

# Example usage throughout your cleaning
n_before = len(df)
df = df.drop_duplicates(subset=["station_id", "datetime"])
log_step(1, "all", "Removed duplicate station+timestamp rows",
         n_before - len(df), len(df))

n_nan_before = df["velo_in"].isnull().sum()
df["velo_in"] = df["velo_in"].interpolate(method="linear", limit=4)
n_nan_after = df["velo_in"].isnull().sum()
log_step(2, "velo_in", "Linear interpolation for gaps <= 1 hour",
         n_nan_before - n_nan_after, len(df))

# Print summary at the end
log_df = pd.DataFrame(cleaning_log)
print(log_df.to_string(index=False))
```

### Assertions as guardrails

Place assertions throughout your cleaning pipeline. They catch regressions if the raw data changes.

```python
# After loading
assert df.shape[0] > 100_000, f"Expected >100k rows, got {df.shape[0]}"
assert "datetime" in df.columns, "Missing datetime column"

# After deduplication
assert not df.duplicated(subset=["station_id", "datetime"]).any(), "Duplicates remain!"

# After type conversion
assert df["datetime"].dtype == "datetime64[ns]", "datetime not parsed"
assert df["velo_in"].dtype in ["int64", "float64"], "velo_in not numeric"

# After range checks
assert (df["velo_in"].dropna() >= 0).all(), "Negative bike counts found"
assert df["datetime"].min().year >= 2020, "Unexpected old data"

# After merge
assert len(merged) > 0, "Merge produced empty result"
assert merged["temperature"].isnull().mean() < 0.1, "Too many unmatched weather records"
```

### Save clean data with metadata

```python
# Save clean data
df.to_parquet("data/clean/zurich_velo_clean.parquet", index=True)

# Save cleaning metadata
import json
from datetime import datetime

metadata = {
    "created": datetime.now().isoformat(),
    "source_files": ["2020_verkehrszaehlungen_werte_fussgaenger_velo.csv", "..."],
    "rows_raw": 1_257_696,
    "rows_clean": len(df),
    "rows_dropped": 1_257_696 - len(df),
    "columns": df.columns.tolist(),
    "date_range": f"{df.index.min()} to {df.index.max()}",
    "cleaning_steps": cleaning_log,
}

with open("data/clean/zurich_velo_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2, default=str)
```

---

## 11. Cleaning Patterns for Common Data Types

### Time series sensor data (like bike counters)

```python
# Typical issues:
# - Gaps from sensor downtime
# - Zeros that mean "no data" vs genuine zero traffic
# - Counter resets or overflows
# - Seasonal station activation/deactivation

# Distinguish real zeros from missing data
# At 3 AM on a Tuesday, zero bikes is plausible
# Zero for 3 consecutive days is probably sensor failure

def flag_suspicious_zeros(series, max_consecutive=12):
    """Flag sequences of zeros longer than max_consecutive as likely sensor failure."""
    is_zero = series == 0
    groups = is_zero.ne(is_zero.shift()).cumsum()
    consecutive = is_zero.groupby(groups).transform("sum")
    return is_zero & (consecutive > max_consecutive)

df["suspicious_zero"] = flag_suspicious_zeros(df["velo_in"], max_consecutive=12)
df.loc[df["suspicious_zero"], "velo_in"] = np.nan
```

### Weather data

```python
# Typical issues:
# - Missing values coded as -999 or 99999
# - Different stations have different measurement times
# - Accumulated values (precipitation) vs instantaneous (temperature)

# Replace sentinel values
SENTINEL_VALUES = [-999, -9999, 99999, 9999]
for col in weather_df.select_dtypes(include="number"):
    weather_df[col] = weather_df[col].replace(SENTINEL_VALUES, np.nan)

# Validate physical ranges
weather_df.loc[weather_df["temperature"] < -40, "temperature"] = np.nan
weather_df.loc[weather_df["temperature"] > 50, "temperature"] = np.nan
weather_df.loc[weather_df["precipitation"] < 0, "precipitation"] = np.nan
weather_df.loc[weather_df["humidity"] > 100, "humidity"] = np.nan
```

### Categorical / coded data

```python
# Typical issues:
# - Inconsistent casing ("Zürich" vs "zürich" vs "ZÜRICH")
# - Trailing/leading whitespace
# - Encoding issues (Ã¼ instead of ü)
# - Multiple codes for the same thing

# Standardization pipeline
def clean_categorical(series):
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)   # Normalize whitespace
    )

df["station_name"] = clean_categorical(df["station_name"])

# Verify against known valid values
VALID_STATIONS = ["mythenquai", "langstrasse", "binz", "sihlhölzli"]
unknown = df[~df["station_name"].isin(VALID_STATIONS)]["station_name"].unique()
if len(unknown) > 0:
    print(f"Unknown station names: {unknown}")
```

### Geocoordinates

```python
# Typical issues:
# - Swapped lat/lon
# - Wrong coordinate system (LV95 vs WGS84)
# - (0, 0) as missing value

# Check for (0, 0) — "Null Island"
null_island = df[(df["lon"] == 0) & (df["lat"] == 0)]
df.loc[(df["lon"] == 0) & (df["lat"] == 0), ["lon", "lat"]] = np.nan

# Swiss coordinates (LV95) to WGS84
# LV95 easting ~2_600_000, northing ~1_200_000
# WGS84 lon ~6-10, lat ~46-48
# If values are in millions, they're LV95
if df["ost"].max() > 1_000_000:
    print("Coordinates appear to be in LV95, conversion to WGS84 needed")
```

---

## 12. Anti-Patterns — What NOT To Do

### 1. Cleaning in place without backup

```python
# BAD: modifying the only copy
df["value"] = df["value"].fillna(0)

# GOOD: keep raw data intact, create clean version
df_clean = df.copy()
df_clean["value"] = df_clean["value"].fillna(0)

# BEST: read raw data → transform → save separately
raw = pd.read_csv("data/raw/data.csv")
clean = cleaning_pipeline(raw)
clean.to_parquet("data/clean/data.parquet")
```

### 2. Dropping rows without understanding why they're problematic

```python
# BAD: just make the NaNs go away
df = df.dropna()  # Might drop 40% of your data

# GOOD: targeted, justified drops
df = df.dropna(subset=["velo_in", "datetime"])  # Only critical columns
```

### 3. Filling missing values with the global mean

```python
# BAD: global mean ignores structure
df["velo_in"] = df["velo_in"].fillna(df["velo_in"].mean())
# This fills a 3 AM gap with the average of all hours — nonsense

# GOOD: context-aware fill
df["velo_in"] = df.groupby(["station_id", "hour", "weekday"])["velo_in"].transform(
    lambda x: x.fillna(x.median())
)
# Fills with the median for that station, at that hour, on that day type
```

### 4. Changing data to fit your expectations

```python
# BAD: "This outlier doesn't match my hypothesis, let me remove it"
# This is scientific fraud. Never do this.

# GOOD: define cleaning rules BEFORE looking at results
# Document rules upfront, apply them consistently, report what was removed
```

### 5. Not checking merge results

```python
# BAD: merge and move on
merged = pd.merge(velo, weather, on="datetime")

# GOOD: verify the merge worked
print(f"Left:   {len(velo)} rows")
print(f"Right:  {len(weather)} rows")
print(f"Merged: {len(merged)} rows")
print(f"NaN in temperature after merge: {merged['temperature'].isnull().sum()}")
# If merged has fewer rows than expected, you lost data
# If temperature has many NaNs, the join keys didn't match
```

### 6. Over-cleaning

Not every imperfection needs fixing. Ask:
- Does this issue affect my analysis?
- Is the "fix" introducing more bias than the original problem?
- Am I spending time on columns I won't even use?

Clean what matters. Leave the rest.

---

## 13. Validation Checklist

Run this checklist before declaring your data "clean":

### Structure
- [ ] Column names are consistent (lowercase, underscores, no spaces)
- [ ] No duplicate rows (or duplicates are investigated and justified)
- [ ] No empty rows or columns
- [ ] Row count is plausible (no unexpected data loss)

### Completeness
- [ ] Missing data is profiled and documented
- [ ] Fill strategy is justified for each column
- [ ] No large gaps were silently filled
- [ ] Remaining NaN count is acceptable for your analysis

### Types
- [ ] Dates are datetime type, not strings
- [ ] Numbers are numeric type, not strings
- [ ] Categories are category type with valid levels
- [ ] No mixed types within a column

### Validity
- [ ] All values are within physically possible ranges
- [ ] Cross-column constraints are satisfied
- [ ] Time series has expected frequency (no gaps, no duplicates)
- [ ] Date range matches expected period

### Consistency
- [ ] Timezones are aligned across all sources
- [ ] Units are consistent (all °C, all mm, all m/s)
- [ ] Naming conventions match across merged datasets
- [ ] Granularity is aligned (all hourly, or all 15-min)

### Reproducibility
- [ ] Raw data is untouched and preserved
- [ ] All cleaning steps are in code (not manual edits)
- [ ] Cleaning log documents every decision and its justification
- [ ] Assertions validate assumptions at each step
- [ ] Clean data is saved separately with metadata
