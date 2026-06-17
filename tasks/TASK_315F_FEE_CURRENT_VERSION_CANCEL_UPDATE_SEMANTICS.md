# TASK_315F: Fee Current Version Cancel And Update Semantics

Status: Complete.

## Goal

Align Fee Evaluation with the Matrix authority lifecycle: after Matrix Confirm, the current Matrix authority version must have a durable Fee current working version. Opening Fee Evaluation edits that Matrix-bound Fee working version. `Cancel` must discard only the current page editing session and return to Workbench without deleting the saved Fee pricing payload. The primary action should read as `Update Fee`, creating or refreshing the Confirmed Fee authority revision from the saved current pricing payload.

## Business Rule

Matrix remains the authority for group and step structure. Fee Evaluation follows that structure and owns pricing details only:

- Matrix Confirm seeds or promotes the current Fee Evaluation pricing payload for the current Matrix authority version.
- The current Fee Evaluation pricing payload is the durable Fee working version for that Matrix authority version and must not be removed by normal page cancellation.
- Fee Evaluation cannot add, remove, or reorder Matrix groups/steps.
- `Cancel` means leave the page and discard this page session's edits back to the entry baseline. It is not a Fee current-version delete operation.
- `Update Fee` means publish the latest saved Fee pricing payload as a new Confirmed Fee authority revision.

## Current Problem

`Cancel` in Fee Evaluation currently calls the pricing draft DELETE endpoint after prompting:

```text
Discard Fee Evaluation pricing edits and return to Workbench?
```

That deletes the saved pricing draft for the current Matrix/Fee-rule context. When the operator returns to Fee Evaluation, the form can be empty or reset to defaults, which conflicts with the expectation that each confirmed Matrix has a corresponding Fee Evaluation current version.

The primary button currently reads `Confirm Fee`, which suggests a one-time first confirmation. After Matrix-to-Fee promotion and incremental updates, the intended user action is closer to updating the current Fee authority revision.

## Scope

- Change Fee Evaluation `Cancel` behavior so normal cancellation does not call the pricing draft DELETE endpoint.
- Keep the saved current pricing payload available after leaving and reopening Fee Evaluation.
- If the page has local edits, cancel must stop pending autosave and restore the entry baseline safely instead of deleting the pricing payload.
- If an in-flight autosave cannot be confirmed complete before baseline restore, Cancel must stay on the Fee Evaluation page and ask the operator to retry instead of navigating away with uncertain server state.
- Baseline restore must verify that the entry Matrix/Fee context still matches the current server context and must send expected Matrix/Fee context tokens with the restore write. If the context changed, Cancel must stay on the page and ask the operator to refresh.
- Rename the primary action from `Confirm Fee` to `Update Fee` in the Fee Evaluation page.
- Keep the backend Confirmed Fee version creation endpoint and service behavior unless a narrow compatibility wrapper is required.
- Update user-facing copy and frontend regression tests for the new semantics.
- Add focused backend/API regression coverage only if implementation changes backend behavior.

## Out Of Scope

- No new Fee revision browser or history UI.
- No hidden inactive-row UI.
- No Matrix Editor behavior changes.
- No Fee calculation/rule changes.
- No Project Folder Required Forms readiness rule changes beyond copy updates if needed.
- No database schema migration unless a discovered implementation blocker proves it necessary.
- No StepInstance, Report, AI review, permissions, LAN/server, or multi-user scope.
- No destructive "Reset Fee Draft" UI in this task.

## Required Design Semantics

### Current Fee Pricing Payload

The saved pricing payload bound to `(project_id, confirmed_matrix_id, confirmed_revision, fee_rule_version_id)`. It is the editable current Fee Evaluation payload for the active Matrix context.

### Confirmed Fee Authority Version

The immutable authority snapshot created from the saved pricing payload. Existing backend naming may remain `ConfirmedFeeVersion` in code during this task. The user-facing action should be `Update Fee`.

### Cancel

Cancel returns to Project Workbench and must not delete the current pricing payload. If the page has unsaved or autosaved session edits, the implementation must choose the safest narrow behavior:

- If edits have not been autosaved yet, clear the pending autosave and leave.
- If edits may already have autosaved, restore the entry baseline pricing payload before leaving.
- If an in-flight autosave cannot be confirmed complete, do not leave the page. Show an actionable retry message.
- If the entry context no longer matches the current Matrix/Fee context, do not write the baseline and do not leave the page. Show an actionable refresh message. The restore write itself must also carry expected Matrix/Fee context tokens so the backend rejects a context change between pre-check and PUT.
- If restore fails, stay on the Fee Evaluation page and show an actionable error.

### Update Fee

Update Fee uses the latest saved pricing payload to create the current Confirmed Fee authority revision. It keeps the existing saved-draft id/signature guard so the authority snapshot matches the visible totals.

