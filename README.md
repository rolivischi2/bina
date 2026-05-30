# bina — Veloverkehr Zürich (BI-Projekt, Semester 2)

Exploratory data analysis on bicycle traffic in Zürich. Investigates
temporal patterns and growth hotspots (2020–2025) and produces a
station-level priority ranking for capacity-expansion decisions.

---

## Repo layout

```
bina/
├── README.md             (you are here)
├── environment.yml       Conda env definition
├── data/
│   └── data_bundle.zip   compressed dataset bundle (~97 MB, tracked in git)
│                         — unzip in place to hydrate data/ (gitignored otherwise)
└── notebooks/
    ├── FF1/              FF1: absolutes Veloaufkommen
    ├── FF2/              FF2: growth hotspots (incl. data cleaning)
    └── FF3/              FF3: Wettersensitivität
```

Each research question lives in its own subfolder under `notebooks/` and cleans
its own data inline. The raw datasets ship compressed as `data/data_bundle.zip`;
unzip it in place before running any notebook.

---

## 1. One-time setup

### 1.1 Clone the repo

```bash
git clone https://github.com/rolivischi2/bina.git
cd bina
```

### 1.2 Create the conda environment

The environment is defined in [environment.yml](environment.yml).

```bash
conda env create -f environment.yml
conda activate bina
```

If the env already exists and is missing a package, sync it:

```bash
conda env update -f environment.yml --prune
```

### 1.3 Register the kernel for Jupyter / VSCode

```bash
python -m ipykernel install --user --name bina --display-name "Python (bina)"
```

This makes a kernel called **Python (bina)** available to any Jupyter
client on this machine.

### 1.4 Hydrate `data/`

The repo ships a compressed bundle (`data/data_bundle.zip`, ~97 MB) with all
raw datasets needed by the notebooks. **Unzip it in place** into `data/`:

```bash
unzip data/data_bundle.zip -d data/
```

Windows Explorer (right-click → Extract All into `data/`), PowerShell
(`Expand-Archive data/data_bundle.zip data/`), and macOS double-click all
work natively too.

> The bundle stays tracked in git (only the loose `*.csv/json/parquet` it
> contains are gitignored), so a fresh clone already has it — you just extract.

To refresh from the upstream Zürich open-data portal after a new year of
measurements is published, download the updated CSV/parquet files and
regenerate `data/data_bundle.zip`.

### 1.5 Sanity check

```bash
python -c "import pandas, numpy, matplotlib, seaborn, scipy, folium, pyproj; print('ok')"
```

---

## 2. Running notebooks in VSCode

1. Install the **Python** and **Jupyter** extensions (Microsoft).
2. `File → Open Folder…` → pick the cloned `bina/` repo.
3. Open a notebook, e.g. [notebooks/FF2/03_ff2_growth_hotspots.ipynb](notebooks/FF2/03_ff2_growth_hotspots.ipynb).
4. Top-right of the notebook view, click the kernel picker and choose
   **Python (bina)**. First-time kernel start takes ~25 s while pandas /
   matplotlib / folium load.
5. `Run All` (or step through with `Shift+Enter`).

### Order to run

First **unzip `data/data_bundle.zip`** (see 1.4) to hydrate `data/`. Then run
any notebook below in **any order** — each cleans its own data inline.

| # | Notebook | Role |
|---|----------|------|
| FF1 | `notebooks/FF1/FF1_absolutes_aufkommen.ipynb` | standalone — cleans + analyses its own data |
| FF2 | `notebooks/FF2/03_ff2_growth_hotspots.ipynb` | standalone — cleaning + growth analysis in one notebook |
| FF3 | `notebooks/FF3/04_ff3_Wettersensitivität_v2.ipynb` | standalone — weather-sensitivity analysis |

### Running from the CLI

```bash
conda activate bina
unzip data/data_bundle.zip -d data/   # once, to hydrate data/
jupyter nbconvert --to notebook --execute --inplace notebooks/FF2/03_ff2_growth_hotspots.ipynb
```

### Common pitfalls

- **Kernel hangs on "Connecting to kernel…"** — the registered `bina`
  kernel points to a different interpreter than the one you set up.
  Re-run `python -m ipykernel install --user --name bina`.
- **`ModuleNotFoundError: pyproj`** — env was created before pyproj was
  added. Run `conda env update -f environment.yml --prune`.
- **Folium map shows blank in VSCode** — make sure the cell ran in this
  branch (it now embeds the map as a base64 data-URI iframe). Older
  output that used `IFrame("ff2_zuerich_map.html")` will not render in
  VSCode's webview because the relative path does not resolve. Just
  rerun the cell.

---

## 3. Contributing with git

### 3.1 Create a feature branch

`master` is the integration branch. Don't commit directly. Branch off:

```bash
git checkout master
git pull
git checkout -b ff2/refine-priority-score
```

Branch naming: `<area>/<short-topic>` — examples:
- `ff2/refine-priority-score`
- `cleaning/handle-2026-data`
- `docs/update-readme`

### 3.2 Make changes, run notebooks before committing

For notebook changes, **always re-run the affected notebooks** so the
committed `.ipynb` reflects the new outputs. Otherwise reviewers see
stale results.

```bash
conda activate bina
jupyter nbconvert --to notebook --execute --inplace notebooks/FF2/03_ff2_growth_hotspots.ipynb
```

### 3.3 Stage and commit

```bash
git status
git add <files you actually changed>
git commit -m "ff2: refine priority weighting (volume 0.30, urgency 0.20)"
```

Commit message format: `<area>: <imperative summary>` — keep it short,
explain the *why* in the body if it isn't obvious from the diff.

**Don't commit:**
- `data/` — gitignored, derived from `data.stadt-zuerich.ch`
- `*.html` under `notebooks/` — gitignored, regenerated by nbconvert and
  the folium cell
- Local Claude / VSCode settings (`.claude/settings.local.json`)
- Secrets, API keys, anything in `.env`

### 3.4 Push and open a pull request

```bash
git push -u origin ff2/refine-priority-score
```

GitHub will print a PR URL. Open it, add a one-paragraph summary plus a
short test plan ("Re-ran notebook 03 end-to-end, priority A list
unchanged, score for station 3003 went from 0.73 → 0.78").

Get a review, address comments with **new commits** (don't force-push
your branch unless asked), then merge into `master` once approved.

### 3.5 Keeping your branch up to date

If `master` moves while you work, rebase or merge it in:

```bash
git fetch origin
git rebase origin/master
# or, if you prefer merge commits:
git merge origin/master
```

Resolve any conflicts, re-run the notebooks if data-prep cells changed,
and force-push **only your feature branch** (never `master`):

```bash
git push --force-with-lease
```

### 3.6 Notebook-specific git tips

Notebooks are JSON, so diffs and merges are noisy. Two habits help:

1. **Restart kernel and run all cells before committing** so execution
   counts and outputs are deterministic.
2. **Edit only one notebook at a time** in a given branch when you can —
   merge conflicts inside cell metadata are painful to resolve by hand.

For larger projects, tools like `nbstripout` or `jupytext` can help, but
they are not configured here.
