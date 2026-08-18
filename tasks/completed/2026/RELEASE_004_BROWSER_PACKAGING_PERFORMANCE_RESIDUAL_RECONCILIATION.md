# RELEASE_004 Browser Packaging Performance Residual Reconciliation

Date: 2026-07-22

Status: complete / accepted after Integrator static package gate

Lane: `release-004-browser-packaging-performance-residual-reconciliation`

Role: Integrator closeout

Implementation authorization: completed as a static-only package; generated-artifact validation remains separately gated.

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none, per accepted `docs/task_board.md` HEAD at `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- Why allowed: User requested an independent Planner Discovery for the self-contained browser release packaging residual. This pass may create planned-only governance and route Reviewer plan gate, but must not implement, stage, commit, push, delete release artifacts, or run a real release build.

## User Goal

Assess the current browser release packaging residual as an independent release-engineering package. Determine whether the four-file candidate can become a planned-only package/readiness lane, freeze the exact scope and validation contract for Reviewer plan gate, and keep `dist_release/**` as ignored local generated output outside every package.

## Candidate Residual Files

Future May Touch, if later approved:

- `packaging/connlab_browser_server.spec`
- `scripts/build_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- `docs/release_004_browser_release_packaging_performance_plan.md`
- `tasks/RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION.md`
- `docs/release_004_browser_packaging_performance_residual_reconciliation_plan.md`
- `docs/lane_evidence/RELEASE_004_browser-packaging-performance-residual-reconciliation_planner.md`
- `docs/task_board.md` only for lane status governance

## Confirmed Repository Evidence

- `HEAD` and `origin/master` are both `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- Staging is empty.
- Root `.gitignore` includes `/dist_release/`.
- `TASK_366A_EXTERNAL_EXCEL_XLS_READ_COMPATIBILITY` is complete/accepted at local commit `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`; any prior wording that described TASK_366A as planned-only/current is superseded.
- Reviewer B1 plan re-gate passed; User approved Developer planning-first; Developer docs-only planning-first is complete.
- Planner B2 docs-only contract fix is complete; Reviewer implementation-readiness re-gate passed.
- User explicitly approved product/package implementation.
- Developer implementation, Reviewer, QA, and Integrator static package gates passed. The lane is complete/accepted; generated-artifact/runtime validation remains a separately gated future option.
- The candidate release residual changes the browser-server PyInstaller spec to filter desktop-only backend prefixes and exclude `webview`, `PyQt5`, `pythonnet`, and `clr_loader`.
- The candidate release script adds `Invoke-TimedStep` around tests, frontend build, PyInstaller check, PyInstaller packaging, and release folder preparation.
- The candidate test file adds static assertions for the spec filter/excludes and build timing output.
- The untracked `docs/release_004_browser_release_packaging_performance_plan.md` describes the same purpose: reduce browser package bloat and expose release step timings.

## Planned Scope

This lane is a release packaging residual reconciliation lane. It is now authorized for a narrow static-only browser release optimization after Reviewer plan/readiness gates and explicit user implementation/package approval.

Allowed implementation candidate behavior:

- Keep browser release behavior and operator URL unchanged.
- Keep `backend.desktop.packaged_server` as the browser server entry.
- Filter browser hidden imports through PyInstaller's native recursive `collect_submodules("backend", filter=is_browser_backend_submodule)` callback, not by collecting the entire backend and filtering the returned list afterward.
- Match excluded backend modules by exact module or subtree only: `name == prefix` or `name.startswith(prefix + ".")`. Naked `name.startswith(prefix)` / `name.startswith(tuple)` semantics are forbidden because they can exclude unrelated sibling names that merely share a textual prefix.
- Add PyInstaller excludes for desktop-only runtime dependencies.
- Add timing output around existing build steps with a primary-error-safe Stopwatch helper: one action invocation, elapsed-time reporting on success and failure, cleanup in `finally`, and original action/exit-code failure preserved as the primary error even if timing/reporting fails.
- Add or keep static release-script/spec tests that do not execute a real packaging build.

## Must Not Touch

- Fee/default-fill residuals.
- Parser residuals.
- Contact Measurement Summary UI residuals.
- TASK_364A/TASK_363D old governance residuals.
- Other board/task/evidence mixed changes.
- Frontend product code.
- API, schema, database, Settings, Matrix, Fee, LTR, Project lifecycle, Office gateway, or public-drive workflows.
- `dist_release/**` contents except read-only ignore/status inspection.
- Real DB, real public-drive files, source workbooks, or operator files.
- Network publishing, remote push, release upload, or real packaging output mutation.

## Locked Paths

- `dist_release/**` is ignored local generated output and must not be staged, deleted, cleaned, or rewritten by this lane.
- `backend/**`, `frontend/**`, `data/**`, `.agents/**`, `docs/project_management/**`, real operator folders, and public-drive paths stay locked unless a future release lane explicitly re-gates them.

## Validation Gate Draft

Reviewer plan gate:

- Review exact four-file candidate boundary and this task/plan/evidence.
- Confirm no product behavior, data authority, or frontend UI scope is included.
- Confirm `dist_release/**` remains ignored generated output and excluded from package.

Authorized static implementation/package validation:

- `py -m pytest tests\unit\test_desktop_release_scripts.py -q`
- `git diff --check -- packaging/connlab_browser_server.spec scripts/build_windows_browser_release.ps1 tests/unit/test_desktop_release_scripts.py docs/release_004_browser_release_packaging_performance_plan.md`
- UTF-8 trailing whitespace scan over candidate files.
- Package isolation scan proving only the exact whitelist is touched.
- Staging-empty or exact staged-whitelist check, depending on role.
- No real release build unless a later user-approved validation gate explicitly allows it.
- No release-folder smoke, dependency-removal probe against generated release output, HTTP smoke from generated output, or `dist_release/**` generation/modification/deletion in this planned-only lane.

Static test acceptance for `tests/unit/test_desktop_release_scripts.py`:

- Browser spec node requires `filter=is_browser_backend_submodule` on `collect_submodules("backend", ...)`, rejects direct broad concatenation and post-collection-only filtering, requires exact subtree matching with `name == prefix` / `name.startswith(f"{prefix}.")`, and includes a prefix-collision negative such as a sibling module name that shares a prefix but is not inside the excluded subtree.
- Browser spec node retains explicit `backend.desktop.packaged_server` hidden import and all four Analysis excludes: `webview`, `PyQt5`, `pythonnet`, and `clr_loader`.
- Browser build-script node requires Stopwatch start/stop, `try`/`finally`, success and failure elapsed reporting, cleanup/finally behavior, and primary-error/exit-code precedence. It also preserves skip behavior, action order, environment/location restoration, release-folder mutation semantics, and source-only validation.

## Merge Gate Draft

- Reviewer plan gate pass.
- Reviewer implementation-readiness re-gate pass.
- User explicit approval before Developer/package implementation.
- Reviewer/QA or Integrator gate must prove exact whitelist, no `dist_release/**`, no product code, no real data/file mutation, and no hidden mixed residual absorption.

## Definition Of Ready

DoR for implementation authorization is satisfied. The candidate files share one release-packaging purpose, have concrete boundaries, have a static test path, passed Reviewer implementation-readiness re-gate, and received explicit user implementation/package approval. This authorization does not permit real release builds or generated artifact smoke.

## Next Legal Role

User/Orchestrator. This closeout does not authorize or activate a generated-artifact/runtime gate.
