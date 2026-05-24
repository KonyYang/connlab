# TASK_252_MATRIX_EDITOR_DOCX_IMPORT_PREVIEW_AND_MANUAL_TABLE_SELECTION

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252_MATRIX_EDITOR_DOCX_IMPORT_PREVIEW_AND_MANUAL_TABLE_SELECTION`.

## Why This Task Is Allowed Now

`TASK_251` is complete and the user explicitly approved `TASK_252` implementation. User requested the next controlled Matrix Editor import slice and provided business rules plus real product specification samples for Matrix extraction.

This task is the first import implementation slice and intentionally limits Matrix extraction to `.docx`. Because real product specifications contain many non-Matrix tables, this task must include Word COM-assisted table location metadata so the user can correct selection by page/table context instead of counting the document-wide table index.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Bounded full-stack slice with existing backend parser/API foundations.
- Requires deterministic parser refinement, Word COM layout metadata through the existing Office boundary, typed API additions, and focused Matrix Editor UI wiring.
- Avoids PDF/Excel dependencies in this slice; Word COM follows the existing Windows Office gateway direction.

## Objective

Implement the minimal `.docx` Matrix import loop in Matrix Editor:

1. Add an Import entry point in Matrix Editor.
2. Let the user preview a `.docx` product specification Matrix before applying it.
3. Improve `.docx` Matrix table detection using provided business rules.
4. Allow manual table selection when automatic detection fails or chooses the wrong table, using page number, page-local table number, preceding paragraph, or obvious table text features.
5. Generate a new Matrix draft version from the import preview.
6. Let the user choose whether the imported Matrix replaces or appends to the current Matrix draft.
7. Display import source traceability in Matrix Editor.

## Business Rules From User

- Qualification Matrix is usually near the final document sections.
- Nearby title/heading often includes:
  - `Qualification Test`
  - `Qualification Test Sequences`
  - `Test Matrix`
- Matrix table shape:
  - left columns: `Test Item`, `Section`
  - right columns: multiple Group columns
  - group labels may be `1`, `2`, `3`, `8a`, `8b`, `G1`, `G2`, or `Group 1`
- Section values often match `^\d+(\.\d+)+$`, for example `5.4`, `6.1`, `7.2`, `8.1`.
- Group cells are mostly numeric tokens, for example `1`, `1,15`, `2,7,9`, `3(a)`.
- Empty Matrix cells are normal.
- Final row often contains `Sample Quantity` or `Sample Size` and must become per-group sample quantity, not a normal test step.
- One product specification usually contains one Matrix table.
- Operators usually know the Matrix location as:
  - page number
  - the Nth table on that page
  - the paragraph immediately before the table
  - an obvious phrase/header inside or near the table
- Operators should not be expected to count the document-wide table index because product specifications contain many tables.

## Local Sample Sources For Manual Smoke

These files are local validation inputs only and must not be hard-coded into application code:

- `C:\Users\White\Desktop\AI information\Spec\GS-12-1507 RA Coplanar Rev7 (3).docx`
- `C:\Users\White\Desktop\AI information\Spec\GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`
- `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.doc`
- `C:\Users\White\Desktop\AI information\Spec\matrix.xlsx`
- `C:\Users\White\Desktop\AI information\Spec\PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`

Only the two `.docx` samples are in TASK_252 implementation scope. The `.doc`, `.xlsx`, and PDF samples are retained for follow-up tasks.

## Scope

Allowed:

- `.docx` Matrix extraction only.
- Word COM-assisted table location metadata for `.docx` manual correction.
- Backend parser refinement under `backend/modules/test_plan`.
- Application service/API support for previewing an auto-selected or manually located `.docx` table.
- Matrix Editor import UI and local apply flow.
- Draft creation/update as a new version after user confirmation.
- Source metadata display in Matrix Editor.
- Unit/integration/static frontend tests.

Forbidden:

- `.doc`, PDF, Excel import implementation.
- Cross-project Matrix copy implementation.
- Report generation, fee calculation, or test record generation changes.
- StepInstance/test execution persistence.
- AI extraction.
- PDF/Excel parser dependencies.
- Direct frontend access to Word files or SQLite.

## Acceptance Criteria

- Matrix Editor has a visible `Import` action.
- `.docx` preview returns:
  - selected table index
  - page number when Word COM can resolve it
  - page-local table number when Word COM can resolve it
  - preceding paragraph or nearby title hint when available
  - candidate table list with confidence/reasons
  - groups
  - normal test rows/steps
  - sample quantity per group when `Sample Quantity` or `Sample Size` row exists
  - warnings and blockers
  - source metadata
- Automatic table selection prefers the best Matrix-like table near the end of the document.
- User can manually specify page number plus page-local table number when automatic detection is wrong.
- User can search/filter candidates by preceding paragraph or obvious table text.
- Document-wide table index can be shown as diagnostic traceability but is not the primary user input.
- If Word COM is unavailable, the API returns an actionable blocker for page-based manual selection instead of silently falling back to an unusable workflow.
- Import confirmation creates a new draft version before applying to the editor.
- User must choose replace current Matrix or append imported Matrix.
- Imported source is visible after apply.
- Existing Matrix Editor manual editing and `Samples Quantity (PCS)` guards continue to work.
- Build and targeted backend/frontend tests pass.

## Validation

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_source_candidates_api.py -q
```

Result: passed, `12 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252 or task251 or task249"
```

Result: passed, `3 passed`, `93 deselected`.

Real `.docx` sample smoke:

- `GS-12-1507 RA Coplanar Rev7 (3).docx`: supported, selected table `1`, extracted `10` groups and `130` steps. Warnings include duplicate sequence notices from the source Matrix.
- `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`: supported, selected table `14`, extracted `11` groups and `98` steps.

Manual UI smoke path:

1. Open Matrix Editor for a project.
2. Click `Import`.
3. Preview a real `.docx` product specification.
4. Verify automatic candidate selection.
5. Manually select by page number and page-local table number, then preview again.
6. Manually search/filter by preceding paragraph or obvious table text when needed.
7. Confirm import as replace.
8. Confirm import as append in a separate run.
9. Verify source metadata and sample quantity row are visible.

## Deferred Follow-Up Tasks

- `TASK_253`: Excel fixed-template Matrix import.
- `TASK_254`: Legacy `.doc` Matrix import through the same Word COM table-location/read gateway.
- `TASK_255`: PDF Matrix import with approved deterministic table extraction dependency.
- `TASK_256`: Copy Matrix from another project draft/reviewed authority.
