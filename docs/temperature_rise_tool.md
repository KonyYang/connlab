# Temperature Rise and Derating Tool

Status: implemented. Current refinement (2026-10-17): unified current decimal precision, compact manual Test Info without project lookup
and a compact XLSX metadata header. Editable measurement names, stable source identity,
reversible ambient-role suspension and consecutive regrouping after explicit moves remain supported.
Compact charts, automatic generation after confirmation and scan-based feedback remain in place.

## Compact source and confirmation controls (2026-10-17)

The standalone imported filename row is removed. The worksheet dropdown sits immediately after
Load Initial Data in the header with no visible Sheet Name label; its accessible name is retained.
Ambient Column, Current Column, Samples and Current Decimals follow the worksheet dropdown on the same
header line. The worksheet selector is 144px and both column selectors are 128px (twice their
initial compact widths); full selected source headers remain available on hover. TC/Sample sits
between Samples and Current Decimals; numeric spinner widths and calculation behavior are unchanged.
The import/parameter strip scrolls horizontally when space is insufficient. Compact Confirm Data
and Download Excel actions follow Current Decimals and stay fixed at the far right of the header,
with complete labels and unchanged eligibility rules. There is no duplicate parameter row in the data panel.
Hovering the dropdown shows the complete source filename. Changing the sheet still reloads that
sheet and requires confirmation again. The browser upload contract supplies no disk absolute path; the UI does not fabricate
one or add filesystem access. The sticky bottom bar now holds feedback only, in a single line.
Data Needs Review uses ellipsis when needed and a hover title containing all messages on separate
lines; the full text remains in the accessible region. The former large review panel is removed,
but flagged-row highlighting, error blocking, confirmation, busy states and invalidation are unchanged.
The feedback bar is omitted when empty.

Data Preview shows Included / Excluded Rows beside its title instead of the sample/channel summary.
The duplicate row-count footer below the table is removed. Counts still derive from the selected
data range and explicit row exclusions, updating on exclude, restore and undo. Sample grouping
controls, warnings and calculations are unchanged.

## Current precision contract (2026-10-17)

`Current Decimals` is a native number spinner immediately after Samples (0–4, step 1, default 0).
It is a calculation setting, not just an Excel display format. Preparation applies decimal half-up
rounding after the selected current scale, then treats a rounded zero as unpowered for that column.
Examples: at 0 places, 0.4123→0 and 0.5→1; at 1 place, 0.04→0.0 and 0.05→0.1; at 2 places,
0.0087→0.01. It replaces the former fixed 0.1 A cutoff. Auxiliary power detection uses the same
precision without treating a zero main current as proof that other current columns are off.

Stage detection and fits consume these prepared values. Original import/Initial Data values remain
unchanged, including excluded rows and full-precision CSV strings. Zero readings are flagged for
review, never automatically excluded. Changing precision invalidates confirmation, fits, calculated
current, Derating and downloads; it preserves row exclusions, names, source IDs and sample groups.
Automatic intercept defaults are rechecked from the precision-aware prepared auxiliary currents;
explicit manual intercept choices remain authoritative.

Web stage/current results, current axes and annotations, Excel summary/stage current values,
auxiliary rows, calculator and Derating current formats all follow the selected precision. Excel
uses ROUND for measured currents and matching formula caches. Temperature precision and six-decimal
fit coefficients do not change; calculated-current/Derating curves retain underlying precision for
smooth calculations and use the selected current display format. Earlier dated acceptance numbers
and display-only precision notes below are historical, superseded by this contract.

`Tested By` snapshots the persistent local project-leader display name for each new import via
`frontend/src/currentUser.ts`, falling back to anonymous `Lab User`. Late session bootstrap may fill
an unassigned default, but editing the local name never overwrites an existing report. Manual replacement
or deliberate clearing overrides the default, survives reimport, and is sent to the XLSX report.
See `docs/local_identity.md` for the login-free single-field name setting, New Project defaults and
the preservation boundary. Existing registered account data is retained independently, never read
or migrated by the profile flow.

Sample count refinement (2026-10-14): instrument measurement-name prefixes `1_`, `2_`, `3_` etc.
take priority; their actual group count can be 1, 3, 5 or more. Unnumbered imports default to 3 Samples.
The compact editable Samples control derives TC/Sample, without a competing editable probe-count
control. Unequal groups/nondivisible totals retain all source IDs and block confirmation, analysis
and download until explicit adjustment. No channel is rounded away or silently omitted. Unnumbered
spares beside numbered groups remain available, not silently activated. Exclusion retains original
sample ownership; balanced exclusions update derived probe count. Explicit Samples edits or moves
regroup current effective column order. Role suspension/restoration and undo retain desired Samples.
Optional API `sample_count` is authoritative when supplied; omitted/null retains legacy TC/Sample
requests. Renaming display labels never changes source IDs or group ownership.

Export presentation refinement (2026-10-14): `Initial Data` has no frozen panes. The summary's
`Current(A)` row uses the selected current precision (integer `0` by default), with rounded measured
values/formulas shared by chart fits and calculations. T-riseChart's summary, calculator and stage-detail tables use
horizontal center alignment, including column A. No cell comments are generated. The top report
information block retains its readable label/value layout, and other numeric precision is unchanged.

Warning-review refinement (2026-10-14): `Keep Flagged Rows`, `Select Unpowered Rows` and
`Restore All Rows` are removed. Explicit `Confirm Data` retains warning-only readings without a
second acknowledgement control. The frontend uses the existing API `acknowledge_warnings=true`
contract; backend errors still block confirmation, analysis and export. Warning text and source-row
highlight/accessibility labels remain visible. Row checkboxes (including Select All Rows) and the
top Exclude Selected / Restore / Undo controls are the single editing path. Row/data edits invalidate
confirmation and dependent results as before. Backend thresholds and calculation logic are unchanged.
Validation: two targeted regressions failed before implementation; 91 frontend tests, 65 backend
preparation/API tests, and sequential TypeScript/Vite build passed. An isolated Edge smoke verified
real warning highlight, top-row exclusion/restoration, reconfirmation and successful download without
page errors. In-app browser connection was restricted; the user's browser session was untouched.

Multi-current export (2026-10-14): stable auxiliary current rows precede the selected main current
in `TemperatureRiseSummary`. Preparation reuses the existing source-region classification (at least
two powered readings, all rounding above zero at the selected precision, raw spread <=1%) and carries a source-indexed
`stable_auxiliary_current_columns` tuple to the workbook adapter; the prepare HTTP response gains
the equivalent additive array. Selected ambient/main/thermocouple roles are excluded from that list.
Other varying/unpowered electrical columns remain in original/detail data, not the current header.
Current labels use the actual unit-free instrument/edited name followed by `(A)`; numeric prefixes
are stripped without expanding abbreviations. Generic `Current(A)` remains the fallback for the main.
Current axes of exported T-riseChart and Derating charts follow Current Decimals with source linking
disabled; temperature axes retain integer labels. Measured current coordinates and fits use prepared
rounded values, while computed curves remain smooth and annotation formats follow Current Decimals.
Axis-only refinement validation: the new exported-chart regression failed for `0.0` before the fix,
then passed. Final affected QA passed 70 workbook/HTTP tests; a read-only native Excel instance
confirmed all four tick-label formats are `0` with source linking disabled. Exported chart PNGs
were visually checked, while non-integer series values and the 66.5444574215 A calculator baseline
remained unchanged. Prior unchanged preparation/numerical checks were not repeated.
All current rows are gray, bold, centered and formatted at the selected current precision.
Each auxiliary value links to that main-current stage's genuine retained endpoint, including actual
zero-current background readings. Synthetic-origin auxiliary cells stay blank. Numeric CSV text is
coerced in the report formula only; `Initial Data` preserves the original strings/coordinates.
The chart, fits and calculator still reference only the main-current row. Final row locations are
computed before formulas/chart references are built; no row insertion or auxiliary-current fitting
is introduced. Single-current exports retain their existing summary layout and numerical behavior.
Validation: two export regressions failed before implementation. Final review/QA passed 119 backend
preparation/numerical/workbook/HTTP tests. Three isolated read-only Excel cases (recorded origin,
synthetic origin and three 10-probe samples) recalculated without errors; changing an auxiliary raw
cell updated its header value without changing the main-current fit/calculator. Printed previews
confirmed aligned current rows and intact tables/charts. A real localhost CSV import/download also
returned the new rows and unrounded values. Frontend code was unchanged; no frontend build rerun.
Standards and Spec reviews were separate sequential passes by the same agent, with zero findings.

## Compact XLSX export (2026-10-11)

`Initial Data` now contains the complete imported value table at its original one-based row/column
positions, including scanner metadata, excluded rows, excluded/spare channels and auxiliary currents.
It no longer adds confirmation banners, an Original Row column or a reordered prepared-data table.
Only genuine selected stage endpoints are highlighted across the source row in yellow; a synthetic
origin is never highlighted. Source values are not scaled, normalized or renamed. The import is
values-only: original workbook formulas, styles, macros and unrelated source sheets are not copied.
Literal scanner strings remain text, including strings beginning with an equals sign.

The `T-riseChart` report retains its endpoint readings, temperature-rise build and formula-backed
summary. Summary measurement labels omit numeric scanner/sample prefixes by keeping the substring
starting at the first letter when a label starts with a digit: `1_HS` becomes `HS`, not `Header Solder`.
Other names such as `Contact` stay unchanged; blank/all-numeric labels use the T-number fallback.
Edited names follow the same export-only formatting. Sample totals use `n# Single Max`; overall MAX/AVG remain intact.
A is narrower, numeric columns have equal compact widths, long summary labels wrap with fitted row
height, sample subtotals use tan and overall totals use light blue, matching the supplied reference.

Every successful T-riseChart generation calculates the current for the entered Target Rise (30 °C
by default) using the newly generated MAX fit. The result is retained for display and download without
a separate Calculate Current click. Manual retries remain available; a failed or obsolete calculation
does not continue the automatic Derating chain. Editing Target Rise clears the old result until the
operator calculates or regenerates the chart. Exported x(A) is a bold orange formula using Current Decimals
result matching the MAX curve; the displayed number is calculated, never copied from a screenshot.

Revision validation: 85 temperature frontend tests, 105 backend preparation/calculation/export/API
tests and the Vite production build passed. Native Excel read-only QA confirmed HS/H/C/RS labels,
the bold orange one-decimal current and recalculation after changing the target. The original
attachment hash stayed unchanged. The artifact preview's existing LINEST limitation shows formula
errors in its calculator view only; native Excel recalculation found no errors. Sequential same-agent
Standards and Spec reviews found no outstanding issues.

Only the MAX y/a/b/c/x calculator remains visible below the summary. The AVG coefficient block and
both live chart-fit rows are collapsed, not deleted: coefficient overrides, recalculation, linked chart
equations and Derating inputs retain their existing behavior. The native scatter chart has rounded
corners and a larger plot area using the Derating layout proportions; printing includes the calculator.
An empty `Setup` sheet precedes the existing three sheets; `T-riseChart` is selected on opening,
independently of tab order. The unused `CR` sheet is no longer created. No contact-resistance
calculation or setup content is imported. The source attachment and project/report authorities remain
untouched; the change applies only to newly generated downloads.

## Compact manual Test Info (2026-10-13)

Below the imported filename, report information appears in a compact, always-visible editor without
a Test Info heading or collapse control. All four editable fields
are shown together: LTR, Tested By, equipment IDs,
and test condition. There is no separate More Information fold or project selector; Remark is
also hidden and is reserved for direct completion in the exported workbook.
Labels and inputs share a line; an editor at least 720 px wide uses four fields per row.
Inputs are capped at 180 px; narrow editors wrap to two or one field
per row without clipped labels.
Metadata is bounded literal text, including labels starting with `=`. The request boundary retains
its optional humidity validation (finite 0–100 %RH) for compatibility; this tool always supplies 50.

Report information is entered manually. Opening or editing this tool does not query the project
registry or Basic Information, nor infer an LTR or tester from a project. Test Date is hidden
and automatically follows the latest retained source date below. No heading or permanent
explanatory row occupies additional space.

The report environment defaults to 23 °C and 50% RH as explicitly requested by the operator. There
are no visible/editable ambient or humidity report fields; the download metadata carries
`ambient_temperature: "23"` and numeric `relative_humidity: 50`. These are report-only defaults,
not measured values inferred from the file. The selected Ambient
Column, original readings and row-specific temperature-rise calculations remain unchanged.

