# QUICK_FIX_20260628_NO_MATRIX_WORKBENCH_DRAFT_PREVIEW

Status: integrator_accepted
Role: Quick Fixer
Date: 2026-06-28

## Scope

Lightweight frontend-only Workbench UI fix after `TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT` was accepted.

Allowed quick-fix scope:

- Reduce no-Matrix Workbench explanatory copy.
- Make the no-Matrix Matrix area visually align with the active Matrix Workbench: left Matrix-like table, right Step workspace / Folder Action rail.
- Preserve existing Workbench commandbar and lifecycle behavior.

Must not touch:

- backend / API / schema / database
- frontend API client
- Projects list
- Matrix Editor business logic
- StepInstance / Report / AI / permissions / LAN/server / multi-user future scope
- accepted TASK_344C evidence or board closeout

## Changed Files

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`

## Implementation Notes

- `NoMatrixWorkspaceEmptyState` now renders a Matrix-like read-only table.
- If a Workbench `matrixCandidateDraft` or `matrixDraft` exists, the table is derived from `ProjectTestPlanDraft.payload.groups[].steps[]`.
- If no draft rows exist, the Workbench shows the same starter Visual Examination row used by the Matrix Editor default initialization:
  - `Visual Examination`
  - `EIA-364-18B`
  - `10x min magnification`
  - `No detrimental condition`
- The no-Matrix right rail now shows `Step workspace` and `Folder Action`.
- Long no-Matrix explanatory copy is removed from the visible Workbench area.
- No backend/API/client/lifecycle rule changes were made.

## Validation

- `npm test -- ProjectWorkbenchLayout.test.tsx ProjectWorkbenchCloseConfirmation.test.tsx ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - result: pass, `3` files / `50` tests
  - note: expected console error remains in the Matrix projection error-state test.
- `npm test -- ProjectWorkbenchLayout.test.tsx`
  - result: pass, `39` tests
- `npm run build`
  - result: pass
  - note: existing Vite chunk-size warning only.
- Browser smoke via in-app browser:
  - registered/no-Matrix fixture `7c55618e2acc41bd9973b7e4eaaf7e0f`: pass
  - temporary/no-LTR fixture `c4f39233742949febda453a428bd5e42`: pass
  - observed: no-Matrix table present, Step workspace present, Folder Action present, long Matrix helper copy absent.
- `git diff --check -- frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css`
  - result: pass with CRLF working-copy warnings only.

## Residual Risk

Low. This is a display-only quick fix. The fallback starter row is duplicated from current Matrix Editor initialization because those helper functions are local to `MatrixEditorWorkspace.tsx`; extracting them to a shared model should be a separate formal lane if desired.

Integrator residual: fallback starter row duplication remains non-blocking. If the team wants to remove it, route a future formal shared Matrix preview model lane rather than expanding this quick fix.

## Next Recommendation

No Reviewer/QA gate is required for this quick fix unless the user wants formal acceptance. If the team wants closed-project reactivation or lifecycle model changes, route to Planner as a formal lane.

## Integrator Lightweight Packaging Checkpoint

Status: `integrator_accepted`
Date: 2026-06-28

Reviewer callback: `reviewer_pass`. QA not required because Quick Fixer completed browser smoke and Reviewer reran focused tests/build/static checks.

Accepted package files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/QUICK_FIX_20260628_no_matrix_workbench_draft_preview.md`

Excluded residuals:

- `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*`.
- backend/API/schema/database/frontend API client.
- Projects list.
- Matrix Editor business logic.
- TASK_343/TASK_344 accepted task/evidence/board files.
- StepInstance, Report, AI, permissions, LAN/server, and multi-user future scope.

Integrator validation:

- Focused tests passed: `3` files / `50` tests. The Matrix projection error-state console error is expected by that test.
- Frontend build passed with the existing non-blocking Vite chunk-size warning only.
- Package diff check passed with LF/CRLF working-copy warnings only.
- Trailing whitespace and forbidden-scope checks passed.

Stop point: local controlled quick-fix commit only. Remote push intentionally not performed.

## Quick Fix Follow-up Checkpoint

Status: `quick_fix_followup_verified`
Date: 2026-06-28

Reason:

- User observed that no-Matrix Matrix step tokens looked like steps but were not clickable, so the right Step workspace did not respond.
- Quick Fixer self-review also identified readonly action guard and narrow-table residual risks.

Follow-up changes:

- Converted no-Matrix preview tokens from static text to selectable buttons.
- Selecting a token updates the right `Step workspace` with group/step context plus method, condition, and requirement.
- Default selection now uses the first visible preview token so the right rail is not inert.
- `Fee Evaluation` is disabled when lifecycle readonly is active, including no-Matrix projects with a draft.
- no-Matrix preview group columns now use stable internal keys to avoid label collisions.
- Added horizontal overflow protection for the no-Matrix preview table and single-column stacking at narrow widths.

Validation:

- `npm test -- ProjectWorkbenchLayout.test.tsx`
  - result: pass, `40` tests
- `npm test -- ProjectWorkbenchLayout.test.tsx ProjectWorkbenchCloseConfirmation.test.tsx ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - result: pass, `3` files / `51` tests
  - note: expected console error remains in the Matrix projection error-state test.
- `npm run build`
  - result: pass
  - note: existing Vite chunk-size warning only.
- `git diff --check -- frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css`
  - result: pass with CRLF working-copy warnings only.

Residual risk:

- Browser smoke was rerun after the follow-up at:
  - registered/no-Matrix fixture `7c55618e2acc41bd9973b7e4eaaf7e0f`
  - temporary/no-LTR fixture `c4f39233742949febda453a428bd5e42`
- Both browser smoke paths confirmed:
  - no-Matrix preview table is visible
  - `Step workspace` is visible
  - `Folder Action` is visible
  - long Matrix helper copy is absent
  - preview token `1` is clickable and remains selected
  - right `Step workspace` shows `EIA-364-18B`, `10x min magnification`, and `No detrimental condition`
- The original project URL `72fbbfa290294da9a507344b68ff900f` currently renders an active Matrix projection, not a readonly no-Matrix shell, so it was not a valid browser fixture for the no-Matrix readonly guard. The readonly Fee guard remains covered by focused regression tests.
- This remains display-only no-Matrix preview behavior. Real StepInstance editing is still future scope and was not implemented.
