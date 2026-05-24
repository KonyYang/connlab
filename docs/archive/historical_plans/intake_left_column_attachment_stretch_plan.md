# Intake Left Column Attachment Stretch Plan

## Purpose

Adjust the New Project Intake layout so the left column behaves like this:

```text
Import source       natural height
Email information   natural height
Attachments         stretches to match the right preview column and can scroll
```

This avoids oversized empty space in `Import source` and `Email information` while keeping the left column visually aligned with the right attachment preview.

## Current Code Shape

Route page:

`frontend/src/pages/IntakeInboxPage.tsx`

Current structure:

```tsx
<div className="intake-step-grid">
  <aside className="intake-left-stack">
    <IntakeSourcePanel ... />
    <AttachmentList ... />
  </aside>

  <AttachmentPreviewPanel ... />
</div>
```

`IntakeSourcePanel` renders two panels:

`frontend/src/features/intake/IntakeSourcePanel.tsx`

```tsx
<>
  <section className="intake-panel">
    <h3>Import source</h3>
    ...
  </section>

  <section className="intake-panel">
    <h3>Email information</h3>
    ...
  </section>
</>
```

`AttachmentList` renders the third left-column panel:

`frontend/src/features/intake/AttachmentList.tsx`

```tsx
<section className="intake-panel intake-attachments-panel">
  ...
</section>
```

Relevant CSS:

`frontend/src/intake-inbox.css`

```css
.intake-step-grid {
  display: grid;
  grid-template-columns: minmax(320px, 410px) minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
}

.intake-left-stack {
  display: grid;
  gap: 16px;
}
```

Because grid items stretch by default, the left stack can expand to match the right preview height. If the stack rows are not controlled, this can visually enlarge the wrong panels.

## Desired Behavior

Keep this:

- The full left column can align with the right preview column.
- The `Attachments` panel may stretch.
- The attachment list can use extra vertical space.

Change this:

- `Import source` should not stretch.
- `Email information` should not stretch.
- Only `Attachments` should consume leftover vertical space.

## Impact

Low frontend CSS impact.

Expected changed files:

- `frontend/src/intake-inbox.css`
- `tests/unit/test_frontend_shell_files.py`

Optional file only if more explicit class hooks are desired:

- `frontend/src/features/intake/IntakeSourcePanel.tsx`

No backend, API, parser, storage, or Precheck changes are needed.

## Recommended Implementation

### Step 1: Make The Left Stack A Three-Row Layout

File:

`frontend/src/intake-inbox.css`

Update `.intake-left-stack`.

Current:

```css
.intake-left-stack {
  display: grid;
  gap: 16px;
}
```

Recommended:

```css
.intake-left-stack {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  gap: 16px;
  align-self: stretch;
  min-height: 0;
}
```

Why:

- First row: `Import source`, natural height.
- Second row: `Email information`, natural height.
- Third row: `Attachments`, takes the remaining height.
- `minmax(0, 1fr)` prevents overflow math issues in nested grids.

### Step 2: Make The Attachments Panel Stretch

Same CSS file.

Add:

```css
.intake-attachments-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 0;
}
```

Why:

- Heading stays natural height.
- Attachment list area can expand and scroll.

### Step 3: Let The Attachment List Scroll When Needed

Current `.attachment-list`:

```css
.attachment-list {
  display: grid;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}
```

Recommended:

```css
.attachment-list {
  display: grid;
  align-content: start;
  min-height: 0;
  overflow: auto;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}
```

Why:

- `overflow: auto` allows many attachments without pushing the whole page.
- `align-content: start` keeps rows pinned to the top instead of distributing extra vertical space.
- `min-height: 0` allows the list to shrink inside a grid row.

### Step 4: Keep Empty State Comfortable

Current `AttachmentList` can render `.attachment-empty` instead of `.attachment-list`.

If an empty state looks vertically awkward after stretching, add:

```css
.intake-attachments-panel .attachment-empty {
  align-self: start;
}
```

Do not center it vertically unless the panel is intentionally empty-state focused.

### Step 5: Medium Viewport Check

There is a medium viewport rule:

```css
@media (min-width: 761px) and (max-width: 1366px) {
  .intake-step-grid {
    grid-template-columns: minmax(310px, 385px) minmax(0, 1fr);
    gap: 12px;
  }

  .intake-panel {
    padding: 14px;
  }
}
```

You probably do not need special handling there.

If the left column becomes too cramped, add only this:

