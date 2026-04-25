# Veloverkehr-Analyse Zürich — Manual

End-to-end guide for the data cleaning and FF2 (growth hotspots) analysis. Read this first if you're picking the project up.

---

## 1. Environment

Two paths to a working interpreter:

### 1a. Conda (preferred, matches `environment.yml`)
```bash
conda env create -f environment.yml
conda activate bina
python -m ipykernel install --user --name bina --display-name "Python (bina)"
```

### 1b. Plain pip (works without conda)
The notebooks were validated against the user-site CPython 3.12 install at
`C:\Users\visch\AppData\Local\Programs\Python\Python312\python.exe`. Install
deps directly into that interpreter:
```bash
"C:/Users/visch/AppData/Local/Programs/Python/Python312/python.exe" -m pip install \
    pandas numpy matplotlib seaborn scipy folium openpyxl requests pyarrow plotly pyproj nbconvert
```

The notebooks pin to a kernel named `bina` (registered at
`%APPDATA%\jupyter\kernels\bina\kernel.json`). If that kernel points to the
wrong interpreter, VSCode will hang on **"Connecting to kernel…"** — the
process starts but every `import pandas` fails. Re-run the
`ipykernel install` line above to repoint it.

### Sanity check
```bash
"C:/Users/visch/AppData/Local/Programs/Python/Python312/python.exe" -c \
    "import pandas, numpy, matplotlib, seaborn, scipy, plotly, folium, pyproj; print('ok')"
```

---

## 2. Running notebooks

### In VSCode
Open the `.ipynb`, top-right kernel picker → **Python (bina)**, run cells.
First-time kernel start can take ~25 s while the data-science stack imports.

### From the CLI (no VSCode needed)
Execute end-to-end and write outputs back into the file:
```bash
"<python.exe>" -m jupyter nbconvert --to notebook --execute --inplace 02_data_cleaning.ipynb
"<python.exe>" -m jupyter nbconvert --to notebook --execute --inplace 03_ff2_growth_hotspots.ipynb
```

Useful flags:
- `--allow-errors` — keep going past failing cells, capture the traceback in the cell output
- `--ExecutePreprocessor.timeout=600` — per-cell timeout (default 30 s)
- `--output _scratch.ipynb` — write to a side file instead of overwriting

### Generate a shareable HTML report
```bash
"<python.exe>" -m jupyter nbconvert --to html 03_ff2_growth_hotspots.ipynb
```
Produces `03_ff2_growth_hotspots.html` (~1 MB) — open in any browser. The
Folium map and matplotlib charts render natively, no kernel needed.

### Inspect errors after a CLI run
```bash
python -c "import json; nb=json.load(open('03_ff2_growth_hotspots.ipynb', encoding='utf-8')); \
[print(f'Cell {i}:', o.get('ename'), o.get('evalue')) \
 for i,c in enumerate(nb['cells']) if c['cell_type']=='code' \
 for o in c.get('outputs',[]) if o.get('output_type')=='error']"
```

---

## 3. Notebook 02 — Data Cleaning

**Input:** raw CSVs in `data/20*_verkehrszaehlungen_werte_fussgaenger_velo.csv`
(downloaded by [01_data_acquisition.ipynb](01_data_acquisition.ipynb)).
**Outputs:** cleaned 15-minute parquet + station metadata in `data/clean/`.

Each step calls `log_step(...)` so every transformation is recorded in
`cleaning_log` and printed inline.

### Step 1.1 — Load & rename
Concatenates per-year CSVs into one DataFrame. Renames the cryptic source
columns to readable names (`FK_STANDORT → station_id`, `DATUM → datetime`,
`OST/NORD → easting/northing`, etc.).

### Step 1.2 — Drop pedestrian-only stations
The source file mixes `velo_*` and `fuss_*` columns. We:
- Identify which stations ever recorded velo data
- Drop pedestrian-only stations entirely
- Drop the `fuss_in` / `fuss_out` columns
This gets us a velo-focused dataset for both research questions.

### Step 1.3 — Datetime + duplicates
Parses `datetime` with explicit format (`%Y-%m-%dT%H:%M`), drops
`(station_id, datetime)` duplicates, and pre-computes `year / month / hour /
weekday` columns so downstream notebooks don't repeat the work.

### Step 1.4 — Uni- vs. bi-directional + total
Some stations only count one direction (`velo_out` is always null), others
count both. Naïvely summing `in + out` would under-count uni-directional
stations. We:
- Classify each station based on whether `velo_out` ever has a value
- For bi-directional: `velo_total = velo_in + velo_out`
- For uni-directional: `velo_total = velo_in`
- Store the classification as `is_bidirectional` for transparency

