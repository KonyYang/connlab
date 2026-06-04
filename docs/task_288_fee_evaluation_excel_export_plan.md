# TASK_288 Fee Evaluation Excel Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for execution tracking.

**Goal:** Export the reviewed Matrix-derived Fee Evaluation draft into the official fee workbook template and register the generated output lineage.

**Architecture:** Add a backend application export service that consumes TASK_286 fee draft data, writes the workbook through the Office gateway boundary, and registers a `ProjectOutputRecord` for `fee_evaluation`. Keep Excel as an output artifact and keep fee rule maintenance, UI review persistence, StepInstance, and report expansion out of scope.

**Tech Stack:** Python 3.11+, FastAPI, pytest, existing Office gateway boundary, existing `ProjectOutputRecordService`, existing external resource/project folder infrastructure where available.

---

## Current Task Context

- Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current dependency chain: TASK_288 is blocked until TASK_287 is complete.
- Why this task becomes allowed: TASK_288 can only be implemented after TASK_286 and TASK_287 are complete and this plan is explicitly approved.
- Current planning allowance: user explicitly requested a detailed TASK_288 executable plan.
- Implementation gate: do not write implementation code until the user explicitly approves this plan and the task board marks TASK_288 as current/allowed.

## Scope Summary

### In Scope

- Backend export service for active confirmed Matrix fee draft.
- Excel gateway write support for structured TASK_286 fee draft rows.
- Preserve official template layout where practical, especially `Testing Prices`.
- Controlled output path generation.
- No-overwrite guard unless `overwrite=true`.
- `ProjectOutputRecord` registration for `fee_evaluation`.
- Prepared by default:
  - ConnLab login user first when future login context is available.
  - Windows/computer user fallback in V1.
- Approved by is supplied per export or left blank for manual Excel completion according to request.
- `.xlsx` fallback allowed when `.xls` COM automation is unavailable or unsuitable.
- Backend unit and integration tests.

### Out Of Scope

- No pricing rule maintenance UI.
- No automatic Unit Price Reference import/update workflow.
- No persisted edited fee draft unless TASK_287 introduced an approved review payload contract.
- No StepInstance, execution persistence, report generation expansion, AI validation, or approval package assembly expansion.
- No broad rewrite of legacy `test_record_fee_*` services.
- No direct UI work unless a later approved task adds an export button.

## Existing Code Fit

Relevant existing files:

- `backend/application/confirmed_matrix_fee_draft_service.py`
  - Source of structured fee draft rows, totals, rule version, and matrix traceability.
- `backend/api/routes_confirmed_matrix_fee_draft.py`
  - Existing read-only draft response mapper.
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - Current COM-only fee workbook gateway.
  - Currently writes placeholder summary from legacy `TestRecordFeeDatasetPreview`; TASK_288 replaces/extends this with structured fee-draft writing.
- `backend/application/project_output_record_service.py`
  - Existing output lineage registration and stale/current status logic.
- `backend/api/routes_project_output_records.py`
  - Existing output status API; TASK_288 should register through service, not duplicate route logic.
- `backend/application/test_record_fee_document_generation_service.py`
  - Legacy combined test-record/fee path; do not expand it except for narrow compatibility if required by imports.
- `backend/shared/config.py`
  - Currently has Test Record template settings but no Fee Evaluation template setting.
- `backend/domain/enums.py`
  - Existing `ProjectOutputKind.FEE_EVALUATION`.

## Data Semantics

### Excel Is Output

The generated workbook is a derived output artifact. It must not become the source of truth for Matrix authority, fee rules, or reviewed fee lines.

### Export Source

Use TASK_286 service output:

```python
ConfirmedMatrixFeeDraftService.build_draft(
    BuildConfirmedMatrixFeeDraftCommand(project_id=project_id)
)
```

Export must reject drafts that are not ready unless explicit `allow_review_required=True` is supplied by the export command. V1 default should be conservative:

- `draft_status == "ready"`: export allowed.
- `draft_status == "needs_review"`: reject by default with actionable reason.
- `draft_status == "empty"`: reject with no fee lines reason.

This keeps TASK_288 aligned with "reviewed draft" semantics without adding review persistence.

### Line Traceability

Workbook write input must retain:

- project id.
- confirmed Matrix id.
- confirmed revision.
- pricing rule version id.
- pricing effective date.
- line-level `matched_rule_id`.
- line-level `matched_rule_version_id`.
- line-level confirmed group/row identifiers.

