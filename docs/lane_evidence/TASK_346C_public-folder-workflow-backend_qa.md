# TASK_346C Public Folder Workflow Backend - QA Evidence

Status: qa_pass
Date: 2026-06-30
Role: QA / Smoke Owner
Task: `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`
Lane: `public-folder-workflow-backend`

## Scope

QA executed temp-dir-only backend/API validation for the TASK_346C public folder workflow backend after Reviewer implementation re-gate pass.

No product source, tests, board, packaging files, real local/public folders, or LTR workbook files were modified by QA. This QA pass only created this evidence file.

## Sources Re-read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND.md`
- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_planner.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_reconciliation_planner.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- Reviewer callback from the current delegation prompt
- TASK_346C backend/API implementation and focused tests:
  - `backend/application/public_folder_year_resolver.py`
  - `backend/application/public_folder_path_resolver.py`
  - `backend/application/public_folder_workflow_service.py`
  - `backend/infrastructure/files/public_folder_workflow_gateway.py`
  - `backend/infrastructure/storage/repositories/public_folder_workflow.py`
  - `backend/api/routes_public_folder_workflow.py`
  - `tests/unit/test_public_folder_year_resolver.py`
  - `tests/unit/test_public_folder_workflow_service.py`
  - `tests/unit/test_public_folder_workflow_gateway.py`
  - `tests/integration/test_public_folder_workflow_api.py`
  - `tests/integration/test_public_folder_workflow_migration.py`

## Current Phase / Task Authorization

- Current phase from `docs/task_board.md`: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task from `docs/task_board.md`: `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`.
- QA gate is allowed by the delegation because Reviewer implementation re-gate passed and QA is required.

## Validation Commands

Focused TASK_346C backend/API suite:

```powershell
py -m pytest tests\unit\test_public_folder_year_resolver.py tests\unit\test_public_folder_workflow_service.py tests\unit\test_public_folder_workflow_gateway.py tests\integration\test_public_folder_workflow_api.py tests\integration\test_public_folder_workflow_migration.py -q
```

Result:

```text
19 passed in 2.01s
```

Old public-drive/default regression:

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py tests\integration\test_public_drive_upload_api.py tests\integration\test_api_default_dependencies.py -q
```

Result:

```text
20 passed in 1.90s
```

Python compile:

```powershell
py -m py_compile backend\application\public_folder_workflow_service.py backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\infrastructure\files\public_folder_workflow_gateway.py backend\infrastructure\storage\repositories\public_folder_workflow.py backend\api\routes_public_folder_workflow.py backend\api\dependencies.py backend\api\main.py
```

Result: passed.

Package diff check:

```powershell
git diff --check -- backend/api/dependencies.py backend/api/main.py backend/api/routes_public_folder_workflow.py backend/application/public_folder_path_resolver.py backend/application/public_folder_workflow_service.py backend/application/public_folder_year_resolver.py backend/infrastructure/files/public_folder_workflow_gateway.py backend/infrastructure/storage/models.py backend/infrastructure/storage/repositories/__init__.py backend/infrastructure/storage/repositories/public_folder_workflow.py tests/unit/test_public_folder_year_resolver.py tests/unit/test_public_folder_workflow_service.py tests/unit/test_public_folder_workflow_gateway.py tests/integration/test_public_folder_workflow_api.py tests/integration/test_public_folder_workflow_migration.py docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md
```

Result: passed with existing LF/CRLF warnings only for:

- `backend/api/dependencies.py`
- `backend/api/main.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/__init__.py`

Trailing whitespace scan on TASK_346C package files:

```powershell
rg -n "[ \t]$" <TASK_346C package files>
```

Result: no matches.

Static no-real-folder scan:

```powershell
rg -n "D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject" <TASK_346C backend/API/test files>
```

Result: no matches.

Static test write scan:

```powershell
rg -n "open\(|write_text\(|write_bytes\(|shutil\.|copytree|move\(|os\.replace|mkdir\(" tests/unit/test_public_folder_year_resolver.py tests/unit/test_public_folder_workflow_service.py tests/unit/test_public_folder_workflow_gateway.py tests/integration/test_public_folder_workflow_api.py tests/integration/test_public_folder_workflow_migration.py
```

Result: file writes/mkdir operations are confined to `tmp_path` or temporary directories in focused tests.

Future-scope/static scan notes:

- No StepInstance, Report generation, AI review, frontend API client, Projects registry, or Matrix Editor implementation strings were found in TASK_346C package files.
- Expected non-blocking textual matches:
  - `backend/application/public_folder_workflow_service.py` contains required confirmation `no_encryption_or_permissions_v1`, which documents that Submit v1 does not implement encryption or permissions.
  - `backend/api/dependencies.py` contains existing public-drive upload dependency wiring and existing read-only LTR workbook lookup comments; these are not TASK_346C real workbook writes.

Forbidden-scope status:

```powershell
git status --short -- frontend frontend/src/api/client.ts frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/matrix-editor .agents docs/project_management temp_agents_stash.md docs/packaging_notes.md pyproject.toml backend/desktop dist_release packaging scripts/build_windows_desktop_release.ps1 scripts/smoke_windows_desktop_release.ps1
```

Result:

```text
 M docs/packaging_notes.md
 M pyproject.toml
