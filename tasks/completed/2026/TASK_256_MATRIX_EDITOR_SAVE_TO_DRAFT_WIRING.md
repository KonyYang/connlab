# TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING

## Status

Complete.

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
- Persist only the approved Matrix working-copy field whitelist:
  - rows
  - groups
  - cells
  - selected groups
  - group-level sample quantity
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
- Persisting UI-only state such as right-side preview expansion, transient validation highlight, hover state, focus state, dialog visibility, scroll position, temporary error decoration, or other non-domain presentation state.
- Implicitly creating a Project Matrix Draft when no `project_matrix_draft_id` is available.
- Implementing optimistic concurrency/version checks unless explicitly approved in a later task.

## Acceptance Criteria

- Matrix Editor can load or reference an existing Project Matrix Draft identity before saving.
- If no `project_matrix_draft_id` exists, `Save` is disabled and shows an operator-readable reason. This task must not create a draft implicitly from Save.
- Clicking `Save` persists current editable rows, groups, selected groups, sparse non-empty cells, and group-level sample quantity to Project Matrix Draft persistence.
- Save persists only the approved field whitelist and excludes UI-only state.
- Empty cell values are saved as absence of draft cell rows, not as persisted empty strings.
- This task uses last-write-wins save semantics. `updated_at` may be returned/displayed, but optimistic concurrency/version conflict protection is explicitly out of scope.
- Save does not create Confirmed Matrix authority, active Matrix version, runtime projection, or execution records.
- Save does not mutate Source Matrix import/snapshot rows.
- API routes call application services only.
- Error mapping is stable:
  - `404` for draft not found
  - `409` for conflict if the application service detects one
  - `422` for request payload validation
  - `500` for unexpected failures
- Frontend API calls stay in `frontend/src/api/client.ts`.
- Matrix Editor shows clear save feedback and does not expose future confirmation/report/runtime actions as active.
- Existing import preview and local edit behaviors remain functional.
- Tests cover successful save, sparse empty-cell behavior, source immutability, route boundary, frontend wiring, missing draft target disabled state, repository update rollback on failure, and existing Matrix Editor smoke/static checks.
- Completion must update `docs/task_board.md` with status, validation commands/results, next stop point, and any residual risk.

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

## Completion Notes

- Added draft update/list application + API path for Project Matrix Draft working-copy persistence:
  - `GET /api/projects/{project_id}/matrix-drafts`
  - `PUT /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}`
- Save update uses atomic aggregate replacement (record/groups/rows/cells) and keeps Source Matrix snapshot immutable.
- Save request enforces sparse cell semantics: empty/whitespace values are removed from persisted cell rows.
- Save now persists editable row fields (`test_item`, `source_section`, `method`, `condition`, `requirement`) instead of dropping method/condition/requirement.
- Local-added rows/groups no longer use pseudo lineage ids; lineage columns are nullable and saved as `null` for local additions.
- Save semantics are last-write-wins for TASK_256 scope (no optimistic timestamp conflict gate).
- Matrix Editor `Save` is now wired to Project Matrix Draft persistence through typed API client methods in `frontend/src/api/client.ts`.
- Matrix Editor now loads latest project matrix draft summary/detail on entry when available, tracks save state (`saving`, `saved`, `unsaved`, `failed`), and disables save when no persisted draft target exists.
- Existing import preview / local edit / step preview behaviors remain available.

Validation executed:

- `py -m pytest tests\unit\test_project_matrix_draft_persistence_service.py tests\unit\test_project_matrix_draft_repository.py -q` (`13 passed`)
- `py -m pytest tests\integration\test_project_matrix_draft_save_api.py tests\integration\test_project_matrix_draft_from_source_matrix_api.py -q` (`2 passed`)
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task256"` (`33 passed`, `70 deselected`)
- `py -m pytest tests\integration\test_api_default_dependencies.py -q` (`1 passed`)
- `cd frontend && npm run build` (passed)
