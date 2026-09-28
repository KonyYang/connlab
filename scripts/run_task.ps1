[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Task,

    [ValidateSet("Submit", "Revise", "Close", "CloseAndSubmit")]
    [string]$Action = "Submit",

    [string]$RequestJson,
    [string]$DecisionRef,
    [string]$NextTask,

    [ValidateSet("completed", "cancelled")]
    [string]$Disposition = "completed",

    [string]$ExpectedBoardSha256,
    [string]$RepositoryRoot,
    [string]$WorktreeRoot,
    [ValidateSet("main", "micro")]
    [string]$Slot,
    [string]$ResourcesJson = "[]",
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
    throw "-ExpectedBoardSha256 is required for task transitions."
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
    "Revise" {
        if ([string]::IsNullOrWhiteSpace($DecisionRef)) {
            throw "-DecisionRef is required for Revise."
        }
        $arguments = @(
            $helper, "revise", "--repo-root", $RepositoryRoot,
            "--expected-board-sha256", $ExpectedBoardSha256,
            "--task-id", $Task, "--decision-ref", $DecisionRef, "--json"
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
    "CloseAndSubmit" {
        if ([string]::IsNullOrWhiteSpace($DecisionRef)) {
            throw "-DecisionRef is required for CloseAndSubmit."
        }
        if ([string]::IsNullOrWhiteSpace($NextTask)) {
            throw "-NextTask is required for CloseAndSubmit."
        }
        if ([string]::IsNullOrWhiteSpace($RequestJson)) {
            throw "-RequestJson is required for CloseAndSubmit."
        }
        $arguments = @(
            $helper, "close-and-submit", "--repo-root", $RepositoryRoot,
            "--expected-board-sha256", $ExpectedBoardSha256,
            "--task-id", $Task, "--decision-ref", $DecisionRef,
            "--disposition", $Disposition, "--next-task-id", $NextTask,
            "--request-json", $RequestJson, "--json"
        )
    }
}

function Invoke-PythonJsonArgv {
    param(
        [Parameter(Mandatory = $true)]
        [object[]]$ArgumentList
    )

    $environmentName = "CONNLAB_SOL_TASK_ARGV_JSON"
    if (Test-Path "Env:$environmentName") {
        throw "$environmentName is already set."
    }
    $launcher = "import json,os,runpy,sys;sys.argv=json.loads(os.environ.pop('CONNLAB_SOL_TASK_ARGV_JSON'));runpy.run_path(sys.argv[0],run_name='__main__')"
    try {
        $env:CONNLAB_SOL_TASK_ARGV_JSON = ConvertTo-Json -InputObject $ArgumentList -Compress -Depth 5
        $captured = @(& py -c $launcher) -join "`n"
        return @($LASTEXITCODE, $captured)
    } finally {
        Remove-Item Env:$environmentName -ErrorAction SilentlyContinue
    }
}

if ($WorktreeRoot) { $arguments += @("--worktree-root", $WorktreeRoot) }
if ($Slot) { $arguments += @("--slot", $Slot) }
$arguments += @("--resources-json", $ResourcesJson)
if ($Action -eq "Close") { $arguments += "--publish-close" }
$invocation = Invoke-PythonJsonArgv -ArgumentList $arguments
Write-Output ([string]$invocation[1])
exit ([int]$invocation[0])
