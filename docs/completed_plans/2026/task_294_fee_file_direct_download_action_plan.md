# TASK_294 Fee File Direct Download Action Plan

## Execution Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: TASK_294_FEE_FILE_DIRECT_DOWNLOAD_ACTION.
- Current status: Planned; awaiting explicit approval.
- Allowed reason: TASK_293 is complete, and the user approved creating TASK_294 after reviewing the Fee Evaluation page and asking for Test Record-style Fee file generation/download.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for executing this plan because the task is a bounded integration of existing backend export services, an existing Test Record direct-download pattern, and a focused React UI simplification. The model should avoid inventing new fee logic, settings screens, or workbook writers, and should implement only the route/client/page changes listed here.

## Goal

Replace the current Fee Evaluation export-settings panel with a direct `Fee file` download action inside the `Fee File` preview card.

The operator should not need a generated project folder before clicking the action. The backend should generate a temporary/server-side workbook output under ConnLab data storage and return it as a browser download, matching the current Test Record user flow.

## Current Reality

### Existing Fee Export

Endpoint:

```text
POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export
```

Characteristics:

- returns JSON metadata
- requires caller-provided `template_path`
- requires caller-provided or service-resolved `output_dir`
- currently used by the Fee page with latest project folder path
- already supports `fill_mode="matrix_basic"`
- already goes through the TASK_291 timeout-aware dependency

### Existing Test Record Download Pattern

Endpoint:

```text
POST /api/projects/{project_id}/confirmed-matrix/test-record-draft/generate
```

Characteristics:

- generates under `settings.data_dir / "generated_test_records"`
- returns `FileResponse`
- frontend calls `generateConfirmedMatrixTestRecordDraftDownload()`
- frontend creates an object URL and clicks a temporary anchor
- no project folder is required

### Existing Fee Page

Current page component:

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
```

Current supporting components:

```text
frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
frontend/src/features/fee-evaluation/FeeEvaluationReviewDetails.tsx
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
```

After TASK_293 follow-up, the page is preview-first, but still has a separate export panel and project-folder output dependency.

## Design Decisions

### 1. Add A New Download Endpoint

Do not repurpose the existing JSON export endpoint. Keep it for backend/API compatibility and approval-package style workflows.

Add a new endpoint in the same route module:

```text
POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/file/generate
```

Why:

- keeps direct download semantics explicit
- mirrors Test Record route
- avoids changing existing clients that expect JSON
- allows frontend `requestBlobResponse(...)` usage

### 2. Reuse The Existing Export Service

The route should call the existing `FeeEvaluationExportServicePort` dependency from TASK_291:

```python
service.export(
    ExportConfirmedMatrixFeeEvaluationCommand(
        project_id=project_id,
        template_path=FEE_FILE_TEMPLATE_PATH,
        output_dir=settings.data_dir / "generated_fee_files",
        output_file_name=None,
        overwrite=True,
        allow_review_required=True,
        fill_mode="matrix_basic",
    )
)
```

V1 collision policy:

- Use `overwrite=True` for generated download cache output to avoid repeat-click failures with deterministic file names.
- Keep the existing JSON export endpoint default `overwrite=False` unchanged.
- Do not overwrite the formal template.
- Concurrent route/API calls for the same project may race on the deterministic cache file. This is accepted for V1 offline-workstation usage because the UI disables the action while running, the output is only a generated download cache, and the official project-folder export path remains separate. Do not add a locking system or unique file-naming scheme in TASK_294.

### 3. Template Path

V1 uses the already confirmed formal template:

```text
D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls
```

This task does not add a settings UI or database setting for that path. If the formal template becomes configurable later, that should be a separate settings task.

### 4. Download Directory

Use:

```text
settings.data_dir / "generated_fee_files"
```

The route should create the directory with `mkdir(parents=True, exist_ok=True)` before calling the export service, because the export service requires an existing output directory.

Before returning a browser download, the route must validate the returned path defensively:

```text
resolved_download_dir = (settings.data_dir / "generated_fee_files").resolve()
resolved_output_path = result.output_path.resolve()
```

Required checks:

- `resolved_output_path.exists()`
- `resolved_output_path.is_file()`
- `resolved_output_path.suffix.lower() == ".xls"`
- `resolved_output_path` is inside `resolved_download_dir`

If any check fails, return an actionable server error instead of calling `FileResponse`. This route-level guard prevents future service/runner regressions from becoming an unintended file-serving path.

### 5. Frontend UI

The Fee page becomes:

```text
Fee File
  Back to Workbench
  All Group selector with selected fee value
  Fee file action
  Excel-like preview rows
  totals band

