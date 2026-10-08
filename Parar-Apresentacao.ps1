param([switch]$PublicOnly)
$ErrorActionPreference = 'Stop'
$services = if ($PublicOnly) { @('public-app','tunnel') } else { @('public-app','tunnel','app','mail') }
foreach ($service in $services) {
 $pidPath = Join-Path $PSScriptRoot ".local-run/$service.pid"
 if (Test-Path -LiteralPath $pidPath) {
  $serviceId = [int](Get-Content -LiteralPath $pidPath)
  $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$serviceId" -ErrorAction SilentlyContinue
  $relative = if ($service -eq 'mail') { '.local-tools/mailpit/mailpit.exe' } elseif ($service -eq 'tunnel') { '.local-tools/cloudflared/cloudflared.exe' } else { '.venv/Scripts/python.exe' }
  $expected = Join-Path $PSScriptRoot $relative
  if ($processInfo -and $processInfo.ExecutablePath -and [IO.Path]::GetFullPath($processInfo.ExecutablePath) -eq [IO.Path]::GetFullPath($expected)) {
   if ($service -in @('mail','tunnel') -or $processInfo.CommandLine -match 'uvicorn main:app') { Stop-Process -Id $serviceId }
  }
 }
}
Write-Host 'Serviços selecionados encerrados.'
