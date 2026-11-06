# Report working copy and Tools bridge (batches 1–2)

Scope: the approved first two batches only. No automatic formal publication, project-folder
overwrite, temperature algorithm change, general workflow engine, or new database schema.

## Implemented interface

- Report Workspace loads the existing authoring revision before enabling report actions. Its
  latest output is the selected working copy, shown separately from the project-folder report.
  Reload restores this selection. A failed state read does not fall back to writing the original.
- A current report may be retained as a read-only source, or an uploaded original/reference may
  be explicitly selected. LLCR, equipment, results, photos and customer review copies continue
  the same authoring output lineage. Current official-report behavior remains compatible when
  no working copy is selected; it is not used as a fallback from selected-copy operations.
- Copy operations preserve revision/SHA/Matrix guards and existing section writers. They do not
  set a draft as the official current report. Equipment selections persist even if report bytes
  are unchanged; repeated identical decisions produce no additional version.
- Mechanical Summary and Temperature Rise Tools keep their original Excel download. Optional
  **Export for Report** creates a portable ZIP containing the actual sources, generated Summary
  and reviewed selection. Tools remain project-independent.
- In Report preparation, retain that ZIP as a **Tools results package**, choose its result and
  the current Matrix Group/Step, preview and confirm. No repeated column/sheet selection is
  needed. Unknown temperature specimen SNs still need explicit mapping; channel groups are not SNs.
  An LTR mismatch requires explicit applicability confirmation. Outcomes default to Pending.
- Then inspect the existing report destinations and update a new report copy. Part/colour,
  instrument record, raw signed force, peak/hold/duration remain distinct. Temperature notes
  distinguish original fitted chart coefficients from Tools effective calculator/derating inputs.

## Contract and recovery

The package is `connlab.report-results`, version 1 with `temperature.v1` or `mechanical.v1`
parser profile. Import checks safe names, counts, expanded sizes, duplicate entries, CRC and
SHA256; it never extracts into a project folder. It re-reads original sources and replays
reviewed selections instead of trusting precomputed numbers. SHA256 is consistency evidence,
not a signature or formal approval. The Summary is retained for audit; report numbers come
from the reviewed source projection. Parser meaning changes require a new profile.

Existing authoring source assets, revisions and confirmed-result records retain the whole package
and its source/summary hashes. No separate result database or execution state machine is added.
Manual XLSX/CSV result mapping remains available for non-Tools summaries.

## Boundaries and remaining batches

- Qualitative mechanical matrices are retained and visibly unsupported for numerical report
  application; missing hold duration is not guessed. Their report adapter belongs to a later batch.
- No source folder scanning, bulk report composition, automatic conclusions, broad template/photo
  matching or formal-release automation is included.
- Mechanical workbook generation keeps its existing installed-Excel dependency; package import
  does not require Excel. Temperature workbook generation remains unchanged.
- Changing a retained source or Matrix invalidates the existing result/review checks. Previous
  files and outputs remain available. Real reports, templates and project folders are read-only
  throughout this task's validation.

## Acceptance

1. Isolated API tests: select/adopt original → LLCR → equipment → reload; previous output/original
   SHA unchanged, latest selected output persists, stale SHA/revision rejected.
2. Tools exports and Report import: original bytes preserved, review replayed, effective/fitted
   coefficients distinguished, force part/sign/hold retained, no automatically inherited Pass.
3. Negative cases: changed package bytes, unsafe/duplicate entries, unsupported version/profile,
   mismatched LTR, invalid sample count and stale selections fail without official writes.
4. Frontend tests, typecheck/build and independent local-browser smoke against a disposable DB.
5. Inspect generated workbook/package and report-copy contents; verify real source files were not
   accessed for writes. Word visual acceptance is limited to representative generated sample pages.

The final verification counts and material caveats are recorded in the task completion report;
this document is a feature boundary and operator guide, not another task protocol.

### Native Word visual verification — 2026-11-07

Completed with the isolated synthetic baseline and the actual working-copy output downloaded in
the Tools-to-Report browser smoke. Microsoft Word exported the baseline (1 page) and updated report
(2 pages); every page was rendered and inspected by the primary agent and a separate reviewer.

| Page | Visual result |
| --- | --- |
| Baseline 1 | Fixed wording, Group table, Appendix A heading, header and footer intact. Large whitespace is intentional in this synthetic fixture. |
| Updated 1 | Original wording/header/footer preserved; added result text wraps within its narrow cell without clipping or overlap. |
| Updated 2 | Appendix B measurement table, source-row references, Max/Avg values, coefficient notes, complete curve and legend readable and inside page bounds. |

The earlier automation blocker was in the temporary QA helper, not evidence of a broken Word
installation: it read `Word.Application.Hwnd` before opening a document. Word exposes the handle on
`Document.ActiveWindow.Hwnd`. The corrected helper opens only the isolated copy read-only, verifies
its window belongs to the newly attributed automation process, exports, and closes without saving.
Nested cleanup guarantees that a document-close/options error still attempts the owned application's
Quit and COM release; it never terminates pre-existing Word processes. A final export with this
cleanup produced pixel-identical pages and left no owned Word process running.

Both input DOCX SHA-256 values remained unchanged: baseline
`c6e34c087146f2d3336f16772a5500a7f9bdab06ed12d01fd6a67b4fb226cb03`, updated copy
`0264e8ac1cbe64b282246f72ec2e2e91fa0c059b6eb4653fe95a36226b3dee78`.
Local PDFs, page images, inventory and helper are under `tmp/word_tools_visual_20261107/` in the
primary checkout; these disposable QA artifacts are not product files. No real reports, templates
or project data were changed. This closes representative sample pagination acceptance, not visual
certification of every real template or automatic approval/publication of laboratory results.
