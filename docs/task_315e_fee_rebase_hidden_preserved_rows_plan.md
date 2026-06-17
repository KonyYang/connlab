# TASK_315E Fee Rebase Hidden Preserved Rows Implementation Plan

Status: Complete.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve operator-edited Fee Evaluation rows across Matrix soft removals, keep them hidden from active Fee Form behavior, and restore them when Matrix reselects the same group/step.

**Architecture:** Extend the existing TASK_315 rebase pipeline with a hidden preserved-row lane. Active Fee rows remain the only visible/countable/exportable rows; hidden preserved rows are persisted in the pricing draft and merged back into rebase source candidates only when Matrix reselects matching identities.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy/SQLite persistence, Pydantic v2 DTO validation, pytest, React/TypeScript only if response hydration changes require frontend adjustment.

---

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Active Task

`TASK_315E_FEE_REBASE_HIDDEN_PRESERVED_ROWS`

## Why This Is Allowed

The user explicitly requested a TASK_315E plan/task file after reviewing TASK_315A-D behavior. The task is a direct follow-up to the approved Matrix-to-Fee rebase sequence and addresses the observed gap where Matrix soft-removed Fee rows are hidden correctly but may not be preserved for later restoration after Matrix Confirm.

## Task Understanding

1. Goal: make Fee Evaluation follow Matrix selected/unselected/delete semantics while preserving edited pricing values for Matrix soft removals.
2. Input data: current confirmed Matrix basic-fill rows, saved Matrix editor draft selected groups/cells, current exact-context Fee pricing draft, pending rebase payload, and existing Fee edited values.
3. Output data: current Fee pricing draft with active rows plus hidden preserved rows, pending rebase payload that can restore preserved rows, and Confirm Fee/export behavior that sees active rows only.
4. Modules involved: Fee edited values dataclasses, pricing draft JSON persistence, rebase core, pending rebase builder, promotion service, pricing draft API tests, confirmed fee validation tests.
5. Not allowed: UI for inactive rows, Fee calculation changes, Project Folder changes, StepInstance/report/AI/permissions/LAN/multi-user work.

## File Structure

- Modify: `backend/application/fee_evaluation_edited_export_values.py`
  - Add a hidden preserved-row value object or extend the existing edited-values aggregate with `inactive_rows`.
  - Keep active-row validation separate from hidden-row compatibility checks.
- Modify: `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
  - Serialize and deserialize hidden preserved rows in pricing draft JSON.
  - Preserve backward compatibility for older drafts without `inactive_rows`.
- Modify: `backend/application/matrix_fee_draft_rebase_service.py`
  - Allow source candidates to include hidden inactive rows.
  - Extend removed-row output so inactive rows retain the full rebase key or equivalent primitive identity, including group identity, row identity, step token, and step index.
  - Preserve clear summary counts for active preserved, added, soft removed, and hard-deleted rows.
- Modify: `backend/application/matrix_fee_pending_rebase_service.py`
  - Feed current active rows plus hidden preserved rows into pending rebase source construction.
  - Compute structural Matrix rebase keys from the saved Matrix draft separately from selected target rows so soft-remove and hard-delete can be distinguished.
  - Serialize pending inactive rows without exposing them as active Fee rows.
- Create: `backend/application/matrix_fee_pending_rebase_payload.py`
  - Keep pending rebase JSON serialization/deserialization separate from the pending rebase lifecycle service so the service file stays under the project file-size limit.
- Create: `backend/application/matrix_fee_pending_rebase_source.py`
  - Keep pending rebase source-row construction, including hidden-row source candidates, separate from the lifecycle service so the service file stays under the project file-size limit.
- Modify: `backend/application/matrix_fee_rebase_promotion_service.py`
  - Carry inactive rows into promoted current pricing drafts.
  - Remap active rows to the new confirmed Matrix context while storing inactive rows as hidden recovery data.
- Modify: `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`
  - Cover JSON round-trip and legacy payload compatibility.
- Modify: `tests/unit/test_matrix_fee_draft_rebase_service.py`
  - Cover hidden preserved rows restoring when reselected and not appearing active when still unselected.
- Modify: `tests/unit/test_matrix_fee_pending_rebase_service.py`
  - Cover pending rebase source construction from active plus inactive rows.
- Modify: `tests/unit/test_matrix_fee_rebase_promotion_service.py`
  - Cover Matrix Confirm promotion preserving hidden inactive rows and later fallback restoration.
- Modify: `tests/unit/test_confirmed_fee_version_service.py` and/or `tests/integration/test_confirmed_fee_version_api.py`
  - Cover Confirm Fee ignores hidden inactive rows.
- Verify: `backend/api/routes_fee_evaluation.py` or related DTO tests to confirm hidden rows do not leak into the normal Fee Form response.
- Verify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx` and test to confirm hidden rows do not render in the Fee Evaluation page.

