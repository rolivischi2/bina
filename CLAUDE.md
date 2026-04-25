# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

University semester 2 BI-Projekt (Business Intelligence & Analytics) analyzing bicycle traffic in Zürich. Exploratory data analysis with Python, investigating temporal patterns, growth hotspots, and demand ranking.

## Environment

- **Conda env:** `bina` (defined in `environment.yml`)
- **Activate:** `conda activate bina`
- **Run notebooks:** `jupyter lab` or `jupyter notebook`
- **Key packages:** pandas, numpy, matplotlib, seaborn, folium, scipy, plotly, pyproj

## Data Sources

All CSVs are downloaded into `data/` (gitignored). Notebook `01_data_acquisition.ipynb` handles downloads.

| Dataset | Source | Format |
|---------|--------|--------|
| Zürich velo counts (15-min) | data.stadt-zuerich.ch | CSV per year |

## Research Questions (Forschungsfragen)

- FF1: Temporal patterns & demand ranking (time-of-day, weekday, season)
- FF2: Growth hotspots (which stations show strongest growth trends 2020-2025?)

## Repo Structure

```
bina/
├── CLAUDE.md              Project instructions for Claude
├── environment.yml        Conda environment definition
├── data/                  Raw + cleaned datasets (gitignored)
│   └── clean/             Cleaned parquet/CSV outputs from notebook 02
├── notebooks/             Analysis notebooks
│   ├── 01_data_acquisition.ipynb    Shared: download raw CSVs
│   ├── 02_data_cleaning.ipynb       Shared: clean + export parquet
│   └── FF2/               FF2 specific: growth hotspots
│       ├── 03_ff2_growth_hotspots.ipynb
│       ├── 03_ff2_growth_hotspots.html   nbconvert export
│       └── ff2_zuerich_map.html          folium map output
└── docs/                  Guidelines, reference PDFs, DOCX briefs,
                           cheatsheets, non-technical guides
```

Shared preparation notebooks (01, 02) live directly under `notebooks/`.
Each research question gets its own subfolder (`FF2/`, future `FF1/`, `FF3/`, ...).
Notebooks reference data with relative paths: `../data/...` from `notebooks/`,
`../../data/...` from `notebooks/FF2/`.
