# TASK_140_NEW_PROJECT_DRAFT_FRICTION_CLEANUP

## Status

plan_review

## Phase / Active Task Justification

- Current Phase: `Phase 10C - New Project intake flow friction cleanup`
- Current Active Task on board: `None - awaiting next approved task`
- Why this task is allowed to plan now: New Project now creates and saves intake package/case/draft state early. The current UI still exposes deletion and replacement-confirmation controls that were designed for a more temporary draft model. This task narrows the New Project page to the actual operator workflow without changing project confirmation, LTR, folder, Matrix, Report, AI, email sending, or Outlook inbox scope.

## Step 1 Plan Only

This document is the executable implementation plan for review.
No implementation code may be written until the user approves this plan.

## Purpose

Reduce unnecessary interruption in the New Project page after manual `.msg` import and application-form selection.

ConnLab currently persists creation work as soon as a package/case/draft is created, and operator field edits are saved continuously. In that model, the New Project editing surface should behave like a workbench, not a temporary wizard that repeatedly asks whether the operator wants to discard or replace the draft.

## Task Understanding

Confirmed product rules:

- Importing a request package creates durable intake package/case/draft state.
- New Project is the creation workspace before a Project exists.
- After Project creation, normal navigation should leave New Project and open Project Workbench or the Project list.
- Backend must still protect already confirmed cases from stale browser tabs or abnormal API calls.

Goal:

- Remove `Cancel and remove draft` from the New Project primary editing page.
- Keep draft discard as a management action in `Drafts / In Progress`.
- When the operator selects a different eligible application form in the same New Project package, directly replace/rebind the current unconfirmed creation case draft.
- Remove the extra inline confirmation prompt for replacing current editor values.

## Scope

Frontend:

1. Remove the New Project page `Cancel and remove draft` action and its double-confirm state.
2. Keep normal page exit/navigation available without deleting package/case/draft records.
3. Change application-form selection from confirmation-first to direct replacement for the active unconfirmed creation case.
4. Remove the `Importing ... will replace the current editor values` confirmation panel and related CSS.
5. Show only a lightweight operational success/error message after replacement if current patterns already support it.

Backend/API:

1. Preserve existing `discard` APIs for `Drafts / In Progress` and defensive cleanup.
2. Preserve confirmed-case protection in `IntakeFormSelectionService`.
3. No new deletion semantics in this task.

Documentation:

1. Update `docs/task_board.md` after implementation.
2. Mark this task `done` after validation.

## Out Of Scope

- No duplicate email import detection.
- No same-name `.msg` comparison UI.
- No changes to project creation confirmation.
- No deletion of saved drafts from New Project.
- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, permissions, or LAN deployment.

## Proposed File-Level Changes

Likely files:

1. `frontend/src/pages/IntakeInboxPage.tsx`
   - Remove `confirmDiscard` and `exiting` state used only by New Project page discard.
   - Remove `handleDiscardDraft` if it is no longer used on this page.
   - Change selected-form replacement flow to call `selectApplicationForm(..., true)` directly.
   - Remove pending replacement confirmation state and panel.
2. `frontend/src/intake-inbox.css`
   - Remove `.new-project-import-confirmation` styles if no longer referenced.
3. `tests/unit/test_frontend_shell_files.py`
   - Update static shell expectations that currently require `Cancel and remove draft` or replacement confirmation copy.
   - Add expectations that New Project still exposes draft persistence but not delete/replacement confirmation UI.

## Acceptance Criteria

- New Project page no longer shows `Cancel and remove draft`.
- Existing saved draft discard remains available from `Drafts / In Progress`.
- Selecting a different eligible application form in New Project directly updates the active creation draft.
- The old replacement confirmation panel is removed.
- Backend confirmed-case protection remains unchanged.
- No project data, workbook, folder, or external resource behavior changes.

## Validation Plan

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

Recommended if backend tests are affected:

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py -q
```

Final:

```powershell
git diff --check
```

## Risks And Mitigations

Risk: operators lose the ability to clean up accidental imports from the New Project page.

- Mitigation: keep cleanup in `Drafts / In Progress`, where draft management belongs.

Risk: stale browser tabs could overwrite confirmed case data.

- Mitigation: keep backend confirmed-case protection unchanged and covered by existing tests.

Risk: direct replacement may surprise an operator who clicked the wrong file.

- Mitigation: this applies only before Project creation; the recovery path is to select the intended application form again or re-import the package.

## Approval Gate

After user explicitly approves this task, Step 2 implementation may start.
