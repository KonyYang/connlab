# TASK_283F_STEP_REQUIREMENT_TO_TEST_RECORD_REMARK_BINDING

## Status

Complete (2026-06-02).

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Make Test Record `Remark` use step-level `Requirement` output instead of raw row-level Matrix `requirement`, so multi-step LLCR renders correct per-step requirement text in generated Word.

## Why This Task Exists

Current behavior has a gap:

1. Matrix Editor right-side Step Workspace computes step-level requirement variants (for example LLCR `Initial <= ...` vs `DeltaR <= ...`).
2. Test Record generation still uses preview step requirement mapped directly from row-level `requirement`.
3. Result: generated Test Record `Remark` can ignore step-level variants and remain row-level text.

This task closes that gap by introducing a deterministic, backend-owned step requirement mapping path used by generation consumers.

## Scope

### In Scope

1. Introduce deterministic step-level requirement mapping in backend preview/build path.
2. Ensure Test Record generation uses step-level requirement value for each group step row.
3. Keep LLCR multi-step split behavior consistent with accepted rule:
   - initial step: `<= <initial value>`
   - subsequent steps: `DeltaR <= <delta value>`
4. Define and lock partial LLCR strategy:
   - when only `initial` exists and no `delta` can be extracted, only the initial step is rewritten to `<= <initial value>`;
   - all subsequent LLCR steps keep the original row requirement unchanged.
5. Add tests covering:
   - preview step requirement mapping.
   - Word gateway `Remark` output for multi-step LLCR.
   - non-sequential token ordering behavior (for example `5,2`).
   - no regression for non-LLCR rows.
6. Keep Matrix row-level `method/condition/requirement` as authority source input.

### Out Of Scope

1. No StepInstance persistence model.
2. No execution record persistence.
3. No report-generation redesign beyond current Test Record mapping fix.
4. No AI/LLM interpretation.
5. No frontend UX redesign unless strictly required by the mapping contract.

## Acceptance Criteria

1. Generated Test Record `Remark` reflects per-step requirement mapping, not blind row-level copy.
2. LLCR split output:
   - initial step uses `<= ... mOhm`.
   - follow-up steps use `DeltaR <= ... mOhm`.
3. Partial LLCR output (only initial, no delta):
   - initial step uses `<= ...`.
   - follow-up steps keep original row requirement unchanged.
4. LLCR step classification uses final sorted step order by `sequence` (stable tie-break by `raw_token`), not row traversal order.
5. Existing Matrix authority flow remains unchanged.
6. Existing non-LLCR families do not regress.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded deterministic mapping and consumer-wiring change across existing backend services and tests.

## Stop Rule

Create and approve a separate implementation plan before coding.
