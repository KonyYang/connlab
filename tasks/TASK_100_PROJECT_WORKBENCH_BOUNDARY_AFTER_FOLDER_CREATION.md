# TASK_100_PROJECT_WORKBENCH_BOUNDARY_AFTER_FOLDER_CREATION

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10B - LTR workbook write hardening`
- Current Active Task on board: `None - TASK_099 complete, pending user decision for next task`
- Why this task is allowed to plan now: `TASK_099` completed the post-LTR base-edit freeze. The next controlled boundary is where operators land after New Project writes the LTR workbook and creates the project folder. Planning this task is allowed by user approval, but implementation must wait for explicit approval of this plan.

## Step 1 Plan Only

This document is the executable implementation plan for review.
No implementation code may be written until the user approves this plan.

## Purpose

Make `Project Workbench` the post-creation project surface, not a duplicate creation wizard.

After New Project completes, the operator should use Workbench to inspect confirmed project identity, LTR state, folder state, source materials, and evidence placement. Normal creation continuation stays in `New Project` and `Drafts / In Progress`.

## Task Understanding

Goal:

- Confirmed Projects use `Open`.
- Saved creation drafts use `Continue`.
- Project Workbench should not be the normal place to upload/edit the application form, run precheck, register LTR, or generate the initial project folder after the New Project one-action flow exists.
- Workbench may show lifecycle summary/status, but it should be read-only/status-oriented for creation stages.
- Workbench may retain MVP post-folder source material/evidence placement management, because this belongs after project folder creation.

Inputs:

- Confirmed `Project` records from `GET /api/projects`.
- Saved creation drafts from `GET /api/project-creation-drafts`.
- Existing project LTR records from `GET /api/projects/{project_id}/ltr`.
- Existing folder/evidence APIs if the Workbench still needs to show or recover folder/source-material state.

Outputs:

- A clearer Workbench UI boundary.
- Typed API/state usage that distinguishes confirmed projects from creation drafts.
- Static and integration tests that guard `Open` versus `Continue` and prevent Workbench from regrowing creation controls.

Involved modules:

- Frontend route/page:
  - `frontend/src/pages/ProjectListPage.tsx`
  - `frontend/src/pages/ProjectWorkbenchPage.tsx`
  - `frontend/src/App.tsx`
- Frontend workflow components/state:
  - `frontend/src/components/workflow/workflowState.ts`
  - existing workflow action panels only if retained as read-only summaries or removed from Workbench composition
- API client:
  - `frontend/src/api/client.ts`
- Backend/API if discovery confirms a missing read model:
  - `backend/api/routes_project.py`
  - existing folder/LTR/project repositories
- Tests:
  - `tests/unit/test_frontend_shell_files.py`
  - focused integration tests only if backend response shape changes

Out of scope:

- No Matrix, Test Record, Report Generation, AI review, LAN, permissions, Outlook auto-scan, or email sending.
- No full file manager.
- No full revise/exception workflow.
- No broad Workbench redesign or app shell redesign.
- No external workbook write changes.

## Current Code Findings

Current `ProjectListPage` already separates:

- confirmed projects table: action text `Open`, routes through `onOpenProject`
- saved creation drafts table: action text `Continue`, routes through `onContinueDraft`

Current `ProjectWorkbenchPage` still composes creation-era controls:

- `ApplicationFormActionPanel` for uploading application form
- `PrecheckPanel` with `Run precheck`
- `LtrActionPanel` with local LTR preview/commit behavior
- `FolderActionPanel` with folder preview/generate behavior
- evidence placement controls

This is the main boundary mismatch after New Project became the one-action creation flow.

## Proposed Design

### 1. Keep Project Registry And Drafts Split

Preserve `ProjectListPage` structure:

- Projects table action remains `Open`.
- Drafts / In Progress action remains `Continue`.
- Draft rows continue to route back into New Project via `onContinueDraft`.
- Confirmed project rows route only to `/projects/{project_id}`.

Add or tighten tests so this separation is explicit.

### 2. Convert Workbench Creation Steps To Status Summary

Replace Workbench's creation-wizard behavior with post-creation status sections:

- Project identity summary:
  - project name/product/requestor/business unit/status
  - LTR number(s)
  - folder status/path if available
- Creation baseline summary:
  - application/precheck/LTR/folder status as read-only lifecycle facts
  - no upload form button
  - no run precheck button
  - no local LTR commit button
  - no initial folder generate form

UX copy should be operational:

- `Created project`
- `LTR registered`
- `Project folder`
- `Source materials`
- `Evidence placement`

Avoid copy that implies the operator should resume creation from Workbench.

### 3. Preserve Narrow Post-Folder Source Material Management

Keep only source-material/evidence placement controls if they are already MVP and safe:

- evidence placement preview
- evidence placement execution
- read-only display of planned/copied source material results

This is permitted because source material placement belongs after project folder creation and does not duplicate New Project creation steps.

If no folder has been created, Workbench should show a clear blocked state:

- `Project folder is not recorded for this project. Complete New Project folder creation or use a future recovery task.`

Do not implement a new recovery action unless current APIs already support it without expanding scope. Prefer read-only message and future task note.

### 4. Backend/API Strategy

Prefer no backend schema change for this task.

Use existing APIs first:

- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/ltr`
- existing evidence placement preview/place APIs

