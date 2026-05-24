# Attachment Details Requested Testing Alignment Plan

Last updated: 2026-05-04

## 1. Anti-Skip Status

- Current phase: `Phase 10A - Intake Entry Completion`
- Active implementation task: none
- Related completed scope: `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION`, `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION`
- Why this change is allowed now: this is a narrow polish/fix to the already completed Intake Attachment details preview. It does not start `TASK_091`, does not add new workflow behavior, and does not introduce future-scope features.

## 2. Problem

The Intake Attachment details preview currently renders a bottom table titled `Requested Testing` with rows such as:

- `Requested Testing`
- `Send Copies To`

This mixes two different business concerns:

- The operator reviewing the application form needs to see `Description of Requested Testing` and `Additional Information`.
- `Send Copies To` is a report distribution field. It is still valid structured data for Precheck/confirmation, but it is not important in the Attachment details preview.

The Attachment details preview should align with the Precheck page mental model:

- show the requested testing description clearly
- show additional information clearly
- do not show `Send Copies To` in the attachment preview

## 3. Desired Result

For `docx_application_form` attachment previews:

1. Keep the existing unified preview header, download placeholder, key information grid, and `Test Sample Information` table.
2. Replace the generic bottom `Requested Testing` table with an application-form-shaped preview:
   - `Description of Requested Testing` renders as a full-width two-column table: `Tests to be Performed` and `Applicable Specifications`
   - `Additional Information` renders below it as a separate bordered text block using the same compact preview typography
3. If `Additional Information` is empty, show the same empty-state copy as Precheck:
   - `No additional information extracted from the selected application form.`
4. Do not render `Send Copies To` in Attachment details.
5. Do not remove or change `send_copies_recipients` from parser, persistence, Precheck, or confirmation. This field remains part of the project/precheck data flow.

## Implementation Result

- `ParsedRequestedTestingRow` preserves requested-testing table rows as `test_to_be_performed` plus `applicable_specification`.
- The parser supports real application-form structures where `Additional Information` is a heading paragraph followed by a single-cell content table.
- Attachment details now renders `Description of Requested Testing` through the same preview table component used by `Test Sample Information`.
- Additional Information renders as a separate bordered text block, not as a side-by-side card.
- Validation: `py -m pytest tests\unit\test_application_form_parser.py tests\unit\test_intake_asset_preview_service.py tests\unit\test_frontend_shell_files.py -q` = 48 passed; `py -m pytest tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py -q` = 8 passed; `npm run build` passed; `py -m pytest -q` = 293 passed.

## 4. Impact Assessment

### Low Risk

- This change is display-focused.
- It affects only the selected attachment preview for application-form Word files.
- It does not change stored draft data, project confirmation rules, or Precheck editing.

### Medium Risk

- Backend tests may currently expect a `Requested Testing` table title or row.
- Frontend static tests may need to detect the new Intake preview component and ensure the old generic display path no longer leaks `Send Copies To`.
- If the API response shape is changed too much, existing frontend table rendering may break.

### Recommended Risk Control

Keep the backend API shape stable:

- Continue returning a `PreviewTable` for requested-testing content.
- Remove only the `Send Copies To` row.
- Optionally relabel the requested-testing row to `Description of Requested Testing`.
- Let the frontend detect that table and render it through a specialized Intake preview component.

## 5. Files To Change

Primary files:

- `backend/application/intake_asset_preview_service.py`
- `frontend/src/features/intake/AttachmentPreviewPanel.tsx`
- `frontend/src/intake-inbox.css`

Tests:

- `tests/unit/test_intake_asset_preview_service.py`
- `tests/unit/test_frontend_shell_files.py`

Record updates after implementation:

- `docs/archive/historical_plans/current_session_state.md`
- `docs/archive/historical_plans/attachment_details_preview_simplification_plan.md`
- optionally `tasks/TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md`

Do not update `docs/task_board.md` unless the change becomes a formal controlled task completion. For this narrow polish, `current_session_state.md` plus the relevant plan/task note is enough.

## 6. Backend Implementation Steps

### Step 1: Update `_requested_testing_table`

File:

```text
backend/application/intake_asset_preview_service.py
```

Find:

```python
def _requested_testing_table(parsed: ParsedApplicationForm) -> PreviewTable | None:
```

Change the rows so they include only requested-testing content and additional information.

Recommended behavior:

