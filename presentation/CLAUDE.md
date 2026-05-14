# CLAUDE.md — presentation/

This file gives a future AI assistant (or collaborator) full context on the presentation layer of the **BINA** project so work can resume without re-reading notebooks or re-discovering prior decisions.

---

## 1. Business context

**Project:** BINA — Semester 2 BI project, Zurich University of Applied Sciences  
**Topic:** Bicycle traffic analysis, City of Zurich, 2020–2025  
**Strategic anchor:** Velostrategie 2030 — the city's goal to make cycling "für alle jederzeit selbstverständlich" (self-evident for everyone at all times).  
**Methodology framework:** CPA «From Data to Decisions» (Marr, 2020), Steps 1–4 (Step 5 = management decision, not part of the notebooks).  
**Audience:** Non-technical management / city decision-makers → slides must be in German, jargon-free, insight-first.

### Three research questions

| ID  | Forschungsfrage | Management takeaway |
|-----|-----------------|---------------------|
| FF1 | Welche Zählstellen weisen konstant das höchste absolute Veloaufkommen auf, und wie hat sich dieses von 2020 bis 2025 verändert? | Identifies the core infrastructure axes that carry the most load. |
| FF2 | Welche Zählstellen zeigen den stärksten Wachstumstrend (CAGR 2020–2025)? Wo soll die Stadt präventive Kapazitätserweiterungen priorisieren? | Concentration finding: 80% of net growth on 3 corridors → targeted investment. |
| FF3 | Wie stark reagiert das Veloaufkommen auf Regen und tiefe Temperaturen? Welche Standorte weisen überdurchschnittliche Wettersensitivität auf? | Cold (−41.6%) is 4× more impactful than rain (−10.2%) — structural barrier to year-round use. |

---

## 2. Repository layout (relevant to this folder)

```
bina/
├── data_bundle.zip              compressed dataset bundle (~93 MB, in git)
├── setup.sh / setup.ps1         one-shot extraction scripts
├── data/                        gitignored — populated by setup scripts
│   └── clean/
│       ├── velo_15min_clean.parquet
│       ├── station_metadata.csv
│       ├── ff2_growth_trends.csv
│       └── ff2_yearly_totals.csv
├── notebooks/
│   ├── FF1/FF1_absolutes_aufkommen.ipynb
│   ├── FF2/03_ff2_growth_hotspots.ipynb
│   └── FF3/04_ff3_Wettersensitivität_v2.ipynb
└── presentation/                ← YOU ARE HERE
    ├── CLAUDE.md                (this file)
    ├── make_pptx_ff1.py         the single self-contained PPTX generator
    ├── intro_highlight.md       source bullet points for the Highlights slide
    └── FF1_Veloaufkommen_Zürich.pptx   generated output (not in git)
```

---

## 3. The PPTX generator — `make_pptx_ff1.py`

### Key design decision: fully self-contained

**No CSV/parquet reads at runtime.** All data is hardcoded from verified notebook outputs. This means the script runs anywhere with only Python + the libraries listed below — no `data/` folder needed.

If notebook results change (e.g. new year of data), update the hardcoded constants at the top of the script.

### Runtime dependencies

```
python-pptx
matplotlib
seaborn
numpy
Pillow (PIL)
```

Install via the repo's conda env (`conda activate bina`) or:
```bash
pip install python-pptx matplotlib seaborn numpy Pillow
```

### Running the script

```bash
cd bina/presentation
python3 make_pptx_ff1.py
```

Output: `FF1_Veloaufkommen_Zürich.pptx` — written next to the script.

---

## 4. Slide structure (current)

Slides are created in code order, then reordered via XML manipulation before saving. The reorder block moves the Highlights slide (created 3rd) to position 1 (after Intro, before Title).

| Position | Label | Variable | Content |
|----------|-------|----------|---------|
| 1 | `01` | `s_intro` | Kontext & Forschungsfragen — Velostrategie 2030 + FF1/FF2/FF3 cards |
| 2 | `02` | `s2` | Projekt-Highlights — team learnings (3-column card layout) |
| 3 | *(none)* | `s1` | Title slide — "Absolutes Veloaufkommen", stats boxes |
| 4 | `03` | `s3` (first) | FF1 Heatmap — Top-15 stations × years |
| 5 | `04` | `s3` (reused) | FF2 Wachstums-Hotspots — CAGR ranking bar chart |
| 6 | `05` | `s4` | FF3 Wettersensitivität — weather effect bar chart |

