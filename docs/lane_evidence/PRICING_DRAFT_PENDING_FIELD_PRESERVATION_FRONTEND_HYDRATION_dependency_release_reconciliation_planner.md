# PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION Dependency Release Reconciliation

Date: 2026-07-24
Role: Planner
Status: `qa_blocked_pending_reviewer_tests_only_scope_gate`
Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`

## Accepted Dependency Facts

- Child 1 accepted commit: `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b`.
- Child 2 accepted commit: `dff635a6489f2664f7e496c424ceff8400237283`.
- Both are current HEAD ancestors; HEAD is Child 2.
- Child 1 owns Base Fee precedence and metadata.
- Child 2 owns typed duration authority and dependent-field/default-fill metadata.
- TASK_361L/TASK_363D own V2 provenance, attestation, reviewed rebase, currentness, token, CAS, and consumer guards.

## Release Decision

Child 3's dependency is released. Reviewer passed the plan/dependency-release re-gate, the User
approved Developer docs-only planning-first, and Developer completed that pass. Child 3 may
consume accepted backend payloads and metadata but may not change or duplicate those contracts.

## Frozen Implementation Scope

1. Confirm the field-level Pending and manual-preservation contract.
2. Confirm that `rebase_required` must render the server merged candidate while remaining non-current.
3. Confirm exact page/model/helper hunk ownership and the exclusion of both oversized dirty test hunks. The model must retain the existing hydration public symbol/result type through a narrow delegation while the helper owns implementation.
4. Confirm no frontend API-client or backend V2 module change is needed.
5. Confirm line budgets, bounded tests, build/browser smoke, and package isolation.

## Reviewer B1 Reconciliation

- `feeEvaluationPricingDraftHydration.ts` owns the hydration implementation and remains `<=300` lines.
- `feeEvaluationPreviewModel.ts` keeps `hydrateFeeEvaluationPreviewEditsFromSavedDraft`, its existing signature, and `FeeEvaluationSavedDraftHydrationResult`; its runtime edge points to the helper.
- Helper references to model types are type-only. A helper-to-model runtime import is forbidden.
- No shared type module is authorized (`0`-line effective budget). If one becomes necessary, implementation stops for an exact-path scope re-gate.
- The model's retained compatibility import/wrapper/type count inside its final `<=925` budget.
- The existing `1389`-line test stays read-only. Its six hydration nodes retain their current import from `feeEvaluationPreviewModel.ts`; the new bounded test imports the helper directly.
- Reviewer implementation-readiness passed and the User explicitly approved product
  implementation. This authorization checkpoint is historical and superseded by Developer
  completion, Reviewer B2 pass, and the current QA tests-only scope blocker.
- The model must finish `<=925` lines including compatibility wrapper/import/result type; helper
  and bounded tests retain their frozen budgets.

## Authorization Boundary

The completed docs-only Developer planning-first pass and User product authorization are
recorded. Developer completed the product candidate and Reviewer passed the B2 implementation
re-gate. Product code is now locked.

QA passed the bounded Child 3, compatibility, and V2 suites but reproduced `16 failed / 28 total`
in the locked `1718`-line Fee page test. The exact classification and proposed line-neutral
test-only boundary are frozen in
`PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION_tests_only_scope_reconciliation_planner.md`.
Tests-only implementation is not authorized until Reviewer confirms those exact sixteen nodes.
The twelve passing nodes, global fixture behavior, and all product files remain locked.

## Next Role

Reviewer tests-only scope gate.