Traceability may be written into hidden workbook cells, a metadata note block, or an output-record note. It must be available in service result and output record note even if the official visible sheet has limited room.

### Prepared By

Implement a small resolver in application layer:

```python
def resolve_prepared_by(connlab_user: str | None) -> str:
    ...
```

Policy:

- if `connlab_user` is non-empty, use it.
- else use `getpass.getuser()`.
- if OS user cannot be resolved, use empty string and add warning.

Do not implement authentication in TASK_288.

### Approved By

`approved_by` is request-scoped:

- If supplied, write it to the workbook header.
- If omitted or blank, leave the workbook field blank and add a warning that approval remains manual.
- Do not default `approved_by` from any system user.

### Template Source

Use explicit request template path first. If later settings add a fee template path, that can become a fallback in a separate task.

V1 command field:

```python
template_path: Path
```

The known current authoritative template is:

```text
D:\Source\Template\Testing Fee Evaluation-Even.xls
```

This absolute path should not be hard-coded in service defaults. It may appear in tests/docs as an operator example only.

## API Design

Create a dedicated export route:

```text
POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export
```

Request:

```python
class ConfirmedMatrixFeeEvaluationExportRequest(BaseModel):
    template_path: str
    output_dir: str | None = None
    output_file_name: str | None = None
    overwrite: bool = False
    allow_review_required: bool = False
    prepared_by: str | None = None
    approved_by: str | None = None
```

Response:

```python
class ConfirmedMatrixFeeEvaluationExportResponse(BaseModel):
    project_id: str
    output_path: str
    output_format: str
    status: str
    confirmed_matrix_id: str
    confirmed_revision: int
    pricing_rule_version_id: str
    pricing_effective_from: str | None
    prepared_by: str | None
    approved_by: str | None
    output_record_id: str | None
    warnings: list[str]
```

Status mapping:

- `200`: workbook generated and output record registered.
- `400`: invalid request, existing output without overwrite, not-ready draft.
- `404`: project, confirmed Matrix, template, or output directory not found.
- `422`: internal draft/gateway data cannot be mapped to workbook rows.
- `503`: Excel automation unavailable and `.xlsx` fallback cannot be produced.

No browser download behavior is required in this task.

## Application Service Design

Create `backend/application/confirmed_matrix_fee_evaluation_export_service.py`.

Core dataclasses:

```python
@dataclass(frozen=True, slots=True)
class ExportConfirmedMatrixFeeEvaluationCommand:
    project_id: str
    template_path: Path
    output_dir: Path | None = None
    output_file_name: str | None = None
    overwrite: bool = False
    allow_review_required: bool = False
    prepared_by: str | None = None
    approved_by: str | None = None
    connlab_user: str | None = None


@dataclass(frozen=True, slots=True)
class ExportConfirmedMatrixFeeEvaluationResult:
    project_id: str
    output_path: Path
    output_format: str
    status: str
    confirmed_matrix_id: str
    confirmed_revision: int
    pricing_rule_version_id: str
    pricing_effective_from: str | None
    prepared_by: str | None
    approved_by: str | None
    output_record_id: str | None
    warnings: tuple[str, ...]
```

Service dependencies:

```python
class FeeEvaluationWorkbookWriter(Protocol):
    def generate_from_draft(
        self,
        *,
        template_path: Path,
        output_path: Path,
        draft: FeeEvaluationDraft,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        ...
```

Concrete service:

```python
class ConfirmedMatrixFeeEvaluationExportService:
    def __init__(
        self,
        *,
        fee_draft_service: ConfirmedMatrixFeeDraftService,
        project_output_service: ProjectOutputRecordService,
        workbook_writer: FeeEvaluationWorkbookWriter,
    ) -> None:
        ...
```

Validation flow:

1. Validate template path exists and suffix is `.xls` or `.xlsx`.
2. Build draft from active confirmed Matrix.
3. Reject empty/needs-review draft unless `allow_review_required=True`.
4. Resolve output directory:
   - explicit `output_dir` first.
   - otherwise use a narrow existing project folder/output root helper only if available without broad redesign.
   - otherwise return actionable missing output directory error.
5. Build deterministic output file name when not supplied:
   - `<project_id>_fee_evaluation_<confirmed_revision>_<pricing_rule_version_id>.xls`
   - sanitize unsafe filename characters.
