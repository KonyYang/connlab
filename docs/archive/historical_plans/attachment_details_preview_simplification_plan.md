# Attachment Details Preview Simplification Plan

## Purpose

This document is the implementation guide for simplifying the Intake `Attachment details` preview area.

It replaces the earlier partial plan that only simplified `docx_application_form` previews. The desired direction is now broader:

- DOCX application form
- PDF
- MSG
- image
- Excel
- non-application Word
- unsupported / metadata-only files

should all use one consistent preview structure.

## Current Problem

The current right-side attachment preview area can show two nested headers:

```text
Attachment details
selected-file-name.docx
Preview / File size / Role

[W] Laboratory Testing Request preview
selected-file-name.docx
...
```

This creates several issues:

- The file name appears twice.
- `File size` is not useful for the operator's intake decision.
- Raw `Role` values such as `supporting_attachment` expose backend terminology.
- `Preview = Metadata only` or `Structured Word preview` repeats what the inner preview already communicates.
- PDF/MSG/IMG/XLS and DOCX previews use different visual rules after the first simplification pass.
- The meaningful preview content is pushed down by system metadata.

## Follow-up: Requested Testing Alignment

- Attachment details requested-testing content should stay aligned with Precheck: `Description of Requested Testing` plus `Additional Information`.
- `Send Copies To` remains structured data for Precheck/confirmation, but should not render in Attachment details preview.
- Validation (first pass): `py -m pytest tests\unit\test_intake_asset_preview_service.py tests\unit\test_frontend_shell_files.py -q` = 40 passed; `npm run build` passed.

## Parser Structural Alignment (2026-05-04)

- DOCX parser now preserves the application-form two-column requested-testing table with columns `Tests to be Performed` and `Applicable Specifications`.
- `ParsedApplicationForm` gained `requested_testing_rows: tuple[ParsedRequestedTestingRow, ...]`.
- `Additional Information` is extracted from its dedicated block table after skipping Confidential/Subcontracted tables.
- Preview service returns `Description of Requested Testing` as a two-column table and `Additional Information` as a separate single-column table.
- Frontend `AttachmentPreviewPanel` renders the two-column requested-testing table in the left panel and Additional Information text in the right panel.
- Validation: `py -m pytest tests\unit\test_application_form_parser.py tests\unit\test_intake_asset_preview_service.py tests\unit\test_frontend_shell_files.py -q` = 48 passed; `npm run build` passed; `py -m pytest -q` = 293 passed.

## Final Target

Use one preview container for every attachment type.

All attachment previews should follow this visual structure:

```text
[TYPE] Preview title                                      [Download] [columns]
       file-name.ext

preview content or guidance
```

Examples:

```text
[W] Laboratory Testing Request preview                    [Download] [columns]
    Coolpower ... Request-20251111.docx

[business field cards]
[Test Sample Information table]
[Requested Testing table]
```

```text
[PDF] PDF attachment                                      [Download] [columns]
      2043130018-PS-000.pdf

PDF content is stored with this intake package. Detailed rendering is not implemented in this task.
```

```text
[MSG] MSG attachment                                      [Download] [columns]
      RE: Coolpower HDF 3.40mm ....msg

MSG content is stored with this intake package. Detailed rendering is not implemented in this task.
```

```text
[IMG] Image preview                                      [Download] [columns]
      screenshot.png

[image frame]
```

## Scope

Expected changed files:

- `frontend/src/features/intake/AttachmentPreviewPanel.tsx`
- `frontend/src/intake-inbox.css`
- `tests/unit/test_frontend_shell_files.py`

Optional documentation after implementation:

- `tasks/TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md`
- `docs/archive/historical_plans/current_session_state.md`

Do not change unless separately required:

- backend APIs
- parser behavior
- storage schema
- intake package asset model
- Precheck behavior
- `docs/task_board.md` active task

## Non-Goals

Do not implement real download.

Do not implement full PDF rendering.

Do not implement full Excel rendering.

