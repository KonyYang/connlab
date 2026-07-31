[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendRoot = Join-Path $repoRoot "frontend"
$viteCommand = Join-Path $frontendRoot "node_modules\.bin\vite.cmd"
Set-Location $frontendRoot

if (!(Test-Path -LiteralPath $viteCommand -PathType Leaf)) {
    Write-Host "Installing frontend dependencies..."
    npm install
}

if (!(Test-Path -LiteralPath $viteCommand -PathType Leaf)) {
    throw "Vite command is still unavailable after npm install: $viteCommand. Review the npm install output and repair the frontend dependencies before retrying."
}

Write-Host "===================================="
Write-Host " Starting ConnLab Frontend"
Write-Host "===================================="
Write-Host "Frontend dev server will print the local URL."
Write-Host "API proxy target: http://127.0.0.1:8000"

npm run dev
