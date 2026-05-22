# TASK_256 Matrix Editor Save To Draft Wiring Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING`
- Why this task is allowed now:
  - `TASK_253` defined the persistence sequence.
  - `TASK_254` persisted immutable Source Matrix imports.
  - `TASK_255` persisted editable Project Matrix Draft working copies.
  - The next controlled step is save wiring from Matrix Editor to Project Matrix Draft, without confirmation semantics.

This document is a plan only. No implementation should start until user approval.

## 1) Task Goal

Make Matrix Editor's `Save` action persist the operator's current editable Matrix working copy into the structured Project Matrix Draft persistence model.

The save operation stores draft-local working state only. It does not create confirmed authority, active Matrix version, runtime projection, report data, fee data, or StepInstance execution data.

## 2) Inputs And Outputs

Input:

- Existing Project Matrix Draft identity.
- Matrix Editor current group columns, rows, sparse group-cell values, selected group state, and sample quantity expressions.

Output:

- Updated persisted Project Matrix Draft aggregate:
  - draft root updated timestamp
  - draft groups
  - draft rows
  - sparse non-empty draft cells
  - draft-local selected groups
  - group-level sample quantity expression

Non-output:

- UI-only state must not be persisted. This includes right-side preview expansion, temporary validation highlight, hover/focus state, dialog visibility, scroll position, transient error decoration, and other presentation-only state.

## 3) Architecture Boundary

Frontend:

- Matrix Editor owns UI state and save feedback.
- API calls must go through `frontend/src/api/client.ts`.
- No direct filesystem, Office, SQLite, or repository access.

API:

- Routes accept typed DTOs and call application services only.
- Routes must not directly instantiate repository behavior for business logic.

Application:

- Owns save validation and draft update orchestration.
- Preserves Source Matrix lineage.
- Enforces sparse non-empty cell semantics.

Infrastructure:

- Repository persists root/groups/rows/cells atomically inside the request transaction.

## 4) File-Level Change Plan

1. Backend service/repository
   - Extend `backend/application/project_matrix_draft_persistence_service.py` with update/save operation.
   - Extend `backend/infrastructure/storage/repositories/project_matrix_draft.py` with replace-working-copy or update-aggregate operation.
   - Preserve lineage IDs for source groups/rows when saving.
   - Treat empty cell values as delete/no-row.

2. Backend API
   - Extend `backend/api/routes_project_matrix_drafts.py` with minimal save/update endpoint if existing create/get routes are insufficient.
   - Keep request/response DTOs typed and operational.
   - Map not-found/conflict/validation errors to actionable HTTP responses.

3. Frontend API client
   - Add typed Project Matrix Draft DTOs and save method in `frontend/src/api/client.ts`.
   - Do not introduce direct `fetch()` outside API client.

4. Matrix Editor wiring
   - Load or receive existing `project_matrix_draft_id` context.
   - If no `project_matrix_draft_id` exists, keep `Save` disabled and show an operator-readable reason.
   - Do not implicitly create a Project Matrix Draft from the Save action.
   - Map Matrix Editor state into save payload:
     - groups
     - row order and row fields
     - sparse group-cell values
     - selected group state
     - group sample quantity expression
   - Exclude UI-only state from save payload.
   - Enable `Save` only when a persisted draft target exists and there are changes.
   - Show saving/saved/unsaved/save failed feedback.
   - Leave `Publish for approval` disabled/out of scope.

5. Tests
   - Backend unit tests for aggregate save mapping and sparse cell deletion.
   - Repository tests for atomic replace/update behavior.
   - API integration tests for save endpoint and source immutability.
   - Frontend static tests for API client boundary and Matrix Editor save wiring.

## 5) Data Semantics

Draft update:

