# Precheck Lower Panels Editable Requested Testing Plan

Last updated: 2026-05-04

## 1. Anti-Skip Status

- Current phase: `Phase 10A - Intake Entry Completion`
- Active implementation task: none
- Related completed scope: `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE`, `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION`, `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION`
- Why this change is allowed as a plan: this document describes a focused correction to the already implemented Precheck edit surface. It does not start `TASK_091`, does not add future-scope workflow, and does not change LTR/folder behavior.

## 2. Problem Summary

The current Precheck lower panel has four issues:

1. `Confidential test or samples?*` and `Can testing be subcontracted?*` should not occupy a tall left column. They should sit in one horizontal consent row, with the two questions side by side.
2. The Yes/No radio buttons are `readOnly`, so the operator cannot correct parsed values.
3. `Description of Requested Testing` is hardcoded as three rows and one parsed value. It does not preserve the application-form two-column table:
   - `Tests to be Performed`
   - `Applicable Specifications`
4. `+ Add Row`, table cells, and `Additional Information` are not editable, even though this page is named `Key Information Edit & Confirm` and the Save Draft flow already exists.

## 3. Current Code Reality

Primary frontend file:

```text
frontend/src/features/precheck/PrecheckLowerPanels.tsx
```

Current behavior:

- `RadioLine` renders `input checked={...} readOnly`.
- `RequestedTestingPanel` renders fixed table rows:
  - `Qualification test`
  - `Defect/Performance test`
  - `Environmental test`
- `+ Add Row` has no handler.
- `AdditionalInfoPanel` renders `<textarea value={value} readOnly ... />`.

The page already has an edit/save flow:

```text
frontend/src/pages/IntakeCaseReviewPage.tsx
```

- `fieldValues` stores editable field values.
- `sampleRows` stores editable sample rows.
- `handleSaveFields()` calls `updateIntakeCaseReviewFields(...)`.
- Save Draft is enabled by `draftChanged`.

Backend currently allows manual overrides for:

```text
requested_testing
confidential
subcontract
additional_information
```

But it does not yet expose or persist structured requested-testing rows for Precheck review.

## 4. Desired UX

### Overall Lower-Panel Layout

Do not keep the three lower panels as parallel columns.

Use three vertical sections instead:

```text
[ Confidential test or samples?* Yes/No ] [ Can testing be subcontracted?* Yes/No ]

Description of Requested Testing
[ full-width two-column requested-testing table ]

Additional Information
[ full-width editable text area ]
```

This matches the current Precheck direction shown in the screenshot: the requested-testing table and Additional Information should read as full-width application-form sections, not cramped columns.

### Consent Row

Render `Confidential test or samples?*` and `Can testing be subcontracted?*` as two compact editable controls in the same row.

Recommended layout:

```text
[ Confidential test or samples?*      Yes  No ]  [ Can testing be subcontracted?*      Yes  No ]
```

Rules:

- Radio buttons must be editable before project confirmation.
- When `savingFields` is true or `activeCase.confirmed_project_id` exists, controls are disabled.
- Values should be normalized as `"Yes"` or `"No"` in `fieldValues`.
- The row must not clip the `Yes` / `No` controls at 14-inch laptop widths.
- On narrow screens, the two controls may stack vertically.

### Requested Testing

Render a full-width application-form-style editable table with two columns. It should visually match the table shown in the latest screenshot:

```text
Description of Requested Testing

| Tests to be Performed | Applicable Specifications |
| ...                   | ...                       |
```

Controls:

- Each table cell is editable.
- `+ Add Row` appends a blank row.
- Add an `Actions` column matching the `Test Sample Information` table pattern shown in the reference screenshot.
- Each requested-testing row should support row actions:
  - Edit/focus the row
  - Copy/duplicate the row
  - Delete the row
- Do not keep hardcoded default rows like `Qualification test`, `Defect/Performance test`, or `Environmental test`.
- Do not render a blank operation column. If the `Actions` column exists, it must contain visible icon buttons.
- Default cell height should be close to normal table rows. Inputs may grow for long text, but they should not look like oversized cards.

### Additional Information

Render as editable textarea:

```text
Additional Information
[ editable textarea ]
```

Rules:

- Textarea writes to `fieldValues.additional_information`.
- Save Draft persists it through the existing review-fields API.
- It should be a full-width row below requested testing, not a right-side parallel panel.
- Placeholder remains:

