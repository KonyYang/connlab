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

## Protected Office document access

`REPORT-003D` centralizes the fixed laboratory Word/PowerPoint open-password policy. App-owned Word
COM sessions always supply both the document-open and write-reservation password, while PowerPoint
uses its supported password-qualified file-name form. The password is never returned through the API,
shown in the UI, written into filesystem names, or copied into exception text.

`python-docx` cannot read an encrypted OOXML container. Readers therefore request a caller-scoped
readable copy from `ProtectedWordPackageGateway`; the gateway detects encrypted DOCX containers,
uses an owned hidden Word session to create a temporary unprotected package, and removes it
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

Preview is mandatory. Missing, ambiguous, incomplete, or structurally invalid catalog rows block the
write. An unmatched customer/external fixture may proceed only after all five report fields and an
explanation are supplied. Expired calibration is a warning that requires an explicit acknowledgement.
The preview fingerprints `EquipmentID.docx`, the calibration workbook, and the current report; all are
rechecked before publication.

Only the body rows of the table headed `Item / Manufacturer / ID Number / Last Cal. / Cal. Due` are
owned by this action. The approved template, both source files, headings, Purpose, Conclusions, test
results, images, appendices, and revision record are not changed. The existing report publication
gateway archives a changed prior report under `History/Report` and performs atomic replacement.

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

The canonical Test Record authority created by Project Folder is
`{official qualification folder}/Submitted Material/{DL} Test Record.docx`. Matrix Editor publication
uses that same path: the existing file is the version archived to `History/Test Record`, and only the
newly generated file becomes the current Submitted Material document. `Test results` is not a second
Test Record authority.

## Deferred phases

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
