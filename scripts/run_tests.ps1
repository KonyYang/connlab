[CmdletBinding()]
param(
    [ValidateSet("All", "Python", "Frontend", "Office")]
    [string]$Suite = "All"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$logRoot = Join-Path $repositoryRoot "logs"
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null

function Invoke-PythonTests {
    param([switch]$OfficeOnly)

    $selection = if ($OfficeOnly) { "office_integration" } else { "not office_integration" }
    $logName = if ($OfficeOnly) { "pytest_office_last.log" } else { "pytest_last.log" }
    $logPath = Join-Path $logRoot $logName

    Push-Location $repositoryRoot
    try {
        & py -m pytest -p no:cacheprovider -m $selection 2>&1 |
            Tee-Object -FilePath $logPath
        if ($LASTEXITCODE -ne 0) {
            throw "Python test suite failed. See $logPath"
        }
    }
    finally {
        Pop-Location
    }
}

function Invoke-FrontendTests {
    $frontendRoot = Join-Path $repositoryRoot "frontend"

    Push-Location $frontendRoot
    try {
        & npm.cmd test
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend test suite failed."
        }

        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend build failed."
        }
    }
    finally {
        Pop-Location
    }
}

switch ($Suite) {
    "All" {
        Invoke-PythonTests
        Invoke-FrontendTests
    }
    "Python" { Invoke-PythonTests }
    "Frontend" { Invoke-FrontendTests }
    "Office" { Invoke-PythonTests -OfficeOnly }
}

Write-Host "All requested checks passed."
