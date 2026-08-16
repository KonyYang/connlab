[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Task,

    [ValidateSet("Submit", "Approve", "AmendPlan", "Close")]
    [string]$Action = "Submit",

    [string]$RequestJson,

    [string]$ApprovedRequestJson,

    [string]$PlanRef,

    [string]$ApprovalRef,

    [string]$CallbackJson,

    [string]$DecisionRef,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedBoardSha256,

    [string]$RepositoryRoot,

    [switch]$Preview,

    [switch]$ControlledLaneV2,

    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$helper = Join-Path $PSScriptRoot "connlab_personal_task.py"

if ($ControlledLaneV2) {
    $snapshotText = @(& py $helper inspect --repo-root $RepositoryRoot --json) -join "`n"
    if ($LASTEXITCODE -ne 0) {
        Write-Output $snapshotText
        exit $LASTEXITCODE
    }
    $result = $snapshotText | ConvertFrom-Json
    $result.code = "BLOCKED_LEGACY_MODE_FROZEN"
    $result.allowed = $false
    $result.command = "submit"
    $result.task_id = $Task
    $result.reason = "Controlled Lane V2 is frozen and cannot be started from run_task.ps1."
    $result | ConvertTo-Json -Compress -Depth 20
    exit 2
}

if ($Preview) {
    $output = @(& py $helper inspect --repo-root $RepositoryRoot --json) -join "`n"
    $exitCode = $LASTEXITCODE
    Write-Output $output
    exit $exitCode
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
"Approve" {
    if ([string]::IsNullOrWhiteSpace($ApprovedRequestJson) -or
        [string]::IsNullOrWhiteSpace($PlanRef) -or
        [string]::IsNullOrWhiteSpace($ApprovalRef)) {
        throw "Approve requires -ApprovedRequestJson, -PlanRef, and -ApprovalRef."
    }
    $arguments = @(
        $helper, "approve", "--repo-root", $RepositoryRoot,
        "--expected-board-sha256", $ExpectedBoardSha256,
        "--task-id", $Task, "--approved-request-json", $ApprovedRequestJson,
        "--plan-ref", $PlanRef, "--approval-ref", $ApprovalRef, "--json"
    )
}
"AmendPlan" {
    if ([string]::IsNullOrWhiteSpace($PlanRef) -or
        [string]::IsNullOrWhiteSpace($ApprovalRef) -or
        [string]::IsNullOrWhiteSpace($CallbackJson)) {
        throw "AmendPlan requires -PlanRef, -ApprovalRef, and -CallbackJson."
    }
    $arguments = @(
        $helper, "amend-plan", "--repo-root", $RepositoryRoot,
        "--expected-board-sha256", $ExpectedBoardSha256,
        "--task-id", $Task, "--plan-ref", $PlanRef,
        "--approval-ref", $ApprovalRef, "--callback-json", $CallbackJson, "--json"
    )
}
"Close" {
    if ([string]::IsNullOrWhiteSpace($DecisionRef)) {
        throw "Close requires -DecisionRef containing the explicit User decision."
    }
    $arguments = @(
        $helper, "close", "--repo-root", $RepositoryRoot,
        "--expected-board-sha256", $ExpectedBoardSha256,
        "--task-id", $Task, "--decision-ref", $DecisionRef, "--json"
    )
}
}

$argvEnvironmentName = "CONNLAB_PERSONAL_TASK_ARGV_JSON"
if (Test-Path "Env:$argvEnvironmentName") {
    throw "$argvEnvironmentName is already set."
}
$launcher = "import json,os,runpy,sys;sys.argv=json.loads(os.environ.pop('CONNLAB_PERSONAL_TASK_ARGV_JSON'));runpy.run_path(sys.argv[0],run_name='__main__')"
try {
    $env:CONNLAB_PERSONAL_TASK_ARGV_JSON = ConvertTo-Json -InputObject $arguments -Compress -Depth 5
    $output = @(& py -c $launcher) -join "`n"
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item Env:CONNLAB_PERSONAL_TASK_ARGV_JSON -ErrorAction SilentlyContinue
}
Write-Output $output
exit $exitCode
