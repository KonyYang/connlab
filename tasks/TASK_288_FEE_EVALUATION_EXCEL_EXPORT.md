# TASK_288_FEE_EVALUATION_EXCEL_EXPORT

## Status

Complete. Implemented after explicit user approval on 2026-06-04.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Export the reviewed Matrix-derived Fee Evaluation draft into the official Excel fee form template and update project output status lineage.

This task writes the `Testing Prices` sheet from structured fee-draft data. It does not implement fee rule maintenance UI or execution persistence.

## Business Context

The laboratory currently prepares `Testing Prices` manually from Matrix groups/steps and the `Unit Price Reference` page. After ConnLab generates a reviewable draft and the operator reviews uncertain items, ConnLab should generate the official workbook while preserving source traceability and output freshness.

## Scope

### In Scope

1. Extend the Excel gateway to write structured fee draft rows into the `Testing Prices` sheet.
2. Preserve workbook template format where practical:
   - header fields
   - group labels
   - spend time
   - description
   - unit price
   - units
   - base fee
   - discount
   - testing fee
   - total rows
3. Generate output into the controlled project output/generated-output location.
4. Reject overwrite unless explicitly allowed.
5. Update `ProjectOutputRecord` for `fee_evaluation`.
6. Mark fee output freshness using the existing `ProjectOutputRecord` draft-version status model; preserve confirmed Matrix id/revision and fee rule version as traceability metadata. V1 does not add a new confirmed-Matrix/rule-version stale comparator.
7. Use the ConnLab login user first, then Windows/computer user, as default `Prepared by`.
8. Leave `Approved by` for per-export manual entry/review.
9. Allow `.xlsx` output as a V1 fallback only through Excel COM SaveAs when `.xls` output is unsuitable. If Excel COM is unavailable, return an actionable unavailable error instead of adding a new workbook-writer dependency.
10. Add backend tests for workbook gateway behavior, export service, output-record update, COM SaveAs `.xlsx` fallback selection, unavailable-automation behavior, and no-overwrite guard.

### Out Of Scope

1. No pricing rule maintenance UI.
2. No automatic import of new `Unit Price Reference` versions.
3. No StepInstance or execution persistence.
4. No report generation expansion.
5. No Approval Package assembly expansion beyond existing output record status.
6. No AI/LLM fee validation.
7. No broad rewrite of legacy `test_record_fee_*` generation unless the approved plan explicitly narrows a compatibility adapter.

## Data Semantics

### Excel Is Output

The generated workbook is an output artifact. It is not the source of truth for Matrix authority or fee rules.

### Output Traceability

The generated output must retain enough metadata in service results and output-record lineage to identify:

- project id
- confirmed Matrix authority id/revision
- fee rule version id
- output path
- generation timestamp

### Prepared And Approved By

`Prepared by` defaults to the ConnLab login user when available. If no ConnLab login user exists, fall back to the current Windows/computer user.

`Approved by` is not auto-filled in V1 and must remain a per-export manual value.

### Workbook Format Fallback

The preferred template remains the official fee workbook. V1 may output `.xlsx` when Excel COM can open the official template and save the generated workbook as `.xlsx`. V1 does not add `openpyxl`, `xlsxwriter`, `xlwt`, or another workbook-writer dependency. If Excel COM is unavailable, return an actionable unavailable error.

## Acceptance Criteria

1. Export creates a `.xls` or `.xlsx` fee evaluation workbook from a reviewed fee draft.
2. The workbook `Testing Prices` sheet contains line items grouped consistently with the fee draft.
3. Totals match the structured draft totals.
4. Existing files are not overwritten unless explicitly allowed.
5. Missing template or unavailable Excel automation returns actionable errors.
6. When `.xls` output is unsuitable but Excel COM is available, `.xlsx` SaveAs fallback is allowed and tested. When Excel COM is unavailable, the export returns an actionable unavailable error.
7. `Prepared by` defaults to ConnLab login user first, then Windows/computer user.
8. `Approved by` remains manually supplied for each export.
9. `ProjectOutputRecord` is updated for generated fee evaluation output.
10. Fee output freshness is identified by the existing draft-version output status model; confirmed Matrix id/revision and fee rule version are retained for traceability but do not drive V1 stale calculation.
11. Tests cover gateway write behavior, export service, output status update, COM SaveAs `.xlsx` fallback selection, unavailable-automation behavior, and overwrite guard.
12. Scope boundary is held: no rule-maintenance UI, no StepInstance, no report expansion.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded Office-gateway and output-lineage feature with clear inputs, outputs, and existing infrastructure boundaries.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and its executable plan are reviewed and explicitly approved by the user.

## Completion Notes

- Added backend export service for active Confirmed Matrix Fee Evaluation drafts.
- Added `POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export`.
- Added structured workbook writer support for the `Testing Prices` sheet behind the Office gateway boundary.
- Registered generated outputs as `ProjectOutputKind.FEE_EVALUATION` through the existing `ProjectOutputRecord` draft-version freshness model.
- Preserved confirmed Matrix id/revision, pricing rule version, and pricing effective date in service results and output-record notes.
- Follow-up review fixes preserve line-level traceability in service results, API responses, output-record notes, and workbook rows: line id, confirmed group/row ids, source row id, matched rule id/version, and step tokens.
- Follow-up review fixes carry Matrix row `day_expression` as export `spend_time` and write it to `Testing Prices`.
- Kept `.xlsx` fallback limited to Excel COM SaveAs behavior with explicit Excel `FileFormat` selection; no workbook-writer dependency was added.
- Validation:
  - `py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q` -> `12 passed`
  - `py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py tests/integration/test_project_output_records_api.py -q` -> `8 passed`
  - `py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q` -> `12 passed`
