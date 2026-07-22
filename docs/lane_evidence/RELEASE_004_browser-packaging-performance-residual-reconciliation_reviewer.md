# RELEASE_004 Browser Packaging Performance Residual Reconciliation - Reviewer Evidence

Date: 2026-07-22

Role: Reviewer

Status: `reviewer_blocked / Planner docs-only fix required`

Task: `RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION`

Lane: `release-004-browser-packaging-performance-residual-reconciliation`

## Current Phase / Active Task / Review Boundary

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled
  foundation.
- Current active task: none. The board records TASK_366A and TASK_366C as accepted.
- This was a plan-only review. No product, packaging script, test, release artifact,
  database, public-drive file, attachment, staging, commit, or push operation occurred.

## Review Findings

### B1: The exact candidate release_004 document contradicts the planned-only lane contract

`docs/release_004_browser_release_packaging_performance_plan.md` is one of the four
declared candidate paths, so it must agree with the governing task and reconciliation
plan. It currently does not:

- It names TASK_366A as the active planned-only task, although the board records no
  active task and TASK_366A as accepted.
- It permits generated build outputs during validation, instructs a real
  `build_windows_browser_release.ps1` run plus release-folder smoke/dependency checks,
  and says to report whether a new release was generated. Those instructions conflict
  with this lane's explicit planned-only status, no-real-release-build boundary, and
  immutable `dist_release/**` lock.

The packaging code/test candidate itself is narrowly coherent: the spec filters only
desktop shell prefixes and excludes desktop dependencies; the script's timer wrapper
preserves the existing command/error checks; the static test additions cover the new
symbols. However, the stale candidate document would authorize the very artifact
mutation that this gate must prohibit, so the package is not yet safe to advance.

## Required Planner Docs-Only Fix

Update only the Release 004 governance/candidate document and its related planned-lane
status wording:

1. Replace its stale TASK_366A/current-task statements with the current board fact:
   no active task, with TASK_366A accepted.
2. State that this lane's implementation and validation are static only. Remove real
   browser-release execution, release-folder smoke, artifact-shape checks, and
   generated-release reporting from its current validation/stop instructions.
3. Preserve any real release build, package-shape, dependency-removal, and HTTP smoke
   commands only as a separately gated future validation option requiring explicit
   user approval. They must not authorize writing, deleting, cleaning, staging, or
   committing `dist_release/**` in this lane.
4. Keep the exact four-file candidate boundary and all product/Fee/parser/frontend/API/
   schema/database/real-data locks unchanged.

## Validation Performed

- Read `AGENTS.md`, the current board, this task, the reconciliation plan, Planner
  evidence, the exact candidate diff, browser entrypoint, static test, and root
  ignore rules.
- Confirmed `HEAD` is `add69823668d7ac4bf18645c688ce367a8fe0d42`; the index is empty.
- Confirmed the three tracked candidate hunks are limited to the browser PyInstaller
  spec, the Windows build script, and its static test. `git diff --check` reported
  only existing LF/CRLF notices. The candidate document and all bounded code/test
  files remain below the project's line limits.
- Confirmed `/dist_release/` is ignored and inspected it only through Git's
  ignore/status view; no artifact was opened, changed, removed, staged, or packaged.

## Next Legal Route

Route only to **Planner docs-only fix pass** for B1. Do not route Developer,
QA, or Integrator; implementation/package work remains unauthorized.

## B1 Plan Re-Gate

Date: 2026-07-22

Status: `reviewer_pass`

### Re-Gate Conclusion

- The exact candidate release_004 document now states the current board fact: no
  active task, with TASK_366A accepted at `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`.
- It expressly prohibits real browser-release execution, release-folder smoke,
  generated-output dependency probes, generated-output HTTP smoke, and every
  create/modify/delete/stage/commit action under `dist_release/**` during this
  planned-only lane. Those commands are retained only as future optional checks behind
  a separate explicit user approval.
