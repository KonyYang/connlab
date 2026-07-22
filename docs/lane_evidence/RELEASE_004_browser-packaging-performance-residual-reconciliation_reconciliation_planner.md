# RELEASE_004 Browser Packaging Performance Residual Reconciliation - Source-Of-Truth Reconciliation

Date: 2026-07-22

Role: Planner

Status: complete / accepted after Integrator static package gate

Task: `RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION`

Lane: `release-004-browser-packaging-performance-residual-reconciliation`

Implementation authorization: completed as a static-only package; generated-artifact validation remains separately gated.

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none.
- Why allowed: Reviewer implementation-readiness re-gate passed and the user explicitly approved product/package implementation. The board/task/plan/evidence need final docs-only authorization reconciliation before routing Developer implementation.

## Recorded Gate Chain

- Reviewer B1 plan re-gate: passed.
- User approved Developer planning-first.
- Developer docs-only planning-first: complete.
- Planner B2 docs-only contract fix: complete.
- Reviewer implementation-readiness re-gate: passed.
- User explicit product/package implementation approval: recorded.
- Developer implementation, Reviewer, QA, and Integrator static package gates passed. The lane is complete/accepted.

## Frozen Contract Preserved

- PyInstaller native recursive filter for browser backend submodule discovery:
  `collect_submodules("backend", filter=is_browser_backend_submodule)`.
- Exact subtree matching only: `name == prefix` or `name.startswith(prefix + ".")`.
  Naked `startswith(prefix)` / `startswith(tuple)` matching is forbidden due sibling
  prefix-collision risk.
- Primary-error-safe Stopwatch timing around the existing release build actions:
  one action invocation, start/stop cleanup, success and failure elapsed reporting, and
  original action/exit-code failure preserved as primary even if timing/reporting
  cleanup fails.
- Exact May Touch remains the three release candidate files plus lane governance:
  - `packaging/connlab_browser_server.spec`
  - `scripts/build_windows_browser_release.ps1`
  - `tests/unit/test_desktop_release_scripts.py`
  - `docs/release_004_browser_release_packaging_performance_plan.md`
  - lane task/plan/evidence/board status hunks
- Static-only implementation gate remains: focused static pytest, py_compile, PowerShell parser-only validation, diff/trailing/line/scope/staging checks.
- Static tests must cover native filter before collection/Analysis, exact subtree and prefix-collision negative, Stopwatch success/failure elapsed reporting, cleanup/finally behavior, and primary-error precedence.
- Separate future generated-artifact gate remains required before any real release build, release-folder smoke, dependency probe, generated-output HTTP smoke, or `dist_release/**` generation/modification/deletion/staging/commit.
- Line budgets remain unchanged: spec <= 120, build script <= 210, static test module <= 180, plan/evidence <= 500.

## Final Authorization Reconciliation

- Authorized scope remains exactly four implementation paths plus necessary governance evidence:
  - `packaging/connlab_browser_server.spec`
  - `scripts/build_windows_browser_release.ps1`
  - `tests/unit/test_desktop_release_scripts.py`
  - `docs/release_004_browser_release_packaging_performance_plan.md`
- Developer implementation remains static-only. It may implement the native PyInstaller filter, exact subtree/prefix-collision safeguards, primary-error-safe Stopwatch timing, and static tests inside the frozen paths.
- This authorization does not permit real release builds, release-folder smoke, generated-output dependency probes, generated-output HTTP smoke, or `dist_release/**` access-after-read, generation, modification, deletion, staging, or commit.
- All external residual exclusions remain unchanged.

## Must Not Touch / Locked Paths

- No packaging spec, PowerShell script, or test implementation changes in this Planner pass.
- No real release build or release-folder smoke.
- No access, modification, deletion, staging, or commit of `dist_release/**`.
- No Fee/default-fill, parser, Contact Measurement Summary UI, TASK_364A/TASK_363D old governance residuals, frontend product code, API/schema/database, real DB/public-drive/source workbook/attachment, stage, commit, or push.

## Verification

- UTF-8 trailing scan: clean.
- `git diff --check`: clean except existing LF/CRLF warnings.
- Stale-status/scope scan: current effective governance no longer routes to Reviewer plan re-gate.
- Staging: empty.
- Candidate diff counts preserved from Developer planning-first: `24/2`, `76/51`, `11/1`.
- No release build/smoke/generated probe/HTTP smoke was run.

## Next Legal Role

User/Orchestrator. This closeout does not authorize or activate a generated-artifact/runtime gate.
