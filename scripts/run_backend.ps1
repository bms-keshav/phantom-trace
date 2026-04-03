$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.\.venv\Scripts\python.exe')) {
  throw 'No .venv found. Run scripts/setup_backend.ps1 first.'
}

& .\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