?? backend/desktop/packaged_launcher.py
?? backend/desktop/packaged_static.py
?? backend/desktop/runtime_paths.py
?? dist_release/
?? packaging/
?? scripts/build_windows_desktop_release.ps1
?? scripts/smoke_windows_desktop_release.ps1
?? temp_agents_stash.md
```

Interpretation: forbidden frontend/API-client/Projects/Matrix/.agents/docs_project_management paths showed no changes. Listed release/packaging files and `temp_agents_stash.md` are external residuals and must remain excluded from TASK_346C packaging.

## Temp-dir Backend/API Smoke

QA ran an additional temp-dir-only smoke using real `PublicFolderWorkflowService` and `PublicFolderWorkflowGateway`, with roots created under `C:\Users\White\AppData\Local\Temp\connlab_task346c_qa_*`. The temporary directories were disposable and were removed when the script exited.

Observed service smoke:

- Sync preview status: `ready`.
- Sync execute status: `completed`.
- Managed local files were copied to `PublicProject\Open\2026\<project folder>`.
- Submit preview status: `ready`.
- Submit execute status: `completed`.
- Public Open folder no longer existed after Submit.
- Public Closed file existed after Submit.
- Backend workflow state set `sync_locked=True`.
- Pull preview status: `ready`.
- Pull execute status: `completed`.
- Pull target was a local history folder beside the current local folder.
- Existing current local file remained preserved.
- Operation audit sequence recorded: `sync`, `submit`, `pull`.

B1 unmanaged Public Open conflict smoke:

- After a managed Sync, QA added `human-extra.txt` directly under temp Public Open.
- Submit preview returned `status=conflict`, `next_action=none`.
- Conflict copy: `Public Open file is not managed by ConnLab; remove or sync through ConnLab before Submit.`
- Submit execute rejected with the same conflict.
- Public Open remained intact.
- `human-extra.txt` remained in Public Open.
- Public Closed was not created.

Stale preview smoke:

- QA took a ready Submit preview, then added unmanaged `human-extra.txt`.
- Submit execute with the old preview hash rejected with `Public folder preview is stale.`
- Public Open remained intact.
- Public Closed was not created.

Missing root/path blocker smoke:

- `PublicFolderPathResolver.resolve(...)` with a missing public root raised `Public Project locations must be an existing directory.`
- The missing public root was not created.

API route smoke with dependency override and temp-dir real service:

- `POST /api/projects/P1/public-folder-workflow/sync/preview` -> `200`, `status=ready`.
- `POST /api/projects/P1/public-folder-workflow/sync/execute` -> `200`, `status=completed`.
- After adding unmanaged `human-extra.txt` under Public Open:
  - `POST /api/projects/P1/public-folder-workflow/submit/preview` -> `200`, `status=conflict`.
  - `POST /api/projects/P1/public-folder-workflow/submit/execute` -> `409`, detail `Public Open file is not managed by ConnLab; remove or sync through ConnLab before Submit.`
- Public Open remained intact and Public Closed was not created.

## Coverage Mapping

- Public folder year resolver priority/blocker behavior: covered by `tests/unit/test_public_folder_year_resolver.py`.
- Open/Closed path resolver containment and missing/config blocker behavior: covered by focused tests and QA missing-root smoke.
- Sync preview/execute copies managed local files to Public Open safely: covered by focused tests and QA temp-dir service/API smoke.
- Submit preview/execute moves managed Open package to Closed only after valid `preview_hash` and no conflicts: covered by focused tests and QA success smoke.
- Submit lock behavior: covered by focused tests and QA success smoke (`sync_locked=True`, Sync preview blocked after Submit).
- Submit unmanaged Public Open conflict: covered by B1 regression tests, QA service smoke, and QA API smoke.
- Pull preview/execute preserves local history and does not silently overwrite current local folder: covered by focused tests and QA success smoke.
- Stale preview hash rejection: covered by focused tests and QA stale preview smoke.
- Old public-drive/default regression: covered by `20 passed`.

## QA Result

QA gate: pass.

Blocking findings: none.

Residual risk:

- This QA pass intentionally used temp directories and dependency overrides only. It did not touch real `D:\Test Project`, `D:\PublicProject`, public-drive folders, or real LTR workbook files.
- Frontend UI wiring is not part of TASK_346C and remains downstream TASK_346D/TASK_346E scope.
- External release/packaging residuals and `temp_agents_stash.md` remain present in the working tree and must be excluded during Integrator packaging.

Recommended next role: Integrator packaging/readiness.