Review details
```

Remove the standalone export panel and its local `Approved by` / `File name` fields from V1. The generated file uses backend defaults, and manual completion remains inside Excel.

## Data And Interface Design

### Backend Route Constant

Candidate location:

```text
backend/api/routes_confirmed_matrix_fee_evaluation_export.py
```

Add:

```python
FEE_FILE_TEMPLATE_PATH = Path(
    "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls"
)
FEE_FILE_DOWNLOAD_DIR_NAME = "generated_fee_files"
```

The path is intentionally scoped to this controlled V1 route and documented in the task. Do not introduce a broader settings mechanism in this task.

### Backend Response

Return:

```python
FileResponse(
    path=resolved_output_path,
    filename=resolved_output_path.name,
    media_type="application/vnd.ms-excel",
)
```

For `.xlsx` fallback in the future, media type can be extended, but V1 formal template is `.xls`.

### Frontend API Client

Add:

```ts
export function generateConfirmedMatrixFeeFileDownload(
  projectId: string
): Promise<BlobDownloadResponse>
```

Implementation mirrors:

```ts
generateConfirmedMatrixTestRecordDraftDownload(projectId)
```

Endpoint:

```text
/api/projects/${projectId}/confirmed-matrix/fee-evaluation/file/generate
```

### Frontend Page State

Replace JSON export state:

```ts
type ExportState = "idle" | "running" | "success" | "error"
```

with download state:

```ts
type FeeFileDownloadState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "success"; fileName: string | null }
  | { kind: "error"; message: string; manualCleanupWarning?: string | null };
