# TASK_096_PROJECT_CREATION_DRAFT_LIFECYCLE

## Status

done

## Current Phase

Phase 10A follow-up. This is the first proposed task in the Project creation draft flow series.

## Active Task Rule

Do not implement this task until `docs/task_board.md` explicitly marks `TASK_096_PROJECT_CREATION_DRAFT_LIFECYCLE` as the current active task or a ready task approved by the user.

When active, this task is allowed because it stays inside MVP project creation:

- Project stage: New Project before confirmed Project/folder completion.
- Input: imported `.msg`, direct `.docx`, selected application form, Precheck draft data.
- Output: explicit save-or-discard lifecycle for creation-in-progress data.
- Domain impact: intake package/case/draft lifecycle only; no future-scope object.
- MVP scope: intake, precheck, LTR, and folder preparation.

## User Decision Baseline

The user approved this policy:

- If the operator exits without saving a draft, ConnLab should leave no trace in its own database and stored files.
- Outlook remains the source for abandoned email material. ConnLab must not touch Outlook originals.
- ConnLab should keep imported `.msg` and attachments only when the operator saves a creation draft or successfully creates the project.

## Goal

Introduce an explicit creation draft lifecycle so temporary imported files and database rows do not become hidden, confusing leftovers.

Required operator choices:

- `Save draft and exit`: persist the in-progress creation package and show it later in Drafts / In Progress.
- `Exit without saving`: delete ConnLab-created temporary database rows and stored files for the current unsaved creation session.
- Successful project creation/folder creation: preserve source `.msg` and attachments as project evidence/source files according to the existing folder rules.

## Scope

Backend:

- Define which records and copied files belong to an unsaved creation session.
- Add an application service boundary for discarding an unsaved creation session.
- Ensure deletion affects only ConnLab-owned imported copies and database rows.
- Do not delete Outlook originals or any external source path.
- Ensure saved drafts are not removed by the unsaved-session cleanup path.

Frontend/API:

- Expose typed API operation(s) for `Save draft and exit` and `Exit without saving`.
- Route pages must call application services through API, not directly manipulate files.
- Show clear confirmation copy before destructive discard.

## Out Of Scope

- Do not build the Drafts / In Progress UI list in this task; that is `TASK_097`.
- Do not redesign Project Workbench.
- Do not implement LTR revise/exception behavior.
- Do not add Matrix, Report, AI review, permissions, LAN, Outlook inbox auto-scan, or email sending.

## Acceptance Criteria

- Importing a `.msg` or `.docx` creates temporary ConnLab-owned intake records/files.
- Choosing `Exit without saving` deletes those ConnLab-owned rows/files.
- Choosing `Save draft and exit` preserves the records/files for later continuation.
- Discard never touches Outlook originals or arbitrary user source files.
- Saved drafts and confirmed projects are not removed by unsaved cleanup.
- User-facing copy distinguishes saving from destructive discard.

## Validation

Add or update tests:

- Unit test: discard removes unsaved intake package/case/draft records.
- Unit or integration test: discard removes ConnLab-owned stored files.
- Unit test: saved draft is not discarded by the unsaved cleanup path.
- Integration/API smoke test: discard returns a typed response and actionable errors.
- Frontend static test: destructive action copy is present and no raw backend terms leak into UI.

Recommended validation:

```powershell
py -m pytest tests\unit tests\integration -q
npm run build
```

## Stop Rule

After completing this task, update `docs/task_board.md`, record validation, and stop. Do not start `TASK_097` automatically.

## Completion Notes

Completed on 2026-05-05.

- Added `IntakePackageStatus.DRAFT_SAVED` to distinguish explicitly saved creation drafts from temporary unsaved intake imports.
- Added `ProjectCreationDraftLifecycleService` with `save_draft()` and `discard_unsaved()` application boundaries.
- Added safe ConnLab-owned intake package directory deletion through `IntakeStorage.delete_package()`.
- Added repository deletion methods for package-owned drafts, cases, assets, and package rows.
- Added typed API endpoints:
  - `POST /api/intake-packages/{package_id}/draft/save`
  - `POST /api/intake-packages/{package_id}/draft/discard`
- Added frontend API client functions and Intake/Precheck footer actions for `Save draft and exit` and `Exit without saving`.
- `Exit without saving` uses a second confirmation click and operator copy that says only ConnLab imported copies are removed.
- Precheck `Save draft and exit` saves current field/sample/requested-testing corrections before marking the package as a saved draft.
- `Back to Intake` remains in place for this task; removal is still deferred to `TASK_098_PRECHECK_CONFIRMED_APPLICATION_EDITING`.

Validation:

```powershell
py -m pytest tests\unit\test_project_creation_draft_lifecycle_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q
```

Result: `54 passed`.

```powershell
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit tests\integration -q
```

Result: `319 passed`, `7 failed`.

Observed failures outside this task's change scope:

- `tests/unit/test_direct_word_intake_service.py::test_direct_word_import_allows_doc_but_keeps_low_score_as_supporting` expects direct `.doc` intake, while current service accepts only `.docx`.
- Several phase-board tests still assert the exact historical phrase `Current Active Task: None - pending user approval for next phase`.
- `tests/integration/test_intake_package_repositories.py::test_form_selection_service_creates_case_and_draft_with_repositories` seeds a fake `.docx` path and fails the current Word header gate.

Known limitations:

- Draft listing and continuation from a dedicated Drafts / In Progress surface is not implemented here; that remains `TASK_097`.
- Saved-draft discard from the future Drafts / In Progress surface is intentionally not implemented here.
