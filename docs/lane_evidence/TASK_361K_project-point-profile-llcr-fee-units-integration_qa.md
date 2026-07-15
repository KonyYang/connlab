# TASK_361K QA Evidence

Date: 2026-07-15

Task: `TASK_361K_PROJECT_POINT_PROFILE_LLCR_FEE_UNITS_INTEGRATION`
Lane: `project-point-profile-llcr-fee-units-integration`
Role: QA / Smoke Owner
Gate result: `qa_pass`

## Scope And Environment

- Current board phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Board state for TASK_361K: Developer implementation complete, Reviewer pass, pending QA.
- QA used the repository's disposable pytest root only: `tmp/task_361k_qa_pytest`.
- No real SQLite database, project folder, public-drive path, LTR workbook, generated workbook, frontend product source, API client, Fee rule/pricing/UI, or task board was modified.

## Executed Validation

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361k_qa_pytest tests\unit\test_contact_point_profile_confirmed_consumer_adapter.py tests\unit\test_confirmed_matrix_fee_step_quantities.py tests\unit\test_fee_default_fill.py tests\unit\test_confirmed_matrix_fee_draft_service.py tests\unit\test_confirmed_matrix_fee_draft_step_quantities.py tests\unit\test_confirmed_matrix_fee_draft_profile_consumer.py tests\integration\test_confirmed_matrix_fee_draft_api.py tests\unit\test_confirmed_matrix_fee_evaluation_export_service.py tests\unit\test_fee_evaluation_export_subprocess_runner.py tests\integration\test_fee_evaluation_export_child_transaction.py tests\unit\test_matrix_fee_rebase_promotion_service.py -q
```

Actual result: `94 passed in 3.62s`.

```powershell
py -m py_compile backend/api/dependencies.py backend/application/contact_point_profile_confirmed_consumer_adapter.py backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_step_quantities.py backend/application/matrix_fee_rebase_promotion_service.py backend/application/matrix_fee_rebase_promotion_values.py backend/infrastructure/office/fee_evaluation_export_child.py backend/modules/fee_evaluation/fee_step_quantity_defaults.py
git diff --check
```

Actual result: compilation passed. `git diff --check` passed; only established working-copy LF/CRLF normalization warnings appeared. Targeted trailing-whitespace scan found no matches. Candidate module line counts were 120, 452, 204, 427, 230, 181, and 125 respectively, all below the 500-line hard limit.

## Functional Smoke Findings

- Confirmed profile fixture `P / 1-4` resolved to `readings_per_sample = 4`; with confirmed Matrix group sample quantity `5`, the LLCR line calculated `Units = 20`. The API-level assertion also passed.
- `FeeFieldMetadata.source` preserved deterministic lineage: `Confirmed Project Point Profile: revision <sequence> (<revision-id>; <fingerprint>)`.
- `not_started` and `disabled` Measurement Plan states calculated from the confirmed profile without requiring a legacy `ConfirmedMatrixStepQuantity`.
- Active-root omission and invalid group quantity stayed `review_required` with no profile or text fallback. Covered profile-state failures include draft/unconfirmed, missing, stale/corrupt, and mixed/divergent authority sources.
- Exact active Measurement Plan target precedence and no-double-count behavior remained covered; omitted, excluded, affected, or corrupt active-root states block before profile selection.
- CR specified-current and non-LLCR paths remained on their existing paths.
- The focused suite exercised the same typed adapter through Fee preview, direct export, required forms, subprocess child export, and Matrix Fee rebase composition.
- No write path was invoked by QA. Failure/review cases in the disposable fixtures produced typed review-required/no-write outcomes.

## Scope And Residual Checks

- Tracked candidate diff contained no frontend, API-client, Point Profile editor/schema/parser, LTR/project-folder module, `.agents`, or `docs/project_management` path changes.
- Diff-only real-path scan found no new `D:\Test Project`, `D:\PublicProject`, `connlab.sqlite3`, public-drive, or LTR mutation reference in TASK_361K candidate changes. Broad `backend/api/dependencies.py` retains unrelated pre-existing LTR helpers and must be hunk-isolated during packaging.
- External residuals remain excluded: `docs/task_board.md`, TASK_361F operational evidence, and TASK_361H screenshot artifacts.
- Browser smoke and frontend build are not applicable to this backend-only, disposable-authority integration lane; the 94-test suite covers the requested API/export composition paths without a real artifact or file write.

## QA Disposition

`QA gate: pass`

No blocking finding. Recommend `Integrator packaging/readiness`, staging only the reconciled TASK_361K backend/test/docs candidate and excluding the external residuals listed above.
