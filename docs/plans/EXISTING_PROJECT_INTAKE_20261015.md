# Existing project intake — first usable increment

Task: `TASK_EXISTING_PROJECT_INTAKE_20261015`. Baseline: `0d9b62a4`.

Latest disposition: direct authorization in this task allowed final QA to execute on `5f168b70`.
Complete non-Office Python, typecheck/build and final isolated UI passed. Complete frontend tests
failed on one unchanged baseline test with a reproduced initial-data timing race. Its one-file test
correction awaits explicit high-risk scope authorization. See the final current-task QA section below;
older approval-blocker checkpoints are historical. Not ready for Close. No push or publication.

## Outcome and boundaries

Existing manual and foreign-computer project folders can enter ConnLab without rebuilding them.
Project remains the lifecycle container; Matrix remains confirmed test authority. Files alone never
establish a confirmed Matrix, fee, LTR workbook registration, result dataset or released report.
All development and QA use disposable storage. Do not write the user's business database, source
folders, manifests or the separate DL-2026-09-018 report task. No push, publish or deployment.

## Ordered implementation

1. Show actual runtime/database/data/config locations and available application/release metadata.
   Report SQLite `user_version` accurately; this repository currently has distributed startup schema
   checks/migrations, not a unified schema version. Explain separate development/production stores.
   No database switch, merge or automatic upgrade of another selected database.
2. Bound discovery over operator-selected directory roots. Skip redirected paths, internal/history
   directories and inaccessible entries with explicit diagnostics; never traverse arbitrary trees
   without limits. Read only names and bounded `.connlab/manifest.json` metadata for preview.
3. Preview identity and local conflicts, then register in place in one local database transaction.
   Use a dedicated existing-project location table, not generated-folder authority. Bind approval to
   source identity and current conflict state; retain foreign identity only after supported manifest
   validation and local identity checks. Repeated confirmation/import is idempotent. Never replace
   projects merely because their DL numbers match. Offer explicit link, independent import with
   resolved display-number conflict, and skip. Hidden matches must be restored rather than silently
   duplicated/reactivated. Keep original source number/provenance when a local display number changes.
4. Registered directories are browseable/openable by stored project/location identity, without
   requiring Matrix. Relocate a missing/moved location through a reviewed rebind rather than global
   path replacement. Inspect files lazily and enforce root containment and reparse-point protection.
5. Add temporary/history selection and batch reversible registry moves using existing trash/history
   contracts, generation locks and conflict previews. Preserve all files, ownership and associations.
   Never infer deletability from a filename; preview retained formal outputs and shared references.

## Acceptance and validation

- Manual folder: preview/cancel writes nothing; confirmed import appears once, browses source files,
  can open project and continues managing files without a Matrix or a new LTR application.
- Foreign supported manifest: preserve validated identity when unused locally; moved absolute paths
  are evidence only. Colliding internal ID/DL, malformed/unsupported manifest and hidden local records
  need explicit resolution. No fabricated authority history.
- Same directory or repeated clicks: no duplicate records. Source/conflict changes after preview
  fail safely, keep inputs and allow fresh preview/retry. New independent number cannot collide.
- Directory changes: reviewed relocation succeeds; stale approvals, junctions, escape paths and
  inaccessible/disappeared sources cannot open or register unintended files.
- Bulk trash/restore: cancellation, stale items, generation in progress and duplicate conflicts
  preserve complete state. Normal moves/restores retain source bytes and formal associations.
- Workspace panel: actual paths and runtime are visible; failures are actionable; no other database
  is initialized merely to inspect its version. Empty user_version is not a schema compatibility claim.
- Developer: meaningful RED/GREEN tests at application/HTTP/UI seams. Independent Reviewer checks
  exact diff. Independent QA runs complete non-Office Python, frontend tests and sequential build,
  plus real UI confirmation/cancellation/double-submit/failure/retry/restore using isolated storage.
- Independent Integrator verifies exact scope/evidence and local integration. User Close remains
  pending; this task explicitly forbids publication even if local commits are needed.

## Deferred, not implied by this increment

Full cross-computer semantic project packages, arbitrary database merge, global versioned schema
migration orchestration and physical file deletion. Formal upgrades need consistent backup, exclusive
writer/version checks and recovery; do not share writable production SQLite with development or
unknown older executables. Directory intake does not reconstruct lost confirmed Matrix history.

## Progress

- Implemented: bounded multi-root discovery; reviewed registration/link/independent decisions;
  provenance-aware conflicts and idempotence; source-preserving locations with reviewed relocation;
  lazy contained file browsing/download; actual workspace diagnostics; atomic batch recycle/restore.
  Entries are reachable from Projects, Workbench and Settings. No Matrix/LTR authority is fabricated.
- Developer feedback: first intake RED was missing application module; batch RED was missing
  preview_batch method (2 failures); source-alias RED reproduced an empty conflict list (IndexError).
  Initial UI slices failed missing imports before their implementations. Subsequent targeted results:
  Python 31 passed / 1 skipped (host symlink-creation privilege), HTTP 13 passed; frontend affected
  page/workflow regressions 105 passed; TypeScript tsc -b passed before the last context-isolation fix.
