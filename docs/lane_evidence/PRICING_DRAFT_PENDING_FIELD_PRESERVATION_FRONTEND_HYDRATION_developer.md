# PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION Developer Evidence

Status: ready_for_reviewer_implementation_qa_re_gate / tests_only_fix_complete
Date: 2026-07-24
Role: Developer tests-only fix pass
Implementation authorization: authorized by User after Reviewer implementation-readiness pass
Task: `PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION`
Lane: `pricing-draft-pending-field-preservation-frontend-hydration`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`

## Gate

Current phase: Phase 11 controlled Matrix/Fee foundation.

This implementation is allowed because Reviewer implementation-readiness passed, the User
explicitly approved Child 3 product implementation, and Planner completed final source-of-truth
reconciliation. Work stayed within the frozen exact May Touch.

Accepted read-only dependencies:

- Child 1: `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b`
- Child 2 and current HEAD: `dff635a6489f2664f7e496c424ceff8400237283`
- Both commits are verified HEAD ancestors.

## Required Reads

Read and applied:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `tasks/PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION.md`
- `docs/pricing_draft_pending_field_preservation_frontend_hydration_plan.md`
- Child 3 Planner, dependency-release, and Reviewer evidence
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `.agents/skills/impeccable/SKILL.md`
- loaded the ConnLab product/design register through the required impeccable context command

## Read-Only Code Reconciliation

Verified actual server and frontend flow:

- pricing-draft GET returns status, saved draft id, generation, source-context fingerprint,
  payload fingerprint, updated-at, validation token, and payload;
- the route maps Pending Unit Price, Units, and Testing Fee to `""`, Unit Type to
  `"Pending"`, and preserves explicit numeric `"0"`;
- `feeEvaluationPreviewModel.ts` currently owns the stable-identity hydration implementation
  and its public compatibility result/function;
- six existing calls in the oversized model test import the public function from the model;
- the Fee page hydrates `current/current_v2`, but currently discards the server payload for
  `rebase_required` and renders raw preview defaults;
- the `missing` branch currently schedules initial seed-save after classification;
- Cancel currently has an entry payload/context path, but its restore payload omits the exact
  saved generation/payload/updated-at CAS facts.

These last three facts are implementation risks and are now frozen in the plan rather than
left implicit.

## Frozen Implementation Contract

### Hydration boundary

Implemented helper:

`frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts`

- owns stable identity, row matching, placeholder compatibility, Pending value handling, and
  hydration-only normalization;
- accepts explicit `current_v2_compatibility` and `server_rebase_candidate` modes;
- imports model types only with `import type`;
- has no runtime import from the model or API client;
- remains `<=300` UTF-8 physical lines.

Compatibility surface retained in `feeEvaluationPreviewModel.ts`:

- `FeeEvaluationSavedDraftHydrationResult`
- `hydrateFeeEvaluationPreviewEditsFromSavedDraft(previewRows, savedDraft)`

The existing function remains a two-argument wrapper for compatibility mode. The model may add
one narrow delegation for server rebase candidates. The page continues to import through the
model. Runtime direction between these modules is model to helper only.

### Exact value semantics

- `null` payload means no hydration.
- `""` is Pending/unavailable and is not `0`, `1`, or a request for browser fallback.
- `"Pending"` Unit Type remains Pending.
- `"0"` remains a real numeric value.
- empty manual text remains empty.
- `manual_required` blank Unit Price/Units remain blank.
- Testing Fee is derived by the accepted preview calculation from final visible dependencies;
  it is not independently hydrated.
- Base Fee is consumed from accepted Child 1 server value/metadata only.

### Status and write lifecycle

- loading/error: no hydration from stale state and zero-write;
- missing: render an unsaved local preview and do not schedule seed-save merely from load;
- current_v2: exact saved payload hydration;
- compatibility current: compatibility hydration only, never sufficient for a V2 consumer;
- rebase_required: render the server merged candidate, remain non-current, and suspend generic
  background autosave;
- blocked/legacy/stale: no payload hydration and no save;
- Update Fee is the explicit reviewed-rebase save boundary;
- after save, a fresh GET must prove matching `current_v2` before a production consumer runs.

### Cancel

- entry payload, entry source context, and entry CAS are immutable session baseline facts;
- untouched Cancel is zero-write;
- every page-owned successful save updates a separate latest session-owned CAS;
- post-save Cancel reloads first and restores only when server context matches entry context and
  server CAS equals the latest session-owned CAS;
- restore uses that exact CAS, then reloads and verifies `current_v2` and the entry signature;
- concurrent replacement returns typed conflict/no overwrite.

## Exact May Touch

Product:

- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts` (new)
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