Test Date uses the greatest valid calendar date in the time column of included source rows,
respecting source region and exclusions even when rows are not sorted by date. ISO or year-first
slash dates are recognized; time-only, ambiguous, blank and invalid timestamps are ignored.
If no valid date or time column remains, the exported date stays blank rather than using today.
Exclusions and reimports refresh it automatically; a previous manual date cannot override it.
Equipment IDs and conditions stay blank without a verified
test-specific source. No download date, planned project date or
generic project-wide equipment list is substituted for actual test facts.

Visible manual fields, including intentional empty values, take precedence over all later suggestions
and source changes. Values are session-local and retained through source/role/sheet changes until
leaving the tool. Report edits clear only old download feedback, not confirmed data or curve/current
results. The record temperature never replaces the row-specific ambient used in calculations.
There is no project Basic Information, Matrix, database or external source write-back.

The download request carries a separate report_metadata object, with empty defaults for older clients.
T-riseChart starts the report information at A1 (Excel has no A0). It uses a vertical, pale-yellow
label/value table: LTR, Test Date, Tested By, Amb Temp. and Rel. Hum. and Test Equipment ID.
Equipment always retains a row, with a blank value when not entered; the condition row
appears only when entered. Remark always occupies the final information row, blank for manual
completion unless an existing API client supplied text. Labels occupy A:B, values C:I; ordinary merged
presentation cells wrap with fitted row heights. TemperatureTestInfo names this top-left region.
The summary/chart and MAX calculator follow it; endpoint readings and the temperature-rise build
remain inspectable below the printable report, rather than preceding its information. All blocks
are written at their final locations instead of inserting rows after formulas have been created.
Named ranges, chart anchors, caches and formula references derive from that layout. Printing starts
at A1 and excludes the supporting detail, preserving the readable single-page report. Initial Data,
numerical behavior are unchanged. Output tabs are Setup, Initial Data, T-riseChart and Derating;
only T-riseChart is selected and is the default opening view. Setup remains blank.

Validation: the new project/manual-override page regression failed before implementation and passed
afterward. Final affected matrix: 103 frontend tests and 109 Python preparation/calculation/workbook/API
tests passed, plus TypeScript/Vite build. Native Excel read-only QA verified header placement, complete
single-page printing, no formula errors and 66.5 A for the established 30 °C target baseline. The rendered
print preview was visually inspected for overlaps and clipped text. No source attachment was modified.
Live browser QA was attempted but blocked by the Browser runtime's EPERM; the offline Playwright CLI
was not cached. Narrow-window CSS and interactions have code/page-test coverage, not a live screenshot.

Top-left layout revision: the HTTP download regression reproduced A21 instead of A1 before the fix,
then passed. It verifies vertical metadata, literal-string safety, blank/zero humidity, preserved raw
readings/Initial Data and equal summary values with/without optional information. Revision touches
only the report-layout adapter, workbook/download tests and this document; frontend behavior is unchanged.
Existing formula regressions now locate readings through the supported KeyStageReadings name rather
than requiring its former physical row 2. The first matrix caught six obsolete fixed-row assertions;
their scan/time, spare-channel, scale and cached numerical checks remain in place.
Final revision matrix: 111 Python tests passed (one existing Starlette/httpx deprecation warning).
Native Excel QA found no formula errors, confirmed the information at A1:I6, and visually verified
the single-page A1:W44 print. Changing Target Rise to 35 recalculated 72.8608073355 A; increasing a
relocated endpoint's thermocouple value by 1 increased its linked summary rise by 1. Temporary edits
were restored before rendering and never saved back. No frontend code changed in this revision.

Opening-view revision (2026-10-12): workbook/HTTP regressions first failed for the previous tab order
and absent blank equipment row, then passed after the localized adapter changes. Formula caches
are assembled after the final tab order is established, preserving each worksheet's cached values.
Final opening-view validation: 111 Python tests passed (the same existing deprecation warning).
A separate hidden Excel instance opened the file directly on T-riseChart, confirmed Setup at index 1
and the blank equipment row, found no formula errors and retained the target/source-edit recalculation
baseline. No frontend changes or project/source writes; the workbook was closed without saving edits.

### Standards

Separate same-agent exact-diff pass: API remains typed and centralized; metadata state belongs to its
feature hook, source suggestions are pure, workbook formatting stays in infrastructure and numerical
domain code is untouched. No new dependency or authority mutation. Zero outstanding findings.
The top-left revision keeps layout ownership in the same Office adapter and its public download
seam; each moved source/reference is regenerated, not patched by inserting worksheet rows.
Opening-view pass: existing workbook APIs set tab order/active selection before caches are mapped;
no private worksheet-list manipulation, added dependency or authority write. Zero findings.

### Spec

Separate same-agent requirements pass: optional project association, confirmed-only tester defaults,
manual/blank override preservation, stale-response guards, collapsible entry, compact printable header
and CR removal are implemented. Missing physical facts remain editable/blank. Zero outstanding findings;
live-browser visual verification remains a stated limitation, not an independently passed check.
Top-left revision: information begins at A1, follows the supplied vertical label/value reference,
and retains calculations, supporting detail and the no-CR tab set. Standards 0 / Spec 0 findings.
Opening-view pass: equipment row is always present, Setup is first yet T-riseChart opens by default;
original data/charts/formulas remain intact. Zero findings. Both passes remain sequential same-agent.

Changed paths: frontend/src/api/temperature.ts; frontend/src/pages/TemperatureRisePage.tsx and its tests;
frontend/src/features/temperature/TestInfo.tsx, reportInfo.ts, reportInfo.test.ts,
useTemperatureReportInfo.ts, useTemperatureTool.ts and temperature.css;
backend/api/temperature_schemas.py and routes_tools_temperature.py;
backend/application/temperature_report_metadata.py and tools_temperature_service.py;
backend/infrastructure/office/temperature_rise_report_sheet.py and temperature_workbook_gateway.py;
tests/integration/test_tools_temperature_api.py; tests/unit/test_temperature_workbook_gateway.py;
this document and the sole-writer task board. Methods: tdd, code-review, spreadsheets and PDF visual QA.
Review passes were sequential in one agent; no independent-agent review is claimed.

Regression protection uses the public workbook writer/render and HTTP download boundaries, covering
raw coordinates, exclusion preservation, exact stage highlighting, literal-string safety, names and
numeric fallbacks, blank sheets, native chart XML, hidden formula dependencies and original numerical
baselines. Review is sequential same-agent Standards/Spec. Visual checks use the bundled spreadsheet
preview for tables and a separate hidden Excel instance for the generated chart and native formula
recalculation; the attachment and any already-open Excel instance are never opened for writing.
Final affected matrix: 103 tests passed. Native Excel recalculated the MAX calculator without errors
(30 °C -> 66.5444574215 A; changing only the target to 35 °C -> 72.8608073355 A), and the exported
rounded chart was inspected. The source attachment hash was unchanged. The preview engine cannot
evaluate the existing LINEST array formulas, so its calculator error display was checked against
native Excel rather than treated as an export failure. The first complete matrix caught one old
test-coordinate assertion (B time versus C temperature); it was corrected, and the final complete
matrix passed. The existing Starlette/httpx deprecation warning is non-blocking.

## Source identity, names and edit state

The source preview no longer displays Excel column letters. Scan/time titles and scanner channel
numbers remain visible. A temperature header's measurement name is a text field; clicking it edits
the name without selecting/moving the column. Original source indices remain the immutable internal
keys even after moves, exclusion, restoration or renaming. Channel numbers and names are metadata,
not identifiers; duplicate names therefore cannot exchange readings or change sample membership.

`selection.channel_names` is an optional source-indexed JSON object. The domain stores immutable
pairs, and the import endpoint projects an object (including `{}`), not a tuple/list. Names are bounded
to 200 characters and existing non-index source columns, with control characters rejected. Renaming
invalidates confirmed/generated results through the existing data-change path; confirm again before
download. The T-riseChart summary uses the edited name, or the original unit-free instrument name
when not edited; an explicitly blank name falls back to the sample's T-number. Names are written as
literal Excel strings. Source headers, full-precision readings and numerical calculations stay intact.

Roles, exclusion and grouping are separate state. Choosing an effective thermocouple as ambient
temporarily suspends it; returning to the previous ambient restores its retained slot. A previously
excluded channel remains excluded through that roundtrip. This includes the last effective channel.
Exclusion alone retains established sample membership (the imported groups until an explicit move);
balanced exclusions update TC/Sample, whereas uneven/empty samples block confirmation.

Every explicit move uses the displayed destination position, including excluded destinations at
the tail, and partitions the current effective column order using the current TC/Sample,
including moves from incomplete groups. It does not silently increase TC/Sample when a spare is
added. Restoring a column after a move follows this new order rather than resurrecting old groups;
the next exclusion from complete groups preserves those newly established groups. Undo restores
the prior grouping mode, slots, order and exclusions. Later role/count choices clear obsolete Undo
history but do not discard excluded channels or measurement names.

Regression evidence: name editing/request propagation; reordered Excel labels/default/blank names
and formula-like literal names; rejected invalid names; balanced exclusions with repeated ambient
changes; last-channel suspension; incomplete cross-sample move/restore/Undo; complete import,
prepare, analysis and download roundtrips. Final results: 68 frontend tests, 97 backend tests and
TypeScript/Vite build passed. The first full backend run caught an import-response array/object
mismatch; it was fixed at the HTTP boundary and all 97 tests rerun successfully. The existing
Starlette/httpx deprecation warning is non-blocking. Focused review also caught movement using an
excluded destination's original rather than displayed position; a failing grid test reproduced it,
the move was aligned with display order, and the final frontend matrix/build were rerun.

Review: sequential same-agent Standards and Spec passes, zero outstanding findings on each axis.
Methods: TDD and code-review. Browser visual QA is unavailable because the required runtime import
returns EPERM at realpath; no browser session/actions were acquired. Actual Excel bytes were tested
with openpyxl, not native Office. Native visual rendering remains unverified. Original files and the
User's browser tab were not operated; development hot refresh may require reimporting the data.

Revision paths: backend `api/routes_tools_temperature.py`, `api/temperature_schemas.py`,
`application/temperature_data_preparation.py`, `domain/temperature_data.py`,
`infrastructure/office/temperature_rise_report_sheet.py`; frontend `api/temperature.ts`,
`pages/TemperatureRisePage.tsx`, `pages/TemperatureRisePage.test.tsx`, feature files `ColumnActions.tsx`,
`DataPreview.tsx`, `DataPreview.test.tsx`, `sampleGroups.ts`, `sourceColumns.ts`, `sourcePresentation.ts`,
`temperature.css`, `useDataGridEditing.ts` under `src/features/temperature/`; tests
`integration/test_tools_temperature_api.py`, `unit/test_temperature_workbook_gateway.py`; this document.
The board is lifecycle-only. No original workbook, project record or database schema is mutated.

## Effective-column grouping

Column headers now replace the column checkboxes: plain click selects one, Ctrl-click toggles a
noncontiguous selection, and Shift-click selects the inclusive displayed range from the last plain
or Ctrl-click anchor. Ctrl+Shift adds a range; Meta also toggles. Repeated Shift endpoints retain
the anchor. Right-click preserves an already selected block; an unselected header becomes the
selection. Space/Enter select a focused header with the same modifiers, and ContextMenu/Shift+F10
opens its operations. A/B, ambient and all current roles remain protected and are skipped in ranges.
Selecting rows, committing edits, Undo, or changing roles/count resets the column anchor. Row
checkboxes and row Shift selection are unchanged; presentation precision never changes source values.
Acceptance covers click/toggle, forward/reverse/reordered ranges, protected/disabled headers, keyboard
block movement, balanced exclusion/restoration and Undo. This is only a frontend interaction revision;
API and numerical behavior are unchanged. Methods: TDD and sequential same-agent code-review.

