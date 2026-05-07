# TASK_097_DRAFTS_IN_PROGRESS_SURFACE

## Status

done

## Current Phase

Phase 10A follow-up. This is the second proposed task in the Project creation draft flow series.

## Active Task Rule

Do not implement this task until `docs/task_board.md` explicitly marks `TASK_097_DRAFTS_IN_PROGRESS_SURFACE` as current or ready after `TASK_096_PROJECT_CREATION_DRAFT_LIFECYCLE` is complete.

## User Decision Baseline

The user approved a separate `Drafts / In Progress` area so unfinished creation work is not mixed with confirmed Projects.

## Goal

Create a clear UI/API surface for continuing or discarding saved creation drafts.

Recommended product model:

```text
Projects
  - confirmed projects only
  - primary action: Open

Drafts / In Progress
  - saved creation drafts only
  - primary action: Continue
  - secondary action: Discard
```

## Scope

Backend/API:

- Expose a typed list of saved creation drafts.
- Include enough display data for operators to recognize a draft: source subject/file, requester, product name, last updated time, and current workflow step when available.
- Expose continue metadata: package ID, selected form asset ID, active case ID, and current step.
- Expose discard for saved drafts with confirmation-friendly error messages.

Frontend:

- Add a Drafts / In Progress section or page.
- Draft rows use `Continue` and `Discard`, not `Open`.
- `Continue` routes back into New Project at the correct step.
- Confirmed projects keep using `Open` into Project Workbench.

## Out Of Scope

- Do not merge Drafts into the normal Projects table as confirmed projects.
- Do not implement historical multi-case review.
- Do not change LTR workbook behavior.
- Do not implement future-scope modules.

## Acceptance Criteria

- Saved drafts appear under Drafts / In Progress, not as confirmed Projects.
- Confirmed Projects still open Project Workbench.
- Drafts continue into the New Project workflow, not Project Workbench.
- Discarding a draft removes ConnLab-owned draft records/files through backend service rules.
- Empty Drafts state is operational and concise.
- User-facing labels avoid raw terms such as `asset_id`, `case_id`, and API paths.

## Validation

Add or update tests:

- API test: list saved drafts.
- API test: continue metadata resolves the expected New Project step.
- API test: discard saved draft removes only draft-owned resources.
- Frontend static test: Drafts uses `Continue`, Projects uses `Open`.
- Frontend build passes.

Recommended validation:

```powershell
py -m pytest tests\integration -q
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

## Stop Rule

After completing this task, update `docs/task_board.md`, record validation, and stop. Do not start `TASK_098` automatically.

## Completion Notes

Completed on 2026-05-05.

- Added `ProjectCreationDraftQueryService` to list saved `draft_saved` creation packages for Drafts / In Progress.
- Draft list rows include operator recognition fields and continuation metadata: source file/subject, requester, product name, updated time, current step, selected form asset, and active case.
- Added API endpoints:
  - `GET /api/project-creation-drafts`
  - `POST /api/project-creation-drafts/{package_id}/discard`
- Added saved-draft discard behavior to `ProjectCreationDraftLifecycleService`, separate from the TASK_096 unsaved-session discard path.
- Projects page now displays a separate `Drafts / In Progress` panel below confirmed Projects.
- Confirmed project rows still use `Open`.
- Saved draft rows use `Continue` and `Discard`, with second-click confirmation for discard.
- Continuing a draft loads package detail, restores the intake session, and routes to Intake or Precheck based on the draft's current step.

Validation:

```powershell
py -m pytest tests\integration\test_manual_intake_api.py tests\unit\test_project_creation_draft_lifecycle_service.py tests\unit\test_frontend_shell_files.py -q
```

Result: `57 passed`.

```powershell
npm run build
```

Result: passed.

```powershell
py -m pytest tests\integration -q
```

Result: `53 passed`, `1 failed`.

Observed failure outside this task's change scope:

- `tests/integration/test_intake_package_repositories.py::test_form_selection_service_creates_case_and_draft_with_repositories` seeds a fake `.docx` path and fails the current Word header gate.

Known limitations:

- Drafts are shown in the existing Projects route as a separate section; no new sidebar route was added.
- Historical multi-case draft management is still not implemented.
- Removing Precheck `Back to Intake` remains deferred to `TASK_098_PRECHECK_CONFIRMED_APPLICATION_EDITING`.
