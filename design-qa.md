# Unified Temperature Data Editor — Design QA

final result: passed

## Evidence and comparison state

- Source visual truth: `C:/Users/White/.codex/generated_images/01a02cd2-b111-7c53-a4b3-d1e1802d7ed3/exec-f41c50c6-0067-47a1-ae52-1e1c2c4bc67c.png` (selected displayed image 2).
- Implementation: `http://localhost:5173/tools/temperature-rise`, isolated QA tab; the user's tab was not reimported or edited.
- Evidence directory: `C:/Users/White/.codex/visualizations/2026/08/23/01a02cd2-b111-7c53-a4b3-d1e1802d7ed3/`.
- Implementation screenshot: `grid-editor-final.png` in that directory.
- Source and implementation: both 1487×1058 pixels; CSS viewport 1487×1058, devicePixelRatio 1. No density rescaling.
- Matched state: real `3A new.csv`, 3 samples × 10 probes, AG ambient / AI plot current, excluded row 49, selected column G, open column menu, Move Before D. Source values/time strings in the generated mock are illustrative; the implementation preserves actual values and full timestamps.
- Full-view combined comparison: `grid-comparison-pass1.png`, then `grid-comparison-final.png`. Both source and capture were placed together before judging.
- Focused combined comparison: `grid-detail-pass1.png`, then `grid-detail-final.png`; header/selection/menu typography and spacing examined at native detail size.
- Responsive evidence: `grid-editor-856.png`, `grid-editor-narrow.png` (543×804). Page widths 841 and 528 CSS px respectively; horizontal scrolling remains inside parameter/table regions. At 543px the popup bounds were x267–511, y332–540, inside the viewport. Temporary viewport override reset and QA tab closed.

## Findings and comparison history

Pass 1: blocked for a P2 header/readability issue. Single-line scanner channel identifiers made columns unnecessarily wide and difficult to scan, and the popup lacked the selected source identity.

Fix: scanner headings split into channel number and channel name/unit, table text raised to 13px, full source header kept in its title, menu shows the selected original column identity, Move receives the primary-action treatment. Row exclusions also retain explicit `(Excluded)` text and semantic row headers.

Pass 2: final combined full-view and focused evidence inspected after these fixes. No remaining actionable P0/P1/P2 findings in the unified editor.

## Required fidelity surfaces

- Typography: existing ConnLab Segoe UI, regular source values and labels, stronger title/group hierarchy. Header names remain readable in two lines; long metadata preserves full values rather than imitating shortened mock values.
- Layout/spacing: full-width spreadsheet replaces configuration cards. Compact parameter row, selected-count toolbar, grouped sticky headers, nearby small popup, local scrolling, and confirmation below the grid. Toolbar wraps without overlap at narrow widths.
- Colors/tokens: existing blue action/group tokens, blue selected column, muted gray excluded row/column, amber review state. Move/focus remain distinguishable; no extra decorative colors.
- Assets/icons: no raster assets in the editor reference. Existing ConnLab navigation icons and chevron library are reused; no new artwork, icon dependency or fake imagery.
- Copy/content: English operating labels, original scanner headers retained. Ambient, Plot Current, and Retained / Not Plotted · Stable are visible directly in headers. Grouping errors name the required recovery action.
- Accessibility/states: native labelled checkboxes/selects/buttons; semantic table/row headers; keyboard-focusable scroll region; popup Escape/Tab/focus return and outside dismissal; clear selected/excluded/pending/disabled states.

## Intentional integration differences

- Preserve the existing application shell, typography scale and Initial Data card instead of scaffolding a new standalone app.
- Existing T-riseChart/Derating analysis panels remain unchanged, rather than reproducing the mock's collapsed illustrative panels. This revision targets the unified preparation editor; numerical controls and their established workflow are not rewritten.
- Add pagination, range-selection disclosure and Restore All Rows for long real files. Full timestamps and decimal readings remain unchanged, unlike the mock's invented examples.
- Excluding unused metadata affects editor visibility state only; calculation exclusion is represented by the ordered temperature-column selection and excluded rows. Ambient/plot/known auxiliary current roles are protected. Original uploads are never rewritten.

## Primary interactions and implementation checklist

- [x] Real CSV import, all source columns, sample grouping and stable-current default.
- [x] Row selection/exclusion/restoration; no automatic removal of unpowered records.
- [x] Column exclusion, incomplete-group blocking, entire spare column moved into position, confirmation and curve generation (disposable CSV fixture).
- [x] Multi-column ordered moves, range selection, Undo, role protection and keyboard closure (automated regressions).
- [x] Editing after curve generation clears old results and requires reconfirmation.
- [x] Real CSV with explicitly kept flagged rows still gives measured baseline Max 26.544°C / Avg 24.572°C with unchecked Zero Intercept.
- [x] Desktop/856px/543px layouts checked; popup and persistent controls contained.
- [x] Isolated browser console: zero error/warning logs.

Residual gaps: no new screen-reader session or native Excel rendering; numerical/export implementation is unchanged. Review was a same-agent visual/functional pass, not an independent reviewer.
