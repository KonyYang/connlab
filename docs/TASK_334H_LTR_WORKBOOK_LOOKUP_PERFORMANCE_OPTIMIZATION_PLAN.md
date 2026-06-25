# TASK_334H LTR Workbook Lookup Performance Optimization Plan

Status: Proposed
Created: 2026-06-25
Task: `TASK_334H_LTR_WORKBOOK_LOOKUP_PERFORMANCE_OPTIMIZATION`

## Protocol Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task board stop point: `TASK_334G_APPLICATION_FORM_WORD_WRITE_BACK_REUSE_AND_HOTPATH_OPTIMIZATION` is complete and the board requires separate explicit approval before the next task.
- Why this plan is allowed now: the user explicitly requested the previously discussed three-tier LTR lookup optimization, but project protocol requires a task file and reviewable plan before implementation.
- Implementation status: no backend or frontend implementation is authorized by this plan until the user explicitly approves `TASK_334H`.

## Objective

Reduce the time spent finding the LTR workbook row and opening the workbook read-only from the Workbench LTR update preview surface, without weakening exact DL matching, duplicate protection, no-op protection, or read-only workbook safety.

## Current Behavior To Verify During Implementation

Known relevant files:

- `backend/application/ltr_workbook_basic_information_sync_service.py`
  - Builds preview data for Workbench LTR update.
  - Resolves exact DL row.
  - Commits updates after preview validation.
  - Opens the workbook read-only at the exact DL cell.
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
  - Owns Excel COM workbook access.
  - Already exposes a DL-column-oriented read path that should be reused where safe.
  - Owns read-only workbook open behavior.
- Frontend should need little or no change unless labels/loading states are adjusted:
  - `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`

The suspected slow path is full-sheet data retrieval before row lookup. The implementation must confirm this in code before editing.

## Tier 1 - Fast Preview Lookup

Goal: make preview locate by DL column first, then read only the target row.

Implementation steps:

- [ ] Add or reuse an application helper such as `_locate_exact_ltr_number_fast(session, sheet_name, ltr_number)`.
- [ ] Use the workbook gateway/session DL-column reader to read only the DL column for the annual sheet.
- [ ] Preserve exact-match rules:
  - [ ] no substring match
  - [ ] no prefix match
  - [ ] duplicate exact rows block
  - [ ] missing exact row blocks
- [ ] Add or reuse a gateway/session method to read one target row, e.g. `A{row}:Q{row}`, after the row number is known.
- [ ] Build comparison values from that single target row plus Basic Information pending write values.
- [ ] Keep field/column mapping centralized so current workbook values and pending values are compared against the same business fields.

Tests:

- [ ] Unit test that preview can resolve a target row using only the DL-column reader and target-row reader in a fake session.
- [ ] Unit test that prefix rows do not match.
- [ ] Unit test that duplicate exact rows block.
- [ ] Unit test that comparison values still include the expected LTR fields in workbook column order.

Validation:

- [ ] `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q`
- [ ] `py -m pytest tests/integration/test_ltr_workbook_basic_information_sync_api.py -q`

## Tier 2 - Lightweight Read-Only Open

Goal: make `Open read-only workbook` avoid rebuilding full comparison preview.

Implementation steps:

- [ ] Update the read-only open application path to use the same fast exact-DL locator as Tier 1.
- [ ] Do not build full old/new comparison values for read-only open.
- [ ] Before opening/selecting, validate that the resolved row still has an exact DL value in the DL column.
- [ ] Preserve existing read-only open behavior:
  - [ ] read-only workbook open
  - [ ] configured password/read-only prompt compatibility
  - [ ] visible Excel session for the operator
  - [ ] clear filters and unhide rows/columns for inspection
  - [ ] select the exact DL cell

Tests:

- [ ] Unit test read-only open uses fast exact-DL location without requesting full preview data.
- [ ] Unit test stale/mismatched row validation blocks open.
- [ ] Keep existing read-only open gateway tests.