**Creation order in code:** s_intro → s1 (Title) → s2 (Highlights) → s3 (Heatmap) → s3 (FF2) → s4 (FF3)

**Reorder logic (at end of build section, before save):**
```python
_sldIdLst = prs.slides._sldIdLst
_slides = list(_sldIdLst)
_el = _slides[2]          # Highlights (created 3rd, index 2)
_sldIdLst.remove(_el)
_sldIdLst.insert(1, _el)  # move to position 1 (after Intro)
```

Result order: Intro(0) → Highlights(1) → Title(2) → Heatmap(3) → FF2(4) → FF3(5)

**When adding a new slide:** create it in code, then update the reorder index if it affects position. Update all affected label numbers manually.

---

## 5. Design system

### Slide dimensions
```python
SLIDE_W = Inches(13.33)   # widescreen 16:9
SLIDE_H = Inches(7.5)
```

### Colour palette
```python
C_BG     = RGBColor(0x0D, 0x1B, 0x2A)   # dark navy — slide background
C_ACCENT = RGBColor(0x00, 0xB4, 0xD8)   # cyan — primary accent, borders, numbers
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)   # body text
C_LIGHT  = RGBColor(0xB0, 0xC4, 0xDE)   # muted blue-grey — subtitles, descriptions
C_ORANGE = RGBColor(0xFF, 0x6B, 0x35)   # callout highlights
BG_HEX   = "#0D1B2A"                    # same as C_BG but as hex string for matplotlib
```

Additional per-slide colours (defined inline):
- `C_GREEN2 = RGBColor(0x2D, 0xD4, 0x8A)` — Highlights col 2 / FF2 accent
- `C_PURPLE = RGBColor(0xA2, 0x8B, 0xF5)` — Highlights col 3 / FF3 accent
- `C_RED    = RGBColor(0xFF, 0x4D, 0x6D)` — FF3 danger callout

### Layout conventions
- Slide number label: top-left, `Inches(0.25), Inches(0.2)`, size 11, `C_ACCENT`
- Slide title: `Inches(0.25), Inches(0.45)`, size 22–26, bold, `C_WHITE`
- Subtitle / source line: `Inches(0.25), Inches(0.95)`, size 12, `C_LIGHT`
- Top accent bar: `accent_line(slide, 0, 0, SLIDE_W, 0.06")`
- Bottom accent bar: `accent_line(slide, 0, SLIDE_H - 0.06", SLIDE_W, 0.06")`
- Card/panel background: `RGBColor(0x12, 0x26, 0x3A)` (slightly lighter than BG)
- Card/panel inner highlight: `RGBColor(0x1A, 0x2F, 0x4A)` (for nested boxes)

### Helper functions
```python
fig_to_stream(fig)          # saves matplotlib fig → BytesIO at dpi=120
add_bg(slide)               # fills slide background with C_BG
add_label(slide, text, left, top, width, height, size, bold, color, align)
accent_line(slide, left, top, width, height)
```

---

## 6. Hardcoded data constants

All values sourced from notebooks as of 2026. Update here if notebooks are re-run with new data.

### FF1 — Heatmap (`HEATMAP`, `YEARS`)
- 15 stations, yearly totals 2020–2025
- Source: `notebooks/FF1/FF1_absolutes_aufkommen.ipynb`
- Key finding: Stadttunnel Nord has extreme variance (sensor issues); Sonneggstrasse & Hardbrücke are stable top performers

### FF2 — Growth hotspots (`FF2_STATIONS`)
- 12 consistent stations (≥60% data coverage every year)
- Fields per row: `(name, cagr_pct, trend_quality, mean_annual)`
- `trend_quality`: `"strong"` (low p-value + high R²) / `"moderate"` / `"weak"`
- Source: `notebooks/FF2/03_ff2_growth_hotspots.ipynb` → also exported to `data/clean/ff2_growth_trends.csv`
- Key finding: Baslerstrasse +13.4% CAGR (R²=0.91), top priority. Langstrasse Unterführungen declining (−5% to −7%).