Do not parse nested `.msg` bodies in this UI cleanup.

Do not remove metadata from API responses. Hide unnecessary metadata in the operator UI only.

Do not expose raw backend values such as `supporting_attachment` in the main preview header.

## Implementation Strategy

The correct strategy is not to special-case only DOCX.

Instead:

1. Remove the outer `Attachment details` header and `Preview / File size / Role` row from the rendered panel.
2. Move the disabled `Download` and columns buttons into every inner preview header.
3. Keep one shared header style for DOCX, PDF, MSG, IMG, XLS, metadata-only, and unsupported previews.
4. Keep empty, loading, and error states clear.

## Step 1: Simplify `AttachmentPreviewPanel`

File:

`frontend/src/features/intake/AttachmentPreviewPanel.tsx`

Current implementation may still render:

- `attachment-details-heading`
- `attachment-meta-grid`
- `previewStatusText`
- `formatBytes`
- raw `selectedAsset.asset_role`

Replace the top-level render with a single document preview container.

Recommended implementation:

```tsx
export function AttachmentPreviewPanel({
  error,
  loading,
  preview,
  selectedAsset,
}: AttachmentPreviewPanelProps): ReactElement {
  return (
    <section className="attachment-details-panel attachment-details-panel-compact">
      <div className="document-preview">
        <AttachmentPreview asset={selectedAsset} error={error} loading={loading} preview={preview} />
      </div>
    </section>
  );
}
```

After this change, remove unused imports from `./intakeSelectors`:

```tsx
assetKind
assetKindLabel
formatBytes
previewStatusText
```

Keep these imports if still used by inner preview rendering:

```tsx
assetKindFromPreview
assetKindLabelFromPreview
```

`directWordName` can remain in the prop type temporarily if removing it forces broader changes. If TypeScript reports it is unused only in destructuring, stop destructuring it.

## Step 2: Keep One Shared Action Component

Same file.

Keep or add this helper:

```tsx
function AttachmentPreviewActions(): ReactElement {
  return (
    <div className="details-actions">
      <button className="secondary-action" disabled type="button">
        Download
      </button>
      <button className="toolbar-button toolbar-icon-button" disabled type="button">
        <UiIcon name="columns" />
      </button>
    </div>
  );
}
```

This is still a placeholder. Do not wire real download in this cleanup.

## Step 3: Add Actions To DOCX Preview Header

Same file.

In `DocxApplicationPreview`, use:

```tsx
<div className="docx-preview-title docx-preview-title-with-actions">
  <span className="file-chip file-chip-word">W</span>
  <div>
    <strong>{preview.title}</strong>
    <span>{preview.metadata.original_name}</span>
  </div>
  <AttachmentPreviewActions />
</div>
```

Keep the existing field/table rendering below it.

Keep the existing `Form No./Revision` merge if it already exists:

```tsx
businessPreviewFields(preview)
formVersionText(preview)
```

## Step 4: Add Actions To Image Preview Header

Same file.

In `ImageAttachmentPreview`, change the title block to:

```tsx
<div className="docx-preview-title docx-preview-title-with-actions">
  <span className="file-chip file-chip-image">IMG</span>
  <div>
    <strong>{preview.title}</strong>
    <span>{preview.metadata.original_name}</span>
  </div>
  <AttachmentPreviewActions />
</div>
```

Keep the image frame below:

```tsx
<div className="image-preview-frame">
  <img alt={preview.metadata.original_name} src={preview.image_data_url} />
</div>
```

## Step 5: Add Actions To Metadata-Only / Unsupported Preview Header

Same file.

In `MetadataOnlyPreview`, change the title block to:

```tsx
<div className="docx-preview-title docx-preview-title-with-actions">
  <span className={`file-chip file-chip-${assetKindFromPreview(preview)}`}>
    {assetKindLabelFromPreview(preview)}
  </span>
  <div>
    <strong>{preview.title}</strong>
    <span>{preview.metadata.original_name}</span>
  </div>
  <AttachmentPreviewActions />
</div>
```

