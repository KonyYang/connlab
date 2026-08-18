# Pricing Draft Pending Field Preservation Frontend Hydration Plan

Status: complete / Integrator accepted pending controlled local package closeout
Date: 2026-07-24
Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`
Implementation authorization: product candidate complete and locked; tests-only migration not yet authorized

## 1. Goal

Preserve backend Pending/manual-required Fee state across pricing-draft API serialization and frontend hydration while retaining accepted V2 manual provenance, currentness, reviewed rebase, CAS, and no-write behavior.

Child 3 is a presentation and persistence-compatibility lane. It consumes accepted backend facts and cannot own Base Fee precedence, typed duration authority, Fee formulas, rule resolution, or default fill.

## 2. Dependency Release

Repository verification on 2026-07-24:

- `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` is a HEAD ancestor and is the accepted Child 1 package.
- `dff635a6489f2664f7e496c424ceff8400237283` is a HEAD ancestor and is the accepted Child 2 package.
- Current HEAD equals the Child 2 accepted commit.
- TASK_361L and TASK_363D remain the accepted pricing-draft V2 and prior-default attestation baseline.

The Child 3 backend metadata/default dependency is released. Reviewer passed the
plan/dependency-release and implementation-readiness gates. The User approved Developer
docs-only planning-first and later explicitly approved product implementation. Developer
planning-first and Planner final source-of-truth reconciliation are complete.

## 3. Source Facts

| Path | Current fact | Child 3 ownership |
|---|---:|---|
| `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py` | `319` lines, residual `13/6` | Exact response payload mapping only. |
| `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py` | `176` lines, residual `4/4` | Bounded API compatibility assertions. |
| `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts` | `1035` lines, residual `23/13` | Extract hydration implementation; retain the public compatibility entry point/result type and narrow copy hunk. |
| `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts` | `1389` lines, residual `114/0` | Read-only; six existing hydration nodes validate the unchanged compatibility entry point. |
| `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx` | `1718` lines, residual `1/5` | Read-only; migrate coverage. |
| `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx` | `1425` lines, clean | Exact current/rebase/load/Cancel wiring is required. |

The accepted backend returns `field_metadata` with `manual_required` and `auto_filled` states. The pricing-draft load result already distinguishes `missing`, `current_v2`, `rebase_required`, `legacy_unclassified`, and `blocked`. A `rebase_required` snapshot contains the server-built merge of current automatic defaults and compatible manual provenance and remains read-only until explicitly saved.

The current frontend `rebase_required` branch discards that returned payload and renders raw current preview defaults. This can lose compatible manual values. Child 3 must plan the exact page hunk that renders the server candidate while preserving its non-current status.

The current page also has two behaviors that cannot be carried forward unchanged:

- `missing` sets `needsInitialSeedSave`, so a classification-only load can later write without
  an operator edit. Child 3 freezes `missing` load as zero-write.
- Cancel restoration currently sends source context without the loaded/saved generation,
  payload fingerprint, and updated-at CAS facts. Child 3 freezes restoration to the exact
  session-owned server generation and rejects concurrent replacement.

## 4. Field Ownership

| Field | Backend authority | Child 3 behavior |
|---|---|---|
| Spend time | accepted saved/manual provenance | Preserve proven manual value; no new default. |
| Unit Price | accepted rule/default/manual metadata | Blank when manual-required; current backend automatic value otherwise; preserve proven manual value. |
| Unit Type | accepted rule/default/manual metadata | Keep `Pending` when unavailable; do not infer. |
| Units | accepted authority/default/manual metadata | Blank when manual-required; current backend automatic value otherwise; preserve proven manual value. |
| Base Fee | accepted Child 1 precedence and metadata | Consume visible backend value only; never recreate precedence. |
| Discount | accepted saved/manual provenance | Preserve; never clear from blank fallback. |
| Notes | accepted saved/manual provenance | Preserve exactly. |
| Testing Fee | backend-derived from final safe inputs | Render derived/Pending state; never hydrate as independent authority or independent blocker. |

## 5. State Machine

### Load

1. Fetch the current Confirmed Matrix Fee draft and pricing-draft load result.
2. Never write during classification.
3. Apply only the branch allowed by server status:
   - `missing`: render the current backend preview as an unsaved local view. Do not seed-save,
     set an autosave sentinel, or manufacture a saved baseline merely because load completed.
   - `current_v2`: stable-identity hydration from saved payload.
   - `rebase_required`: stable-identity hydration from server merged candidate; status remains stale/review-required.
   - compatibility `current`: hydrate only through the compatibility wrapper, but do not let a
     legacy status satisfy a V2 production-consumer gate. A server save and reload must return
     `current_v2` before Update Fee may proceed.
   - `legacy_unclassified`, `blocked`, compatibility stale: no payload hydration and no save.
4. Preserve generation, payload fingerprint, updated-at, validation token, and source-context identity for the next exact CAS operation.
5. `payload = null` means there is no server candidate. It never means "use browser defaults as
   persisted provenance".

### Hydration value semantics

- `null` payload: no hydration.
- `""`: an explicit Pending/unavailable editable value. Preserve it; do not coerce it to `0`,
  `1`, or the browser preview default.
- `"Pending"` Unit Type: preserve exactly as the unavailable state.
- `"0"`: a real numeric value and not equivalent to blank.
- empty Notes or other manual text: preserve exactly; an empty string is not an instruction to
  copy a browser default.
- `manual_required` metadata: blank Unit Price or Units remains blank.
- Testing Fee is not hydrated as independent authority. Existing preview calculation derives it
  from the final visible Unit Price, Units, Base Fee, and discount; unsafe dependencies remain
  Pending.
- Base Fee is consumed exactly from the accepted Child 1 server payload/metadata. No frontend
  branch reconstructs manual/rule-specific/automatic-zero precedence.

### Reviewed rebase

1. Server builds the candidate through accepted TASK_361L/TASK_363D rules.
2. Frontend renders the returned candidate, including compatible manual fields and refreshed automatic fields.
3. Frontend does not autosave the candidate merely because it loaded.
4. Operator visibly reviews it.
5. The existing Update Fee command is the explicit save boundary for an unchanged or locally
   reviewed candidate. Generic background autosave remains suspended while status is
   `rebase_required`.
6. Explicit save submits the visible server candidate plus allowed local manual edits with the
   returned exact CAS context.
7. The frontend performs a fresh GET after save. The save response alone is not the final
   currentness proof.
8. Server reload/revalidation must return `current_v2` with matching draft id, generation,
   payload fingerprint, validation token, source context, and canonical visible payload.
9. Only then may Confirm/Update Fee or another production consumer proceed.

### Save, reload, and Cancel

- Save and autosave use existing CAS fields and cannot send browser defaults as provenance.
- A `missing` load and a `rebase_required` load are both zero-write. Normal autosave begins only
  after an operator edit in an ordinary current/missing local session; reviewed rebase uses the
  explicit Update Fee save boundary above.
- Reload always repeats server currentness and never reuses a stale browser payload.
- Untouched Cancel is zero-write.
- At entry, retain separate immutable facts: entry payload, entry source context, and entry CAS.
  Also track the latest CAS returned by this page's own successful save as `session-owned CAS`.
- If the page has not written, Cancel discards local state and navigates with zero API writes.
- If this page already changed the saved draft, Cancel first reloads the server. Restore is
  allowed only when the reloaded source context matches the entry context and the reloaded CAS
  exactly equals the latest session-owned CAS. It then writes the immutable entry payload using
  that current CAS, reloads again, and verifies `current_v2` plus the entry canonical signature.
- Context/CAS mismatch blocks with no overwrite.
- Blocked or legacy states cannot be normalized into current by the frontend.
- Loading or request failure never writes, never reuses an older project's payload, and leaves
  Update disabled with a visible existing error/review state. Retry starts from a fresh GET.

## 6. File-Level Implementation Order

1. Add backend API assertions in `test_fee_evaluation_pricing_draft_compatibility_api.py`.
2. Add bounded `feeEvaluationPricingDraftHydration.test.ts`.
3. Add bounded `FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx`.
4. Extract stable-identity/Pending hydration and pure load interpretation into
   `feeEvaluationPricingDraftHydration.ts`. The helper accepts an explicit mode:
   `current_v2_compatibility` or `server_rebase_candidate`.
5. Mechanically move the stable identity builder and all hydration-only matching, placeholder,
   numeric/unit/discount/summary normalization into the helper. Do not leave duplicate
   normalizers in both modules.
6. Retain `hydrateFeeEvaluationPreviewEditsFromSavedDraft`, its exact two-argument signature,
   and `FeeEvaluationSavedDraftHydrationResult` in `feeEvaluationPreviewModel.ts`. That function
   delegates to `current_v2_compatibility`, so all six old call sites remain unchanged. Add only
   a narrow model-level delegation for the page's `server_rebase_candidate` mode.
7. Update only the exact payload mapping in the pricing-draft route if the API red tests prove a
   mapping gap. The currently observed Pending mapper is the baseline, not a reason for broader
   route refactoring.
8. Update only the pricing-draft load/save/reload/Cancel state hunks in the Fee page.
9. Run focused tests, accepted V2 regressions, build, and controlled browser smoke.

## 7. Exact May Touch

Product:

- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts` (new)
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

