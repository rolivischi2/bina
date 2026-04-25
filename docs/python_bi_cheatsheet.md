# Python for BI & Data Science — Comprehensive Cheat Sheet

A practical reference covering Python skills for data cleaning, analysis, and the statistical concepts most relevant to Business Intelligence and Data Science.

---

## Table of Contents

1. [Data Loading & Inspection](#1-data-loading--inspection)
2. [Data Cleaning](#2-data-cleaning)
3. [Data Transformation](#3-data-transformation)
4. [Merging & Joining](#4-merging--joining)
5. [Grouping & Aggregation](#5-grouping--aggregation)
6. [Time Series Handling](#6-time-series-handling)
7. [Descriptive Statistics](#7-descriptive-statistics)
8. [Distributions & Probability](#8-distributions--probability)
9. [Correlation & Regression](#9-correlation--regression)
10. [Hypothesis Testing](#10-hypothesis-testing)
11. [Effect Size & Practical Significance](#11-effect-size--practical-significance)
12. [Resampling & Bootstrapping](#12-resampling--bootstrapping)
13. [Outlier Detection](#13-outlier-detection)
14. [Feature Engineering](#14-feature-engineering)
15. [Visualization for BI](#15-visualization-for-bi)
16. [Common Pitfalls](#16-common-pitfalls)

---

## 1. Data Loading & Inspection

### Reading different formats

```python
import pandas as pd

# CSV (comma-separated)
df = pd.read_csv("data.csv")

# CSV with different delimiter
df = pd.read_csv("data.csv", sep=";", encoding="utf-8")

# Specify dtypes upfront (faster, avoids type guessing)
df = pd.read_csv("data.csv", dtype={"id": str, "value": float})

# Only load specific columns
df = pd.read_csv("data.csv", usecols=["date", "value", "station"])

# JSON
df = pd.read_json("data.json")

# Excel
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# Parquet (fast, compressed — preferred for large datasets)
df = pd.read_parquet("data.parquet")
```

### First look at the data

```python
df.shape              # (rows, columns)
df.head(10)           # First 10 rows
df.tail(5)            # Last 5 rows
df.dtypes             # Data types per column
df.info()             # Non-null counts + dtypes + memory usage
df.describe()         # Summary statistics for numeric columns
df.describe(include="object")  # Summary for categorical columns
df.columns.tolist()   # Column names as list
df.nunique()          # Unique values per column
df.sample(5)          # Random 5 rows (useful for large datasets)
```

### Memory optimization

```python
# Check memory usage
df.memory_usage(deep=True).sum() / 1e6  # MB

# Downcast numeric types
df["count"] = pd.to_numeric(df["count"], downcast="integer")
df["value"] = pd.to_numeric(df["value"], downcast="float")

# Convert low-cardinality strings to category
df["city"] = df["city"].astype("category")
```

---

## 2. Data Cleaning

### Missing values

```python
# Detect
df.isnull().sum()                  # Missing count per column
df.isnull().mean() * 100           # Missing percentage per column
df[df["value"].isnull()]           # Show rows where value is missing

# Drop
df.dropna()                        # Drop any row with any NaN
df.dropna(subset=["value"])        # Drop rows where 'value' is NaN
df.dropna(thresh=3)                # Keep rows with at least 3 non-NaN values

# Fill
df["value"].fillna(0)                          # Fill with constant
df["value"].fillna(df["value"].mean())         # Fill with column mean
df["value"].fillna(df["value"].median())       # Fill with median (robust to outliers)
df["value"].fillna(method="ffill")             # Forward fill (last known value)
df["value"].fillna(method="bfill")             # Backward fill
df["value"].interpolate(method="linear")       # Linear interpolation
df["value"].interpolate(method="time")         # Time-weighted interpolation
```

### Duplicates

```python
# Detect
df.duplicated().sum()                          # Total duplicate rows
df[df.duplicated(subset=["id", "date"])]       # Duplicates based on key columns

# Remove
df.drop_duplicates()                           # Drop exact duplicate rows
df.drop_duplicates(subset=["id", "date"], keep="last")  # Keep last occurrence
```

### Data types

```python
# String to numeric (coerce turns errors into NaN)
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# String to datetime
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M")

# Numeric to category
df["rating"] = df["rating"].astype("category")

# Boolean
df["is_weekend"] = df["weekday"].isin([5, 6])
```

### String cleaning

```python
# Strip whitespace
df["name"] = df["name"].str.strip()

# Lowercase
df["name"] = df["name"].str.lower()

# Replace substrings
df["name"] = df["name"].str.replace("ä", "ae", regex=False)

# Extract patterns with regex
df["year"] = df["filename"].str.extract(r"(\d{4})")

# Split into multiple columns
df[["first", "last"]] = df["name"].str.split(" ", n=1, expand=True)
```

### Handling inconsistent categories

```python
# See all unique values
df["station"].value_counts()

# Map inconsistent values
mapping = {
    "Zurich": "Zürich",
    "Zuerich": "Zürich",
    "ZH": "Zürich",
}
df["station"] = df["station"].replace(mapping)

# Catch-all: strip + lowercase + replace
df["station"] = df["station"].str.strip().str.lower().replace(mapping)
```

---

## 3. Data Transformation

### Column operations

```python
# New column from calculation
df["total"] = df["velo_in"] + df["velo_out"]

# Conditional column
df["peak"] = df["hour"].between(7, 9) | df["hour"].between(17, 19)

# np.where for if/else
import numpy as np
df["type"] = np.where(df["weekday"] < 5, "workday", "weekend")

# np.select for multiple conditions
conditions = [
    df["hour"].between(6, 9),
    df["hour"].between(10, 15),
    df["hour"].between(16, 19),
    df["hour"].between(20, 23) | df["hour"].between(0, 5),
]
labels = ["morning_rush", "midday", "evening_rush", "night"]
df["period"] = np.select(conditions, labels, default="other")

# Apply a custom function
df["log_value"] = df["value"].apply(np.log1p)

# Apply across rows
df["max_direction"] = df[["velo_in", "velo_out"]].max(axis=1)
```

### Binning / Discretization

```python
# Equal-width bins
df["temp_bin"] = pd.cut(df["temperature"], bins=5, labels=["very_cold", "cold", "mild", "warm", "hot"])

# Custom bin edges
df["temp_bin"] = pd.cut(df["temperature"], bins=[-10, 0, 10, 20, 40], labels=["freezing", "cold", "mild", "warm"])

# Quantile-based bins (equal frequency)
df["volume_quartile"] = pd.qcut(df["total"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])
```

### Ranking

```python
# Rank values (useful for non-parametric analysis)
df["rank"] = df["total"].rank(method="average")

# Percentile rank (0-100)
df["percentile"] = df["total"].rank(pct=True) * 100
```

---

## 4. Merging & Joining

```python
# Inner join (only matching rows)
merged = pd.merge(velo_df, weather_df, on="datetime", how="inner")

# Left join (keep all rows from left)
merged = pd.merge(velo_df, weather_df, on="datetime", how="left")

# Join on different column names
merged = pd.merge(velo_df, weather_df, left_on="timestamp", right_on="date")

# Join on multiple keys
merged = pd.merge(df1, df2, on=["station", "date"])

# Concatenate vertically (stack dataframes)
all_years = pd.concat([df_2020, df_2021, df_2022], ignore_index=True)

# Concatenate horizontally
combined = pd.concat([df_a, df_b], axis=1)
```

### Merge diagnostics

```python
# Check for key uniqueness before merging
assert df1["id"].is_unique, "Duplicate keys in df1!"

# Validate merge result
merged = pd.merge(df1, df2, on="key", how="left", indicator=True)
print(merged["_merge"].value_counts())
# both          = matched
# left_only     = no match in right
# right_only    = no match in left
```

---

## 5. Grouping & Aggregation

### Basic groupby

```python
# Single aggregation
df.groupby("station")["total"].sum()
df.groupby("station")["total"].mean()

# Multiple aggregations
df.groupby("station")["total"].agg(["mean", "median", "std", "count"])

# Multiple columns, multiple aggregations
df.groupby("station").agg(
    avg_volume=("total", "mean"),
    max_volume=("total", "max"),
    days_counted=("date", "nunique"),
)

# Group by multiple keys
df.groupby(["station", "year"])["total"].mean()
```

### Transform vs. aggregate

```python
# aggregate: reduces to one row per group
df.groupby("station")["total"].mean()

# transform: returns same-sized Series (useful for adding group stats back)
df["station_avg"] = df.groupby("station")["total"].transform("mean")

# Normalize within group (z-score per station)
df["z_score"] = df.groupby("station")["total"].transform(
    lambda x: (x - x.mean()) / x.std()
)
```

### Pivot tables

```python
# Pivot: rows=station, columns=month, values=mean volume
pivot = df.pivot_table(
    values="total",
    index="station",
    columns="month",
    aggfunc="mean",
)

# Multiple aggregation functions
pivot = df.pivot_table(
    values="total",
    index="station",
    columns="is_weekend",
    aggfunc=["mean", "std"],
)
```

### Crosstabs (frequency tables)

```python
pd.crosstab(df["station"], df["weekday"])
pd.crosstab(df["station"], df["weekday"], normalize="index")  # Row percentages
```

---

## 6. Time Series Handling

### Datetime basics

```python
df["date"] = pd.to_datetime(df["date"])

# Extract components
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["hour"] = df["date"].dt.hour
df["weekday"] = df["date"].dt.weekday        # 0=Monday, 6=Sunday
df["day_name"] = df["date"].dt.day_name()     # "Monday", "Tuesday", ...
df["week"] = df["date"].dt.isocalendar().week
df["quarter"] = df["date"].dt.quarter
df["is_month_end"] = df["date"].dt.is_month_end

# Set as index for time series operations
df = df.set_index("date").sort_index()
```

### Resampling (changing frequency)

```python
# 15-min data → hourly (sum)
hourly = df.resample("h")["total"].sum()

# 15-min data → daily (sum)
daily = df.resample("D")["total"].sum()

# Daily → monthly (mean)
monthly = df.resample("ME")["total"].mean()

# Daily → yearly (sum)
yearly = df.resample("YE")["total"].sum()

# Resample with multiple aggregations
daily_stats = df.resample("D").agg(
    total=("total", "sum"),
    peak_hour=("total", "max"),
    hours_active=("total", lambda x: (x > 0).sum()),
)
```

### Rolling windows (moving averages)

```python
# 7-day moving average (smooths out daily noise)
df["ma_7d"] = df["total"].rolling(window=7).mean()

# 30-day moving average (smooths out weekly patterns)
df["ma_30d"] = df["total"].rolling(window=30).mean()

# Rolling standard deviation (volatility)
df["std_7d"] = df["total"].rolling(window=7).std()

# Centered window (look both directions)
df["ma_7d_centered"] = df["total"].rolling(window=7, center=True).mean()

# Exponentially weighted moving average (recent data weighted more)
df["ewma"] = df["total"].ewm(span=7).mean()
```

### Year-over-year comparison

```python
# Shift by 1 year
df["total_prev_year"] = df["total"].shift(365)
df["yoy_change"] = (df["total"] - df["total_prev_year"]) / df["total_prev_year"] * 100

# Better: group by day-of-year for averaging
df["dayofyear"] = df.index.dayofyear
seasonal_avg = df.groupby("dayofyear")["total"].mean()
```

---

## 7. Descriptive Statistics

### Measures of Central Tendency

| Measure | What it tells you | When to use | Code |
|---------|-------------------|-------------|------|
| **Mean** | Arithmetic average | Symmetric distributions, no extreme outliers | `df["x"].mean()` |
| **Median** | Middle value (50th percentile) | Skewed distributions, presence of outliers | `df["x"].median()` |
| **Mode** | Most frequent value | Categorical data, multimodal distributions | `df["x"].mode()` |
| **Trimmed mean** | Mean after removing extreme values | When you want robustness but still need a mean | `scipy.stats.trim_mean(df["x"], 0.1)` |

```python
from scipy import stats

mean = df["total"].mean()
median = df["total"].median()
mode = df["total"].mode()[0]
trimmed = stats.trim_mean(df["total"].dropna(), proportiontocut=0.1)  # Cut 10% from each tail

# Compare mean vs median to detect skew
# mean >> median → right-skewed (common for count data)
# mean << median → left-skewed
```

### Measures of Spread / Dispersion

| Measure | What it tells you | Code |
|---------|-------------------|------|
| **Range** | Total spread (max - min) | `df["x"].max() - df["x"].min()` |
| **Variance** | Average squared deviation from mean | `df["x"].var()` |
| **Standard deviation** | Square root of variance (same unit as data) | `df["x"].std()` |
| **IQR** | Range of middle 50% (Q3 - Q1) | `df["x"].quantile(0.75) - df["x"].quantile(0.25)` |
| **CV** | Relative spread (std / mean), unitless | `df["x"].std() / df["x"].mean()` |
| **MAD** | Median absolute deviation (robust) | `df["x"].mad()` or `stats.median_abs_deviation()` |

```python
std = df["total"].std()
iqr = df["total"].quantile(0.75) - df["total"].quantile(0.25)
cv = df["total"].std() / df["total"].mean()   # Coefficient of variation

# Percentiles / quantiles
df["total"].quantile([0.05, 0.25, 0.5, 0.75, 0.95])
```

### Measures of Shape

```python
# Skewness: 0 = symmetric, >0 = right tail, <0 = left tail
df["total"].skew()

# Kurtosis: 0 = normal, >0 = heavy tails, <0 = light tails
df["total"].kurtosis()
```

**Interpretation for BI:**
- High positive skew in count data (e.g., bike counts) is normal — most intervals have moderate traffic, a few have very high traffic
- High kurtosis means extreme values are more likely than a normal distribution would predict — important for capacity planning

---

## 8. Distributions & Probability

### Common distributions you'll encounter

| Distribution | Use case | Example |
|-------------|----------|---------|
| **Normal** | Means of large samples (CLT), measurement errors | Average daily bike count across many days |
| **Poisson** | Count of rare events per time interval | Number of accidents per month at a station |
| **Negative Binomial** | Overdispersed count data (variance > mean) | Bike counts when variance exceeds what Poisson predicts |
| **Log-normal** | Positive-only data with right skew | Individual trip durations, daily traffic volumes |
| **Uniform** | Equal probability across range | Random sampling, simulation |

### Checking if data is normally distributed

```python
import matplotlib.pyplot as plt
from scipy import stats

# Visual check — histogram with normal curve overlay
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(df["total"], bins=50, density=True, alpha=0.7)
axes[0].set_title("Histogram")

# Q-Q plot — points should follow the diagonal if normal
stats.probplot(df["total"].dropna(), plot=axes[1])
axes[1].set_title("Q-Q Plot")

plt.tight_layout()
plt.show()

# Statistical tests for normality
# Shapiro-Wilk (best for n < 5000)
stat, p = stats.shapiro(df["total"].sample(5000))
print(f"Shapiro-Wilk: p = {p:.4f}")

# D'Agostino-Pearson (works for larger samples)
stat, p = stats.normaltest(df["total"].dropna())
print(f"D'Agostino: p = {p:.4f}")

# p < 0.05 → reject normality
# Note: with large n, nearly everything is "significantly" non-normal.
# Use visual checks (histogram, Q-Q plot) alongside the test.
```

### Central Limit Theorem (CLT)

The most important concept for BI: **the mean of a large enough sample is approximately normally distributed**, regardless of the original distribution. This is why confidence intervals and t-tests work even for non-normal data.

```python
# Demonstration: daily means are approximately normal even if 15-min counts are skewed
daily_means = df.groupby(df.index.date)["total"].mean()
print(f"Skewness of raw data:    {df['total'].skew():.2f}")
print(f"Skewness of daily means: {daily_means.skew():.2f}")  # Much closer to 0
```

---

## 9. Correlation & Regression

### Correlation

Measures the **strength and direction** of a linear relationship between two variables. Does NOT imply causation.

| Method | Range | When to use |
|--------|-------|-------------|
| **Pearson** | -1 to +1 | Both variables roughly normal, linear relationship |
| **Spearman** | -1 to +1 | Ordinal data or non-linear monotonic relationships |
| **Kendall** | -1 to +1 | Small samples, many tied ranks |

```python
# Pearson correlation (default)
df[["total", "temperature", "precipitation"]].corr()

# Spearman (rank-based, robust to non-linearity)
df[["total", "temperature", "precipitation"]].corr(method="spearman")

# Single pair with p-value
r, p = stats.pearsonr(df["total"], df["temperature"])
print(f"Pearson r = {r:.3f}, p = {p:.4f}")

rho, p = stats.spearmanr(df["total"], df["temperature"])
print(f"Spearman ρ = {rho:.3f}, p = {p:.4f}")
```

**Interpreting correlation strength:**

| |r| | Strength |
|------|----------|
| 0.0 – 0.1 | Negligible |
| 0.1 – 0.3 | Weak |
| 0.3 – 0.5 | Moderate |
| 0.5 – 0.7 | Strong |
| 0.7 – 1.0 | Very strong |

**Watch out for:**
- **Spurious correlation**: two variables correlate because they share a common cause (e.g., bike counts and ice cream sales both rise with temperature)
- **Ecological fallacy**: correlation at group level doesn't imply correlation at individual level
- **Simpson's paradox**: a trend that appears in groups reverses when groups are combined

### Correlation heatmap

```python
import seaborn as sns

corr_matrix = df[["total", "temperature", "precipitation", "wind"]].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", center=0, fmt=".2f")
plt.title("Correlation Matrix")
plt.tight_layout()
plt.show()
```

### Simple Linear Regression

Models the relationship `y = β₀ + β₁x + ε`. Answers: "for every 1-unit increase in x, how much does y change on average?"

```python
from scipy import stats

# Quick regression with scipy
slope, intercept, r_value, p_value, std_err = stats.linregress(
    df["temperature"], df["total"]
)
print(f"y = {intercept:.1f} + {slope:.1f} * temperature")
print(f"R² = {r_value**2:.3f}")    # Proportion of variance explained
print(f"p  = {p_value:.4f}")

# Predict
df["predicted"] = intercept + slope * df["temperature"]
```

### Multiple Linear Regression

```python
import statsmodels.api as sm

# Prepare features (add constant for intercept)
X = df[["temperature", "precipitation", "wind_speed"]]
X = sm.add_constant(X)
y = df["total"]

# Fit
model = sm.OLS(y, X).fit()
print(model.summary())

# Key outputs to look at:
# - R² (adj.): how much variance is explained
# - coef: effect size per variable
# - P>|t|: significance of each variable (< 0.05)
# - F-statistic p-value: is the overall model significant?
```

**Interpreting the regression summary:**

| Metric | What it means |
|--------|---------------|
| **R² (adjusted)** | % of variance in y explained by the model. 0.3 = 30% explained. |
| **Coefficients** | "For every 1°C increase in temperature, bike count increases by [coef], holding other variables constant." |
| **p-value per coefficient** | < 0.05 means this variable has a statistically significant effect |
| **F-statistic** | Tests whether the model as a whole is significant |
| **Residuals** | Should be roughly normally distributed with no pattern (check with plots) |

### Regression diagnostics

```python
# Residual plot — should show no pattern
residuals = model.resid
fitted = model.fittedvalues

plt.scatter(fitted, residuals, alpha=0.3, s=5)
plt.axhline(y=0, color="red", linestyle="--")
plt.xlabel("Fitted values")
plt.ylabel("Residuals")
plt.title("Residual Plot")
plt.show()

# Check for multicollinearity (VIF)
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif = pd.DataFrame({
    "variable": X.columns[1:],  # Skip constant
    "VIF": [variance_inflation_factor(X.values, i+1) for i in range(X.shape[1]-1)]
})
print(vif)
# VIF > 5 → concerning, VIF > 10 → serious multicollinearity
```

---

## 10. Hypothesis Testing

### The logic of hypothesis testing

1. **H₀ (null hypothesis):** "There is no effect / no difference"
2. **H₁ (alternative hypothesis):** "There IS an effect / difference"
3. Choose significance level α (typically 0.05)
4. Compute test statistic → p-value
5. If p < α → reject H₀ (result is statistically significant)

**p-value** = probability of observing data this extreme *if H₀ were true*. It is NOT the probability that H₀ is true.

### Choosing the right test

| Question | Test | Code |
|----------|------|------|
| Is the mean different from a value? | One-sample t-test | `stats.ttest_1samp(data, popmean=X)` |
| Are two group means different? | Independent t-test | `stats.ttest_ind(group1, group2)` |
| Are paired measurements different? | Paired t-test | `stats.ttest_rel(before, after)` |
| Are >2 group means different? | One-way ANOVA | `stats.f_oneway(g1, g2, g3)` |
| Non-normal, 2 groups? | Mann-Whitney U | `stats.mannwhitneyu(g1, g2)` |
| Non-normal, >2 groups? | Kruskal-Wallis | `stats.kruskal(g1, g2, g3)` |
| Are two categorical variables related? | Chi-squared test | `stats.chi2_contingency(table)` |

### Examples

```python
# t-test: Is weekday cycling significantly different from weekend cycling?
weekday = df[df["weekday"] < 5]["total"]
weekend = df[df["weekday"] >= 5]["total"]

t_stat, p_value = stats.ttest_ind(weekday, weekend)
print(f"t = {t_stat:.2f}, p = {p_value:.4f}")
# p < 0.05 → weekday and weekend volumes are significantly different

# Mann-Whitney (non-parametric alternative — use when data is skewed)
u_stat, p_value = stats.mannwhitneyu(weekday, weekend, alternative="two-sided")
print(f"U = {u_stat:.0f}, p = {p_value:.4f}")

# ANOVA: Do seasonal means differ across all four seasons?
spring = df[df["month"].isin([3, 4, 5])]["total"]
summer = df[df["month"].isin([6, 7, 8])]["total"]
autumn = df[df["month"].isin([9, 10, 11])]["total"]
winter = df[df["month"].isin([12, 1, 2])]["total"]

f_stat, p_value = stats.f_oneway(spring, summer, autumn, winter)
print(f"F = {f_stat:.2f}, p = {p_value:.4f}")
# If significant, do post-hoc pairwise comparisons

# Chi-squared: Is the distribution of peak hours independent of season?
contingency = pd.crosstab(df["season"], df["is_peak"])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"χ² = {chi2:.2f}, p = {p:.4f}, dof = {dof}")
```

### Multiple comparisons problem

When you run many tests, some will be significant by chance. Correct for this:

```python
from statsmodels.stats.multitest import multipletests

# Suppose you ran 10 pairwise t-tests and got these p-values
p_values = [0.001, 0.013, 0.042, 0.067, 0.120, 0.340, 0.510, 0.780, 0.880, 0.950]

# Bonferroni correction (conservative)
rejected, corrected_p, _, _ = multipletests(p_values, method="bonferroni")
print("Bonferroni:", corrected_p)

# Benjamini-Hochberg (less conservative, controls false discovery rate)
rejected, corrected_p, _, _ = multipletests(p_values, method="fdr_bh")
print("BH:", corrected_p)
```

### Confidence Intervals

A 95% CI means: if we repeated the study 100 times, ~95 of the intervals would contain the true parameter.

```python
import numpy as np

data = df["total"].dropna()
mean = data.mean()
se = stats.sem(data)                          # Standard error of the mean
ci = stats.t.interval(0.95, df=len(data)-1, loc=mean, scale=se)
print(f"Mean: {mean:.1f}, 95% CI: [{ci[0]:.1f}, {ci[1]:.1f}]")

# Confidence interval for difference in means
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

d1 = DescrStatsW(weekday)
d2 = DescrStatsW(weekend)
cm = CompareMeans(d1, d2)
ci_diff = cm.tconfint_diff(alpha=0.05)
print(f"Difference in means 95% CI: [{ci_diff[0]:.1f}, {ci_diff[1]:.1f}]")
```

---

## 11. Effect Size & Practical Significance

Statistical significance (p < 0.05) only tells you the effect is unlikely due to chance. **Effect size** tells you if the effect actually matters.

With large datasets (like 15-min bike counts over years), almost everything will be "statistically significant." Effect size is what you should actually care about.

| Measure | Use case | Interpretation |
|---------|----------|----------------|
| **Cohen's d** | Difference between two means | 0.2 = small, 0.5 = medium, 0.8 = large |
| **R²** | Regression | % of variance explained |
| **η² (eta-squared)** | ANOVA | % of variance explained by group |
| **Cramér's V** | Chi-squared | Strength of association for categorical data |

```python
# Cohen's d: standardized difference between two means
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / pooled_std

d = cohens_d(weekday, weekend)
print(f"Cohen's d = {d:.3f}")
# |d| < 0.2 → negligible practical difference, even if p < 0.05

# Eta-squared from ANOVA
# η² = SS_between / SS_total
def eta_squared(groups):
    all_data = np.concatenate(groups)
    grand_mean = all_data.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
    ss_total = sum((all_data - grand_mean)**2)
    return ss_between / ss_total

eta2 = eta_squared([spring, summer, autumn, winter])
print(f"η² = {eta2:.3f}")  # 0.01=small, 0.06=medium, 0.14=large

# Cramér's V for chi-squared
def cramers_v(contingency_table):
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    k = min(contingency_table.shape) - 1
    return np.sqrt(chi2 / (n * k))

v = cramers_v(contingency)
print(f"Cramér's V = {v:.3f}")  # 0.1=small, 0.3=medium, 0.5=large
```

---

## 12. Resampling & Bootstrapping

When you're unsure about distributional assumptions, bootstrap gives you confidence intervals empirically.

```python
from scipy.stats import bootstrap

# Bootstrap 95% CI for the mean
data = (df["total"].dropna().values,)  # Must be tuple of arrays
result = bootstrap(data, np.mean, n_resamples=10000, confidence_level=0.95)
print(f"95% CI: [{result.confidence_interval.low:.1f}, {result.confidence_interval.high:.1f}]")

# Manual bootstrap (more flexible)
def bootstrap_ci(data, stat_func=np.mean, n_boot=10000, ci=0.95):
    boot_stats = []
    for _ in range(n_boot):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_stats.append(stat_func(sample))
    alpha = (1 - ci) / 2
    return np.percentile(boot_stats, [alpha * 100, (1 - alpha) * 100])

ci = bootstrap_ci(df["total"].dropna().values, stat_func=np.median)
print(f"Bootstrap 95% CI for median: [{ci[0]:.1f}, {ci[1]:.1f}]")
```

---

## 13. Outlier Detection

### Statistical methods

```python
# Z-score method (assumes roughly normal data)
z_scores = np.abs(stats.zscore(df["total"].dropna()))
outliers_z = df[z_scores > 3]  # More than 3 std from mean
print(f"Z-score outliers: {len(outliers_z)}")

# IQR method (robust, works for skewed data)
Q1 = df["total"].quantile(0.25)
Q3 = df["total"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers_iqr = df[(df["total"] < lower) | (df["total"] > upper)]
print(f"IQR outliers: {len(outliers_iqr)}")

# Modified Z-score (uses median — very robust)
median = df["total"].median()
mad = stats.median_abs_deviation(df["total"].dropna())
modified_z = 0.6745 * (df["total"] - median) / mad
outliers_mz = df[np.abs(modified_z) > 3.5]
```

### Handling outliers

```python
# Option 1: Remove
df_clean = df[(df["total"] >= lower) & (df["total"] <= upper)]

# Option 2: Cap / Winsorize (replace extremes with boundary values)
df["total_capped"] = df["total"].clip(lower=lower, upper=upper)

# Option 3: Flag (keep but mark)
df["is_outlier"] = (df["total"] < lower) | (df["total"] > upper)

# Option 4: Log transform (compresses right tail)
df["total_log"] = np.log1p(df["total"])
```

**BI guidance:** Don't automatically remove outliers. A bike count outlier might be a real event (festival, protest, construction detour). Investigate before removing.

---

## 14. Feature Engineering

Features specific to time-series BI projects:

```python
# Calendar features
df["is_weekend"] = df["weekday"] >= 5
df["is_holiday"] = df.index.isin(holidays_list)  # You'd define this list
df["season"] = df["month"].map({
    12: "winter", 1: "winter", 2: "winter",
    3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn",
})

# Cyclical encoding (so Dec and Jan are "close")
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

# Lag features (previous time step)
df["total_lag_1h"] = df["total"].shift(4)    # 4 × 15min = 1 hour
df["total_lag_1d"] = df["total"].shift(96)   # 96 × 15min = 1 day
df["total_lag_1w"] = df["total"].shift(672)  # 1 week

# Rolling statistics
df["rolling_mean_24h"] = df["total"].rolling(96).mean()
df["rolling_std_24h"] = df["total"].rolling(96).std()

# Difference from typical (ratio to rolling average)
df["relative_volume"] = df["total"] / df["rolling_mean_24h"]

# Weather interaction features
df["rain_flag"] = (df["precipitation"] > 0).astype(int)
df["cold_flag"] = (df["temperature"] < 5).astype(int)
df["bad_weather"] = df["rain_flag"] | df["cold_flag"]

# Directional imbalance
df["direction_ratio"] = df["velo_in"] / (df["velo_in"] + df["velo_out"] + 1e-6)
```

---

## 15. Visualization for BI

### Core chart types and when to use them

| Chart | Use case | Pandas/Seaborn |
|-------|----------|----------------|
| **Line chart** | Trends over time | `df.plot(kind="line")` |
| **Bar chart** | Compare categories | `df.plot(kind="bar")` |
| **Histogram** | Distribution of one variable | `df["x"].hist(bins=50)` |
| **Box plot** | Distribution + outliers per group | `sns.boxplot(x="group", y="value")` |
| **Violin plot** | Full distribution shape per group | `sns.violinplot(x="group", y="value")` |
| **Scatter plot** | Relationship between 2 variables | `plt.scatter(x, y)` |
| **Heatmap** | Matrix of values (correlation, pivot) | `sns.heatmap(matrix)` |

### Practical examples

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set a clean style
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120

# --- Line chart: monthly trend by year ---
monthly = df.groupby([df.index.year, df.index.month])["total"].sum().unstack(level=0)
monthly.plot(figsize=(12, 5))
plt.xlabel("Month")
plt.ylabel("Total bike count")
plt.title("Monthly bike volume by year")
plt.legend(title="Year")
plt.tight_layout()
plt.show()

# --- Heatmap: hour × weekday average ---
heatmap_data = df.pivot_table(values="total", index="hour", columns="weekday", aggfunc="mean")
heatmap_data.columns = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

plt.figure(figsize=(8, 10))
sns.heatmap(heatmap_data, cmap="YlOrRd", annot=True, fmt=".0f")
plt.title("Average bike volume by hour and weekday")
plt.ylabel("Hour of day")
plt.tight_layout()
plt.show()

# --- Box plot: volume distribution by season ---
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="season", y="total",
            order=["spring", "summer", "autumn", "winter"])
plt.title("Bike volume distribution by season")
plt.tight_layout()
plt.show()

# --- Scatter + regression: temperature vs volume ---
plt.figure(figsize=(8, 5))
sns.regplot(data=df.sample(5000), x="temperature", y="total",
            scatter_kws={"alpha": 0.2, "s": 10}, line_kws={"color": "red"})
plt.title("Temperature vs bike volume")
plt.tight_layout()
plt.show()

# --- Small multiples: one line chart per station ---
top_stations = df.groupby("station")["total"].sum().nlargest(6).index
subset = df[df["station"].isin(top_stations)]
daily = subset.groupby([subset.index.date, "station"])["total"].sum().reset_index()
daily.columns = ["date", "station", "total"]
daily["date"] = pd.to_datetime(daily["date"])

g = sns.FacetGrid(daily, col="station", col_wrap=3, sharey=False, height=3)
g.map_dataframe(sns.lineplot, x="date", y="total", linewidth=0.5)
g.set_titles("{col_name}")
g.tight_layout()
plt.show()
```

### Formatting tips for presentations

```python
# Clean, presentation-ready chart template
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(monthly_totals.index, monthly_totals.values, color="#2C73D2", linewidth=2)

ax.set_title("Veloverkehr Zürich — Monatliche Entwicklung", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Anzahl Velos", fontsize=11)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.tick_params(labelsize=10)

plt.tight_layout()
plt.savefig("chart.png", dpi=200, bbox_inches="tight")
plt.show()
```

---

## 16. Common Pitfalls

### Statistical pitfalls

| Pitfall | What goes wrong | How to avoid |
|---------|----------------|--------------|
| **Confusing correlation with causation** | "Temperature causes cycling" — maybe, but maybe both are caused by season | Always consider confounders. State "is associated with," not "causes" |
| **p-hacking** | Testing many hypotheses until one is significant | Pre-register your questions (like the CPA KAQs). Apply multiple-testing correction |
| **Large-N significance** | With millions of rows, even trivial effects are "significant" | Always report effect size alongside p-values |
| **Survivorship bias** | Analyzing only stations that have data, ignoring those removed | Document which stations were excluded and why |
| **Simpson's paradox** | A trend reverses when data is split by a lurking variable | Always check if results hold within subgroups |
| **Ecological fallacy** | "Stations with more rain have fewer bikes" ≠ "Rain reduces cycling" | Be precise about what unit your conclusion applies to |

### Data cleaning pitfalls

| Pitfall | What goes wrong | How to avoid |
|---------|----------------|--------------|
| **Dropping NaN carelessly** | Losing valid rows because one unimportant column is null | Only drop NaN in columns you actually need |
| **Fill-forward across gaps** | Filling a 3-month data gap with the last known value | Limit fill: `fillna(method="ffill", limit=4)` |
| **Timezone issues** | Joining weather (UTC) with bike counts (local time) | Always explicitly handle timezones: `df.index = df.index.tz_localize("Europe/Zurich")` |
| **Integer overflow in aggregation** | Summing int32 columns that overflow | Use `df["x"].astype("int64")` before large sums |
| **Merging on floats** | `0.1 + 0.2 != 0.3` in floating point | Round before merging, or merge on strings/integers |

### Visualization pitfalls

| Pitfall | How to avoid |
|---------|--------------|
| Truncated y-axis exaggerating differences | Start y-axis at 0 for bar charts. For line charts, make the range clear |
| Too many colors / categories | Limit to 5-7 colors. Group small categories into "Other" |
| Pie charts for comparing similar values | Use bar charts instead — humans are bad at comparing angles |
| Dual y-axes | Almost always misleading. Use two separate panels instead |
| Not labeling units | Always include units (bikes/hour, °C, mm precipitation) |
