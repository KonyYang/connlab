# TASK_333C LTR Workbook On-Demand Preview and Exact DL Match Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

No implementation task is active after `TASK_333B_LTR_WORKBOOK_UPDATE_PREVIEW_OLD_NEW_COMPARISON` completion.

`TASK_333C_LTR_WORKBOOK_ON_DEMAND_PREVIEW_AND_EXACT_DL_MATCH` is a proposed task requested by the user and established by approval to create the task/plan. It must not be implemented until the user explicitly approves implementation and the task board marks it as active.

## User Problem

The current Workbench `LTR Information` card still behaves like a Basic Information summary with an update workflow attached to it.

The desired behavior is narrower and safer:

- show the LTR workbook update function as the main purpose of the card
- avoid showing a static field summary that duplicates data from Basic Information
- only read the public-drive workbook when the operator explicitly requests a preview
- compare the current workbook row with the Basic Information-derived write values
- make changed fields stand out before the operator confirms the write
- prevent wrong-row updates by requiring an exact DL match

## Product Decision

The `LTR Information` card should become an on-demand workbook synchronization surface.

Recommended card states:

1. **Unconfirmed Basic Information**
   - Card title: `LTR Information`
   - Action is visible but disabled.
   - Copy is short: confirm Basic Information before updating the LTR workbook.

2. **Confirmed Basic Information, no preview loaded**
   - Card title: `LTR Information`
   - Primary action: `Preview LTR update`
   - No current workbook fields are shown yet.

3. **Preview loaded**
   - Show workbook path and target row metadata.
   - Show current workbook value vs value to write.
   - Highlight rows with differences.
   - If no differences exist, show an up-to-date state and disable commit.
   - If blockers exist, show blockers and no commit.

4. **Commit completed**
   - Show concise success copy without exposing backup paths.
   - Leave the action available for a fresh preview.

This keeps the UI aligned with ConnLab's principle: preview before write, and action only when the operator asks for it.

## Exact DL Matching Rule

The LTR workbook target row must be found by exact DL number equality.

Allowed normalization:

- convert missing cell values to empty text
- replace non-breaking spaces with normal spaces
- trim leading/trailing whitespace

Forbidden matching:

- prefix matching
- substring matching
- case-insensitive fuzzy matching that could collapse distinct records
- ignoring suffix letters or punctuation

Examples:

```text
Target DL: DL-2026-05-011

Matches:
- "DL-2026-05-011"
- " DL-2026-05-011 "

Does not match:
- "DL-2026-05-011A"
- "DL-2026-05-011-1"
- "DL-2026-05-011 / old"
```

If the exact match count is:

- `0`: block preview with a row-not-found message
- `1`: preview that row
- `>1`: block preview with a duplicate exact-DL message

Commit must repeat the exact match check and ensure the matched row is still the same row that was previewed.

## Backend Design

### Files To Inspect/Modify

- `backend/application/ltr_workbook_basic_information_sync_service.py`
- existing LTR workbook transaction/session gateway under `backend/infrastructure/`
- LTR workbook sync API route/DTO module if response fields are added
- existing LTR workbook sync unit and API tests

### Preview Flow

Use the existing read-only preview transaction.

Planned flow:

1. Load the latest registered LTR for the project.
2. Load the latest confirmed Basic Information snapshot.
3. Open the configured LTR workbook read-only.
4. Find the target workbook row using exact DL match only.
5. Build pending write values from the same Basic Information -> LTR mapping used by commit.
6. Read current workbook row values from the target row using the same business-field mapping.
7. Return comparison rows with a `changed` flag.

Suggested comparison DTO addition:

```python
@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationSyncComparisonValue:
    field_name: str
    label: str
    current_value: object | None
    pending_value: object | None
    changed: bool
```

If the existing API response uses Pydantic models in the route layer, mirror the same `changed: bool` field there.

### Comparison Normalization

Compute `changed` from normalized business display values, not raw Python or Excel object identity.

Use the same normalization for `current_value` and `pending_value` before comparing:

- Treat `None`, empty string, and whitespace-only text as the same blank value.
- Replace non-breaking spaces with normal spaces, trim leading/trailing whitespace, and collapse repeated internal whitespace for text fields.
- Compare text case-sensitively by default because LTR workbook values are business-visible identifiers; do not silently lower-case DL numbers, names, part numbers, or remarks.
- Compare numeric values by their business display string when the workbook field is shown as text to the operator, so `12531` and `"12531"` do not become a false difference.
- Compare date values by canonical `YYYY/MM/DD` display date when a field is a date, so Excel date objects and already-formatted strings do not become a false difference.
- Preserve the original display values in the response for the table, but base the `changed` flag on the normalized values.

