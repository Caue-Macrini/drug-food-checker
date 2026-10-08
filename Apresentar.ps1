param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectPath = $PSScriptRoot
$pythonPath = Join-Path $projectPath '.venv/Scripts/python.exe'
$runPath = Join-Path $projectPath '.local-run'
New-Item -ItemType Directory -Force -Path $runPath | Out-Null
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Execute setup.ps1 primeiro.' }
if (!(Test-Path -LiteralPath (Join-Path $projectPath 'frontend/dist/index.html'))) { throw 'Frontend não compilado. Execute setup.ps1.' }
$mailpitPath = Join-Path $projectPath '.local-tools/mailpit/mailpit.exe'
if (!(Test-Path -LiteralPath $mailpitPath)) { throw 'Mailpit local não encontrado. Consulte APRESENTACAO.md.' }
function Test-Endpoint([string]$url) {
 try { $null = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2; return $true } catch { return $false }
}
if (!(Test-Endpoint 'http://127.0.0.1:8025/readyz')) {
 $mailProcess = Start-Process -FilePath $mailpitPath -ArgumentList '--listen','127.0.0.1:8025','--smtp','127.0.0.1:1025','--disable-version-check','--quiet' -WorkingDirectory $runPath -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runPath 'mail.log') -RedirectStandardError (Join-Path $runPath 'mail-error.log')
 $mailProcess.Id | Set-Content (Join-Path $runPath 'mail.pid')
}
if (!(Test-Endpoint 'http://127.0.0.1:8000/api/health')) {
 $env:APP_ORIGIN = 'http://127.0.0.1:8000'
 $env:APP_ENV = 'development'
 $env:SMTP_HOST = '127.0.0.1'
 $env:SMTP_PORT = '1025'
 $env:SMTP_TLS = 'false'
 $env:SMTP_SSL = 'false'
 $env:SMTP_FROM = 'demonstracao@drugfood.local'
 $env:DATABASE_URL = 'sqlite:///./drugfood.db'
 $env:SMTP_USER = ''
 $env:SMTP_PASSWORD = ''
 $appProcess = Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8000','--no-access-log' -WorkingDirectory (Join-Path $projectPath 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runPath 'app.log') -RedirectStandardError (Join-Path $runPath 'app-error.log')
 $appProcess.Id | Set-Content (Join-Path $runPath 'app.pid')
}
$ready = $false
for ($attempt=0; $attempt -lt 30; $attempt++) {
 if ((Test-Endpoint 'http://127.0.0.1:8000/api/health') -and (Test-Endpoint 'http://127.0.0.1:8025/readyz')) { $ready=$true; break }
 Start-Sleep -Milliseconds 500
}
if (!$ready) { throw 'Não foi possível iniciar. Consulte .local-run/app-error.log e mail-error.log.' }
Write-Host 'Sistema: http://127.0.0.1:8000'
Write-Host 'E-mails de demonstração: http://127.0.0.1:8025'
Write-Host 'Os serviços continuam rodando após fechar esta janela.'
if (!$NoBrowser) { Start-Process 'http://127.0.0.1:8000' }
