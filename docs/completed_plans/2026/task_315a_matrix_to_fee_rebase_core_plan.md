# TASK_315A Matrix To Fee Rebase Core Plan

Status: Complete. Implemented after separate explicit user approval.

## Current Phase And Permission Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task status:

```text
TASK_315A_MATRIX_TO_FEE_REBASE_CORE is complete.
```

TASK_315A was implemented only after the user explicitly approved this specific subtask.

## Anti-Skip Statement

- Current completed baseline: TASK_314A, TASK_314B, and TASK_314C are complete.
- TASK_315 is now an umbrella and must not be implemented as one combined task.
- TASK_315A implementation was allowed because the user explicitly approved it.
- Not allowed in TASK_315A: pending persistence, Matrix autosave integration, Matrix Cancel cleanup, Matrix Confirm promotion, Fee Evaluation UI, Project Folder behavior, StepInstance, report generation, AI, permissions, LAN/server, or multi-user scope.

## Task Understanding

### Goal

Build a pure backend Matrix-to-Fee rebase core that can preserve Fee draft edits across Matrix structural edits.

The core should transform source Fee edited values from a base Matrix context into target Fee edited values for a changed Matrix draft context.

### Inputs

- Source/base active Matrix row and group identity metadata.
- Source/base Fee edited rows and manual rows.
- Target Matrix draft row and group identity metadata.
- Target default Fee rows or a caller-supplied default-row builder result.

### Outputs

- Active target Fee rows.
- Inactive removed Fee rows.
- Preserved/rebased manual rows.
- Rebase summary counts.
- Optional warnings for fallback matching.

### Modules

Expected backend files:

- `backend/application/matrix_fee_draft_rebase_service.py`
- `tests/unit/test_matrix_fee_draft_rebase_service.py`

Possible touched files only if the implementation needs shared value types:

- `backend/domain/confirmed_matrix_fee_evaluation.py`
- `backend/application/confirmed_matrix_fee_template_basic_fill_service.py`

Only touch `backend/application/confirmed_matrix_fee_template_basic_fill_service.py`
if TASK_315A needs to reuse existing `MatrixBasicFillLine`,
`MatrixBasicFillGroup`, or `MatrixBasicFillWorkbook` value types. Do not
create or edit a non-existent `fee_evaluation_basic_fill_service.py` module.

No API route, repository, frontend, or Project Folder files should be modified in TASK_315A.

### Explicit Non-Goals

- No database table or repository for pending rebase.
- No FastAPI route changes.
- No Matrix autosave response changes.
- No Matrix Confirm behavior changes.
- No pricing draft save/load behavior changes.
- No Fee UI or Project Folder UI changes.
- No Confirm Fee behavior changes.

## Design

### Rebase Key Helper

Add a deterministic key helper in the application layer. Keep it pure and testable.

Proposed value:

```python
@dataclass(frozen=True)
class MatrixFeeRebaseKey:
    group_identity: str
    row_identity: str
    step_token: str
    step_index: int
```

Normalization rules:

- trim leading/trailing whitespace;
- collapse internal whitespace;
- casefold for identity comparison;
- stringify numeric step tokens consistently;
- use the existing 0-based parsed-token `step_index` convention from
  `MatrixBasicFillLine.step_index`;
- preserve raw display text separately on rows, not inside the key.

Row identity priority:

1. `source_row_snapshot_id`
2. `draft_row_id`
3. normalized row signature from `test_item`, `source_section`, `method`, `condition`, `requirement`

Group identity priority:

1. normalized group key
2. normalized group label

### Value Models

Use small dataclasses or Pydantic-free application value objects unless existing project conventions strongly prefer existing domain dataclasses.

Proposed models:

```python
@dataclass(frozen=True)
class MatrixFeeRebaseSourceRow:
    key: MatrixFeeRebaseKey
    edited_row: FeeEvaluationEditedExportRow
    group_key: str | None
    group_label: str
    row_signature: str

@dataclass(frozen=True)
class MatrixFeeRebaseTargetRow:
    key: MatrixFeeRebaseKey
    default_row: FeeEvaluationEditedExportRow
    group_key: str | None
    group_label: str
    row_signature: str

@dataclass(frozen=True)
class MatrixFeeInactiveRemovedRow:
    previous_row: FeeEvaluationEditedExportRow
    previous_group_key: str | None
    previous_group_label: str
    previous_row_signature: str
    inactive_reason: str = "removed_from_matrix"

@dataclass(frozen=True)
class MatrixFeeRebaseSummary:
    preserved_count: int
    added_count: int
    removed_count: int
    preserved_manual_count: int = 0
    removed_manual_count: int = 0

@dataclass(frozen=True)
class MatrixFeeRebaseResult:
    active_rows: tuple[FeeEvaluationEditedExportRow, ...]
    inactive_removed_rows: tuple[MatrixFeeInactiveRemovedRow, ...]
    manual_rows: tuple[FeeEvaluationManualRow, ...]
    summary: MatrixFeeRebaseSummary
    warnings: tuple[str, ...] = ()
```

