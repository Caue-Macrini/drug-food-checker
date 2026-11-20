param([switch]$NoBrowser)
# Publica o Drug-Food Checker no endereço fixo do Tailscale Funnel, em modo de demonstração.
$ErrorActionPreference = 'Stop'
$publicUrl = 'https://drugfood.tail7a6e28.ts.net'
$tailscale = 'C:\Program Files\Tailscale\tailscale.exe'
$runPath = Join-Path $PSScriptRoot '.local-run'
New-Item -ItemType Directory -Force -Path $runPath | Out-Null

# Sistema local (porta 8000, completo, inclusive administração) e caixa de e-mails de demonstração.
& (Join-Path $PSScriptRoot 'Apresentar.ps1') -NoBrowser
# Encerra a instância pública anterior e o túnel temporário do Cloudflare, se existirem.
& (Join-Path $PSScriptRoot 'Parar-Apresentacao.ps1') -PublicOnly

# Conta de visitante usada pelo botão "Entrar como visitante".
$accounts = Get-Content -LiteralPath (Join-Path $runPath 'ACESSOS-APRESENTACAO.txt') -Raw
$demoEmail = ([regex]'E-mail:\s*(\S+)').Match(($accounts -csplit 'Visitante')[1]).Groups[1].Value

$env:SMTP_HOST = ''; $env:SMTP_PORT = ''
$env:APP_ORIGIN = "https://drugfood.painel.host,$publicUrl"
$env:APP_ENV = 'production'
$env:DEMO_MODE = 'true'
$env:DEMO_EMAIL = $demoEmail
$env:JWT_SECRET = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'backend/.local-secret') -Raw).Trim()
$env:DATABASE_URL = 'sqlite:///./drugfood.db'
$pythonPath = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$publicApp = Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8002','--no-access-log','--proxy-headers','--forwarded-allow-ips','127.0.0.1' -WorkingDirectory (Join-Path $PSScriptRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runPath 'public-app.log') -RedirectStandardError (Join-Path $runPath 'public-app-error.log')
$env:JWT_SECRET = ''; $env:DEMO_MODE = ''; $env:DEMO_EMAIL = ''
$publicApp.Id | Set-Content (Join-Path $runPath 'public-app.pid')

# Funnel fica salvo no Tailscale e volta sozinho após reiniciar o PC.
& $tailscale funnel --bg 8002 | Out-Null

$ready = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
  try { $health = Invoke-RestMethod "$publicUrl/api/health" -TimeoutSec 5; if ($health.status -eq 'ok') { $ready = $true; break } } catch {}
  Start-Sleep -Milliseconds 1000
}
$publicUrl | Set-Content -LiteralPath (Join-Path $runPath 'LINK-PUBLICO.txt')
if ($ready) { Write-Host "Link público fixo (modo demonstração): $publicUrl" } else { Write-Host "Servidor iniciado; o link $publicUrl ainda não respondeu. Verifique o Tailscale." }
if (!$NoBrowser) { Start-Process $publicUrl }