6. Reject existing target unless `overwrite=True`.
7. Resolve `prepared_by`.
8. Pass structured draft to gateway.
9. Register `ProjectOutputRecord`:
   - `output_kind=ProjectOutputKind.FEE_EVALUATION`
   - `status=ProjectOutputStatus.CURRENT`
   - `source=ProjectOutputSource.SYSTEM_GENERATED`
   - `output_path=str(result.output_path)`
   - `draft_id`/version bridge: use active reviewed draft id if available from existing `ProjectOutputRecordService` path, or register against a confirmed-matrix-compatible draft id only if repository already exposes it.

Important lineage note:

Current `ProjectOutputRecordService` links freshness to `ProjectTestPlanDraft` ids/versions. Confirmed Matrix authority has its own ids/revisions. TASK_288 should not redesign the output record schema. If no direct confirmed-to-draft id is available from existing repositories, register the output record with the active reviewed draft id returned by existing output-status infrastructure, and store confirmed Matrix id/revision plus fee rule version in `note`.

## Workbook Gateway Design

Modify `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`.

Add a new method:

```python
def generate_from_draft(
    self,
    *,
    template_path: Path,
    output_path: Path,
    draft: FeeEvaluationDraft,
    prepared_by: str | None,
    approved_by: str | None,
) -> FeeEvaluationWorkbookWriteResult:
    ...
```

Keep old `generate(... preview: TestRecordFeeDatasetPreview)` temporarily for compatibility with legacy `TestRecordFeeDocumentGenerationService` unless TASK_288 explicitly updates all callers.

Visible workbook write policy:

- Prefer sheet named `Testing Prices`.
- If the sheet is missing, fail with an actionable gateway error.
- Preserve template formatting where practical by copying/writing into existing rows.
- Write header fields:
  - project id or LTR if available through future command extension.
  - prepared by.
  - approved by when supplied.
  - pricing effective date.
  - pricing rule version id.
- Write fee rows:
  - group label.
  - description/test item.
  - unit price.
  - units.
  - base fee.
  - discount.
  - testing fee.
- Write totals using structured draft values when available.
- For review-required exported rows allowed by `allow_review_required=True`, leave uncertain numeric fields blank rather than guessing.

Fallback policy:

- Preferred path for `.xls`: Excel COM open template and SaveAs target.
- If COM is unavailable and target/template can be represented as `.xlsx`, write `.xlsx` fallback using project-available Python spreadsheet tooling only if already available in dependencies.
- If no safe fallback writer is available, raise `OfficeAutomationUnavailable` and map route to `503`.

Do not add a new external dependency solely for fallback unless separately approved.

## File-Level Changes

### Create

- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
  - Export service, command/result dataclasses, validation, prepared-by resolver.

