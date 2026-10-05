# Temperature Rise and Derating Tool

Status: implemented. Current refinement: automatic data-region selection with exception-only row
correction (`TASK_TEMPERATURE_AUTO_DATA_REGION_20261005`).

## Scope and acceptance

The Tools entry opens a dedicated page using the selected third design: a full-width Initial Data
preparation area above two analysis panels (Temperature Rise and Derating). At narrow widths the
panels stack. Existing ConnLab navigation, fonts, controls and quiet feedback remain in use.

- Read `.xls`, `.xlsx` and `.xlsm` without executing VBA or changing the source.
- Automatically locate a unique scanner header and data region; show row settings only for missing
  or ambiguous recognition. Let the user choose the sheet, ambient and current columns,
  thermocouples per sample, and ordered sample/channel mapping. A spare source channel can replace
  any failed channel. Channel order determines sample/thermocouple slots and is shown explicitly.
- Exclude/restore rows and channels without changing source data. Retain original row numbers and
  column letters. Suspicious rows are suggestions only; the user confirms their inclusion/exclusion.
- Confirm the prepared data before analysis. A later input/mapping/exclusion change invalidates
  dependent charts, coefficients, current and downloads. Late responses must not restore stale data.
- Generate T-riseChart, retrieve and edit MAX/AVG coefficients, calculate current from MAX and a
  target rise, and generate Derating from AVG and the working-temperature parameters.
- Download an independent `.xlsx` containing Initial Data, T-riseChart and Derating, with native XY
  charts, polynomial trendlines, equations, R² and review provenance. No save-before-clear dialogs.
- Preserve other Tools functions and all project/Matrix/report authority.

## Calculation contract

The baseline is the user-supplied `T-rise&Derating Rev20161002.xlsm`, SHA-256
`2b2565e5d5db5d342d77db4eed21cccce37ff2b2e41c59e2a4c302b745b4f402`.
Its Initial Data is already manually cleaned; it is not evidence that every scanner has the same
column order or that zero-current rows should automatically be removed.

Within each current stage, adjacent relative change is at most 1% of the previous nonzero current.
Use the last row of each stable stage (at least two successive readings). This is current stability,
not a thermal-equilibrium assertion. Subtract that row's ambient from each thermocouple. For each
sample take its highest rise, then plot the highest sample maximum and the mean of sample maxima.
Insert an origin point when the first plotted current is nonzero. Fit second-degree polynomials,
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
   Expand Sample & Channel Mapping; assign each sample's thermocouples, including spare replacements.
3. In Data Preview select original row numbers or ranges, exclude/restore rows as needed, and Confirm
   Data. Warnings are never silently deleted; keeping flagged rows needs explicit acknowledgment.
4. Generate T-riseChart → Get Coefficients → Calculate Current / Generate Derating → Download Excel.

Selections are an in-memory editing session, not a saved project. Refreshing or leaving the page
requires reimport; download the result before leaving. This is not a general cell editor: correct
individual source values in Excel, then reimport. All samples currently use the same confirmed
thermocouple count. Formula inputs are read from Excel's saved cached values; uncached formulas must
be recalculated and saved in Excel first. Files are bounded to 25 MB, expanded XML 100 MB, 20,000 rows,
256 columns and 1,000,000 cells. Current-stage stability is not proof of thermal equilibrium.

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
