# PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION

Status: complete / Integrator accepted pending controlled local package closeout
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`
Implementation authorization: product and Reviewer-authorized tests-only migration complete; QA passed
Developer planning-first authorization: approved and complete
Date: 2026-07-24

## Current Phase And Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: this Child 3 lane, QA blocked / pending Reviewer tests-only scope gate.
- Why allowed: Developer completed the authorized product candidate and Reviewer passed the B2 implementation re-gate. QA found sixteen failures only in a locked legacy test file, so Planner may reconcile an exact tests-only scope without modifying product/tests.

## Accepted Dependencies

- Child 1, `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY`, is complete/accepted at `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b`.
- Child 2, `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`, is complete/accepted at `dff635a6489f2664f7e496c424ceff8400237283`.
- Both commits are ancestors of the current HEAD; current HEAD is the Child 2 accepted commit.
- TASK_361L and TASK_363D remain the accepted V2 pricing-draft envelope, provenance, automatic-default attestation, reviewed-rebase, currentness, token, CAS, and no-write authority.

Child 1 and Child 2 are read-only dependencies. Their rule resolution, Base Fee precedence, typed duration authority, default-fill behavior, metadata, and Fee calculations must not be recreated or changed by Child 3.

## Purpose

Preserve backend Pending/manual-required Fee fields across pricing-draft save, load, reload, reviewed rebase, and frontend hydration. The UI must display accepted backend automatic defaults and review-required state without replacing Pending values with empty-cache defaults, `0`, `1`, or stale saved values.

## Frozen Field Contract

### Backend ownership

- The accepted backend Fee draft and its `field_metadata` are authoritative for automatic values, `manual_required`, `auto_filled`, review reasons, and derived Testing Fee.
- Child 3 consumes Child 1 Base Fee metadata and Child 2 dependent-field metadata. It must not infer Base Fee precedence, duration authority, Units, Unit Price, or Testing Fee in the frontend.
- Manual Unit Price, Units, Base Fee, discount, notes, and spend time remain protected by accepted V2 operator provenance.
- Testing Fee is derived from the final safe Unit Price, Units, Base Fee, and discount. It is not an independently editable or independently blocking frontend field.

### Pending serialization

- A saved Pending or blank Unit Price, Units, or Testing Fee is returned as an empty editable string, never a generated `0` or `1`.
- Unit Type remains `Pending` when the backend has no safe value.
- Base Fee uses accepted Child 1 semantics. A saved blank cannot cause the frontend to recompute precedence. The current backend preview and `field_metadata` decide whether the visible value is a proven manual value, a rule-specific value, the automatic fallback `0`, or a manual-required blank.
- Historical V1 placeholders and stale saved `0`/`1` values cannot overwrite refreshed accepted backend automatic defaults.

### Frontend hydration

- For `current_v2`, hydrate only matching stable row identities. Preserve proven saved manual fields; keep backend-manual-required blank fields blank; use current backend automatic values when metadata marks the field automatic.
- Unmatched rows are not applied and produce a visible stale/review state.
- Empty strings and browser/local defaults are not evidence of operator provenance.
- The frontend must never reconstruct Child 1 or Child 2 business rules.

## Pricing-Draft State Contract

- `missing`: show current backend defaults; the existing initial-seed flow may save only through the accepted server path.
- `current_v2`: hydrate the server payload by stable row identity and retain the returned generation, payload fingerprint, validation token, updated-at value, and source-context fingerprint.
- `rebase_required`: the server payload is the read-only reviewed-rebase candidate already merged from current automatic defaults and compatible manual provenance. Render that candidate for visible review, keep the page non-current, and require an explicit save followed by server reload/revalidation to `current_v2` before Update Fee or any consumer.
- `legacy_unclassified`, `blocked`, and compatibility `stale`: do not hydrate or save the non-current payload; show current backend defaults with a typed blocking state.
- Only server-validated `current_v2` is consumable by Update Fee, exports, Required Forms, or rebase consumers. The pre-V2 `current` compatibility status may remain readable only under the existing accepted compatibility boundary; Child 3 cannot widen it.

Load and classification are zero-write. A no-edit Cancel is zero-write. If this page already autosaved operator edits, Cancel may only restore the exact entry snapshot through the accepted CAS path and read-verify it; context or CAS mismatch is typed conflict/no-write and cannot blind-overwrite newer state. Reload repeats server classification and cannot reuse a stale browser cache.

## Exact Future May Touch

Product paths:

1. `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
   - Exact payload-response mapping only.
   - Preserve Pending Unit Price, Units, and Testing Fee without generated placeholders.
   - No persistence, status classification, V2 policy, or formula changes.
