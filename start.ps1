$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (!(Test-Path -LiteralPath '.venv/Scripts/python.exe')) { throw 'Execute ./setup.ps1 primeiro.' }
if (!(Test-Path -LiteralPath 'frontend/dist/index.html')) { throw 'Frontend não compilado. Execute ./setup.ps1.' }
$env:APP_ORIGIN = 'http://127.0.0.1:8000'
Write-Host 'Drug-Food Checker: http://127.0.0.1:8000'
Write-Host 'Para parar, pressione Ctrl+C.'
Push-Location backend
try { & ../.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-access-log }
finally { Pop-Location }
