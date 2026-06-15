# TASK_315C Matrix Confirm Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After Matrix Confirm succeeds, promote pending Matrix-to-Fee rebase output into the current Fee Evaluation pricing draft for the newly confirmed Matrix context, with a synchronous fallback when pending rebase is missing.

**Architecture:** Keep TASK_315C as a backend lifecycle slice hanging off Matrix Confirm. It consumes TASK_315B pending payloads or computes a confirm-time fallback, remaps Matrix draft lineage to the newly generated Confirmed Matrix ids and new Fee basic-fill identities, writes only Fee pricing draft state, and returns non-fatal promotion status on the Matrix Confirm response. Fee UI, Project Folder, inactive-row display, and Confirm Fee authority remain later tasks.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, SQLite, Pydantic v2, pytest.

---

## Current Phase And Permission Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task status:

```text
TASK_315C_MATRIX_CONFIRM_PROMOTION is planned only.
```

TASK_315C may be implemented only after the user explicitly approves this specific subtask.

Implementation status:

```text
Complete after explicit user approval on 2026-06-15.
Review follow-up complete: pending promotion now validates the pending Matrix draft payload signature against the saved Matrix draft signature being confirmed, and tests cover stale-signature fallback plus sample-preparation manual row remap.
```

## Anti-Skip Statement

- Current completed baseline: TASK_314A, TASK_314B, TASK_314C, TASK_315A, and TASK_315B are complete.
- TASK_315 remains an umbrella and must not be implemented as one combined task.
- TASK_315C is allowed to plan because TASK_315B now persists pending rebase output and the user requested a Matrix Confirm promotion plan.
- Not allowed in TASK_315C: Fee Evaluation UI, inactive-row display, Project Folder behavior, Confirm Fee changes, StepInstance, report generation, AI, permissions, LAN/server, or multi-user scope.

## Task Understanding

### Goal

Matrix Confirm should publish the Matrix authority first. After that succeeds, ConnLab should try to create/update the current Fee Evaluation pricing draft for the new Confirmed Matrix revision:

1. Prefer the pending rebase snapshot produced by Matrix autosave.
2. If pending is missing/stale/unusable, run a synchronous fallback rebase.
3. If promotion fails, keep Matrix Confirm successful and return promotion failure metadata.

### Inputs

- `ProjectMatrixDraftSnapshot` loaded by `MatrixEditorSessionService._load_expected_saved_draft(...)`.
- Previous active `ConfirmedMatrixSnapshot`.
- Newly published `ConfirmedMatrixSnapshot`.
- `MatrixFeePendingRebaseSnapshot` from `MatrixFeePendingRebaseRepository`.
- Previous-context `FeeEvaluationPricingDraftSnapshot`, when one exists.
- Current Fee rule version id.
- `FeeEvaluationPricingDraftEditRepository`.
- TASK_315A rebase core plus explicit basic-fill rows built from the previous active Confirmed Matrix snapshot for fallback.

### Outputs

- A new current `FeeEvaluationPricingDraftSnapshot` for:

```text
project_id + new_confirmed_matrix_id + new_confirmed_revision + fee_rule_version_id
```

- Matrix Confirm response fields:

```python
fee_rebase_promotion_status: str = "not_required"
fee_rebase_promotion_summary: MatrixFeeRebaseSummaryResponse | None = None
fee_rebase_promotion_error: str | None = None
```

### Explicit Non-Goals

- Do not create Confirmed Fee authority.
- Do not change Confirm Fee validation.
- Do not display inactive removed rows.
- Do not include inactive removed rows in Fee draft active rows.
- Do not change Project Folder readiness.
- Do not add frontend Matrix/Fee UI status.
- Do not run fallback source construction through an active-only Matrix basic-fill service after Matrix Confirm has already published the new active Matrix.

## Design Summary

### Promotion Status

Use:

```python
MatrixFeeRebasePromotionStatus = Literal[
    "not_required",
    "promoted",
    "fallback_promoted",
    "skipped",
    "failed",
]
```

Status rules:

- `not_required`: no-change confirm or first authority publish.
- `promoted`: pending rebase consumed and saved into new pricing draft context.
- `fallback_promoted`: pending missing/unusable, fallback rebase saved into new pricing draft context.
- `skipped`: no pending and no base pricing draft exists, so there is no saved Fee work to preserve.
- `failed`: Matrix Confirm succeeded, but promotion/fallback failed.

