# RELEASE_004 Browser Packaging Performance Residual Reconciliation - Developer Evidence

Date: 2026-07-22

Role: Developer implementation

Status: `ready_for_review`

Task: `RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION`

Lane: `release-004-browser-packaging-performance-residual-reconciliation`

Implementation authorization: authorized for the bounded static-only package.

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled
  foundation.
- Current active board task: none.
- Accepted TASK_366A baseline:
  `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`.
- Audited repository HEAD:
  `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- Reviewer B1 plan re-gate is `reviewer_pass`; the user explicitly approved this
  Developer planning-first pass.
- Superseded before Planner reconciliation: the board previously still said pending
  Reviewer plan re-gate, so the next legal role was Planner source-of-truth
  reconciliation rather than product implementation. Planner reconciliation is now
  complete, and the next legal role is Reviewer implementation-readiness.

## Read-Only Evidence Audited

- `AGENTS.md`, task board, task execution/review governance.
- Release 004 plan and Planner/Reviewer evidence.
- Accepted HEAD and current residual diffs for:
  - `packaging/connlab_browser_server.spec`
  - `scripts/build_windows_browser_release.ps1`
  - `tests/unit/test_desktop_release_scripts.py`
- `backend/desktop/packaged_server.py`, `packaged_launcher.py`, path-picker and shell
  import references.
- Installed PyInstaller 6.21.0 `collect_submodules` signature and local source.
- `pyproject.toml` release/desktop dependency declarations.

No release script, spec, product test, release build, release-folder smoke, generated
dependency probe, or generated HTTP smoke was executed.

## Confirmed Candidate Facts

- The three tracked candidate residuals are limited to `24/2`, `76/51`, and `11/1`
  additions/deletions respectively; the release plan is the fourth untracked candidate.
- Accepted browser spec broadly collects all backend submodules. The residual filters
  desktop names after collection and adds Analysis exclusions for `webview`, `PyQt5`,
  `pythonnet`, and `clr_loader`.
- Browser `packaged_server` does not import desktop launcher/path picker/shell. Those
  modules own the PyWebView imports and are browser-only package exclusions.
- The Fee export child branch remains part of browser server behavior and must not be
  removed by broad Office/Fee exclusions.
- The residual PowerShell helper wraps the five existing build actions and improves
  pytest environment restoration. It currently writes elapsed time only after a
  successful `Measure-Command` return.
- Existing static tests read source text only; they do not execute PyInstaller or the
  build script.

## Planning Refinements

### Native recursive filtering

The local PyInstaller API supports `filter=` and applies it before recursively visiting
subpackages. The implementation plan therefore replaces post-collection filtering with
`collect_submodules("backend", filter=is_browser_backend_submodule)`. Exact module or
subtree matching uses `name == prefix` or `name.startswith(prefix + ".")`; it does not
use a loose string prefix that could exclude an unrelated sibling module.

The browser server remains explicitly present in hidden imports, and Analysis retains
the four desktop runtime excludes. No manual backend allowlist is introduced in this
bounded lane.

### Timing and primary-error precedence

The plan freezes a Stopwatch-based `Invoke-TimedStep` with reporting in `finally`.
Every action runs exactly once; successful and failed actions both report elapsed time;
the original action exception or explicit exit-code failure continues to propagate.
Skipped tests/frontend steps retain their existing skip output and do not report a fake
duration.

Existing action order, arguments, release paths, mutation behavior, frontend guard,
environment restoration, location restoration, and final success output remain fixed.

### Static-only implementation gate

The later implementation gate may run only:

- the existing static release-script test module;
- Python syntax compilation of spec/test;
- PowerShell parser-only validation;
- exact diff/trailing/physical-line/whitelist/staging checks.

It must not run a real build or make a package-shape/runtime claim. A generated-artifact
gate requires separate explicit user approval with output and rollback boundaries.

## Exact May Touch

Product/test candidates:

1. `packaging/connlab_browser_server.spec`
2. `scripts/build_windows_browser_release.ps1`
3. `tests/unit/test_desktop_release_scripts.py`

Planning/governance candidates:

4. `docs/release_004_browser_release_packaging_performance_plan.md`
5. This lane's Developer/Planner/Reviewer/reconciliation evidence and responsible-role
   board status hunk.

All other paths are locked. The three mixed residual files require hunk-level handling;
there is no permission to clean or stage unrelated worktree changes.

## Line Budget

UTF-8 physical counts including blank lines at planning-first audit:

- spec: 93
- PowerShell script: 169
- static test module: 129
- plan before this refinement: 177

Future limits are spec 120, script 210, test 180, and each governance document 500.
Blank-line suppression is forbidden.

## Risks And Rollback

- Static evidence cannot prove actual package size, build duration, hidden-import
  completeness, or runtime success. Those remain explicit residual risk.
- Over-broad exclusion could break packaged runtime; the plan limits exclusions to the
  three proven desktop modules and four desktop dependency roots.
- Timer changes could mask action errors; the frozen `try/finally` design preserves the
  primary exception and only adds output.
- Rollback before generated validation is source-only and limited to the exact lane
  hunks. No `dist_release/**` cleanup is needed or authorized.
- A future generated validation failure must not promote a release or trigger ad hoc
  artifact deletion.

## Planning-First Validation

- Product/package/test files modified by this Developer pass: none.
- Real release build, generated folder smoke, dependency probe, generated HTTP smoke:
  not run.
- Real DB, public drive, attachment, source workbook, `dist_release/**`: not accessed or
  modified by this pass.
- Stage/commit/push: none; index remained empty.
- Plan/evidence UTF-8 trailing-whitespace, no-index diff-check, scope/status, physical
  line, and staging-empty checks completed as follows:
  - refined plan: 275 physical lines;
  - Developer evidence before this closeout note: 161 physical lines;
  - UTF-8 trailing whitespace: clean;
  - no-index diff-check: no whitespace errors, only the repository's LF/CRLF notice;
  - tracked residual diff counts remained exactly `24/2`, `76/51`, and `11/1`;
  - targeted status contained only the three pre-existing residuals plus the two
    planning documents;
  - staging index: empty.

## Planning-First Historical Blocker Summary

Superseded by the implementation evidence below. Planner reconciliation recorded the
passed Reviewer plan re-gate, user-approved Developer planning-first, and Developer
planning-first completion; implementation was still unauthorized at that point.

## Planning-First Historical Next Legal Role

The next role at that point was Reviewer implementation-readiness. This historical route
is superseded by the current checkpoint below.

## Authorized Implementation

- `connlab_browser_server.spec` now supplies
  `filter=is_browser_backend_submodule` directly to `collect_submodules`.
- The predicate rejects only an exact excluded module or its dotted descendants. The
  sibling `backend.desktop.shellfish` remains included, proving there is no naked-prefix
  collision.
- `backend.desktop.packaged_server` remains explicit and the four Analysis exclusions
  remain `webview`, `PyQt5`, `pythonnet`, and `clr_loader`.
- `Invoke-TimedStep` uses one Stopwatch and one action invocation. It captures the
  primary action error, stops/reports in `finally`, suppresses a reporting error only
  when a primary action error already exists, then rethrows that primary error.
- The existing five actions, four `$LASTEXITCODE` guards, skip behavior, pytest
  environment restoration, frontend location restoration, release paths, and folder
  mutation order remain unchanged.

## TDD Evidence

Initial static module run: `3 failed, 5 passed`.

- missing Stopwatch source contract;
- failed action emitted no `[time]` line under the old `Measure-Command` helper;
- spec did not use native `filter=is_browser_backend_submodule`.

After the minimal spec/script implementation, the module passed `8 passed`. The timer
test executes only the extracted helper in a child PowerShell process and proves:

- successful and failed actions both emit elapsed output;
- success/failure/reporting-failure scenarios invoke each action exactly once;
- the action's `primary failure` / `action wins` error remains visible;
- a reporting failure does not replace an existing primary action error.

The filter test parses only the spec's constant/predicate AST and proves exact module,
dotted child, and sibling-prefix behavior without invoking PyInstaller.

## Implementation Validation

- `py -m pytest tests/unit/test_desktop_release_scripts.py -q`: `8 passed`.
- `py -m py_compile packaging/connlab_browser_server.spec tests/unit/test_desktop_release_scripts.py`:
  passed.
- PowerShell `Parser.ParseFile` syntax check: clean; script main flow not executed.
- UTF-8 physical lines including blanks:
  - spec: 95 / limit 120;
  - build script: 187 / limit 210;
  - static test: 179 / limit 180.
- Final diff/trailing/scope/staging results are recorded in the closeout below.
- Real release build, release-folder smoke, dependency probe, generated HTTP smoke,
  and `dist_release/**` access/mutation: none.
- Real DB, public drive, attachment, source workbook, stage, commit, push: none.

## Current Blocker Summary

None for Reviewer implementation gate. Static evidence does not prove actual build
duration, package size, dependency absence, or runtime health; those remain explicitly
outside this lane until a separate generated-artifact authorization.

## Current Next Legal Role

Reviewer implementation gate only. Do not route QA or Integrator directly.

## Final Closeout

- Final focused pytest rerun: `8 passed`.
- Final Python compile and PowerShell parser-only checks: passed.
- Final physical lines: spec 95, script 187, static test 179, plan 322 before this
  closeout update, evidence 231 before this closeout update; all within frozen limits.
- Final tracked candidate diff counts relative to accepted HEAD: spec `26/2`, script
  `94/51`, static test `78/17`. The larger test diff includes only the authorized static
  contracts plus a mechanical `_read_text()` extraction used to stay under 180 lines.
- Exact candidate diff-check and UTF-8 trailing-whitespace scan: clean except existing
  LF/CRLF notices.
- Native-filter content scan rejects bare `name.startswith(prefix)` and the build script
  no longer contains `Measure-Command`.
- Targeted status contains only the three authorized residuals plus plan/evidence;
  staging and real-data status are empty.
- No build script/spec main execution, release artifact access, `dist_release/**`
  operation, real DB/file access, stage, commit, or push occurred.
