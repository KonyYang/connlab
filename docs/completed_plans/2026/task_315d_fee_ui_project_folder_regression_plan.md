# TASK_315D Fee UI + Project Folder Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure Fee Evaluation and Project Folder behave correctly after TASK_315C promotes Matrix-to-Fee rebase output into the current Fee pricing draft.

**Architecture:** Keep TASK_315D as a frontend/UI plus regression slice. Fee Evaluation should consume existing pricing draft and Confirmed Fee APIs, while Project Folder selectors must continue to treat only current Confirmed Fee authority as readiness, not promoted pricing drafts. Backend changes are allowed only for a narrow proven linkage gap discovered by the regression tests.

**Tech Stack:** React + TypeScript, Vitest, pytest static guards, FastAPI/pytest only if backend linkage is touched.

---

## Anti-Skip Statement

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task for this plan: `TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION`.

Why this task is allowed to plan now:

- TASK_315A rebase core is complete.
- TASK_315B pending storage/autosave/cancel lifecycle is complete.
- TASK_315C Matrix Confirm promotion is complete, including saved Matrix draft signature validation.
- TASK_315D is listed by the board as the future Fee Evaluation UI plus Project Folder regression slice.

Implementation was approved explicitly by the user after this plan was reviewed.

Implementation status:

```text
Complete after explicit user approval on 2026-06-15.
```

## Current Code Reality

Relevant existing files:

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
  - loads Confirmed Matrix Fee draft;
  - loads pricing draft via `getFeeEvaluationPricingDraft(projectId)`;
  - tracks `pricingDraftLoadStatus`, `latestSavedPricingDraftId`, `savedLocalPricingSignature`, `baselinePricingSignature`, `hasUserEditedPricingDraft`, and autosave/discard state;
  - disables Confirm Fee through `confirmFeeBlocker(...)`.
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
  - existing Fee Evaluation frontend tests.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
  - hydrates saved pricing draft values into the preview model and builds export payload/signature inputs.
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - derives Project Folder task rows;
  - already blocks Required forms when `matrixAuthorityReady` is false or `confirmedFeeAuthorityStatus !== "confirmed"`.
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - selector regression target.
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - task detail/action UI.
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
  - task-list UI regression target.
- `frontend/src/api/client.ts`
  - typed Fee Evaluation pricing draft, Confirmed Fee, Matrix Editor session confirm, and Project Folder API client boundary.
- `tests/unit/test_frontend_shell_files.py`
  - static guard target when API wiring/copy needs protection.

Physical UI scene: lab coordinator on a Windows workstation reviewing a Matrix revision and deciding whether the carried-forward Fee values are safe to confirm. The UI should be calm, dense, status-first, and not decorative.

## Scope Boundaries

In scope:

- Fee Evaluation presentation and state handling for TASK_315C promoted current pricing drafts.
- Confirm Fee gating tests around promoted draft ids/signatures.
- Project Folder selector/UI regression proving Required forms depend on current Confirmed Fee authority.
- Minimal operator-facing copy where existing text misleads after promotion.

Out of scope:

- Matrix rebase algorithm changes.
- Pending rebase storage or autosave lifecycle changes.
- Matrix Confirm promotion backend changes unless a test proves an existing API contract bug.
- Automatic Confirm Fee.
- Inactive removed-row editing/display.
- Fee calculation/rule changes.
- Required forms generation semantics.
- ProjectOutputRecord schema/API changes.
- StepInstance, report generation, evidence/image, AI, permissions, LAN/server, multi-user work.

Hard stop rule: if a fix must touch files outside the narrow Fee UI, Project Folder selector/UI, API DTO typing, or directly related tests, stop and create a follow-up task.

## Data And State Contract

TASK_315D should not introduce new backend DTOs unless unavoidable.

Use existing API contracts:

