"""Hydrate the local data/ folder from the committed data_bundle.zip.

Runs out-of-the-box on any OS with Python 3 (no third-party libs required).
Idempotent: if data/ is already populated, it skips the extraction.

Usage:
    python scripts/setup_data.py            # extract bundle into data/
    python scripts/setup_data.py --force    # re-extract even if already hydrated
"""
from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Candidate bundle filenames in priority order. .zip is the default; we keep
# the older formats supported so old clones still work after a format change.
CANDIDATE_BUNDLES: tuple[str, ...] = (
    "data_bundle.zip",
    "data_bundle.tar.xz",
    "data_bundle.tar.gz",
)

# A canonical file we expect to exist after a successful hydration.
SENTINEL = DATA / "verkehrszaehlungen_werte_fussgaenger_velo_alle_jahre.parquet"


def find_bundle() -> Path | None:
    for name in CANDIDATE_BUNDLES:
        candidate = ROOT / name
        if candidate.exists():
            return candidate
    return None


def extract_zip(bundle: Path) -> None:
    with zipfile.ZipFile(bundle, "r") as zf:
        zf.extractall(DATA)


def extract_tar(bundle: Path, mode: str) -> None:
    with tarfile.open(bundle, mode=mode) as tf:
        tf.extractall(DATA, filter="data")


def extract_bundle(bundle: Path) -> None:
    DATA.mkdir(exist_ok=True)
    size_mb = bundle.stat().st_size / 1e6
    print(f"Extracting {bundle.name} ({size_mb:.1f} MB) into {DATA.relative_to(ROOT)}/ ...")

    suffix = "".join(bundle.suffixes).lower()
    if suffix.endswith(".zip"):
        extract_zip(bundle)
    elif suffix.endswith(".tar.xz") or bundle.suffix == ".xz":
        extract_tar(bundle, "r:xz")
    elif suffix.endswith(".tar.gz") or bundle.suffix in (".gz", ".tgz"):
        extract_tar(bundle, "r:gz")
    else:
        print(f"ERROR: unrecognized bundle format: {bundle.name}", file=sys.stderr)
        sys.exit(1)

    n_files = sum(1 for _ in DATA.rglob("*") if _.is_file())
    print(f"Done. data/ now has {n_files} files.")


def already_hydrated() -> bool:
    return SENTINEL.exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="Hydrate data/ from the committed archive.")
    parser.add_argument(
        "--force", action="store_true",
        help="Re-extract even if data/ is already populated.",
    )
    args = parser.parse_args()

    if already_hydrated() and not args.force:
        rel = SENTINEL.relative_to(ROOT)
        print(f"data/ already hydrated (found {rel}). Use --force to re-extract.")
        return 0

    bundle = find_bundle()
    if bundle is None:
        print(
            f"ERROR: no dataset bundle found in {ROOT}. Looked for: "
            + ", ".join(CANDIDATE_BUNDLES)
            + "\nEither pull again, or run notebook 01_data_acquisition.ipynb "
            "to re-download the raw files from data.stadt-zuerich.ch.",
            file=sys.stderr,
        )
        return 1

    extract_bundle(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