## Data Design

Use the existing `FeeEvaluationEditedExportValues` aggregate as the current pricing draft root:

```python
@dataclass(frozen=True)
class FeeEvaluationEditedExportValues:
    rows: tuple[FeeEvaluationEditedExportRow, ...]
    summary: FeeEvaluationEditedExportSummary
    manual_rows: tuple[FeeEvaluationEditedManualRow, ...] = ()
    inactive_rows: tuple[FeeEvaluationEditedInactiveRow, ...] = ()
```

Add a hidden row wrapper that stores the previous edited row plus enough Matrix/Fee lineage to decide whether it can be restored:

```python
@dataclass(frozen=True)
class FeeEvaluationEditedInactiveRow:
    previous_row: FeeEvaluationEditedExportRow
    rebase_key: FeeEvaluationEditedInactiveRowKey
    group_key: str
    group_label: str
    group_signature: str
    inactive_reason: str = "removed_from_matrix"
```

Use a local serializable inactive identity dataclass rather than importing `MatrixFeeRebaseKey` into `fee_evaluation_edited_export_values.py`. This keeps the Fee edited-values aggregate independent of the rebase service module while preserving the exact matching fields:

```python
@dataclass(frozen=True)
class FeeEvaluationEditedInactiveRowKey:
    group_identity: str
    row_identity: str
    step_token: str
    step_index: int
```

## API And Persistence Design

Pricing draft JSON should become:

```json
{
  "rows": [],
  "summary": {},
  "manual_rows": [],
  "inactive_rows": [
    {
      "previous_row": {},
      "key": {
        "group_identity": "group:a",
        "row_identity": "row:1",
        "step_token": "review_details",
        "step_index": 0
      },
      "group_key": "group:a",
      "group_label": "Group A",
      "group_signature": "group a",
      "inactive_reason": "removed_from_matrix"
    }
  ]
}
```

Backward compatibility rule:

```python
inactive_rows=tuple(_inactive_row_from_dict(row) for row in payload.get("inactive_rows", []))
```

Active Fee Form response/export/Confirm Fee should continue to build from `values.rows`, `values.manual_rows`, and `values.summary` only.

## Task 1: Add Full Inactive Rebase Identity To Rebase Output

**Files:**
- Modify: `tests/unit/test_matrix_fee_draft_rebase_service.py`
- Modify: `backend/application/matrix_fee_draft_rebase_service.py`

- [ ] **Step 1: Write failing removed-row identity test**

Add a rebase test where a source row is removed from selected targets. Assert the inactive removed row carries the complete rebase identity:

```python
removed = result.inactive_removed_rows[0]
assert removed.rebase_key.group_identity == "key:group-a"
assert removed.rebase_key.row_identity == "source:source-row-1"
assert removed.rebase_key.step_token == "review_details"
assert removed.rebase_key.step_index == 0
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

Expected: the new test fails because `MatrixFeeInactiveRemovedRow` does not retain the full rebase key.

- [ ] **Step 3: Extend inactive removed-row output**

Update `MatrixFeeInactiveRemovedRow` to include the full `MatrixFeeRebaseKey` generated by `_key_for(row.lineage)`. Keep the existing previous-row, group, and signature fields for backward-compatible summary/debug use.

- [ ] **Step 4: Run test to verify pass**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

Expected: rebase service tests pass and removed rows retain recoverable identity.

## Task 2: Add Hidden Row Persistence Tests

**Files:**
- Modify: `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`
- Modify: `backend/application/fee_evaluation_edited_export_values.py`
- Modify: `backend/application/fee_evaluation_pricing_draft_persistence_service.py`

- [ ] **Step 1: Write failing JSON round-trip test**

Add a test that creates a `FeeEvaluationEditedExportValues` instance with one active row and one inactive row, serializes it with `edited_values_to_json()`, deserializes it with `edited_values_from_json()`, and asserts:

```python
assert loaded.rows == values.rows
assert loaded.inactive_rows == values.inactive_rows
assert loaded.manual_rows == values.manual_rows
assert loaded.summary == values.summary
```

- [ ] **Step 2: Write legacy compatibility test**

Deserialize a JSON payload containing only `rows`, `summary`, and `manual_rows`; assert:

```python
assert loaded.inactive_rows == ()
```

- [ ] **Step 3: Run test to verify failure**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
```

Expected: tests fail because `inactive_rows` does not exist yet.

- [ ] **Step 4: Implement inactive row dataclasses and JSON round-trip**

Add the hidden inactive row dataclasses and update `edited_values_to_json()` / `edited_values_from_json()`.

