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

## Notebook Structure

Notebooks are numbered sequentially: `01_data_acquisition`, `02_data_cleaning`, `03_ff2_growth_hotspots` etc.