```css
@media (min-width: 761px) and (max-width: 1366px) {
  .intake-left-stack {
    gap: 12px;
  }
}
```

Avoid changing `.intake-step-grid { align-items: start; }`, because that would stop the left column from matching the right preview height and prevent the attachment panel from naturally using leftover height.

### Step 6: Narrow Viewport Check

There is a narrow viewport rule:

```css
@media (max-width: 900px) {
  .intake-step-grid,
  .step-footer,
  .attachment-details-heading,
  .attachment-meta-grid {
    grid-template-columns: 1fr;
  }
}
```

If the page stacks into one column on narrow widths, the attachment panel should not consume excessive height. Add:

```css
@media (max-width: 900px) {
  .intake-left-stack {
    grid-template-rows: none;
    align-self: start;
  }

  .intake-attachments-panel {
    grid-template-rows: auto;
  }

  .attachment-list {
    max-height: 360px;
  }
}
```

Use this only if manual smoke shows the stacked layout becomes too tall. On desktop-only usage, this can be deferred.

## Optional Alternative: Add Explicit Panel Classes

This is optional. It gives cleaner CSS but touches TSX.

File:

`frontend/src/features/intake/IntakeSourcePanel.tsx`

Change:

```tsx
<section className="intake-panel">
```

to:

```tsx
<section className="intake-panel intake-import-panel">
```

and:

```tsx
<section className="intake-panel">
```

to:

```tsx
<section className="intake-panel intake-email-panel">
```

Then CSS can explicitly state:

```css
.intake-import-panel,
.intake-email-panel {
  align-self: start;
}
```

This is not required if `grid-template-rows: auto auto minmax(0, 1fr)` works as expected.

## Static Test Updates

File:

`tests/unit/test_frontend_shell_files.py`

Add expectations to an existing Intake layout test, likely `test_task087_intake_information_density_cleanup` or `test_task090_intake_workflow_structure_extraction`.

Recommended assertions:

```python
assert "grid-template-rows: auto auto minmax(0, 1fr);" in inbox_styles
assert ".intake-attachments-panel" in inbox_styles
assert "grid-template-rows: auto minmax(0, 1fr);" in inbox_styles
assert "overflow: auto;" in inbox_styles
assert "align-content: start;" in inbox_styles
```

Do not overfit the test to exact media-query behavior unless you add the narrow viewport rules.

## Validation Commands

Run targeted frontend static test:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task090_intake_workflow_structure_extraction -q
```

If you updated a different test, run that one directly.

Run full frontend static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Run frontend build:

```powershell
cd frontend
npm run build
```

## Manual Browser Check

Check these cases:

1. One attachment, DOCX preview tall.
   - `Import source` stays natural height.
   - `Email information` stays natural height.
   - `Attachments` stretches downward.
   - Right preview and left column bottom align acceptably.

2. Six or more attachments.
   - Attachment list uses extra height.
   - If list exceeds panel height, it scrolls.
   - Left column does not push the right preview.

3. No imported package.
   - Empty attachment state still reads clearly.
   - It is not awkwardly centered in a huge blank panel.

4. Narrow / side-by-side Windows layout.
   - Cards do not overlap.
   - Attachment list does not consume the whole screen if columns stack.

## Expected Final Layout

```text
Left column                           Right column

Import source                         Attachment preview
natural height                        tall content

Email information
natural height

Attachments
stretches to remaining height
scrolls if needed
```

## Documentation Guidance

This is a frontend UI polish under completed Intake/Attachment preview work.

If the change is kept:

- Add a short note to `tasks/TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION.md` or `TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md`.
- Prefer `TASK_090` if you treat it as Intake layout structure polish.
- Prefer `TASK_088` if you treat it as part of Attachment details preview polish.
- Do not open `TASK_091`.
- Do not change `docs/task_board.md` active task.

Suggested note:

```md
- Intake left column layout now keeps `Import source` and `Email information` at natural height while allowing the `Attachments` panel to consume remaining height and scroll when needed.
```

## Deferred Cleanup

Do not clean unrelated Intake CSS in the same pass unless the layout is already visually stable.

Track a later focused cleanup for unused legacy selectors left by the Attachment details simplification:

- `.attachment-details-heading`
- `.attachment-meta-grid`
- `.detail-file-icon`
- `.metadata-preview-grid`

These can be removed later if a repo-wide search confirms they are no longer rendered. Validate with:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
cd frontend
npm run build
```