The column popup is action-only: its redundant Close button and visible column/selection heading
are removed. The highlighted column(s) and toolbar selection count remain the visible context;
the dialog keeps its accessible column name. Outside click, Escape, scrolling and resize dismiss it.
Keyboard focus starts on the first enabled action, Tab wraps within the popup, and Escape returns
focus to the source header. No selection, preparation or numerical behavior is changed.
The Move confirmation button is also removed. Move Before is a borderless action row with a black
right-pointing triangle. Clicking it opens a separate destination submenu to its right; the parent
shifts left near the viewport edge to reserve room. The destination list uses the available viewport
height and scrolls independently without dismissing the popup. There is no Choose Column field.
Opening the submenu does not move anything. Choosing a destination immediately moves
the selected column/block and closes the menu, returning focus to the source header. End Of
Temperature Columns uses the existing placement rule; Undo restores the previous data selection.
Immediate-move validation: the new grid interaction test failed before the change and passed after
it. All 58 affected tests (27 preview, 31 page), production build and isolated browser checks passed.
Browser checks covered a single move, a Shift-selected block moved to the end, Undo, the empty initial
destination and Escape; console warnings/errors were zero. Sequential same-agent Standards/Spec
review found no outstanding issues. Changed paths for this refinement: `ColumnActions.tsx`,
`DataPreview.test.tsx`, `temperature.css`, `frontend/src/pages/TemperatureRisePage.test.tsx` and this
document. No source-file, API or numerical changes; the User's existing tab was not operated.
Single-row refinement validation: the amended interaction test failed on the old Choose Column
presentation, then passed. The complete 58-test preview/page matrix and production build passed on
the final code/test state. An isolated browser confirmed a black triangle, native expanded options,
immediate move and Undo with no console warnings/errors; the User tab was not operated. Sequential
same-agent Standards/Spec review found zero outstanding findings. Refinement paths: `ColumnActions.tsx`,
`DataPreview.test.tsx`, `temperature.css` and this document; board changes are lifecycle-only.
Right-side submenu refinement (2026-10-10): the new public grid interaction test failed on the old
native dropdown and passed after implementation. All 60 affected tests (29 preview, 31 page) and the
production build passed on final source/test bytes. Coverage includes opening without mutation,
right/left arrow entry/return, Escape collapsing only the submenu, Home/End and arrow navigation,
internal scrolling, immediate movement, Undo, and right-side placement within a narrow viewport.
Sequential same-agent Standards/Spec review found no outstanding code findings. Actual browser
visual validation is blocked: the required browser runtime import returns EPERM during realpath,
including a retry with the same module's file URL. No browser session was acquired and the User's
tab was not operated; popup rendering/viewport-height behavior remains a visual verification risk.
This refinement changes `ColumnActions.tsx`, `DataPreview.test.tsx`, `temperature.css`,
`frontend/src/pages/TemperatureRisePage.test.tsx` and this document only; API, source values and
column-ordering rules are unchanged. Methods: TDD and sequential same-agent code-review.
Popup refinement validation: 26 preview tests and the production build passed. An isolated browser
confirmed the action-only popup, outside-click dismissal and Escape focus restoration with no console
warnings/errors. The exact local diff received sequential same-agent Standards/Spec passes with zero
outstanding findings. Refinement paths: `frontend/src/features/temperature/ColumnActions.tsx`,
`DataPreview.tsx`, `DataPreview.test.tsx`, `temperature.css`, and this document; the task board is
lifecycle-only. Source data, API and calculations are unchanged; no User-tab operations were performed.

Header-selection revision validation: 56 affected frontend tests passed (25 preview, 31 page),
followed by the TypeScript/Vite production build. Isolated browser checks passed Ctrl multi-select,
balanced TC2 exclusion (4→3), Shift restoration (3→4), Shift+F10 block movement and Undo; console
warnings/errors were zero. A label locator failed during automation; the observed combobox-role
locator completed the move without a product change. No operations were performed in the User tab.
Standards and Spec passes each found zero outstanding issues; both were sequential same-agent passes.
Revision paths: `frontend/src/features/temperature/DataPreview.tsx`, `useDataGridEditing.ts`,
`temperature.css`, `DataPreview.test.tsx`; `frontend/src/pages/TemperatureRisePage.test.tsx`;
this document. Board changes are lifecycle-only. Source files and numerical/API contracts are untouched.

The preview orders A/B, active thermocouples, ambient, selected main current, other retained currents,
unused source columns, then excluded columns. This is logical presentation, not a source-file rewrite.
The extra Sample header band is removed; alternating restrained header tones, a group boundary and
accessible/hover sample descriptions identify consecutive groups. Electrical columns are protected
and never counted as thermocouples.

Exclusion retains the established sample slots. Removing TC2 from every four-TC sample automatically
changes the count to three and preserves per-sample maxima/average-of-maxima. Restore and Undo retain
membership and count. Uneven/empty groups block confirmation even when the total is divisible.
Explicit moves, including spare moves from incomplete groups, or a manual count edit establish
new consecutive groups by current effective order and TC/Sample. Later role/count decisions clear
older Undo history, but unrelated excluded channels remain restorable.

The optional `selection.sample_groups` carries active source-column groups through preparation,
analysis and download; the backend checks equal positive counts and exact ordered coverage. Legacy
requests without it retain their existing contract. Numerical fits, original values, other-current
retention and Zero Intercept defaults are unchanged. Regression acceptance covers balanced TC2
exclusion, unequal-but-divisible rejection, restore/Undo, spare/block moves, role changes and actual
analysis/Excel download. No authoritative workbook, project record or database schema is mutated.

Grouping implementation validation (before the header-selection revision): 59 affected frontend tests
and 88 preparation/calculation/workbook/API tests passed;
TypeScript/Vite production build passed. The initial frontend matrix had one test-only A/B text-node
assertion failure; that assertion was corrected and its complete 21-test preview file passed again.
The other passing files were unchanged. Isolated browser QA confirmed the three-sample 4→3 case,
actual chart generation, unequal-count blocking and right-click restoration; no browser console
warnings/errors. The stale local API reload process was restarted through `run_backend.ps1` and its
OpenAPI contract verified. No manual operation was performed in the User's tab, but React development
hot refresh rebuilt that session during the hook update: the original file needs reimporting.
Source bytes are untouched. Excel download values were inspected with openpyxl, not native Excel.

Sequential same-agent code-review passes: Standards — zero outstanding findings (feature-owned
group/slot helpers, typed bounded compatible request, existing application validation); Spec — zero
outstanding findings (agreed ordering, single header, preserved groups/count, reversible edits and
unchanged calculation defaults). Methods used: tdd and code-review; no independent review claimed.

Changed paths: `frontend/src/api/temperature.ts`; feature files `DataPreview.tsx`,
`DataPreview.test.tsx`, `sampleGroups.ts`, `sourceColumns.ts`, `temperature.css`,
`useDataGridEditing.ts`, `useTemperatureTool.ts` under `frontend/src/features/temperature/`;
`frontend/src/pages/TemperatureRisePage.test.tsx`; `backend/api/temperature_schemas.py`;
`backend/application/temperature_data_preparation.py`; `backend/domain/temperature_data.py`;
`tests/unit/test_temperature_data_preparation.py`; `tests/integration/test_tools_temperature_api.py`;
this document. Task lifecycle state is recorded only by the board writer.

## Scope and acceptance

The Tools entry opens a dedicated page using the selected third design: a full-width Initial Data
preparation area above two analysis panels (Temperature Rise and Derating). At narrow widths the
panels stack. Existing ConnLab navigation, fonts, controls and quiet feedback remain in use.

- Read `.xls`, `.xlsx`, `.xlsm` and scanner `.csv` without executing VBA or changing the source.
- Automatically locate a unique scanner header and data region; show row settings only for missing
  or ambiguous recognition. Let the user choose the sheet, ambient and current columns,
  thermocouples per sample, and ordered sample/channel mapping. A spare source channel can replace
  any failed channel. Channel order determines sample/thermocouple slots and is shown explicitly.
- Exclude/restore rows and channels without changing source data. Retain original row keys for
  provenance and column letters; use A-column scan identifiers in operator feedback. Suspicious
  rows are suggestions only; the user confirms their inclusion/exclusion.
- Confirm the prepared data before analysis. A later input/mapping/exclusion change invalidates
  dependent charts, coefficients, current and downloads. Late responses must not restore stale data.
- Generate T-riseChart, automatically retain MAX/AVG fit coefficients, calculate current from
  MAX and a target rise, and generate Derating from AVG and the working-temperature parameters.
- Download an independent `.xlsx` containing Initial Data, T-riseChart and Derating, with native XY
  charts, polynomial trendlines, equations, R² and review provenance. No save-before-clear dialogs.
- Preserve other Tools functions and all project/Matrix/report authority.

## Calculation contract

The baseline is the user-supplied `T-rise&Derating Rev20161002.xlsm`, SHA-256
`2b2565e5d5db5d342d77db4eed21cccce37ff2b2e41c59e2a4c302b745b4f402`.
Its Initial Data is already manually cleaned; it is not evidence that every scanner has the same
column order or that zero-current rows should automatically be removed.

Within each current stage, adjacent relative change is at most 1% of the previous nonzero current.
Use the last row of each energized stable stage (at least two successive readings). Also retain the
last confirmed zero-current row immediately before energization, including a single zero reading.
Its measured temperature rise may be nonzero because other currents remain powered. A trailing
shutdown zero run has no following energized stage and is not selected. This is current stability,
not a thermal-equilibrium assertion. Subtract that row's ambient from each thermocouple. For each
sample take its highest rise, then plot the highest sample maximum and the mean of sample maxima.
Insert an origin point only when the first selected stage current is nonzero; never replace a real
zero-current reading's rise with zero. This origin-insertion rule applies in both intercept modes,
as in the VBA. Fit second-degree polynomials,
optionally constrained to zero intercept. Show six coefficient decimals; calculations use the
effective editable six-decimal values. Display R² as squared correlation of observed and fitted
values, matching desktop Excel's native polynomial trendline labels, including forced-zero fits.

Current uses the nonnegative increasing-branch root of `a I² + b I + c = target rise`.
Derating requires zero intercept and uses AVG coefficients with `rise = max temperature - ambient`.
The derated current is 80% of Basic current. Include the exact requested ambient annotation, even
when it falls between step points. Validate finite values, fit rank, roots, units and grouping.

Baseline expected stage source rows: 81, 131, 181, 231, 281, 331. MAX coefficients:
0.004677, 0.139598, 0; AVG: 0.004630, 0.122028, 0. Target 30 °C gives 66.5444574215 A.
At ambient 75 °C, max 105 °C: Basic 68.3888159321 A and 80% 54.7110527456 A.

## Boundaries and implementation sequence

1. Pure domain calculations and macro baseline tests; workbook reader/writer and native-chart checks.
2. Thin stateless Tools API; uploaded data and explicit preparation choices, with bounded inputs.
3. Data preparation and analysis UI with invalidation, reversible edits and real chart rendering.
4. Focused review, affected test matrix, production build, browser smoke and exported-file inspection.

Domain has no Office, HTTP or UI dependency. Infrastructure owns workbook IO. Application owns
preparation/validation and orchestration. Frontend API modules own transport; feature components own
the editable session. No new database persistence, Excel COM or full spreadsheet editor is required.

## Verification and risks

Use the real scanner fixture and independently saved macro outcomes, plus synthetic reordered
columns, replacement channels, power-drop/tail-zero rows, missing cells, unequal group sizes,
insufficient stages, invalid roots and stale-response cases. Check exported native chart series,
references, formulas and visual appearance; a successful ZIP export alone is insufficient.
Review numerical rounding, current scaling (scanner metadata may say VDC despite pre-applied gain),
human-confirmed anomalies and input-change invalidation. Browser smoke must exercise preparation,
both charts and download at wide and narrow widths. Final goal completion requires ready_for_close.

## Completed verification (2026-10-04)

- Python 3.11 ConnLab runtime: 62 affected backend tests passed, including the existing Tools and
  Office-boundary tests. One existing Starlette/httpx deprecation warning remains.
- Frontend full suite: 820 passed, one existing skip. After the final chart-label-only adjustment,
  the six affected temperature UI/transport tests passed again, and TypeScript/Vite build passed.
- Browser: imported the supplied 300-row scanner sheet; automatically suggested C:V, ambient W,
  current X, scale 1 and four thermocouples per sample. Explicit confirmation, both charts, editable
  coefficients, 66.54 A current, 68.39/54.71 A Derating and download feedback passed.
- A disposable workbook with a failed D channel and spare Y channel verified replacement at Sample
  1 / TC 2. Zero-current rows 100 and 331 were flagged, manually excluded, and the remaining 298 rows
  analyzed. Restoring rows invalidated prior results and required confirmation again.
- Desktop 1330×1182 and narrow 738×804 / 543×804 checked. No page-level horizontal overflow or browser
  error/warning logs in the final isolated smoke tab. See `design-qa.md` for visual comparisons.
- The final generated `.xlsx` was opened read-only in a separate hidden desktop Excel instance,
  both native charts rendered, trendline coefficients/R² checked, and formula values at 75°C matched
  the baseline. The supplied `.xlsm` SHA-256 remained unchanged; no VBA ran.
- Review was a sequential same-agent standards pass and specification pass, not independent-agent
  review. Resolved findings: filesystem ownership moved to the infrastructure port; Chinese scanner
  metadata excluded from channel guesses; JSON download header corrected; invalid duplicate OOXML
  line fills removed; R² aligned with native Excel; very small current scale rejected clearly;
  chart annotation spacing corrected. No remaining blocking finding.

