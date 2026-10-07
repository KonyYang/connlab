# Temperature Rise and Derating Tool

Status: implemented. Current refinement: automatic editable coefficient population on chart generation
and generation after successful confirmation, with scan-based operator feedback
(`TASK_TEMPERATURE_AUTO_COEFFICIENTS_20261007`);
unified raw-data row/column editing remains in place without a separate row-range form.

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
- Generate T-riseChart, automatically populate editable MAX/AVG coefficients, calculate current from
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
   MAX/AVG a/b/c populate automatically after chart generation; download uses these values or the user's
   subsequent edits. Regeneration replaces edits with the new fit; changing source data clears the
   coefficients and dependent results. In nonzero-intercept mode, c also populates and stays editable.

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
  separately into the report. The synthetic zero-current column is identified by a cell comment.
  Report pagination depends on sample/stage counts; a five-sample table may occupy a separate page.

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
T-riseChart no longer freezes column A or its top row; Initial Data keeps its existing navigation.
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
Changing F10 in Excel moves the guide, markers and labels together. Existing coefficient and maximum
temperature inputs, domain calculations and T-riseChart presentation remain unchanged. The supplied
macro workbook is read-only style evidence; no macros are run and no source file is overwritten.

Verification: the old frozen-pane behavior failed two RED export checks before implementation.
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
  The original source value is unchanged. Select Unpowered Rows only selects flagged rows; the operator
  must separately exclude or explicitly keep them. Entire records are not automatically discarded,
  because auxiliary currents may remain powered.

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