```ts
type FeeEvaluationPricingDraftStatus = "missing" | "current" | "stale";

type FeeEvaluationPricingDraftResponse = {
  status: FeeEvaluationPricingDraftStatus;
  current_confirmed_matrix_id: string;
  current_confirmed_revision: number;
  current_fee_rule_version_id: string;
  saved_confirmed_matrix_id?: string | null;
  saved_confirmed_revision?: number | null;
  saved_fee_rule_version_id?: string | null;
  saved_draft_edit_id?: string | null;
  payload?: FeeEvaluationEditedFileExportRequest | null;
};

type ConfirmedFeeStatus = "missing" | "current" | "stale";
```

Expected UI interpretation:

- `pricingDraft.status === "current"` with `saved_draft_edit_id` means the visible draft can be loaded as the current saved pricing basis, including drafts promoted by TASK_315C.
- `pricingDraft.status === "missing"` means Fee Evaluation may seed defaults through the existing TASK_314B controlled seed path.
- `pricingDraft.status === "stale"` means the saved pricing draft must not be confirmed for the active Matrix.
- `confirmedFee.status !== "current"` means Project Folder controlled Fee outputs are not authority-ready.

No Project Folder state may infer Confirmed Fee authority from `FeeEvaluationPricingDraftResponse`.

## Task 0: Baseline Verification

**Files:**

- Read only: existing test files listed below.
- Read only: `PRODUCT.md`
- Read only: `DESIGN.md`
- Read only: `docs/02_ARCHITECTURE_RULES.md`
- Read only: `docs/frontend_architecture_rules.md`

- [ ] **Step 1: Load frontend/UI rules context**

Before implementation, load `$impeccable` context and read the project frontend rules:

```powershell
node .agents/skills/impeccable/scripts/load-context.mjs
```

```powershell
Get-Content docs/02_ARCHITECTURE_RULES.md -Encoding UTF8
Get-Content docs/frontend_architecture_rules.md -Encoding UTF8
```

Expected:

- ConnLab is treated as `$impeccable` `register: product`;
- Fee UI and Project Folder changes keep restrained product UI, business-readable copy, centralized API access through `frontend/src/api/client.ts`, and feature-level selector/component boundaries.

- [ ] **Step 2: Run Matrix/Fee backend baseline**

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

Expected: existing tests pass before TASK_315D changes.

- [ ] **Step 3: Run Fee UI baseline**

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: existing Fee Evaluation tests pass or any existing unrelated warnings are recorded before changes.