### Pending Payload Deserialization

TASK_315B serializes pending payload as:

```json
{
  "active_rows": [],
  "inactive_removed_rows": [],
  "manual_rows": [],
  "summary": {
    "preserved_count": 0,
    "added_count": 0,
    "removed_count": 0,
    "preserved_manual_count": 0,
    "removed_manual_count": 0
  },
  "warnings": []
}
```

TASK_315C should add a deserializer beside the serializer in `backend/application/matrix_fee_pending_rebase_service.py` or a small new helper module if the file grows too large:

```python
def pending_rebase_payload_from_json(payload_json: str) -> MatrixFeeRebaseResult:
    ...
```

The deserializer must preserve active rows, inactive removed rows, manual rows, summary, and warnings. TASK_315C must not put `inactive_removed_rows` into the current Fee pricing draft `rows`.

### New-Context Identity Projection

TASK_315B pending active rows are target-draft-shaped. They may contain `confirmed_group_id`/`confirmed_row_id` values that are actually Matrix draft ids, and their `source_line_id` may also be draft-shaped. After Matrix Confirm, the new Confirmed Matrix uses fresh confirmed ids and the Fee draft validation identity is:

```python
(source_line_id, confirmed_group_id, confirmed_row_id, step_token, step_index)
```

`source_line_id` must match the new basic-fill line generated from the new Confirmed Matrix. It cannot be preserved from pending payload when that value was based on Matrix draft ids or the previous authority.

Promotion must therefore project each promoted row onto the new Confirmed Matrix basic-fill identity:

- use `ConfirmedMatrixGroup.draft_group_id` to map draft group id to new `confirmed_group_id`;
- use `ConfirmedMatrixRow.draft_row_id` to map draft row id to new `confirmed_row_id`;
- generate or look up the new `source_line_id` from the same basic-fill identity logic used by Fee Evaluation for the new Confirmed Matrix;
- keep editable pricing fields from the pending/fallback rebase row;
- keep `step_token` and `step_index` only when they match the new basic-fill line identity.

Implementation should extract a snapshot-based helper from `confirmed_matrix_fee_template_basic_fill_service.py` if needed, for example:

```python
def build_basic_fill_from_confirmed_snapshot(
    snapshot: ConfirmedMatrixSnapshot,
) -> MatrixBasicFillWorkbook:
    ...
```

`ConfirmedMatrixFeeTemplateBasicFillService.build(project_id)` can continue to call the helper with active-by-project. TASK_315C promotion/fallback must call the helper directly with the explicit previous or new snapshot so it does not accidentally read the wrong active Matrix.

Manual sample-preparation rows with a group id/key/label should be remapped to the new Confirmed Matrix group id by draft id when available, otherwise by normalized group key/label. Report-preparation manual rows remain global.

If an active row cannot be remapped to the new Confirmed Matrix, promotion must fail non-fatally with `fee_rebase_promotion_status="failed"` rather than saving a partial current pricing draft.

Before saving, promotion must validate the resulting `FeeEvaluationEditedExportValues` against a basic-fill workbook built from the new Confirmed Matrix snapshot. A current pricing draft created by TASK_315C must be accepted by `edited_row_lookup(...)` / `_validate_edited_values(...)` for the new context.

### Previous Summary Preservation

Pending payloads from TASK_315B store rebase rows and rebase summary counts, not the editable Fee summary fields:

```python
condition_confirmation_spend_time
external_cost
external_cost_note
lab_manpower_hourly_rate
```

TASK_315C must load the previous-context pricing draft whenever one exists, even when pending payload is valid. The promoted draft summary must come from that previous pricing draft for both:

- pending promotion;
- synchronous fallback promotion.

Blank/default summary values are allowed only when no previous pricing draft exists. In the normal valid-pending path, missing previous pricing draft should be treated as `skipped` unless the implementation has a tested, product-accepted seed/default behavior.

### Fallback Source Context

Fallback runs after Matrix Confirm has already published the new active Matrix, so it must not call `DefaultMatrixFeePendingRebaseBuilder.build_and_rebase(...)` unchanged if that builder reads source rows via `ConfirmedMatrixFeeTemplateBasicFillService.build(project_id)`.

