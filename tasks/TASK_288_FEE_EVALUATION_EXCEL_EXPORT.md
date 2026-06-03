# TASK_288_FEE_EVALUATION_EXCEL_EXPORT

## Status

Planned follow-up. Blocked until TASK_287 is complete.

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
6. Mark fee output stale when Matrix authority or fee rule version changes, if existing output status infrastructure can support it without broad redesign.
7. Add backend tests for workbook gateway behavior, export service, output-record update, and no-overwrite guard.

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

## Acceptance Criteria

1. Export creates a `.xls` or `.xlsx` fee evaluation workbook from a reviewed fee draft.
2. The workbook `Testing Prices` sheet contains line items grouped consistently with the fee draft.
3. Totals match the structured draft totals.
4. Existing files are not overwritten unless explicitly allowed.
5. Missing template or unavailable Excel automation returns actionable errors.
6. `ProjectOutputRecord` is updated for generated fee evaluation output.
7. Fee output can be identified as stale against later Matrix/rule changes where current infrastructure supports it.
8. Tests cover gateway write behavior, export service, output status update, and overwrite guard.
9. Scope boundary is held: no rule-maintenance UI, no StepInstance, no report expansion.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded Office-gateway and output-lineage feature with clear inputs, outputs, and existing infrastructure boundaries.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and its executable plan are reviewed and explicitly approved by the user.
