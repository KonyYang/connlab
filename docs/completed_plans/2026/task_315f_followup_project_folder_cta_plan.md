# TASK_315F Follow-up Plan: Project Folder CTA In Workbench Commandbar

Status: Approved for implementation.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Active Task ID

`TASK_315F_FEE_CURRENT_VERSION_CANCEL_UPDATE_SEMANTICS` is complete. This plan treats the browser comment as a narrow user-approved follow-up candidate for the completed Phase 11 Workbench/Fee authority surface, not as a new Matrix execution feature.

## Why This Is Allowed Now

The requested change is limited to the existing Project Workbench commandbar after active Matrix authority exists. It does not add StepInstance, execution persistence, report generation, AI review, permissions, LAN/server, multi-user behavior, or backend authority semantics.

## User Request

In the `Project commands` area, remove the visible status chips such as `Matrix confirmed`, `Fee v19 confirmed`, and `Folder generated`. Backend authority confirmation is enough; the frontend does not need to restate those states as chips. Instead, permanently display the project folder action button. The button should become clickable only when both Matrix authority and Fee authority versions exist and the existing folder preview says the operation is actionable.

If the project folder does not exist yet, the button label should be `Generate project folder`. If the project folder already exists, the same permanent button should display `Updated project folder`.

## Existing Behavior

`frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` currently renders:

- Three status chips for Matrix, Fee, and Folder readiness.
- `Open Matrix` and `Open Fee` buttons.
- A primary folder command only when `effectiveFolderReady` is false.
- A disabled `History` button for a planned future surface.

Current folder button availability is based on `officialWorkspaceStatus` being `ready` or `adoptable`. The button is hidden after folder readiness is true.

## Proposed Scope

Implement a frontend-only Workbench commandbar adjustment:

1. Remove the visible `Project status` chip group from the active Matrix commandbar.
2. Always render the folder CTA in the commandbar.
   - Use `Generate project folder` before the project folder exists.
   - Use `Updated project folder` after the project folder exists.
3. Enable the folder CTA only when:
   - `activeMatrixAuthorityReady` is true.
   - `confirmedFeeLatest?.status === "current"`.
   - The existing folder preview status is actionable, meaning `officialWorkspaceStatus` is `ready` or `adoptable`.
   - The folder command is not already creating.
4. Keep the existing folder command handler and backend safety behavior. If the folder already exists, the button label changes to generated/update-state language, but the implementation must not introduce unsafe overwrite behavior or new backend semantics.
5. Keep the Matrix Editor and Fee entry buttons as secondary actions. The Matrix entry label should read `Matrix Editor`.
6. Remove the disabled `History` button from this commandbar if it remains part of the same status-info noise the user selected.

## Out Of Scope

- No backend API changes.
- No new folder overwrite or regeneration semantics.
- No change to Matrix/Fee authority creation.
- No Fee history UI.
- No activity history UI.
- No Required Forms generation changes.
- No StepInstance, report, AI, permissions, LAN/server, or multi-user scope.

## File-Level Changes

Expected implementation files:

- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - Replace status-chip rendering with a permanent folder CTA.
  - Derive folder CTA disabled state from Matrix authority, current Fee authority, folder preview readiness, and creating state.
  - Remove now-unused `StatusChip` and `formatFeeAuthorityLabel` helpers if no longer referenced.

- `frontend/src/workbench.css`
  - Adjust `.runtime-console-commandbar` layout for secondary actions plus the permanent folder CTA.
  - Remove or leave harmless unused status-chip CSS depending on nearby reuse.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - Update expectations that currently assert status-chip behavior or hidden folder CTA after folder generation.
  - Add coverage that `Generate project folder` is always visible.
  - Add coverage that it is disabled when Matrix authority or current Fee authority is missing/stale.
  - Add coverage that it is enabled when Matrix and Fee authority are current and folder preview is actionable.

## UX Detail

The commandbar should become action-led rather than status-led:

- Secondary actions: `Matrix Editor`, `Open Fee`
- Primary action:
  - `Generate project folder` when the folder is not recorded/generated.
  - `Updated project folder` when the folder already exists.

When disabled, the button title should explain the first blocker in operational language:

- Missing Matrix authority: `Confirm Matrix before generating the project folder.`
- Missing or stale Fee authority: `Update Fee before generating the project folder.`
- Missing template or target path: `Project folder template or target path is not ready.`
- In progress: `Generating project folder...`

The title tooltip should be used only for disabled guidance. When the button is enabled, it should not show extra status explanation on hover; the backend authority and existing preview checks are the source of truth.

## Risks

- If `effectiveFolderReady` is true, the existing `onFolderCommand` branch may invoke the selected Project Folder task action instead of creating a new folder. The implementation must align the `Updated project folder` label with current safe frontend behavior without changing backend overwrite semantics.
- Existing tests may rely on the old hidden-button behavior when folder generation is complete. Those tests should be updated to the new permanent CTA rule.
- The commandbar should stay compact in the 754px-wide browser viewport shown in the comment.

## Validation Plan

Run focused frontend checks:

```bash
cd frontend
npm test -- --run ProjectWorkbenchLayout --watch=false
npm run build
```

Run static guard tests if the UI shell expectations are touched:

```bash
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project or folder or task315"
```

Manual browser smoke:

1. Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
2. Confirm the `Project commands` area no longer shows Matrix/Fee/Folder status chips.
3. Confirm the folder CTA is always visible.
4. Confirm the label is `Generate project folder` before a folder exists and `Updated project folder` after a folder exists.
5. Confirm it is enabled only when current Matrix authority, current Fee authority, and folder preview readiness are present.
6. Confirm disabled hover/title guidance appears only when the button is blocked.

## Stop Point

After implementation and validation, update `docs/task_board.md` with a TASK_315F follow-up completion note and stop. Do not proceed to another task.

## Approved Addendum: Matrix Editor Fee Evaluation Entry

The user approved a narrow placement follow-up on 2026-06-18: because Fee Evaluation is bound to the active Matrix, add a `Fee Evaluation` entry to the Matrix Editor target header beside `Import Matrix` and `Test record`.

Scope:

- Add a Matrix Editor header action labeled `Fee Evaluation`.
- Reuse the existing project Fee Evaluation route and page.
- Keep the Workbench `Open Fee` shortcut unchanged.
- Do not change Fee authority semantics, pricing draft behavior, Matrix Confirm behavior, Test Record generation, or backend APIs.

Expected file-level changes:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Accept a narrow `onOpenFeeEvaluation` callback and render the new header action.
- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
  - Pass the callback through from the route page.
- `frontend/src/App.tsx`
  - Wire the callback to `/projects/{projectId}/fee-evaluation`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Cover that the header action is visible and invokes the navigation callback.

Validation:

```bash
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
npm run build
```

Manual browser smoke:

1. Open `/projects/72fbbfa290294da9a507344b68ff900f/matrix-editor`.
2. Confirm the header shows `Import Matrix`, `Test record`, and `Fee Evaluation`.
3. Click `Fee Evaluation` and confirm the app navigates to `/projects/72fbbfa290294da9a507344b68ff900f/fee-evaluation`.