## Acceptance Criteria

- Clicking `Cancel` on Fee Evaluation never calls `discardFeeEvaluationPricingDraft` in the normal page flow.
- A saved current pricing payload remains available after `Cancel` and reopen.
- Local unsaved edits are not published as a Confirmed Fee authority version by `Cancel`.
- Autosave race protection is deterministic: if an in-flight autosave cannot be confirmed safe, Cancel stays on the page and does not navigate.
- Baseline restore is context-protected: an entry baseline is never written to a different active Matrix/Fee context, including context changes between pre-check and restore PUT.
- If the page has dirty edits and the operator confirms cancellation, the page returns to Workbench without clearing the Fee form.
- The primary action displays `Update Fee`; busy/success/error copy uses update language.
- `Update Fee` still creates or refreshes the Confirmed Fee authority version using the latest saved pricing draft id.
- Matrix add group/step keeps existing filled Fee rows and only adds corresponding new active rows.
- Matrix soft delete hides corresponding Fee rows while preserving hidden inactive rows in the pricing draft.
- Matrix restores the same group/step and recovers prior price, notes, spend time, and other edited values.
- Matrix real structural delete clears the Fee recovery scope for that structure.
- Existing Matrix soft-remove/reselect hidden-row recovery remains unchanged.
- Existing Confirmed Fee active-only snapshot behavior remains unchanged.
- Confirmed Fee authority snapshots still contain only active rows, not hidden inactive rows.
- Frontend tests cover Cancel no-delete behavior, autosave race protection, context-protected restore, reopen-baseline behavior, hidden inactive recovery safety, and Update Fee copy/action behavior.

## Validation Targets

- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false`
- Focused Cancel regression: open an existing pricing draft, edit notes with and without completed autosave, click Cancel, reopen Fee Evaluation, and verify the original baseline still exists.
- Focused hidden-row regression: Matrix soft-remove/reselect recovery remains intact after the Fee Evaluation Cancel changes.
- `cd frontend; npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false` if Workbench copy changes.
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or task315"`
- `py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q` if backend Confirmed Fee code changes.
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` if pricing draft persistence/API code changes.
- `cd frontend; npm run build`

## Stop Point

After this task is implemented and validated, stop. Do not add a destructive reset draft UI, Fee history UI, inactive-row UI, StepInstance, report generation, AI review, permissions, LAN/server, multi-user scope, or any later Matrix execution scope without a separate task and explicit approval.

## Completion Notes

- Fee Evaluation `Cancel` no longer calls the pricing draft DELETE API in the normal page flow.
- The page now tracks an entry baseline pricing payload and Matrix/Fee context for the current session.
- If no Fee pricing fields changed in the session, `Cancel` returns directly to Workbench without saving or deleting.
- If session edits were autosaved, `Cancel` verifies that any in-flight autosave has settled without aborting it, confirms the current server Matrix/Fee context still matches the entry context, restores the entry baseline payload with context-protected `PUT pricing-draft`, then returns to Workbench.
- If an in-flight autosave cannot be confirmed safe, or if the Matrix/Fee context changed, the page stays open and shows retry/refresh guidance.
- Pricing draft `PUT` now accepts narrow expected Matrix/Fee context tokens and rejects mismatches with a 409 before writing, preventing an entry baseline from being restored into a newer active Matrix context.
- Fee Form download errors now preserve non-Matrix 404 details, such as a missing Fee Evaluation Excel template, instead of incorrectly showing the Matrix authority blocker.
- Fee Form generation now discovers the Fee Evaluation workbook template from the configured Template folder by requiring exactly one `.xls` file whose filename contains `FDQF-E-176`, instead of hardcoding a versioned workbook filename.
- Cancel restore failure now pauses further autosave for the current dirty state so the actionable Cancel error is not overwritten by a background save failure.
- The Fee Evaluation primary authority action now displays `Update Fee`, with update-oriented busy/success/error/blocker copy, while reusing the existing backend Confirmed Fee revision API.
- Static frontend guards now prevent reintroducing `discardFeeEvaluationPricingDraft` into the Fee Evaluation page.

## Validation Summary

- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false` (`24 passed`, with existing non-failing React `act(...)` warnings)
- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false` after Fee Form download error-copy follow-up (`25 passed`, with existing non-failing React `act(...)` warnings)
- `py -m pytest tests/unit/test_config.py tests/unit/test_fee_evaluation_template_discovery.py tests/integration/test_confirmed_matrix_fee_file_download_api.py tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py -q` (`44 passed`)
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or task315"` (`9 passed, 137 deselected`)
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` (`25 passed`)
- `py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_confirmed_fee_version_service.py tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` (`61 passed`)
- `cd frontend; npm run build` passed
