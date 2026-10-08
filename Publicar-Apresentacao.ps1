param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Apresentar.ps1') -NoBrowser
$runPath = Join-Path $PSScriptRoot '.local-run'
$linkPath = Join-Path $runPath 'LINK-PUBLICO.txt'
if (Test-Path -LiteralPath $linkPath) {
 $oldLink = (Get-Content -LiteralPath $linkPath -Raw).Trim()
 try {
  $health = Invoke-RestMethod "$oldLink/api/health" -TimeoutSec 10
  if ($health.status -eq 'ok') {
   Write-Host "Link ativo: $oldLink"
   if (!$NoBrowser) { Start-Process $oldLink }
   exit 0
  }
 } catch {}
}
& (Join-Path $PSScriptRoot 'Parar-Apresentacao.ps1') -PublicOnly
$tunnelExe = Join-Path $PSScriptRoot '.local-tools/cloudflared/cloudflared.exe'
if (!(Test-Path -LiteralPath $tunnelExe)) { throw 'cloudflared não instalado. Consulte APRESENTACAO.md.' }
$tunnelLog = Join-Path $runPath 'tunnel-error.log'
$tunnel = Start-Process -FilePath $tunnelExe -ArgumentList 'tunnel','--url','http://127.0.0.1:8002','--no-autoupdate' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runPath 'tunnel.log') -RedirectStandardError $tunnelLog
$tunnel.Id | Set-Content (Join-Path $runPath 'tunnel.pid')
$publicUrl = $null
for ($attempt=0; $attempt -lt 60; $attempt++) {
 if (Test-Path -LiteralPath $tunnelLog) {
  $logText = Get-Content -LiteralPath $tunnelLog -Raw
  if ($logText -match 'https://[a-z0-9-]+\.trycloudflare\.com') { $publicUrl = $Matches[0]; break }
 }
 Start-Sleep -Milliseconds 500
}
if (!$publicUrl) { throw 'Não foi possível obter o link. O sistema local continua disponível.' }
$env:SMTP_HOST = '127.0.0.1'
$env:SMTP_PORT = '1025'
$env:SMTP_TLS = 'false'
$env:SMTP_SSL = 'false'
$env:SMTP_USER = ''
$env:SMTP_PASSWORD = ''
$env:SMTP_FROM = 'demonstracao@drugfood.local'
$env:APP_ORIGIN = $publicUrl
$env:APP_ENV = 'production'
$env:JWT_SECRET = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'backend/.local-secret') -Raw).Trim()
$env:DATABASE_URL = 'sqlite:///./drugfood.db'
$pythonPath = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$publicApp = Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8002','--no-access-log','--proxy-headers','--forwarded-allow-ips','127.0.0.1' -WorkingDirectory (Join-Path $PSScriptRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runPath 'public-app.log') -RedirectStandardError (Join-Path $runPath 'public-app-error.log')
$env:JWT_SECRET = ''
$publicApp.Id | Set-Content (Join-Path $runPath 'public-app.pid')
$ready = $false
for ($attempt=0; $attempt -lt 15; $attempt++) {
 try { $health = Invoke-RestMethod "$publicUrl/api/health" -TimeoutSec 5; if ($health.status -eq 'ok') { $ready=$true; break } } catch {}
 Start-Sleep -Milliseconds 500
}
if (!$ready) { throw 'Link criado, mas ainda sem resposta. Consulte os logs em .local-run.' }
$publicUrl | Set-Content -LiteralPath $linkPath
Write-Host "Link público: $publicUrl"
Write-Host 'Mantenha o computador ligado e conectado. O endereço muda quando o túnel é recriado.'
if (!$NoBrowser) { Start-Process $publicUrl }