- [ ] **Step 5: Run test to verify pass**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
```

Expected: pricing draft persistence tests pass.

## Task 3: Preserve Hidden Rows During Matrix Confirm Promotion

**Files:**
- Modify: `tests/unit/test_matrix_fee_rebase_promotion_service.py`
- Modify: `backend/application/matrix_fee_rebase_promotion_service.py`

- [ ] **Step 1: Write failing promotion test**

Create a pending rebase result where one source row is removed from active target rows and appears in `inactive_removed_rows` with a full rebase key. Promote it to a new confirmed Matrix. Assert:

```python
assert promoted.edited_values.rows == expected_active_rows
assert len(promoted.edited_values.inactive_rows) == 1
assert promoted.edited_values.inactive_rows[0].previous_row.notes == "operator edited note"
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

Expected: test fails because promotion currently drops inactive rows.

- [ ] **Step 3: Map `inactive_removed_rows` into hidden `inactive_rows`**

Update `remap_rebase_result_to_confirmed_matrix()` so active rows continue to remap to confirmed Matrix identities, while inactive rows are converted into hidden preserved rows and attached to `FeeEvaluationEditedExportValues(inactive_rows=...)`.

- [ ] **Step 4: Run test to verify pass**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

Expected: promotion tests pass.

## Task 4: Use Hidden Rows As Rebase Source Candidates

**Files:**
- Modify: `tests/unit/test_matrix_fee_pending_rebase_service.py`
- Modify: `tests/unit/test_matrix_fee_draft_rebase_service.py`
- Modify: `backend/application/matrix_fee_pending_rebase_service.py`
- Modify: `backend/application/matrix_fee_draft_rebase_service.py`

- [ ] **Step 1: Write failing restoration test**

Build a source pricing draft with:

```python
rows=()
inactive_rows=(previously_edited_group_a_row,)
```

Build a Matrix draft target where Group A is selected again. Assert the rebased active row restores the edited values:

```python
assert result.active_rows[0].edited_values.notes == "operator edited note"
assert result.active_rows[0].edited_values.unit_price == "888"
assert result.summary.preserved_count == 1
```

- [ ] **Step 2: Write still-hidden test**

Build a Matrix draft target where Group A remains unselected. Assert:

```python
assert result.active_rows == ()
assert len(result.inactive_removed_rows) == 1
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

Expected: restoration fails because hidden inactive rows are not fed as source candidates.

- [ ] **Step 4: Merge active and hidden rows into rebase source input**

Update the pending rebase builder so it converts hidden inactive rows into `MatrixFeeRebaseSourceRow` candidates alongside current active rows. Preserve key identity so selected Matrix targets can match the old hidden row.

- [ ] **Step 5: Run tests to verify pass**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

Expected: rebase and pending service tests pass.

## Task 5: Distinguish Soft Remove From Hard Delete

**Files:**
- Modify: `tests/unit/test_matrix_fee_pending_rebase_service.py`
- Modify: `backend/application/matrix_fee_pending_rebase_service.py`
- Modify: `backend/application/matrix_fee_draft_rebase_service.py`

- [ ] **Step 1: Write failing hard-delete cleanup test**

Build a previous inactive row for Group A, then build a Matrix draft where Group A no longer exists structurally. Assert the new pending/current hidden rows no longer include Group A:

```python
assert all(row.group_key != "group:a" for row in result.inactive_removed_rows)
```

- [ ] **Step 2: Write soft-remove preservation test**

Build a Matrix draft where Group A exists structurally but `is_selected=False`. Assert the hidden row remains available:

```python
assert any(row.group_key == "group:a" for row in result.inactive_removed_rows)
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py -q
```

Expected: hard-delete/soft-remove distinction is not explicit yet.

- [ ] **Step 4: Add structural existence filtering**

When creating target/source context from a Matrix draft, add a helper with this contract:

```python
def _structural_rebase_keys_from_matrix_draft(
    draft: ProjectMatrixDraftSnapshot,
) -> set[MatrixFeeRebaseKey]:
    """Return keys for all structurally present non-sample Matrix row steps."""
```

The helper must inspect all non-sample Matrix rows/cells/groups that still exist in the draft, not only groups where `is_selected=True`. Preserve hidden rows only when their key is in this structural key set and absent from selected target rows. Drop hidden rows whose key is missing from the structural set because that is the Matrix hard-delete case.

- [ ] **Step 5: Run tests to verify pass**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py -q
```

Expected: pending rebase tests pass with explicit soft/hard semantics.

## Task 6: Keep Confirm Fee And Export Active-Only

**Files:**
- Modify: `tests/unit/test_confirmed_fee_version_service.py`
- Modify: `tests/integration/test_confirmed_fee_version_api.py`
- Verify: `backend/application/confirmed_fee_version_service.py`
- Verify: Fee Evaluation export/payload route modules