### No-Difference Preview

When all comparison rows have `changed == False`:

- preview status can remain `ready`
- response should include `has_differences=False` or derive it on the frontend from comparison rows
- frontend should disable commit and show `LTR workbook is already up to date.`

Prefer deriving from comparison rows unless the backend already has a clean preview-level field.

### Commit Flow

Keep the existing version/source-signature confirmation from `TASK_333`.

Before writing:

1. Re-open the workbook in the write transaction.
2. Repeat exact DL lookup.
3. Block if no row or duplicate rows exist.
4. Block if the exact row number is different from the preview target row.
5. Rebuild pending write values from the confirmed Basic Information snapshot.
6. Write only that row.

This avoids accidentally overwriting a related but different DL record.

## Frontend Design

### Files To Inspect/Modify

- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/api/client.ts`
- related stylesheet where `runtime-console-basic-information` / `runtime-console-ltr-sync-*` classes live

### Card Layout

Before preview, remove the always-visible summary list from the `LTR Information` card.

Keep:

- title
- short confirmed/unconfirmed guidance
- visible action button
- preview result area after the operator clicks the action

Basic Information viewing must remain available outside this card:

- Preserve the existing Workbench top `Basic Information` navigation button as the primary entry to the confirmed Basic Information page.
- Do not keep a secondary `View` action inside the `LTR Information` card unless implementation proves the top Workbench entry is unavailable.
- The `LTR Information` card should stay focused on workbook preview/update only.

Suggested button naming:

- No preview loaded: `Preview LTR update`
- Preview loading: `Previewing...`
- Ready preview with differences: `Confirm update`
- Ready preview without differences: no commit action, show up-to-date text

### Difference Highlighting

Render the comparison rows in LTR workbook business-column order.

For changed rows:

- apply a visible row or cell style such as `is-changed`
- do not rely on color alone; use a subtle `Changed` text/tag if the current design has enough room
- keep labels readable on small widths

The preview table should continue to avoid Excel A-Q column letters.

### Error Copy

Add operator-facing mapping for exact-match blockers:

- missing exact row: `No exact LTR workbook row was found for this DL number.`
- duplicate exact rows: `Multiple exact LTR workbook rows were found for this DL number. Resolve the workbook duplicates before updating.`
- stale row: `The LTR workbook row changed after preview. Refresh the preview before updating.`

Do not show raw Python tracebacks or local gateway implementation details.

## Tests

### Backend Unit/API Tests

Add or update tests for:

- exact match accepts trimmed same DL
- exact match rejects suffix rows such as `DL-2026-05-011A`
- missing exact row blocks preview
- duplicate exact rows block preview
- preview marks changed comparison rows
- preview marks no-difference state
- commit rechecks row and blocks if the previewed row is no longer the exact target

### Frontend Tests

Add or update tests for:

- card does not render the summary value list before preview
- top Workbench `Basic Information` navigation remains available after the LTR card is simplified
- preview action is visible but disabled before Basic Information confirmation
- preview action calls the API only when clicked
- changed rows are highlighted
- semantically equal blank, numeric, and date display values do not produce false changed rows
- no-difference preview disables `Confirm update`
- missing/duplicate exact-row blockers are shown with operator-facing copy

## Risks

- If exact lookup logic is currently shared with initial LTR registration, changing it carelessly could affect New Project registration. Keep `TASK_333C` changes scoped to the Workbench update sync path unless a shared helper is already clearly used only for safe exact lookup.
- If workbook row lookup only returns one pointer today, duplicate detection may require a new read-only lookup method. Add it narrowly.
- If the frontend currently couples `View` and `Update LTR` to the same summary card state, remove the summary display without breaking the separate Basic Information page entry.
- If old tests assert always-visible summary values, update them to the new product behavior.

## Validation Commands

After implementation approval:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

Run any focused LTR workbook transaction gateway tests if the gateway lookup contract changes.

## Stop Point

This plan is for review only. Stop after creating the task, plan, and task board entry. Do not implement until the user explicitly approves `TASK_333C` implementation.
