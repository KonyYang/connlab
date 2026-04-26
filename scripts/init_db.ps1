[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "===================================="
Write-Host " Initializing ConnLab SQLite DB"
Write-Host "===================================="

py -c "from backend.infrastructure.storage.database import create_database_engine, init_db; engine = create_database_engine(); init_db(engine); engine.dispose(); print('Database initialized')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Database initialization failed"
    exit $LASTEXITCODE
}

Write-Host "ConnLab database is ready."
