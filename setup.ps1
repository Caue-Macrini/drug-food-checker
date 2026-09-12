param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& $Python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o ambiente Python. Informe -Python com o caminho do Python 3.12 ou superior.' }
$env:PIP_CONFIG_FILE = 'NUL'
& ./.venv/Scripts/python.exe -m pip install --no-cache-dir --disable-pip-version-check -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha na instalação das dependências Python.' }
Push-Location frontend
try {
    npm.cmd ci --cache ../.npm-cache
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências do frontend.' }
    npm.cmd run build -- --configLoader runner
    if ($LASTEXITCODE -ne 0) { throw 'Falha na compilação do frontend.' }
} finally { Pop-Location }
Write-Host 'Instalação concluída. Execute ./start.ps1'