The fallback path must use explicit contexts:

- source rows: basic-fill rows built from `previous_confirmed_matrix`;
- source pricing values: previous-context pricing draft;
- target rows/groups: saved Matrix draft confirmed by this Matrix Confirm;
- save context: newly published Confirmed Matrix id/revision.

This can be implemented either by:

- adding a new fallback builder that accepts explicit `previous_confirmed_matrix` and `saved_matrix_draft`; or
- extracting lower-level helpers so promotion can call `MatrixFeeDraftRebaseService.rebase(...)` directly with explicit source/target inputs.

Do not rely on active-by-project source lookup after publish; at that point active-by-project is the new Matrix.

### Promotion Service

Create `backend/application/matrix_fee_rebase_promotion_service.py`.

Core dataclasses:

```python
@dataclass(frozen=True, slots=True)
class PromoteMatrixFeeRebaseCommand:
    project_id: str
    saved_matrix_draft: ProjectMatrixDraftSnapshot
    previous_confirmed_matrix: ConfirmedMatrixSnapshot
    new_confirmed_matrix: ConfirmedMatrixSnapshot
    fee_rule_version_id: str

@dataclass(frozen=True, slots=True)
class MatrixFeeRebasePromotionResult:
    status: MatrixFeeRebasePromotionStatus
    summary: MatrixFeeRebaseSummary | None = None
    error: str | None = None
```

Store Protocols:

```python
class MatrixFeePendingRebaseReadStore(Protocol):
    def get_by_context(
        self,
        *,
        project_matrix_draft_id: str,
        fee_rule_version_id: str,
    ) -> MatrixFeePendingRebaseSnapshot | None: ...

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int: ...

class FeePricingDraftPromotionStore(Protocol):
    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None: ...

    def upsert_current(
        self,
        snapshot: FeeEvaluationPricingDraftSnapshot,
    ) -> FeeEvaluationPricingDraftSnapshot: ...
```

Promotion behavior:

1. Load pending by `saved_matrix_draft.record.project_matrix_draft_id + fee_rule_version_id`.
2. Validate pending:
   - same project id;
   - same draft id;
   - same base Confirmed Matrix id/revision as previous active Matrix;
   - same fee rule version.
3. If pending is valid:
   - deserialize pending result;
   - remap active/manual rows to new Confirmed Matrix ids;
   - save a new current Fee pricing draft for the new confirmed context;
   - delete pending rows for the Matrix draft only after save succeeds;
   - return `promoted`.
4. If pending is missing/stale/unusable:
   - if no base pricing draft exists for previous active Matrix/rule, return `skipped`;
   - otherwise run fallback rebase using explicit previous active Matrix source rows and the saved Matrix draft target rows;
   - remap/save/delete as above;
   - return `fallback_promoted`.
5. Catch operational failures and return `failed` with actionable message.

### Matrix Confirm Integration

Integration point:

- `MatrixEditorSessionService.confirm_session`, immediately after `_publish_saved_revision(...)` succeeds.

V1 should only promote for existing-active-Matrix saved revision confirms:

```python
saved_draft = self._load_expected_saved_draft(command, active)
confirmed = self._publish_saved_revision(...)
promotion = self._fee_rebase_promotion.promote_after_matrix_confirm(...)
return MatrixEditorSessionConfirmResult(..., fee_rebase_promotion_status=promotion.status, ...)
```

No-change and first authority publish should return `not_required`.

The existing source-lineage replacement path should be treated carefully:

- If it publishes a new Confirmed Matrix without an editor saved draft/pending rebase, return `not_required` in TASK_315C.
- Do not expand source replacement behavior unless a test proves it uses the same saved draft/pending contract.

### API Response Extension

Extend `MatrixEditorSessionConfirmResponse` in `backend/api/routes_matrix_editor_session.py`:

```python
fee_rebase_promotion_status: str = "not_required"
fee_rebase_promotion_summary: MatrixFeeRebaseSummaryResponse | None = None
fee_rebase_promotion_error: str | None = None
```

Reuse the summary response shape introduced by TASK_315B for autosave.

Do not add a new API endpoint in TASK_315C.

## File-Level Plan

