# `data/` — local-only datasets

The raw CSV/JSON/parquet files in this folder are **gitignored** and not
committed. The **two exceptions tracked in git** are this `NOTE.md` and the
compressed bundle `data_bundle.zip` — the bundle ships the raw data so a fresh
clone can hydrate this folder.

## How it gets populated

The bundle lives right here:

```
data/data_bundle.zip   (~97 MB, tracked in git)
```

**Unzip it in place** after cloning:

```bash
unzip data/data_bundle.zip -d data/
```

Windows Explorer (right-click → Extract All into `data/`), PowerShell
(`Expand-Archive data/data_bundle.zip data/`), and macOS double-click all
handle `.zip` natively too.

## What ends up here

After extraction, you'll see roughly:

```
data/
├── NOTE.md                                                (this file)
├── 2020_verkehrszaehlungen_werte_fussgaenger_velo.csv     ← FF2 (per-year, 15-min)
├── ...                                                    (one CSV per year, 2020-2025)
├── 2025_verkehrszaehlungen_werte_fussgaenger_velo.csv
├── verkehrszaehlungen_werte_fussgaenger_velo_alle_jahre.parquet  ← FF3
├── standorte_velo_fuss.json                               ← FF2 (id1 → bezeichnung)
├── taz.view_eco_standorte.csv                             ← FF3
├── ugz_ogd_meteo_d1_2020.csv                              ← FF3 (Tagesmeteodaten)
├── ...                                                    (one CSV per year)
└── ugz_ogd_meteo_d1_2025.csv
```

Each FF notebook cleans its own data inline (no shared cleaning step anymore).
FF1 pulls its own per-year CSVs from a separate GitHub repo, so it does not
depend on the files above.

## Refreshing from upstream

If new measurement data is published on
[data.stadt-zuerich.ch](https://data.stadt-zuerich.ch) (typically yearly),
download the updated files and regenerate `data/data_bundle.zip`.

## Don't commit the loose data files

`.gitignore` rules out `*.csv`, `*.json`, `*.geojson`, `*.xlsx`, `*.parquet`
and `clean/` to prevent accidentally pushing the raw data. The compressed
`data_bundle.zip` is **not** ignored and is the only data artifact meant to be
tracked — to ship updated data, regenerate that bundle rather than committing
loose files.