```text
No additional information extracted from the selected application form.
```

## 5. Data Contract Decision

To fully preserve application-form shape, do not parse the requested-testing table from a flattened string in the frontend.

Add structured requested-testing rows to draft data:

```json
"requested_testing_rows": [
  {
    "test_to_be_performed": "...",
    "applicable_specification": "..."
  }
]
```

Keep the existing flattened field:

```json
"requested_testing": "..."
```

Reason:

- Existing precheck blocker checks and downstream project confirmation already expect `requested_testing`.
- Structured rows are needed only for the editable Precheck table and future better downstream mapping.

When rows are edited, also update flattened `requested_testing` as a compatibility value by joining non-empty `test_to_be_performed` values with `\n`.

## 6. Backend Implementation Steps

### Step 1: Include Parser Rows In Draft Fields

File:

```text
backend/application/intake_form_selection_service.py
```

In the function that maps `ParsedApplicationForm` to `parsed_fields`, add:

```python
"requested_testing_rows": [
    {
        "test_to_be_performed": self._clean(row.test_to_be_performed),
        "applicable_specification": self._clean(row.applicable_specification),
    }
    for row in parsed.requested_testing_rows
],
```

Keep:

```python
"requested_testing": self._clean(parsed.requested_testing_description)
```

### Step 2: Allow Structured Rows As A Manual Override

File:

```text
backend/application/intake_case_review_service.py
```

Add `"requested_testing_rows"` to `_editable_fields`.

Add a normalizer, similar to `_normalized_sample_rows`, for rows:

```python
def _normalized_requested_testing_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized_rows = []
    for row in rows:
        normalized_row = {
            "test_to_be_performed": str(row.get("test_to_be_performed", "")).strip(),
            "applicable_specification": str(row.get("applicable_specification", "")).strip(),
        }
        if any(normalized_row.values()):
            normalized_rows.append(normalized_row)
    return normalized_rows
```

In `update_case_fields()`:

- Handle `requested_testing_rows` specially.
- Store normalized rows in `overrides["requested_testing_rows"]`.
- Also set `overrides["requested_testing"]` to a newline-joined string of non-empty `test_to_be_performed` values unless the caller explicitly provides `requested_testing`.

This preserves current SECTION 1 required-field checks.

### Step 3: Keep API Shape Compatible

File:

```text
frontend/src/api/client.ts
```

Update `UpdateIntakeCaseReviewFieldsInput`:

```ts
requested_testing_rows?: Record<string, string>[];
```

Better typed version:

```ts
export type RequestedTestingRowInput = {
  test_to_be_performed: string;
  applicable_specification: string;
};
```

Then:

```ts
export type UpdateIntakeCaseReviewFieldsInput = {
  fields: Record<string, string | null>;
  sample_rows?: Record<string, string>[];
  requested_testing_rows?: RequestedTestingRowInput[];
};
```

If you prefer to avoid changing the endpoint body, you can send `requested_testing_rows` inside `fields` because backend accepts arbitrary JSON values internally. However, an explicit top-level field is cleaner and easier to test.

## 7. Frontend Implementation Steps

### Step 1: Add Row Types And Helpers

File:

```text
frontend/src/features/precheck/precheckFieldConfig.ts
```

Add:

```ts
export type PrecheckRequestedTestingRow = {
  test_to_be_performed: string;
  applicable_specification: string;
};

export const PRECHECK_REQUESTED_TESTING_COLUMNS = [
  { key: "test_to_be_performed", label: "Tests to be Performed" },
  { key: "applicable_specification", label: "Applicable Specifications" },
] as const;

export function emptyPrecheckRequestedTestingRow(): PrecheckRequestedTestingRow {
  return {
    test_to_be_performed: "",
    applicable_specification: "",
  };
}
```

### Step 2: Add Selectors For Requested Testing Rows

File:

```text
frontend/src/features/precheck/precheckReviewSelectors.ts
```

Add:

