# TASK_252 Plan - Matrix Editor DOCX Import Preview And Manual Table Selection

## 1. Task Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task before this plan: none
- New planned task: `TASK_252_MATRIX_EDITOR_DOCX_IMPORT_PREVIEW_AND_MANUAL_TABLE_SELECTION`
- Why allowed now: `TASK_251` is complete, and the user requested the next controlled Matrix Editor import plan with `.docx` as the first implementation slice.

## 2. Goal

Build the first real Matrix import loop for Matrix Editor using `.docx` product specification files:

```text
select/identify source -> preview extracted Matrix -> manual table correction if needed -> create new draft version -> choose replace or append -> fill editor -> show source
```

This is not the full import program. It is the smallest slice that validates existing Word parsing through the actual Matrix Editor workflow.

Revision after sample-source discussion:

- The original plan assumed manual correction by document-wide table index.
- That is not usable for real product specifications because Word files contain many tables.
- TASK_252 must therefore include Word COM-assisted table location metadata so an operator can select by page number, page-local table number, preceding paragraph, or obvious table text.
- Matrix extraction remains `.docx` only in this task. `.doc`, Excel, PDF, and cross-project copy stay deferred.

## 3. Product Boundary

Matrix remains the execution authority map. Import is only a draft creation/update path:

- Imported data must not silently become confirmed authority.
- User must preview blockers/warnings first.
- User must choose replace or append.
- Import must create a new version before changing the active editable Matrix.
- Source traceability must be visible after import.

## 4. Existing Code To Reuse

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/application/project_test_plan_draft_service.py`
- `backend/api/routes_project_test_plan_drafts.py`
- `backend/api/routes_project_test_plan_matrix_edit.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`

## 5. Backend Design

### 5.1 Parser Refinement

Update `ProductSpecMatrixParser` so it no longer accepts only `Group 1` style headers.

Candidate scoring should use:

- table is later in document
- nearby or detected title text contains:
  - `Qualification Test`
  - `Qualification Test Sequences`
  - `Test Matrix`
- left side has `Test`, `Test Item`, or `Test Items`
- section-like column has values matching `^\d+(\.\d+)+$`
- group headers match:
  - `Group 1`
  - `G1`
  - `1`
  - `8a`
  - `8b`
- group cells contain numeric token patterns such as:
  - `1`
  - `1,15`
  - `2,7,9`
  - `3(a)`
- rows labelled `Sample Quantity` or `Sample Size` are extracted into group `sample_size`, not test steps

### 5.1A Word COM Table Location Metadata

Add an Office-boundary method for `.docx` table layout metadata. The frontend and API must not call Word COM directly.

Recommended gateway result:

```python
@dataclass(frozen=True, slots=True)
class WordTableLocation:
    table_index: int
    page_number: int | None
    page_table_index: int | None
    preceding_paragraph: str | None
    text_preview: str
    row_count: int
    column_count: int
```

Implementation notes:

- Use Word COM through `WordDocumentGateway` or a focused helper under `backend/infrastructure/office`.
- Open documents read-only and never mutate source files.
- Use COM only inside infrastructure.
- Preserve python-docx table extraction as the deterministic content parser where suitable.
- COM metadata should allow mapping a user location (`page_number`, `page_table_index`) back to the selected table.
- If COM is unavailable, return a clear blocker for page-based manual selection.

Why this belongs in TASK_252:

- User knowledge is page-based, not document-wide table-index-based.
- Product specifications can contain many tables before the Matrix.
- Without COM location metadata, the manual correction path is not usable enough for real smoke testing.

### 5.2 Candidate Tables

Add a read model such as:

```python
@dataclass(frozen=True, slots=True)
class MatrixTableCandidate:
    table_index: int
    page_number: int | None
    page_table_index: int | None
    confidence: int
    reasons: tuple[str, ...]
    title_hint: str | None
    preceding_paragraph: str | None
    text_preview: str
    row_count: int
    column_count: int
    group_labels: tuple[str, ...]
    selected: bool
```

`MatrixParseResult` should include candidate tables.

### 5.3 Manual Table Selection

Extend preview command:

```python
@dataclass(frozen=True, slots=True)
class MatrixPreviewFromPathCommand:
    source_path: Path
    project_id: str | None = None
    table_index: int | None = None
    page_number: int | None = None
    page_table_index: int | None = None
    table_text_query: str | None = None
    operator_page_hint: int | None = None
