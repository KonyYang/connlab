# TASK_330D_PROJECT_FOLDER_UPDATE_PERFORMANCE_AND_COLLECT_DTO_HOTFIX

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330C_PROJECT_FOLDER_OUTPUT_CONSUMES_BASIC_INFORMATION is complete, including review follow-up. Browser/API timing review of the post-330C `Update project folder` button found two independent defects in the existing button chain:

1. `request-material/collect` can return 500 because the API response converter treats `RequestMaterialCollectResult` as a preview DTO and reads a missing `local_workspace_path`.
2. Required forms generation can spend about 30 seconds in Fee Form generation because the button flow reruns Excel COM even when a safe current Fee Form artifact may already exist.

This task is a narrow hotfix candidate after TASK_330C. It is not a Basic Information output-consumption task and must not reopen TASK_330C scope.

## Goal

Make the Project Folder update button flow reliable and faster by:

- fixing the `request-material/collect` response DTO conversion bug;
- reusing a safe current Fee Form artifact when available instead of rerunning Excel COM;
- preserving existing managed-output fingerprint safety.

## In Scope

- `request-material/collect` result/response DTO correction.
- Unit/API regression coverage for the collect response.
- A narrow Required forms Fee Form reuse path.
- Tests proving the Fee Form generator is skipped only when a safe current generated artifact exists.
- Tests proving the Fee Form generator still runs when reuse is unsafe or unavailable.
- Required forms timing labels may be extended for reuse diagnostics.

## Out Of Scope

- No Basic Information blockers, signatures, field mapping, or Word write-back changes.
- No TASK_330C output-consumption semantic changes.
- No Office field mapping changes.
- No Excel COM batch-write optimization.
- No LTR workbook writeback.
- No report generation.
- No Matrix/Fee Basic Information source-provider additions.
- No frontend redesign or user-facing copy changes unless a typed DTO adjustment requires a small client update.
- No StepInstance, AI, permissions, LAN/server, or multi-user behavior.

## Acceptance Criteria

- `POST /api/projects/{project_id}/request-material/collect` returns a typed collect response without Internal Server Error for a valid collect result.
- The collect response preserves workspace path context rather than returning placeholder nulls when the service has post-copy preview context.
- Required forms generation can copy a safe current Fee Form artifact into the official project folder without invoking Excel COM.
- Reuse is allowed only when source context, generated source, file existence, extension, and sha256/fingerprint checks pass.
- Existing final-target managed-output conflict protection remains unchanged.
- Unsafe/missing/stale/manual Fee Form artifacts fall back to the current Excel COM export path.
- No Basic Information output-consumption behavior is added or changed by TASK_330D.

## Validation

Completed targeted validation:

```powershell
py -m pytest tests/unit/test_project_request_material_collection_service.py -q
# 8 passed

py -m pytest tests/integration/test_project_request_material_collection_api.py -q
# 3 passed

py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
# 30 passed

py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
# 4 passed

py -m pytest tests/integration/test_api_default_dependencies.py -q
# 3 passed

py -m pytest tests/unit/test_project_request_material_collection_service.py tests/integration/test_project_request_material_collection_api.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
# 45 passed
```

If frontend DTO types change:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout --watch=false
npm run build
```

Manual smoke:

- Open a project with current Matrix/Fee and confirmed Basic Information.
- Click `Update project folder`.
- Verify no `request-material/collect` Internal Server Error appears.
- Verify a safe current Fee Form output is reused when available.
- Verify cold/missing Fee Form artifacts still generate through the existing Excel path.

## Stop Point

Stop after TASK_330D is implemented and validated. Do not proceed to LTR workbook writeback, report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope without a separate approved task.
