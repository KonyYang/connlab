# TASK_181 Plan - Test Record Template And Fee Form Generation

## 1. Current Phase And Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task before creation: `none; TASK_180 complete`.
- Allowed now because TASK_180 produced the structured dataset preview required by downstream document generation.
- This plan is proposal-only. Implementation must wait for explicit user approval: `批准执行 TASK_181`.

## 2. Goal

Create a controlled backend generation path for the two approval-package files that currently depend on manually copying test-plan data:

- test record template document;
- fee evaluation form.

The service will consume the TASK_180 dataset preview instead of re-parsing specifications or relying on New Project draft data.

## 3. Design Decision

Use a two-layer generation design:

- Application service coordinates validation, dataset retrieval, output path safety, and result assembly.
- Infrastructure Office gateways perform all actual Word/Excel file writes.

Reasoning:

- `python-docx` is already a declared dependency and suitable for `.docx` test record generation.
- The user-provided fee template is `.xls`; this cannot be safely written with the current read-only XML `.xlsx` gateway and no `openpyxl` dependency is declared.
- Therefore `.xls` support must be isolated behind a dedicated Office gateway, with tests using fake seams and graceful unavailable reporting when COM is unavailable.

## 4. Data Flow

1. API receives project, draft, template paths, output directory, overwrite flag, and include flags.
2. Application service calls TASK_180 dataset preview service.
3. Application service validates:
   - at least one output requested;
   - templates exist;
   - output directory exists or is creatable under explicit command rules;
   - output files do not already exist when `overwrite=false`;
   - template extensions match supported gateway rules.
4. Application service builds deterministic output file names from project/draft/source data.
5. Word gateway copies the test record template and writes dataset tables/sections.
6. Fee workbook gateway copies the fee template and writes line candidates/summary, or reports an unavailable gateway if the required Excel writer is not available.
7. API returns generated file records and warnings.

## 5. Proposed Data Structures

Application command:

```python
@dataclass(frozen=True, slots=True)
class TestRecordFeeDocumentGenerationCommand:
    project_id: str
    draft_id: str
    test_record_template_path: Path | None
    fee_evaluation_template_path: Path | None
    output_dir: Path
    overwrite: bool = False
    include_test_record: bool = True
    include_fee_evaluation: bool = True
```

Generated file result:

```python
@dataclass(frozen=True, slots=True)
class GeneratedApprovalDocument:
    kind: str
    source_template_path: Path
    output_path: Path | None
    status: str
    warnings: tuple[str, ...]
```

Service result:

```python
@dataclass(frozen=True, slots=True)
class TestRecordFeeDocumentGenerationResult:
    project_id: str
    draft_id: str
    generated_files: tuple[GeneratedApprovalDocument, ...]
    warnings: tuple[str, ...]
```

## 6. API Contract

Endpoint:

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-documents/generate
```

Request DTO:

```json
{
  "test_record_template_path": "D:/Source/2/Template/FDQF-E-036 Test Record Template-Even.docx",
  "fee_evaluation_template_path": "D:/Source/2/Template/DL-2025-11-073 Form for Testing Fee Evaluation.xls",
  "output_dir": "D:/Project/DL-XXXX/Submitted Material",
  "overwrite": false,
  "include_test_record": true,
  "include_fee_evaluation": true
}
```

## 7. File-Level Changes

Add:

- `backend/application/test_record_fee_document_generation_service.py`
- `backend/api/routes_test_record_fee_document_generation.py`
- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
- `tests/unit/test_test_record_fee_document_generation_service.py`
- `tests/unit/test_test_record_document_gateway.py`
- `tests/unit/test_fee_evaluation_workbook_gateway.py`
- `tests/integration/test_test_record_fee_document_generation_api.py`

Modify:

- `backend/api/dependencies.py`
- `backend/api/main.py`
- `backend/infrastructure/office/models.py`
- `backend/infrastructure/office/__init__.py`
- `docs/task_board.md`

## 8. Implementation Boundaries

Allowed:

- Copy template to output path.
- Write generated test record content into a `.docx` copy through infrastructure gateway.
- Write fee evaluation content through infrastructure gateway.
- Return warnings for missing dataset fields and missing price source.
- Use fake gateway seams in tests.

Forbidden:

- Do not write Office files directly in API/application layers.
- Do not calculate fees without a price source.
- Do not mutate ProjectTestPlanDraft payloads.
- Do not mutate New Project intake/application draft data.
- Do not add frontend UI.
- Do not implement report generation or customer feedback forms.
- Do not add new dependencies without explicit approval.

## 9. Risk And Mitigation

Risk: `.xls` writing requires Microsoft Excel COM and cannot be validated in CI-like pytest environments.

Mitigation: Keep `.xls` writer behind a gateway protocol, unit-test application behavior with fake gateways, and make real COM unavailable states explicit and actionable.

Risk: Real templates may not have stable placeholders.

Mitigation: First implementation should append or fill deterministic generated sections rather than depend on fragile placeholder matching unless placeholders are found.

Risk: Generated output could overwrite manually edited files.

Mitigation: Default `overwrite=false`; block existing output paths.

## 10. Validation

Targeted implementation validation:

```powershell
py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\unit\test_test_record_document_gateway.py tests\unit\test_fee_evaluation_workbook_gateway.py tests\integration\test_test_record_fee_document_generation_api.py -q
```

Regression validation:

```powershell
py -m pytest tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

Board guard validation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 11. Review Checklist Result For Plan Stage

- Architecture boundary: planned application orchestration plus infrastructure Office writers.
- Scope: document generation only; no frontend, report, pricing, or feedback forms.
- Data source: Project-stage TASK_180 dataset preview only.
- Office boundary: no direct COM or python-docx usage outside infrastructure.
- Stop condition: wait for explicit implementation approval.