If folder state cannot be read from existing project status alone, add the smallest read-only endpoint or response field needed to distinguish:

- folder created / not recorded
- known folder path if already stored

Do not add write behavior in this task.

### 5. Frontend Architecture Strategy

Do not grow `ProjectWorkbenchPage` with more ad hoc JSX.

Preferred small extraction:

```text
frontend/src/features/project-workbench/
  ProjectWorkbenchStatus.tsx
  ProjectWorkbenchEvidencePanel.tsx
  projectWorkbenchSelectors.ts
```

If implementation can stay smaller, extract only selectors and one named status component. The route page should remain a loader/composer.

### 6. Test Strategy

Update static frontend tests to assert:

- Projects rows still contain `Open`.
- Draft rows still contain `Continue`.
- Workbench no longer imports or renders normal creation action panels:
  - no `ApplicationFormActionPanel`
  - no `LtrActionPanel`
  - no `FolderActionPanel` initial folder generation flow
  - no `uploadApplicationForm`
  - no `runPrecheck`
  - no `commitLtrLocally`
  - no `generateFolder`
- Workbench still allows or displays source/evidence placement only if retained:
  - `previewEvidencePlacement`
  - `placeEvidence`
- No Matrix/Report/AI terms are introduced.

Run build validation.

If backend read model changes:

- add focused integration test for confirmed project response versus saved draft response.

## Proposed File-Level Changes

Likely frontend changes:

1. `frontend/src/pages/ProjectWorkbenchPage.tsx`
   - remove creation action imports and state
   - keep project/LTR/evidence loading
   - compose read-only Workbench status and evidence panels
2. `frontend/src/features/project-workbench/ProjectWorkbenchStatus.tsx`
   - new read-only post-creation status component
3. `frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx`
   - optional extraction if evidence logic remains non-trivial
4. `frontend/src/features/project-workbench/projectWorkbenchSelectors.ts`
   - derive folder/LTR/display state without scattering conditions through JSX
5. `frontend/src/api/client.ts`
   - only if a minimal folder-state read endpoint is added
6. `frontend/src/workbench.css`
   - adjust status/evidence layout without redesigning the app shell

Likely backend changes:

1. None preferred.
2. If needed, add a read-only folder-state endpoint or project detail field using existing `ProjectFolderRecordRepository`.

Likely tests:

1. `tests/unit/test_frontend_shell_files.py`
   - add `TASK_100` boundary guard
   - update old Workbench tests that still expect creation action panels
2. Integration tests only if backend changes.

Documentation:

1. `docs/task_board.md`
   - move `TASK_100` from plan review to active only after user approval
   - record completion and validation after implementation
2. This task file
   - update `Status` to `active` when implementation starts
   - update `Status` to `done` after validation

## Acceptance Criteria

- `Projects` table uses `Open` only for confirmed projects.
- `Drafts / In Progress` uses `Continue` only for saved creation drafts.
- `/projects/{project_id}` does not render normal creation controls:
  - no application form upload action
  - no run precheck action
  - no LTR local commit action
  - no initial folder generation action
- Workbench shows post-creation project identity, LTR status, and folder/source-material state.
- Evidence placement remains only if it is clearly post-folder source material handling.
- Disabled/blocked states have concise business-readable reasons.
- No future-scope modules are surfaced.

## Validation Plan

Required after implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

If backend read model changes:

```powershell
py -m pytest tests\integration -q
```

Final verification:

```powershell
py -m pytest tests\unit tests\integration -q
git diff --check
```

Expected result:

- frontend static guard passes
- frontend build passes
- full backend test suite remains green
- `git diff --check` passes, with only known LF/CRLF working-copy warnings if present

## Risks And Mitigations

Risk: removing Workbench creation controls may break old static tests.

- Mitigation: update tests to reflect the approved post-New-Project boundary.

Risk: folder path is not currently available as a read-only Workbench field.

- Mitigation: prefer project status first; only add a narrow read endpoint if implementation discovery proves the path is required for operator clarity.

Risk: evidence placement depends on folder record state.

- Mitigation: keep evidence actions behind existing backend preview/place APIs and display backend errors as business-readable blocked states.

Risk: task expands into a file manager.

- Mitigation: only retain source/evidence placement already present in MVP; no browsing, moving, deleting, renaming, or arbitrary filesystem operations.

## Implementation Summary

- `ProjectWorkbenchPage` no longer runs creation-stage actions (form upload, precheck execution, local LTR commit, initial folder generation).
- Workbench now shows a post-creation boundary panel with read-only lifecycle facts:
  - `Created project`
  - `LTR Number registered`
  - `Project folder`
  - `Source materials`
- Evidence placement preview/place is retained as post-folder source material management.
- When folder state is not `folder_created`, Workbench shows a blocked message and disables evidence actions.
- `ProjectListPage` keeps the split:
  - confirmed projects => `Open`
  - saved drafts => `Continue`

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
py -m pytest tests\unit tests\integration -q
```

Result:

- frontend shell tests: `53 passed`
- frontend build: passed
- full backend/unit/integration suite: `409 passed`
