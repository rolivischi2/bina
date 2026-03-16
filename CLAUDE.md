# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

University semester 2 BI-Projekt (Business Intelligence & Analytics) analyzing bicycle traffic in Swiss cities (Zürich, Basel, St. Gallen). Exploratory data analysis with Python, investigating temporal patterns, weather correlation, COVID impact, and inter-city differences.

## Environment

- **Conda env:** `bina` (defined in `environment.yml`)
- **Activate:** `conda activate bina`
- **Run notebooks:** `jupyter lab` or `jupyter notebook`
- **Key packages:** pandas, numpy, matplotlib, seaborn, folium, scipy

## Data Sources

All CSVs are downloaded into `data/` (gitignored). Notebook `01_data_acquisition.ipynb` handles downloads.

| Dataset | Source | Format |
|---------|--------|--------|
| Zürich velo counts (15-min) | data.stadt-zuerich.ch | CSV per year |
| Basel velo counts (hourly) | data-bs.ch | CSV (semicolon-delimited) |
| St. Gallen velo (daily) | daten.stadt.sg.ch | CSV (semicolon-delimited) |
| MeteoSwiss weather (hourly, station SMA/Fluntern) | data.geo.admin.ch STAC API | CSV |

## Research Questions (Forschungsfragen)

- FF1: Temporal patterns (time-of-day, weekday, season)
- FF2: Weather influence (temperature, precipitation, wind)
- FF3: COVID-19 impact on cycling
- FF4: Inter-city comparison (ZH vs BS vs SG)

## Notebook Structure

Notebooks are numbered sequentially: `01_data_acquisition`, `02_...` etc.
