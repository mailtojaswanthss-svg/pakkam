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
# An old backend still holds the search index (Qdrant allows one process), and an old
# tunnel points at it; stop both so the new ones start cleanly.
$old = @(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { $_.OwningProcess })
# A backend that crashed or is still loading holds the index without listening on 8000:
# also stop every process started as "... fastapi run" (python and uv).
$old += @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -match "fastapi(\.exe)?[`"']?\s+run" } |
    ForEach-Object { $_.ProcessId })
foreach ($id in ($old | Sort-Object -Unique)) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
if ($old) { Start-Sleep -Seconds 3 }
$indexBuild = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -match "schemebot\.(index|ingest)" }
if ($indexBuild) { throw "An index rebuild is still running. Wait for it to finish, then start Pakkam again." }
# Both models already downloaded: load them from disk without asking huggingface.co for a newer
# version, so a dropped connection to the Hub cannot stop the backend from starting.
$hub = if ($env:HF_HOME) { Join-Path $env:HF_HOME "hub" } else { Join-Path $env:USERPROFILE ".cache\huggingface\hub" }
if ((Test-Path (Join-Path $hub "models--BAAI--bge-m3")) -and (Test-Path (Join-Path $hub "models--BAAI--bge-reranker-v2-m3"))) {
    $env:HF_HUB_OFFLINE = "1"
    Write-Host "    Models found on this laptop: loading them offline." -ForegroundColor DarkGray
}
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
$paths = "/ask", "/ask/sources", "/sources", "/transcribe", "/speak", "/feedback", "/check-forward", "/page", "/checklist", "/officer-request", "/dashboard/stats"
$rewrites = $paths | ForEach-Object { [ordered]@{ source = $_; destination = "$url$_" } }
$json = @{ rewrites = @($rewrites) } | ConvertTo-Json -Depth 4
# UTF-8 without a byte-order mark: Windows PowerShell's "-Encoding utf8" adds one, and Vercel
# then rejects vercel.json as invalid JSON.
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "web\vercel.json"), $json, (New-Object System.Text.UTF8Encoding $false))
try {
    npx vercel deploy --prod --yes
    Write-Host "Done. Open https://pakkam-alpha.vercel.app/" -ForegroundColor Green
} catch {
    Write-Host "Vercel deploy failed (run 'npx vercel login' and 'npx vercel link --project pakkam' once)." -ForegroundColor Yellow
    Write-Host "Send this link to Claude instead: $url"
} finally {
    git checkout -- web/vercel.json  # the link changes every run; keep the repo clean
}