```python
rows: list[tuple[str, str]] = []
if _text(parsed.requested_testing_description):
    rows.append(("Description of Requested Testing", _text(parsed.requested_testing_description)))
if _text(parsed.additional_information):
    rows.append(("Additional Information", _text(parsed.additional_information)))
if not rows:
    return None
return PreviewTable(
    "Requested Testing",
    ("Field", "Value"),
    tuple(rows),
)
```

Important:

- Remove this row from the attachment preview table:

```python
if _text(parsed.send_copies_recipients):
    rows.append(("Send Copies To", _text(parsed.send_copies_recipients)))
```

- Do not delete `send_copies_recipients` from the parser or domain DTOs.
- Do not change Precheck display of report-copy recipients.

### Step 2: Keep Table Title Stable

Keep the table title as:

```python
"Requested Testing"
```

Reason:

- This avoids unnecessary API contract churn.
- The frontend can still detect this table by title.
- Tests and integrations that look for a requested-testing section remain easier to update.

## 7. Frontend Implementation Steps

### Step 1: Split Requested Testing From `otherTables`

File:

```text
frontend/src/features/intake/AttachmentPreviewPanel.tsx
```

Current logic likely looks like this:

```tsx
const sampleTable = preview.tables.find((table) => table.title === "Test Sample Information");
const otherTables = preview.tables.filter((table) => table.title !== "Test Sample Information");
```

Replace with:

```tsx
const sampleTable = preview.tables.find((table) => table.title === "Test Sample Information");
const requestedTestingTable = preview.tables.find((table) => table.title === "Requested Testing");
const otherTables = preview.tables.filter(
  (table) => table.title !== "Test Sample Information" && table.title !== "Requested Testing",
);
```

Then render in this order:

```tsx
{sampleTable ? <PreviewTableSection table={sampleTable} compact /> : null}
{requestedTestingTable ? <RequestedTestingPreviewSection table={requestedTestingTable} /> : null}
{otherTables.map((table) => <PreviewTableSection key={table.title} table={table} />)}
```

### Step 2: Add A Specialized Requested Testing Preview Component

In the same file, add a local helper and component near `PreviewTableSection`.

Suggested helper:

```tsx
function previewRowValue(
  table: IntakeAssetPreview["tables"][number],
  labels: string[],
): string {
  const normalizedLabels = labels.map((label) => label.toLowerCase());
  const row = table.rows.find((candidate) => normalizedLabels.includes(candidate[0]?.toLowerCase() ?? ""));
  return row?.[1] ?? "";
}
```

Suggested component:

```tsx
function RequestedTestingPreviewSection({
  table,
}: {
  table: IntakeAssetPreview["tables"][number];
}): ReactElement {
  const requestedTesting = previewRowValue(table, [
    "Requested Testing",
    "Description of Requested Testing",
  ]);
  const additionalInformation = previewRowValue(table, ["Additional Information"]);

  return (
    <section className="attachment-requested-testing-preview">
      <div className="attachment-requested-testing-panel">
        <h4>Description of Requested Testing</h4>
        <p>{requestedTesting || "No requested testing description extracted from the selected application form."}</p>
      </div>
      <div className="attachment-requested-testing-panel">
        <h4>Additional Information</h4>
        <p>{additionalInformation || "No additional information extracted from the selected application form."}</p>
      </div>
    </section>
  );
}
```

Notes:

- Use `p` or a readonly text block, not an editable `textarea`, because Attachment details is a preview surface.
- Keep the labels identical to Precheck where possible.
- Keep this component in `AttachmentPreviewPanel.tsx` for now; it is specific to Intake attachment preview and does not need to become a shared generic abstraction.

### Step 3: Prevent `Send Copies To` From Leaking Through Generic Tables

After adding `requestedTestingTable`, make sure it is excluded from `otherTables`.

This matters because otherwise the new two-panel display and the old generic table could both render the same content.

## 8. CSS Implementation Steps

File:

```text
frontend/src/intake-inbox.css
```

Add styles scoped to the attachment preview:

```css
.attachment-requested-testing-preview {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
}

.attachment-requested-testing-panel {
  min-width: 0;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-canvas);
  padding: 12px 14px;
}

.attachment-requested-testing-panel h4 {
  margin: 0 0 8px;
  color: var(--color-primary-strong);
  font-size: 0.9rem;
}

.attachment-requested-testing-panel p {
  margin: 0;
  color: var(--color-ink);
  white-space: pre-wrap;
}
```

Responsive fallback:

```css
@media (max-width: 900px) {
  .attachment-requested-testing-preview {
    grid-template-columns: 1fr;
  }
}
```

Design notes:

