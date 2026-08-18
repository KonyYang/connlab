# RELEASE_004 Browser Packaging Performance Residual Reconciliation Plan

Date: 2026-07-22

Status: complete / accepted after Integrator static package gate

Task: `RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION`

Lane: `release-004-browser-packaging-performance-residual-reconciliation`

Implementation authorization: authorized for static-only Developer implementation

## Current Phase / Active Task / Role / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none.
- Current role: Integrator closeout.
- Why allowed: User requested a release-engineering residual discovery for exactly four candidate files and explicitly prohibited product implementation, cleanup, staging, commit, push, real release build, and `dist_release/**` mutation.

## User Goal Restatement

The user wants to decide whether the current browser release packaging residual is a valid independent package. The candidate should slim the local browser release by excluding desktop-only WebView dependencies from the browser server package and add timing output to the Windows release build script. The task must remain release packaging only, with `dist_release/**` treated as ignored generated output and with no product behavior, schema, API, frontend, Fee, Matrix, LTR, or real-file scope.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/release_003_local_browser_server_packaging_plan.md`
- `docs/release_004_browser_release_packaging_performance_plan.md`
- `.gitignore`
- `packaging/connlab_browser_server.spec`
- `scripts/build_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- Git status/diff facts for the exact candidate paths.

## Confirmed By User

- `HEAD` and `origin/master` are both `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- Current active task is none.
- Staging is empty.
- `dist_release` was accepted into root ignore and generated folders must remain untouched.
- `TASK_366A_EXTERNAL_EXCEL_XLS_READ_COMPATIBILITY` is complete/accepted at local commit `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`. Any candidate-plan wording that treated TASK_366A as planned-only/current is superseded by this source-of-truth.
- Reviewer B1 plan re-gate passed; User approved Developer planning-first; Developer docs-only planning-first complete.
- Planner B2 docs-only contract fix is complete; Reviewer implementation-readiness re-gate passed.
- User explicitly approved product/package implementation.
- Developer implementation, Reviewer, QA, and Integrator static package gates passed. The lane is complete/accepted; generated-artifact/runtime validation remains separately gated.
- This pass must review only four candidate files and must not submit product candidates.

## Confirmed By Repository Evidence

- `.gitignore` contains `/dist_release/`.
- `packaging/connlab_browser_server.spec` candidate diff is `24` additions / `2` deletions.
- `scripts/build_windows_browser_release.ps1` candidate diff is `76` additions / `51` deletions by `git diff --numstat`.
- `tests/unit/test_desktop_release_scripts.py` candidate diff is `11` additions / `1` deletion.
- `docs/release_004_browser_release_packaging_performance_plan.md` is an untracked 122-line candidate plan.
- Candidate physical line counts are:
  - `packaging/connlab_browser_server.spec`: 79
  - `scripts/build_windows_browser_release.ps1`: 152
  - `tests/unit/test_desktop_release_scripts.py`: 105
  - `docs/release_004_browser_release_packaging_performance_plan.md`: 122
- The candidate changes form one release-engineering package:
  - spec hidden-import filtering plus desktop-only excludes
  - PowerShell timing wrapper around existing release build steps
  - static tests for spec/script contract
  - plan document describing package bloat and timing goals

## Planner Inference

- This should be treated as a corrective/package lane under the existing browser release family, not as Fee, parser, frontend, Matrix, Settings, LTR, or product runtime work.
- The existing residual is coherent enough for a planned-only Reviewer plan gate.
- A real release build is not required for plan gate and should remain out of scope until separately approved because it writes build/dist output and can interact with local release artifacts.

## Not Yet Confirmed

- Whether the user wants this residual eventually packaged as-is, adjusted by Reviewer findings, or discarded.
- Whether a later validation gate should ever run the real release build; current plan assumes static tests only unless separately approved.

## Exact May Touch

Authorized static implementation/package May Touch:

- `packaging/connlab_browser_server.spec`
- `scripts/build_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- `docs/release_004_browser_release_packaging_performance_plan.md`
- `tasks/RELEASE_004_BROWSER_PACKAGING_PERFORMANCE_RESIDUAL_RECONCILIATION.md`
- `docs/release_004_browser_packaging_performance_residual_reconciliation_plan.md`
- `docs/lane_evidence/RELEASE_004_browser-packaging-performance-residual-reconciliation_planner.md`
- `docs/task_board.md` only for lane status governance

## Must Not Touch / Locked Paths

- `dist_release/**`: ignored generated artifact root; no delete, clean, rewrite, stage, commit, or package inclusion.
- `dist/**`, `build/**`, and `tmp/**`: no real release build or cleanup in Planner/Reviewer plan gate.
- `backend/**` except read-only release packaging entry references.
- `frontend/**` product code and API client.
- Fee/default-fill residuals, parser residuals, Contact Measurement Summary UI residuals, TASK_364A/TASK_363D old governance residuals, and all other mixed dirty hunks.
- API, schema, database, Settings, Matrix, LTR, Project lifecycle, Office gateways, real DB, public-drive files, source workbooks, operator files, network publishing, commit, push.