### Step 1.5 — Sensor failure detection
Long runs of zeros (>6 hours, i.e. >24 fifteen-minute intervals) are almost
certainly sensor outages, not real "no traffic" periods. We flag these as
`sensor_failure = True` and overwrite the affected `velo_in / velo_out /
velo_total` with NaN. Without this, FF2 trends would be skewed downward by
broken sensors.

### Step 1.6 — Range validation
Negative counts are physically impossible. Set them to NaN, then recompute
`velo_total`. Extreme values (>99.9th percentile) are flagged but kept —
real events (Critical Mass, races) can produce legitimate spikes.

### Step 1.7 — Station consistency for FF2 (critical)
The Zürich network changed substantially: many stations were
decommissioned, others installed in 2022/2023. A naïve trend over all
stations would mostly reflect *which stations existed when*, not actual
behaviour change.

We compute coverage per `(station_id, year)` and require ≥60 % of the
expected ~35,064 fifteen-minute intervals. Two windows are evaluated:
- **Full span** 2020–2024 — strict, fewer stations, longest trend
- **Recent span** 2022–2024 — more stations, shorter but practical
The recent set is stored as `is_consistent` on every row.

### Step 1.8 — Missing-data report
Daily NaN-rate plot over the full date range — quick visual sanity check
that no large gaps remain after cleaning.

### Outputs (`data/clean/`)
| File | Contents |
|------|----------|
| `velo_15min_clean.parquet` | full 15-min dataset, columns: `station_id, datetime, velo_in, velo_out, velo_total, easting, northing, year, month, hour, weekday, is_bidirectional, is_consistent, sensor_failure` |
| `station_metadata.csv` | per-station: coords, direction type, consistency flag, first/last date, valid-row count |

The final cell runs assertions (no negatives, parsed datetimes, no
duplicates, ≥5 consistent stations) — the notebook fails loudly if any
invariant is violated.

---

## 4. Notebook 03 — FF2 Growth Hotspots

**Question:** which stations show the strongest growth trend 2020–2024,
and which would double their volume within 5 years if the trend holds?

**Inputs:** `velo_15min_clean.parquet` + `station_metadata.csv` from NB02.
**Outputs:** `data/clean/ff2_growth_trends.csv` and `ff2_yearly_totals.csv`.

### Step 1 — Load
Read parquet + metadata.

### Step 2 — Filter to consistent stations
Keep only `is_consistent == True` (the 2022–2024 set from NB02).

### Step 3 — Drop sensor failures
Remove rows flagged in NB02 — they would deflate yearly totals.

### Step 4 — Coverage per (station, year)
Compute % of the ~35,064 expected intervals that are present after
cleaning. Used downstream to decide whether a year is usable.

### Step 5 — Annualisation of partial years
2025 is incomplete. Naïve sum vs full-year sum would dwarf the real
trend. We annualise: `velo_annual = raw_sum / (coverage_pct / 100)`,
but only if coverage ≥ 25 %. Below that, set `velo_annual = NaN`.

### Step 6 — Seasonality check
The naïve annualisation assumes uniform monthly distribution. Velo
traffic is not uniform (summer ≫ winter). We compute the seasonal
profile from full years (2020–2024) and check what *share of the
typical year* the available 2025 months represent. If it deviates
materially from a uniform allocation, 2025 is excluded from the
regression (`EXCLUDE_2025 = True`).

### Step 7 — Final yearly totals
Apply the 2025 decision and drop rows with `velo_annual == NaN`.

### Step 8 — YoY growth rates
Per-station year-over-year `% change`, pivoted into a station × year
matrix for inspection.

### Step 9 — Linear regression per station
For each station, fit `velo_annual ~ year` via `scipy.stats.linregress`.
Returns `slope`, `intercept`, `r_squared`, `p_value`, `n_years`, and
the first/last yearly totals. Stations with <3 data points get NaN.
Also computes `slope_pct = slope / mean_annual × 100` so trends are
comparable across stations of different sizes.

### Step 10 — CAGR + doubling time + trend quality
- `cagr = (last/first)^(1/n) − 1`
- `doubling_years = ln(2) / ln(1+cagr)` (for positive CAGR, else `inf`)
- `doubles_in_5y = doubling_years ≤ 5`
- `trend_quality ∈ {strong, moderate, weak, insufficient_data}` based on
  p-value and R². **Computed here so later cells can use it.**

