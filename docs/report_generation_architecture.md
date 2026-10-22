# Test Report generation architecture

## Current delivered boundary

The delivered report workflow now creates one current E-3707_H Internal Report and updates controlled
regions without rebuilding the document. Initial generation consumes Confirmed Basic Information and
the Active Confirmed Matrix. Later section actions preserve manual edits outside their declared region,
stage changes, fingerprint the current file, archive the previous revision, and replace atomically.

LLCR Result/Comment synchronization and Section 7 Equipment List synchronization are delivered.
The E-4515_F customer report is now a deterministic projection of the current Internal Report.
Temperature-rise and other result adapters, photographs, appendices, and final narrative automation
remain deferred.

### Internal Report destination and draft download

`Generate Internal Report` previews the destination first. With an available, identity-validated
official project folder, existing publication and explicit Archive and regenerate confirmation remain
unchanged. Without a registered folder, or when the registered folder or identity file is missing,
the page downloads an independent `_Draft.docx` copy instead of recreating the folder or blocking on
its absence. Existing reports and same-name drafts are never overwritten by this download.

The preview-bound draft endpoint uses request-owned staging and removes it after the response; it does
not publish, archive, register a current report, or change report authority. Confirmed Basic Information,
Matrix plan dates and steps, and the approved template remain prerequisites. Authority/template/folder
changes during generation reject the stale download and clean only its staging. An existing folder
with conflicting or redirected identity still fails closed rather than being treated as an official
destination. Legacy managed-report APIs remain compatible; the page's new fallback is download-only.

## Protected Office document access

`REPORT-003D` centralizes the fixed laboratory Word/PowerPoint open-password policy. App-owned Word
COM sessions always supply both the document-open and write-reservation password, while PowerPoint
uses its supported password-qualified file-name form. The password is never returned through the API,
shown in the UI, written into filesystem names, or copied into exception text.

`python-docx` cannot read an encrypted OOXML container. Readers therefore request a caller-scoped
readable copy from `ProtectedWordPackageGateway`; the gateway detects encrypted DOCX containers,
decrypts the OOXML container to a temporary unprotected package without a Word round-trip, and removes it
deterministically. This access seam also covers intake application-form parsing and EquipmentID or
historical-report extraction. Report and application-form updates stage an editable copy, perform and
audit the declared region change, then restore the source document's password-protection state before
atomic publication. An encrypted Internal Report consequently remains encrypted after LLCR or
Equipment List updates, and it can still serve as the source for the E-4515_F customer projection.
An encrypted E-4515_F template is audited while readable and restored to its original protection state
before publication. Approved templates and source reports remain unmodified.

If a customer report is deleted or moved after the Report Workspace loaded it, generation fails closed
with a typed stale-preview conflict. The page refreshes filesystem state and asks the operator whether
to generate a new customer report from the current Internal Report. Confirmation sends no prior
customer fingerprint, creates no empty History entry, and still rechecks both the Internal Report and
customer-report directory before publication. A customer report that reappears is never overwritten.

## Customer report projection

`REPORT-003C` treats the current Internal Report as the only customer-report source. It never merges
from an older customer report and does not creatively rewrite report content. The Word adapter copies
the internal report, applies the approved E-4515_F header/footer and page contract, and removes only
the validated internal-only scope: internal identity fields, internal disclosures, Equipment List,
appendices, cross-project references, and controlled sample details that the approved customer
goldens omit. Test-result tables, accepted evidence images, revision data, and customer-visible
narrative remain source-authored.

The current customer-report state is one of `missing`, `ready`, `stale`, `untracked`, `ambiguous`, or
`blocked`. A custom DOCX property records the SHA-256 of the Internal Report used for generation, so a
later Internal Report change is visible as `stale`. Generation requires the previewed Internal Report
fingerprint and, when a customer report already exists, its fingerprint as well. The source is checked
before and after Word generation.

With an official project folder, the canonical `{DL}-CR ... .docx` is published beside the Internal
Report. A changed prior customer report is archived under `History/Report`, and the generated staging
file replaces it atomically. Without an official project folder, the generated file is returned as a
browser download and is not promoted into project authority. The approved E-4515_F template and both
source reports remain read-only.

