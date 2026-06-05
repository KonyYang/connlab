# TASK_290_FEE_TEMPLATE_MATRIX_BASIC_FILL Executable Plan

## Summary

Implement an explicit Matrix basic-fill export mode for Fee Evaluation workbooks.
The mode uses active Confirmed Matrix authority selected/non-empty cells as the
row source and writes only the formal template's `Testing Prices` A/C columns.

## Current Phase And Permission

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
  controlled foundation.
- Current active task before this work: none; TASK_285-TASK_289 are complete.
- TASK_290 is allowed because the user explicitly approved this plan.

## Design

- Add a small application model/service for Matrix basic fill rows built directly
  from active Confirmed Matrix authority.
- Extend the existing export service with an explicit `fill_mode` command field:
  default `fee_draft`, optional `matrix_basic`.
- Keep the TASK_288 default path unchanged.
- In `matrix_basic`, build Confirmed Matrix authority rows first; fee draft
  metadata is best-effort only and must not block A/C fill.
- Force pricing review if fee draft metadata is unavailable or if authority
  basic-fill rows are not represented in fee draft line traceability.
- JSON-encode basic-fill source `cell_value` in output-record notes so user data
  containing delimiters cannot make lineage ambiguous.
- Treat fee draft metadata as best-effort only for known draft/rule seed failures;
  unexpected programming errors must still propagate.
- Add a dedicated workbook-writer method for Matrix basic fill so the existing
  structured fee-draft writer remains compatible.
- Register output records with a note that distinguishes Matrix basic fill from
  final fee confirmation and includes selected Matrix `cell_value` lineage.

## Implementation Steps

1. Write unit tests for the new Matrix authority source service.
2. Write export-service/API tests proving `matrix_basic` is explicit and allows
   review-required drafts.
3. Write workbook-gateway tests proving A/C write behavior and blank price detail
   columns.
4. Implement the Matrix basic-fill service and lineage note helpers.
5. Implement export-service/API fill-mode routing.
6. Implement workbook-gateway Matrix basic-fill writer.
7. Run targeted backend tests and `git diff --check`.

## Validation

- `py -m pytest tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py -q`
- `py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q`
- `py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q`
- `py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q`
- `py -m pytest tests/integration/test_project_output_records_api.py tests/integration/test_api_default_dependencies.py -q`
- `py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q`
- `git diff --check`

## COM Smoke Boundary

Do not run direct Excel COM smoke again inside TASK_290. A real-template smoke was
interrupted before output creation, and the temporary smoke harness had no
subprocess timeout or step-level logging. TASK_290 closes on automated non-COM
verification. If real Excel COM smoke is still required, open a separate
`TASK_290A_EXCEL_COM_SMOKE_TIMEOUT_HARNESS` follow-up that adds isolated
subprocess execution, timeout, step logs, and cleanup.

## Risks

- Excel COM row insertion can damage template layout if anchors are missing.
  The writer must fail fast when `Testing Prices`, `Report preparation`, `Total`,
  or `Grand Cost` cannot be found.
- Basic fill intentionally allows review-required pricing state, so output notes
  must not imply final fee confirmation.
- The formal template remains an external `.xls`; real-template manual smoke is
  recommended after automated tests.