## Package Boundary

The package is self-contained only if all three code/test hunks and the release performance plan are treated together:

- The spec change supplies the actual dependency filtering and PyInstaller excludes. The controlling contract is PyInstaller's native recursive `collect_submodules("backend", filter=is_browser_backend_submodule)` callback, not post-collection filtering.
- The spec predicate must compare exact module/subtree boundaries with `name == prefix` or `name.startswith(prefix + ".")`; naked `startswith(prefix)` or `startswith(tuple)` behavior is rejected because it is vulnerable to sibling-prefix collisions.
- The script change supplies timing output and preserves existing build order/failure behavior. The controlling contract is a Stopwatch helper with start/stop and `finally` cleanup, success/failure elapsed reporting, and primary action/exit-code error precedence over timing/reporting errors.
- The test change guards the spec/script contract by static inspection, including exact subtree and prefix-collision negatives plus success/failure timing and primary-error-precedence assertions.
- The release_004 plan documents the rationale, risk, and validation expectations.

Do not split the spec and tests into separate packages. Do not combine this with unrelated release folders or product work.

## Validation Gate Draft

Reviewer plan gate:

- Confirm exact candidate whitelist and no hidden dependencies on product files.
- Confirm static tests are adequate for plan/readiness and do not run a real build.
- Confirm no `dist_release/**` artifacts are included.

Authorized static implementation/package checks:

```powershell
py -m pytest tests\unit\test_desktop_release_scripts.py -q
git diff --check -- packaging/connlab_browser_server.spec scripts/build_windows_browser_release.ps1 tests/unit/test_desktop_release_scripts.py docs/release_004_browser_release_packaging_performance_plan.md
```

Additional checks:

- UTF-8 trailing whitespace scan for exact candidate files.
- `git status --short -- dist_release` must show no staged or tracked release artifacts.
- Scope scan must exclude Fee, parser, Summary UI, backend product modules, frontend product modules, API/schema/database, real DB/files, and public-drive paths.
- No real `scripts/build_windows_browser_release.ps1` execution unless a future explicit user-approved validation gate allows generated output.
- No release-folder smoke, dependency-removal probe against generated release output, HTTP smoke from generated output, or `dist_release/**` generation/modification/deletion in the discovery/plan gate.

Required static assertions in `tests/unit/test_desktop_release_scripts.py`:

- The browser spec test must require `filter=is_browser_backend_submodule` at the `collect_submodules("backend", ...)` call site and must reject post-collection-only filtering.
- The browser spec test must require exact subtree matching with `name == prefix` and `name.startswith(f"{prefix}.")`; it must also include a prefix-collision negative proving a sibling name that only shares the prefix is not excluded.
- The browser spec test must retain explicit `backend.desktop.packaged_server` inclusion and the four Analysis excludes.
- The browser release script test must require Stopwatch start/stop, `try`/`finally`, elapsed reporting for success and failure paths, cleanup/finally behavior, and primary action/exit-code error precedence.
- The browser release script test must preserve existing assertions for action order, skip behavior, environment restoration, location restoration, release-folder mutation semantics, and no product/LTR/Settings leakage.

## Acceptance Criteria

- Browser release spec no longer uses the broad direct `collect_submodules("backend") + ...` hidden import pattern.
- Browser release spec uses PyInstaller's native recursive collection filter and not post-collection-only filtering.
- Browser release spec uses exact subtree matching and forbids naked prefix matching that can collide with sibling module names.
- Browser release spec keeps `backend.desktop.packaged_server`.
- Browser release spec excludes desktop-only browser-shell dependencies: `webview`, `PyQt5`, `pythonnet`, `clr_loader`.
- Browser release script reports `[time]` for the existing release steps on success and failure, while preserving the original action/exit-code failure as primary.
- Existing release build order and error propagation remain intact.
- Static release tests cover the new script/spec behavior.
- No real release artifact is created, modified, deleted, staged, or committed by this lane.
- Real release build and release-folder smoke are future optional gates only after explicit user approval.

## Merge Gate Draft

- Reviewer plan gate passes.
- User explicitly authorizes implementation/package.
- Reviewer/QA/Integrator evidence proves exact whitelist, no real release artifact package inclusion, no product scope, and clean diff/trailing/staging checks.

## Definition Of Ready

DoR for implementation authorization is satisfied. Reviewer implementation-readiness re-gate passed and the user explicitly approved static-only product/package implementation. Real release builds and generated-artifact validation remain excluded until a later explicit gate.

## Next Legal Role

User/Orchestrator. This closeout does not authorize or activate a generated-artifact/runtime gate.
