# Draft download information

Implemented scope: Fee Form browser downloads, both Test Record DOCX download entrances,
LLCR/CR current-Matrix downloads, IR/DWV downloads, and registered/confirmed metadata for
LLCR/CR blank forms generated through the existing project-folder workflow.

## Read policy and boundaries

- Download values overlay explicitly present saved Basic Information draft fields (including
  deliberate empty strings) onto confirmed values, then read-only project/LTR/application/sample
  source fallbacks for missing fields. Current Matrix request data continues to own draft test
  steps/conditions; no independent confirmed Matrix is substituted for those fields.
- Downloads do not initialize/save drafts, confirm Basic Information, register an official output,
  publish into project folders or allocate an LTR. A source-augmented or draft snapshot never carries
  a confirmed Basic Information version/hash as if it were confirmed authority.
- Registered LTR sample descriptions, including the supported legacy note shape, remain available;
  Test Record's existing specification extraction still supplies genuinely missing specifications.
  Source fallbacks do not replace explicitly present blank draft values.
- Formal saving retains its existing confirmed-authority, lifecycle, preview fingerprint, workspace
  and archive/conflict gates. The confirmed-Matrix Test Record command defaults to the original
  strict header behavior; only the browser-download route opts into available-information mode.
- LLCR/CR yellow panels fill registered LTR and default Tested By from Project Leader. Drafts use
  available Basic Information; project-folder/formal generation uses confirmed Basic Information
  only. Formal fingerprints include the metadata to reject changed sources before publication.
  When no registered LTR exists, a draft download may display an available Basic Information DL
  value; this does not allocate/register it. A temporary project identifier is not guessed as LTR.
- Checked by/Date and actual equipment are not inferred from a Basic Information confirmer,
  generation date or the entire project equipment list. Missing actual facts remain blank. IR/DWV
  retains explicitly configured template instrument defaults and its existing warning; these are
  not asserted to be the equipment actually used.
- Existing generation previews and source-staleness checks remain; this feature introduces no
  additional human confirmation screen. Unsaved Matrix inputs already submitted by the current
  page are used. Basic Information from another page must already be available in its saved draft
  or source records; a download cannot read another page's private, unsubmitted browser state.

## Architecture

`ProjectBasicInformationSnapshotReader.get_download_snapshot` is the explicit read-only download
seam. Existing `get_latest_confirmed` and confirmed-first preview behavior remain unchanged.
Composition supplies the existing source assembler without calling the write-capable Basic
Information service. Download consumers and formal consumers select distinct read methods.
Office adapters retain layouts/formulas and write LLCR metadata as literal strings, including `=`.

## Regression and acceptance

Tests use the public snapshot reader, fee destination/download validation, actual HTTP DOCX/XLSX
downloads and formal preview projections. RED/GREEN evidence covers draft-first filling, preserved
blank overrides, missing sources, stale fee metadata, literal LLCR tester strings, both Word entrances,
IR/DWV source separation and formal contact-form metadata fingerprints. The Test Record API test
also verifies that download leaves the saved draft unchanged and creates no confirmed/output record.

Acceptance: draft/header/source values appear in downloaded files; current Matrix text is preserved;
formal guards still reject unconfirmed/changed sources; unknown actual facts are not fabricated;
source/template files and existing human-filled records are not modified.

Final validation: 357 tests passed across 22 relevant unit/integration modules, with one existing
Starlette/httpx deprecation warning. The matrix covers fee workbook output, both Word download
routes, LLCR/CR and IR/DWV downloads/formal guards, project-folder generation and recovery.
The initial matrix stopped with 271 passed and four old IR/DWV test-double interface failures;
the fixtures were migrated to the new explicit download read port and the agreed leader default.
No compatibility fallback was added to production merely to satisfy those test doubles.

A separate hidden Excel instance opened an isolated generated LLCR draft read-only: LTR
DL-2026-05-999, Tested By Min, condition 20 mV/100 mA, checker/equipment blank, tester stored as
literal text and no formula errors after recalculation. The workbook was closed without saving.
Frontend/UI and document layout structure were unchanged; no browser or frontend-build pass is
claimed for this backend-only task. No real project folder, template or source attachment was changed.

## Standards

Separate sequential same-agent exact-diff review: application-owned read policy, explicit opt-in for
the legacy Word download route, existing infrastructure-only format handling, no schema or authority
write changes. Registered-description compatibility is owned by the existing project identity module.
No outstanding standards findings; no independent-agent review claimed.

## Spec

Separate sequential same-agent requirements pass: available information fills draft downloads without
requiring confirmation; formal consumers retain confirmed-only reads; project-folder LLCR/CR receives
registered/confirmed information. Equipment/checker/date limitations above are intentional because
there is no test-specific actual source to copy. No additional product workflow or dependency added.
