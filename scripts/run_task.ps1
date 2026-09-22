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

$invocation = Invoke-PythonJsonArgv -ArgumentList $arguments
$exitCode = [int]$invocation[0]
$output = [string]$invocation[1]
if ($exitCode -ne 0 -or $Action -ne "Close") {
    Write-Output $output
    exit $exitCode
}

$closeResult = $output | ConvertFrom-Json
$boardPath = "docs/task_board.md"
$statusLines = @(& git -C $RepositoryRoot status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect Git status after Close."
}
$changedPaths = @($statusLines | ForEach-Object {
    if ($_.Length -ge 4) { $_.Substring(3).Replace("\", "/") } else { $_ }
})
if ($changedPaths.Count -ne 1 -or $changedPaths[0] -ne $boardPath) {
    throw "Close may commit only docs/task_board.md; found: $($changedPaths -join ', ')"
}

& git -C $RepositoryRoot add -- $boardPath
if ($LASTEXITCODE -ne 0) {
    throw "Unable to stage the closed task board."
}
$stagedPaths = @(& git -C $RepositoryRoot diff --cached --name-only)
if ($LASTEXITCODE -ne 0 -or $stagedPaths.Count -ne 1 -or $stagedPaths[0].Replace("\", "/") -ne $boardPath) {
    throw "Close commit staging was not board-only."
}

$commitMessage = if ($Disposition -eq "completed") {
    "close($Task): publish completed task"
} else {
    "close($Task): record cancelled task"
}
& git -C $RepositoryRoot commit -m $commitMessage | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Unable to commit the closed task board."
}
$closeHead = @(& git -C $RepositoryRoot rev-parse HEAD) -join ""
if ($LASTEXITCODE -ne 0) {
    throw "Unable to resolve the close commit."
}
$closeResult | Add-Member -NotePropertyName close_commit -NotePropertyValue $closeHead

if ($Disposition -eq "cancelled") {
    $closeResult | Add-Member -NotePropertyName publication -NotePropertyValue ([pscustomobject]@{
        code = "SKIPPED_CANCELLED_CLOSE"
        changed = $false
    })
    Write-Output ($closeResult | ConvertTo-Json -Compress -Depth 12)
    exit 0
}

$publishHelper = Join-Path $PSScriptRoot "connlab_publish_closed_task.py"
$publishArguments = @(
    $publishHelper, "--repo-root", $RepositoryRoot,
    "--task-id", $Task, "--expected-head", $closeHead, "--json"
)
$publicationInvocation = Invoke-PythonJsonArgv -ArgumentList $publishArguments
$publicationExitCode = [int]$publicationInvocation[0]
$publication = ([string]$publicationInvocation[1]) | ConvertFrom-Json
if ($publicationExitCode -ne 0) {
    $publication | Add-Member -NotePropertyName close_result -NotePropertyValue $closeResult
    $publication | Add-Member -NotePropertyName close_commit -NotePropertyValue $closeHead -Force
    Write-Output ($publication | ConvertTo-Json -Compress -Depth 12)
    exit $publicationExitCode
}

$closeResult | Add-Member -NotePropertyName publication -NotePropertyValue $publication
Write-Output ($closeResult | ConvertTo-Json -Compress -Depth 12)
exit 0
