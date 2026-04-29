"""Hydrate the local data/ folder from the committed data_bundle.tar.xz.

Runs out-of-the-box on any OS with Python 3 (no third-party libs required).
Idempotent: if data/ is already populated, it skips the extraction.

Usage:
    python scripts/setup_data.py            # extract bundle into data/
    python scripts/setup_data.py --force    # re-extract even if already hydrated
    python scripts/setup_data.py --refresh  # re-download via Notebook 01 cells
"""
from __future__ import annotations

import argparse
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "data_bundle.tar.xz"
DATA = ROOT / "data"

# A canonical file we expect to exist after a successful hydration.
SENTINEL = DATA / "verkehrszaehlungen_werte_fussgaenger_velo_alle_jahre.parquet"


def extract_bundle() -> None:
    if not BUNDLE.exists():
        print(
            f"ERROR: {BUNDLE.name} is missing in the repo root.\n"
            "Either pull again, or run notebook 01_data_acquisition.ipynb to "
            "re-download the raw files from data.stadt-zuerich.ch.",
            file=sys.stderr,
        )
        sys.exit(1)

    DATA.mkdir(exist_ok=True)
    print(f"Extracting {BUNDLE.name} ({BUNDLE.stat().st_size / 1e6:.1f} MB) into {DATA.relative_to(ROOT)}/ ...")
    with tarfile.open(BUNDLE, mode="r:xz") as tf:
        tf.extractall(DATA, filter="data")
    n_files = sum(1 for _ in DATA.rglob("*") if _.is_file())
    print(f"Done. data/ now has {n_files} files.")


def already_hydrated() -> bool:
    return SENTINEL.exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="Hydrate data/ from the committed archive.")
    parser.add_argument("--force", action="store_true",
                        help="Re-extract even if data/ is already populated.")
    args = parser.parse_args()

    if already_hydrated() and not args.force:
        rel = SENTINEL.relative_to(ROOT)
        print(f"data/ already hydrated (found {rel}). Use --force to re-extract.")
        return 0

    extract_bundle()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