When no ready official Internal Report exists, Customer Report source resolution also checks the
current user's OS Downloads folder (including Windows Known Folder relocation). It only scans the
top level for this project's exact DL-prefixed `_Draft.docx` files and ordinary browser `(n)` copies.
The newest modification time wins, with browser copy number as the equal-time tie breaker. The
selected document must repeat that DL in its header and carry the E-3707 internal form identity in
its footer; customer reports, other projects, partial downloads, and redirected files are not sources.
Conflicting latest candidates or an unreadable/invalid latest draft require manual file selection,
not silent fallback to an older report. Other browser-configured download directories use the manual
picker. A valid official source remains preferred and existing official ambiguity is never bypassed.

This downloaded source is used only for the Customer Report projection. It is not registered as the
current Internal Report, and neither the source nor existing downloaded reports are changed. The
customer result keeps its `Draft` marker and uses the existing asynchronous job/download flow and
ordinary browser duplicate-name handling. Preview hashes and post-generation source re-resolution
reject edits or a newer download appearing during generation. Legacy managed drafts remain compatible
when no matching downloaded draft exists.

Before Microsoft Word starts, ConnLab copies the Internal Report, the customer template, and the
working output into a short task-owned directory. Word therefore never receives the potentially long
official project path or creates its temporary files beside the project report. The completed working
copy is then returned to the existing publication stage, which keeps the full descriptive customer
report filename and its non-overwrite and history rules.

Customer-report generation does not abort merely because one Word stage takes 120 seconds. The
isolated process retains a 600-second total safety limit. If one stage has not advanced for 120 seconds,
the child records a non-terminating diagnostic snapshot with the current stage and Python thread
stacks; the parent writes a redacted copy to the runtime log and continues waiting. Job logs correlate
the operation identifier, stage, elapsed time, child exit status, and bounded stdout/stderr details so
an exported diagnostics package can distinguish template preparation, Word startup, content copying,
formatting, saving, verification, and output protection failures without retaining report contents.

Report history is intentionally flat. A prior Internal Report is stored directly as
`History/Report/{DL} Report_Rev_{revision} {YYYYMMDD-HHMMSS}.docx`; a prior Customer Report uses
`{DL}-CR Report_Rev_{revision} {YYYYMMDD-HHMMSS}.docx`. The product title is omitted from history
filenames, no timestamp subdirectory is created, and a same-second collision receives `(2)`, `(3)`,
and so on. Publication reserves the history filename before copying so concurrent updates cannot
silently overwrite an earlier revision.

## Equipment List controlled update

`REPORT-003B` uses two read-only external authorities:

- `{project local workspace}/EquipmentID.docx` selects equipment for this project. Paragraph and table
  values are read in order and deduplicated case-insensitively; `DG-Q-0000`, `Q-0000`, `DG-L-0000`,
  and `L-0000` references share the legacy match token.
- Settings `Equipment calibration Excel` supplies `Item`, `Manufacturer`, `ID Number`, `Last Cal.`,
  and `Cal. Due`. Both the current structured header layout and the legacy `All Equip.` row-4
  `Item (Equipment Name)` / A-C-D-E-F layout are supported. Legacy Excel date values are normalized
  to `DD-MMM-YYYY`; `Not applicable` remains a valid non-expiring value.

Preview is mandatory. Missing `EquipmentID.docx`, an unreadable or empty selection, an unavailable
catalog, and an unavailable current report remain workflow blockers because the update cannot identify
its source rows or safe target. Row-level data quality never blocks the other selected equipment:
ambiguous matches are projected as ID-only rows, incomplete catalog rows retain only valid cells, and
invalid correction values are omitted. Each case is shown as a warning. The operator may supply all
five report fields plus an explanation as an optional correction, or skip the correction and complete
blank cells manually in Word. Expired calibration is a warning that still requires an explicit
acknowledgement. The preview fingerprints `EquipmentID.docx`, the calibration workbook, and the
current report; all are rechecked before publication.

Only the data cells in the body rows of the table headed
`Item / Manufacturer / ID Number / Last Cal. / Cal. Due` are owned by this action. The approved
template and both source files are never changed; heading, Purpose, Conclusion, result, image,
appendix, and revision-record content and formatting are preserved. Existing table headers, column
widths, row/cell properties and unchanged data cells are retained. Changed cells inherit the existing
paragraph and run formatting; extra rows use the first data row's layout. Calibration due-date colors
remain owned by this action. The existing report publication gateway archives a changed prior report
under `History/Report` and performs atomic replacement.

