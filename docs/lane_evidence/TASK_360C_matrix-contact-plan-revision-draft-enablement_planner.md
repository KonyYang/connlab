# TASK_360C Matrix Contact Plan Revision-Draft Enablement Planner Evidence

Date: 2026-07-11

Role: Planner

Status: implementation_authorized, pending Developer implementation pass.

## Discovery Outcome

The authorized live smoke is reproducible from current source behavior, not an inferred product issue. After confirmation, Matrix Editor loads an authority projection with no saved revision-draft id. The quantity effect clears its draft-only target items, so Contact Measurement Plan shows zero targets and refuses save. TASK_360B correctly blocks because it reads confirmed authority only and there are no included confirmed targets.

The repository already has the safe bridge: `POST /api/projects/{project_id}/matrix-revisions`, the existing typed `createMatrixRevisionDraft()` helper, session reload, and confirmed Step quantity/contact-plan carry-forward. The missing surface is one explicit Matrix Editor action to create or recover that revision draft.

## Planned Scope

- Add one inline editable-draft action and draft-required affordance in the existing Matrix Editor workflow.
- Reuse existing revision creation and reload the session instead of changing backend/API/client contracts.
- Keep Contact Measurement Plan draft-only for edits, then preserve existing Confirm Matrix promotion and TASK_360B confirmed-only preview/generate behavior.

## Scope Locks

- No backend/API/schema/revision-flow modifications.
- No changes to Fee, generic Test Record, specialized workbook behavior, parser/import, LTR/public-drive, StepInstance, Report, real files, release/settings, `.agents/**`, or `docs/project_management/**`.
- Existing Fee rule/seed/test worktree residuals are external and excluded.

## Definition Of Ready

Reviewer plan gate and implementation-readiness passed after docs-only Developer planning-first. The user then approved reconciliation plus Developer implementation. The scope remains limited to the existing typed revision create, `409` recovery, session reload, and confirmed contact-plan carry-forward bridge.

## Recommended Next Role

Developer implementation pass.

## Validation Record

- Read Matrix Editor session seed/save/confirm behavior, Step quantity load/save behavior, revision API/service, confirmed quantity carry-forward, TASK_360A/360B task and QA evidence, and the current board.
- Confirmed `TASK_360C` identifiers were unused before this planning pass.
- Confirmed current worktree product residuals are limited to external Fee rule/seed/test files and are excluded from this lane.
