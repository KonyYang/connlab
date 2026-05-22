# TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING`

## Why This Task Is Allowed Now

- `TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN` defined the Matrix persistence sequence.
- `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL` completed immutable Source Matrix import persistence.
- `TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL` completed structured editable Project Matrix Draft persistence.
- The next controlled step is to connect Matrix Editor's current editable state to Project Matrix Draft persistence without introducing confirm/authority semantics.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task crosses frontend state mapping, typed API client updates, and backend draft update persistence.
- It must preserve Matrix Editor behavior while adding save semantics and operator feedback.
- It must keep confirmed authority, revision flow, runtime execution, reports, fee, duration, and equipment out of scope.

## Objective

Connect Matrix Editor's current edit state to structured Project Matrix Draft persistence.

This task makes "Save" persist the editable Matrix working copy into the `ProjectMatrixDraft` model created by `TASK_255`, while keeping the Matrix unconfirmed.

## Scope

Allowed:

- Add/extend backend application service operations needed to update an existing Project Matrix Draft working copy.
- Add a minimal API route for saving/loading Project Matrix Draft aggregate state if existing routes are insufficient.
- Add typed frontend API client methods for Project Matrix Draft save/load.
- Wire Matrix Editor `Save` action to persist current group/row/cell/sample state into Project Matrix Draft.
- Display save state feedback:
  - saving
  - saved
  - unsaved changes
  - save failed
- Preserve current import preview, replace/append, local edit, sample notes, and step preview behavior.
- Add focused tests for backend update persistence, API boundary, frontend wiring, and no confirmed authority side effects.

Forbidden:

- Confirmed Matrix authority implementation.
- Active confirmed Matrix uniqueness rules.
- Matrix revision flow.
- Project Matrix Draft creation from new imports beyond existing `TASK_255` API behavior.
- Runtime execution, StepInstance persistence, report generation, fee/duration/equipment outputs.
- Report/readiness projection changes.
- Direct frontend access to SQLite, filesystem, Office, or repositories.
- Route-level business logic that bypasses application services.
- Reinterpreting selected groups as confirmed authority.

## Acceptance Criteria

- Matrix Editor can load or reference an existing Project Matrix Draft identity before saving.
- Clicking `Save` persists current editable rows, groups, selected groups, sparse non-empty cells, and group-level sample quantity to Project Matrix Draft persistence.
- Empty cell values are saved as absence of draft cell rows, not as persisted empty strings.
- Save does not create Confirmed Matrix authority, active Matrix version, runtime projection, or execution records.
- Save does not mutate Source Matrix import/snapshot rows.
- API routes call application services only.
- Frontend API calls stay in `frontend/src/api/client.ts`.
- Matrix Editor shows clear save feedback and does not expose future confirmation/report/runtime actions as active.
- Existing import preview and local edit behaviors remain functional.
- Tests cover successful save, sparse empty-cell behavior, source immutability, route boundary, frontend wiring, and existing Matrix Editor smoke/static checks.

## Validation

```powershell
py -m pytest tests\unit\test_project_matrix_draft_update_service.py tests\unit\test_project_matrix_draft_repository.py -q
```

```powershell
py -m pytest tests\integration\test_project_matrix_draft_save_api.py tests\integration\test_project_matrix_draft_from_source_matrix_api.py -q
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task256"
```

```powershell
cd frontend
npm run build
```
