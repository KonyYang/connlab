# TASK_259_MATRIX_EDITOR_REVISION_ACTIONS_WIRING

## Status

Planned. Awaiting user approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_259_MATRIX_EDITOR_REVISION_ACTIONS_WIRING` is planned only.

## Why This Task Is Allowed Now

- `TASK_258_MATRIX_REVISION_FLOW` completed the backend revision APIs.
- `docs/task_board.md` recommends a controlled frontend wiring task for Matrix revision actions.
- Matrix Editor already loads and saves persisted Project Matrix Drafts, so the next bounded step is exposing revision create/confirm actions through the existing frontend API boundary and Matrix Editor workflow.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded React + TypeScript wiring slice with typed API additions, existing Matrix Editor state integration, disabled-state selectors, and focused static/build checks.
- It requires careful UX state handling but no new backend domain model, database migration, Office parsing, runtime execution, report generation, LAN, permissions, or AI behavior.

## Objective

Wire Matrix revision actions into Matrix Editor:

- create a revision draft from the active confirmed Matrix
- load that revision draft into the editor
- save edits through the existing draft save path
- confirm the revision draft through the TASK_258 confirm-revision API

The UI must make the authority state explicit enough that operators understand whether they are editing a persisted draft, a revision draft, or blocked because no revision target exists.

## Scope

Allowed:

- Add typed frontend API client functions and DTO updates for:
  - `POST /api/projects/{project_id}/matrix-revisions`
  - `POST /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/confirm-revision`
  - nullable `source_import_id`
  - `base_confirmed_matrix_id`
  - confirmed Matrix response metadata needed for status feedback
- Wire Matrix Editor actions for:
  - creating a revision draft
  - loading the created revision draft into the current editor state
  - confirming the current revision draft
- Reuse existing Save behavior for draft edits.
- Add clear disabled reasons:
  - no project id
  - no persisted draft target
  - unsaved changes before confirm revision
  - current draft is not a revision draft
  - validation errors
  - request in progress
- Add restrained operational UI copy and status feedback consistent with ConnLab product UI.
- Add/update focused frontend static tests and run frontend build.
- Update `docs/task_board.md` after completion.

Forbidden:

- Backend API, application, repository, domain, storage, or migration changes.
- Runtime projection refresh or Runtime Console consumption.
- StepInstance, execution records, evidence/image management, report, fee, duration, equipment, Confirmed Step Output, AI review, LAN, permissions, or deployment work.
- Matrix parser, import preview, Word/Office gateway, or file handling changes.
- Creating revisions from non-active historical confirmed versions.
- Editing confirmed Matrix authority directly in the frontend.
- Reworking Matrix Editor layout beyond the minimal action/status controls required by this task.
- Splitting `api/client.ts` or performing broad Matrix Editor refactors unless strictly required to keep the task reviewable.

## UX Boundary

Use restrained product UI:

- No modal-first flow for normal actions. Prefer inline action controls and status messages.
- Keep copy operational and business-readable.
- Pair disabled buttons with visible reasons when the operator needs to act.
- Avoid decorative panels, nested cards, gradient text, glassmorphism, or thick side accents.
- Do not expose future workflow promises such as report generation, execution tracking, or AI review.

## Acceptance Criteria

- `frontend/src/api/client.ts` includes typed DTOs and functions for creating and confirming Matrix revisions.
- Matrix Editor can create a revision draft when backend state allows it.
- After successful revision draft creation:
  - the returned draft is loaded into the grid
  - `projectMatrixDraftId` points to the revision draft
  - `base_confirmed_matrix_id` is retained in frontend state
  - save baseline is refreshed so the freshly loaded revision draft is not marked dirty
- Confirm Revision is enabled only for a persisted revision draft with no unsaved changes and no Matrix validation errors.
- Confirm Revision calls the TASK_258 confirm-revision API and shows clear success/error feedback.
- If the current draft is source-import based and not a revision draft, Confirm Revision is disabled with a clear reason.
- Existing Save behavior remains unchanged.
- Existing import preview and append/replace behavior remains unchanged.
- No raw `fetch()` is added outside `frontend/src/api/client.ts`.
- Static tests cover API client symbols, Matrix Editor action wiring, disabled reasons, and preservation of existing Save wiring.
- `cd frontend; npm run build` passes.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task259 or task256"
```

```powershell
cd frontend; npm run build
```

## Residual Risk Record

- This task does not add backend read APIs for active confirmed authority status. The frontend relies on existing draft list/load behavior and TASK_258 create/confirm responses.
- Runtime Console and downstream outputs will not reflect confirmed revision changes until a later runtime/projection consumer task.
- Operator-facing revision history is not implemented in this task.