2. `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
   - Mechanical removal of the pricing-draft hydration implementation into the bounded module below.
   - Retain the existing public `hydrateFeeEvaluationPreviewEditsFromSavedDraft` symbol, its existing signature, and `FeeEvaluationSavedDraftHydrationResult` type as a compatibility entry point.
   - The compatibility entry point must be a narrow wrapper/delegation to the helper implementation. Existing callers and the six locked regression nodes must not change imports.
   - Narrow blocker-copy adjustment only; no Fee business-rule ownership.
3. `frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts` (new, bounded)
   - Own the stable-identity hydration implementation, metadata-aware Pending handling, and pure current/rebase load interpretation.
   - It may import model types only with `import type`. It must not runtime-import `feeEvaluationPreviewModel.ts`.
   - Any stable-identity implementation moved with hydration is called by the model through a one-way runtime dependency from model to helper; helper-to-model remains type-only.
4. `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
   - Exact pricing-draft load/rebase/CAS/Cancel wiring only.
   - Render the server-provided reviewed-rebase candidate without making it current or autosaving before visible review.

Test paths:

5. `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py`
   - Bounded API serialization and compatibility assertions only.
6. `frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts` (new, bounded)
   - Pure current/rebase/Pending/manual/identity hydration matrix.
7. `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx` (new, bounded)
   - Page wiring for reviewed rebase, CAS save/reload, blocked states, and Cancel.

Governance docs for this lane may also be updated.

## Existing Mixed Residual Ownership

- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`: current residual `13/6`, Child 3 candidate only at the payload mapper hunk.
- `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py`: current residual `4/4`, Child 3 bounded test candidate.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`: current residual `23/13`; only Pending hydration and row-review copy are candidate behavior, and hydration must be extracted to the bounded module.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`: current residual `114/0`, excluded from the package and read-only. Its six existing hydration nodes remain unchanged and validate the compatibility entry point; new helper-level coverage belongs in the bounded new test.
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`: current residual `1/5`, excluded from the package. Migrate relevant coverage to the new bounded page test.
- `FeeEvaluationReviewExportPage.tsx` is clean relative to HEAD but requires a future exact orchestration hunk because the current `rebase_required` branch does not apply the server-returned merged candidate.

Whole-file staging of any mixed path is forbidden.

## Line Budgets

Blank-inclusive UTF-8 source facts:

- pricing-draft route: `319` lines; final maximum `350`.
- preview model: `1035` lines; accepted oversized legacy module. Child 3 must extract hydration behavior and finish at or below `925`, with no unrelated cleanup.
- Fee page: `1425` lines; accepted oversized legacy page. Child 3 may only replace the exact pricing-draft orchestration branch and must not increase the final line count.
- compatibility API test: `176` lines; final maximum `250`.
- old preview-model test: `1389` lines, read-only regression execution.
- old Fee page test: `1718` lines, read-only regression execution.
- new hydration product helper: maximum `300` lines.
- no shared type module is authorized in this scope; its effective line budget is `0`. If a later implementation proves a shared type module necessary, Planner/Reviewer must re-gate an exact path and explicit maximum before use.
- preview-model imports, compatibility wrapper/delegation, and retained public result type all count within the final `<=925` model maximum.
- each new frontend test module: maximum `450` lines.

No blank-line suppression is allowed. Python files remain below the project hard limit of `500`.

## Must Not Touch

- Child 1 or Child 2 accepted source, including Base Fee policy, rule resolution, typed duration authority, default-fill, Fee composition, Matrix source/draft/confirmed authority, and their tests.
- TASK_361L/TASK_363D V2 contract, attestation, persistence, rebase policy, consumer guards, token, CAS, and repository modules.
- `frontend/src/api/client.ts`, CSS, Fee formulas, seeds/manifest, API DTO shape, schema/database, workbook/export layout, Required Forms layout, Matrix, Point Profile, Measurement Plan, LLCR/CR authority, LTR, and project lifecycle.
- Existing oversized frontend tests except the sixteen exact
  `FeeEvaluationReviewExportPage.test.tsx` nodes proposed below. That proposal remains locked
  until Reviewer tests-only scope approval.
- Real DB/files, generated artifacts, external dirty residuals, stage/commit/push.

## Acceptance Criteria

