# bina — Veloverkehr Zürich (BI-Projekt, Semester 2)

Exploratory data analysis on bicycle traffic in Zürich. Investigates
temporal patterns and growth hotspots (2020–2025) and produces a
station-level priority ranking for capacity-expansion decisions.

## View the notebooks

The notebooks are committed **with their outputs rendered**, so you can read
them directly on GitHub — no setup needed:

| # | Notebook | Topic |
|---|----------|-------|
| FF1 | [FF1_absolutes_aufkommen.ipynb](notebooks/FF1/FF1_absolutes_aufkommen.ipynb) | absolutes Veloaufkommen |
| FF2 | [03_ff2_growth_hotspots.ipynb](notebooks/FF2/03_ff2_growth_hotspots.ipynb) | growth hotspots + priority ranking |
| FF3 | [04_ff3_Wettersensitivität_v2.ipynb](notebooks/FF3/04_ff3_Wettersensitivität_v2.ipynb) | Wettersensitivität |

If a notebook fails to preview on github.com (its renderer occasionally times
out or strips interactive maps), open it via
[nbviewer](https://nbviewer.org/github/rolivischi2/bina/tree/master/notebooks/)
instead.

Each research question lives in its own subfolder and cleans its own data inline.

## Run it yourself

```bash
git clone https://github.com/rolivischi2/bina.git && cd bina

conda env create -f environment.yml && conda activate bina
python -m ipykernel install --user --name bina --display-name "Python (bina)"

unzip data/data_bundle.zip -d data/      # hydrate data/ (gitignored otherwise)

jupyter nbconvert --to notebook --execute --inplace notebooks/FF2/03_ff2_growth_hotspots.ipynb
```

Or open the repo in VSCode (Python + Jupyter extensions), pick the **Python (bina)**
kernel, and `Run All`. The notebooks run in any order. If a package is missing later,
sync the env with `conda env update -f environment.yml --prune`.

## Contributing

- `master` is the integration branch; branch off as `<area>/<short-topic>`
  (e.g. `ff2/refine-priority-score`).
- **Restart kernel and run all cells before committing** so outputs and
  execution counts are deterministic.
- Edit one notebook per branch — cell-metadata merge conflicts are painful.
- Don't commit: `data/` (raw files are gitignored; `data_bundle.zip` is the
  tracked exception), `*.html` under `notebooks/`, local settings, secrets.
- Commit messages: `<area>: <imperative summary>`.
