$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host 'BridgeTwin AI - local workspace' -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Install Python 3.12 and enable Add Python to PATH, then run again.' }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Install Node.js 22 LTS or newer, then run again.' }
if (-not (Test-Path 'backend/.venv/Scripts/python.exe')) {
    python -m venv backend/.venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python virtual environment.' }
}
$BridgePython = Join-Path $PSScriptRoot 'backend/.venv/Scripts/python.exe'
if (-not (Test-Path 'backend/.venv/.bridgetwin-installed')) {
    & $BridgePython -m pip install -r backend/requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed. Check your internet connection and retry.' }
    New-Item 'backend/.venv/.bridgetwin-installed' -ItemType File -Force | Out-Null
}
if (-not (Test-Path 'frontend/node_modules/.package-lock.json')) {
    npm.cmd --prefix frontend ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed. Check your internet connection and retry.' }
}
Write-Host 'Open http://localhost:5173 after both services are ready. Press Ctrl+C to stop.' -ForegroundColor Green
node scripts/dev.mjs
