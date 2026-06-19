# TASK_322 Matrix Editor confirm-status jank hotfix plan

> Status: Draft for user review. Do not implement before explicit approval.
> Date: 2026-06-19
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Active task candidate: TASK_322_MATRIX_EDITOR_CONFIRM_STATUS_JANK_HOTFIX

## 1. Why this task is allowed now

The current task board has no active implementation task after TASK_315F completion. The user directly reported a Matrix Editor UX defect on `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/matrix-editor` and requested a UI-only correction.

This is a narrow out-of-sequence UI hotfix candidate because it does not add Matrix execution scope, StepInstance, report automation, AI review, permissions, LAN deployment, multi-user behavior, or new business workflow. Implementation still requires explicit user approval after this plan.

## 2. Observed root cause

Browser reproduction:

- Static Matrix Editor page: `.matrix-editor-grid-surface` top was about `135px`.
- After editing `Row 1 test item`, autosave state rendered `Preparing confirm...` in `.matrix-editor-save-status`.
- The status section was inserted between the target header and the grid surface.
- Grid top moved to about `181px`, and `Show selected groups only` moved with it.
- No browser console errors were recorded during reproduction.

Code root cause:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` maps `saveState === "saving"` to `Preparing confirm...`.
- The message is rendered as a standalone `<section className="matrix-editor-save-status">` above the Matrix grid.
- `frontend/src/workbench.css` styles `.matrix-editor-save-status` as a visible bordered card with margin and padding, so transient save states change document layout.

## 3. Scope

In scope:

- Remove normal Matrix autosave progress copy from the top-level layout flow.
- Keep operator-blocking errors visible and actionable.
- Keep existing Confirm Matrix gating and bottom dock blocker text.
- Keep API calls and backend behavior unchanged.
- Add focused regression coverage for the UI behavior.

Out of scope:

- No backend changes.
- No new Matrix authority semantics.
- No StepInstance, report, AI, permissions, LAN, or multi-user work.
- No broad Matrix Editor component extraction.
- No redesign of the Matrix table, group model, or autosave lifecycle.

## 4. Recommended UX decision

Use the quietest operator-facing behavior:

- Do not show `Editing`, `Saving Matrix draft...`, `Preparing confirm...`, or `Saved` as visible cards.
- If draft save fails, show a compact inline error beside `Show selected groups only` inside the Matrix grid control row.
- Keep the bottom Confirm dock message for disabled Confirm action, for example `Saving Matrix draft before confirm...` or `Autosave failed. Retry before confirming.`

Rationale:

- Lab operators do not need to understand autosave internals.
- Normal save progress should not move the work surface.
- Failures that block Confirm still need visible feedback; hiding all failures only in logs would leave users stuck.
- Placing failure feedback in the grid control row matches the user's suggested location and avoids pushing the editor down.

## 5. File-level design

Expected implementation files:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Change `AUTO_SAVE_STATUS_COPY` or derived `editorStatusMessage` so normal autosave states return no visible top-level message.
  - Keep save failure copy available as an inline grid control row message.
  - Remove or stop rendering the top-level `editorStatusMessage` section above `.matrix-editor-studio`.
  - Add inline markup near `.matrix-editor-filter-toggle`, likely:
    - checkbox label on the left
    - compact status text on the right only for save errors

- `frontend/src/workbench.css`
  - Add a small grid toolbar/control-row style if needed.
  - Ensure status text beside the filter does not alter vertical layout when absent.
  - Keep existing `.matrix-editor-save-status` only if still needed by test-record messages, or split test-record status into a more specific class later if required.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Add/adjust tests proving `Preparing confirm...` is not rendered as a visible top-level card during autosave.
  - Add/adjust tests proving save errors remain visible and Confirm stays blocked.

- `tests/unit/test_frontend_shell_files.py`
  - Update shell assertions that currently require `Preparing confirm...`.
  - Add a guard that Matrix Editor does not wire `Preparing confirm...` as visible operator copy.

## 6. Validation plan

Automated:

```text
cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task322"
cd frontend; npm run build
```

Manual browser smoke:

1. Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/matrix-editor`.
2. Note the `Show selected groups only` row position.
3. Edit a Matrix cell to trigger autosave.
4. Confirm no `Preparing confirm...` card appears above the editor and the Matrix grid does not jump downward.
5. Confirm `Confirm Matrix` still stays disabled while a required draft save is pending or failed.

## 7. Risks

- The Matrix Editor files are currently dirty in the working tree, so implementation must preserve existing uncommitted work.
- Existing tests intentionally assert `Preparing confirm...` exists, so they must be updated to the new approved UX.
- If autosave can remain stuck in `saving`, removing the top status makes the bottom Confirm dock blocker the remaining user-visible signal. This is acceptable because the blocker is tied to the action being attempted.

## 8. Review checklist before coding

- Current phase stated: Phase 11 controlled foundation.
- Current active task ID stated: TASK_322_MATRIX_EDITOR_CONFIRM_STATUS_JANK_HOTFIX candidate.
- Allowed reason stated: user-requested Matrix Editor UI-only hotfix; no future scope.
- Implementation is blocked until user approval.
- No implementation code changed in this planning step.