### Standards review

Reviewed the working-tree diff against the repository dependency direction, explicit resource
ownership, small-scope changes and existing Tools contracts. Domain remains independent; temporary
files and workbook handles are infrastructure-owned; no new framework, persistence or COM runtime
dependency was introduced. The workbook port has a present testing/IO boundary, not speculative scope.
Outstanding findings: 0.

### Specification review

Checked the accepted third layout and subsequent mapping/exclusion requirements against the live
workflow and tests. Original files, macro safety, manual confirmation, current-stage baseline,
six-decimal coefficients, both real curves and independent export are covered. No old save-before-clear
dialog, arbitrary report writes or general-purpose spreadsheet editor was added. Operator save-location
and session-persistence limitations are explicit below. Outstanding blocking findings: 0.

Review summary: Standards 0 outstanding; Specification 0 outstanding blocking findings.

## Operator acceptance and limitations

1. Tools → Generate Temperature-Rise Curves → select scanner workbook.
2. Check sheet and ambient/current roles. Header/data row settings are hidden
   after successful recognition. On a recognition warning, inspect Source Rows, select a different
   sheet or enter the header/first/last rows and Apply Data Rows; this does not confirm the readings.
   Review the sample/channel summary and make exceptional column adjustments in Data Preview.
3. Identify records using A Scan and B Time. Select rows directly; Shift-click an endpoint checkbox
   selects the continuous block, including offscreen records. Exclude/restore as needed and Confirm
   Data. The separate row-range form is removed. Review notices, row selection labels and Stage Results
   use A-column scan identifiers; internal source-row keys remain unchanged. Warnings are never
   silently deleted; keeping flagged rows needs explicit acknowledgment.
4. Successful Confirm Data automatically generates T-riseChart and, when Zero Intercept is enabled,
   Derating. Review blockers stop the sequence. The Generate buttons remain available for manual
   retries or recalculation after edits; Calculate Current and Download Excel remain explicit actions.
   MAX/AVG a/b/c are retained automatically after chart generation for calculation/export without a
   separate coefficient table. Chart equations remain visible. Regeneration uses the new fit; changing
   source data clears coefficients and dependent results. Nonzero-intercept mode retains c as well.

Selections are an in-memory editing session, not a saved project. Refreshing or leaving the page
requires reimport; download the result before leaving. This is not a general cell editor: correct
individual source values in Excel, then reimport. All samples currently use the same confirmed
thermocouple count. Formula inputs are read from Excel's saved cached values; uncached formulas must
be recalculated and saved in Excel first. Files are bounded to 25 MB, expanded XML 100 MB, 20,000 rows,
256 columns and 1,000,000 cells. Current-stage stability is not proof of thermal equilibrium.

## Automatic coefficient refinement (2026-10-07)

The separate Get Coefficients action is removed. A successful analysis atomically updates the chart
and both six-decimal coefficient sets using the existing request-generation guard. Manual edits,
Zero Intercept behavior and dependent-result invalidation remain unchanged. No automatic download,
new API request, numerical algorithm change or source-workbook mutation is introduced.

- Regression evidence: before implementation, auto-population and direct calculation workflows
  failed; after implementation, all 44 affected frontend tests passed (19 page, 18 preview, two
  transport and five top-bar tests). TypeScript/Vite production build passed on the same source state.
- An isolated browser tab with disposable six-row scanner CSV verified automatic a/b/c values,
  direct 38.01 A calculation and both charts without coefficient retrieval; no warning/error logs.
  The tab was closed without operating the user's imported-data tab.
- Standards review: sequential same-agent review found no outstanding issue in hook ownership,
  async guarding, editable-state preservation, transport boundaries or scope. No new dependency.
- Specification review: button removed; both MAX and AVG export values default to the generated
  coefficients, remain editable, refresh on regeneration and clear on input changes. Tests cover
  nonzero c and late analysis after upload. No outstanding blocking finding.
- Residual boundary: the workbook exporter itself is unchanged; default and edited coefficient
  payloads are verified at the existing API seam. No new desktop Excel rendering run was required.

The browser smoke verified the download action, HTTP success and filename feedback; the in-app
automation did not expose a completed OS download event. Browser save location therefore remains
user/browser-controlled. The bytes from the same export service were separately validated in desktop
Excel. Native Excel charts are editable; the standalone workbook is a result snapshot, not a new
macro-driven editor or automatic report write-back.

## Report-ready Excel revision (2026-10-04)

The export now follows the supplied `DL-2026-07-115 T-Rise Summary and CR.xlsx` T-riseChart
layout and the pasted statistical table/chart on pages 10–11 of
`DL-2024-12-050 EK200 Connector Qualification Testing Report_Rev_A.docx`.
Both references are read-only design evidence, not calculation authority or report write targets.

- T-riseChart starts with the original endpoint readings, preserving all source values and original
  row traceability. There is no fabricated raw reading for the inserted origin. The next block computes
  channel rise with formulas using the confirmed channel order, selected ambient and current scale.
- The report table transposes applied current into columns and sample/thermocouple into rows.
  Sample maxima have blue shading; overall Max and Avg of Max have orange shading. Numeric display
  is one decimal, without rounding the underlying measurements/statistics. Borders, compact Arial
  text and wrapped labels support copying the table into Word.
- The adjacent native XY chart uses orange diamonds for Max and deep-blue squares for Avg of Max.
  Its bold, color-matched equation labels include the curve name and R². Labels are linked to
  worksheet LINEST/RSQ-equivalent formulas, not static text copied from the reference. Editing the
  endpoint cells recalculates statistics, fits and labels in desktop Excel. The original stage
  selection is fixed: editing a cell does not rerun ConnLab's stage detection or row confirmation.
- The visible y/a/b/c/x calculator remains editable. Default coefficients follow the fit rounded
  to six decimals; explicit MAX/AVG overrides supplied by the operator remain literal values.
  Changing y recomputes current. Manually overriding calculator coefficients does not change the
  chart fit. Derating retains its separate editable coefficient/temperature inputs and baseline.
- Excel's Name Box can select `KeyStageReadings`, `StageTemperatureRise`, `TemperatureRiseSummary`,
  `CurrentCalculator` and `AverageCoefficients`. Copy `TemperatureRiseSummary` and the chart
  separately into the report. A synthetic zero-current origin remains part of the summary but has
  no corresponding scanner row in the key-stage readings. Cell comments are not added to the export.
  Report pagination depends on sample/stage counts; a five-sample table may occupy a separate page.
- The copied `KeyStageReadings` data rows use the same yellow fill as the selected source endpoints
  in Initial Data. Their grey header, raw values and number formats are retained; the lower
  `StageTemperatureRise` calculation table and blank separator rows are not recolored.

Implementation stays in the workbook infrastructure: the gateway owns file lifecycle and caches,
and `temperature_rise_report_sheet.py` owns report sheet layout. No UI, API, domain calculation,
Office runtime dependency, automatic Word assembly or source-file mutation was introduced.

Revision acceptance includes export regression tests, existing temperature/Tools boundary coverage,
native Excel recalculation, actual Excel-to-Word table and chart paste, rendered visual inspection,
and SHA-256 preservation of all supplied source/reference files. Validated formula inputs have no
Excel errors. An operator entering invalid coefficients/negative discriminants directly in Excel
can still produce Excel formula errors; the export is not a replacement for input confirmation.

Revision verification: 56 affected backend tests passed (one existing Starlette/httpx deprecation
warning). Independent hidden desktop Excel instances opened the final export and three disposable
edge workbooks: unconstrained intercept, all-zero rise, and explicit coefficient overrides. All
formula cells were error-free; coefficients and R² matched the domain baseline. The exported table
and chart were actually pasted into a disposable Word document and its rendered pages inspected.
Baseline current remained 66.5444574215 A; changing y to 40°C gave 78.7522250715 A; editing an endpoint
updated the linked chart equation. Derating at 75°C remained 68.3888159321/54.7110527456 A.
All three source/reference SHA-256 digests were unchanged. Sequential same-agent standards and
specification review found no outstanding blocking issue. Frontend was untouched, so its earlier
validated tests/build remain applicable; they were not rerun for this export-only revision.

## Chart labels and navigation refinement (2026-10-05)

The Desktop reference workbook and screenshot establish the presentation for this narrow revision.
T-riseChart no longer freezes column A or its top row; Initial Data also has no frozen panes.
Derating's subsequent presentation refinement below also removes frozen panes. The two chart series
reference the summary's column-A names, `Max T-Rise` and
`Avg of max T-Rise on each sample`. Equation helper names also reference those cells, so editing a
summary name in Excel updates both the legend and its linked equation label. Orange and deep-blue
bold equation/R² labels are stacked inside the upper-left plot area, with room for the full AVG name.

No stage selection, numerical fit, calculator, Derating formula, source file, UI or API behavior changes.
Regression coverage checks the exported native references, cached names, pane state and label layout.
Acceptance additionally uses read-only desktop Excel to render the chart, check formula errors and
rename a summary label in memory; the supplied files must retain their SHA-256 digests. Manual label
repositioning may still be useful for unusual data distributions or names longer than the reference.

Verification completed: 57 affected backend tests passed (one existing Starlette/httpx deprecation).
Read-only desktop Excel showed no formula errors and no frozen panes on T-riseChart; both full labels
rendered without clipping. Renaming A51 updated the native series and equation without changing the
current result. Current and Derating baselines above remained unchanged, as did both source hashes.
Sequential same-agent review found Standards 0 / Specification 0 outstanding findings.

### Follow-up: aligned Scan / Time columns

Both endpoint tables now lead with A `扫描` and B `时间` (rows 1–7 and 12–18 for the six-stage
baseline). These contain the scanner's actual scan counter and time from the same endpoint record,
not the original Excel row number. Recognizable, unique Chinese/English identifier columns move to
the front; confirmed measurement roles take priority and all other source columns remain in relative
order. Missing or ambiguous identifier fields stay blank rather than borrowing a measurement or
inventing a scan/time. Original worksheet row numbers remain in Initial Data and the existing A1
provenance note. The time column is widened for the complete scanner timestamp.

Temperature channels begin at C in the rise block. Their references, ambient/current references and
the summary formulas use the source-to-export mapping, preserving replacement-channel order and
current scaling. Chart labels, panes, fit/calculator and Derating semantics remain unchanged.

Follow-up verification: RED checks reproduced the old Original Row/shifted identifier layout; final
61 affected tests passed, including Chinese/English headers, missing fields, reordered channels,
current scaling, literal source strings and Boolean metadata type preservation. Read-only desktop
Excel confirmed identical A/B values in both blocks, complete timestamps, no formula errors and
live recalculation after a C2 temperature edit. The rendered top 18 rows were visually inspected;
calculator/Derating baselines and source hashes remained unchanged. Same-agent exact-diff review
found no outstanding Standards or Specification issue.

### Follow-up: reference-style Derating chart

Derating now follows the supplied `T-rise&Derating.xlsm` and screenshot: pale-yellow chart area,
white plot, deep-red Basic and orange 80% Derating curves, bold title/axis labels, dashed gray grid,
5°C horizontal ticks and a bottom-left legend containing only the two curves. The vertical current
scale remains automatic rather than forcing the reference's 160 A maximum onto other measurements.
Selected ambient points use matching colored circles and bold one-decimal values to their right.
Only display precision changes; underlying numbers retain full precision. Derating has no frozen
row or column, while Initial Data retains its existing panes.

The blue dashed guide now ends at the selected Basic current instead of the initial maximum current.
Its endpoints reference the editable ambient/current cells, with cached values for immediate viewing.
Changing F2 in Excel moves the guide, markers and labels together. Existing coefficient and maximum
temperature inputs, domain calculations and T-riseChart presentation remain unchanged. The supplied
macro workbook is read-only style evidence; no macros are run and no source file is overwritten.

### Follow-up: compact Derating tables (2026-10-18)

Generated Derating sheets omit the former title/subtitle rows. Editable AVG coefficients and maximum
temperature occupy A1:D2; the ambient-point input/results sit at F1:H2 and the two live guide endpoints
at J1:K2. All three blocks and the main A5:C data table have thin borders and centered content.
Headers retain their fill; coefficient precision and selected current precision are unchanged.
Column widths are compact and sized for their headers/numbers; E and I are narrow group spacers.
Both native chart areas are 20% smaller in each dimension: T-riseChart is 18.8 × 11.2 cm and Derating
is 19.2 × 11.2 cm. Anchors, axis precision, native editability and source bindings are preserved.
Bottom clearance separates axis titles from legends at the reduced chart size without shrinking fonts.
For Word transfer, keep the chart's aspect ratio and fit it within the destination section's text
width, rather than stretching it or copying a worksheet screenshot. Current configured report
templates have 18.034 cm and 19.05 cm text widths; other templates must use their own page/margin
settings. The Excel chart remains native/editable, while the final Word placement must retain full
titles, equations, ticks and legends at readable size.
The native chart starts at E5 beside the main data table, rather than below stacked parameter blocks.
All formulas, caches and chart source references use the relocated inputs; changing F2 updates both
point results and guide endpoints. Source data and other worksheets are unchanged.