Equipment calibration values marked `Not applicable` are copied to both `Last Cal.` and `Cal. Due`
without date coercion; this is the approved representation for equipment that does not require
calibration. Initial generation gives the Equipment table a fixed five-column layout with at least
1800 dxa allocated to `ID Number` and makes that column non-wrapping. Later section updates preserve
the current report's layout instead of reapplying those template defaults.

Initial report generation uses 11 pt body text, including body tables. Numbered chapter headings, Group
result headings, and Appendix headings use 12 pt while retaining the template's bold/underline
formatting. Only initialization removes direct Word `keepNext` paragraph controls from the output
copy and uses explicit page breaks. LLCR and Equipment updates do not normalize the whole document.
Approved template files, source workbooks, and header/footer typography remain unchanged.

### Local update fidelity

LLCR changes only matched Result/Comment cells and Appendix A numeric cells. For an existing
Appendix A, the supported two-row header and Group/Stage mapping must match the dataset, including
row count. Its heading, pagination, merged headers, column widths, colors and existing typography
are preserved. A structural/mapping mismatch stops before publication with a review message instead
of rebuilding the approved appendix. If Appendix A is absent, the existing default appendix builder
still inserts it before later appendices or End of Report. LLCR formulas and Final R versus delta-R
semantics have not changed; semantic correction is a separate batch.

Text/table-only section updates replace only `word/document.xml` in the staged DOCX ZIP; all other
package parts keep their original bytes, including relationships, media, headers/footers, styles and
settings. These operations must not add relationships to new external parts. Unchanged values avoid
cell rewriting; a no-op on an unencrypted package remains byte-identical. Encrypted reports retain
password protection, but their randomized encryption envelope is not a byte-identity promise.
Within a changed cell, the generated value replaces its content using the existing first paragraph
and run properties; arbitrary mixed formatting within that replaced value is not retained.

Regression validation uses isolated reports and covers unrelated body XML/package bytes, manual
typography, existing appendix layout, incompatible mappings, repeated updates, and source hashes.
The two authoritative project reference copies (DL-2026-09-021/031) additionally exercise equipment
updates and protected-package round-trips; no source reports, templates or project data are written.
Their `Final LLCR` labels and the 031 appendix's different header layout are not evidence of LLCR
semantic compatibility with the current dataset. This batch must not relabel them as delta-R or
claim that those real appendices can already be synchronized; that mapping remains next-batch work.
Preserving pagination controls does not freeze page count when new text or row counts actually grow.

## Authority and dependency flow

```text
Project Workbench
  -> POST /api/projects/{project_id}/test-report-draft/generate
    -> Settings Template folder -> unique E-3707_H .docx
    -> confirmed Basic Information
    -> Active Confirmed Matrix -> report groups and steps
    -> semantic TestReportDraftData
    -> E-3707_H Word adapter
    -> data_dir/generated_test_reports/{project_id}/new draft.docx
    -> browser download
```

Word is an output format, not the report domain model. Application code owns the semantic draft data;
the Office adapter owns template validation and OOXML manipulation.

## Template contract

The approved template is never edited in place. Generation first resolves exactly one active
`E-3707_H` `.docx` from the Settings `Template folder`, rejects ambiguity, and validates the controlled
headings and table headers before writing a copied draft.

The adapter intentionally populates:

- report number, report date, requestor, project leader/tester, and title in first/continuation headers;
- Purpose, a non-passing draft Conclusion, received date, and the initial sample row;
- Test Description sequences and sample quantities by Matrix group;
- unique Test Methods/Requirements;
- one Test Results table per Matrix group with empty Result and Comment columns;
- Revision A as `Initial draft - not released`.

The adapter leaves test results, judgements, equipment, photographs, and final conclusion for later
work. A template whose mapped headings or table headers drift is rejected explicitly instead of being
silently populated in the wrong location.

## Storage and non-overwrite rule

Drafts are stored under `Settings.data_dir/generated_test_reports/{project_id}`. The base filename is:

