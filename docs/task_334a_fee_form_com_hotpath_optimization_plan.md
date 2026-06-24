# TASK_334A Fee Form COM Hot-Path Optimization Plan

## Summary

The Fee Form `.xls` path still uses Excel COM, which is correct for legacy `.xls` output. Real profile evidence shows the expensive part is not data building or saving the workbook; it is repeated worksheet COM round-trips.

This task narrows the fix to the Fee Form writer hot path. It does not change output format, customer feedback generation, Word Application Form write-back, UI progress, pricing rules, or Basic Information behavior.

## Current Evidence

Focused profile on project `72fbbfa290294da9a507344b68ff900f`:

| Area | Observed time |
| --- | ---: |
| `basic_fill.build` | `~21ms` |
| `fee_draft.build_draft` | `~8ms` |
| output registration | `~33ms` |
| Excel `DispatchEx` | `~2.1s` |
| Excel `Workbooks.Open` | `~1.7s` |
| `write_basic_information_identity` | `~0.34s` to `~1.08s` |
| four `_find_required_row` calls | `~2.5s` to `~3.9s` |
| one `_find_optional_row` call | `~11.9s` to `~16.2s` |
| 113 `_write_matrix_detail_row` calls | `~8.2s` to `~11.4s` |
| 113 `_set_cell_comment` calls | `~1.5s` to `~1.9s` |
| 137 `_set_formula` calls | `~1.5s` to `~2.0s` |
| `SaveAs` | `<0.1s` |

Root cause: repeated per-cell and per-row COM calls.

## Design

### 1. Add A Cached Worksheet Anchor Snapshot

Create a focused helper in `backend/infrastructure/office/fee_evaluation_anchor_snapshot.py`.

Responsibilities:

- Read a bounded worksheet region once using `Range(...).Value`.
- Normalize cell labels.
- Provide:
  - `find_required(label: str) -> int`
  - `find_optional(label: str) -> int | None`
  - `find_identity_target(aliases: tuple[str, ...], max_row: int) -> tuple[int, int] | None`
  - `cell_value(row: int, column: int) -> str`
  - `cell_formula(row: int, column: int) -> str`
- Keep fallback behavior for fake sheets and unusual COM range return shapes.

Initial region:

- Rows `1..200`
- Columns `1..9`

This keeps behavior equivalent to current scanning while turning 1,800 COM reads into one range read.

### 2. Use Snapshot In Header Writer

Modify `fee_evaluation_identity_header_writer.py`:

- Accept an optional `FeeEvaluationAnchorSnapshot`.
- Use snapshot lookup to find identity target cells.
- Preserve existing fallback if no snapshot is supplied.

### 3. Use Snapshot In Matrix Basic-Fill Writer

Modify `fee_evaluation_matrix_basic_fill_writer.py`:

- Build one snapshot at the start of `write_matrix_basic_fill`.
- Replace:
  - `_find_required_row(...)`
  - `_find_optional_row(...)`
  - `_capture_template_row(...)` value/formula reads
- Keep existing row insertion, value write, formula write, fill, border, and comment behavior.

### 4. Skip Blank Comment Operations

Current `_write_matrix_detail_row()` calls `_set_cell_comment(..., text="")` for unedited rows. On real Excel this clears comments for every generated blank-note row and costs about `1.5s` to `1.9s`.

Change:

- Do not call `_set_cell_comment` for unedited rows with blank notes.
- Keep comment clearing/writing for edited rows because edited notes are operator-authored output.
- Keep existing warning behavior when a nonblank note cannot be written.

### 5. Optional Formula Batch

After snapshot/comment fixes, rerun timing. If `_set_formula` remains material:

- Add a helper to set the Testing Fee formula range in one batch where rows are contiguous.
- Keep formulas identical: `=D{row}*F{row}*(1-H{row})+G{row}`.
- Only do this if fake-COM tests can prove formulas are equivalent and implementation remains small.

## Files

Create:

- `backend/infrastructure/office/fee_evaluation_anchor_snapshot.py`

Modify:

- `backend/infrastructure/office/fee_evaluation_identity_header_writer.py`
- `backend/infrastructure/office/fee_evaluation_matrix_basic_fill_writer.py`
- `tests/unit/test_fee_evaluation_workbook_gateway.py`

Do not modify:

- Customer Feedback generator/gateway.
- Application Form Word gateway.
- Frontend progress UI.
- Basic Information service/schema.

## Test Plan

Add or update tests in `tests/unit/test_fee_evaluation_workbook_gateway.py`:

- `test_fee_gateway_anchor_snapshot_avoids_repeated_cell_scans`
  - Fake sheet tracks cell reads and range reads.
  - Running matrix basic-fill should use one bounded range read for anchor discovery.
  - Repeated required/optional/header anchor lookup should not multiply cell reads.
- `test_fee_gateway_matrix_basic_fill_does_not_clear_blank_comments`
  - Unedited generated rows must not call fake `ClearComments`.
- `test_fee_gateway_matrix_basic_fill_preserves_edited_note_comments`
  - Edited rows with notes still call comment write and preserve warning behavior.
- Existing header placement and edited-value tests must still pass.

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
```

## Real Smoke

Use the same diagnostic style already used for TASK_334:

- Generate `tmp/fee_profile/profile_fee_form.xls`.
- Capture aggregate timings before/after.
- Expected improvement:
  - `_find_optional_row` should disappear or become near-zero snapshot lookup.
  - `_find_required_row` should disappear or become near-zero snapshot lookup.
  - blank `_set_cell_comment` calls should disappear.
  - total `write_matrix_basic_fill` should drop materially.

## Risks

- Excel COM `Range.Value` return shape can vary for one-row or one-column ranges; helper must normalize tuple/scalar shapes.
- Inserted rows can shift later anchors. The snapshot should only be used for anchors captured before row insertion. Current logic already finds all anchors before insertion except `External Cost`, so the new writer should collect all needed row indices before inserting rows.
- Formula batching can be risky with `.xls`; only implement if post-snapshot timing still justifies it.

## Completion

Implemented and validated on 2026-06-24.

Final focused profile on project `72fbbfa290294da9a507344b68ff900f`:

| Area | After TASK_334A |
| --- | ---: |
| total focused export | `~6.5s` |
| `write_matrix_basic_fill` | `~3.7s` |
| Excel `DispatchEx` | `~1.1s` |
| Excel `Workbooks.Open` | `~1.0s` |
| cached anchor snapshot | `~30ms` |
| Basic Information header write | `~46ms` |
| unedited detail block writes | `~1.0s` across 10 blocks |
| formula writes | `~347ms` |
| `SaveAs` | `~49ms` |

The original `~11.9s-16.2s` `_find_optional_row` hotspot and `~2.5s-3.9s` repeated `_find_required_row` hotspot are removed from the hot path.
