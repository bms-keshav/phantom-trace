$ErrorActionPreference = 'Stop'

Write-Host '[PHANTOM TRACE] Setting up backend...' -ForegroundColor Cyan

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  throw 'Python launcher (py) not found. Install Python 3.11 first.'
}

py -3.11 -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host '[PHANTOM TRACE] Backend setup complete.' -ForegroundColor Green
