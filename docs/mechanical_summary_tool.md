# Mechanical Summary — folder generation

## User outcome

Tools → Mechanical Summary opens a folder picker. The tool scans PDF/XLS/XLSX records recursively, identifies supported mechanical tests and downloads a uniquely named editable XLSX when the source identities and results are complete. Otherwise it shows only the test sections needing sample mappings, a hold-force field or confirmed qualitative report coverage. Optional metadata can remain `Not recorded`.

The tool is independent of project registration. It does not change source files, update the Matrix, issue a report or write into the selected folder. Downloads use the registered-looking LTR found in the current records and a Shanghai-time timestamp, including microseconds. Existing files are not overwritten by the application.

## Evidence and review rules

- Supported PDF records: MF/UMF, peak retention, FEnd section / FEnd section 1 hold records and cable-clamp pull. Recognize the actual instrument headers and rows, including wrapped headings and metadata columns; compare the extracted row count with any explicit instrument sample count; filenames are additional evidence. Scanned or unrecognized named mechanical records block generation with actionable feedback.
- Supported original workbooks: polarisation/mis-mating and protection against electric shock exports with measurement headings, `[N]` / `[mm]`, numbered records and populated instrument statistics. Preserve exact raw strings, signs, precision and original cell coordinates so native chart series remain valid. An unnamed but recognizable instrument worksheet asks for its test type; it is not silently dropped. Irrelevant worksheets are listed separately.
- Exclude existing Mechanical Summary files, temporary Office files, Source/Source Book, History, Backup and Archive directories. Display excluded files and their reasons. Deduplicate identical bytes; reject duplicate relative paths and mixed project IDs. An unreadable selected record cannot silently produce a complete-looking output. The user may explicitly exclude an irrelevant failing file and rescan.
- Each section is bound to the source SHA-256 plus worksheet index. Generation re-reads the uploaded bytes and validates all source identities. Review accepts labels, metadata, display convention and explicit conclusions; it cannot replace measured values, add invented curves, drop PDF measurements or reuse another project's confirmation.
- Sample ID, colour and part are split only when explicit in the current source. Unlabelled MF curves require the operator's input. Curve `1.20` remains text. Do not infer physical colour from plot colour or reuse the 032 six-curve mapping as a default.
- Qualitative report tables have operator-confirmed sample/part coverage and literal Pass/Fail/N/A. Polarisation supports diagonal applicable combinations. The number of report cells need not equal the number of raw curves: 032's confirmed four-column protection matrix does not invent three extra curves. No force threshold automatically proves Pass.
- Completed confirmations are retained in this browser's local storage per LTR and unchanged source fingerprint. They are revalidated by the backend on reuse. Another browser/device or changed source requires new review; no project mappings are hardcoded in production.

## Workbook layout

- Copy original XLS/XLSX worksheets through an isolated Excel instance, retaining native drawings and charts. Remove unneeded introductory fields and empty specification/limit/Cpk placeholders; keep measurement headings, units, numbered values and original populated statistics.
- Preserve original PDF result/curve images and instrument statistics, cropped to effective content. Never redraw, fit or estimate values from curves. Generic photos are not automatically interpreted as sample mappings or equipment evidence.
- Add a separate copyable report table. Quantitative reports contain SN, optional Colour/Part and measured force columns, followed by MIN/MAX/AVERAGE/sample STDEV formulas. Curve is outside the report borders. Merge repeated confirmed SN rows where colour/part distinguishes readings. Signed raw withdrawal values stay intact; magnitude display requires explicit confirmation.
- Qualitative reports use only the confirmed matrix and conclusions. Do not create a second numeric summary. Use gray headers, Arial 11, centered content, thin borders and light-blue quantitative statistics. Arrange compact polarisation/mis-mating tables side by side when they fit.
- All sections have eight editable light-blue information fields: LTR; Test Date; Tested By; Amb Temp. and Rel. Hum.; Test Equipment ID; Test Condition; Item/Process; Remark. Test Date is an Excel date. Never substitute print/export/file timestamps, load-cell capacity or a contact person's name. Unsupported or missing metadata remains `Not recorded`; labels and long values wrap without clipping.
- Test categories/stages determine sheet count. Do not manufacture missing cable torsion/offset results merely because a historical summary contained those sheets. Original files and actual numeric provenance remain authoritative.

## Implementation boundaries

`MechanicalSummaryTool` owns selection, progress, targeted review and download. Typed frontend API methods send relative names and bytes, never arbitrary local filesystem paths. `mechanicalSummaryReview` builds only permitted review fields and handles the project-scoped cache. Leaving Tools invalidates pending downloads.

Folder API routes coordinate source inspection and review. `application/mechanical_summary_folder.py` owns explicit evidence/review rules. `infrastructure/files/mechanical_summary_folder.py` reads supported sources. `infrastructure/office/mechanical_summary_folder.py` owns Excel, drawings, formulas and PDF images. The original per-file preview/generate APIs remain available for existing callers.

Microsoft Excel and the existing Windows Office dependencies are required for generation. Each operation creates its own hidden Excel instance, disables macros/events/link updates, uses temporary copies and closes workbooks and COM resources. Failures leave sources untouched and offer retry guidance.

## Validation and acceptance

- Unit tests cover real instrument header variants, effective data selection, exact curve text, empty metadata, duplicate/mixed sources, explicit review and rejection of numeric tampering/stale source confirmations.
- API tests cover folder preview and refusal to generate unresolved results. Native Office tests inspect the generated XLSX for original values/images, report borders, merged SN, formulas, styles and metadata.
- Frontend tests cover automatic generation, unresolved mapping input, cancel, unmount, project/source-specific cache boundaries and continuing to edit colour/metadata after filling the last sample.
- Validate 031 and 032 in isolated copies, retaining source hashes. Use each project's own confirmed mappings/matrices; compare measured values, all effective raw cells, image content/aspect, formula recalculation and rendered layouts. Never modify real project files for acceptance.
- Final checks: affected Python tests including Office integration, affected frontend tests, TypeScript/Vite build, live folder upload/download at workstation and narrow widths, focused diff review.

Known limits: unsupported instrument formats and unreadable scans require a readable export or explicit exclusion; photos do not establish hidden sample-to-curve associations. Browser-local confirmations are not a shared database or formal approval record.