Then remove this metadata grid from the operator UI:

```tsx
<dl className="metadata-preview-grid">
  {preview.fields.map((field) => (
    <div key={`${field.label}-${field.value}`}>
      <dt>{field.label}</dt>
      <dd>{field.value}</dd>
    </div>
  ))}
</dl>
```

Keep the message paragraph:

```tsx
<p>{preview.message ?? "Attachment metadata is available. Structured rendering is not implemented for this file type."}</p>
```

Reason:

- API still contains metadata for future backend/AI use.
- The operator UI no longer needs file size, file type, and role repeated in the preview surface.

## Step 6: Simplify Fallback Unsupported Branch

Same file.

The existing branch:

```tsx
if (preview.kind === "metadata_only" || preview.kind === "unsupported") {
  return <MetadataOnlyPreview preview={preview} />;
}
```

already covers unsupported previews.

If there is still a later fallback like:

```tsx
if (preview.kind !== "docx_application_form") {
  return (
    <div className="preview-empty unsupported-preview">
      ...
    </div>
  );
}
```

you can simplify it to:

```tsx
if (preview.kind !== "docx_application_form") {
  return <MetadataOnlyPreview preview={preview} />;
}
```

or leave it as a defensive fallback if TypeScript narrowing complains. The important point is that normal PDF/MSG/XLS metadata-only previews should use `MetadataOnlyPreview`.

## Step 7: CSS Update For One Preview Container

File:

`frontend/src/intake-inbox.css`

### 7.1 Simplify outer panel

Recommended:

```css
.attachment-details-panel {
  display: grid;
  min-height: 610px;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}
```

This removes the extra outer card. The actual visual container becomes `.document-preview`.

### 7.2 Make document preview the main card

Change `.document-preview` away from centered placeholder layout.

Recommended:

```css
.document-preview {
  position: relative;
  display: grid;
  align-items: stretch;
  min-height: 610px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
}
```

Avoid:

```css
place-items: center;
```

because it creates large empty centered layouts for PDF/MSG/XLS preview messages.

### 7.3 Use one body layout for preview types

Merge shared layout rules:

```css
.docx-structured-preview,
.image-attachment-preview,
.metadata-only-preview {
  display: grid;
  align-self: stretch;
  width: 100%;
  gap: 14px;
  padding: 18px;
  background: var(--color-surface);
}
```

If these selectors already exist separately, merge them carefully instead of duplicating rules.

### 7.4 Header with actions

Keep or add:

```css
.docx-preview-title {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
}

.docx-preview-title-with-actions {
  grid-template-columns: max-content minmax(0, 1fr) auto;
  align-items: center;
}

.docx-preview-title-with-actions > div {
  min-width: 0;
}

.docx-preview-title-with-actions .details-actions {
  justify-self: end;
}

.docx-preview-title-with-actions .secondary-action {
  min-height: 36px;
  padding: 8px 14px;
}
```

### 7.5 Keep text wrapping safe

Ensure file names do not collide with the buttons:

```css
.docx-preview-title span {
  overflow-wrap: anywhere;
}
```

If current CSS forces `white-space: nowrap` on preview title spans, remove that for this area.

### 7.6 Leave unused outer styles for a later cleanup

You may leave these classes in CSS temporarily even if TSX no longer renders them:

```css
.attachment-details-heading
.attachment-meta-grid
.detail-file-icon
```

Do not spend this pass on broad CSS deletion unless tests and screenshots are already stable.

## Step 8: Update Static Tests

File:

`tests/unit/test_frontend_shell_files.py`

In `test_task088_attachment_details_preview_completion`, keep existing assertions for:

- `AttachmentPreviewPanel`
- `AttachmentPreview`
- `DocxApplicationPreview`
- `ImageAttachmentPreview`
- `MetadataOnlyPreview`
- `PreviewTableSection`

Add or update assertions:

