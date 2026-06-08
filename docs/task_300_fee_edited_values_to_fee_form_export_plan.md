# TASK_300 Fee Edited Values To Fee Form Export - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: TASK_300_FEE_EDITED_VALUES_TO_FEE_FORM_EXPORT.
- Allowed now because: TASK_298 and TASK_299 are complete, and the series plan identifies TASK_300 as the next controlled step.
- Status: planned; awaiting explicit approval before implementation.

This plan is for review only. Do not implement until the user explicitly approves TASK_300 implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The work is a bounded data-flow implementation from existing local React state through typed API DTOs, timeout-protected application service, and an existing Excel COM gateway. The model should not make new pricing judgments, persistence decisions, or template redesigns.

## Step 1 - Task Understanding

### Goal

Export the current Fee Evaluation page's edited preview values into the generated Fee Form workbook.

### Inputs

- Active Confirmed Matrix authority.
- Existing Matrix basic-fill workbook rows.
- Existing official Fee Evaluation template.
- Current frontend local edited row values from TASK_299.
- Current frontend local summary values:
  - condition confirmation spend time
  - external cost
  - external cost note, exported only when the V1 template exposes a stable target anchor
  - lab manpower hourly rate

### Outputs

- Browser-downloaded `.xls` workbook.
- Existing output record behavior where available.
- Existing warnings/status behavior from TASK_288-TASK_291 export path.

### Modules

- Frontend Fee Evaluation feature.
- API client.
- FastAPI fee evaluation export route.
- Export application service and timeout/subprocess runner.
- Matrix basic-fill service.
- Office workbook gateway.
- Unit/integration/frontend tests.

### Not Allowed

- No edit persistence.
- No database migration.
- No rule-reference update.
- No new pricing-policy calculation beyond the existing TASK_299 formula.
- No broad template redesign.
- No StepInstance/execution/report scope.

## Design Overview

TASK_300 should reuse the existing production export path:

```text
FeeEvaluationReviewExportPage
  -> client.generateConfirmedMatrixFeeFileDownload(projectId, editedPayload)
  -> POST /api/projects/{id}/confirmed-matrix/fee-evaluation/file/generate
  -> ConfirmedMatrixFeeEvaluationExportTimeoutService
  -> subprocess runner
  -> ConfirmedMatrixFeeEvaluationExportService
  -> FeeEvaluationWorkbookGateway.generate_matrix_basic_fill(...)
  -> FileResponse guarded under generated_fee_files
```

The main change is to pass an optional edited-value payload into the existing direct-download route and through the export command. When no payload is present, behavior should remain compatible with current Matrix basic-fill export.

## Data Contract

### Frontend Request Type

Add a typed request in `frontend/src/api/client.ts`:

```ts
export type FeeEvaluationEditedRowExportInput = {
  source_line_id: string;
  confirmed_group_id: string;
  confirmed_row_id: string;
  step_token: string;
  step_index: number;
  spend_time: string;
  unit_price: string;
  unit_type: string;
  units: string;
  base_fee: string;
  discount: string;
  testing_fee: string;
  notes: string;
};

export type FeeEvaluationEditedSummaryExportInput = {
  condition_confirmation_spend_time: string;
  external_cost: string;
  external_cost_note: string;
  lab_manpower_hourly_rate: string;
};

export type FeeEvaluationEditedFileExportRequest = {
  rows: FeeEvaluationEditedRowExportInput[];
  summary: FeeEvaluationEditedSummaryExportInput;
};
```

Update `generateConfirmedMatrixFeeFileDownload(projectId, input?)` to POST JSON when `input` is provided and remain body-less-compatible when omitted.

### Backend DTO

Add matching Pydantic DTOs in `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`.

Validation rules:

- `source_line_id`, `confirmed_group_id`, and `confirmed_row_id`: stripped non-empty strings.
- `step_token`: stripped string; empty string is allowed only for no-step rows.
- `step_index`: non-negative integer.
- duplicate row identity tuple rejects 422:

```text
(source_line_id, confirmed_group_id, confirmed_row_id, step_token, step_index)
```

- value fields: accept strings; service normalizes before writing.
- `unit_type`: must be one of the TASK_299 UI labels or a canonical value that can map to a workbook display value.

### Application Command

