# Workbench Execution Surface Density Polish Implementation Plan

## Task

`TASK_276_WORKBENCH_EXECUTION_SURFACE_DENSITY_POLISH`

## Status

Complete. Executed and validated on 2026-05-26.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_275 is complete, the task board has no active implementation task, and this is a controlled frontend-only follow-up from user smoke-test feedback.

## Product Register

`product`

ConnLab is a dense offline laboratory workbench. The UI should be quiet, operational, and business-readable. This task removes explanatory dashboard noise and keeps Matrix plus Step Workspace as the first-screen working surface.

## Problem Statement

After TASK_275, the Workbench improved its information hierarchy, but the first screen still carries too much explanatory and duplicated UI:

- Header still exposes low-value administrative metadata.
- `Last updated` implies passive freshness rather than on-demand history.
- Matrix area still contains labels that describe implementation state rather than user work.
- Filter controls and status legends consume space while users can read state directly from the Matrix table.
- Project issues/reminders and fee information compete with the Matrix/Step workflow.
- Matrix-related actions should live with the Matrix table, not inside Step Workspace or disconnected top controls.
- The right Step Workspace is the future input surface for test data, images, evidence, result judgement, and completion information, but it currently repeats Matrix metadata and shows actions that belong elsewhere.

## Target Experience

The first viewport should answer:

1. Which project/LTR is this?
2. What product/test is being executed?
3. Which test groups and steps are progressing, passed, failed, or not started?
4. Which selected step is currently in focus?
5. Where do I edit Matrix authority or move toward the Test Record workflow?
6. Where will I enter step execution data, images, judgement, and completion information?

Everything else should be hidden, removed, or moved to a secondary placement.

## Scope

### Frontend Only

Expected implementation files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts` only if needed
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Tracking files:

- `tasks/TASK_276_WORKBENCH_EXECUTION_SURFACE_DENSITY_POLISH.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

### Explicit Non-Goals

- No backend/API/domain/storage edits.
- No Matrix Editor behavior changes.
- No StepInstance or execution data persistence.
- No real activity-history modal.
- No real Test Record generation activation.
- No real fee calculation.
- No result judgement persistence or automated judgement logic.
- No report/evidence/image upload implementation.
- No broad component-library rewrite.

## Implementation Steps

### 1. Update Regression Expectations First

Files:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `tests/unit/test_frontend_shell_files.py`

Add or update checks for:

- no Matrix explanatory headings/copy:
  - `Matrix Projection`
  - `Matrix execution projection`
  - `Read-only projection`
  - `Read-only authority view`
- no Matrix status legend text
- Matrix area includes `Matrix` and `Test record`
- bottom rows still include `Sample sizes`, `Estimated completion date`, and `Status`
- token selection callback still drives Step Workspace context
- Step Workspace does not render repeated standalone `Test item`, `Section`, `Group`, or `Step token` metadata fields
- Step Workspace does not render `Edit step`, `Copy to other steps`, or `Generate record`
- Step Workspace includes compact placeholders for result judgement, estimated completion, actual completion, and bottom intake actions
- static guard prevents reintroducing the removed filterbar and always-visible issues/reminders
- static guard verifies explanatory Matrix copy removal in both `ProjectWorkbenchLayout.tsx` and `ProjectWorkbenchMatrixProjectionPanel.tsx`

### 2. Compress Header Identity

File:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Change header identity to one line:

```text
<LTR or temporary project id> · <product description> · <test description>
```

Rules:

- Start with LTR when available.
- Use a temporary project marker when no LTR exists.
- Use only an existing frontend-available test-description source.
- If no test description is available in current frontend state, use stable fallback copy: `Test description unavailable`.
- Do not show business unit or requester in the main header identity.
- Keep text to one line with responsive truncation instead of wrapping into multiple lines.

Replace `Last updated` with:

```text
View activity history
```

If no real activity modal exists in current approved scope, keep it as an inert/placeholder action with styling that does not imply data mutation.

### 3. Remove Top Dashboard Metrics And Filterbar

File:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Remove the first-screen surfaces for:

- top execution metric strip/cards if still present
- test item category selector
- active-item/status-icon/marker checkboxes
- status filter radio controls
- filterbar row navigation controls

Any Matrix execution signal that remains must move into the Matrix surface and stay compact.

### 4. Distill Matrix Surface

Files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`

Remove user-facing explanatory labels (across Layout and Panel, depending on where each string is currently rendered):

- `Matrix Projection`
- `Matrix execution projection`
- `Read-only projection`
- `Read-only authority view`

Remove the status legend. The table cells already carry status through label and color.

Add Matrix-local controls:

- `Matrix`: calls existing Matrix Editor navigation callback.
- `Test record`: remains disabled/placeholder unless there is already a safe non-mutating route/action in current code.

Preserve:

- Matrix table itself
- group columns
- token click handling
- bottom rows for sample sizes, estimated completion date, and status
- limited status set: `Not started`, `In progress`, `Pass`, `Failed`

### 5. Remove Issues/Reminders From First Screen

File:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Remove always-visible `Project issues / reminders`.

Do not replace it with a new card. If future issues/reminders are needed, they should be introduced by a later task with a clear trigger and data source.

### 6. Move Fee Estimate To Right Column

Files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/workbench.css`