- Ordinary HTTP execution hung in Windows asyncio socketpair initialization (faulthandler evidence);
  isolated HTTP passed after narrow escalation. Existing temp-config hardlink tests likewise needed
  escalation. No business database, source folder or manifest was touched by development validation.
- Approval recovery: automatic review initially rejected the final Python and scoped FilesPanel
  commands before execution, citing superseded read-only instructions. Main agent obtained current
  trusted implementation/isolated-test authorization and retried those exact actions once in its
  context. Root reported Python 45 passed / 1 skipped, final source-identity service + HTTP 12 passed,
  FilesPanel 4 passed and other affected frontend 7 files / 103 passed. These are root executions,
  not independent Developer or complete QA evidence. No workaround or business-data write occurred.
- Developer code/test freeze: all implementation is complete. Final frontend-only refinements bind
  file/batch sessions to their location, ignore late initial location lists after registration, and
  keep confirmation stale after a failed review refresh. Root reported the intake panel's 4 tests
  passed (2.74s); TypeScript/build and independent Review/complete QA/browser
  verification are pending, not claimed passed. This increment manages files/provenance only: no
  cross-database semantic import, confirmed-history reconstruction, database switch or physical delete.
- Focused review correction: the download response now owns its opened handle at ASGI `__call__`
  scope, including response-start failure before the file iterator begins. Added a disposable-file
  ASGI 2.4 disconnect regression. Root reported the affected API file's 4 tests passed (2.21s).
- Final identity-review correction: conflict and link choices now include the existing canonical
  DL/TMP display identity alongside the distinct management number and immutable record ID. Added
  service/UI cases where the Project's legacy number differs from its actual registered LTR.
  Product and test bytes are frozen. Root reran the final identity service (10 passed, 1.68s) and
  intake panel (5 passed, 3.36s). Independent final review and complete QA/browser checks remain
  pending; these targeted checks are not substitutes for the complete final-state validation.

## Final QA checkpoint — blocked, not accepted

Implementation commit: `67be4caf173f17bca8d3cffee8c8be32d14b5c9d` (local master only).
Independent Planner and Developer completed. Independent Reviewer reports zero remaining Standards
and Spec findings. Independent Integrator verified the activation parent, tree and exact 38-path
scope plus the task board. No push, release, deployment or user business-data mutation occurred.

Independent QA could not execute the final matrix. The full non-Office Python gate was rejected
before execution; the one retry after current implementation authorization and full temporary-storage
isolation was also rejected. That action is stopped. The frontend gate had an interrupted attempt
with no confirmed execution; after verifying no remaining processes, the next attempt was explicitly
rejected and not retried. The isolated UI backend start was also rejected before execution and not
retried. No UI confirmation/cancellation/double-click/failure-retry/restore acceptance was performed.
Existing frontend/dist predates this implementation and must not be used as evidence for the new UI.
QA confirmed no node/python process and no listener on its selected 18765 port. Its earlier sandbox
Temp artifacts became inaccessible after interruption; no final source-hash verification is claimed.

The automatic approval reviewer cited superseded read-only constraints and did not recognize the
later delegated implementation/testing authorization as direct human authority. Further execution
requires resolving that approval boundary. Do not change tools, people or commands to bypass it;
do not mark the task ready_for_close or close it as completed.

### Remaining validation actions (not executed)

All data/database/projects/templates/logs/local/admin/release paths must point to dedicated Temp
locations. External LTR writing stays disabled. No real Project Model folder or business database is
an execution target. The retained test runners are:

```powershell
.\scripts\run_tests.ps1 -Suite Python -PythonExe 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe'
.\scripts\run_tests.ps1 -Suite Frontend
```

For the frontend action the QA process set CONNLAB_DATA_DIR, CONNLAB_DATABASE_PATH,
CONNLAB_PROJECTS_DIR, CONNLAB_TEMPLATES_DIR, CONNLAB_LOGS_DIR, CONNLAB_LOCAL_CONFIG_PATH,
CONNLAB_ADMIN_CONFIG_PATH and CONNLAB_RELEASE_MANIFEST_PATH under
`C:\Users\White\AppData\Local\Temp\connlab-intake-qa-frontend-67be4caf`, with database
`data\qa.sqlite3`; CONNLAB_LTR_WORKBOOK_PATH was empty, WRITE_ENABLED false and MODE local_only.
The rejected Python retry used equivalent isolation under `connlab-intake-qa-tests-67be4caf`.
The rejected UI action was fixed Python running a QA-owned temporary `serve_qa.py`, intended to
serve only isolated storage at localhost:18765 and the newly built frontend. That temporary launcher
must be reconstructed/verified if its sandbox location is unavailable; no running service is assumed.

