# Keeps the public Drug-Food Checker online (demo mode) at https://drugfood.painel.host (Cloudflare Tunnel)
# and https://drugfood.tail7a6e28.ts.net (Tailscale Funnel). Idempotent: run at logon and every few minutes
# by the scheduled task "Drug-Food Checker - servidor 24h"; it only starts what is not running.
$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$runPath = Join-Path $root '.local-run'
New-Item -ItemType Directory -Force -Path $runPath | Out-Null
$log = Join-Path $runPath 'servidor-24h.log'
function Log($m) { "$(Get-Date -Format s) $m" | Add-Content -LiteralPath $log }
function Healthy($url) { try { (Invoke-RestMethod "$url/api/health" -TimeoutSec 8).status -eq 'ok' } catch { $false } }

# 1. Application on 127.0.0.1:8002
if (-not (Healthy 'http://127.0.0.1:8002')) {
  $pidFile = Join-Path $runPath 'public-app.pid'
  if (Test-Path $pidFile) { Stop-Process -Id (Get-Content $pidFile) -Force -ErrorAction SilentlyContinue }
  $accounts = Get-Content -LiteralPath (Join-Path $runPath 'ACESSOS-APRESENTACAO.txt') -Raw
  $env:DEMO_EMAIL = ([regex]'E-mail:\s*(\S+)').Match(($accounts -csplit 'Visitante')[1]).Groups[1].Value
  $env:SMTP_HOST = ''; $env:SMTP_PORT = ''
  $env:APP_ORIGIN = 'https://drugfood.painel.host,https://drugfood.tail7a6e28.ts.net'
  $env:APP_ENV = 'production'; $env:DEMO_MODE = 'true'
  $env:JWT_SECRET = (Get-Content -LiteralPath (Join-Path $root 'backend/.local-secret') -Raw).Trim()
  $env:DATABASE_URL = 'sqlite:///./drugfood.db'
  $p = Start-Process -FilePath (Join-Path $root '.venv/Scripts/python.exe') -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8002','--no-access-log','--proxy-headers','--forwarded-allow-ips','127.0.0.1' `
       -WorkingDirectory (Join-Path $root 'backend') -WindowStyle Hidden -PassThru `
       -RedirectStandardOutput (Join-Path $runPath 'public-app.log') -RedirectStandardError (Join-Path $runPath 'public-app-error.log')
  $env:JWT_SECRET = ''; $env:DEMO_MODE = ''; $env:DEMO_EMAIL = ''
  $p.Id | Set-Content $pidFile
  Log "app iniciado (pid $($p.Id))"
  for ($i = 0; $i -lt 60 -and -not (Healthy 'http://127.0.0.1:8002'); $i++) { Start-Sleep 2 }
}

# 2. Cloudflare Tunnel (drugfood.painel.host)
$cf = Join-Path $root '.local-tools/cloudflared/cloudflared.exe'
$cfConfig = Join-Path $env:USERPROFILE '.cloudflared/drugfood.yml'
$running = Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" | Where-Object { $_.CommandLine -like '*drugfood.yml*' }
if ((Test-Path $cfConfig) -and -not $running) {
  $t = Start-Process -FilePath $cf -ArgumentList 'tunnel','--config',$cfConfig,'run','drugfood' -WindowStyle Hidden -PassThru `
       -RedirectStandardOutput (Join-Path $runPath 'cloudflared.log') -RedirectStandardError (Join-Path $runPath 'cloudflared-error.log')
  Log "tunel cloudflare iniciado (pid $($t.Id))"
}

# 3. Tailscale Funnel (kept by the Tailscale service; re-applied in case it was reset)
$ts = 'C:\Program Files\Tailscale\tailscale.exe'
if (Test-Path $ts) { & $ts funnel --bg 8002 *> $null }