Move the total-only `Fee estimate` surface below or with the right Step Workspace column.

Rules:

- It should visually align with the Step Workspace.
- It remains total-only.
- It must not show spent/remaining breakdown.
- It must not implement fee calculation.

### 7. Refocus Right Step Workspace

File:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Treat the right Step Workspace as the future execution data-entry area.

Remove duplicated standalone metadata fields when already represented by the selected Matrix context:

- `Test item`
- `Section`
- `Group`
- `Step token`

Remove misplaced action buttons:

- `Edit step`
- `Copy to other steps`
- `Generate record`

Reposition execution intake controls:

- Move `Image` to the bottom action row with `Import data`.
- Keep inactive/future actions visually disabled or placeholder-only when no approved implementation exists.

Simplify lifecycle:

- Replace the full multi-stage lifecycle row with one dynamic status label such as `Not started`, `In progress`, `Pass`, or `Failed`.
- Do not render every lifecycle step at once.

Clarify completion and result:

- Distinguish `Estimated completion` from `Actual completion`.
- Add a `Result judgement` display/edit placeholder.
- Do not implement persistence or automated judgement logic.

### 8. CSS Density And Responsiveness Pass

File:

- `frontend/src/workbench.css`

Update classes affected by:

- one-line header truncation
- removed filterbar/metrics sections
- Matrix toolbar/action placement
- right-column Step Workspace plus fee stacking
- simplified Step Workspace execution input layout
- removed issues/reminders card

Keep the UI dense and operational:

- no nested card stacks
- no decorative hero/card treatment
- stable table dimensions
- no overlapping text at desktop widths

### 9. Validation

Run:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

Then from repository root:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task276 or task275 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

Manual browser smoke:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

Check:

- header identity is a single line led by LTR or temporary id
- no business unit/requester in main header identity
- `View activity history` replaces `Last updated`
- no filterbar
- no Matrix explanatory/read-only labels
- no status legend
- no issues/reminders card
- Matrix and Test record controls sit with the Matrix surface
- Step Workspace remains the right-side selected-token context
- Step Workspace no longer repeats Matrix metadata fields or misplaced actions
- Step Workspace shows compact lifecycle status, estimated completion, actual completion, and result judgement placeholder
- Fee estimate sits under or with the right Step Workspace

### 10. Completion Updates

After implementation and validation only:

- update `tasks/TASK_276_WORKBENCH_EXECUTION_SURFACE_DENSITY_POLISH.md` to Complete
- update `docs/task_board.md`
- update `docs/task_plan_index.md`
- summarize changed files and validation results

## Risks

1. Removing the filterbar may hide a useful future affordance.
   - Mitigation: this task follows current user feedback; future filtering can return as a secondary action if real use proves it necessary.
2. Moving `Test record` near Matrix may imply active generation.
   - Mitigation: keep it disabled/placeholder unless an approved safe route already exists.
3. Compacting header text may overflow on smaller widths.
   - Mitigation: use responsive truncation and browser smoke check.
4. Removing issues/reminders may reduce visibility for exceptions.
   - Mitigation: current scope removes the always-visible card only; exception surfacing can be reintroduced with a later task tied to real data and clear trigger.
5. Refocusing Step Workspace could accidentally imply test data persistence exists.
   - Mitigation: keep all new execution input surfaces as non-mutating placeholders unless a current approved API already exists.

## Acceptance Criteria

1. Header uses a one-line LTR/temp-id first identity and includes test description when available, otherwise `Test description unavailable` fallback.
2. Header does not show business unit or requester as primary identity.
3. `View activity history` replaces `Last updated`.
4. Top metric strip/cards and filterbar are removed from first screen.
5. Matrix explanatory/read-only labels and status legend are removed.
6. Matrix area contains `Matrix` and `Test record` controls.
7. `Test record` does not perform unapproved generation.
8. `Project issues / reminders` is not always visible.
9. Fee estimate is aligned under/with the right Step Workspace and remains total-only.
10. Matrix table bottom rows and token-to-Step-Workspace selection still work.
11. Right Step Workspace removes duplicate `Test item`, `Section`, `Group`, and `Step token` standalone metadata fields.
12. Right Step Workspace removes `Edit step`, `Copy to other steps`, and `Generate record`.
13. `Image` is grouped with bottom execution intake actions such as `Import data`.
14. Step lifecycle is shown as one compact status label.
15. Step Workspace distinguishes estimated completion from actual completion and includes a result judgement placeholder.
16. Relevant frontend tests, static guards, build, smoke integration, backend no-change check, and diff check pass.

## Recommended Execution Mode

Use:

```text
superpowers:executing-plans
```

This task should be executed serially because the main risk is accidentally removing live wiring while reducing visual clutter.
