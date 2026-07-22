# RELEASE_004 Browser Packaging Performance Residual Reconciliation - Planner Evidence

Date: 2026-07-22

Role: Planner

Status: implementation authorized / pending Developer implementation

Task: `RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION`

Lane: `release-004-browser-packaging-performance-residual-reconciliation`

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none.
- `HEAD`: `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- `origin/master`: `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- Why allowed: Reviewer implementation-readiness re-gate passed and the user explicitly approved static-only product/package implementation. This Planner pass may align source-of-truth governance, but must not modify implementation files, run builds, access release artifacts, stage, commit, or push.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/release_003_local_browser_server_packaging_plan.md`
- `.gitignore`
- `docs/release_004_browser_release_packaging_performance_plan.md`
- `packaging/connlab_browser_server.spec`
- `scripts/build_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- Git commands: `git rev-parse HEAD`, `git rev-parse origin/master`, `git status --short`, `git diff --numstat`, targeted `git diff`, `git status --ignored --short -- dist_release`.

## Confirmed By User

- Current active task is none.
- Staging index is empty.
- `dist_release` is ignored and generated artifacts on disk must remain untouched.
- `TASK_366A_EXTERNAL_EXCEL_XLS_READ_COMPATIBILITY` is complete/accepted at local commit `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`; older wording in the candidate release_004 plan that called TASK_366A planned-only/current is superseded.
- Discovery is limited to four candidate files:
  - `packaging/connlab_browser_server.spec`
  - `scripts/build_windows_browser_release.ps1`
  - `tests/unit/test_desktop_release_scripts.py`
  - `docs/release_004_browser_release_packaging_performance_plan.md`
- Final authorization is limited to static-only product/package implementation across the exact release packaging scope; real release build, cleanup, staging, commit, push, real DB, public-drive, or source workbook access remains forbidden.

## Confirmed By Repository Evidence

- `.gitignore` contains `/dist_release/`.
- `git status --short` shows the three tracked release candidate files modified and the release_004 plan untracked.
- Candidate source diff stats:
  - `packaging/connlab_browser_server.spec`: `24` additions / `2` deletions.
  - `scripts/build_windows_browser_release.ps1`: `76` additions / `51` deletions.
  - `tests/unit/test_desktop_release_scripts.py`: `11` additions / `1` deletion.
- Candidate physical line counts:
  - `packaging/connlab_browser_server.spec`: 79
  - `scripts/build_windows_browser_release.ps1`: 152
  - `tests/unit/test_desktop_release_scripts.py`: 105
  - `docs/release_004_browser_release_packaging_performance_plan.md`: 122
- The spec candidate replaces direct broad hidden-import concatenation with `collect_browser_backend_submodules()` and excludes `webview`, `PyQt5`, `pythonnet`, and `clr_loader`.
- The script candidate wraps existing release steps in `Invoke-TimedStep` and keeps the same release folder naming, frontend guard, PyInstaller call, and release folder preparation behavior.
- The test candidate statically asserts timing output and browser spec filtering/excludes.

## Planner Inference

- The four files share one coherent owner: Release 004 browser packaging performance and dependency-bloat reduction.
- This should be a planned-only package/readiness lane, not a product lane and not a cleanup of `dist_release/**`.
- Static tests are the appropriate first validation gate. Real release builds can write large generated output and should require a separate explicit validation approval if needed later.

## Not Yet Confirmed

- Whether the user wants this residual packaged after Reviewer plan gate or discarded.
- Whether any later QA gate may run a real browser release build. Current planned boundary excludes it.

## Recommended Lane Decision

Create planned-only lane `RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION` and route Reviewer plan gate. Do not route Developer, QA, or Integrator.

## May Touch / Must Not Touch Summary

May Touch after future user approval:

- exact four candidate files
- task/plan/Planner evidence
- `docs/task_board.md` lane status hunk only

Must Not Touch:

- `dist_release/**`
- product backend/frontend/API/schema/database files
- Fee/default-fill residuals
- parser residuals
- Contact Measurement Summary UI residuals
- TASK_364A/TASK_363D old governance residuals
- real DB, public-drive files, source workbooks, release uploads, stage, commit, push