### FF3 — Weather effect (`FF3_WEATHER`, `FF3_STATION_RAIN`)
- `FF3_WEATHER`: network-level avg velos per station-day by condition
  - Trocken & mild: 1500 → Nur Regen: 1347 (−10.2%) → Nur Kalt ≤5°C: 904 (−41.6%) → Regen + Kalt: 790 (−47%)
- `FF3_STATION_RAIN`: station-level rain sensitivity, sorted most→least sensitive
- Source: `notebooks/FF3/04_ff3_Wettersensitivität_v2.ipynb`
- Key finding: cold is structural barrier (4× stronger than rain); sensitivity improving 2020→2025 (−43.9% → −36.3%)

---

## 7. Known technical gotchas

### PIL DecompressionBomb
python-pptx passes embedded images through PIL when saving. PIL blocks images >89 MP by default. Fix already in place at top of script:
```python
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
```
Do not remove this line.

### Chart DPI
Kept at `dpi=120` in `fig_to_stream()`. Higher values (160+) caused PIL loading errors on some machines due to image size. 120 is the safe maximum for this slide size.

### FF3 chart coordinate system
The FF3 chart was originally built with `ax.get_xaxis_transform()` at `y=-220` (mixing data and axes coordinates — broken). It was completely rewritten to use only standard axes: `fig.subplots_adjust(bottom=0.12)` instead of `tight_layout`, percentage labels inside bars, no custom transforms or annotations. Do not reintroduce transforms or `ax.annotate` arrows on this chart.

### Slide variable name reuse
The FF2 slide uses `s3` as its variable name (same as the Heatmap slide). This is intentional and harmless since each `add_slide()` call returns a new object. The variable is just a local handle. Don't read into the naming — slide identity is determined by insertion order, not variable name.

### pandas removed
The script originally imported pandas for the heatmap DataFrame. It was removed; the heatmap now uses a numpy array + manual `ax.set_yticks/set_yticklabels`. Do not re-add pandas — it creates a dependency that isn't needed.

---

## 8. How to extend

### Add a new research-question slide

1. Hardcode any new data as a constant near the top (with a comment citing the source notebook).
2. Generate the chart using matplotlib; store result with `fig_to_stream(fig)`.
3. Add `sN = prs.slides.add_slide(blank)` in the build section in the desired creation order.
4. Apply `add_bg(sN)`, accent lines, label with the correct slide number.
5. If slide ordering needs adjustment, update the reorder block (see Section 4).
6. Increment all affected slide number labels.

### Update data after a new year of measurements

1. Re-run `notebooks/FF1/FF1_absolutes_aufkommen.ipynb` and extract the updated heatmap totals → update `HEATMAP` and `YEARS`.
2. Re-run `notebooks/FF2/03_ff2_growth_hotspots.ipynb` → update `FF2_STATIONS` from `data/clean/ff2_growth_trends.csv`.
3. Re-run `notebooks/FF3/04_ff3_Wettersensitivität_v2.ipynb` → update `FF3_WEATHER` and `FF3_STATION_RAIN`.
4. Run `python3 make_pptx_ff1.py` to regenerate the PPTX.

### Change slide language / copy

All German text is inline in the build section. Search for the relevant slide section header comment (e.g. `# ── SLIDE 5: FF3`) and edit the `add_label(...)` calls directly.

---

## 9. Source notebooks — quick reference

| Notebook | Path | What it covers |
|----------|------|----------------|
| FF1 | `notebooks/FF1/FF1_absolutes_aufkommen.ipynb` | Absolute traffic volume, heatmap, geographic map |
| FF2 | `notebooks/FF2/03_ff2_growth_hotspots.ipynb` | CAGR, linear regression, priority score, doubling time |
| FF3 | `notebooks/FF3/04_ff3_Wettersensitivität_v2.ipynb` | Rain/cold effect, station-level sensitivity, time trend |
| Cleaning | `notebooks/02_data_cleaning.ipynb` | Produces parquet/CSV inputs for FF2 and FF3 |
| Acquisition | `notebooks/01_data_acquisition.ipynb` | Downloads raw CSVs from data.stadt-zuerich.ch |
