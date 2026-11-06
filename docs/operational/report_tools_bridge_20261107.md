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