- The exact package remains self-contained: the browser spec filters the three
  desktop-shell prefixes and excludes the four desktop-only runtime dependencies; the
  build script's timing wrapper preserves the existing action/error boundaries; the
  static test protects those textual contracts. No backend product, frontend product,
  API/schema/database, Fee, parser, Summary UI, or accepted-task residual is included.

### Re-Gate Validation

- Re-read the task, reconciliation plan, Planner evidence, candidate release plan,
  board, exact candidate diff, browser entrypoint, static tests, and ignore rules.
- The stale TASK_366A/current-task and generated-output authorization phrases have no
  remaining match in the active RELEASE_004 governance set.
- Exact candidate code/test diff remains limited to
  `packaging/connlab_browser_server.spec`, `scripts/build_windows_browser_release.ps1`,
  and `tests/unit/test_desktop_release_scripts.py`; the fourth candidate is the
  untracked release_004 plan. All four have no UTF-8 trailing whitespace and remain
  below line limits. The index and `dist_release/**` remain untouched.

## Next Legal Route

Recommend only **User approval for Developer planning-first**. Product/package
implementation remains unauthorized; do not route Developer implementation, QA, or
Integrator directly.

## Implementation-Readiness Gate

Date: 2026-07-22

Status: `reviewer_blocked / Planner docs-only fix required`

Implementation authorization: none.

### B2: Native filter and primary-error-safe timing are not yet controlling task/plan contracts

The reconciled board and evidence correctly record the passed plan gate, user-approved
Developer planning-first, and the static-only/no-artifact boundary. However, the
implementation-readiness contract remains incomplete in the controlling task and
reconciliation plan:

- The current candidate still filters after `collect_submodules("backend")` and uses
  `str.startswith()` with the tuple of excluded prefixes. The intended native PyInstaller
  `filter=` callback and exact `name == prefix or name.startswith(prefix + ".")`
  subtree boundary exist only in Developer planning-first evidence. The installed
  PyInstaller signature confirms `collect_submodules(package, filter=...)` is available,
  but the task/plan do not yet freeze its call shape or the sibling-name negative case.
- The candidate `Invoke-TimedStep` uses `Measure-Command` and writes timing only after a
  successful action. The intended Stopwatch plus `try`/`finally` contract that reports
  failed-step duration without allowing reporting failure to replace the action's
  primary error likewise exists only in Developer evidence. It is absent from the
  task/plan acceptance criteria and focused static test matrix.

Without those requirements in the controlling documents, a future implementation can
legitimately retain the current post-collection prefix filter and success-only timing,
which does not meet the declared readiness target.

## Required Planner Docs-Only Fix

Update the task, reconciliation plan, Planner/Developer evidence, and board wording as
needed; do not edit the three implementation candidates or execute any build:

1. Freeze `collect_submodules("backend", filter=is_browser_backend_submodule)` as the
   required recursive filter and require an exact module/subtree predicate, rejecting
   only `name == prefix` or `name.startswith(prefix + ".")`. Add positive and sibling
   negative static-test acceptance nodes plus the retained explicit packaged-server
   import and four Analysis excludes.
2. Freeze a single-action Stopwatch `try`/`finally` wrapper: report elapsed time for
   both success and failure; retain the original action/exit-code failure as the
   primary error if reporting itself fails; preserve skip behavior, action order,
   environment/location restoration, and all release-folder mutation semantics.
   Add focused static-test acceptance nodes for that source shape and error precedence.
3. Keep the implementation validation static-only: no release build, release-folder
   smoke, generated-output probe/HTTP smoke, or access to/mutation of
   `dist_release/**`. Preserve the exact candidate and external-residual locks.

## Validation Performed

- Read board, task, plan, Planner/Developer/reconciliation/Reviewer evidence, exact
  residual diff, candidate script/spec/static tests, and the local PyInstaller API.
- Confirmed the installed API accepts the `filter` parameter, while the current planned
  candidate has not yet adopted it and the current timer is not failure-reporting.
- Confirmed candidate diffs remain `24/2`, `76/51`, and `11/1`; no build, artifact,
  data, public-drive, attachment, staging, commit, or push operation occurred.