- Updates Project Matrix Draft working-copy state.
- Does not create or update Source Matrix rows/groups/cells.
- Does not create Confirmed Matrix authority.
- Does not supersede draft versions unless explicitly required by existing draft persistence behavior.
- Does not implicitly create a draft when Save has no existing `project_matrix_draft_id`.
- Uses last-write-wins semantics in this task. Optimistic concurrency/version checks based on `updated_at` or a version column are explicitly out of scope and should be recorded as residual risk if relevant.

Persisted field whitelist:

- rows
- groups
- cells
- selected groups
- group-level sample quantity

Sparse cells:

- Non-empty string values become draft cell rows.
- Empty or whitespace-only values remove the draft cell row for that row/group intersection.

Selected groups:

- Persisted as draft-local `is_selected`.
- Not authority and not runtime projection.

Sample quantity:

- Group-level `sample_quantity_expression` remains the single editable draft truth.
- Source sample rows remain trace-only.

## 6) UI/UX Constraints

ConnLab is a restrained product UI for lab operators at Windows workstations.

- Use operational labels: `Save`, `Saving...`, `Saved`, `Unsaved changes`, `Save failed`.
- Pair disabled state with a visible reason if the operator can act.
- When no draft target exists, show a concise disabled reason such as `No persisted draft to save`.
- Avoid introducing new future actions such as confirm authority, execution start, report generation, fee generation, or runtime publication.
- Preserve current Matrix Editor density and layout; this task is save wiring, not a redesign.

## 7) Risks And Controls

Risk: Save is mistaken for confirmed authority.

- Control: `Save` copy and API semantics remain draft-only; `Publish for approval` remains disabled/out of scope.

Risk: Save loses Source Matrix lineage.

- Control: payload mapping must preserve existing source group/row lineage where available; tests verify source immutability.

Risk: Empty draft cells become persisted empty strings.

- Control: repository/service normalize empty values to absent sparse cells.

Risk: Frontend grows ad hoc API logic.

- Control: all API calls stay in `frontend/src/api/client.ts`; Matrix Editor calls typed client functions.

Risk: Partial draft replacement persists on failure.

- Control: update root/groups/rows/cells atomically under one transaction and test rollback behavior if repository replacement fails.

Risk: concurrent edits overwrite each other.

- Control: accept last-write-wins for this task and document concurrency as out of scope. Do not add partial optimistic concurrency unless explicitly approved.

Risk: UI-only state pollutes persisted draft data.

- Control: save payload uses an explicit field whitelist and tests/static checks verify UI-only state is not sent.

Risk: Save creates an unintended draft when no target exists.

- Control: disable Save without `project_matrix_draft_id`; draft creation remains a separate flow from `TASK_255`.

Risk: frontend error handling drifts across HTTP statuses.

- Control: stabilize error mapping: `404` draft not found, `409` conflict when defined, `422` payload validation, `500` unexpected failure.

## 8) Validation Plan

Run:

```powershell
py -m pytest tests\unit\test_project_matrix_draft_update_service.py tests\unit\test_project_matrix_draft_repository.py -q
```

Run:

```powershell
py -m pytest tests\integration\test_project_matrix_draft_save_api.py tests\integration\test_project_matrix_draft_from_source_matrix_api.py -q
```

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task256"
```

Run:

```powershell
cd frontend
npm run build
```

Manual smoke after implementation:

1. Open Matrix Editor with an existing Project Matrix Draft.
2. Modify a step cell and group sample quantity.
3. Save, reload, and verify persisted values return.
4. Clear a cell, save, reload, and verify it remains empty through sparse-cell absence.
5. Verify Source Matrix import data is unchanged.
6. Verify no confirmed authority or runtime projection is created.

Documentation closeout:

- Update `docs/task_board.md` with completion status.
- Record validation commands and results.
- Set active task back to none.
- Record residual risks, including last-write-wins concurrency if still applicable.

## 9) Out Of Scope

- Confirmed Matrix authority
- Matrix revision flow
- Optimistic concurrency/version conflict protection
- Runtime execution projection
- StepInstance persistence
- Report generation
- Fee, duration, and equipment assessment
- Major Matrix Editor redesign
