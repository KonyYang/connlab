# TASK_315D Follow-up Plan: Remove Fee Confirm Status Card

Status: Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Active Task

`TASK_315D_FOLLOWUP_REMOVE_FEE_CONFIRM_STATUS_CARD`

## Why This Is Allowed

This is a narrow UI follow-up explicitly requested from the live Fee Evaluation page after `TASK_315D` completion. It removes a low-value status card from the Fee Evaluation form without changing backend authority behavior or Project Folder gating.

## Implementation Plan

1. Remove the `confirmedFeeViewState` display model from `FeeEvaluationReviewExportPage`.
2. Remove the `confirmedFeeViewState` prop and `Confirmed Fee status` card markup from `FeeEvaluationPreviewTable`.
3. Remove unused status-card CSS from `workbench.css`.
4. Update Fee Evaluation tests to verify the status card is absent while Confirm Fee remains gated by autosave/signature state.
5. Update static frontend guards so the removed status card does not return accidentally.
6. Run focused frontend tests, static guards, and build.

## Risks

- Confirm Fee gating could accidentally be tied to the removed display model. Mitigation: keep `confirmFeeBlocker` unchanged and test button behavior.
- Existing tests that asserted the status card copy need to be rewritten around behavior rather than display text.

## Validation

- `npm test -- --run FeeEvaluationReviewExportPage --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee"`
- `npm run build`

## Completion Summary

The status card has been removed from the Fee Evaluation form. Confirm Fee behavior remains controlled by the existing draft/signature gates and the fixed bottom action dock remains unchanged.
