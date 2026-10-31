# One click: start Pakkam on this laptop and point the live website at it.
#
#   powershell -ExecutionPolicy Bypass -File scripts\start_pakkam.ps1
#
# 1. gets the latest code (main), 2. starts the backend in its own window and waits until
# the models are loaded, 3. opens a Cloudflare tunnel and reads its public link, 4. points
# https://pakkam-alpha.vercel.app at that link and redeploys it (Vercel CLI).
# One-time setup for step 4: `npx vercel login`, then `npx vercel link --project pakkam`
# in this folder. Without it the script still runs and prints the link to send to Claude.
# Close the backend and tunnel windows to stop.

param([switch]$NoDeploy)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "1/4 Getting the latest code..." -ForegroundColor Cyan
git checkout main
git pull origin main

Write-Host "2/4 Starting the backend (loading models takes about a minute)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uv run --extra ingest --extra index --extra generate --extra gemini --extra api fastapi run"
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 5
    try { Invoke-RestMethod http://localhost:8000/health -TimeoutSec 4 | Out-Null; $ready = $true; break } catch {}
}
if (-not $ready) { throw "The backend did not start in 5 minutes. Look at its window for the error." }

Write-Host "3/4 Opening the tunnel..." -ForegroundColor Cyan
$log = Join-Path $env:TEMP "pakkam-tunnel.log"
Remove-Item $log -ErrorAction SilentlyContinue
Start-Process cloudflared -ArgumentList "tunnel", "--url", "http://localhost:8000", "--logfile", $log -WindowStyle Minimized
$url = $null
for ($i = 0; $i -lt 30 -and -not $url; $i++) {
    Start-Sleep -Seconds 2
    if (Test-Path $log) {
        $hit = Select-String -Path $log -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" | Select-Object -First 1
        if ($hit) { $url = $hit.Matches[0].Value }
    }
}
if (-not $url) { throw "No tunnel link after 60 s. Check your internet or DNS (1.1.1.1)." }
Write-Host "    Tunnel: $url" -ForegroundColor Green

if ($NoDeploy) { Write-Host "Send this link to Claude: $url"; exit 0 }

Write-Host "4/4 Pointing the website at this laptop..." -ForegroundColor Cyan
$paths = "/ask", "/ask/sources", "/sources", "/transcribe", "/speak", "/feedback"
$rewrites = $paths | ForEach-Object { [ordered]@{ source = $_; destination = "$url$_" } }
@{ rewrites = @($rewrites) } | ConvertTo-Json -Depth 4 | Set-Content web\vercel.json -Encoding utf8
try {
    npx vercel deploy --prod --yes
    Write-Host "Done. Open https://pakkam-alpha.vercel.app/chat/" -ForegroundColor Green
} catch {
    Write-Host "Vercel deploy failed (run 'npx vercel login' and 'npx vercel link --project pakkam' once)." -ForegroundColor Yellow
    Write-Host "Send this link to Claude instead: $url"
} finally {
    git checkout -- web/vercel.json  # the link changes every run; keep the repo clean
}
