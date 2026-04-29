#!/usr/bin/env bash
# Foolproof one-liner for macOS / Linux / Git Bash.
# Hydrates data/ from the committed archive.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python not found. Install Python 3 (or activate the 'bina' conda env)." >&2
    exit 1
fi

PY=python
command -v python3 >/dev/null 2>&1 && PY=python3
"$PY" scripts/setup_data.py "$@"
