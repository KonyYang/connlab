# TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND

## Status

Complete on 2026-05-23. Backend-only read-only Test Record preview from active ConfirmedMatrix authority is implemented and validated.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

none. `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` is complete; awaiting next approved task.

## Why This Task Is Allowed Now

- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
- `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` is complete.
- `TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING` is complete.
- `docs/task_board.md` records `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` as complete.
- Current execution is now blocked until the next task is explicitly approved.
- `docs/matrix_authority_to_test_record_smoke_flow_plan.md` identifies this task as the next controlled backend slice after Matrix import and group selection stabilization.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded backend read-model / projection-consumer slice.
- It must preserve strict authority boundaries: Test Record preview consumes active ConfirmedMatrix only.
- It requires careful mapping and tests, but does not require broad architecture redesign, new persistence aggregates, UI work, Office automation, or generated document formatting.
- Higher reasoning may be useful if existing ConfirmedMatrix repositories or token projection utilities are fragmented, but the expected implementation should remain deterministic and narrow.

## Objective

Create a read-only backend Test Record preview API that derives smoke-flow preview data from the active ConfirmedMatrix authority for a project.

Primary flow:

```text
Project
-> active ConfirmedMatrix
-> selected confirmed groups
-> group-level Test Record preview sections
-> ordered step rows
```

This task proves that confirmed Matrix authority can drive a downstream Test Record preview without introducing execution persistence or document generation.

## Scope

Allowed:

- Add an application service that loads the active ConfirmedMatrix for a project.
- Add typed response DTOs for a minimal read-only Test Record preview.
- Add a thin FastAPI route that calls the application service.
- Build preview groups from confirmed selected groups only.
- Preserve confirmed group order.
- Preserve row order and parsed step-token order inside each group.
- Carry sample quantity expression from the confirmed group as preview sample quantity authority.
- Carry smoke-visible step row fields:
  - sequence / raw token
  - test item
  - section
  - method
  - condition
  - requirement
- Return empty strings for missing method, condition, or requirement fields.
- Return typed 404 when no active ConfirmedMatrix exists for the project.
- Return `200` with `preview_status="empty"` and `groups=[]` when an active ConfirmedMatrix exists but has no confirmed groups or no previewable step rows.
- Add focused unit tests for the application service.
- Add focused integration tests for the API route.
- Update `docs/task_board.md` only after implementation completion.

Forbidden:

- No frontend UI.
- No `.docx`, PDF, Excel, report, or formal Test Record file generation.
- No persisted `TestRecord` aggregate.
- No `StepInstance`, execution result persistence, evidence/image persistence, runtime execution system, reviewer workflow, or structured LLCR form.
- No fee, duration, equipment, AI recommendation, approval package, report, LAN, permissions, or deployment work.
- No consumption of SourceMatrix, ProjectMatrixDraft, frontend temporary state, or request-body Matrix rows as preview authority.
- No mutation of ConfirmedMatrix, ProjectMatrixDraft, SourceMatrix, or project lifecycle state.
- No broad refactor of existing Matrix confirmation, draft persistence, import parsing, or fee dataset preview services.

## Required Boundary

Only ConfirmedMatrix is authority for this task.

The API must not accept Matrix rows, selected groups, draft payloads, source import snapshots, or frontend-derived preview payloads in the request body.

The service must load current project authority from backend persistence, then derive the preview from that authority.

## Expected API Shape

Exact naming may be adjusted during executable planning to match existing route conventions, but the route must remain project-scoped and read-only.

Candidate endpoint:

```text
GET /api/projects/{project_id}/confirmed-matrix/test-record-preview
```

Candidate response shape:

```json
{
  "project_id": "PROJECT-001",
  "confirmed_matrix_id": 10,
  "preview_status": "ready",
  "groups": [
    {
      "group_key": "G1",
      "group_label": "Group 1",
      "sample_quantity_expression": "5",
      "step_count": 2,
      "steps": [
        {
          "sequence": 1,
          "raw_token": "1",
          "test_item": "Visual inspection",
          "section": "6.1",
          "method": "",
          "condition": "",
          "requirement": ""
        }
      ]
    }
  ]
}
```

DTO naming rules:

- `project_id` is a string in the response, matching existing project-scoped API style.
- Step DTO field name is `section`, not `source_section`.
- Missing `method`, `condition`, and `requirement` values are serialized as `""`.
- `preview_status` allowed values for this task are:
  - `"ready"` when at least one preview group with at least one preview step is returned
  - `"empty"` when an active ConfirmedMatrix exists but no previewable groups/steps are available

## Candidate Impact Files

- new `backend/application/confirmed_matrix_test_record_preview_service.py`
- new `backend/api/routes_confirmed_matrix_test_record_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- existing ConfirmedMatrix domain/repository/application files as needed for read-only access
- optional shared mapper/helper only if existing token parsing or Matrix projection utilities are already available and can be reused narrowly
- `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
- `tests/integration/test_confirmed_matrix_test_record_preview_api.py`

## Acceptance Criteria

- A project with an active ConfirmedMatrix can request Test Record preview without sending Matrix rows in the request body.
- Preview contains only confirmed groups.
- Unselected SourceMatrix groups never appear.
- Sample quantity expression is preserved per selected confirmed group.
- Step rows are deterministic: group order, then row order, then parsed token order.
- Each step row carries raw token, test item, section, method, condition, and requirement fields.
- Blank method, condition, or requirement values are represented predictably for smoke visibility.
- No fee dataset is returned.
- No equipment table is returned.
- No report or Test Record file is generated.
- No StepInstance or execution persistence is introduced.
- No active ConfirmedMatrix returns a typed 404.
- Active ConfirmedMatrix with no confirmed groups or no previewable step rows returns `200` with `preview_status="empty"` and `groups=[]`.
- Response `project_id` is serialized as a string.
- Step row field name is `section`; `source_section` must not be introduced.
- Missing `method`, `condition`, or `requirement` values are serialized as empty strings, not placeholder text.
- Route module remains thin and does not contain business mapping logic.
- Unit and integration tests cover happy path, no-confirmed-matrix 404, active-but-empty `200` response, selected-group-only output, sample quantity propagation, string `project_id`, fixed `section` field naming, empty-string missing fields, and deterministic step ordering.

## Validation

Minimum expected validation after implementation:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_preview_service.py -q
```

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

Recommended regression validation:

```powershell
py -m pytest tests\unit\test_matrix_import_commit_service.py tests\unit\test_project_matrix_draft_persistence_service.py -q
```

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\integration\test_project_test_plan_preview_api.py -q
```

## Required Executable Plan Before Implementation

Before implementation, create a reviewable plan document, for example:

```text
docs/task_263_confirmed_matrix_test_record_preview_backend_plan.md
```

The plan must include:

- actual existing ConfirmedMatrix persistence/read path found in code
- exact DTO names and route path
- exact repository/service dependencies
- token expansion strategy and reused helpers
- test fixture strategy
- risks and fallback choices
- validation commands

No implementation code may be written before that plan is reviewed and explicitly approved.

## Residual Risk Record

- Existing `test_record_fee_dataset_preview_service.py` may contain useful mapping ideas, but it is tied to legacy draft/fee behavior. This task must not expand fee scope or reuse it in a way that makes Test Record preview depend on fee data.
- If ConfirmedMatrix persistence lacks a clean active-read method, the executable plan must decide whether to add a narrow repository query or reuse an existing application service. Do not work around this by accepting draft/source payloads from the request.
- This task intentionally returns preview data only. Formal Test Record generation belongs to a later task after the smoke flow is validated.