If existing Fee row classes have different names, adapt to the current code. Do not introduce new persistence DTOs in TASK_315A.

### Row Rebase Algorithm

1. Build a lookup from source rows by `MatrixFeeRebaseKey`.
2. Iterate target rows in target Matrix display/order.
3. If target key exists in source lookup:
   - copy editable Fee fields from the source row;
   - keep target lineage/identity fields from the target default row;
   - count as preserved.
4. If target key is absent:
   - use target default row;
   - count as added.
5. After target iteration, any unused source rows become inactive removed rows.
6. Return active rows in target order and inactive rows in source order.

The copied editable-field set must be explicit. Do not blindly copy source IDs or target lineage fields. If the existing Fee row model is broad, add a private helper such as `_copy_editable_fee_values(source, target_default)`.

### Manual Row Rebase Algorithm

Report preparation:

- Preserve globally.
- Do not bind to Matrix group ids.

Sample preparation:

- Match by normalized group key/label.
- If the group remains in the target Matrix, preserve edited manual row values and update target group display/lineage if the row model supports it.
- If the group is removed, do not return it as an active manual row. TASK_315A may return it as a removed manual warning/count or inactive removed metadata if a value model is introduced.

Do not match sample-preparation rows by regenerated `confirmed_group_id`.

### Inactive Removed Rows

TASK_315A only creates in-memory inactive removed rows.

Rules:

- inactive rows are not included in `active_rows`;
- inactive rows preserve previous edited values for review;
- inactive rows carry `inactive_reason="removed_from_matrix"`;
- inactive rows do not participate in Fee amount totals or active-row totals in
  TASK_315A tests, but they must participate in the rebase summary
  `removed_count`.

Later TASK_315D will decide UI display and API serialization details.

## File-Level Plan

### Add

- `backend/application/matrix_fee_draft_rebase_service.py`
  - rebase key helper
  - source/target/inactive/summary/result value models
  - `MatrixFeeDraftRebaseService.rebase(...)`
  - pure helper functions for normalization and editable-value copying

- `tests/unit/test_matrix_fee_draft_rebase_service.py`
  - unit tests for matching, added rows, removed rows, stable-lineage text edits, row-signature fallback, manual rows, and inactive-row separation

### Avoid

- no repository files
- no migration files
- no FastAPI route files
- no frontend files
- no task selector or Project Folder files

## Test Plan

Unit tests:

- `test_matching_rows_preserve_edited_fee_values`
- `test_text_only_matrix_edit_preserves_values_with_source_snapshot_id`
- `test_text_only_matrix_edit_preserves_values_with_draft_row_id`
- `test_lineage_less_signature_change_becomes_removed_and_added`
- `test_added_group_or_step_uses_default_fee_row`
- `test_removed_group_or_step_becomes_inactive_removed_row`
- `test_removed_rows_are_not_returned_as_active_rows`
- `test_report_preparation_manual_row_is_preserved_globally`
- `test_sample_preparation_manual_row_matches_by_group_key_or_label`
- `test_removed_group_sample_preparation_is_not_active`
- `test_rebase_summary_counts_preserved_added_removed`

Validation command:

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

If shared Fee value types are touched:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_confirmed_fee_version_service.py -q
```

## Risks And Controls

- Risk: copying too much from source rows could preserve old confirmed ids. Control: explicit editable-field copy helper and tests asserting target lineage survives.
- Risk: row-signature fallback could over-preserve unrelated rows. Control: stable lineage wins; fallback is only for lineage-less rows and signature changes are allowed to become remove/add.
- Risk: manual sample rows could match by regenerated group ids. Control: tests require group key/label matching.
- Risk: TASK_315A grows into persistence or UI work. Control: hard out-of-scope list and file-level avoid list.

## Review Checklist

- [ ] Does the service remain pure with no repository/API/frontend dependency?
- [ ] Are regenerated confirmed ids excluded from cross-version keys?
- [ ] Are editable fields copied explicitly?
- [ ] Are inactive rows separate from active rows?
- [ ] Are manual rows handled by the V1 rules?
- [ ] Do tests cover preserved, added, removed, text-edit, lineage-less fallback, and manual-row behavior?

## Stop Point

TASK_315A is complete. Validation: `py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q` (`11 passed`); `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_confirmed_fee_version_service.py -q` (`20 passed`). Stop here and do not implement TASK_315B until it has its own task file, plan, review, and separate explicit approval.
