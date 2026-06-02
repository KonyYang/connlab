# TASK_283D_MATRIX_EDITOR_MCR_REVIEW_UX

## Status

Complete (2026-06-01). TASK_283A/B/C/E backend prerequisites are complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Improve Matrix Editor's Method/Condition/Requirement review experience so operators can quickly confirm or correct automatically filled values.

This task should not change the source of truth. It should make automatic fill provenance and review needs visible in the existing Matrix Editor workflow.

Business positioning:

- TASK_283D is a review UX layer only.
- It does not change extraction/normalization authority logic from TASK_283A/B/E.
- It does not introduce report-generation logic or historical-candidate ingestion logic (TASK_283C).

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
6. Use already available backend notes/status signals only (no new backend API contract in this task unless absolutely required and separately approved).
7. Edited status has highest display priority over Template/Needs review when user changes a field value.

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
5. No-section fallback rows from TASK_283E are visibly distinguishable from section-derived rows.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution because this is a bounded React/TypeScript UX task using existing Matrix Editor feature boundaries.

## Stop Rule

Create a separate implementation plan before coding.