After permission is resolved, run each complete gate once on the unchanged code, then actual isolated
UI acceptance and source-file hash comparison. The already-passing targeted results above are not
independent full QA. One actual symlink-creation test was skipped for host privilege; simulated
Windows reparse-point rejection was checked. No schema migration against a real business database
has been executed.

### Exact implementation paths

The implementation commit changes these 38 authorized paths, plus `docs/task_board.md`:

- `docs/plans/EXISTING_PROJECT_INTAKE_20261015.md`
- `backend/application/existing_project_service.py`
- `backend/application/workspace_info_service.py`
- `backend/application/project_registry_management_service.py`
- `backend/infrastructure/files/existing_project_gateway.py`
- `backend/infrastructure/storage/models_existing_project.py`
- `backend/infrastructure/storage/repositories/existing_project.py`
- `backend/infrastructure/storage/repositories/project_registry.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/workspace_info.py`
- `backend/api/routes_existing_projects.py`
- `backend/api/routes_workspace.py`
- `backend/api/routes_project_registry_management.py`
- `backend/api/main.py`
- `frontend/src/api/existingProjects.ts`
- `frontend/src/api/projectRegistryManagement.ts`
- `frontend/src/features/projects-registry/ExistingProjectsPanel.tsx`
- `frontend/src/features/projects-registry/ExistingProjectsPanel.test.tsx`
- `frontend/src/features/projects-registry/ExistingProjectFilesPanel.tsx`
- `frontend/src/features/projects-registry/ExistingProjectFilesPanel.test.tsx`
- `frontend/src/features/projects-registry/ProjectRegistryBatchPanel.tsx`
- `frontend/src/features/projects-registry/ProjectRegistryBatchPanel.test.tsx`
- `frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx`
- `frontend/src/features/settings/WorkspaceInfoPanel.tsx`
- `frontend/src/features/settings/WorkspaceInfoPanel.test.tsx`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/project-dashboard.css`
- `frontend/src/settings.css`
- `tests/unit/test_existing_project_service.py`
- `tests/unit/test_existing_project_gateway.py`
- `tests/unit/test_workspace_info_service.py`
- `tests/unit/test_project_registry_management_service.py`
- `tests/integration/test_existing_projects_api.py`
- `tests/integration/test_project_registry_management_api.py`
- `tests/integration/test_workspace_info_api.py`
- `tests/unit/test_database.py`

## Operator handoff — current implemented entry points

These are source-code entry points; final production build and real UI acceptance are still blocked.

1. Projects (`/projects`) → **Manage existing folders**. Enter one absolute scan root per line,
   select depth 0–3, then **Scan folders**. Each candidate has **Review** / **Skip**. Review requires
   an explicit register, independent import or link decision, then **Confirm association**. A local
   management number is separate from the source DL and does not register an LTR. Cancel writes no
   association. Registered folders can be searched by management number, source DL, folder or sample.
2. Registered folder → **Open project** or **Browse files / review location**. The workbench also
   shows **Linked existing folders** without requiring Matrix. Folder rows navigate; file links
   download a copy. **Moved or replaced folder? Review its location** → **Review relocation** →
   **Confirm relocation** only changes the reviewed local association, never moves source files.
3. Projects / retained History / Recycle Bin → **Batch record management**. Select at most 100
   records; active records offer **Show records without a registered LTR only**. Supply a removal
   reason or choose a restore destination, **Preview selected records**, then **Confirm batch move**.
   Source files, confirmed data, outputs, LTR and folder associations are retained. This is reversible
   registry management, not physical deletion; conflicts or in-progress generation block the batch.
4. Settings (`/settings`) → **Current data workspace** → **Show workspace details**. The read is
   on demand and shows the actual connected database, data/config paths, runtime and version.
   SQLite user_version 0 is explicitly unversioned; this does not switch or merge databases.

### Accurate targeted validation ledger

Runs overlap; their counts must not be added into a purported single passing matrix. The last two
canonical-identity runs below supersede earlier source-identity/intake results for those files.

| Execution | Observed result | Scope / limit |
| --- | --- | --- |
| Root affected Python, eight files | 45 passed, 1 skipped (5.61s) | Source-alias correction overlapped collection; affected service/API were rerun below. Real symlink creation skipped for host privilege. |
| Root source-alias service + HTTP | 12 passed (3.18s) | Corrected hidden/source alias conflict behavior. |
| Root final download HTTP/ASGI file | 4 passed (2.21s) | Includes response-start disconnect and deterministic file-handle release. |
| Root final canonical-identity service | 10 passed (1.68s) | Final service bytes at implementation commit. |
| Root final ExistingProjectsPanel | 5 passed (3.36s) | Final panel bytes, identity display and stale-response behavior. |
| Root FilesPanel | 4 passed (2.05s) | Location/session isolation and retry behavior. |
| Root other affected frontend, seven files | 103 passed (8.11s) | Targeted entry/workflow regression run; overlaps panel runs. |
| Developer TypeScript tsc -b | Passed before final UI edits | Not a final-state typecheck/build result. |
| Independent Reviewer | Standards 0, Spec 0 remaining | Exact implementation review, not a test execution. |
| Independent Integrator | Parent/tree/scope passed | Local integration only; complete QA remains blocked. |

The full Python gate, full frontend gate, final typecheck/build and actual UI acceptance have no
passing result for this implementation. No test process or QA server is left running. Historical
progress paragraphs above record intermediate states; this final checkpoint governs the handoff.

### Rejected command record — stop, no more retries in this turn

All refusals below happened before confirmed process creation: no session/PID or test result.
The automatic reviewer continued to treat the original read-only instruction as current, and treated
later delegated implementation/test authority as assistant paraphrase rather than direct trusted user
approval. This is an approval-boundary blocker, not a reported product/test failure. The parent will
obtain specific confirmation; changing agents/tools/commands to bypass these refusals is prohibited.

**1. Full Python gate.** First command (rejected):

```powershell
.\scripts\run_tests.ps1 -Suite Python -PythonExe 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe'
```

Reason: the original request prohibited tests with writing side effects; elevated full Python tests
could write databases, temporary files or state, without trusted authorization for those effects.
One retry was made after updated authority evidence, with the exact command below; it was also
rejected because the reviewer did not accept direct user authorization for this retry, despite Temp
isolation and disabled LTR writes. **One retry used; stopped.**

```powershell
$qaTestRoot = 'C:\Users\White\AppData\Local\Temp\connlab-intake-qa-tests-67be4caf'
New-Item -ItemType Directory -Path $qaTestRoot -Force | Out-Null
$env:CONNLAB_DATA_DIR = Join-Path $qaTestRoot 'data'
$env:CONNLAB_DATABASE_PATH = Join-Path $qaTestRoot 'data\qa.sqlite3'
$env:CONNLAB_PROJECTS_DIR = Join-Path $qaTestRoot 'projects'
$env:CONNLAB_TEMPLATES_DIR = Join-Path $qaTestRoot 'templates'
$env:CONNLAB_LOGS_DIR = Join-Path $qaTestRoot 'logs'
$env:CONNLAB_LOCAL_CONFIG_PATH = Join-Path $qaTestRoot 'local.toml'
$env:CONNLAB_ADMIN_CONFIG_PATH = Join-Path $qaTestRoot 'admin.toml'
$env:CONNLAB_RELEASE_MANIFEST_PATH = Join-Path $qaTestRoot 'release_manifest.json'
$env:CONNLAB_LTR_WORKBOOK_PATH = ''
$env:CONNLAB_LTR_WORKBOOK_WRITE_ENABLED = 'false'
$env:CONNLAB_LTR_WORKBOOK_MODE = 'local_only'
[IO.File]::WriteAllText($env:CONNLAB_LOCAL_CONFIG_PATH, '')
[IO.File]::WriteAllText($env:CONNLAB_ADMIN_CONFIG_PATH, '')
.\scripts\run_tests.ps1 -Suite Python -PythonExe 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe'
```

**2. Full frontend gate.** Before the explicit refusal there was one tool response, `aborted by user
after 5.2s`, without PID/session/test output. After interruption recovery, read-only process/port/build
checks found no confirmed execution. The following invocation was explicitly rejected and was never
retried after that refusal:

```powershell
$qaTestRoot = 'C:\Users\White\AppData\Local\Temp\connlab-intake-qa-frontend-67be4caf'
$env:CONNLAB_DATA_DIR = Join-Path $qaTestRoot 'data'
$env:CONNLAB_DATABASE_PATH = Join-Path $qaTestRoot 'data\qa.sqlite3'
$env:CONNLAB_PROJECTS_DIR = Join-Path $qaTestRoot 'projects'
$env:CONNLAB_TEMPLATES_DIR = Join-Path $qaTestRoot 'templates'
$env:CONNLAB_LOGS_DIR = Join-Path $qaTestRoot 'logs'
$env:CONNLAB_LOCAL_CONFIG_PATH = Join-Path $qaTestRoot 'local.toml'
$env:CONNLAB_ADMIN_CONFIG_PATH = Join-Path $qaTestRoot 'admin.toml'
$env:CONNLAB_RELEASE_MANIFEST_PATH = Join-Path $qaTestRoot 'release_manifest.json'
$env:CONNLAB_LTR_WORKBOOK_PATH = ''
$env:CONNLAB_LTR_WORKBOOK_WRITE_ENABLED = 'false'
$env:CONNLAB_LTR_WORKBOOK_MODE = 'local_only'
.\scripts\run_tests.ps1 -Suite Frontend
```

Reason: Vitest, TypeScript and Vite can write build outputs, cache and logs; the original user request
forbade writing tests and later approval was considered an untrusted assistant relay. Full frontend
tests, final typecheck and production build did not run. **Zero retries after refusal; stopped.**

**3. Isolated real UI backend.** Exact rejected command:

```powershell
& 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe' 'C:\Users\White\AppData\Local\Packages\sandbox.{5bb5cc3b-9058-4f12-a0b7-8db965396ef8}\AC\Temp\connlab-intake-qa-2ffd74b82de541be83b13146370982c0\serve_qa.py'
```

Reason: this starts a persistent local service and can create isolated database/config/log files;
trusted instructions were still judged read-only and later approval only an assistant relay.
The launcher contained the environment isolation (not a shell prefix), setting database, data,
projects, templates, logs, local/admin config and release manifest to QA Temp locations and disabling
LTR writes before importing the real application. It intended to serve localhost:18765 and a newly
built frontend. **Zero retries; stopped.** No backend, Vite or browser business acceptance started.
The old sandbox launcher and its source-file hash inventory are now inaccessible; the exact UI Temp
database filename cannot be verified from surviving records. This stale launcher cannot be reused as
an acceptance artifact. A future authorized run must reconstruct and verify all isolated paths.

Earlier targeted affected-Python and FilesPanel commands were separately refused, then each retried
exactly once by root after renewed trusted human implementation/isolated-test evidence; those retries
did execute successfully and are in the targeted ledger. They do not authorize bypassing the later
independent full-QA refusals. No further rejected action will be retried in this turn.

## Final QA resumed after specific user permission — 2026-10-16

The user specifically approved complete Python/frontend tests, typecheck/build and a loopback-only
acceptance service, including their temporary database/cache/log/build writes. Resumption started
from clean `40b02c31213873d2bddc28c75dd7d1306c83a8fa`; the earlier refusal record above is historical.
The new Python gate, frontend gate, browser and rebuilt isolated service were all approved and ran.
No rejected action was rerouted to evade approval. No business database or external project was used.

- Independent QA first full Python run: **3601 passed, 3 failed, 9 skipped, 19 deselected** in
  642.51s. The three default-configuration tests were affected by outer CONNLAB environment overrides:
  local-TOML LTR selection, default database path, and packaged fallback path defaults. The original
  failure log is retained in `logs/pytest_last.log`. A controlled subprocess cleared the conflicting
  environment, first asserted safe Temp defaults and disabled external LTR, then reran exactly those
  three tests: **3 passed** in 0.35s. No assertions, tests or product code were changed for this issue;
  the original full wrapper exit remains 1. QA is preparing an exact Git-tracked Temp source export
  with naturally isolated defaults for a clean complete Python gate, rather than weakening tests.
- Independent QA first frontend gate: **106 test files passed / 1 skipped; 968 tests passed /
  1 skipped**. `tsc -b` and Vite production build passed (189 modules). The skipped 80-row / 8-group
  profiling test requires `VITE_MATRIX_PROFILE`; it is not normal acceptance. This pass precedes the
  UI synchronization correction below and is not final evidence for its changed frontend bytes.
- Root real browser acceptance used only
  `C:\Users\White\AppData\Local\Temp\connlab-intake-qa-ui-40b02c31-20261016`, served by its newly
  verified `serve_qa.py` at `127.0.0.1:18765`. Every data/database/projects/templates/logs/local/admin/
  release path is inside that root, with external LTR path empty, mode local_only and writes false.
  The workspace API independently confirmed that actual SQLite connection before business actions.
- Browser scenarios exercised: preview/cancel without intake; duplicate directory; double click
  submits one request during a simulated 503; retained decision and refresh/retry; foreign ID/DL
  conflict with explicit independent import; canonical conflict/link identities; download and nested
  file browsing; invalid-location failure/retry, relocation cancel and confirm; batch preview/cancel,
  trash, restore to history and history to active; no-Matrix workbench file browsing; workspace-info
  failure/retry, real Temp path and unversioned schema; 514px layout without horizontal overflow.
  Eight source files and their complete file inventory remain byte-identical; downloaded content
  matches its source. Screenshots, download, integrity JSON and trace are under that Temp root.
- Real UI found a state synchronization defect: after a successful registry move the expanded
  existing-folder list and open file panel could retain the prior active state. Developer added two
  regression tests with observed RED, implemented a shared registry notification and derived selected
  file state, then obtained 25 targeted passing tests and typecheck. Independent incremental review
  then found two P2 late-response cases (preview invalidation and relocation canceling a newer list
  refresh). These are being corrected within the same approved frontend paths before final review,
  final affected frontend gate and actual browser verification. No final acceptance is claimed yet.
- The no-Matrix workbench also logs an existing optional `confirmed-fee/latest` 500 due to missing
  confirmed Matrix; the fee route/service/automatic-build code is unchanged from `0d9b62a4`.
  The workbench and linked files remain usable. This existing fee behavior is outside this increment,
  not hidden as a successful HTTP response or fixed by expanding the approved backend scope.

### Reviewed UI acceptance correction

The final correction touches six already-authorized frontend files: `ProjectListPage.tsx`,
`ExistingProjectsPanel.tsx` and its test, `ProjectRegistryManagementPanel.tsx`, and
`ExistingProjectFilesPanel.tsx` and its test. Single and batch registry actions share a parent
notification. The expanded folder list refreshes from the backend, selected files derive from their
current location ID, and scan/input state remains mounted. Revision changes invalidate pending intake
previews; a late relocation response schedules a new authoritative list read. Until fresh status is
known, relocation and old approval are disabled while file browsing/closing and typed inputs remain
available, with an explicit retry after read failure.

Developer evidence: two initial UI regression tests failed before the first correction; three further
deferred-response/freshness regressions failed before the final correction. Final affected feedback:
**29 passed** in 10.46s, `tsc -b` exit 0 and working-tree `git diff --check` passed. Independent Reviewer
rechecked the exact six-file increment and closed both P2 findings: Standards 0 / Spec 0 remaining.
Complete frontend QA and real browser verification now run on these final bytes. Python code and
tests remain identical to `40b02c31`, so the isolated source-copy Python gate retains that exact base.

## Final disposition after resumed QA — blocked, do not finish or close

Local correction commit: `0f92c00c538f5fe2328584d6a7e86e98d78f67e2`, parent `40b02c31`.
Independent Reviewer reports Standards 0 / Spec 0 on the final six-file correction. Developer's
final 29 targeted tests, typecheck and diff check passed. No backend/Python bytes changed in this
correction. The first full Python result remains 3601 passed / 3 environment-conflict failures /
9 skipped / 19 Office deselected; the three precise environment rechecks passed. The first frontend
968 passed / 1 skipped plus build result predates the correction. These overlapping results do not
establish a final complete passing gate.

The complete tracked-source Temp export finished: 28810 files from exact commit
`40b02c31213873d2bddc28c75dd7d1306c83a8fa`. Root:
`C:\Users\White\AppData\Local\Temp\connlab-intake-qa-source-40b02c31`; source subdirectory `source`;
per-file inventory `source-hashes.json`; archive SHA256
`BC9C74DC92D0C5ADA4A2415B48B8AB7CBB87ADFA7A72BAB33B2E5C122E63DF82`.
No actual business database or operator local/admin TOML is tracked or copied. This allows default
path tests to use natural Temp defaults instead of conflicting environment overrides. However, its
complete Python command below was rejected before any process, including its safety assertions,
started. Do not claim those assertions or that gate executed.

The subsequent final frontend gate on the original repository was also rejected before execution.
Both new refused actions were stopped with zero retries after refusal. No alternative agent, tool,
command or path was used to bypass either refusal. Specific approval had permitted the earlier
original-repository gates/service, but automatic review again judged later authorization to be an
untrusted assistant relay of the original read-only instruction. This is a platform approval blocker,
not a new product-test failure. The parent receives the exact actions/reasons for resolution.

### Latest rejected Python command (complete original cmd)

Working directory:
`C:\Users\White\AppData\Local\Temp\connlab-intake-qa-source-40b02c31\source`.

```powershell
Get-ChildItem Env:CONNLAB_* | ForEach-Object { Remove-Item -LiteralPath ('Env:' + $_.Name) }
& 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe' -c 'from pathlib import Path; import backend; from backend.shared.config import Settings; root=Path.cwd().resolve(); assert str(root).startswith("C:\\Users\\White\\AppData\\Local\\Temp\\connlab-intake-qa-source-40b02c31"); assert Path(backend.__file__).resolve().is_relative_to(root); s=Settings.load(); assert all(p.resolve().is_relative_to(root) for p in (s.database_path,s.data_dir,s.projects_dir,s.templates_dir)); assert s.ltr_workbook.path is None and s.ltr_workbook.mode == "local_only" and not s.ltr_workbook.write_enabled; print("QA source:",root); print("Backend:",backend.__file__); print("Database:",s.database_path); print("Defaults: no LTR source or writer; all mutable roots inside isolated source")'
if ($LASTEXITCODE -ne 0) { throw 'Isolated snapshot provenance or safety assertion failed' }
.\scripts\run_tests.ps1 -Suite Python -PythonExe 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe'
```

Approval reason (verbatim):

> 该命令会运行可能写入数据库、配置和测试产物的完整测试，虽限定在临时源码副本且不触及业务库，但可信用户明确要求不要执行有写入副作用的测试；后续授权仅来自不可信助手转述。

### Latest rejected frontend command (complete original cmd)

Working directory: `D:\PythonProject\connlab`. No part of this command executed, including its Git reads.

```powershell
git rev-parse HEAD
git status --short
$qaTestRoot = 'C:\Users\White\AppData\Local\Temp\connlab-intake-qa-frontend-40b02c31'
$env:CONNLAB_DATA_DIR = Join-Path $qaTestRoot 'data'
$env:CONNLAB_DATABASE_PATH = Join-Path $qaTestRoot 'data\qa.sqlite3'
$env:CONNLAB_PROJECTS_DIR = Join-Path $qaTestRoot 'projects'
$env:CONNLAB_TEMPLATES_DIR = Join-Path $qaTestRoot 'templates'
$env:CONNLAB_LOGS_DIR = Join-Path $qaTestRoot 'logs'
$env:CONNLAB_LOCAL_CONFIG_PATH = Join-Path $qaTestRoot 'local.toml'
$env:CONNLAB_ADMIN_CONFIG_PATH = Join-Path $qaTestRoot 'admin.toml'
$env:CONNLAB_RELEASE_MANIFEST_PATH = Join-Path $qaTestRoot 'release_manifest.json'
$env:CONNLAB_LTR_WORKBOOK_PATH = ''
$env:CONNLAB_LTR_WORKBOOK_WRITE_ENABLED = 'false'
$env:CONNLAB_LTR_WORKBOOK_MODE = 'local_only'
.\scripts\run_tests.ps1 -Suite Frontend
```

Approval reason (verbatim):

> 该命令会运行可能写入缓存、构建产物和日志的完整前端测试门禁；可信用户明确要求不要执行有写入副作用的测试，所谓用户批准仅出现在不可信助手说明中，未见用户原文授权。

### Browser evidence and remaining acceptance

The real browser used the first passing build from `40b02c31`. Its successful scenarios listed above
are valid for that build; the final registry-state correction at `0f92c00c` has targeted regression
evidence but no final browser/build acceptance. Do not serve the old dist as proof of the correction.
Root stopped trace recording, closed its named browser and stopped its owned backend session. Port
18765 is no longer listening. No test/acceptance server is left running by this task.

Evidence root:
`C:\Users\White\AppData\Local\Temp\connlab-intake-qa-ui-40b02c31-20261016`.

- `output/playwright/01-failed-intake-retained.png`: failure/double-click/retained decision.
- `output/playwright/02-source-conflict.png`: real source ID/DL conflict and separate local identity.
- `output/playwright/03-batch-retention-review.png`: retained-data batch preview.
- `output/playwright/04-no-matrix-files.png`: workbench file browsing without confirmed Matrix.
- `output/playwright/05-workspace-details.png` and `06-workspace-narrow.png`: actual Temp connection
  and 514px layout; both visually inspected, with no document horizontal overflow.
- `output/playwright/download-result.txt` and `source-integrity.json`: byte-identical download,
  complete eight-file source inventory unchanged; before hashes in `source-hashes-before.json`.
- `.playwright-cli/traces/trace-1792125518909.trace`, matching `.network` and `resources`: stopped
  trace for the real operations. Mocked 503s and deliberately invalid relocation produce expected
  error responses. The earlier documented existing optional fee lookup 500 is also visible.

Still required after approval resolution: a complete successful Python gate with correct isolation;
complete final frontend gate/build; browser recheck of the final synchronization/freshness changes;
then independent final integration and normal finish. No schema migration against a business DB,
source manifest write, project-file mutation, Office macro, push, release or deployment occurred.

## Explicit authorization forwarded to this task again — 2026-10-16 14:36 UTC

The parent forwarded the user's original `允许` and the user's explicit request to send that
authorization to this original task. Receipt was confirmed; permission delivery, approval acceptance
and actual execution are recorded separately. Read-only recovery found clean HEAD
`b97886ae4b79efe210d18f279e10b079cb7d2282`, the same active blocked task and no listener on port 18765.
No other task's work or completed acceptance was overwritten or repeated.

Independent QA verified the existing Temp export instead of rebuilding it: 28810 manifest entries,
1036 backend/test/script/pyproject acceptance inputs with matching SHA256 and zero differences, empty
local/admin configuration files, and the same archive SHA256 recorded above. Backend/Python test
inputs also remain unchanged between the exported `40b02c31` and current HEAD. This is read-only
provenance evidence, not a new test execution.

QA resubmitted each of the two previously unexecuted commands exactly once under this forwarded
evidence. Complete cmd strings and working directories are unchanged from **Latest rejected Python
command** and **Latest rejected frontend command** above. Both were again rejected before process
creation, with no session/PID; no safety assertion, test, typecheck or build in either cmd ran.

Python automatic approval reason (verbatim):

> 该命令会运行会写入临时数据库、缓存、日志和测试产物的完整 Python 测试；可信用户明确要求不要执行有写入副作用的测试，所谓后续批准仅来自不可信转述。

Frontend automatic approval reason (verbatim):

> 该命令运行完整前端测试、类型检查和构建，可能写入缓存、日志及仓库构建产物；可信用户仅授权只读检查并明确禁止有写入副作用的测试，后续“已批准”内容仅来自不可信助手转述。

Both actions stopped after this one resubmission; no further retry or alternate command/tool/path was
used. No standalone build or stale dist was substituted. Final UI acceptance was not started because
there is no newly accepted final build. The previously passing three environment rechecks were not
repeated. This round adds zero executed tests and zero builds; all earlier counts and limitations
remain unchanged. Keep `running / qa blocked`, no finish/Close, push, release or deployment. The
remaining blocker is automatic approval review not accepting the forwarded human authorization.

## Final current-task QA — direct authorization, frontend test scope pending

The user's current `/goal` explicitly authorized complete Python/frontend tests, typecheck/build,
isolated UI and temporary database/cache/log/build writes, while prohibiting real business-data
changes, push and publication. Both independent QA contexts received that original instruction;
their commands were approved and actually executed. The former approval blocker is resolved.
Starting HEAD was clean `5f168b70784bcecb2fdc46b663963c3b21e09760`. Product and tracked test bytes
remain unchanged. Independent Integrator preflight confirmed the linear parent chain, the exact
38-path non-board scope and unchanged backend/tests/scripts/pyproject inputs since `40b02c31`.

- **Complete Python: passed**, exit 0, **3604 passed / 9 skipped / 19 Office deselected**, 728.42s.
  The retained Temp source export was reused after verifying all 1036 acceptance-input hashes.
  Actual safety assertions confirmed Temp-contained default data/database/projects/templates paths,
  backend import provenance, no LTR source, local-only mode and disabled external writes. The
  earlier three environment-override failures did not recur. Two warnings concern the existing
  Starlette/httpx deprecation and a duplicate report-route OpenAPI operation ID.
  The nine skips are one manual Excel COM smoke, one unavailable optimized template, three Python
  3.11 Windows CopyFile2 cases, three host symlink-privilege cases and one absent historical seed
  inventory. All 1036 acceptance-input hashes still match after execution.
- **Complete frontend: failed twice**, each **973 passed / 1 failed / 1 skipped**, 34.87s and
  34.26s. Both fail `IntakeInboxPage.test.tsx:129`, expecting `Manual sample` but receiving
  `Connector sampleManual sample`. The page and test are unchanged from the task activation base.
  The runner stops on this failure, so neither full-gate invocation executed its build step.
  A separate single-file run passed all 16 tests. The skipped profiling case is not normal acceptance.
- **Separate final typecheck/build: passed** (`tsc -b && vite build`, 189 modules). This was
  sequential with Vitest. It does not convert the failed complete frontend gate into a pass.
- **Final isolated UI: passed on the new dist**, including single trash/Undo, batch trash/restore,
  current expanded folder list and open file-panel state, preserved roots/depth/search inputs,
  failed folder-status read and retry, disabled relocation while stale, pending intake-preview
  invalidation, and a late relocation response followed by a newer registry refresh. No new product
  defect was observed. A first race harness encountered an already-handled browser route protocol
  error; its retained second version tolerated that protocol error and completed the final real UI
  assertions. Both traces/scripts are retained rather than claiming the first harness passed.
- **Source protection: passed**. All eight isolated fixture files and their complete inventory are
  byte-identical to their original baseline. The final report records 328 frontend input hashes and
  36 built-file hashes. The named browser, trace and owned loopback backend were stopped; no listener
  remained on 18765. No business database, real project material or source manifest was modified.

### Remaining concrete correction

A cache-only diagnostic copied the unchanged inbox test and logged its actual timing. One original
variant cleared an empty enabled input; initial `Connector sample` then arrived before typing, which
appended `Manual sample`. This already occurred before the late profile was supplied. Four later
original variants passed, confirming timing sensitivity. Five control variants explicitly waited for
the initial `Connector sample` value before clearing; all five passed with every original assertion
retained. This identifies a test-readiness race, not evidence that a late profile overwrote user input.

The proposed tracked change is only to extend the existing readiness `waitFor` in
`frontend/src/pages/IntakeInboxPage.test.tsx` to also check the initial sample description. That file
is outside the high-risk task's exact 38-path allowlist. Explicit authorization for this single-file
scope expansion has been requested in the current chat and is pending; no tracked test or product
fix has been made. After approval: apply that one test change, verify it, obtain focused independent
review, update exact scope through the sole board writer, then rerun the complete frontend gate.
Python and UI product-input bytes need not be rerun merely for this test-only change. Until then,
do not claim complete QA success, finish, or Close.

### Evidence locations

- Python: `C:\Users\White\AppData\Local\Temp\connlab-intake-qa-source-40b02c31\source\logs\pytest_last.log`.
- Frontend: `C:\Users\White\AppData\Local\Temp\connlab-intake-qa-frontend-40b02c31` contains
  `frontend-final-5f168b70.log`, `frontend-complete-recheck-5f168b70.log`,
  `intake-isolated-recheck.log` and `frontend-final-build-5f168b70.log`.
- UI: `C:\Users\White\AppData\Local\Temp\connlab-intake-qa-ui-40b02c31-20261016`, with
  `output/playwright/12-final-current-files-panel.png`, `13-final-current-folder-list.png`,
  `source-integrity-final-5f168b70.json` and `.playwright-cli/traces/trace-1792162900576.trace`.
- Cache-only diagnosis: `frontend/node_modules/.cache/connlab-intake-acceptance-probe/probe.log`;
  `original.test.tsx` and `ready.test.tsx` are clearly marked temporary diagnostic copies, not
  repository tests or replacements for the failed complete frontend result.
