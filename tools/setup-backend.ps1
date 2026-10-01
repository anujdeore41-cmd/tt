$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
New-Item -ItemType Directory -Force -Path $backend | Out-Null
python -m venv (Join-Path $backend ".venv")
$pip = Join-Path $backend ".venv\Scripts\pip.exe"
& $pip install --upgrade pip
& $pip install fastapi "uvicorn[standard]" sqlalchemy alembic pydantic pydantic-settings pyjwt bcrypt "psycopg[binary]" ortools reportlab python-multipart email-validator pytest httpx
& $pip list
Write-Host "Backend dependencies installed."