### Create

- `backend/application/matrix_fee_rebase_promotion_service.py`
  - promotion commands/results/status
  - pending payload deserialization or usage of helper
  - previous/new snapshot basic-fill identity projection
  - row/manual-row remapping
  - previous pricing draft summary preservation
  - pending promotion/fallback orchestration

- `tests/unit/test_matrix_fee_rebase_promotion_service.py`
  - unit coverage for promotion, fallback, skipped, failed, remapping, pending cleanup

### Modify

- `backend/application/matrix_fee_pending_rebase_service.py`
  - add `pending_rebase_payload_from_json(...)` if not placed in promotion service
  - do not reuse `DefaultMatrixFeePendingRebaseBuilder.build_and_rebase(...)` for confirm-time fallback unless it is changed to accept explicit previous Matrix context

- `backend/infrastructure/storage/repositories/matrix_fee_pending_rebase.py`
  - no schema changes expected
  - ensure `get_by_context(...)` and `delete_by_matrix_draft(...)` are sufficient

- `backend/application/confirmed_matrix_fee_template_basic_fill_service.py`
  - optional narrow extraction of a snapshot-based basic-fill helper so TASK_315C can build source rows from previous active Matrix and validation rows from new Confirmed Matrix without querying active-by-project

- `backend/application/matrix_editor_session_service.py`
  - add optional promotion service dependency
  - extend `MatrixEditorSessionConfirmResult`
  - call promotion only after saved revision publish succeeds
  - keep Matrix Confirm success if promotion fails

- `backend/api/dependencies.py`
  - wire `MatrixFeeRebasePromotionService`

- `backend/api/routes_matrix_editor_session.py`
  - extend Matrix Confirm response DTO

- `tests/unit/test_matrix_editor_session_service.py`
  - Matrix Confirm promotion status tests

- `tests/integration/test_matrix_editor_session_api.py`
  - API promotion response and persistence tests

### Avoid

- no frontend files
- no Confirmed Fee files
- no Project Folder files
- no Confirm Fee API behavior changes
- no migration unless a real storage gap is discovered

## Implementation Tasks

### Task 1: Pending Payload Deserialization And Remapping Helpers

**Files:**

- Modify: `backend/application/matrix_fee_pending_rebase_service.py`
- Create: `backend/application/matrix_fee_rebase_promotion_service.py`
- Test: `tests/unit/test_matrix_fee_rebase_promotion_service.py`

- [x] **Step 1: Write failing deserialization/remapping tests**

Add tests for:

- `pending_rebase_payload_from_json(...)` roundtrips rows/manual rows/summary/warnings produced by `pending_rebase_payload_to_json(...)`.
- remapping replaces draft group/row ids and draft-shaped `source_line_id` values with new Confirmed Matrix basic-fill identities.
- remapping fails when an active row references a draft row/group not present in the new Confirmed Matrix.
- remapped promoted values pass `edited_row_lookup(...)` or `_validate_edited_values(...)` against a basic-fill workbook built from the new Confirmed Matrix snapshot.

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

Expected: fails because promotion service/deserializer do not exist.

- [x] **Step 2: Implement deserializer and remapping helpers**

Implement:

```python
def pending_rebase_payload_from_json(payload_json: str) -> MatrixFeeRebaseResult:
    ...

def remap_rebase_result_to_confirmed_matrix(
    *,
    rebase_result: MatrixFeeRebaseResult,
    previous_pricing_draft: FeeEvaluationPricingDraftSnapshot | None,
    new_confirmed_matrix: ConfirmedMatrixSnapshot,
) -> FeeEvaluationEditedExportValues:
    ...
```

Rules:

- active rows only become `FeeEvaluationEditedExportValues.rows`;
- inactive removed rows are not saved into active rows;
- `source_line_id`, `confirmed_group_id`, and `confirmed_row_id` must come from the new Confirmed Matrix basic-fill identity, not from pending payload;
- summary must use the previous pricing draft summary when available; safe blank defaults are allowed only when no previous pricing draft exists;
- manual rows are preserved and sample-preparation group ids are remapped to new Confirmed Matrix groups.

- [x] **Step 3: Run tests**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

Expected: deserialization/remapping tests pass.

### Task 2: Promotion Application Service

**Files:**