1. Pending Unit Price, Units, and Testing Fee round-trip as blank editable values, not `0`/`1`.
2. Current backend automatic values, including accepted Base Fee fallback and typed-duration defaults, are not overwritten by stale placeholders.
3. Proven manual Unit Price, Units, Base Fee, discount, notes, and spend time survive current reload and safe reviewed rebase.
4. `rebase_required` visibly renders the server candidate, remains non-current, performs no load-time write, and cannot Update Fee until explicit save returns `current_v2`.
5. `legacy_unclassified`, `blocked`, stale context, invalid token/fingerprint, CAS conflict, and unmatched identity fail closed with no silent hydration or write.
6. Missing/manual-required fields remain visibly Pending and review-required. Testing Fee stays derived and Pending when dependencies are unsafe.
7. Autosave, reload, Update Fee, and Cancel retain accepted CAS/currentness behavior; untouched Cancel is zero-write and a post-autosave restore cannot overwrite a newer server draft.
8. Single- and multi-Group rows hydrate only their own stable identities.
9. Focused backend API tests, bounded frontend tests, read-only accepted V2 regressions, and `npm run build` pass.
10. Controlled desktop and `514x831` browser smoke show Pending/review copy without overflow, overlap, console errors, or visual redesign.
11. No real data/file mutation and no package contamination occurs.

## Proposed Tests-Only Scope After QA

Product code is locked. The only proposed tests-only May Touch is
`frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`, limited to these
sixteen exact node starts:

- line 247 `sends current edited preview values to the Fee Form download`
- line 388 `seeds a missing pricing draft from defaults and confirms without an extra save`
- line 432 `confirms Fee Evaluation with the latest autosaved draft id without saving again`
- line 491 `saves a reviewed rebase candidate before updating Fee`
- line 578 `blocks Update Fee at the incomplete Report preparation row without duplicate alerts`
- line 633 `loads a promoted current pricing draft and allows Update Fee when authority is missing`
- line 718 `normalizes pending numeric values from promoted pricing draft before confirming`
- line 774 `allows Update Fee refresh when confirmed fee is stale and promoted draft is current`
- line 878 `does not confirm when autosave succeeds without a pricing draft id`
- line 968 `restores the entry baseline before leaving when autosave already saved edits`
- line 1018 `stays on Fee Evaluation when baseline restore fails`
- line 1094 `stays on Fee Evaluation when the Matrix or fee context changed before restore`
- line 1134 `keeps the Fee file action enabled when the project folder path is missing`
- line 1147 `downloads the generated Fee file through the direct download endpoint`
- line 1180 `shows timeout cleanup guidance from structured API detail`
- line 1201 `shows the template-missing download error instead of a Matrix blocker`

The six direct stale B2/CAS nodes and ten per-node current-V2 fixture migrations are frozen in
`docs/lane_evidence/PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION_tests_only_scope_reconciliation_planner.md`.
No global fixture change, whole-file authorization, passing-node change, production-gate
weakening, or file growth above `1718` lines is permitted.

### Locked compatibility regressions

The following six existing nodes in `feeEvaluationPreviewModel.test.ts` are read-only and must continue to import and call `hydrateFeeEvaluationPreviewEditsFromSavedDraft` from `feeEvaluationPreviewModel.ts`:

1. `hydrates saved pricing draft rows through stable backend identity`
2. `keeps saved manual-required LLCR price and units pending`
3. `does not let legacy placeholder saved rows overwrite refreshed defaults`
4. `keeps deliberate saved row edits even when refreshed defaults exist`
5. `hydrates saved Sample preparation rows through stable group identity`
6. `does not apply saved pricing draft rows that no longer match the preview`

Read-only regression command:

`npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts -t "hydrates saved pricing draft rows through stable backend identity|keeps saved manual-required LLCR price and units pending|does not let legacy placeholder saved rows overwrite refreshed defaults|keeps deliberate saved row edits even when refreshed defaults exist|hydrates saved Sample preparation rows through stable group identity|does not apply saved pricing draft rows that no longer match the preview"`

The new bounded hydration test imports the helper directly and verifies implementation behavior. It does not replace or rewrite the six compatibility regressions.

## Validation Gate

- Reviewer plan/dependency-release, implementation-readiness, and B2 implementation re-gates:
  passed.
- Developer product implementation: complete and product code locked.
- QA bounded suites: passed; legacy page suite: `16 failed / 28 total`.
- Next gate: Reviewer tests-only scope gate. Tests-only implementation is not yet authorized.
- QA must use disposable API data and a controlled browser environment.
- Integrator must stage only the exact approved hunks and new bounded modules.

## Stop Point

Route only Reviewer tests-only scope gate. Do not route Developer, QA, or Integrator until the
sixteen-node boundary is approved.