- [ ] **Step 4: Run Project Folder selector/UI baseline**

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
```

Expected: existing Project Folder tests pass or existing failures are recorded before changes.

## Task 1: Fee Evaluation Promoted Draft Load Regression

**Files:**

- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- Modify only if failing test proves needed: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Modify only if helper coverage is cleaner: `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`

- [ ] **Step 1: Add a failing test for current promoted pricing draft hydration**

Add a test that mocks:

- `fetchConfirmedMatrixFeeDraft(projectId)` returning a current Fee Evaluation draft for active Matrix `cmv-new`, revision `2`;
- `getFeeEvaluationPricingDraft(projectId)` returning `status: "current"`, `saved_draft_edit_id: "pricing-promoted"`, `current_confirmed_matrix_id: "cmv-new"`, `current_confirmed_revision: 2`, and a payload containing a distinctive promoted row note/value;
- `getConfirmedFeeLatest(projectId)` returning `status: "missing"`.

Assert:

- promoted payload values appear in the editable Fee table;
- the missing-draft seed path is not shown as the primary state;
- Confirmed Fee `missing` or `stale` guidance is visible as review/confirm guidance;
- Confirm Fee is not disabled solely because Confirmed Fee is `missing` or `stale`;
- Confirm Fee remains disabled only if another blocker is present: loading/error status, pricing draft missing/stale, dirty/autosave pending, missing saved draft id, signature mismatch, discard in progress, or empty `confirmed_by`;
- user-facing copy does not expose `promoted`, `fee_rebase`, `payload_signature`, or route names.

Representative assertion shape:

```ts
expect(await screen.findByDisplayValue("promoted pricing note")).toBeTruthy();
expect(screen.queryByText(/Save pricing draft before confirming Fee/i)).toBeNull();
expect(screen.getByText(/Not confirmed/i)).toBeTruthy();
expect(screen.getByRole("button", { name: "Confirm Fee" })).not.toBeDisabled();
expect(screen.queryByText(/fee_rebase|payload_signature|\/api\//i)).toBeNull();
```

- [ ] **Step 2: Run the focused test and verify it fails if current behavior is incomplete**

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: fail only if Fee UI does not correctly hydrate/display current promoted draft. If it passes without production changes, keep the test as regression coverage and do not change production UI.

- [ ] **Step 3: Implement the smallest Fee UI fix if needed**

Allowed fixes:

- adjust load-state assignment for `status === "current"`;
- preserve returned `saved_draft_edit_id` and signature after hydration;
- adjust operator copy around missing/stale Confirmed Fee so it says review and confirm Fee for the active Matrix;
- avoid any backend term in user-facing strings.

Forbidden fixes:

- adding new backend DTO fields for "promoted";
- auto-confirming Fee;
- bypassing saved signature gating.

- [ ] **Step 4: Re-run Fee UI test**

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: pass.

## Task 2: Confirm Fee Gating Regression For Promoted Draft

**Files:**

- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- Modify only if necessary: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

- [ ] **Step 1: Add a failing test for Confirm Fee enabled only after current saved draft signature matches**

Mock a current promoted pricing draft and a `missing` or `stale` Confirmed Fee state. Confirmed Fee status is available in both cases and must not by itself block Confirm Fee. Simulate an operator editing a pricing value.

Assert:

- with no local dirty state and a matching saved draft id/signature, Confirm Fee can be submitted when Confirmed Fee is `missing` or `stale`;
- local edit changes the status to unconfirmed/dirty;
- Confirm Fee is disabled while autosave is pending or saved signature is behind;
- after autosave resolves with `saved_draft_edit_id: "pricing-promoted-updated"` and matching current context, Confirm Fee can be submitted;
- Confirm Fee request uses `expected_pricing_draft_edit_id: "pricing-promoted-updated"`.

Representative assertion shape:

```ts
await user.clear(screen.getByLabelText(/Unit price/i));
await user.type(screen.getByLabelText(/Unit price/i), "88");
expect(screen.getByRole("button", { name: "Confirm Fee" })).toBeDisabled();

await waitFor(() => {
  expect(screen.getByRole("button", { name: "Confirm Fee" })).not.toBeDisabled();
});

await user.click(screen.getByRole("button", { name: "Confirm Fee" }));
expect(confirmFeeVersion).toHaveBeenCalledWith(
  "project-1",
  expect.objectContaining({
    expected_pricing_draft_edit_id: "pricing-promoted-updated",
  })
);
```

- [ ] **Step 2: Run focused test**

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: fail only if promoted draft id/signature handling is incomplete.

- [ ] **Step 3: Implement smallest gating fix if needed**

Allowed fixes:

- update saved id/signature from autosave response consistently;
- ensure current context is taken from pricing draft response;
- keep Confirm Fee blocker reasons business-readable.

Forbidden fixes:

- implicit save inside Confirm Fee;
- removing dirty/signature gates;
- treating `missing` or `stale` Confirmed Fee status as a standalone Confirm Fee blocker;
- backend Confirm Fee schema changes.

- [ ] **Step 4: Re-run focused test**

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: pass.

## Task 3: Project Folder Required Forms Regression

**Files:**

- Modify: `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- Modify only if failing test proves needed: `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- Modify if detail UI copy needs regression: `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` or the nearest existing Workbench test covering Confirmed Fee status mapping
- Modify only if failing test proves needed: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

- [ ] **Step 1: Add selector tests for promoted pricing draft not counting as authority**

Add or strengthen tests for `deriveProjectFolderTasks(...)`:

Case A:

- `matrixAuthorityReady: true`
- `confirmedFeeAuthorityStatus: "missing"`
- `requiredFormsPreview.status: "ready"` or `"current"`

Expected:

- `confirmed_fee_authority` is `blocked`;
- `required_forms` is `blocked`;
- Required forms action target is not `required_forms_generate`.

Case B:

- same, but `confirmedFeeAuthorityStatus: "stale"`

Expected:

- `confirmed_fee_authority` is `blocked`;
- `required_forms` is `blocked`.

Case C:

- `confirmedFeeAuthorityStatus: "confirmed"`
- `requiredFormsPreview.status: "ready"`

Expected:

- `confirmed_fee_authority` is `ready`;
- `required_forms` is `warning` with action target `required_forms_generate`.

- [ ] **Step 2: Run selector tests**

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors --watch=false
```

Expected: pass if TASK_314C selector guard already fully covers this. If not, fail on Required forms being incorrectly ready.

- [ ] **Step 3: Implement narrow selector fix if needed**

Allowed fix:

```ts
if (input.confirmedFeeAuthorityStatus !== "confirmed") {
  return baseTask("required_forms", "Required forms", "Blocked", "blocked", {
    summary: "Confirm Fee authority before generating Required forms.",
    detailKind: "required_forms",
    blockers: ["Current Confirmed Fee authority is required before Required forms."],
    warnings,
  });
}
```

Do not change Required forms generation API or ProjectOutputRecord behavior.

- [ ] **Step 4: Run selector and task-list UI tests**

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
```

Expected: pass.

- [ ] **Step 5: Add Workbench mapping regression for Confirmed Fee latest status**

Add a lightweight Workbench/Layout or mapping regression around the layer that converts `ConfirmedFeeLatestResponse.status` into Project Folder `confirmedFeeAuthorityStatus`.

Mock `getConfirmedFeeLatest(projectId)` responses:

```ts
{ status: "missing", current_confirmed_matrix_id: "cmv-new", current_confirmed_revision: 2, current_fee_rule_version_id: "fee-rules-v1", confirmed_fee: null }
{ status: "stale", current_confirmed_matrix_id: "cmv-new", current_confirmed_revision: 2, current_fee_rule_version_id: "fee-rules-v1", confirmed_fee: staleConfirmedFee }
{ status: "current", current_confirmed_matrix_id: "cmv-new", current_confirmed_revision: 2, current_fee_rule_version_id: "fee-rules-v1", confirmed_fee: currentConfirmedFee }
```

Expected UI task behavior:

- `missing` maps to Project Folder `Confirmed Fee authority` blocked and `Required forms` blocked;
- `stale` maps to Project Folder `Confirmed Fee authority` blocked and `Required forms` blocked;
- `current` maps to Project Folder `Confirmed Fee authority` ready, and Required forms follows the existing Required forms preview state.

If the existing Workbench tests are too broad for this exact assertion, extract a small pure selector/helper for status mapping only within the project-workbench feature boundary and test that helper. Do not move API calls out of `frontend/src/api/client.ts`.

- [ ] **Step 6: Run Workbench mapping regression**

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList --watch=false
```

Expected: pass.

## Task 4: Static Guards And Copy Hygiene

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`
- Modify only if needed: frontend files from previous tasks.

- [ ] **Step 1: Add static guards for TASK_315D copy and boundaries**

Add a narrow test that reads Fee Evaluation and Project Folder frontend files and asserts:

- no user-facing strings expose `fee_rebase`, `payload_signature`, or route paths;
- Project Folder selector still gates Required forms on `confirmedFeeAuthorityStatus !== "confirmed"`;
- Fee Evaluation still calls `getFeeEvaluationPricingDraft`, `saveFeeEvaluationPricingDraft`, and `confirmFeeVersion` through `frontend/src/api/client.ts`.

Representative pytest shape:

```python
def test_task315d_fee_ui_project_folder_regression_wiring_is_present() -> None:
    fee_page = Path("frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx").read_text(encoding="utf-8")
    selector = Path("frontend/src/features/project-workbench/projectFolderTaskSelectors.ts").read_text(encoding="utf-8")
    assert "getFeeEvaluationPricingDraft" in fee_page
    assert "saveFeeEvaluationPricingDraft" in fee_page
    assert "confirmFeeVersion" in fee_page
    assert 'confirmedFeeAuthorityStatus !== "confirmed"' in selector
    assert "fee_rebase" not in fee_page
    assert "payload_signature" not in fee_page
```

- [x] **Step 2: Run static guard**

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

Expected: pass, except unrelated pre-existing deselected tests must not be used as blockers.

## Task 5: Final Validation And Board Sync

**Files:**

- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`
- Modify: `tasks/TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION.md`
- Modify: `docs/task_315d_fee_ui_project_folder_regression_plan.md`

- [x] **Step 1: Run required validation**

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

Expected: pass.

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: pass.

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
```

Expected: pass.

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

Expected: pass or record unrelated pre-existing failures.

```powershell
cd frontend
npm run build
```

Expected: pass.

- [x] **Step 2: Run backend Fee tests if backend linkage was touched**

Only if backend production files changed:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Expected: pass.

- [x] **Step 3: Update completion notes**

Update:

- `tasks/TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION.md`
- `docs/task_315d_fee_ui_project_folder_regression_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

Completion notes must say:

- what UI/regression behavior was implemented;
- validation commands and results;
- TASK_315 umbrella is complete only if TASK_315D is fully validated;
- no next task is authorized automatically.

- [x] **Step 4: Run diff hygiene**

```powershell
git diff --check
```

Expected: no whitespace errors. CRLF working-copy warnings are acceptable if no whitespace errors are reported.

## Risk Register

- **Risk: promoted pricing draft is current but not Confirmed Fee authority.** Mitigation: Project Folder selectors must use Confirmed Fee status only.
- **Risk: Fee UI copy implies autosaved/promoted values are approved.** Mitigation: copy must say review/confirm Fee, not "approved" or "authority".
- **Risk: tests overfit backend internals.** Mitigation: frontend tests should mock public API responses, not repository or promotion internals.
- **Risk: TASK_315D slips into inactive removed-row UI.** Mitigation: inactive row display/editing is explicitly out of scope.
- **Risk: existing React async tests emit non-failing `act(...)` warnings.** Mitigation: record warnings if present, but do not broaden the task just to silence unrelated warnings.

## Review Checklist

- [x] Plan only, no implementation before explicit approval.
- [x] Fee UI consumes existing API contracts unless regression proves otherwise.
- [x] Project Folder readiness remains Confirmed Fee authority based.
- [x] No backend authority/schema changes unless narrowly justified.
- [x] No StepInstance/report/evidence/AI/permissions/LAN/multi-user scope.
- [x] UI copy is business-readable and hides backend names.
- [x] Required validation commands are listed and runnable.

## Completion Summary

TASK_315D was completed as a regression and UI-state gate. No production behavior changes were required after the new tests proved the existing Fee Evaluation UI already accepts TASK_315C promoted current pricing drafts and does not treat missing/stale Confirmed Fee authority as a standalone Confirm Fee blocker. Added coverage for:

- promoted current pricing draft hydration and Confirm Fee creation when authority is missing;
- stale Confirmed Fee authority refresh using the promoted current pricing draft id;
- Project Folder selector gating for Confirmed Fee authority and Required forms;
- Project Workbench mapping from `ConfirmedFeeLatestResponse.status` to Project Folder readiness;
- static frontend guard for Fee API wiring, Project Folder authority gating, and backend-term copy hygiene.

Validation:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
# 31 passed

cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
# 20 passed, with existing non-failing React act(...) warnings in older async tests

cd frontend
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
# 37 passed

py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
# 12 passed, 134 deselected

cd frontend
npm run build
# passed
```