```

Behavior:

- if `page_number` and `page_table_index` are provided, resolve through COM table location metadata and parse that table
- if `table_text_query` is provided, filter candidates by preceding paragraph / title hint / table preview text
- if `table_index` is provided, treat it as diagnostic fallback, not the primary UI path
- if invalid location is provided, return actionable blocker
- if no manual selector is provided, auto-select highest-confidence Matrix candidate

Important boundary: `python-docx` cannot reliably know Word page numbers because pages are layout results. TASK_252 therefore uses Word COM for location metadata, not frontend file access or parser-layer COM calls.

### 5.4 Preview Response

Extend API response with:

- `candidate_tables`
- `selected_table_index`
- `selected_page_number`
- `selected_page_table_index`
- `selection_mode`: `auto`, `manual_page_table`, `manual_table_index`, or `text_query`
- `manual_selector`
- `source_trace`
- `sample_size` per group

Keep route bodies thin and call application services only.

## 6. Frontend Design

### 6.1 Matrix Editor Import Entry

Add `Import` near existing Matrix Editor action controls.

Interaction:

1. User opens import panel.
2. User enters/selects `.docx` source.
3. User previews.
4. UI displays selected table, candidate table list, warnings, blockers, groups/steps, and sample quantity.
5. If wrong table, user enters page number and table number on that page, or searches by preceding paragraph / obvious table text, then previews again.
6. User selects `Replace current Matrix` or `Append to current Matrix`.
7. User confirms, creating a new draft version.

Keep this as an inline panel or side panel, not a modal-first workflow.

### 6.2 Source Selection

For this task, support the existing practical path first:

- project source candidate `.docx`
- external `.docx` path fallback if already available in the local Windows environment

Do not implement `.doc`, PDF, Excel, or cross-project copy UI in this task.

If browser file upload is selected instead of path/candidate, it must be a separate explicit backend storage slice because source traceability and project file asset registration need a clean boundary.

### 6.3 Apply To Editor

Map preview into Matrix Editor state:

- groups become group columns
- unique source rows become Matrix rows
- group step tokens fill group cells
- `sample_size` fills `Samples Quantity (PCS)` row
- source metadata is shown in the editor

Replace:

- current Matrix rows/groups/sample quantities are replaced by imported version

Append:

- imported test rows are appended after current normal rows
- imported groups either create new group columns or map by explicit label only if labels match exactly
- conflicts produce warnings, not silent merge

### 6.4 New Draft Version

Applying an import must create or update through the existing draft service path so a new version is available. It must not silently mutate confirmed authority.

Recommended rule:

- if current draft is reviewed, create a new draft
- if current draft is draft, create a new version from import preview rather than overwriting in place
- preserve `source_document_name`, `source_format`, `selected_table_index`, `operator_page_hint`, and `selection_mode`

## 7. File-Level Change Plan

Backend:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- possibly `backend/modules/test_plan/__init__.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- optionally new feature files under `frontend/src/features/matrix-editor/` if the import panel would make the workspace too large
- `frontend/src/workbench.css`

Tests:

- `tests/unit/test_product_spec_matrix_parser.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_frontend_shell_files.py`

Docs / task:

- `tasks/TASK_252_MATRIX_EDITOR_DOCX_IMPORT_PREVIEW_AND_MANUAL_TABLE_SELECTION.md`
- `docs/task_board.md`

## 8. Risks

1. Word COM environment dependency
   - Page-based table location requires Microsoft Word automation.
   - Mitigation: keep COM inside infrastructure, open read-only, return clear blocker when unavailable.

2. Page number ambiguity without COM
   - `.docx` has no stable page model in `python-docx`.
   - Mitigation: do not pretend page numbers are available without COM.

3. Merged cells
   - `python-docx` can repeat merged-cell text in row cells, which may confuse header detection.
   - Mitigation: scoring-based candidate selection and manual table override.

4. Numeric group headers
   - Headers such as `1`, `2`, `8a` can be mistaken for ordinary columns.
   - Mitigation: require section-pattern evidence and group-cell token evidence.

5. Sample quantity row misclassification
   - It must not become a normal test item.
   - Mitigation: explicit row label detection for `Sample Quantity` and `Sample Size`.

6. Append behavior conflicts
   - Imported rows/groups may collide with current draft.
   - Mitigation: append warnings and exact-label-only group mapping.

## 9. Validation Plan

Backend parser:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py -q
```

API preview:

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
```

Frontend build:

```powershell
cd frontend
npm run build
```

Frontend static checks:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252 or matrix_editor"
```

Manual smoke with real samples:

1. Use these local sample files as validation inputs, never hard-code them:
   - `C:\Users\White\Desktop\AI information\Spec\GS-12-1507 RA Coplanar Rev7 (3).docx`
   - `C:\Users\White\Desktop\AI information\Spec\GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`
   - `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.doc`
   - `C:\Users\White\Desktop\AI information\Spec\matrix.xlsx`
   - `C:\Users\White\Desktop\AI information\Spec\PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`
2. For TASK_252 implementation validation, use the two `.docx` files.
3. Preview auto-selected Matrix.
4. Confirm selected candidate table, page number, page-local table number, preceding paragraph, and warnings.
5. Manually enter page number plus page-local table number and preview again.
6. Search/filter by preceding paragraph or obvious table text when needed.
7. Apply as replace.
8. Apply as append in a separate draft.
9. Verify `Samples Quantity (PCS)` values are populated when source has `Sample Quantity` or `Sample Size`.
10. Verify source metadata remains visible.

## 10. Follow-Up Roadmap

- `TASK_253`: Excel fixed-template Matrix import.
- `TASK_254`: Legacy `.doc` import through the same Word COM table-location/read gateway.
- `TASK_255`: PDF Matrix import after approving deterministic PDF table extraction dependency.
- `TASK_256`: Copy Matrix from another project draft or reviewed authority.

## 11. Stop Point

Do not implement this task until the user explicitly approves `TASK_252`.