Extend `ExportConfirmedMatrixFeeEvaluationCommand` with:

```python
edited_values: FeeEvaluationEditedExportValues | None = None
```

Use frozen dataclasses in `backend/application/confirmed_matrix_fee_evaluation_export_service.py` or a new adjacent module if this keeps the service file under the project size target.

Suggested dataclasses:

```python
@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedExportRow:
    source_line_id: str
    confirmed_group_id: str
    confirmed_row_id: str
    step_token: str
    step_index: int
    spend_time: str
    unit_price: str
    unit_type: str
    units: str
    base_fee: str
    discount: str
    testing_fee: str
    notes: str

@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedExportSummary:
    condition_confirmation_spend_time: str
    external_cost: str
    external_cost_note: str
    lab_manpower_hourly_rate: str

@dataclass(frozen=True, slots=True)
class FeeEvaluationEditedExportValues:
    rows: tuple[FeeEvaluationEditedExportRow, ...]
    summary: FeeEvaluationEditedExportSummary
```

## File-Level Changes

### Frontend

- `frontend/src/api/client.ts`
  - Add edited export request types.
  - Allow `generateConfirmedMatrixFeeFileDownload(projectId, input?)`.
  - Preserve blob response handling and structured error parsing.

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
  - Build edited export payload from `previewRows`, `costPreviewValues`, and existing preview calculation outputs.
  - Call `generateConfirmedMatrixFeeFileDownload(projectId, payload)`.
  - Keep local preview values non-persistent.

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
  - Add a small helper if useful:
    - `buildFeeEvaluationEditedExportRows(previewRows)`
    - `buildFeeEvaluationEditedExportSummary(costPreviewValues)`
  - Reuse existing calculation outputs; do not duplicate formula logic.
  - If `FeeEvaluationPreviewRow` does not currently preserve enough lineage for export identity, extend it from `FeeEvaluationLineItem` with the required fields (`sourceLineId`, `confirmedGroupId`, `confirmedRowId`, `stepToken`, `stepIndex`) before building the payload.
  - Include `notes` from the current preview row. Empty notes are valid and must not block export.

- Frontend tests:
  - `FeeEvaluationReviewExportPage.test.tsx`
  - `feeEvaluationPreviewModel.test.ts`

### API / Backend

- `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
  - Add optional request body to the direct-download route:

from fastapi import Body

def generate_confirmed_matrix_fee_file(
    project_id: str,
    request: ConfirmedMatrixFeeEvaluationEditedFileRequest | None = Body(default=None),
    ...
) -> FileResponse:
```

  - Convert request DTO to application dataclasses.
  - Preserve route-level output-path guard.

- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
  - Extend command with `edited_values`.
  - In `_export_matrix_basic`, pass edited values to workbook writer.
  - Validate duplicate/missing edits relative to Matrix basic-fill step-expanded lineage:
    - Extra identities are rejected.
    - Missing identities are allowed and fall back to current basic-fill defaults.
  - Do not rely on frontend `lineId` alone; it is a local preview key and may differ from backend `MatrixBasicFillLine.line_id`.

- `backend/application/confirmed_matrix_fee_evaluation_export_timeout_service.py`
  - Include edited values in subprocess payload serialization/deserialization.
  - Preserve timeout/manual-cleanup semantics.

- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - Extend `generate_matrix_basic_fill(...)` signature with `edited_values`.
  - Write edited values into the existing official `Testing Prices` columns.
  - Preserve template row copying, group formatting, inserted row handling, formula restoration, and SaveAs format behavior.

### Tests

- `tests/unit/test_fee_evaluation_workbook_gateway.py`
  - Fake COM workbook assertions for edited cells:
    - Man-hour
    - Unit Price
    - Unit Type
    - Units
    - Base Fee
    - Discount
    - Testing Fee formula/value
    - Notes as Excel comments on the final total-price cell (`I[row]`); blank notes create no comments
    - Condition confirmation
    - External Cost
    - External Cost note only when a stable template target is present; otherwise gateway warning

- `tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py`
  - Edited values pass to writer.
  - Duplicate row identity rejected.
  - Extra unknown row identity rejected.
  - Missing row identity falls back safely.
  - Frontend-local `lineId` mismatch cannot silently match the wrong row.

- `tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py`
  - Edited payload survives subprocess serialization.
  - Timeout behavior unchanged.