```ts
export function normalizedRequestedTestingRows(raw: unknown): PrecheckRequestedTestingRow[] {
  if (!Array.isArray(raw)) {
    return [emptyPrecheckRequestedTestingRow()];
  }
  const rows = raw
    .map((row) => ({
      test_to_be_performed: String((row as Record<string, unknown>).test_to_be_performed ?? ""),
      applicable_specification: String((row as Record<string, unknown>).applicable_specification ?? ""),
    }))
    .filter((row) => row.test_to_be_performed || row.applicable_specification);
  return rows.length > 0 ? rows : [emptyPrecheckRequestedTestingRow()];
}

export function requestedTestingText(rows: PrecheckRequestedTestingRow[]): string {
  return rows
    .map((row) => row.test_to_be_performed.trim())
    .filter(Boolean)
    .join("\n");
}
```

### Step 3: Add State In The Route Coordinator

File:

```text
frontend/src/pages/IntakeCaseReviewPage.tsx
```

Import:

```ts
emptyPrecheckRequestedTestingRow,
type PrecheckRequestedTestingRow
```

Add state:

```ts
const [requestedTestingRows, setRequestedTestingRows] = useState<PrecheckRequestedTestingRow[]>([
  emptyPrecheckRequestedTestingRow(),
]);
```

When `activeCase` changes:

```ts
setRequestedTestingRows(
  normalizedRequestedTestingRows(activeCase.parsed_fields?.requested_testing_rows)
);
```

If `parsed_fields` is not exposed directly in frontend DTO, use the existing `activeCase.fields` source only as fallback and update the API serializer to expose structured rows. The preferred fix is to expose rows in the existing case DTO.

Update `draftChanged`:

```ts
const requestedTestingRowsChanged = activeCase
  ? JSON.stringify(requestedTestingRows) !== JSON.stringify(normalizedRequestedTestingRows(...source...))
  : false;

const draftChanged = fieldValuesChanged || sampleRowsChanged || requestedTestingRowsChanged;
```

When saving:

```ts
await updateIntakeCaseReviewFields(activeCase.case_id, {
  fields: {
    ...fieldValues,
    requested_testing: requestedTestingText(requestedTestingRows),
  },
  sample_rows: sampleRows,
  requested_testing_rows: requestedTestingRows,
});
```

### Step 4: Make `PrecheckLowerPanels` Controlled And Editable

File:

```text
frontend/src/features/precheck/PrecheckLowerPanels.tsx
```

Replace props with controlled callbacks:

```ts
type PrecheckLowerPanelsProps = {
  additionalInformation: string;
  confidential: string;
  disabled?: boolean;
  requestedTestingRows: PrecheckRequestedTestingRow[];
  subcontract: string;
  onAdditionalInformationChange: (value: string) => void;
  onConfidentialChange: (value: string) => void;
  onRequestedTestingRowAdd: () => void;
  onRequestedTestingRowChange: (
    rowIndex: number,
    key: keyof PrecheckRequestedTestingRow,
    value: string,
  ) => void;
  onRequestedTestingRowCopy: (rowIndex: number) => void;
  onRequestedTestingRowDelete: (rowIndex: number) => void;
  onRequestedTestingRowEdit: (rowIndex: number) => void;
  onSubcontractChange: (value: string) => void;
};
```

Recommended component structure:

```tsx
return (
  <div className="precheck-lower-grid">
    <section className="precheck-consent-row">
      <RadioLine ... />
      <RadioLine ... />
    </section>
    <RequestedTestingPanel ... />
    <AdditionalInfoPanel ... />
  </div>
);
```

Consent radio:

```tsx
<input
  checked={value === "Yes"}
  disabled={disabled}
  name={name}
  type="radio"
  onChange={() => onChange("Yes")}
/>
```

Requested-testing table:

- Render `PRECHECK_REQUESTED_TESTING_COLUMNS`.
- Use `<textarea>` or `<input>` inside each cell.
- Prefer compact `<textarea rows={1}>` or an auto-height textarea for both columns. Chinese descriptions can be long, but the default row should still look like a table row, not a card.
- Use two data columns plus one action column:
  - `Tests to be Performed`
  - `Applicable Specifications`
  - `Actions`
- Add Row button calls `onRequestedTestingRowAdd`.
- The action column should mirror the sample table actions:
  - edit/focus icon calls `onRequestedTestingRowEdit(rowIndex)`
  - copy icon calls `onRequestedTestingRowCopy(rowIndex)`
  - trash icon calls `onRequestedTestingRowDelete(rowIndex)`
- Disable delete when only one row remains.
- Use the existing icon/button style used by `PrecheckSampleTable` where possible. Do not invent a second row-action visual language.