Earlier chart-style verification (before the compact-layout follow-up): the old frozen-pane
behavior failed two RED export checks before implementation.
The final affected backend matrix passed 62 tests (one existing Starlette/httpx deprecation warning).
An isolated, read-only desktop Excel instance rendered the final chart with labels 68.4 / 54.7 A at
75°C; changing F10 to 80°C updated the labels to 61.5 / 49.2 A and moved the guide to its Basic point.
No formula errors or frozen panes were present. The 66.5444574215 A T-rise calculator baseline and
full series names remained intact; source SHA-256 was unchanged. Sequential same-agent Standards
and Specification review found zero outstanding findings. No frontend files changed.

## Automatic data-region selection (2026-10-05)

Normal imports show only the file and sheet selector before column/channel review. Header Row,
First Data Row and Last Data Row are hidden, without an automatic-detection success notice.
Recognition requires one labelled scanner header and numeric measurement evidence. Numeric/Boolean
channel configuration and colon-ended key/value metadata are not headers. Missing headers, competing
headers/blocks or header-like error records require operator correction instead of a row-2 guess.

Readable but unidentified imports retain the source table, no accepted selection, and an actionable
region warning. Only then does the UI show blank row inputs and a paginated Source Rows preview.
Sheet selection stays available. Apply Data Rows validates the range and restores column/channel
review; Confirm Data is still required before chart generation. Failed corrections retain the entries,
and late responses cannot replace a newer upload.

Incomplete readings, internal blank rows, interruptions and zero-current tails inside the region are
retained for existing review/exclusion controls. A data range is not proof of valid readings, correct
roles or thermal stability. Unfamiliar labels, numeric channel headers and multiple tables can need
manual correction. This is not an Excel cell editor or a guarantee of recognition for every scanner.
Source workbooks and VBA are untouched.

Verification on the final implementation:

- Backend affected matrix: 56 passed, including recognition, ambiguous/error records, manual recovery,
  invalid ranges, numerical/export contracts and Tools boundaries. One existing Starlette/httpx
  deprecation warning remains.
- Frontend affected matrix: 16 passed, including hidden normal settings, exception-only correction,
  retry, stale-response isolation, multipart values, confirmation, channel/row changes and title-bar
  compatibility. TypeScript and Vite production build passed.
- The running localhost service passed unknown-header import/manual recovery with unchanged table
  values. A retained zero-current row blocked unacknowledged analysis. The supplied XLSM selected
  header 31, rows 32–331, ambient W, current X and 20 thermocouples; its 300 rows confirmed and produced
  unchanged MAX/AVG coefficients. Source SHA-256 was unchanged; no VBA ran.
- Live browser at 856×804 showed no row-number settings, no detection alert and no page-level overflow.
  Existing sheet/channel choices and the unconfirmed draft survived hot reload. The exception flow
  was checked through React interaction tests and the live API, not OS file-picker automation or a
  full screen-reader audit.

### Standards

Sequential same-agent review against AGENTS.md and the frontend guide: application owns recognition,
infrastructure retains file lifecycle, typed API owns transport, feature components own local inputs.
No new dependency, persistence, COM, source write or unrelated scope. Zero outstanding findings after
removing unused serialization code and simplifying single-region selection.

### Spec

Sequential same-agent review against the approved request: normal row controls hidden; missing or
ambiguous regions retain a recovery path; confirmation, role review and suspicious-row handling
remain. Fixed a false-header boundary that could skip error records; tests first reproduced it.
Scanner configuration and scan-control preambles also have regression protection. Zero outstanding
findings. Summary: Standards 0; Spec 0.

### Follow-up: remove the extra current-conversion UI

Re-reading the supplied VBA confirmed that `ampVal = ws.Cells(row, lastValidCol).Value` takes the
decimal current reading directly; the rise formula subtracts the penultimate ambient column from
each thermocouple reading. The `Scale To Amperes` input and its conversion guidance were a ConnLab
extension, not controls in that macro. They are now removed, with no hidden advanced replacement.
The three visible mapping fields are Ambient Column, Current Column and Thermocouples Per Sample.

The page uses the imported current values as amperes without adding conversion or rounding; the
selected ambient values remain the subtraction reference, not a way to calculate current. Inputs
must already contain the intended current measurements, as in the original macro workflow. Existing
transport/export scaling support is unchanged for API compatibility, but the normal page does not
offer it and all preparation/analysis/download requests fix it to the identity value 1, including
legacy non-identity suggestions. No source, numerical fit, report chart
style or row-review behavior changes.

Revision validation (2026-10-05): the new UI regression first failed while the extra input remained;
the legacy non-identity suggestion then failed at the preparation boundary. Both passed after removal
and identity enforcement. The final affected frontend matrix passed 17 tests (temperature page,
temperature API and TopBar); `tsc -b` and the Vite production build passed sequentially. The export
regression also verifies that an old non-identity suggestion cannot change downloaded results.
A read-only preparation check preserved decimal current 17.596362 and ambient 20.625 exactly.
Backend code did not change in this revision; the preceding 56-test backend matrix was not rerun.
The live 856×804 page has only three mapping fields, no conversion hint or input, no new alerts and
no horizontal overflow. Inspection preserved the user's imported workbook and current selections.

#### Revision Standards Review

Reviewed the exact revision diff: the common request boundary covers prepare, analyze and export;
source rows are not mutated, API compatibility remains, and the responsive grid follows the existing
control layout. Same-agent sequential review, not an independent review. Zero outstanding findings.

#### Revision Spec Review

Confirmed against the supplied VBA that direct decimal current readings and ambient subtraction are
retained. The extra input and hint are removed without an advanced replacement; channel review,
data confirmation and chart/export behavior remain. Zero outstanding findings. `git diff --check`
passed.

### Follow-up: temperature-page title (2026-10-06)

The temperature route now overrides the top-bar title with `Temperature Rise`; the parent `/tools`
route still uses `Tools`. The Tools return icon and the content heading `Temperature Rise & Derating`
are unchanged. Exact-diff self-review found no outstanding standards or specification issues.
Affected page/TopBar tests passed 15 tests and TypeScript `tsc -b frontend` passed. This literal title
change does not alter data, calculation or export behavior; backend and production build matrices
were not rerun.

The subsequent 2026-10-06 feedback removes the duplicate content heading and its wrapper/unused
styles. In AppShell the Initial Data panel is now the first content block; the top-bar title and
return icon remain. Standalone rendering still retains its return control. Exact-diff self-review
found no outstanding issues; 15 affected page/TopBar tests and `tsc -b frontend` passed on this state.

The next localized feedback also removes the `Initial Data` heading alone. Excel File selection,
mapping and data confirmation are unchanged. The exact diff has no outstanding review findings;
all 10 temperature-page tests passed, including absence of that heading and retention of Excel File.
No additional backend/build/typecheck/browser run was needed for this single literal removal.

### Follow-up: Load Initial Data control (2026-10-06)

The visible `Excel File` label and browser-localized file control are replaced with a native button
named `Load Initial Data`, opening a hidden file input accepting the same `.xls/.xlsx/.xlsm` formats.
The selected filename appears beside it and wraps on narrow screens. The feature hook still owns
import orchestration; cancelling selection preserves the imported workbook. Resetting the input's
value after selection allows choosing the same file again without duplicating draft state.

TDD evidence: the new page interaction test failed on the old visible label, then passed with the
new button. It verifies Enter activation, import, filename feedback, cancellation and same-file
reselection. Final QA passed 18 page/API/TopBar tests, TypeScript and Vite build sequentially.
Live browser inspection at 680×804 confirmed the button, hidden original control, absent Excel File
label, retained top title and no horizontal overflow. No workbook was loaded or cleared for that
inspection. Native OS chooser interaction was represented by the DOM boundary in tests, not
automated against the user's filesystem. Backend and calculation behavior are unchanged.

#### Standards

Same-agent exact-diff review: the control reuses page button/focus tokens, native keyboard semantics,
and the existing feature hook; no extra dependency, abstraction, request channel or source mutation.
The filename uses React text escaping. Zero outstanding findings.

#### Spec

Same-agent exact-diff review: the unwanted label and native chooser text are no longer visible;
`Load Initial Data` triggers the existing file selection/import path, retains filename feedback and
does not clear data on cancellation. Original data review remains. Zero outstanding findings.
Summary: Standards 0; Spec 0. `git diff --check` passed.

### Follow-up: header import action and scanner CSV (2026-10-06)

`Load Initial Data` now occupies the far right of the `Temperature Rise` title bar. The Tools return
icon stays next to the title; no duplicate load button or empty import card remains in the content.
The hidden file input, cancellation/reselection behavior and existing editable session are retained.
After import, the selected filename and data preparation controls remain in the content area.

CSV is another infrastructure input to the same table/preparation contract, not a separate calculation
path. The reader handles BOM-marked UTF-16, UTF-8 (with/without BOM) and GB18030, and recognizes comma,
tab or semicolon separators from parsed records including nonuniform scanner preambles. Quoted labels,
Chinese text, internal blank/error rows, source record positions and literal decimal readings are
retained. Unsupported encodings, malformed quotes and existing file/table resource limits fail clearly.
There is no rounding, new current conversion, automatic row deletion or source-file write. Download
remains a standalone macro-free `.xlsx` with the existing formulas and native charts.

The supplied `3A new.csv` is UTF-16 LE with tab-separated fields, 44 header/preamble records and 403
measurement records. Both the integration boundary and the running localhost service selected header
44 and rows 45–447. `3.0010263` and the timestamp suffix survive import, and source SHA-256 remains
`b2903c3ce08de283af8c02498dafccf4306da26aa528beac5a62b338e65824ff`. Its 30 thermocouples,
ambient channel 313 and four voltage-labelled signal channels still require operator role confirmation.
The 2026-10-07 refinement below recognizes the three sample prefixes and separates the four electrical
columns; automatic suggestions do not replace the final human confirmation.

TDD: 17 new backend cases and two updated/new header cases first failed for missing CSV support/header
placement. A first sandbox test run had temporary-directory permission errors; the authorized rerun
established the functional RED evidence. Final affected QA: 66 backend tests and 19 frontend tests
passed; TypeScript and Vite production build passed sequentially. One pre-existing Starlette/httpx
deprecation warning remains. Browser inspection at 680×804 verified one header load button aligned
with the title and at the right edge, hidden input accepting `.csv`, no empty import panel and no
page-level horizontal overflow. Native OS picker interactions are covered at the React DOM boundary,
not automated; the running import endpoint independently accepted the real attachment. Direct loopback
validation bypassed the host's HTTP proxy after its proxy-only request returned 502.

#### Standards

Same-agent focused exact-diff review: infrastructure owns decoding/CSV parsing and temporary resources;
the application retains filename validation and preparation; the page reuses the shared header portal,
native keyboard semantics and design tokens. No dependency, persistence, COM or external source mutation
was introduced. Existing bounds are checked during CSV parsing. Zero outstanding findings.

#### Spec

Same-agent focused exact-diff review: the action is in the top title row at the far right and accepts
the supplied scanner CSV; original Excel formats and human confirmation remain supported. Metadata,
missing/zero rows and decimal source readings are preserved; exported chart styles/calculations remain
unchanged. Multi-signal role assignment remains an explicit operator responsibility, not silently
inferred from the filename. Zero outstanding findings. Summary: Standards 0; Spec 0.

### Follow-up: compact import parameter row (2026-10-06)

Sheet Name, Ambient Column, Current Column and Thermocouples Per Sample now share one compact
four-field row below the selected filename. Labels use the existing sans font at 12px with a 4px
label/control gap; controls have 32px minimum height and the row has 8px field spacing. Native labels,
tab order, disabled states, sheet reload and mapping handlers remain unchanged. The exception-only
data-region recovery still has its sheet selector even when no mapping can be suggested.

The obsolete separate three-field mapping row and its breakpoint overrides are removed. On windows
too narrow for readable controls, only the parameter row can scroll horizontally; the page itself
does not expand or stack these four fields into additional rows.