- `tests/integration/test_confirmed_matrix_fee_file_download_api.py`
  - Direct-download route accepts edited JSON body.
  - Direct-download route with no body keeps existing Matrix basic-fill behavior.
  - FileResponse path guard still applies.
  - Invalid payload returns 422/actionable response.

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
  - User edits values and clicks `Fee Form`; client receives edited payload.
  - Row lineage identity, notes, and summary fields are included.

- `tests/unit/test_frontend_shell_files.py`
  - Ensure TASK_300 does not add persistence routes or DB migration.

## Workbook Column Mapping

Use the official `Testing Prices` template columns already implied by gateway formula:

```text
A Group
B Man-hour / Spend Time
C Description
D Unit Price
E Unit Type
F Units
G Base Fee
H Discount
I Testing Fee
```

Testing Fee V1 behavior:

```text
I[row] = D[row] * F[row] * (1 - H[row]) + G[row]
```

V1 must write/restore the Excel formula in `I[row]` wherever the template supports formulas. If a fake or real template target cannot support formulas, the gateway may write the numeric value instead, but it must return a warning and tests must cover that fallback.

Notes V1 behavior:

- Notes are row-level operator explanation text for discounts, special price choices, or step-specific comments.
- Notes default to blank and do not participate in validation or fee calculation.
- Notes are not exported as a visible workbook column in TASK_300.
- If a row note is non-empty, the gateway inserts it as an Excel comment on that row's final total-price cell.
- If a row note is blank, the gateway must not insert a comment.
- The final total-price cell is the row-level `Testing Fee` cell in the official template mapping (`I[row]` in V1).

Discount export normalization:

- V1 writes discount as a numeric fraction in column `H` so the Excel formula remains valid.
- `10` and `10%` both write `0.1`.
- blank discount writes `0`.
- Tests must assert the fake gateway receives numeric-fraction discount values.

## Manual Summary Mapping

V1 should be conservative:

- `Condition confirmation`: write the dedicated condition confirmation spend-time field/row that already exists in the template anchor logic.
- `External Cost`: write the dedicated external-cost value if the template has a stable anchor; otherwise add a clear gateway warning and leave the value out rather than guessing a cell.
- `External Cost note`: write next to external cost only if the template has a safe target cell/column; otherwise add a warning.
- `Lab manpower hourly rate` and calculated lab manpower cost remain page-preview values unless the template has a stable approved target.

The implementation must not create a new arbitrary workbook section for missing anchors.

## Subprocess / Timeout Boundary

TASK_300 must keep production export under the TASK_291 timeout boundary.

Required checks:

- Parent serializes edited payload into subprocess command JSON.
- Child reconstructs dataclasses and calls direct export service.
- Child commits output record transaction on success exactly as current behavior does.
- Timeout response remains:

```json
{
  "message": "...",
  "elapsed_seconds": 90.0,
  "manual_cleanup_warning": "..."
}
```

## Risks And Mitigations

- Risk: frontend preview and workbook formulas diverge.
  - Mitigation: reuse the same formula semantics; add test fixtures for representative values.
- Risk: Excel template anchor for `External Cost note` is not stable.
  - Mitigation: gateway must detect and warn rather than guessing arbitrary cells.
- Risk: payload is large for many rows.
  - Mitigation: row count is workstation-scale; keep payload simple JSON and rely on existing local deployment.
- Risk: users think edits are saved after download.
  - Mitigation: TASK_300 does not persist; TASK_301 handles persistence.
- Risk: direct-download route becomes a file-serving bug.
  - Mitigation: keep existing route-level path guard unchanged.

## Validation Commands

After implementation:

```powershell
cd frontend
npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_file_download_api.py tests/integration/test_fee_evaluation_export_child_transaction.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Manual verification:

1. Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
2. Edit at least one row's `Man-hour`, `Unit Price`, `Unit Type`, `Units`, `Base Fee`, `Discount`, and optional `Notes`.
3. Edit `Condition confirmation`, `External Cost`, and `Cost note`.
4. Click `Fee Form`.
5. Open the downloaded `.xls` and compare the workbook values to the page.

## Stop Point

When TASK_300 implementation is later approved and completed, update `docs/task_board.md` and stop. Do not implement TASK_301 persistence in the same task.