## B1 Docs-Only Fix

- Corrected `docs/release_004_browser_release_packaging_performance_plan.md` so TASK_366A is complete/accepted at `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`.
- Clarified this planned-only lane forbids real release build execution, release-folder smoke, dependency-removal probing against generated output, HTTP smoke from generated output, and any `dist_release/**` generation/modification/deletion/staging/commit.
- Moved real build and artifact smoke checks to a future explicit user-approved validation gate.
- Historical B1 checkpoint kept exact candidate scope, residual exclusions, and then-current implementation unauthorized state unchanged; this is superseded by the final authorization reconciliation below.

## Source-Of-Truth Reconciliation

Date: 2026-07-22

Status: `ready_for_reviewer_implementation_readiness`

- Reviewer B1 plan re-gate passed.
- User approved Developer planning-first.
- Developer docs-only planning-first complete.
- Historical source-of-truth checkpoint aligned board, task, plan, Planner evidence, Developer evidence checkpoint, and this reconciliation note to ready for Reviewer implementation-readiness; this is superseded by the final authorization reconciliation below.
- Product/package implementation was not authorized at that checkpoint.
- Frozen contracts remain unchanged: PyInstaller native recursive filter, primary-error-safe Stopwatch timing, exact May Touch/locks, static-only implementation gate, line budgets, and separate future generated-artifact gate.

## B2 Docs-Only Fix

Date: 2026-07-22

Status: `ready_for_reviewer_implementation_readiness_re_gate`

- Promoted the native PyInstaller recursive filter from Developer evidence into the controlling task/plan/evidence contract.
- Frozen call shape: `collect_submodules("backend", filter=is_browser_backend_submodule)`.
- Frozen predicate: exact module/subtree matching only, `name == prefix` or `name.startswith(prefix + ".")`; naked `startswith(prefix)` / `startswith(tuple)` is forbidden because it can collide with unrelated sibling names.
- Promoted the Stopwatch timing contract into controlling docs: one action invocation, start/stop cleanup, success and failure elapsed reporting, cleanup/finally behavior, and primary action/exit-code error precedence if timing/reporting fails.
- Frozen static tests in `tests/unit/test_desktop_release_scripts.py`: native filter before collection/Analysis, exact subtree and prefix-collision negative, four Analysis excludes, Stopwatch success/failure elapsed reporting, cleanup/finally behavior, and primary-error precedence.
- May Touch, exact four-path candidate scope, no-real-build/no-`dist_release/**` locks, static-only implementation gate, and line budgets remain unchanged.

## Final Authorization Reconciliation

Date: 2026-07-22

Status: `implementation_authorized_pending_developer`

- Reviewer implementation-readiness re-gate passed.
- User explicitly approved product/package implementation.
- Board, task, plan, Planner evidence, and reconciliation evidence are aligned to implementation authorized / pending Developer implementation.
- Authorized implementation remains static-only and limited to:
  - `packaging/connlab_browser_server.spec`
  - `scripts/build_windows_browser_release.ps1`
  - `tests/unit/test_desktop_release_scripts.py`
  - `docs/release_004_browser_release_packaging_performance_plan.md`
  - necessary lane governance evidence/status hunks.
- Frozen contracts remain unchanged: PyInstaller native recursive filter, exact subtree matching, prefix-collision negative, primary-error-safe Stopwatch timing, static test matrix, line budgets, and package isolation.
- Real release builds, release-folder smoke, generated-output dependency probes, generated-output HTTP smoke, and `dist_release/**` access-after-read, generation, modification, deletion, staging, or commit remain forbidden until a later explicit user-approved generated-artifact gate.

## Board Update

Board was updated only with release residual governance state. Current Active Task remains none; implementation is authorized only for the bounded static Developer pass.

## Validation Performed In This Planner Pass

- Read-only diff/status/HEAD checks.
- No product code/test implementation changes.
- No real release build.
- No `dist_release/**` cleanup, rewrite, staging, or package inclusion.
- No stage, commit, push.

## Next Legal Role

Developer implementation pass.
