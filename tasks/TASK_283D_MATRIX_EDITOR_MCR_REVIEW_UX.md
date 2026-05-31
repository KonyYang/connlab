# TASK_283D_MATRIX_EDITOR_MCR_REVIEW_UX

## Status

Planned follow-up. Do not implement until TASK_283A/B/C decisions establish the backend data available for review.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Improve Matrix Editor's Method/Condition/Requirement review experience so operators can quickly confirm or correct automatically filled values.

This task should not change the source of truth. It should make automatic fill provenance and review needs visible in the existing Matrix Editor workflow.

## Scope

### In Scope

1. Show concise provenance/status for prefilled MCR cells, for example:
   - `From spec section 6.1`
   - `Template fallback`
   - `Needs review`
2. Add low-noise review affordances in Matrix Editor.
3. Keep all MCR values directly editable.
4. Keep `Confirm Matrix` as the existing authority action.
5. Use `$impeccable` product UI guidance and existing Matrix Editor component boundaries.

### Out Of Scope

- No new Matrix authority lifecycle.
- No Method Library maintenance UI unless separately approved.
- No StepInstance, execution persistence, report generation, fee, evidence/image, AI, permission, or multi-user scope.
- No frontend Office parsing.

## Acceptance Criteria

1. Operators can distinguish extracted, fallback, missing, and manually edited values without reading backend terminology.
2. The UI remains dense and workbench-like, with no large extra import step.
3. Existing Matrix Editor confirm, group selection, sample guard, and row classification behavior remain intact.
4. All API calls remain in `frontend/src/api/client.ts`.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution because this is a bounded React/TypeScript UX task using existing Matrix Editor feature boundaries.

## Stop Rule

Create a separate implementation plan before coding.