- Modify: `backend/application/matrix_fee_rebase_promotion_service.py`
- Test: `tests/unit/test_matrix_fee_rebase_promotion_service.py`

- [x] **Step 1: Write failing promotion service tests**

Cover:

- valid pending rebase is promoted into new pricing draft context;
- promoted rows use new Confirmed Matrix `source_line_id`, group ids, and row ids;
- pending promotion preserves previous pricing draft summary fields;
- pending row is deleted only after save success;
- save failure returns `failed` and does not delete pending;
- missing pending + base pricing draft triggers fallback and returns `fallback_promoted`;
- fallback uses previous active Matrix source rows rather than reading active-by-project after publish;
- fallback promotion preserves previous pricing draft summary fields;
- missing pending + no base pricing draft returns `skipped`;
- stale pending base Confirmed Matrix id/revision triggers fallback or skipped, not promotion.

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

Expected: new tests fail before service implementation.

- [x] **Step 2: Implement service orchestration**

Implement:

```python
class MatrixFeeRebasePromotionService:
    def promote_after_matrix_confirm(
        self,
        command: PromoteMatrixFeeRebaseCommand,
    ) -> MatrixFeeRebasePromotionResult:
        ...
```

Dependencies:

- pending store;
- pricing draft store;
- explicit fallback rebase builder or lower-level `MatrixFeeDraftRebaseService` input helpers that accept previous/new snapshots;
- clock/id factory if needed for deterministic tests.

Promotion save should create/update `FeeEvaluationPricingDraftSnapshot` for the new context and call `pricing_draft_store.upsert_current(...)` directly, avoiding `FeeEvaluationPricingDraftPersistenceService.save(...)` if that service always rebuilds basic-fill from current active Matrix in a way that makes test injection or failure handling too indirect.

The service must still validate the edited values against a basic-fill workbook derived from `new_confirmed_matrix` before calling `upsert_current(...)`.

- [x] **Step 3: Run service tests**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

Expected: all promotion service tests pass.

### Task 3: Matrix Confirm Service Integration

**Files:**

- Modify: `backend/application/matrix_editor_session_service.py`
- Test: `tests/unit/test_matrix_editor_session_service.py`

- [x] **Step 1: Write failing Matrix Confirm integration tests**

Add unit tests for:

- saved revision confirm returns `fee_rebase_promotion_status="promoted"` when promotion service succeeds;
- promotion failure returns `fee_rebase_promotion_status="failed"` but `publish_status="published"`;
- no-change confirm returns `not_required`;
- first authority publish returns `not_required`.

Run:

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py -q
```

Expected: tests fail before result/integration fields exist.

- [x] **Step 2: Extend MatrixEditorSessionConfirmResult**

Add:

```python
fee_rebase_promotion_status: MatrixFeeRebasePromotionStatus = "not_required"
fee_rebase_promotion_summary: MatrixFeeRebaseSummary | None = None
fee_rebase_promotion_error: str | None = None
```

- [x] **Step 3: Wire promotion service**

Add optional dependency:

```python
fee_rebase_promotion_service: MatrixFeeRebasePromotionServiceProtocol | None = None
```

Default null implementation returns `not_required`.

After `_publish_saved_revision(...)` succeeds, call:

```python
promotion = self._fee_rebase_promotion.promote_after_matrix_confirm(
    PromoteMatrixFeeRebaseCommand(
        project_id=command.project_id,
        saved_matrix_draft=saved_draft,
        previous_confirmed_matrix=active,
        new_confirmed_matrix=confirmed,
        fee_rule_version_id=self._fee_rule_version_provider(),
    )
)
```

Return promotion metadata in the confirm result. The promotion service should own exception-to-`failed` conversion; Matrix Confirm should still defensively catch unexpected exceptions and convert them to failed promotion metadata.

- [x] **Step 4: Run service integration tests**

Run:

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py -q
```

Expected: all Matrix session unit tests pass.

### Task 4: API And Dependency Wiring

**Files:**

- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/routes_matrix_editor_session.py`
- Test: `tests/integration/test_matrix_editor_session_api.py`

- [x] **Step 1: Write failing API integration tests**

Cover:

- Confirm Matrix after autosave pending returns `fee_rebase_promotion_status="promoted"` and creates current pricing draft for new confirmed context.
- The created current pricing draft can be loaded/saved by Fee Evaluation pricing draft persistence for the new Confirmed Matrix context, proving its identity fields match new basic-fill output.
- Confirm Matrix with no pending but existing base pricing draft returns `fallback_promoted`.
- Fallback promotion keeps previous pricing row edits and summary values after Matrix Confirm has made the new Matrix active.
- Promotion failure path still returns HTTP 200 with `publish_status="published"` and `fee_rebase_promotion_status="failed"` if achievable via dependency override/fake.

Run:

```powershell
py -m pytest tests/integration/test_matrix_editor_session_api.py -q
```

Expected: tests fail before API response fields/dependency wiring exist.

- [x] **Step 2: Wire dependency**

In `get_matrix_editor_session_service(...)`, create:

```python
promotion_service = MatrixFeeRebasePromotionService(
    pending_store=MatrixFeePendingRebaseRepository(session),
    pricing_draft_store=FeeEvaluationPricingDraftEditRepository(session),
    rebase_service=MatrixFeeDraftRebaseService(),
)
```

Pass any snapshot-basic-fill helper dependency explicitly if the final service constructor needs one. Do not wire the confirm-time fallback to an active-only builder that reads the already-promoted active Matrix as its source.

Pass the promotion service into `MatrixEditorSessionService`.

- [x] **Step 3: Extend API response**

Add promotion fields to `MatrixEditorSessionConfirmResponse` and map them from `MatrixEditorSessionConfirmResult`.

- [x] **Step 4: Run API tests**

Run:

```powershell
py -m pytest tests/integration/test_matrix_editor_session_api.py -q
```

Expected: all Matrix Editor session API tests pass.

### Task 5: Final Validation And Board Sync

**Files:**

- Modify: `docs/task_board.md`
- Modify: `tasks/TASK_315C_MATRIX_CONFIRM_PROMOTION.md`
- Modify: `docs/task_315c_matrix_confirm_promotion_plan.md`
- Optionally modify: `docs/task_plan_index.md`

- [x] **Step 1: Run required validation**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_repository.py tests/unit/test_matrix_fee_draft_rebase_service.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Expected: all pass.

- [x] **Step 2: Confirm no out-of-scope files changed**

Run:

```powershell
git diff --name-only
```

Expected for TASK_315C work: backend application/API Matrix session files, pending/promotion service files, Fee pricing draft tests where needed, docs/task files. No frontend files, no Project Folder files, no Confirmed Fee authority changes.

- [x] **Step 3: Update task board**

Mark TASK_315C complete only after validation. The board must say TASK_315D requires separate task file, plan, review, and explicit approval.

## Race And Failure Test Requirements

The implementation must include at least:

- pending promotion deletes pending only after pricing draft save succeeds;
- failed promotion does not roll back Matrix Confirm;
- stale/mismatched pending base Matrix context is not promoted blindly;
- fallback promotion uses the previous-context base pricing draft and saves to the new Matrix context;
- fallback source rows are built from previous active Matrix context, not active-by-project after publish;
- pending and fallback promotion preserve previous pricing draft summary fields;
- promoted current pricing draft validates against new Confirmed Matrix basic-fill identities;
- no pending and no base pricing draft returns skipped;
- row/group remapping refuses unmapped active rows instead of saving partial data.

## Review Checklist

- [x] Does Matrix Confirm still succeed when Fee promotion fails?
- [x] Does promotion write a current Fee pricing draft for the new Confirmed Matrix id/revision?
- [x] Are promoted rows remapped to new Confirmed Matrix ids and new basic-fill `source_line_id` identities?
- [x] Does fallback build source rows from previous active Matrix rather than active-by-project after publish?
- [x] Are previous pricing draft summary fields preserved in both pending and fallback promotion?
- [x] Are inactive removed rows kept out of active pricing draft rows?
- [x] Is pending deleted only after successful promotion?
- [x] Does fallback avoid blocking Matrix Confirm?
- [x] Are Confirm Fee, Fee UI, Project Folder, and frontend untouched?

## Stop Point

After this plan is reviewed, stop. Do not implement TASK_315C until the user explicitly approves `TASK_315C_MATRIX_CONFIRM_PROMOTION`.
