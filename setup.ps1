# Foolproof one-liner for Windows PowerShell.
# Hydrates data/ from the committed archive.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "python not found. Install Python 3 (or activate the 'bina' conda env)."
    exit 1
}

& $python.Source scripts\setup_data.py @args