- This is not a nested card problem because the entire document preview is the main preview surface and these are field panels, similar to existing extracted field boxes.
- Do not add decorative color strips or heavy shadows.
- Keep the two panels visually quieter than the primary preview header.

## 9. Test Update Steps

### Backend Unit Test

File:

```text
tests/unit/test_intake_asset_preview_service.py
```

Add or update assertions for the Word application preview test:

```python
requested_testing_table = next(
    table for table in preview.tables if table.title == "Requested Testing"
)
rows = dict(requested_testing_table.rows)

assert rows["Description of Requested Testing"] == "Thermal cycling"
assert "Send Copies To" not in rows
```

If the fixture includes additional information, also assert:

```python
assert rows["Additional Information"] == "<expected value>"
```

If the fixture does not include additional information, either add it to the generated fixture or leave that assertion to a dedicated parser/preview test.

### Frontend Static Test

File:

```text
tests/unit/test_frontend_shell_files.py
```

In the Intake attachment preview test, assert the new specialized rendering exists:

```python
assert "RequestedTestingPreviewSection" in attachment_preview_source
assert "attachment-requested-testing-preview" in attachment_preview_source
assert "Description of Requested Testing" in attachment_preview_source
assert "No additional information extracted from the selected application form." in attachment_preview_source
```

Add a CSS assertion:

```python
assert ".attachment-requested-testing-preview" in intake_css
assert "grid-template-columns: minmax(0, 1fr) minmax(0, 1fr)" in intake_css
```

Do not assert globally that `Send Copies To` is absent from all frontend files, because Precheck still legitimately displays report-copy recipients. Keep any negative assertion scoped to Attachment details preview source or backend preview rows.

## 10. Validation Commands

Run targeted tests first:

```powershell
py -m pytest tests\unit\test_intake_asset_preview_service.py tests\unit\test_frontend_shell_files.py -q
```

Then run frontend build:

```powershell
cd frontend
npm run build
```

Optional broader check if the targeted tests pass:

```powershell
py -m pytest tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py -q
```

## 11. Manual Smoke Checklist

Use the Intake page with a real application-form Word attachment.

Confirm:

- Application-form DOCX preview still opens in Attachment details.
- Header still shows file chip, title, filename, disabled `Download`, and preview action placeholder.
- Key Information grid still appears.
- `Test Sample Information` still matches the application-form / Precheck columns.
- Bottom section shows `Description of Requested Testing`.
- Bottom section shows `Additional Information`.
- `Send Copies To` is not shown in Attachment details.
- Precheck page still shows the send-copy recipient field where it belongs.
- PDF, MSG, image, Excel, metadata-only, unsupported, and non-application Word previews are unchanged.

## 12. Final Record Updates After Implementation

After code and tests pass, update records.

### Update `docs/archive/historical_plans/current_session_state.md`

Add one bullet under `Latest hotfixes/polish`:

```markdown
- Intake Attachment details requested-testing preview now mirrors the Precheck information structure: it shows `Description of Requested Testing` and `Additional Information`, and no longer displays report-copy recipients in the attachment preview surface.
```

Update `Current Validation Baseline` with the exact commands and results you ran.

### Update `docs/archive/historical_plans/attachment_details_preview_simplification_plan.md`

Add a short follow-up note:

```markdown
## Follow-up: Requested Testing Alignment

- Attachment details requested-testing content should stay aligned with Precheck: `Description of Requested Testing` plus `Additional Information`.
- `Send Copies To` remains structured data for Precheck/confirmation, but should not render in Attachment details preview.
- Validation: `<commands and results>`.
```

### Optional: Update `tasks/TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md`

If you want the task file to capture this polish, add a post-completion note:

```markdown
Post-completion polish on 2026-05-04:

- Attachment details requested-testing preview was realigned with Precheck by showing `Description of Requested Testing` and `Additional Information` instead of a generic table containing report-copy recipients.
- Validation: `<commands and results>`.
```

### Do Not Update Unless Needed

Do not update `docs/task_board.md` for this narrow polish unless it becomes an approved controlled task. The board currently says no active implementation task is open, and the next controlled task remains `TASK_091_INTAKE_PRECHECK_MANUAL_SMOKE_AND_UI_POLISH_BACKLOG`.

## 13. Review Notes For The Next Audit

When asking for review, include:

- the diff for `backend/application/intake_asset_preview_service.py`
- the diff for `frontend/src/features/intake/AttachmentPreviewPanel.tsx`
- the diff for `frontend/src/intake-inbox.css`
- test command outputs
- screenshots of one DOCX application-form preview and one Precheck requested-testing area