Additional information:

```tsx
<textarea
  disabled={disabled}
  value={additionalInformation}
  placeholder="No additional information extracted from the selected application form."
  onChange={(event) => onAdditionalInformationChange(event.target.value)}
/>
```

### Step 5: Wire It From `IntakeCaseReviewPage`

Replace current call:

```tsx
<PrecheckLowerPanels
  additionalInformation={...}
  confidential={...}
  requestedTesting={...}
  subcontract={...}
/>
```

With:

```tsx
<PrecheckLowerPanels
  additionalInformation={fieldValues.additional_information ?? ""}
  confidential={fieldValues.confidential ?? ""}
  disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
  requestedTestingRows={requestedTestingRows}
  subcontract={fieldValues.subcontract ?? ""}
  onAdditionalInformationChange={(value) => updateFieldValue("additional_information", value)}
  onConfidentialChange={(value) => updateFieldValue("confidential", value)}
  onRequestedTestingRowAdd={() => setRequestedTestingRows((current) => [...current, emptyPrecheckRequestedTestingRow()])}
  onRequestedTestingRowCopy={(rowIndex) => ...}
  onRequestedTestingRowChange={(rowIndex, key, value) => ...}
  onRequestedTestingRowDelete={(rowIndex) => ...}
  onRequestedTestingRowEdit={(rowIndex) => ...}
  onSubcontractChange={(value) => updateFieldValue("subcontract", value)}
/>
```

Create a small helper in the page to avoid repeating message resets:

```ts
function updateFieldValue(key: string, value: string): void {
  setFieldValues((current) => ({ ...current, [key]: value }));
  setFieldSaveMessage(null);
  setFieldSaveError(null);
}
```

Use that helper for `PrecheckFieldGrid` too if you want a small cleanup.

## 8. CSS Implementation Steps

File:

```text
frontend/src/intake-case-review.css
```

### Lower Grid Layout

Replace the current three-column parallel layout with vertical sections:

```css
.precheck-lower-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-top: 10px;
}
```

### Consent Row

Make the two yes/no questions share one row:

```css
.precheck-consent-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 12px;
  align-items: stretch;
  padding: 14px;
  border: 1px solid #d8e4f5;
  border-radius: 8px;
  background: #fbfdff;
}

.radio-line {
  display: grid;
  grid-template-columns: minmax(0, 1fr) max-content max-content;
  gap: 12px;
  align-items: center;
  margin-top: 0;
}
```

On narrow screens:

```css
@media (max-width: 900px) {
  .precheck-consent-row {
    grid-template-columns: 1fr;
  }
}
```

### Requested Testing Table

Add editable table styles:

```css
.requested-testing-panel {
  display: grid;
  gap: 10px;
  padding: 0;
  border: 0;
  background: transparent;
}

.requested-testing-edit-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #d8e4f5;
  border-radius: 8px;
  overflow: hidden;
  font-size: 12px;
}

.requested-testing-edit-table th:first-child,
.requested-testing-edit-table td:first-child {
  width: 58%;
}

.requested-testing-edit-table th:nth-child(2),
.requested-testing-edit-table td:nth-child(2) {
  width: 42%;
}

.requested-testing-edit-table th:last-child,
.requested-testing-edit-table td:last-child {
  width: 112px;
  text-align: center;
}

.requested-testing-edit-table th {
  background: #f0f4fa;
  color: var(--precheck-label-ink);
  font-size: 11px;
  font-weight: 800;
  text-align: left;
}

.requested-testing-edit-table th,
.requested-testing-edit-table td {
  padding: 8px 10px;
  border-right: 1px solid #d8e4f5;
  border-bottom: 1px solid #d8e4f5;
}

.requested-testing-cell-input {
  width: 100%;
  min-height: 34px;
  padding: 6px 8px;
  resize: vertical;
  border: 1px solid transparent;
  background: transparent;
  color: var(--precheck-data-ink);
  font: inherit;
  font-weight: var(--precheck-data-weight);
}

.requested-testing-cell-input:focus {
  border-color: #0b61e8;
  border-radius: 6px;
  outline: 3px solid #d9e8ff;
  background: #fbfdff;
}

.requested-testing-row-actions {
  display: inline-grid;
  grid-auto-flow: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
}
```

### Additional Information Layout

Make Additional Information full width below the requested-testing table:

