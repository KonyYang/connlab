# Temperature Rise and Derating Tool

Status: implemented and locally validated; awaiting user acceptance for task
`TASK_TEMPERATURE_RISE_DERATING_20261004`.

## Scope and acceptance

The Tools entry opens a dedicated page using the selected third design: a full-width Initial Data
preparation area above two analysis panels (Temperature Rise and Derating). At narrow widths the
panels stack. Existing ConnLab navigation, fonts, controls and quiet feedback remain in use.

- Read `.xls`, `.xlsx` and `.xlsm` without executing VBA or changing the source.
- Let the user choose the sheet, header and data rows, ambient and current columns, current scale,
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
2. Check sheet, original header/data row numbers, ambient/current roles and current multiplier.
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
T-riseChart no longer freezes column A or its top row; Initial Data and Derating keep their existing
navigation. The two chart series reference the summary's column-A names, `Max T-Rise` and
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