Validation:

- [ ] `py -m pytest tests/unit/test_ltr_workbook_readonly_open_gateway.py -q`
- [ ] `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q`
- [ ] Manual smoke: click `LTR update preview`, then open workbook read-only and confirm Excel selects the exact DL cell.

## Tier 3 - Guarded Row-Locator Cache

Goal: avoid repeated DL-column scans for the same unchanged workbook and DL number.

Implementation steps:

- [ ] Add a small bounded in-memory locator cache for `(workbook_path, sheet_name, ltr_number)`.
- [ ] Store row number plus workbook signature:
  - [ ] resolved absolute workbook path
  - [ ] file size
  - [ ] last modified timestamp
- [ ] Store whether the cached row was produced by a completed exact-DL uniqueness scan for that same workbook signature.
- [ ] Use cache only when the workbook signature still matches.
- [ ] Before using a cached row for preview/open/commit, validate the DL cell value in the target row exactly equals the requested LTR number.
- [ ] Cache use must preserve duplicate protection:
  - [ ] a cache hit is valid only when the same workbook signature already had a completed exact-DL uniqueness scan
  - [ ] commit must either use that same-signature uniqueness result or rescan the DL column before writing
  - [ ] duplicate exact DL rows must block preview/update/open even when a cached target row exists
- [ ] On signature mismatch, stale row mismatch, missing uniqueness evidence, duplicate detection requirement, or any validation failure, rescan with the Tier 1 fast locator.
- [ ] Keep the cache private to the backend process and do not persist it.

Tests:

- [ ] Cache hit avoids DL-column scan when workbook signature matches.
- [ ] Cache miss occurs when signature changes.
- [ ] Cache stale-row validation falls back or blocks safely.
- [ ] Duplicate exact rows still block even when cache exists for an older workbook signature.
- [ ] A cache hit without same-signature uniqueness evidence is not used for commit.

Validation:

- [ ] Run the Tier 1 and Tier 2 validation commands again.
- [ ] Record objective performance evidence:
  - [ ] fake gateway/session assertions prove preview does not request full `A:Q` annual-sheet data
  - [ ] preview reads only the DL column and target row in unit tests
  - [ ] manual or service-level timing note captures preview/open elapsed time before and after the optimization, or explains why before/after timing is not available
- [ ] Manual smoke: run preview twice against the same unchanged workbook and verify the second lookup is faster or at least does not regress.

## UX And Copy Impact

No major frontend redesign is expected. If any UI copy changes are needed, keep them small and aligned with the current Workbench card:

- `LTR update preview` remains the primary action label.
- The comparison table remains focused on `Field`, `LTR workbook`, and `LTR of Basic Info`.
- Do not reintroduce a permanent Basic Information/LTR summary card.

## Risks

- Excel COM range shape differences can break row/column readers when a range has one row or one column.
- Duplicate detection still requires scanning the full DL column; do not optimize by stopping at the first match.
- Cache staleness could cause wrong-row operations if exact D-cell validation is skipped.
- Shared public-drive workbook latency may still dominate even after row lookup optimization.
- Read-only open has Office prompt/password behavior; preserve the TASK_334F safety path.

## Acceptance Criteria

- Preview lookup uses DL-column scan plus single-row read, not full `A:Q` annual sheet scan.
- Read-only open does not build full preview/comparison data.
- Optional cache is guarded by workbook signature, same-signature exact-DL uniqueness evidence, and exact D-cell validation.
- Exact DL matching, duplicate blocking, no-op blocking, and read-only open safety remain intact.
- Completion notes include objective performance evidence: targeted test assertions for no full `A:Q` lookup and a manual/service-level preview/open timing note where feasible.
- Relevant backend tests pass.
- If frontend changes are made, targeted frontend tests and build pass.

## Implementation Stop Point

After implementation and validation, update `docs/task_board.md` with completion notes and stop. Do not start any next task.