```css
.precheck-additional-panel {
  display: grid;
  gap: 10px;
  padding: 0;
  border: 0;
  background: transparent;
}

.precheck-additional-panel textarea {
  min-height: 118px;
}
```

## 9. Tests To Update

### Frontend Static Tests

File:

```text
tests/unit/test_frontend_shell_files.py
```

Assert:

- `PrecheckLowerPanels` has callback props.
- Radio inputs no longer use `readOnly`.
- `onChange={() => onChange("Yes")}` and `"No"` exist.
- `requestedTestingRows` exists.
- `onRequestedTestingRowAdd` exists.
- `onRequestedTestingRowEdit` exists.
- `onRequestedTestingRowCopy` exists.
- `onRequestedTestingRowChange` exists.
- `onRequestedTestingRowDelete` exists.
- `onAdditionalInformationChange` exists.
- `textarea value={additionalInformation}` is not `readOnly`.
- New CSS classes exist:
  - `.precheck-consent-row`
  - `.requested-testing-edit-table`
  - `.requested-testing-cell-input`
  - `.requested-testing-row-actions`
  - `.precheck-additional-panel`
- Assert the old parallel lower-grid columns are not retained:
  - no `grid-template-columns: 0.82fr 0.92fr 1.8fr`
  - requested-testing action column must contain visible edit/copy/delete icon buttons

### Backend Unit Tests

File:

```text
tests/unit/test_intake_case_review_service.py
```

Add a test:

```python
def test_review_service_updates_requested_testing_rows_as_manual_overrides(...):
```

Assert:

- `requested_testing_rows` persists into `manual_overrides_json`.
- `requested_testing` compatibility value is updated from row first-column text.
- refreshed review no longer reports `requested_testing` missing when rows have a test value.

### Integration Test

File:

```text
tests/integration/test_manual_intake_api.py`
```

Add or extend PATCH `/review-fields` test with:

```json
"requested_testing_rows": [
  {
    "test_to_be_performed": "Qualification test",
    "applicable_specification": "GS-12-2652-22"
  }
]
```

Assert response preserves/accepts update and draft override JSON contains the row.

## 10. Validation Commands

Run targeted backend/frontend tests:

```powershell
py -m pytest tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q
```

Run parser/preview regression because requested-testing structure was recently changed:

```powershell
py -m pytest tests\unit\test_application_form_parser.py tests\unit\test_intake_asset_preview_service.py -q
```

Run frontend build:

```powershell
cd frontend
npm run build
```

Optional full regression:

```powershell
py -m pytest -q
```

## 11. Manual Smoke Checklist

Use a real application form with:

- Confidential = No
- Subcontracted = Yes
- Requested-testing two-column table
- Additional Information text

Verify:

1. Precheck shows `Confidential test or samples?*` and `Can testing be subcontracted?*` side by side in one consent row on wide screens.
2. Selecting Yes/No changes the radio state immediately.
3. Save Draft becomes enabled after radio changes.
4. Requested-testing appears as a full-width section below the consent row.
5. Requested-testing table shows the parsed two columns from the application form: `Tests to be Performed` and `Applicable Specifications`.
6. Editing either table column enables Save Draft.
7. `+ Add Row` appends a blank editable row.
8. Requested-testing `Actions` column shows edit/copy/delete icons like `Test Sample Information`.
9. Copy duplicates the selected requested-testing row.
10. Delete removes the selected requested-testing row while keeping at least one row.
11. Additional Information appears as a full-width editable section below requested testing.
12. Save Draft persists all edits and refreshes blockers.
13. Confirm remains blocked if all requested-testing rows are blank.
14. Confirm becomes allowed again when required fields are restored.
15. Already confirmed cases disable all lower-panel controls.

## 12. Documentation Updates After Implementation

Update:

```text
docs/current_session_state.md
tasks/TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md
```

Suggested note:

```markdown
- Precheck lower panels now support editing Confidential/Subcontracted Yes-No values, requested-testing two-column rows, and Additional Information. Requested-testing rows are persisted as structured draft overrides while maintaining the existing flattened `requested_testing` compatibility value for precheck blockers and downstream confirmation.
```

Do not update `docs/task_board.md` unless this is promoted to an approved controlled task. If it remains a narrow post-completion polish/fix, leave the active task as none and keep `TASK_091` blocked until separately approved.
