# `data/` — local-only datasets

This folder is **gitignored**. It holds the raw and cleaned CSVs/JSON/parquet
files that every notebook reads. Nothing in here is committed to git, but the
folder itself is tracked via this NOTE so a fresh clone has a place to put the
files.

## How it gets populated

The repo ships a compressed dataset bundle at the **repo root**:

```
data_bundle.zip   (~93 MB, tracked in git)
```

Run the setup script once after cloning to extract it into this folder:

```bash
# macOS / Linux / Git Bash
./setup.sh

# Windows PowerShell
.\setup.ps1
```

Both wrappers call `python scripts/setup_data.py`, which is idempotent — if
`data/` is already populated it does nothing. Pass `--force` to re-extract.

Manual fallback: just unzip `data_bundle.zip` into this folder. Windows
Explorer (right-click → Extract All), PowerShell (`Expand-Archive`), and
macOS double-click all handle `.zip` natively.

## What ends up here

After setup, you'll see roughly:

```
data/
├── NOTE.md                                                (this file)
├── 2020_verkehrszaehlungen_werte_fussgaenger_velo.csv     ← FF1, NB02
├── 2021_verkehrszaehlungen_werte_fussgaenger_velo.csv
├── ...                                                    (one CSV per year, 2020-2025)
├── 2025_verkehrszaehlungen_werte_fussgaenger_velo.csv
├── verkehrszaehlungen_werte_fussgaenger_velo_alle_jahre.parquet  ← FF3
├── standorte_velo_fuss.json                               ← FF2 (id1 -> bezeichnung)
├── taz.view_eco_standorte.csv                             ← FF3
├── ugz_ogd_meteo_d1_2020.csv                              ← FF3 (Tagesmeteodaten)
├── ...                                                    (one CSV per year)
├── ugz_ogd_meteo_d1_2025.csv
└── clean/                                                 ← outputs of NB02
    ├── velo_15min_clean.parquet                           ← FF2
    ├── station_metadata.csv                               ← FF2, FF3
    ├── ff2_growth_trends.csv                              ← FF2 (priority score export)
    └── ff2_yearly_totals.csv
```

## Refreshing from upstream

If new measurement data is published on
[data.stadt-zuerich.ch](https://data.stadt-zuerich.ch) (typically yearly), run
[notebooks/01_data_acquisition.ipynb](../notebooks/01_data_acquisition.ipynb)
end-to-end. It re-downloads every file in this folder from the canonical
sources. Then re-run [notebooks/02_data_cleaning.ipynb](../notebooks/02_data_cleaning.ipynb)
to refresh `clean/`.

## Don't commit anything from here

`.gitignore` rules out `*.csv`, `*.json`, `*.geojson`, `*.xlsx`, `*.parquet`
and `clean/` to prevent accidentally pushing the raw data. If you want to
ship a new dataset bundle, regenerate `data_bundle.zip` at the repo root
instead.