```text
{DL} {Product Description} {Test Item} Report_Rev_A_Draft.docx
```

Generation reserves the target atomically. Existing drafts are preserved and the next filename uses
`(2)`, `(3)`, and so on. The API downloads the exact server filename. No official project file or
approved template is mutated in this phase.

Initial-report editing uses a short ConnLab working copy rather than a UUID-suffixed temporary file
beside the final report. The full descriptive draft or official filename is retained when the validated
working copy is published to its reserved target.

The canonical Test Record authority created by Project Folder is
`{official qualification folder}/Submitted Material/{DL} Test Record.docx`. Matrix Editor publication
uses that same path: the existing file is the version archived to `History/Test Record`, and only the
newly generated file becomes the current Submitted Material document. `Test results` is not a second
Test Record authority.

## Deferred phases

### Section updates without a project folder

`Update Internal Report` resolves its source separately from registered report authority:

1. A unique ready official Internal Report retains the existing archive-and-update workflow.
   Ambiguous official reports block updates rather than falling back silently.
2. Otherwise, the latest successful project-specific working draft takes priority, followed by the
   validated latest current-project Internal Report in Downloads and the retained managed source.
   An unsafe latest draft is not silently replaced by an older candidate. The user can explicitly
   select another E-3707 `.docx`; report headers must match the project's DL and Customer Reports
   are rejected.
3. LLCR and Equipment List updates create immutable `_Draft.docx` copies in
   `data_dir/report_working_drafts/{project-hash}/{revision}`. The atomic current pointer advances
   only after generation and source revalidation succeed. No official folder, history entry, report
   registration, or original-file replacement is created in this mode.

The new API boundary is `/api/projects/{project_id}/report-workspace/update-source`: source status,
explicit source selection, LLCR/equipment updates, and revision-scoped downloads. Existing registry
and project-folder write guards still apply. Requests compare the reviewed source mode and SHA-256;
changed sources, stale LLCR datasets, or a newly available official report stop draft publication.

Missing equipment selection accepts an uploaded document or pasted IDs. A validated existing LTR
selection is read only. Draft-owned selections travel with later LLCR/equipment copies, so consecutive
updates preserve previous work. Calibration matching and section writers reuse the existing adapters;
other content and manual edits retain their established preservation contract.

Successful working drafts also feed Customer Report generation, including after a failed browser
download. Retry downloads fetch the same immutable revision rather than rerunning updates. Cached
revisions expire after 24 hours; expired state no longer shadows Downloads, and subsequent updates
prune only expired, owned cache directories. Downloaded files are not cleaned or overwritten; browser
duplicate-name handling remains unchanged. Reopening the page restores an unexpired download link.

Regression coverage includes draft chaining, source/hash/matrix conflicts, selection validation,
formal-report archive compatibility, pending-folder guards, project isolation, cache retention,
duplicate submissions, late responses after navigation, and download retry. Native smoke tests use
temporary databases and copied templates/reports; user projects are never test fixtures.

Future report work should build on the semantic report model rather than adding result-specific logic
to the Word adapter:

1. LLCR result import preview and confirmed structured result snapshots.
2. Temperature-rise and other result-source adapters with explicit operator mapping for irregular
   workbooks.
3. Pass/Fail suggestions derived from structured values and requirements, followed by operator
   confirmation.
4. Photograph selection, Group/Step linkage, caption rules, and chapter placement.
5. Additional controlled region adapters for narrative, result, image, and appendix sections.
6. Final publication/freeze controls for paired Internal and Customer reports.

These phases are not part of `REPORT-001`.

## Verification baseline

The retained reference template inspected for REPORT-001 has SHA-256
`5a2c6b1a59df1612a8095028df8681deea6a7477d83196e6e65ed52554e211c5`.
The retained E-4515_F customer template inspected for REPORT-003C has SHA-256
`3e0548b1140a189411de9b0a1b00f4c9db03a74da1547a61260c9398e4798e5c`.
The implementation is protected by template discovery, application-service, Word contract, API,
download-button, publication-gateway, and Report Workspace tests. The approved 24-page internal
golden is converted into a 21-page customer report and exported by Microsoft Word for page-level
visual inspection; controlled external source and golden files are not modified.