```

### Frontend Preview Component Props

Update `FeeEvaluationPreviewTable` to receive:

```ts
onGenerateFeeFile: () => void;
generateDisabledReason: string | null;
downloadState: FeeFileDownloadState;
scopeFeeLabel: string;
```

Remove:

```ts
selectedTotal
```

and replace with a combined group selector card:

```text
Preview group
[All Group v]
Fee
Pending Excel confirmation
```

The exact JSX may be split for clarity if `FeeEvaluationPreviewTable.tsx` grows too large.

V1 button enable rule:

- Enable `Fee file` only when `draftState.kind === "ready"`.
- Disable while the direct download is running.
- Do not require `projectFolderPath`.
- Do not infer active Matrix readiness from another endpoint in TASK_294.

This is intentionally stricter than the backend Matrix basic-fill export service, which may tolerate missing fee-draft metadata, because the current page preview is driven by `FeeEvaluationDraft`. Adding a separate active-Matrix/basic-fill readiness source is out of scope for TASK_294.

## File-Level Changes

### Backend

Modify:

```text
backend/api/routes_confirmed_matrix_fee_evaluation_export.py
```

Add the direct-download route and shared error mapping helper if duplication with the JSON route becomes noisy.

Do not modify:

```text
backend/application/confirmed_matrix_fee_evaluation_export_service.py
backend/infrastructure/office/**
```

unless tests expose a small compatibility issue. The intended implementation is route-level orchestration only.

### Frontend

Modify:

```text
frontend/src/api/client.ts
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
frontend/src/workbench.css
tests/unit/test_frontend_shell_files.py
```

Potential pure-model update:

```ts
buildFeeEvaluationPreviewScopeTotal(rows, groupFilter)
```

can remain, but the display label should be used inside the group-selector card rather than in a separate selected-total card.

### Docs

Update after implementation:

```text
docs/task_board.md
```

Mark TASK_294 complete and record validation.

## Implementation Tasks

### Task 1: Backend Route Tests First

Create focused tests for the new route.

Suggested files:

```text
tests/integration/test_confirmed_matrix_fee_file_download_api.py
```

Test cases:

1. Successful direct download:
   - override the export service dependency with a fake service
   - call `POST /api/projects/P1/confirmed-matrix/fee-evaluation/file/generate`
   - assert response status `200`
   - assert file download headers include `.xls`
   - assert fake service received:
     - `fill_mode="matrix_basic"`
     - `allow_review_required=True`
     - `output_dir` ending in `generated_fee_files`
     - formal optimized template path
2. Route-level path guard:
   - fake service returns a path outside `generated_fee_files`
   - assert non-success response
   - fake service returns missing file / directory / non-`.xls` file in separate cases where practical
   - assert no arbitrary path is served by `FileResponse`
3. Timeout mapping:
   - fake service raises `ConfirmedMatrixFeeEvaluationExportTimeoutError`
   - assert `503`
   - assert structured detail includes `manual_cleanup_warning`
4. Missing authority mapping:
   - fake service raises not-found error
   - assert `404`

Expected first run:

```text
FAIL, route does not exist
```

### Task 2: Implement Direct Download Route

Modify:

```text
backend/api/routes_confirmed_matrix_fee_evaluation_export.py
```

Steps:

1. Import `FileResponse` and `get_settings`.
2. Add route constants.
3. Add new POST route.
4. Create `settings.data_dir / "generated_fee_files"`.
5. Call existing timeout-aware service dependency.
6. Resolve and validate `result.output_path` before download:
   - must exist
   - must be file
   - must be `.xls`
   - must be inside `settings.data_dir / "generated_fee_files"`
7. Return `FileResponse`.
8. Reuse or extract exception mapping carefully so JSON route behavior remains unchanged.

Do not change existing `/fee-evaluation/export` response model or request model.

### Task 3: Frontend Client Tests / Static Guard

Update:

```text
tests/unit/test_frontend_shell_files.py
```

Assert:

- `generateConfirmedMatrixFeeFileDownload` exists in `client.ts`
- it uses `requestBlobResponse`
- it calls `/confirmed-matrix/fee-evaluation/file/generate`
- Fee page no longer imports/calls `exportConfirmedMatrixFeeEvaluation`
- Fee page no longer renders `Excel output`, `Output directory`, or project-folder blocker copy
- `Fee File` appears in preview component
- `Selected total` is absent

### Task 4: Implement Frontend API Client

Modify:

```text
frontend/src/api/client.ts
```

Add:

```ts
export function generateConfirmedMatrixFeeFileDownload(
  projectId: string
): Promise<BlobDownloadResponse>
```

Use the existing `requestBlobResponse` helper.

### Task 5: Frontend UI Tests First

Modify:

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
```

Test cases:

1. Page renders `Fee File` as the primary preview title.
2. Page does not render standalone `Excel output` / `Output directory` panel.
3. `Fee file` button is inside the `Fee File` preview section.
4. Missing project folder does not disable `Fee file` when the fee draft is loaded.
5. Clicking `Fee file` calls `generateConfirmedMatrixFeeFileDownload(projectId)` and triggers blob download.
6. API error displays business-readable inline feedback.
7. Group selector card shows `Pending Excel confirmation` for all rows and selected group when scope is not fully calculated.
8. Fully calculated selected group displays numeric group total.
9. Text `Selected total` is not rendered.

Expected first run before UI implementation:

```text
FAIL, page still has old export panel / old button wiring
```

### Task 6: Implement UI Simplification

Modify:

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
frontend/src/workbench.css
```

Steps:

1. Remove latest project folder fetch from Fee page context if no longer used.
2. Remove approved-by and file-name local state from V1 page.
3. Remove old export panel JSX.
4. Add `handleGenerateFeeFile()`.
5. Reuse the Test Record blob download pattern:
   - create object URL
   - create temporary anchor
   - use returned `fileName` or fallback
   - click anchor
   - revoke object URL
6. Put `Fee file` action into preview card.
7. Rename preview title to `Fee File`.
8. Merge group selector and selected scope fee into one control card.
9. Keep review details untouched except for any layout spacing adjustments.

### Task 7: Regression Validation

Run:

```text
py -m pytest tests/integration/test_confirmed_matrix_fee_file_download_api.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
cd frontend; npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

If backend direct-download tests require a fake generated file, use temporary paths under pytest `tmp_path`; do not write into the real formal template path.

## Error Handling

Frontend should map errors as follows:

- `404`: `Confirm Matrix authority before generating Fee file.`
- `422` template/config style error: show server message if business-readable.
- `503` timeout/unavailable:
  - show `Excel generation did not complete.`
  - include `manual_cleanup_warning` if returned
- unknown error: `Fee file generation failed.`

Do not show raw API paths or Python exception class names.

## Risks

- Real Excel COM generation can still be slow or unavailable; TASK_291 timeout boundary should prevent indefinite request hangs.
- The V1 template path remains a controlled absolute path. Making it configurable belongs in a later file-location/settings task.
- Repeated or concurrent API calls may overwrite generated cache output if `overwrite=True`; this is accepted for V1 offline-workstation usage because the UI disables duplicate clicks while running and the path is a download cache, not the official project-folder export. Do not add route-level locking in TASK_294.
- Output-record registration remains in the existing export service. If a project lacks required active draft context for registration, the endpoint should surface the existing actionable error rather than bypass traceability.

## Self-Check Checklist For Implementation

- Does the UI directly call Office? No.
- Does the API route directly manipulate Excel? No, it uses the existing application service.
- Does the route bypass the TASK_291 timeout-aware dependency? No.
- Does the task alter fee calculation rules? No.
- Does the task require project folder creation? No.
- Does the task keep the existing JSON export endpoint compatible? Yes.
- Does the task expose future file options or settings UI? No.
- Does the task stop after TASK_294 validation? Yes.
