# TASK_261 Matrix Import Group Selection Commit Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT`
- Why this task is allowed now:
  - `docs/task_board.md` shows `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` complete.
  - Current active task is `none`.
  - `docs/matrix_authority_to_test_record_smoke_flow_plan.md` recommends `TASK_261` as the next controlled task.

This document is a plan only. No implementation should start until user approval.

## 1) Goal

Create a backend import-commit boundary that takes a parsed Matrix preview plus selected group keys, persists the full immutable Source Matrix, and creates a project-specific selected-only `ProjectMatrixDraft`.

The goal is workflow correctness:

```text
Import Matrix -> Group Selection -> SourceMatrix + selected ProjectMatrixDraft
```

## 2) File-Level Change Plan

1. Application service
   - Add `backend/application/matrix_import_commit_service.py`.
   - Define command/input:
     - `project_id`
     - preview payload body
     - `selected_group_keys`
     - optional source metadata already available from preview context
   - Inject:
     - project store
     - Source Matrix import persistence service or store
     - Project Matrix Draft persistence service or store
   - Orchestrate source persistence first, then draft creation in one application boundary.

2. API route
   - Add `backend/api/routes_matrix_import_commit.py` unless existing project-test-plan route is clearly a better bounded home.
   - Suggested route:
     - `POST /api/projects/{project_id}/matrix-import/commit`
   - Request body should be typed and explicit.
   - Route must call application service only.
   - Error mapping:
     - project not found -> 404
     - empty/unknown/invalid selected groups -> 422
     - duplicate existing draft for same source/project -> 409 if current repository constraints require conflict behavior
     - unexpected -> 500

3. DTO/client boundary
   - Backend DTOs are required.
   - Frontend `client.ts` typed function is optional in this task. Include it only if needed to lock the API contract for `TASK_262`.
   - No visible frontend UI is allowed in this task.

4. Tests
   - Add `tests/unit/test_matrix_import_commit_service.py`.
   - Add `tests/integration/test_matrix_import_group_selection_commit_api.py`.
   - Reuse small in-memory preview payload fixtures.
   - Include at least:
     - selected subset creates selected-only draft
     - full source still stores unselected groups
     - sample quantity survives
     - empty selected groups -> 422
     - unknown selected group -> 422
     - route does not bypass service

5. Documentation
   - Mark `tasks/TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT.md` complete after implementation.
   - Update `docs/task_board.md` with deliverables, validation, and next recommended task.

## 3) Transaction Boundary

Preferred behavior: full source import persistence and ProjectMatrixDraft creation should be atomic from the API caller perspective.

Implementation plan must decide the concrete transaction mechanism based on current service/repository boundaries:

- If existing services share the same SQLAlchemy session in dependency wiring, commit both in one request transaction.
- If existing services own separate commit boundaries, refactor only as much as needed to prevent partial source-without-draft or draft-without-source outcomes.

Acceptance requires a rollback test if implementation touches repository transaction behavior.

## 4) Selected Group Semantics

- `selected_group_keys` is required and non-empty.
- Keys are normalized by trimming whitespace.
- The implementation plan should choose one duplicate policy:
  - reject duplicates with 422, recommended for clearer operator feedback; or
  - dedupe preserving first occurrence.
- Selected group ordering in the draft follows source group order, not request order.
- Unselected groups must not appear in `ProjectMatrixDraft.groups` or draft cells.

## 5) Source vs Draft Authority

Source Matrix:

- immutable import lineage
- full imported matrix
- all groups
- all rows
- sparse source cells

ProjectMatrixDraft:

- editable project execution projection
- selected groups only
- group-level sample quantity expression
- sparse non-empty draft cells for selected groups only

ConfirmedMatrix remains out of scope for this task.

## 6) Out Of Scope

- Group Selection View UI.
- Matrix Editor layout changes.
- Confirmed Matrix creation.
- Runtime projection consumer changes.
- Test Record preview.
- StepInstance.
- Execution records.
- Evidence/image handling.
- Report, fee, duration, equipment, AI review, LAN, permissions, deployment.

## 7) Validation Plan

```powershell
py -m pytest tests\unit\test_matrix_import_commit_service.py -q
```

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\integration\test_project_test_plan_preview_api.py -q
```

```powershell
py -m pytest tests\unit\test_source_matrix_persistence_service.py tests\unit\test_project_matrix_draft_persistence_service.py -q
```

## 8) Review Checklist

- Full Source Matrix is persisted.
- ProjectMatrixDraft is selected-only.
- Sample quantity expression survives.
- Unselected source groups remain traceable only through SourceMatrix.
- API route calls application service only.
- Existing preview APIs are unchanged.
- No frontend UI is introduced.
- No ConfirmedMatrix/TestRecord/runtime execution scope is introduced.