Tests:

- `tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py`
- `frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts` (new)
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx`
  (new)

This implementation modified only the exact product/test candidates above plus this Developer
evidence. Existing mixed hunks in those files were preserved; no whole-file cleanup, staging, or
revert was performed.

## Locked Scope

- Child 1 and Child 2 accepted backend product/tests
- TASK_361L/TASK_363D persistence, attestation, rebase, token, CAS, and consumer guards
- `frontend/src/api/client.ts`, CSS, backend DTO contract, schema/database, seeds/manifest
- Fee formulas/rules/default fill and frontend reconstruction of those facts
- Matrix/Point Profile/Measurement Plan/LLCR/CR authority
- export/workbook/Required Forms, LTR, project lifecycle
- old oversized frontend tests except read-only execution
- all mixed dirty residuals, real DB/files, public-drive files, and generated artifacts

## Physical-Line Facts And Budgets

Final measurements use UTF-8 `ReadAllLines`, including blank lines:

- route: `319`, maximum `350`
- compatibility API test: `209`, maximum `250`
- preview model: `925`, maximum `925`
- hydration helper: `288`, maximum `300`
- Fee page: `1425`, maximum `1425`
- hydration helper test: `198`, maximum `450`
- page orchestration test: `422`, maximum `450`
- old model test: `1389`, read-only
- old page test: `1718`, read-only
- API client: `4600`, read-only

The helper owns the extracted stable identity and hydration-only behavior. The model retains the
public compatibility wrapper and the page imports only through the model, so there is no
helper-to-model runtime cycle.

## Implementation And TDD

Implemented:

- backend payload mapping preserves Pending Unit Price, Units, and Testing Fee as `""` while
  preserving explicit `"0"` and existing Unit Type behavior;
- the bounded helper implements `current_v2_compatibility` and
  `server_rebase_candidate` modes without browser-side Fee rule reconstruction;
- the model retains `hydrateFeeEvaluationPreviewEditsFromSavedDraft()` and its public result
  type, and adds one narrow server-candidate delegation;
- missing load no longer creates a seed save;
- `rebase_required` displays the server merged candidate, remains non-current, and suppresses
  generic autosave;
- Update Fee performs explicit CAS save followed by fresh GET and exact current-V2 payload
  verification before Confirm;
- Cancel is zero-write when untouched and restores only when the reloaded CAS equals the latest
  session-owned CAS, followed by current-V2/signature verification.

RED checkpoints:

- helper test initially failed because the bounded module did not exist;
- page orchestration tests initially proved candidate loss, missing-load seed-save, and unsafe
  Cancel restore behavior;
- implementation was added only after those focused failures were captured.

## Validation

Backend/API:

- `py -m pytest tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py -q`
  -> `3 passed`;
- TASK_361L/TASK_363D V2 contract, repository, persistence, rebase, prior-default
  attestation/build-safety, V2 API, Measurement Plan rebase attestation, and compatibility API
  modules -> `46 passed`;
- `py -m py_compile` for the route and compatibility API test -> passed.

Frontend:

- new bounded helper/page tests -> `8 passed`;
- six locked compatibility wrapper nodes -> `6 passed`, `23 skipped`;
- complete model plus bounded Child 3 suite -> `37 passed`;
- `npm run build` -> passed (`127` modules transformed); the existing Vite chunk-size warning
  remains informational and dependencies/package files were unchanged.

Controlled browser smoke:

- disposable mock API and Vite server only; no operator config, real DB, public-drive file, or
  generated business artifact was accessed;
- desktop `1280x720`: server rebase candidate visible, document width `1265 <= 1280`, console
  errors/warnings `0`;
- `514x831`: candidate `77`, Units `3`, and preserved manual note visible; document width
  `499 <= 514`, console errors/warnings `0`;
- the existing Fee table remains inside its established horizontal scroll container on narrow
  viewports; no CSS or layout contract was changed;
- disposable browser tab, mock API, Vite process, and temporary logs were closed/removed.

Final checks:

- exact candidate `git diff --check` -> passed; only existing LF/CRLF notices;
- UTF-8 trailing whitespace scan -> clean;
- physical line budgets -> all pass as listed above;
- runtime dependency scan -> model imports helper; helper uses only type imports from model;
- exact-scope/no-real-data scan -> no unauthorized path added by this pass;
- staged index -> empty;
- no stage, commit, or push.

## Reviewer B2 Bounded Fix

Reviewer B2 was reproduced before the fix: a `rebase_required` candidate left `Fee Form`
enabled because its disabled reason depended only on Matrix draft state.

The bounded repair changes only the existing page currentness gate and bounded page test:

- Matrix draft/lifecycle blockers retain priority;
- `Fee Form` additionally requires pricing status `current` and save state `saved`;
- every successful pricing save response first leaves the page non-current for consumers;
- only the existing explicit fresh GET verification path restores `current`;
- therefore rebase, missing, loading/error, dirty/saving, CAS-conflict, and save-before-GET states
  cannot invoke the production export client.

B2 validation:

- exact RED node failed with `Fee Form` enabled under `rebase_required`;
- exact GREEN node -> `1 passed`;
- complete bounded page suite -> `4 passed`;
- complete model/helper/page suite -> `37 passed`;
- selected TASK_361L/TASK_363D V2/API currentness regressions -> `30 passed`;
- frontend build -> passed with only the existing chunk-size warning;
- controlled browser: rebase initial `Fee Form=false`, save-before-fresh-GET `false`, fresh
  `current_v2` GET `true`; desktop and `514x831` document widths remained within viewport and
  console error/warning count was `0`;
- page/test physical lines `1425/422`, both within frozen budgets;
- exact diff/trailing/scope/no-real-data/staging checks passed.

## Package Isolation

The worktree already contains mixed tracked and untracked residuals outside Child 3. This pass
did not clean, restore, stage, or absorb them. Future Integrator work must stage exact Child 3
hunks and new files only, never whole mixed files.

## Result

Implementation blocker: none.

At the end of the original product pass, Developer status was `ready_for_review`; that historical
checkpoint was superseded by the Reviewer-authorized tests-only pass below.

## QA Legacy Tests-Only Fix

Reviewer authorized a tests-only migration in
`frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`. Product code,
shared fixtures, the twelve already-passing nodes, Child 1/2, and V2/API contracts remained
locked.

The sixteen authorized nodes now establish the state required by their original behavior:

- export and confirm paths use an attested `current_v2` snapshot with page-owned CAS facts;
- edit/save paths remain non-current until a fresh GET returns matching `current_v2`;
- `rebase_required`, missing, incomplete, failed restore, and source-context conflict paths keep
  Fee Form/confirm disabled and assert no consumer call;
- current export/download and structured-error nodes retain their original Matrix, payload, and
  lifecycle assertions under explicit fresh-current context;
- baseline restore uses the latest session-owned CAS and restores the immutable entry payload.

Validation:

- exact remaining RED selector -> `3 passed`, `25 skipped`;
- complete legacy Fee page module -> `28 passed`;
- bounded helper/model/page suites -> `37 passed`;
- six read-only compatibility-wrapper nodes -> `6 passed`, `23 skipped`;
- pricing-draft compatibility API -> `3 passed`;
- disposable TASK_361L/TASK_363D persistence, V2 contract/repository, attestation, build-safety,
  rebase, Measurement Plan, CR, and API regressions -> `45 passed`;
- `npm run build` -> passed, `127` modules transformed; only the existing Vite chunk-size warning
  remains;
- legacy test physical line count including blanks -> `1706 <= 1718`;
- exact candidate `git diff --check` and UTF-8 trailing-whitespace scan -> passed;
- staged index -> empty; no real DB, public-drive file, attachment, or generated business
  artifact was accessed.

No new browser smoke was needed for this tests-only migration. The previously audited disposable
mock-API/Vite smoke remains the product baseline: rebase and save-before-fresh-GET Fee Form
disabled, fresh `current_v2` enabled, desktop and `514x831` widths within viewport, and zero
console warnings/errors. No product, layout, CSS, or runtime hunk changed in this pass.

Implementation blocker: none.

Developer status is `ready_for_reviewer_implementation_qa_re_gate`. Next legal role is Reviewer
implementation/QA re-gate. Do not route QA or Integrator directly.