```python
assert "AttachmentPreviewActions" in inbox_source
assert "docx-preview-title-with-actions" in inbox_source
assert "attachment-details-panel-compact" in inbox_source
assert "metadata-preview-grid" not in inbox_source
assert "previewStatusText" not in inbox_source
assert "formatBytes" not in inbox_source
```

For styles:

```python
assert ".docx-preview-title-with-actions" in inbox_styles
assert ".metadata-only-preview" in inbox_styles
assert ".image-attachment-preview" in inbox_styles
```

Do not assert that `.attachment-meta-grid` is absent from CSS if you choose to leave unused CSS for later cleanup.

## Step 9: Validation Commands

Run targeted static test:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task088_attachment_details_preview_completion -q
```

Run full frontend static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Run production frontend build:

```powershell
cd frontend
npm run build
```

Optional preview backend guard if backend preview code was touched:

```powershell
py -m pytest tests -k preview -q
```

## Manual Smoke Checklist

In the browser, check selected attachments of these types:

- application-form Word `.docx`
- PDF
- MSG
- image
- Excel `.xls` / `.xlsx`
- non-application Word, if available

For each type verify:

- There is no outer `Attachment details` duplicate header.
- There is no outer `Preview / File size / Role` row.
- The preview header has file chip, title, file name, disabled Download, and columns button.
- File name is visible and does not overlap actions.
- PDF/MSG/XLS show one guidance sentence.
- Image preview still renders the image.
- DOCX application form still renders field cards, sample table, and requested testing sections.

## Expected Final UI

DOCX application form:

```text
[W] Laboratory Testing Request preview                    [Download] [columns]
    request.docx

[field cards]
[Test Sample Information]
[Requested Testing]
```

PDF:

```text
[PDF] PDF attachment                                      [Download] [columns]
      spec.pdf

PDF content is stored with this intake package. Detailed rendering is not implemented in this task.
```

MSG:

```text
[MSG] MSG attachment                                      [Download] [columns]
      email.msg

MSG content is stored with this intake package. Detailed rendering is not implemented in this task.
```

Image:

```text
[IMG] Image preview                                      [Download] [columns]
      screenshot.png

[image frame]
```

Excel:

```text
[XLS] Excel attachment                                   [Download] [columns]
      template.xls

Excel content is stored with this intake package. Detailed rendering is not implemented in this task.
```

## Documentation After Implementation

If this change is kept:

1. Add a short note to `tasks/TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md`.
2. Update `docs/archive/historical_plans/current_session_state.md` latest hotfixes/polish and validation baseline.
3. Do not open `TASK_091`.
4. Do not change `docs/task_board.md` active task.

Suggested note:

```md
- Attachment details previews now use one unified header for DOCX, PDF, MSG, image, Excel, metadata-only, and unsupported attachments; operator-facing preview pages no longer show duplicated outer `Attachment details`, `File size`, or raw `Role` rows.
```

## Deferred Cleanup

Do not block the preview simplification on CSS deletion. After the Intake preview and layout changes are stable, schedule a focused dead-style cleanup for legacy selectors that may no longer be rendered from `AttachmentPreviewPanel.tsx`.

Candidate selectors:

- `.attachment-details-heading`
- `.attachment-meta-grid`
- `.detail-file-icon`
- `.metadata-preview-grid`

Before deleting them:

1. Search TSX and CSS references with `rg`.
2. Confirm empty, loading, error, image, metadata-only, unsupported, and responsive preview branches still render correctly.
3. Run `py -m pytest tests\unit\test_frontend_shell_files.py -q`.
4. Run `npm run build` from `frontend/`.

## Review Checklist

Before considering the change complete:

- `docx_application_form` has one visible file name, not two.
- PDF/MSG/XLS/image previews have the same header structure as DOCX.
- `Download` placeholder remains visible for every preview type.
- Raw `Role` is not visible in the operator preview area.
- `File size` is not visible in the operator preview area.
- Metadata-only previews still show useful guidance text.
- Loading, empty, and error states still show clear text.
- `npm run build` passes.
- `tests/unit/test_frontend_shell_files.py` passes.
