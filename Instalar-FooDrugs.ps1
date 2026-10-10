$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Execute setup.ps1 antes de instalar a FooDrugs.' }
Push-Location (Join-Path $PSScriptRoot 'backend')
try {
 & $pythonPath -u install_foodrugs.py
 if ($LASTEXITCODE -ne 0) { throw 'Instalação não concluída. A base anterior foi preservada; confira a mensagem acima.' }
} finally { Pop-Location }