## Next Legal Route

Route only to **Planner docs-only fix pass** for B2. Do not request product/package
implementation approval or route Developer implementation, QA, or Integrator.

## Implementation-Readiness Re-Gate

Date: 2026-07-22

Status: `reviewer_pass`

Implementation authorization: none.

### B2 Closure

The controlling task, reconciliation plan, Planner evidence, and reconciliation
evidence now consistently freeze the missing implementation contract:

- PyInstaller must call
  `collect_submodules("backend", filter=is_browser_backend_submodule)` and use only
  exact module/subtree matching: `name == prefix` or
  `name.startswith(prefix + ".")`. Bare prefix matching and post-collection-only
  filtering are explicitly rejected, including a sibling-prefix negative assertion.
- `Invoke-TimedStep` must invoke the action once and use a Stopwatch with
  start/stop cleanup in `try`/`finally`, success and failure elapsed reporting, and
  primary action/exit-code error precedence over timing or reporting failures.
- The static test matrix now requires the native-filter placement, exact subtree and
  collision checks, retained packaged-server import/four excludes, and the timing
  success/failure, cleanup, and precedence checks.

The exact four-path candidate, static-only validation gate, line budgets, and the
prohibition on real builds, generated-output probes, and any `dist_release/**`
access or mutation remain unchanged.

## Validation Performed

- Re-read the board, task, reconciliation plan, Planner/Developer/reconciliation
  evidence, and current Reviewer evidence.
- Confirmed the controlling documents contain the B2 contract and have no active
  stale readiness wording.
- Confirmed candidate source diffs remain `24/2`, `76/51`, and `11/1`; targeted
  governance diff checks pass and the index is empty. No build, artifact, data,
  public-drive, attachment, stage, commit, or push action occurred.

## Next Legal Route

Route only to **User product/package implementation approval + Planner final
source-of-truth reconciliation**. Do not route Developer implementation, QA, or
Integrator directly.

## Implementation Gate

Date: 2026-07-22

Status: `reviewer_pass`

### Findings

No blocking findings.

- The browser spec now uses PyInstaller's native
  `collect_submodules("backend", filter=is_browser_backend_submodule)` call. Its
  predicate excludes only an exact configured module or dotted descendant; the
  static test proves `backend.desktop.shellfish` remains included. The explicit
  packaged-server import and all four desktop dependency excludes remain present.
- `Invoke-TimedStep` starts one Stopwatch, invokes the action once, and reports
  elapsed time from `finally`. Its extracted-helper test proves success and failed
  actions report time, a reporting failure does not mask an existing action error,
  and the action count is exactly one per invocation. The five existing release
  steps, four exit-code guards, skip branches, and restoration `finally` blocks
  remain intact.
- Candidate changes are limited to the authorized spec, script, static test, and
  release plan. No product/API/schema/frontend/real-data scope was absorbed. The
  `dist_release/**` lock was preserved and no release script main flow or real
  package build was executed.

### Verification

- `py -m pytest tests\\unit\\test_desktop_release_scripts.py -q`: `8 passed`.
- `py -m py_compile packaging\\connlab_browser_server.spec
  tests\\unit\\test_desktop_release_scripts.py`: passed.
- PowerShell `Parser.ParseFile` validation of the build script: clean; no main flow
  execution.
- Candidate diff and UTF-8 trailing checks: clean apart from existing LF/CRLF notices;
  index and `dist_release/**` status are empty.
- Rechecked source facts: native filter present, no bare-prefix predicate or
  post-collection helper, no `Measure-Command`, five timed calls, and four Analysis
  excludes. Current physical counts observed with UTF-8 `Get-Content` are spec 81,
  script 170, static test 149, and plan 261, all below the frozen limits.

## Next Legal Route

Route only to **QA static gate**. QA must remain static-only and must not run a real
release build, release-folder/generated-output smoke, dependency probe, HTTP smoke,
or access or mutate `dist_release/**`. Do not route Integrator directly.
