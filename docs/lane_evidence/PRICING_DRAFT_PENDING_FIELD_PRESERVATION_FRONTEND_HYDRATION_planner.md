# PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION Planner Evidence

Date: 2026-07-24
Role: Planner
Status: `qa_blocked_pending_reviewer_tests_only_scope_gate`
Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`

## Current Phase / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active governance lane: Child 3 post-QA tests-only scope reconciliation.
- Reviewer passed the Child 3 plan/dependency-release re-gate.
- The User approved Developer docs-only planning-first, and Developer completed it.
- Reviewer passed implementation-readiness, the User approved product implementation,
  Developer completed the product candidate, and Reviewer passed the B2 implementation re-gate.
- QA passed the bounded Child 3, wrapper, API compatibility, and V2/currentness/CAS suites but
  reproduced `16 failed / 28 total` in the locked legacy Fee page test. This pass only reconciles
  an exact tests-only scope; it does not modify product/tests.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- Planner Discovery, controlled parallel, lane orchestration, and role registry protocols
- ConnLab Planner and lane orchestrator skills
- `$impeccable` product context, `PRODUCT.md`, `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- Child 1 and Child 2 task/plan/Planner/Developer/Reviewer/QA/Integrator evidence
- TASK_361L and TASK_363D accepted pricing-draft V2 plans/evidence and current product code
- Current pricing-draft route, persistence load states, safe rebase, Fee page orchestration, preview model, frontend API types, tests, git diff, and file line counts

## Dependency Verification

- `git merge-base --is-ancestor c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b HEAD` returned success.
- `git merge-base --is-ancestor dff635a6489f2664f7e496c424ceff8400237283 HEAD` returned success.
- HEAD is `dff635a6489f2664f7e496c424ceff8400237283`.
- Child 1 and Child 2 are therefore accepted read-only baselines and release Child 3's backend metadata/default dependency.

## Repository Findings

1. The backend pricing-draft route currently has a narrow `13/6` residual that preserves Pending Unit Price, Units, and Testing Fee as blank strings rather than `0`/`1`.
2. The bounded compatibility API test has a matching `4/4` residual.
3. The preview model residual is `23/13`; it adds metadata-aware hydration and shorter row review copy.
4. The old preview-model test residual is `114/0` in a `1389` line file, and the Fee page test residual is `1/5` in a `1718` line file. Both are package-excluded and read-only.
5. The accepted backend `field_metadata`, V2 operator provenance, and prior-default attestation already provide the required authority. No frontend rule reconstruction or API-client change is needed.
6. The current Fee page handles `rebase_required` by discarding the server-returned merged payload and rendering raw current defaults. That can lose compatible manual values, so an exact page orchestration hunk is required in the future Child 3 scope.
7. `legacy_unclassified`, `blocked`, stale lineage, fingerprint mismatch, and CAS mismatch must remain fail-closed.
8. Reviewer B1 confirmed that the locked `1389`-line preview-model test directly imports and executes `hydrateFeeEvaluationPreviewEditsFromSavedDraft` at six existing nodes. Removing that public symbol would break a locked regression boundary.

## Frozen Scope

The exact product May Touch is:

- pricing-draft route response mapper;
- preview model mechanical extraction/narrow review copy;
- new bounded hydration/load-state helper;
- exact Fee page current/rebase/CAS/Cancel branch.

The B1 compatibility contract is frozen:

- the new helper owns the hydration implementation;
- `feeEvaluationPreviewModel.ts` retains the existing public function/signature and `FeeEvaluationSavedDraftHydrationResult` through a narrow wrapper/delegation;
- runtime dependency is one-way from model to helper;
- helper-to-model references are `import type` only, so no runtime cycle exists;
- no shared type module is authorized in this scope (`0`-line effective budget);
- model compatibility code counts inside the final `<=925` budget and helper remains `<=300`.

The exact tests are:

- existing bounded compatibility API test;
- new bounded hydration test;
- new bounded Fee page pricing-draft test.

The new hydration test imports the helper directly. The old oversized model test remains unchanged and reruns these six compatibility nodes:

1. `hydrates saved pricing draft rows through stable backend identity`
2. `keeps saved manual-required LLCR price and units pending`
3. `does not let legacy placeholder saved rows overwrite refreshed defaults`
4. `keeps deliberate saved row edits even when refreshed defaults exist`
5. `hydrates saved Sample preparation rows through stable group identity`
6. `does not apply saved pricing draft rows that no longer match the preview`

Child 1/2 product, V2 backend modules, frontend API client, CSS, formulas, rule/default-fill, schema/database, seeds, Matrix/authority, workbook/export/Required Forms, real data/files, and all external residuals remain locked.

## Post-QA Tests-Only Scope

The controlling exact-node classification is:

- `docs/lane_evidence/PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION_tests_only_scope_reconciliation_planner.md`

It freezes six B2/CAS-stale nodes, ten nodes whose business assertions remain valid but whose
local fixtures lack a fresh server-validated `current_v2` context, and zero product-regression or
unrelated-residual failures. Only those sixteen node bodies may be proposed for a later
tests-only pass. The global helper, twelve passing nodes, and all product files remain locked.
The legacy file must remain at or below `1718` UTF-8 physical lines including blanks.

Tests-only implementation is not authorized. Reviewer must first confirm the exact node IDs,
root-cause classification, and line-neutral migration boundary.

## Definition Of Ready

Product DoR and implementation authorization gates are complete:

- user goal and user-visible Pending behavior are explicit;
- accepted dependencies are verified;
- state, field ownership, rebase, CAS, Cancel, and no-write contracts are frozen;
- exact May Touch, locked paths, line budgets, bounded tests, browser/build validation, rollback, and package isolation are explicit;
- no unresolved product decision is hidden in frontend inference.
- the B1 public-symbol compatibility and no-runtime-cycle contracts are explicit.

The product candidate is complete and locked. QA's legacy-suite blocker now requires a separate
Reviewer tests-only scope gate; neither the old broad test module nor the parent umbrella is an
implementation authorization.

## Verification

- Git ancestry and HEAD verified.
- Candidate numstat and blank-inclusive UTF-8 line counts recorded.
- Product/tests were not modified.
- Real data/files and generated artifacts were not accessed.
- No stage/commit/push.

## Next Role / Stop Point

Reviewer tests-only scope gate. Do not route Developer, QA, or Integrator until Reviewer approves
the exact sixteen-node tests-only boundary.