Tests:

- `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py`
- `frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts` (new)
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx` (new)

Governance:

- Child 3 task, plan, Planner/Developer/Reviewer/QA/Integrator evidence, and narrow board hunk.

## 8. Locked Paths

- Child 1 and Child 2 accepted product/test files.
- TASK_361L/TASK_363D pricing-draft persistence, contract, attestation, rebase, policy, token, repository, and consumer-guard product files.
- `frontend/src/api/client.ts`, CSS, backend DTO shape, schema/database, seeds/manifest, Fee rules/formulas/default-fill, Matrix, Point Profile, Measurement Plan, LLCR/CR authority, workbook/export/Required Forms layout, LTR, and lifecycle.
- Existing oversized frontend tests are read-only.
- Real data/files, generated artifacts, and all external dirty residuals.

## 9. Line And Package Budgets

- Route final maximum: `350`.
- Existing preview model: extract behavior and finish `<=925`; the helper import, compatibility wrapper/delegation, and retained public result type count inside this maximum.
- The current model is `1035` physical lines. Moving the approximately `107`-line hydration body
  alone is insufficient after imports/wrappers. The extraction therefore also owns the stable
  identity builder and hydration-only private helpers. The expected model result is `<=925`,
  meeting the final `925` authorization cap.
- Existing Fee page: exact hunk only, final line count must not exceed current `1425`.
- Compatibility API test final maximum: `250`.
- New hydration helper maximum: `300`.
- No shared type module is authorized; its effective budget is `0` lines. A future shared type module requires an exact-path scope re-gate and explicit line cap.
- Each new frontend test maximum: `450`.
- Existing `1389` and `1718` line tests remain read-only.
- No Python file may exceed `500`; no blank-line suppression.
- Integrator stages exact hunks, never whole mixed files.

## 10. TDD Matrix

Backend/API:

- row and manual-row Pending Unit Price/Units/Testing Fee serialize blank;
- Unit Type stays Pending;
- current automatic Base Fee remains backend-owned;
- V1/blocked/missing payload behavior remains fail-closed;
- save/reload does not generate placeholder values.

Frontend pure hydration:

- the new bounded test imports `feeEvaluationPricingDraftHydration.ts` directly and proves helper-owned implementation behavior;
- compatibility mode preserves the existing six-node public-wrapper behavior;
- server-candidate mode preserves `""`, `"Pending"`, explicit `"0"`, empty manual text, and
  server-provided manual fields without browser fallback;
- current V2 manual-required blanks remain blank;
- automatic values use current preview metadata/defaults;
- proven manual fields survive;
- old placeholder `0`/`1` cannot replace current automatic values;
- stable identity mismatch is not applied;
- single/multi-Group identity isolation;
- Testing Fee remains derived.

Page orchestration:

- reviewed-rebase candidate is rendered with manual preservation and automatic refresh;
- missing/current/rebase/blocked load and reload do not write;
- `missing` does not schedule seed-save;
- rebase candidate load does not trigger background autosave;
- Update remains blocked until explicit save followed by GET returns matching `current_v2`;
- legacy/blocked/stale states do not hydrate or autosave;
- CAS conflict leaves the server state unchanged;
- untouched Cancel is zero-write;
- post-autosave Cancel restores the immutable entry payload only when reloaded CAS equals the
  latest session-owned CAS;
- concurrent replacement before Cancel produces conflict/no overwrite;
- reload reclassifies against the server.

Regression:

- accepted TASK_361L/TASK_363D currentness, attestation, safe rebase, and consumer-guard suites;
- accepted Child 1/2 focused suites read-only;
- old oversized frontend tests read-only;
- the six existing hydration nodes in `feeEvaluationPreviewModel.test.ts` continue to import the public function from `feeEvaluationPreviewModel.ts` and run without edits:
  - `hydrates saved pricing draft rows through stable backend identity`
  - `keeps saved manual-required LLCR price and units pending`
  - `does not let legacy placeholder saved rows overwrite refreshed defaults`
  - `keeps deliberate saved row edits even when refreshed defaults exist`
  - `hydrates saved Sample preparation rows through stable group identity`
  - `does not apply saved pricing draft rows that no longer match the preview`
- frontend build;
- desktop and `514x831` controlled browser smoke with no overflow, overlap, or console errors.

Read-only six-node command:

`npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts -t "hydrates saved pricing draft rows through stable backend identity|keeps saved manual-required LLCR price and units pending|does not let legacy placeholder saved rows overwrite refreshed defaults|keeps deliberate saved row edits even when refreshed defaults exist|hydrates saved Sample preparation rows through stable group identity|does not apply saved pricing draft rows that no longer match the preview"`

## 10.1 Compatibility And Dependency Direction

- `feeEvaluationPricingDraftHydration.ts` owns the hydration implementation.
- `feeEvaluationPreviewModel.ts` runtime-imports the helper implementation and exposes the
  existing public wrapper/delegation plus one narrow server-candidate delegation.
- The helper may reference model-owned row/edit/result types only through `import type`; type-only edges erase at runtime.
- The helper must not runtime-import the model, and no helper-model runtime cycle is allowed.
- The page continues to runtime-import from the model; it does not bypass the model by importing
  the helper directly. The only model/helper runtime edge is model to helper.
- `FeeEvaluationSavedDraftHydrationResult` remains publicly available from `feeEvaluationPreviewModel.ts`.
- No shared type module is planned or authorized. If type-only imports prove insufficient, implementation stops for Planner/Reviewer re-scope instead of creating one implicitly.

## 11. Rollback

The implementation package is code-only and additive except narrow mapper/wiring hunks. Rollback removes the new bounded modules and restores the exact route/model/page hunks. It does not rewrite saved V2 drafts, accepted metadata, or real data. Legacy and non-current records remain fail-closed under accepted server rules.

## 11.1 QA Legacy Test Scope Reconciliation

The bounded Child 3 contract passed, but the locked `1718`-line
`FeeEvaluationReviewExportPage.test.tsx` reproduced `16 failed / 28 total`.

Proposed tests-only scope is limited to the sixteen exact nodes at lines `247`, `388`, `432`,
`491`, `578`, `633`, `718`, `774`, `878`, `968`, `1018`, `1094`, `1134`, `1147`, `1180`, and
`1201`. Six nodes contain stale B2/CAS assertions or fixtures; ten retain valid business
assertions but lack explicit per-node fresh-current-V2 context. Exact titles, roots, and
migrations are frozen in the tests-only scope reconciliation evidence.

No product change is allowed. The legacy file must remain `<=1718` lines, passing nodes remain
untouched, and `arrangeSuccessfulContext()` cannot be globally changed to force all nodes
current. New coverage that cannot fit line-neutrally belongs in the existing bounded Child 3
page test.

## 12. Stop Point

Developer product implementation and Reviewer B2 re-gate are complete. QA is blocked only by
the proposed exact-node migration in the locked legacy test. Route only Reviewer tests-only
scope gate; do not route Developer, QA, or Integrator before approval.
