# TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT

## Status

Planned. Awaiting user approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is planned only.

## Why This Task Is Allowed Now

- `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` is complete and task board current active task is `none`.
- `docs/matrix_authority_to_test_record_smoke_flow_plan.md` recommends `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` as the next controlled task.
- The next smoke-flow need is a backend commit boundary that preserves full Source Matrix lineage while creating a project-specific selected-group `ProjectMatrixDraft`.

## Objective

Create the backend Matrix import group-selection commit boundary:

```text
Matrix preview payload + selected_group_keys
-> immutable full Source Matrix lineage
-> selected-only ProjectMatrixDraft
```

This task stabilizes the authority workflow before adding Group Selection UI or Test Record preview.

## Scope

Allowed:

- Add an application service, preferably `backend/application/matrix_import_commit_service.py`, that orchestrates:
  - preview payload validation
  - selected group key validation
  - full Source Matrix persistence
  - selected-only Project Matrix Draft creation
- Add a thin API route, preferably a new `backend/api/routes_matrix_import_commit.py`, for committing a parsed/imported Matrix preview with selected groups.
- Reuse existing Source Matrix import persistence and Project Matrix Draft persistence services where practical.
- Ensure the full Source Matrix stores all source groups/rows/cells.
- Ensure the created ProjectMatrixDraft contains only selected project execution groups.
- Preserve selected group sample quantity expressions.
- Return typed source metadata and created draft aggregate.
- Add focused unit and integration tests.
- Update `docs/task_board.md` after completion.

Forbidden:

- Frontend Group Selection View implementation. That belongs to `TASK_262`.
- Matrix Editor UI changes, except typed API client definitions if the final plan explicitly includes client contract exposure.
- Test Record preview generation. That belongs to `TASK_263`.
- Runtime execution, StepInstance, execution result persistence, evidence/image records, report, fee, duration, equipment, AI review, LAN, permissions, or deployment work.
- Changing existing preview-only APIs.
- Treating SourceMatrix or ProjectMatrixDraft as confirmed authority.
- Creating confirmed Matrix authority directly from import commit.
- Reintroducing hidden/unselected groups into the editable draft.

## Contract Boundary

Input must include:

- `project_id`
- Matrix preview payload or tokenized preview body supported by the existing backend preview pipeline
- `selected_group_keys`

Validation must enforce:

- project exists
- selected group keys are non-empty
- selected group keys are unique after normalization
- every selected group key exists in the preview groups
- preview payload includes enough rows/groups/cells to persist Source Matrix

Response should include:

- source import id / source snapshot id
- created `ProjectMatrixDraft` aggregate
- selected group keys committed

## Data Rules

- Source Matrix stores full imported source lineage, including unselected groups.
- ProjectMatrixDraft stores selected groups only for the project execution editing surface.
- Group order in ProjectMatrixDraft follows source group order filtered by selected keys.
- Rows remain available for editing in the selected-only draft.
- Draft cells are sparse non-empty cells for selected groups only.
- Sample quantity expression is group-level authority in the draft.

## Acceptance Criteria

- Full Source Matrix is persisted even when only a subset of groups is selected.
- ProjectMatrixDraft contains selected groups only.
- Unselected source groups remain available through Source Matrix lineage but do not appear in ProjectMatrixDraft.
- Sample quantity expressions for selected groups are preserved.
- Empty selected group list returns typed 422.
- Unknown selected group key returns typed 422.
- Duplicate selected group keys are normalized and either deduped deterministically or rejected; the implementation plan must choose one behavior.
- API route remains thin and calls application service only.
- Existing Matrix preview APIs remain unchanged.
- Existing Project Matrix Draft save/revision/confirm APIs remain unchanged.
- No database schema migration is introduced unless the implementation plan proves it is required.

## Validation

```powershell
py -m pytest tests\unit\test_matrix_import_commit_service.py -q
```

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\integration\test_project_test_plan_preview_api.py -q
```

```powershell
py -m pytest tests\unit\test_source_matrix_persistence_service.py tests\unit\test_project_matrix_draft_persistence_service.py -q
```

## Residual Risk Record

- This task does not add the operator-facing Group Selection View.
- Existing frontend import flow will not call this commit API until `TASK_262`.
- Existing legacy draft creation paths may still exist; this task should avoid expanding their authority role.
