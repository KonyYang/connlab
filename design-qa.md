# Temperature Rise & Derating — Design QA

final result: passed

## Comparison targets and normalization

- Source visual truth: `C:/Users/White/.codex/generated_images/01a02cd2-b111-7c53-a4b3-d1e1802d7ed3/exec-14c884a2-7bf5-434d-9594-0c669e952996.png` (selected third concept, 1330×1182).
- Implementation: `http://localhost:5173/tools/temperature-rise` in the real ConnLab shell.
- Evidence directory: `C:/Users/White/.codex/visualizations/2026/08/23/01a02cd2-b111-7c53-a4b3-d1e1802d7ed3/`.
- Full-view evidence: `temperature-desktop-final.png`, 1315×1182 screenshot at 1330×1182 CSS viewport;
  browser scrollbar accounts for the 15px difference. No synthetic image scaling or density conversion.
- Focused analysis evidence: `temperature-analysis-final.png`, same viewport, scrolled to expose both
  charts, coefficients, equations/R² and calculated current. Source and implementation were displayed
  together in each final comparison input, not judged from paths or memory.
- Responsive evidence: `temperature-narrow-review.png` (723×804 at 738×804) and
  `temperature-narrow-final.png` (528×804 at 543×804). Native table scroll is deliberate; no page overflow.
- State: real supplied workbook, 20 channels / four per sample, confirmed, both charts and current
  calculated. Desktop overview collapses the preparation details. The source shows three illustrative
  rows; implementation exposes 50 real rows per preview page and editable mapping when expanded.

## Findings and comparison history

1. Initial comparison — blocked: [P1] actions inherited unstyled browser buttons; [P2] coefficient
   labels crowded input columns. Added scoped existing ConnLab action tokens and a fixed row-label
   column with readable inputs. Re-capture: `temperature-desktop-refined.png`.
2. Final wide comparison — blocked: [P2] both Derating annotation labels sat above their points and
   approached/crossed the curves. Placed Basic above and derated below, bounded within the chart.
   A further focused check increased lower-label clearance. The final desktop and narrow captures
   show separate labels without curve/text collisions.
3. Post-fix full and focused comparison — passed: no actionable P0/P1/P2 differences remain.

## Required fidelity surfaces

- Typography: existing ConnLab system font and weights retained; page/section hierarchy and form
  labels are legible. Native file chooser follows OS language. Smaller dense-data text is deliberate.
  Coefficient labels no longer collide; narrow text wraps inside panels.
- Spacing/layout: full-width preparation then two analysis columns, stacking below 850px, as intended.
  Expanded mapping and reversible editing add vertical space requested after the concept selection.
  Panels and buttons use existing radii and spacing. Sticky download remains reachable.
- Colors/tokens: ConnLab light canvas, pale blue controls, green confirmed/download feedback, amber
  review and red error. MAX orange / AVG blue and Basic red / derated orange remain consistent.
- Image quality/assets: no decorative imagery introduced. Curves are actual numeric SVG plots,
  not raster mock screenshots or fake artwork. Existing navigation icons reused; native Excel charts
  were separately rendered and inspected at full resolution.
- Copy/content: named channel roles, original row numbers, explicit scale guidance, Confirm Data and
  quiet feedback replace illustrative mock content. Application text contains no design-preview label.
  Equations/R² and exact results sit outside the plot to keep data readable at narrow widths.
- Interaction/accessibility: labels, native selects/checkboxes, visible focus styles, disabled gates,
  live status, review/error messages, table scrolling, collapsible sections and precise results checked.
  No screen-reader audit was performed; this is a practical visual/interaction acceptance check.

## Tested flows and accepted differences

- Import, spare-channel replacement, row exclusion/restoration, confirmation and invalidation;
  both chart buttons, coefficients, current and download action all exercised against the live backend.
- Browser console warnings/errors: none in final isolated smoke tab.
- The real shell intentionally keeps its existing Tools header/sidebar rather than the concept's
  added branding/breadcrumb. Range is two editable numeric fields. Arbitrary source-column mapping
  replaces a simple C:V text field; it is required by the user's later raw-data review discussion.
- Windows/system fonts and browser-rendered plots are not a pixel-exact raster recreation; information
  architecture, chart meaning, color distinction and primary operations match the selected design.
- OS download-completion event is not exposed by this in-app automation; HTTP/feedback and the exact
  export service's native Excel file were verified separately. No blocking layout defect remains.

## Implementation checklist

- [x] Recheck scoped actions, coefficient grid and chart label clearances after fixes.
- [x] Compare full page and focused chart regions with the source in the same input.
- [x] Check expanded data-review flow and narrow stacked layout.
- [x] Run final affected UI tests and TypeScript/Vite build.
- [x] Preserve source workbook, generate a separate native-chart Excel file, inspect in Excel.

## Follow-up polish

P3: optional larger-viewport density tuning after operator acceptance; no workflow expansion is needed
for this delivery. Full keyboard/screen-reader audit and very large production scanner files remain
future acceptance coverage, not claims made by this visual check.