Final verification: 19 existing page/API/TopBar tests, TypeScript and Vite build passed on the exact
implementation state. Browser read-only inspection at 856×804 showed all four labels/controls at the
same vertical position, a 58px parameter row, and no page-level horizontal overflow. The user's loaded
`3A new.csv`, Initial Data sheet, ambient 33, current 37 and TC count 1 survived hot reload unchanged.
No live selection was edited to test layout; narrow-width containment follows the local scroll rule,
not a newly run resized-browser check. Backend and calculation code did not change and were not rerun.
This reversible presentation-only regrouping reused behavioral regressions rather than adding tests
that freeze DOM grouping or CSS values.

#### Standards

Same-agent exact-diff review: display-only composition/styles remain in the temperature page/feature;
existing semantic labels, focus styles, tokens and single draft state are retained. No new abstraction,
request path, source mutation or business rule. Removed orphaned responsive mapping styles. Findings: 0.

#### Spec

Same-agent exact-diff review: the four named parameters share one compact row; filename feedback,
editing, sheet switching, exception recovery and data confirmation remain available. No unrelated
mapping or chart controls were altered. Findings: 0. Summary: Standards 0; Spec 0.

### Follow-up: labels beside controls (2026-10-06)

The four import fields now use inline label/control pairs: labels are on the left and narrower
native selects/number input are on the right. The last field is named `Thermocouples/Sample`, with a
56px number input. The entire parameter row remains horizontal; small windows retain local scrolling
instead of causing page overflow. Long selected channel/sheet text may be clipped in the narrow closed
select; full option text remains in its native menu. Source choices and numerical limits are unchanged.

Final verification: 19 page/API/TopBar tests passed, including the updated accessible label assertion;
TypeScript and Vite build passed sequentially. Read-only browser inspection at 856×804 confirmed a
40px parameter row, all controls aligned, and no row/page overflow. Imported CSV, sheet, ambient,
current and TC count survived unchanged. Existing correction, confirmation and export regressions
passed. Backend unchanged; no backend rerun or narrow-window resize check was needed for this local
presentation/copy adjustment. `git diff --check` passed.

#### Standards

Same-agent exact-diff review: scoped CSS handles alignment/width; native nested labels preserve
keyboard naming, draft handlers and disabled states. No additional state, request or dependency.
Findings: 0.

#### Spec

Same-agent exact-diff review: `Thermocouples/Sample` replaces the requested label, its narrowed editor
sits immediately to the right, and the three preceding fields receive the same treatment. No mapping,
calculation or source-selection semantics change. Findings: 0. Summary: Standards 0; Spec 0.

## Exception-only channel preparation (2026-10-07)

`temperature_channel_layout.py` owns automatic role/group suggestions; preparation validates the
confirmed assignments, while infrastructure retains source IO and workbook output. The UI displays
one compact sample/count summary and a unified Data Preview grid, not a
selector and three buttons for every thermocouple. All edits still invalidate derived results and
require Confirm Data; stale requests cannot reintroduce prior mappings/results.

- Scanner names such as `<1_H1A>` group channels by sample prefix, not hardware channel number or
  source adjacency. Equal named group sizes suggest Thermocouples/Sample. Interleaved columns are
  reordered logically without editing the upload. Unnamed spares remain available for explicit
  replacement/addition; inconsistent group sizes require explicit adjustment before confirmation.
  Unlabelled legacy inputs retain their existing fallback and operator review.
- Whole-column adjustment uses source-column checkboxes and a small column-header menu. Exclude a
  failed column, then move a spare before that source position. Exclude/restore and Undo are reversible;
  no separate replacement/add-channel editor, automatic source deletion or cell editor is introduced.
- Electrical headers, including scanner VDC labels, are role candidates. A unique varying candidate
  is suggested as the main current; ambiguous candidates show a role-confirmation warning. These
  labels do not prove a physical conversion: input values must already be amperes, as in the macro.
- Auxiliary currents stay in the original preview and are added with original values to the derived
  Initial Data export. They do not enter thermocouple statistics or the selected-current curve.
  Sustained powered auxiliary readings (at least two valid readings, all >=0.1 A, total spread <=1%)
  default Zero Intercept off. This is a default, not a lock: manual changes survive row/mapping edits.
  A newly imported file/sheet receives its own inferred default.
- For the selected current, `|I| < 0.1 A` is normalized to zero for calculation and flagged as unpowered.
  The original source value is unchanged. Warning rows remain highlighted; operators can select them
  and use the top Exclude Selected control, or leave them included when confirming. Entire records
  are not automatically discarded, because auxiliary currents may remain powered.

The supplied `3A new.csv` is a specific acceptance fixture: 3 samples x 10 channels, ambient AG,
main current AI, stable auxiliary AH/AJ/AK. These positions/counts are not hard-coded. Derating's
existing zero-intercept requirement remains unchanged; enabling it requires regenerating the fit.

Acceptance: backend suggestion/preparation/API/export tests, frontend move/undo/review/stale
response tests, TypeScript/build, and an isolated real-CSV browser check. Risks: header naming can be
ambiguous; a stable column alone is not evidence of thermal equilibrium; all samples still require
the same confirmed thermocouple count. Sources must remain unchanged and normal channels must not
reappear as individual editable cards.

### Verification and review

TDD captured failing tests for the former all-non-role-columns mapping, near-zero normalization,
unequal named groups and mixed electrical/group warnings before the corresponding fixes. Final
affected QA: 77 backend tests and 29 frontend tests passed; TypeScript and Vite build passed
sequentially. The existing Starlette/httpx deprecation warning remains; no dependency update was
introduced. The matrix includes original macro-fit, native chart/style/export and Tools regressions.

The isolated browser tab imported the real CSV: 403 records, 3 x 10 probes, AG ambient, AI selected
current, and auxiliary AH/AJ/AK. Zero Intercept defaulted off. Confirm Data flagged 47 unpowered
records; explicit selection/exclusion and reconfirmation left 356 readings. T-riseChart and
coefficient retrieval succeeded; the effective MAX coefficients yielded 21.58 A at 30°C. Excluding
and restoring one channel cleared old results and required confirmation again. The 1280 x 720 normal
view and 543 x 804 exception editor were inspected; no page-level horizontal overflow or browser
error/warning logs were found. Temporary viewport settings were reset; the user's original tab was
not reimported or cleared.

The browser displayed `3A new_T-rise_Derating.xlsx` after download; OS download completion was not
exposed by the in-app browser. A separate disposable export from the same service was inspected:
all retained auxiliary values match every included source row, and the native T-riseChart has no
frozen panes. This is file-structure/value verification, not a new desktop-Excel rendering claim.
The real source SHA-256 remains
`b2903c3ce08de283af8c02498dafccf4306da26aa528beac5a62b338e65824ff`.

Standards review: same-agent sequential exact-diff check of ownership, public seams, reversible
editing, escaping, resource lifecycle and scope. Suggestions/preparation are application-owned;
workbook IO remains infrastructure-owned; no new dependency, persistence, COM or source mutation.
Zero outstanding findings.

Specification review: separate same-agent pass against the confirmed sample/current rules and
exception-only UI. Unequal named group counts now block untouched suggestions even when the total
is divisible; electrical ambiguity warnings are separate from mapping warnings, so a temperature
edit cannot hide an unresolved current-role warning. Stable auxiliaries are retained/not plotted,
manual intercept changes survive edits, and unpowered rows are not silently deleted. Derating's
existing zero-intercept prerequisite remains explicit. Zero outstanding blocking findings.

## Unchecked Zero Intercept correction — 2026-10-07

The supplied `C:/Users/White/Desktop/T-rise&Derating Rev20161002.xlsm` was read as a ZIP/OLE
container; VBA was extracted as text, never executed. In the extracted nonblank `GenarateChart`
listing, lines 780–799 retain the last zero-current row before energization; lines 854–865 subtract
its actual ambient. Lines 883–903 insert a zero column only if no zero stage is present, independently
of the checkbox. Lines 1019–1021 / 1044–1046 set the polynomial intercept only when checked;
lines 405–419 / 463–477 retain the fitted constant when unchecked.

The defect was earlier than the regression solver: ConnLab discarded all zero-current endpoints,
so a measured heated baseline became an invented `(0, 0)` point. The existing unconstrained solver,
native trendline automatic intercept and `LINEST(...,TRUE)` were already correct. The fix preserves
the last confirmed zero reading before an energized stage, including a single reading, and uses its
actual sample maxima/average. Shutdown tails remain unselected. Without a recorded zero endpoint,
the macro's synthetic-origin fallback remains in both modes. Checked mode still constrains c to zero
without falsifying the measured point. No automatic row restoration/deletion is introduced.

Exported stage current formulas now apply the same strict `|I| < 0.1 A` rule as preparation. Raw
scanner values remain unchanged; Excel recalculation cannot turn a normalized baseline back into
0.009999 A. The shared cutoff is a domain constant, not an Office dependency.

Important operator boundary: in a multi-current test, the pre-energization zero-current baseline can
have genuine nonzero heating. Do not exclude every unpowered row indiscriminately; retain the intended
baseline and separately review interruption/shutdown rows. Existing browser exclusions/results are
not rewritten. Confirm the reviewed data and regenerate the curve to obtain the corrected result.

### Changed paths in this revision

- `backend/domain/temperature_rise.py`: measured zero-run endpoints.
- `backend/domain/temperature_data.py`: shared unpowered cutoff.
- `backend/application/temperature_data_preparation.py`: consume that cutoff, unchanged preparation behavior.
- `backend/infrastructure/office/temperature_rise_report_sheet.py`: matching editable Excel current formulas.
- `tests/unit/test_temperature_rise_calculations.py`: real zero baseline, single reading, checked/unchecked and tail cases.
- `tests/unit/test_temperature_workbook_gateway.py`: source-preserving baseline, native chart and formula caches.
- `tests/integration/test_tools_temperature_api.py`: import/analyze/download nonzero-intercept round trip.
- `docs/temperature_rise_tool.md`: corrected numerical contract and acceptance record.

### Standards

Separate same-agent pass: 0 outstanding findings. Domain remains independent of Office/API/UI;
existing public seams and dependency direction are preserved. No dependency, source mutation or
authoritative write was introduced. `git diff --check` passed.

### Spec

Separate same-agent pass: 0 outstanding findings. Compared checkbox behavior, zero-stage capture,
ambient subtraction, fallback origin, coefficients and Excel series against the actual VBA, not an
assumed intercept-only change. Derating's existing prerequisite is outside this correction and unchanged.

### Validation

- RED: three numerical cases returned a synthetic `source_row=None` instead of the measured baseline;
  the native export case started with scan 4 instead of scan 2. GREEN: all four passed after correction.
- Final affected backend matrix: **82 passed**, one existing Starlette/httpx deprecation warning.
  Includes preparation, original forced-zero macro coefficients, numerical analysis, workbook gateway
  and API integration. No frontend source changed; frontend build/tests were not redundantly rerun.
- Supplied 3A CSV, with reviewed rows retained: real baseline row 91, current 0 A, Max 26.544°C,
  Avg of sample maxima 24.572°C. Unchecked fits were Max `(0.017673, -0.368444, 27.406090)` and
  Avg `(0.018148, -0.349932, 25.355670)`. Desktop Excel opened only the independently generated copy
  read-only with macros disabled. Recalculated coefficients matched ConnLab within 1e-8, both series
  preserved the measured zero point, and intercept remained automatic. Native chart PNG inspected.
  These are all-row verification results, not acceptance of the source's thermal equilibrium or R².
- Live `localhost:5173` API probe returned the measured baseline and Max `(0.01, 0.2, 2)`;
  the active service has loaded the correction. No browser draft or existing result was overwritten.
- CSV SHA256 stayed `b2903c3ce08de283af8c02498dafccf4306da26aa528beac5a62b338e65824ff`;
  XLSM stayed `2b2565e5d5db5d342d77db4eed21cccce37ff2b2e41c59e2a4c302b745b4f402`.

Methods used: diagnosing-bugs, tdd, code-review and spreadsheets. Review and QA were sequential
passes by the same agent, not independent agents. Sample export is a disposable QA copy in the
task visualization directory; no original CSV/XLSM or report was modified.

## Unified raw-data editor — selected mock 2 (2026-10-07)

The separate ChannelMapping component, View Channels, Other Current Columns and dedicated
replacement controls are removed. Data Preview now exposes every original source column in one
spreadsheet, with stable source letters, row/temperature-column checkboxes, grouped temperature headings,
explicit Ambient/Plot Current/retained auxiliary-current roles, and one compact action toolbar.

- Select rows or columns, then Exclude Selected or Restore; selections are mutually exclusive.
  Exclusions stay visible in muted gray. Source uploads and cell values are never rewritten.