- `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
  - Thin FastAPI route and DTO mapping.

- `tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py`
  - Service behavior tests with fake draft service, writer, and output service.

- `tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py`
  - Route tests for request validation and output record behavior.

### Modify

- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - Add structured draft writer method.
  - Keep legacy method until all existing callers are deliberately migrated.

- `backend/infrastructure/office/models.py`
  - Extend `FeeEvaluationWorkbookWriteResult` only if status/output format/warnings need typed additions.

- `backend/api/dependencies.py`
  - Add `get_confirmed_matrix_fee_evaluation_export_service()`.

- `backend/api/main.py`
  - Include the new export router.

- `tests/unit/test_fee_evaluation_workbook_gateway.py`
  - Add structured draft writer tests.

- `tests/integration/test_api_default_dependencies.py`
  - Add smoke assertion only if current dependency test enumerates routers/services.

- `docs/task_board.md`
  - Update only after implementation and validation pass.

## Implementation Tasks

### Task 1: Confirm TASK_286/TASK_287 Inputs

- [ ] Verify `FeeEvaluationDraft` dataclasses and route response still contain `matched_rule_version_id`.
- [ ] Verify TASK_287 did not add a persisted reviewed-draft API.
- [ ] Decide export readiness from TASK_286 `draft_status` unless a reviewed payload exists from an approved later change.

### Task 2: Add Export Service Tests First

- [ ] Test ready draft exports and registers output record.
- [ ] Test needs-review draft is rejected by default.
- [ ] Test `allow_review_required=True` passes review-required draft to writer without guessing missing numeric fields.
- [ ] Test existing output path rejects when `overwrite=False`.
- [ ] Test prepared-by uses supplied ConnLab user over Windows fallback.
- [ ] Test approved-by remains blank/manual when omitted.

### Task 3: Implement Application Export Service

- [ ] Create command/result dataclasses.
- [ ] Implement template/output validation.
- [ ] Implement deterministic sanitized file naming.
- [ ] Implement prepared-by resolver.
- [ ] Implement draft readiness guard.
- [ ] Implement writer call.
- [ ] Implement output record registration with fee kind and lineage note.

### Task 4: Add Gateway Structured Writer Tests

- [ ] Test unsupported template type still fails.
- [ ] Test missing template still fails.
- [ ] Test missing `Testing Prices` sheet fails when COM/fallback fake workbook exposes that condition.
- [ ] Test structured writer maps groups/rows/total fields into workbook writer calls using a fake Excel adapter if direct COM is not available.
- [ ] Test fallback `.xlsx` path when COM is unavailable and fallback writer is available.

### Task 5: Implement Workbook Gateway Method

- [ ] Add `generate_from_draft(...)`.
- [ ] Locate `Testing Prices` sheet by name.
- [ ] Write header fields and traceability metadata.
- [ ] Write grouped line rows.
- [ ] Preserve old `generate(... preview=...)` method for existing compatibility.
- [ ] Raise actionable errors for missing template, missing sheet, unavailable automation, and unsupported fallback.

### Task 6: Add API Route

- [ ] Create request/response Pydantic models.
- [ ] Map application errors to HTTP statuses.
- [ ] Keep route body thin and dependency-driven.
- [ ] Do not trigger browser download.

### Task 7: Wire Dependencies

- [ ] Add service builder in `backend/api/dependencies.py`.
- [ ] Include router in `backend/api/main.py`.
- [ ] Keep Office gateway behind infrastructure boundary.

### Task 8: Integration Tests

- [ ] Test export route rejects missing template.
- [ ] Test export route rejects no active confirmed Matrix.
- [ ] Test export route rejects needs-review draft by default where fixture can produce one.
- [ ] Test successful route registers `fee_evaluation` output record using a fake writer dependency override.
- [ ] Test output status summary shows `fee_evaluation` current after export.
- [ ] Test later active Matrix/draft change can surface stale where existing output-status infrastructure supports it.

### Task 9: Validation And Task Closure

- [ ] Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
```

- [ ] Run:

```powershell
py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py tests/integration/test_project_output_records_api.py -q
```

- [ ] Run fee-draft regression:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q
```

- [ ] Run:

```powershell
git diff --check
```

- [ ] Update `docs/task_board.md` only after implementation and validation pass.
- [ ] Stop after TASK_288 completion; do not start rule-maintenance, approval package, or UI export follow-ups.

## Risks And Mitigations

- Risk: Official `.xls` template requires Excel COM and may be unavailable in CI.
  - Mitigation: isolate COM behind gateway, unit-test with fakes, and test fallback behavior without requiring Office.
- Risk: Existing `ProjectOutputRecord` links to Project Matrix draft rather than Confirmed Matrix id.
  - Mitigation: use existing output-status draft linkage for freshness and store confirmed Matrix/rule traceability in record note/service result.
- Risk: Review-required rows could be exported with guessed values.
  - Mitigation: reject needs-review by default and preserve blanks/warnings when explicitly allowed.
- Risk: Hard-coded operator template path.
  - Mitigation: require request template path in V1; document the known operator path without baking it into service defaults.
- Risk: Legacy `test_record_fee_*` callers break.
  - Mitigation: keep existing gateway method until a separate compatibility cleanup task is approved.

## Acceptance Mapping

- Workbook export from reviewed fee draft: covered by service and gateway.
- `Testing Prices` rows and totals: covered by structured writer.
- No-overwrite guard: covered by service tests.
- Actionable template/automation errors: covered by route/gateway tests.
- `.xlsx` fallback: covered where project dependencies support a safe writer; otherwise route returns clear unavailable status.
- Prepared/Approved by semantics: covered by resolver and request mapping.
- Output record update: covered by `ProjectOutputRecordService` registration.
- Stale visibility: covered by existing output status infrastructure where supported.
- Scope boundary: maintained by no UI, no rule maintenance, no StepInstance/report expansion.

## Stop Rule

After this plan is approved, implementation still waits until TASK_288 is the current allowed task on `docs/task_board.md`. Completion of TASK_288 must stop and must not open later fee-rule maintenance, Approval Package, or UI export tasks automatically.
