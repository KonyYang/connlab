[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Task,

    [ValidateSet("Submit", "Close")]
    [string]$Action = "Submit",

    [string]$RequestJson,
    [string]$DecisionRef,

    [ValidateSet("completed", "cancelled")]
    [string]$Disposition = "completed",

    [string]$ExpectedBoardSha256,
    [string]$RepositoryRoot,
    [switch]$Preview,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$helper = Join-Path $PSScriptRoot "connlab_sol_task.py"

if ($Preview) {
    & py $helper inspect --repo-root $RepositoryRoot --json
    exit $LASTEXITCODE
}

if ([string]::IsNullOrWhiteSpace($ExpectedBoardSha256)) {
    throw "-ExpectedBoardSha256 is required for Submit and Close."
}

switch ($Action) {
    "Submit" {
        if ([string]::IsNullOrWhiteSpace($RequestJson)) {
            throw "-RequestJson is required for Submit."
        }
        $arguments = @(
            $helper, "submit", "--repo-root", $RepositoryRoot,
            "--expected-board-sha256", $ExpectedBoardSha256,
            "--task-id", $Task, "--request-json", $RequestJson, "--json"
        )
    }
    "Close" {
        if ([string]::IsNullOrWhiteSpace($DecisionRef)) {
            throw "-DecisionRef is required for Close."
        }
        $arguments = @(
            $helper, "close", "--repo-root", $RepositoryRoot,
            "--expected-board-sha256", $ExpectedBoardSha256,
            "--task-id", $Task, "--decision-ref", $DecisionRef,
            "--disposition", $Disposition, "--json"
        )
    }
}

$environmentName = "CONNLAB_SOL_TASK_ARGV_JSON"
if (Test-Path "Env:$environmentName") {
    throw "$environmentName is already set."
}

$launcher = "import json,os,runpy,sys;sys.argv=json.loads(os.environ.pop('CONNLAB_SOL_TASK_ARGV_JSON'));runpy.run_path(sys.argv[0],run_name='__main__')"
try {
    $env:CONNLAB_SOL_TASK_ARGV_JSON = ConvertTo-Json -InputObject $arguments -Compress -Depth 5
    $output = @(& py -c $launcher) -join "`n"
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item Env:$environmentName -ErrorAction SilentlyContinue
}

Write-Output $output
exit $exitCode
