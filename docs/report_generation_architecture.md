# Test Report generation architecture

## Current delivered boundary

`REPORT-001` provides one deliberately narrow workflow: Project Workbench can generate and download
an internal E-3707_H initialization-report draft from the latest confirmed Basic Information and the
Active Confirmed Matrix.

The workflow is a derived preview output. It does not import result files, calculate Pass/Fail, insert
test photographs, generate a customer report, update an earlier Word report, or write into an official
project/public-drive folder.

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

## Deferred phases

Future report work should build on the semantic report model rather than adding result-specific logic
to the Word adapter:

1. LLCR result import preview and confirmed structured result snapshots.
2. Temperature-rise and other result-source adapters with explicit operator mapping for irregular
   workbooks.
3. Pass/Fail suggestions derived from structured values and requirements, followed by operator
   confirmation.
4. Photograph selection, Group/Step linkage, caption rules, and chapter placement.
5. Safe synchronization into an operator-edited report with explicit managed regions and manual
   override adoption.
6. Official project-folder placement and the separate overwrite/archive-to-Source-Book decision.
7. Independent E-4515_F customer-report projection from the same semantic snapshot.

These phases are not part of `REPORT-001`.

## Verification baseline

The retained reference template inspected for REPORT-001 has SHA-256
`5a2c6b1a59df1612a8095028df8681deea6a7477d83196e6e65ed52554e211c5`.
The implementation is protected by template discovery, application-service, Word contract, API,
download-button, and Project Workbench tests. A real E-3707_H three-group sample is also exported by
Microsoft Word and visually inspected page by page; the local LibreOffice renderer is unavailable on
the current Windows host.