- For a failed thermocouple, exclude the bad source column, select the spare, and use its column
  header menu to Move Before the failed source position. Multiple selected temperatures move as
  an ordered block. Moving an unused spare activates its whole column in the prepared selection.
- Undo restores the previous row exclusions, temperature ordering and editor state. Later manual
  ambient/current/sample-count decisions clear old undo history rather than silently reverting roles.
- Incomplete blocks show Pending Grouping and disable Confirm Data; restore/move the needed columns
  or explicitly correct the equal count. A complete new order is chunked by the confirmed count,
  with visible sample/TC assignments for operator review. The UI cannot infer the intended physical
  wiring of a spare; the operator must place it in the correct position before confirmation.
- A/B scan/time indexes, ambient, plot current and recognized auxiliary electrical roles cannot be excluded/moved as
  thermocouples. Non-temperature metadata exclusions are editor-only; calculation input continues
  to use ordered temperature column IDs and excluded row IDs. Auxiliary originals remain retained.
- Continuous virtual scrolling replaces pagination: all source rows are reachable in one scroll
  region with a fixed header; only nearby rows are mounted. Optional explicit range selection
  remains available. Unpowered-row selection stays explicit, preserving the measured zero baseline.
- Every committed data edit invalidates confirmation and downstream calculations through the
  existing hook. No API contract, formula, native Excel export or Derating behavior changed.

Changed paths: `TemperatureRisePage.tsx` and its tests; temperature feature `DataPreview`,
`ColumnActions`, `useDataGridEditing`, `sourceColumns`, `DataRegionCorrection`, stylesheet and grid
tests; removed `ChannelMapping.tsx`; this document and project-root `design-qa.md`.

### Verification

TDD RED: four unified-editor cases failed against the former row-only preview before implementation.
Final affected QA: **27 frontend tests passed** (grid, page, API adapter and TopBar); TypeScript and
Vite build passed sequentially on the final source/test bytes. No backend source changed in this
revision, so the previously recorded 82-test numerical/export matrix was not repeated.

Isolated browser: actual CSV imports as 403 rows, 3×10 probes, AG ambient / AI current and stable
AH/AJ/AK retained, Zero Intercept off. Explicitly keeping flagged rows generates the real baseline
Max 26.544°C / Avg 24.572°C. Subsequent exclusions clear the old curve. A disposable 2×2-probe CSV
verifies excluding D, moving spare I before D, confirmation, curve generation, and two-step Undo;
both intermediate and restored orders are correct. Console error/warning logs: zero. Desktop,
856×804 and 543×804 views inspected; no page overflow, menu stays in the viewport. User tab untouched,
temporary viewport reset, QA tab closed. No native Excel rendering or new screen-reader session.

### Standards

Same-agent exact-diff pass: existing API selection contract and single calculation state reused;
editor ordering/history and popup lifecycle remain feature-owned. React escapes source headers;
event listeners clean up, focus returns, source arrays are not mutated, no dependency/Office/COM or
filesystem mutation path added. Obsolete mapping UI/styles removed. Zero outstanding findings.

### Spec

Separate same-agent pass: selected mock's unified checkbox grid and small header move menu replace
the requested redundant panels. Row/column exclusion, restoration, whole spare moves, multi-column
ordering, Undo, incomplete-group confirmation guard, role protection and downstream invalidation
are verified. Existing analysis panels are intentionally retained; this is a preparation-editor
revision, not a chart-control rewrite. Visual comparison passed after a header-readability fix.
Zero outstanding blocking findings. Summary: Standards 0; Spec 0.

Methods used: tdd, image-to-code, design-qa and code-review. Execution/review/QA were sequential
passes by one agent; no independent-agent review is claimed. Residual domain risk: scanner header
ambiguity and physical channel positions still require human confirmation before calculating.

## Continuous preview and Shift selection (2026-10-07)

- Previous/Next/Page controls are removed. The source grid uses a feature-owned row-window hook,
  a fixed single-line row height, measured viewport/header height, and native vertical/horizontal
  scrollbars. It adds no dependency and does not change loaded values or calculation/export inputs.
- Click a row checkbox to toggle it and establish a range anchor. Shift-click
  another row selects the inclusive interval in either direction, including offscreen rows; clicking
  a checked endpoint with Shift clears that interval. Existing unrelated selections remain intact.
  Shift+Space on a row checkbox works too. Column selection, bulk selection, a committed edit or Undo
  clears the anchor, preventing an old range from leaking into the next operation.
- The header checkbox now explicitly selects ALL source rows, not merely mounted/visible rows.
  A partial selection shows its mixed state. Selection persists as original row IDs while scrolling.
  Exclude, Restore and Undo retain their existing draft/confirmation invalidation semantics.
- Large-range checks use sets; source-column and issue lookup data are cached across scrolling.
  Long source cells remain available in hover titles, rather than expanding the fixed-height rows.
  Native browser Find/copy only sees mounted rows; use original row IDs/range selection for distant
  intervals. Excel export still consumes the complete confirmed data, not the rendered row window.

Validation: three new continuous/range cases failed against the old preview before implementation;
all five new cases pass along with the six existing editor cases. Browser QA uses a disposable
20,000-row CSV (19,999 data rows): 774→800 selects 27 rows, exclusion updates the count and Undo
restores it; End reaches original row 20,000 with a fixed header and only 17 rows mounted at the
bottom. Final affected QA: 32 tests across editor/page/API/TopBar passed; TypeScript and Vite build
passed sequentially. The final checkbox change was also rechecked in the browser. At 543×804,
scrolling remains local with no page-width overflow; the temporary viewport was reset. Separate
same-agent Standards and Spec exact-diff passes found no outstanding issues. The User's original
tab and source files are not reimported or edited. Numerical fitting,
Office export and backend code are unchanged. No new screen-reader session is claimed.

## Compact preview and fixed scan/time indexes (2026-10-07)

- Original Row is removed from the displayed grid. A (scan) and B (time) are permanent indexes:
  no column checkboxes or move actions, and they stay visible during horizontal scrolling. They
  remain outside the temperature-channel grouping and are not chart series. Internal source row
  IDs are retained for issue matching, exclusions and API compatibility; the optional range input
  still uses source worksheet row numbers, explicitly identified by its tooltip.
- Fixed widths are 32 px for row selection, 64 px for scan, 184 px for timestamps, and 104 px per
  remaining channel. Long values/headers remain available in hover titles; the grid scrolls locally.
- Clicking any data cell highlights its entire row without selecting it or changing preparation,
  confirmation or calculated results. Keyboard focus on a row control also highlights it. Excluded
  and review rows keep their status background, with an active-row outline. Highlight persists
  across virtual scrolling; batch actions and Shift ranges continue to use the row checkboxes.
- Changed paths: `DataPreview.tsx` and its tests, `useDataGridEditing.ts`, `sourceColumns.ts`,
  `temperature.css`, `TemperatureRisePage.test.tsx`, and this document. No backend, source upload,
  native workbook export, curve calculation or Derating implementation changed.

### Verification and review

TDD: the three new index/highlight regressions failed before implementation, together with the
updated excluded-row status assertion; all 14 grid tests then passed. The first affected matrix
identified three page-test failures because its former fixture put a thermocouple in B. The fixture
now models the confirmed A scan / B time structure, with every spare-move, restore, Undo and
downstream-invalidation assertion retained at the corresponding shifted source column IDs.
Final affected QA: **35 tests passed** across grid/page/API/TopBar; TypeScript and Vite build passed
sequentially after the final source/test changes.

Isolated browser QA imported the disposable 19,999-data-row CSV: Original Row absent, A/B controls
absent, compact widths verified, A/B positions unchanged after horizontal scrolling, cell clicks
highlighted all cells without checking a row, and Shift 2→10 selected nine rows. Exclusion and Undo
preserved their behavior and status display. At 543×804, scan/time remain visible and page-width
overflow is absent. Console warnings/errors: zero. Temporary viewport reset and QA tab closed;
the User's imported tab and source files were not reimported or edited. No new screen-reader or
native Excel rendering session is claimed.

Separate same-agent code-review passes: Standards 0 outstanding findings (feature-owned local
highlight, protected indexes, no data mutation/dependency or API changes); Spec 0 outstanding
findings (removed duplicate index, compact frozen A/B, whole-row highlight and retained bulk
selection). Review and QA are sequential passes by one agent, not independent-agent evidence.
Methods: tdd and code-review. Residual limitation: native browser Find/copy sees only mounted rows,
as with the existing virtual preview; full confirmed data still reaches calculation/export.

## Context actions and unit-aware compact preview (2026-10-07)

- Column-arrow buttons are removed. Click a temperature header to select it, or use checkboxes
  for a block; right-click a header or its data cell to open Exclude/Restore/Move Before operations.
  Right-click inside a selected block preserves it; an unselected column becomes the selection.
  Focusable headers also support Shift+F10/the context-menu key, Escape and focus return. Existing
  protected A/B, ambient and current roles, whole-column moves, Undo and Shift row selection remain.
- Explicit trailing scanner units take precedence: `(C)` (including temperature spelling variants)
  is temperature; `(VDC)` is current. Existing V/A/mA spellings remain supported. Ambient choices
  contain only temperature columns; Current choices contain only electrical columns. Untagged legacy
  workbooks retain imported/confirmed role suggestions. If an imported role contradicts an explicit
  unit, show an empty choice and an actionable alert, blocking Confirm until corrected rather than
  silently choosing a different calculation column.
- Visible headers/options omit unit suffixes and normal per-channel Sample/TC labels. Sample group
  bands and exceptional/role markers remain; complete original headers are available on hover.
- Temperature readings display one decimal and current readings two. Scan/time indexes, malformed
  readings and blanks retain their source text. Display rounding does not rewrite source arrays,
  selected column IDs, near-zero review rules, calculation requests or exported numeric data.
- Content-based column widths replace the previous fixed channel width: compute from all formatted
  readings and header lines once per imported region/role change, not per scroll/highlight/selection.
  Keep the 32 px row selector and existing virtual row window; data values are not width-capped.

### Verification and review

TDD: four new public-behavior cases recorded RED then GREEN: context-menu/block selection,
display-only rounding and clean headers, unit-filtered selectors/exact submitted data, and correction
of an explicit-unit conflict. Existing operation tests use the new context-menu interaction while
retaining their move/exclusion/restoration/Undo/invalidation assertions. Final affected matrix:
**39 tests passed** across DataPreview, TemperatureRisePage, temperature API and TopBar; TypeScript
and Vite production build passed sequentially on the final source/test bytes.

Isolated browser QA with actual `3A new.csv`: 403 rows, three samples × ten thermocouples,
31 temperature choices, four current choices, AG ambient/AI curve current and stable AH/AJ/AK
retained with Zero Intercept off. Multi-column right-click, keyboard Move Before and Undo passed.
Temperature columns measure 56 px for this file, scan 44 px and time 186 px; no mounted data cells
are clipped. At 543×804, local scrolling keeps A/B in place, page-width overflow is absent and the
right-click popup remains within the viewport. Console warnings/errors: zero. Source CSV SHA256
remains `b2903c3ce08de283af8c02498dafccf4306da26aa528beac5a62b338e65824ff`.
Temporary viewport reset and QA tab closed; the User's tab was not operated or reimported.

Same-agent Standards pass: shared feature-owned unit/presentation rules, cached sizing and existing
selection state reused; no backend/API/dependency/Office/source-file mutation introduced. Spec pass:
right-click operation parity, filtered roles, precision-only display, compact full readings and
removed redundant per-TC labels match the request. Both exact-diff passes have zero outstanding
findings; sequential passes do not claim independent-agent review. Methods: tdd and code-review.
Residual limitation: untagged/ambiguous scanner headers still require role confirmation; native
Find/copy still sees only mounted virtual rows. No native Excel or new screen-reader session claimed.

Changed paths for this revision: `frontend/src/features/temperature/ColumnActions.tsx`,
`DataPreview.tsx`, `DataPreview.test.tsx`, `sourceColumns.ts`, new `sourcePresentation.ts`,
`useDataGridEditing.ts`, `temperature.css`, `frontend/src/pages/TemperatureRisePage.tsx`, its test,
and this document. The sole task-board writer records lifecycle evidence separately.

## Protected header cleanup (2026-10-07)

Ambient and all electrical/current headers omit their non-operable checkboxes and repeated gray
Ambient/Current/Retained captions. The unit follows the channel number on the first line, for example
`318 (°C)` with `Ambient T` beneath, or `320 (A)` with `Current` beneath. Untagged headers without a
channel number append the unit to their single title line. This is preview-only: original scanner
units remain in hover titles/source data, selector options and calculation/export are unchanged.
Dynamic widths include the annotated number line; editable temperature headers retain selection,
right-click and exceptional grouping/exclusion markers.