- [ ] **Step 1: Write active-only Confirm Fee test**

Create saved pricing draft values with one active row and one inactive row. Confirm Fee with summary matching only the active row. Assert Confirm Fee succeeds and the confirmed Fee snapshot contains only active rows.

- [ ] **Step 2: Write inactive-row exclusion test**

Use an inactive row with a large `testing_fee`, e.g. `999999`. Assert backend derived totals do not include it:

```python
assert confirmed.summary.testing_fee_total != "999999"
```

- [ ] **Step 3: Run tests**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Expected: tests pass if the existing code is already active-only. If either test fails, the failure identifies the boundary that must be narrowed before this task can be complete.

- [ ] **Step 4: Narrow active-only paths if needed**

If any Confirm Fee/export path accidentally reads inactive rows, change it to read active `rows` only and keep hidden rows server-side draft recovery data.

- [ ] **Step 5: Run tests to verify pass**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Expected: Confirm Fee tests pass.

## Task 7: Frontend/API Compatibility Verification

**Files:**
- Verify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Verify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

- [ ] **Step 1: Run existing Fee frontend test**

Run:

```powershell
cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

Expected: pass if API still returns only active rows to the page or frontend ignores unknown `inactive_rows`.

- [ ] **Step 2: Record compatibility result**

If the test passes without frontend changes, record that no frontend modification is required because hidden rows remain server-side recovery data. If the test shows hidden rows leak into visible rows, add a focused regression asserting the removed group label is not rendered while active rows still render, then fix the hydration boundary.

- [ ] **Step 3: Build frontend after compatibility verification**

Run:

```powershell
cd frontend; npm run build
```

Expected: build passes.

## Task 8: Final Validation And Board Update

**Files:**
- Modify: `docs/task_board.md`
- Modify: `tasks/TASK_315E_FEE_REBASE_HIDDEN_PRESERVED_ROWS.md`
- Modify: `docs/task_315e_fee_rebase_hidden_preserved_rows_plan.md`

- [ ] **Step 1: Run focused backend validation**

Run:

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Expected: all focused tests pass.

- [ ] **Step 2: Run frontend validation if frontend changed**

Run:

```powershell
cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false
cd frontend; npm run build
```

Expected: tests/build pass.

- [ ] **Step 3: Update task file and board**

Set `TASK_315E` status to complete only after implementation and validation. Update `docs/task_board.md` with validation summary and the stop point.

- [ ] **Step 4: Stop**

Do not proceed to inactive-row UI, StepInstance, report generation, AI review, permissions, LAN/server, multi-user scope, or later tasks without a separate approved task.

## Risks

- Hidden rows must not be validated as active current Matrix identities, or old inactive rows could block pricing draft load/save.
- Hidden rows must not leak into Fee totals, exports, or Confirm Fee snapshots.
- Hard delete detection depends on Matrix draft structural identity being available separately from selected target rows.
- Existing historical pricing drafts lack `inactive_rows`; deserialization must treat that as an empty tuple.
- Rebase identity must stay stable enough to recover operator edits after label-only changes where lineage still matches.

## Review Checklist

- Architecture: application services keep business logic; API/routes remain thin.
- Scope: only hidden preserved Fee rows for Matrix soft remove/reselect lifecycle.
- Data: active rows and hidden inactive rows have distinct validation/export behavior.
- Tests: soft remove, reselect restore, hard delete cleanup, JSON round-trip, Confirm Fee active-only.
- Stop point: implementation halts after TASK_315E validation.

## Completion Summary

TASK_315E is implemented. Hidden inactive rows are persisted in Fee pricing drafts for Matrix soft-remove recovery, restored when Matrix reselects matching rows, filtered out when Matrix structure is truly deleted, and excluded from Confirm Fee authority snapshots. Pending rebase payload JSON helpers were split into `backend/application/matrix_fee_pending_rebase_payload.py` so the pending rebase lifecycle service stays under the project file-size limit.

Review follow-up closed the remaining lifecycle gaps: active-only Fee autosave now preserves existing server-side hidden inactive rows, hidden inactive rows can become source candidates even when absent from the current Confirmed Matrix basic-fill, and a service-level regression now covers soft-remove promotion plus Fee autosave plus later Matrix reselect restoration. Source-row construction was split into `backend/application/matrix_fee_pending_rebase_source.py` to keep the pending rebase lifecycle service under the project file-size limit.

Validation:

- `py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py -q` (`41 passed`)
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` (`22 passed`)
- `py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q` (`16 passed`)
- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false` (`22 passed`, with existing non-failing React `act(...)` warnings)
- `cd frontend; npm run build` passed
