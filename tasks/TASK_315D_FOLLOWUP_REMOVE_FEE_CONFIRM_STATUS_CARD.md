# TASK_315D Follow-up: Remove Fee Confirm Status Card

Status: Complete.

## Goal

Remove the visible Confirmed Fee authority status card from the Fee Evaluation page. The page should behave like a fee evaluation form: operators edit/review pricing and use the fixed bottom `Cancel` / `Confirm Fee` actions.

## Scope

- Remove the visible `Confirmed Fee status` card from `FeeEvaluationPreviewTable`.
- Remove the page-level `confirmedFeeViewState` display model used only by that card.
- Keep Confirm Fee gating, autosave, discard, and authority update behavior unchanged.
- Keep Confirm Fee error/success feedback and the fixed bottom action dock.
- Add/update frontend and static tests proving the card is absent.

## Out Of Scope

- No backend API changes.
- No Confirm Fee authority contract changes.
- No Project Folder readiness changes.
- No Matrix rebase or promotion changes.

## Acceptance

- Fee Evaluation page no longer renders the `Confirmed Fee status` card.
- Normal current status text such as `Fee authority is current.` is not shown in the main form.
- Right-bottom `Cancel` and `Confirm Fee` remain available according to existing gating.
- Confirm Fee still submits the existing backend-compatible internal actor.
- Relevant tests and build pass.

## Completion Notes

- Removed `confirmedFeeViewState` and the Confirmed Fee status card DOM.
- Removed unused status-card CSS, including the stale `fee-evaluation-confirm-button` styles.
- Updated tests to assert the card remains absent while Confirm Fee behavior continues to work.