### Step 11 — Trend lines + 5-year extrapolation (matplotlib)
Per-station subplot grid: actual annual totals as scatter, fitted trend
line, dashed extrapolation, and a horizontal "doubling threshold" line.

### Step 12 — Growth ranking (matplotlib bars)
Two horizontal bar charts side-by-side: absolute slope and CAGR. Green
for growth, red for shrinkage.

### Step 13 — Significance filter
Re-applies `classify_trend` (idempotent) and prints the **growth
hotspots** — stations with strong/moderate trend quality and positive
slope.

### Step 14 — CPA decision basis
Concentration analysis: is the total growth concentrated on few
stations (Top-3 share > 60 %) or evenly distributed? Maps the result
to one of the two decision branches in the project's CPA framework.

### Step 15 — Zürich map (Folium, with radar emanation)
Each station appears as **three concentric circles** with decreasing
opacity (0.35 → 0.18 → 0.07) and a small white center marker:
- **Color** — green for growing stations, red for shrinking
- **Radius (in metres)** — proportional to absolute slope, scaled
  against the strongest trend in the set
- **Center marker** — click for full statistics popup (slope, CAGR,
  R², doubling time, etc.)

Coordinates are converted from Swiss LV95 (EPSG:2056) to WGS84 with
`pyproj.Transformer`. Zoom on the map; circles are geographic so they
scale with the basemap, no recalculation needed.

**Rendering in VSCode:** the cell writes the map to
`ff2_zuerich_map.html` next to the notebook and displays it via
`IPython.display.IFrame`. This bypasses VSCode's notebook-trust
sandbox, which otherwise blocks folium's default `<iframe srcdoc="…">`
output and shows only the *"Make this Notebook Trusted"* fallback text.
The standalone `ff2_zuerich_map.html` can also be double-clicked to
open the map full-screen in any browser.

When generating the HTML report (`nbconvert --to html`), ship
`ff2_zuerich_map.html` alongside it — the exported HTML references it
via relative path.

### Step 16 — Export
| File | Contents |
|------|----------|
| `data/clean/ff2_growth_trends.csv` | one row per station: slope, slope_pct, intercept, r², p-value, CAGR, doubling years, trend_quality, n_years, mean/first/last annual totals |
| `data/clean/ff2_yearly_totals.csv` | one row per (station, year): raw sum, annualised total, coverage % |

These feed downstream notebooks (FF synthesis / prioritisation).

---

## 5. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| VSCode stuck on "Connecting to kernel…" | `bina` kernel.json points to interpreter without pandas/numpy/etc | Run the pip install in §1b, or re-register kernel from the right env |
| `ModuleNotFoundError: No module named 'pandas'` (or numpy/scipy/…) | Same as above | Same |
| Folium map shows only *"Make this Notebook Trusted"* | VSCode has no Trust-Notebook button; folium's srcdoc iframe is sandboxed | The map cell already saves `ff2_zuerich_map.html` and renders it via `IFrame` — re-run the cell; fall back to double-clicking the saved HTML if VSCode still blocks it |
| `ValueError: 'trend_quality' not a column` (cell ~Step 12) | Cells run out of order; trend_quality is built in Step 10 | Use **Run All**, or run cells top-to-bottom |
| `groupby.apply` deprecation warning | Non-fatal in pandas ≥2.2 | Ignore, or pass `include_groups=False` |
| `ipynb` won't open / VSCode says corrupted | Editor saved while kernel was writing outputs | Re-execute via `nbconvert --inplace` to rewrite a clean file |

---

## 6. File map

```
bina/
├── 01_data_acquisition.ipynb     # downloads raw Zürich CSVs into data/
├── 02_data_cleaning.ipynb        # → data/clean/velo_15min_clean.parquet
│                                 #   data/clean/station_metadata.csv
├── 03_ff2_growth_hotspots.ipynb  # → data/clean/ff2_growth_trends.csv
│                                 #   data/clean/ff2_yearly_totals.csv
│                                 #   ff2_zuerich_map.html  (standalone map)
├── 03_ff2_growth_hotspots.html   # generated, shareable report (gitignore-able)
├── ff2_zuerich_map.html          # standalone map; VSCode + HTML-export need this
├── environment.yml               # conda spec
├── CLAUDE.md                     # AI-assistant context for this repo
└── MANUAL.md                     # this file
```

Run order: **01 → 02 → 03**. Each subsequent notebook only consumes the
cleaned outputs of the previous one — no need to keep raw CSVs around
once `data/clean/` is populated.