TDD recorded RED/GREEN for protected-header units/control removal and the subsequent User correction
placing units after the number. The role-change regression now expects that placement while retaining
all protection and Undo checks. Final affected QA: **41 tests passed** (18 editor, 16 page, 2 API,
5 TopBar); TypeScript/Vite build passed on final source/test bytes. Isolated browser checks use actual
`3A new.csv` and a clearly named disposable example CSV with 318 ambient/320 current: unit lines,
absent inactive controls and repeated captions verified; console warnings/errors zero. Source files
and User tab not operated; QA tab closed. No native Excel or new screen-reader session.

Standards: same-agent exact-diff review found zero outstanding issues; existing protected-column
decision and feature-owned presentation seam reused, no new state/dependency/API changes. Spec:
separate same-agent pass found zero outstanding issues; Celsius for ambient, amperes for all current
columns, exact number-line placement and unchanged preparation behavior match the corrected request.
Methods: tdd and code-review; no independent-agent review claimed. Changed paths: DataPreview.tsx,
sourcePresentation.ts, DataPreview.test.tsx, TemperatureRisePage.test.tsx and this document; lifecycle
record via the sole board writer. Existing untagged-source confirmation limitation remains.

## Scan-based feedback and range-form removal (2026-10-08)

Removed Select Rows By Range, its parser/state and unused styles. Data Needs Review notices,
row-checkbox labels/hover feedback, row-specific operation errors and Stage Results now identify
records using A-column Scan, not physical file row numbers. String identifiers retain leading zeros.
A missing scan displays Unavailable instead of inventing a file-row identifier; synthetic chart
origins remain Origin. Source-row keys still drive exclusion/restoration and API requests, so repeated
or nonconsecutive scan identifiers do not change the records being edited. Worksheet-boundary recovery
settings and exported source-row provenance intentionally remain unchanged.

TDD: four new behavioral checks failed before implementation; the final affected frontend matrix
passed **47 tests** (22 page, 18 preview, 2 API, 5 TopBar). TypeScript/Vite production build passed on
the final source/test bytes. Tests cover leading-zero scans, missing scans, API error presentation,
Stage Results, unchanged exclusion keys, reversible Shift selection and stale-response protections.
An isolated browser with disposable seven-record CSV verified Scan 774 review feedback, absence of
the range form, checkbox hover labels, Select Unpowered Rows, and Shift selection through Scan 800
across scan-number gaps. Console warnings/errors: zero. QA tab closed; User tab/data not operated.

Standards review (same-agent exact diff): presentation-only mapping is shared at the temperature
feature seam; no backend/API/dependency/source-workbook mutation or editing-key change. Zero
outstanding findings. Specification review (separate sequential same-agent pass): removed area,
scan-based notices and preserved selection/exclusion behavior match the request. Zero outstanding
findings; no independent-agent review claimed. Methods: tdd and code-review. Residual limitation:
plain API errors use the existing Row N prefix contract; missing scan values are visibly unavailable.

Changed paths: `frontend/src/features/temperature/DataPreview.tsx`,
`frontend/src/features/temperature/DataPreview.test.tsx`,
`frontend/src/features/temperature/TemperatureCharts.tsx`,
`frontend/src/features/temperature/sourceScan.ts`,
`frontend/src/features/temperature/temperature.css`,
`frontend/src/pages/TemperatureRisePage.tsx`,
`frontend/src/pages/TemperatureRisePage.test.tsx` and `docs/temperature_rise_tool.md`.
The existing task also retains its earlier `frontend/src/features/temperature/useTemperatureTool.ts`
coefficient change; the sole board writer records cumulative completion evidence separately.

## Automatic generation after confirmation (2026-10-08)

Confirm Data now awaits successful, current preparation before generating T-riseChart. A successful
fit populates both coefficient sets; if Zero Intercept is enabled, Derating follows using that new
AVG fit rounded to the same six decimals displayed/exported and the current working-temperature
settings. Nonzero-intercept mode generates temperature rise only, matching existing Derating button
eligibility. Manual Generate actions remain available and retain their previous scope: a manual
T-riseChart regeneration clears downstream results but does not itself auto-generate Derating.
Calculate Current, download, source-file mutation and worksheet calculations are not added to the chain.

The existing request-generation guard now also controls continuation: obsolete or failed stages
return no result and cannot launch the next stage. Busy/error feedback uses the existing stage labels.
Review warnings still require an explicit keep/exclude choice. A Derating error retains the successful
temperature-rise chart and coefficients for correction/retry; any input invalidation still clears
the affected results. Recognition/import alone never generates charts.

TDD recorded five expected failures before implementation and GREEN after the hook change. Final
affected matrix: **55 passed** (30 page, 18 preview, 2 API, 5 TopBar); TypeScript/Vite build passed
sequentially on the final source/test bytes. Coverage includes ordered stages, fresh rounded AVG
coefficients, custom settings, nonzero-intercept skipping, review blocking, each-stage failure/retry,
late responses during preparation/analysis/Derating and page unmount. Isolated browser verification
with the disposable scanner CSV confirmed both charts after one accepted confirmation and only
temperature rise with Zero Intercept off; console warnings/errors zero. The QA tab was closed and
the User's imported-data tab was not operated. No new native Excel/export-rendering check: exporter,
API and numerical algorithms are unchanged.

### Standards

Sequential same-agent exact-diff pass: orchestration stays in the existing feature hook, preserves
request invalidation, reuses Derating transport/settings and adds no dependency or second state
channel. Zero outstanding findings.

### Spec

Separate same-agent pass: automatic generation occurs only after successful explicit confirmation;
Derating uses existing eligibility and the newly generated coefficients; failures and obsolete work
stop continuation, and manual correction/retry remains available. No unsolicited current calculation
or download. Zero outstanding findings. Methods: tdd and code-review; not independent-agent review.

Changed paths for this revision: `frontend/src/features/temperature/useTemperatureTool.ts`,
`frontend/src/pages/TemperatureRisePage.test.tsx` and `docs/temperature_rise_tool.md`; lifecycle records
use the sole board writer. Residual behavior is intentional: invalid Derating parameter values produce
the same actionable validation error as the enabled manual action, without discarding the rise chart.

## Coefficient display removal (2026-10-08)

Removed the entire Polynomial Coefficients MAX/AVG a/b/c input table, its unused edit action and
table-specific styles. The fit equations and R² below the chart remain. Internal generated coefficients,
six-decimal calculation/export values, confirmation-triggered charts and manual Generate retries are
unchanged. On-page coefficient editing is intentionally removed with the table; source preparation,
Zero Intercept, target-rise and Derating parameter editing remain available. The exporter and native
Excel artifacts are unchanged.

TDD: the absence/continued-calculation-and-export regression failed before removal and passed after.
Existing field-based checks now verify equations, regenerated calculation payloads, parameter
invalidation and exported fits at the page/API seam. Final affected matrix **55 passed** (30 page,
18 preview, 2 API, 5 TopBar); TypeScript/Vite production build passed on final source/test bytes.
An isolated browser with disposable scanner CSV verified no coefficient table before/after analysis,
both automatic charts, retained equations and current calculation at 38.01 A. Console warnings/errors
zero; QA tab closed, User tab not operated. No new native Excel rendering check because exporter and
numerical algorithms are unchanged; generated coefficient payloads remain covered by regression tests.

### Standards

Same-agent exact-diff review: display-only controls/styles and their single unused handler are removed;
feature-owned coefficient state and async invalidation remain. No new dependencies, API or backend
changes. Zero outstanding findings.

### Spec

Separate sequential same-agent review: entire selected block removed, charts move up naturally, and
calculation, auto-generation, equation labels and Excel export retain their prior contracts. No extra
collapsed editor or replacement panel. Zero outstanding findings. Methods: tdd and code-review;
no independent-agent review claimed.

Changed paths: `frontend/src/pages/TemperatureRisePage.tsx`,
`frontend/src/pages/TemperatureRisePage.test.tsx`,
`frontend/src/features/temperature/useTemperatureTool.ts`,
`frontend/src/features/temperature/temperature.css` and `docs/temperature_rise_tool.md`; task state
recorded through the sole board writer. No new residual risk identified beyond the existing tool limits.

## Outside-editor highlight dismissal (2026-10-11)

Pointer clicks outside Data Preview clear only the active-row highlight and temporary column
selection/column Shift anchor. Checked rows and the row Shift anchor remain. The editor section,
measurement-name inputs, toolbar controls and the portalled context menu (including its right-side
destination submenu) share the same interaction boundary. Normal exclude/restore/move actions still
consume their selection after executing. No source data, grouping, role or export contracts change.

Two interaction regressions failed before implementation and passed afterward. The final affected
frontend matrix covers outside dismissal, retained row ranges, name editing and actual toolbar/menu
actions. Validation: 70 frontend tests and the sequential TypeScript/Vite build passed. Browser visual
verification is not claimed; the browser runtime previously failed with EPERM. No backend rerun is
needed for this UI-only refinement.

### Standards

Sequential same-agent exact-diff review: state remains in the existing feature hook, listeners clean
up on unmount, and a shared DOM ref recognizes the menu without global selectors or new dependencies.
Zero outstanding findings.

### Spec

Separate same-agent review: outside clicks dismiss temporary highlights without removing checked
rows or their range anchor; internal and portalled interactions do not preempt actions. Zero
outstanding findings. Methods: tdd and code-review; not independent-agent review.

Changed paths: `DataPreview.tsx`, `useDataGridEditing.ts`, `ColumnActions.tsx` and
`DataPreview.test.tsx` under `frontend/src/features/temperature/`, plus this document and the
sole-writer task-board lifecycle record.

## Ambient and unused-temperature column presentation (2026-10-11)

The current Ambient Column uses a pale amber header and data-cell background and remains protected
from selection/exclusion/movement. Other non-excluded temperature columns outside the current
sample calculation use a pale cyan tint. This follows the selected role and effective temperature
list, not scanner channel 318 or the editable measurement name. Header tooltips/accessibility
descriptions distinguish protected ambient, unused temperature, excluded and sample states without
adding another visible caption row.

Unused columns retain the existing normal select/exclude/restore/move controls. Restoring an unused
column does not silently include it in samples; explicit movement into the effective block activates
it and partitions samples by the current order. Excluded columns retain their exclusion styling;
selection, active-row and review styling take precedence over passive role tinting.

TDD: the role/interaction regression failed before implementation, then passed. The regression
switches ambient roles, protects the new ambient, selects/excludes/restores the former ambient,
moves it into a complete two-sample layout, and verifies the outgoing channel/group selection.
Final affected validation: 71 frontend tests and sequential TypeScript/Vite build passed. Browser
connection was attempted but its bundled runtime import failed with EPERM; visual QA remains
unverified. No backend/source/export changes or native Excel rerun in this refinement.

### Standards

Same-agent exact-diff review: derived display state reuses existing role/type/selection authority;
no new state channel, dependency or numerical logic. CSS keeps transient/excluded/review states
above passive role colors. Zero outstanding findings.

### Spec

Separate sequential same-agent review: current ambient stays protected, unused temperatures receive
distinct colors and retain normal operations, and role changes update presentation. Zero outstanding
findings. Methods: tdd and code-review; no independent-agent review claimed.

Changed paths: `frontend/src/features/temperature/DataPreview.tsx`, `DataPreview.test.tsx` and
`temperature.css` in that feature, this document and the sole-writer task-board record.

## Compact unpowered review messages (2026-10-11)

The review display abbreviates zero-current warnings to
`Scan 51~53: |current| < 0.1 A is treated as unpowered.` Consecutive warning entries merge only
when their source rows are adjacent and their actual A-column scan IDs are ascending consecutive
safe integers. Gaps, duplicate/reset IDs, missing/non-numeric IDs and intervening other issues
remain separate. Leading zeros in scan labels are retained. Other warnings/errors keep their text.
This display projection never alters raw issues, row highlighting, selection, exclusion, acknowledgement
or calculation. The original data/API and threshold are unchanged.

TDD: the page-level range display regression failed before implementation and passed afterward.
Final affected validation: 81 frontend tests (including nine formatter boundary cases) and the
TypeScript/Vite production build passed. Separate sequential same-agent Standards/Spec reviews found
zero outstanding issues. No browser run for this text-only presentation mapping, proven at the
rendered-page seam; no backend or native Excel changes. Methods: tdd and code-review.

Changed paths: `frontend/src/features/temperature/sourceScan.ts`, `sourceScan.test.ts` in that feature,
`frontend/src/pages/TemperatureRisePage.tsx`, `TemperatureRisePage.test.tsx` in that folder, this document
and the sole-writer task-board record.
