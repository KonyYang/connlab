# TASK_311 Customer Feedback Form Generation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use test-driven development when implementing this plan.

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION`, complete.

Allowed reason: `docs/task_board.md` marked TASK_311 planned and the user explicitly approved implementation. This document records the executable plan used for TASK_311.

## Goal

Add a backend/API foundation that generates a Customer Feedback Form workbook from the configured Template folder's `E-4243` `.xlsx` template.

## Architecture

TASK_311 is a backend application-service-first generator with a thin API route and an Office infrastructure gateway. It discovers the Customer Feedback template from the existing Template folder resource, copies the template to a controlled generated-output location, and returns generated file metadata plus an explicit warning that verified Excel cell filling is deferred. It does not add frontend UI, package orchestration, public-drive placement, or downstream output registration.

## Mandatory Preconditions

Before implementation:

1. Read `AGENTS.md`.
2. Read `docs/task_board.md`.
3. Read `tasks/TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION.md`.
4. Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
5. Re-read this executable plan.
6. Confirm explicit user approval for implementation.

No `$impeccable` preload is required for TASK_311 implementation because V1 is backend/API only and introduces no frontend UI or user-facing layout change. If implementation scope changes to include UI, stop and update the task/plan first.

## Task Understanding

Goal:

- Generate a Customer Feedback Form `.xlsx` from a template stored in the configured Template folder.

Inputs:

- `project_id`
- Existing configured Template folder resource (`project_folder_template`)
- A unique template file directly under that folder whose file name contains `E-4243` and suffix is `.xlsx`
- Safe existing structured project context

Outputs:

- Generated Customer Feedback `.xlsx` copy
- Metadata including generated path, file name, matched template path, and warnings

Not allowed:

- No Workbench button or frontend action.
- No package preview or package execute.
- No public-drive publish.
- No ProjectOutputRecord registration.
- No Confirm Matrix, Confirm Fee, Section 2 sync, Test Record, Fee Form, or folder-generation side effects.
- No new workbook-writing dependency.
- No hardcoded production path such as `D:\Source\Template`.

## Current Code Context

Relevant existing patterns:

- `backend/domain/enums.py`
  - `ExternalResourceType.PROJECT_FOLDER_TEMPLATE = "project_folder_template"`
- `frontend/src/features/settings/settingsResourceConfig.ts`
  - User-facing `Template folder` is backed by `project_folder_template`
- `backend/api/dependencies.py`
  - Default dependency wiring pattern
- `backend/api/main.py`
  - Router registration pattern
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - Existing Excel COM write boundary pattern
- `backend/infrastructure/office/fee_evaluation_export_subprocess_runner.py`
  - Existing timeout-protected Excel export pattern
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - Existing document generation service shape

Important dependency reality:

- `pyproject.toml` has no `openpyxl` or other `.xlsx` writer dependency.
- TASK_311 must not add one without separate approval.
- Excel writes must remain behind an infrastructure gateway.

## Template Discovery Design

Create a small discovery helper in the TASK_311 application/service boundary or a focused utility module.

Rules:

- Input: configured Template folder `Path`.
- The folder must exist and be a directory.
- Candidate files are direct children only in V1.
- Candidate predicate:
  - `path.is_file()`
  - `"E-4243"` appears in `path.name` case-insensitively
  - `path.suffix.lower() == ".xlsx"`
- Sort candidates by normalized file name only for deterministic error reporting.
- If zero candidates, raise a readiness error with message similar to:
  - `Customer Feedback template was not found in Template folder. Add an .xlsx file whose name contains E-4243.`
- If multiple candidates, raise a readiness error with message similar to:
  - `Multiple Customer Feedback templates were found. Keep exactly one E-4243 .xlsx template in Template folder.`
- Do not choose by modified time, revision letter, filename sort, or directory order.

## Backend Service Design

Create:

- `backend/application/customer_feedback_form_generation_service.py`

Suggested dataclasses:

```python
@dataclass(frozen=True, slots=True)
class CustomerFeedbackFormGenerationCommand:
    project_id: str
    output_dir: Path | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class CustomerFeedbackFormGenerationResult:
    project_id: str
    template_path: Path
    output_path: Path
    output_file_name: str
    warnings: tuple[str, ...] = ()
```

Suggested service:

```python
class CustomerFeedbackFormGenerationService:
    def generate(
        self,
        command: CustomerFeedbackFormGenerationCommand,
    ) -> CustomerFeedbackFormGenerationResult:
        ...
```

Service dependencies:

- Project repository or project lookup service.
- External resource repository/read service for `project_folder_template`.
- Customer Feedback workbook gateway.
- Settings/config for safe generated-output root.

Behavior:

1. Validate project exists.
2. Load configured Template folder resource.
3. Discover the unique `*E-4243*.xlsx` template.
4. Build a controlled output path.
5. Build a safe identity payload from existing structured data.
6. Call infrastructure gateway to copy/write the workbook.
7. Return metadata and warnings.

Output path:

- The public API does not expose `output_dir` in V1.
- Internal callers may provide `output_dir` only when it resolves under the controlled generated output root.
- If no `output_dir` is provided, use a controlled generated output folder under configured app data, for example `settings.data_dir / "generated_customer_feedback" / project_id`.
- Never write to public drive in TASK_311.
- Never overwrite a source template.
- Use deterministic business-readable output file names with collision protection.

## Office Gateway Design

Create:

- `backend/infrastructure/office/customer_feedback_workbook_gateway.py`

V1 responsibilities:

- Accept `template_path`, `output_path`, and safe identity data.
- Copy/open the workbook through the existing Office boundary pattern.
- Fill only cells that the implementation can safely identify from the template.
- Save as `.xlsx`.
- Return warnings when optional safe fields cannot be written.

Template-cell mapping:

- During implementation, inspect the real template structure manually or through a safe probe before coding anchors.
- Only write stable anchors that can be tested with a fake gateway/model.
- If no stable anchor can be safely identified for a field, skip it with a warning rather than guessing.

Real Excel smoke:

- Any real Office COM smoke must be manual or timeout-protected.
- Do not run an unbounded Excel COM operation in automated test flow.

## API Design

Create:

- `backend/api/routes_customer_feedback_form_generation.py`

Register in:

- `backend/api/main.py`
- `backend/api/dependencies.py`

Suggested route:

- `POST /api/projects/{project_id}/customer-feedback/generate`

Request:

```python
class CustomerFeedbackFormGenerationRequest(BaseModel):
    operator: str | None = None
```

Response:

```python
class CustomerFeedbackFormGenerationResponse(BaseModel):
    project_id: str
    template_path: str
    output_path: str
    output_file_name: str
    warnings: list[str]
```

HTTP behavior:

- Project not found: `404`
- Missing Template folder: `409`
- Missing `*E-4243*.xlsx`: `409`
- Multiple `*E-4243*.xlsx`: `409`
- Office/gateway failure: actionable `503` or `500` depending on error type

## Safe Field Fill Policy

TASK_311 V1 does not fill Customer Feedback cells because stable Excel anchors have not been verified. The gateway performs safe-copy generation and returns a warning:

- `Customer Feedback workbook was copied; safe cell filling requires Excel COM implementation.`

Future approved tasks may fill only safe project identity fields already available as structured data, such as:

- LTR number
- project id / project number if already present
- requester if already present
- product/sample description if already present
- received date / estimated completion date after TASK_310 if already present

Do not infer missing fields from filenames, public-drive folder names, or unstructured Office documents.

If the Customer Feedback template has fields whose meaning is unclear, leave them blank and return a warning. The generator must prioritize not corrupting the business template.

## Implementation Tasks

### Task 1: Service Tests

Files:

- Create `tests/unit/test_customer_feedback_form_generation_service.py`

Tests:

- Unique `E-4243` `.xlsx` candidate succeeds.
- Missing Template folder resource returns readiness error.
- Template folder path does not exist returns readiness error.
- No matching `.xlsx` returns readiness error.
- Multiple matching `.xlsx` files return ambiguous-template error.
- Generated output does not equal source template path.
- Service does not call ProjectOutputRecord or package services.

### Task 2: Application Service And Discovery

Files:

- Create `backend/application/customer_feedback_form_generation_service.py`

Implementation:

- Define command/result dataclasses.
- Define focused error classes:
  - `CustomerFeedbackGenerationError`
  - `CustomerFeedbackReadinessError`
  - `CustomerFeedbackTemplateAmbiguousError`
- Implement project lookup, Template folder lookup, template discovery, output path selection, gateway call.

### Task 3: Gateway Tests

Files:

- Create `tests/unit/test_customer_feedback_workbook_gateway.py`

Tests:

- Fake/minimal gateway path handling verifies source template is not overwritten.
- `.xlsx` output is required.
- Optional field write warnings are returned when safe anchors are missing.

### Task 4: Office Gateway

Files:

- Create `backend/infrastructure/office/customer_feedback_workbook_gateway.py`

Implementation:

- Keep Office details inside infrastructure.
- Do not expose COM objects outside the gateway.
- Reuse existing gateway error/warning conventions where practical.

### Task 5: API Tests

Files:

- Create `tests/integration/test_customer_feedback_form_generation_api.py`

Tests:

- Success returns output metadata.
- Project not found returns `404`.
- Missing Template folder/missing template/multiple templates return `409`.
- Response includes matched template path.

### Task 6: API Route And Dependency Wiring

Files:

- Create `backend/api/routes_customer_feedback_form_generation.py`
- Modify `backend/api/dependencies.py`
- Modify `backend/api/main.py`

Implementation:

- Add typed request/response DTOs.
- Route body stays thin and calls the application service.
- Map readiness exceptions to `409`.
- Map project missing to `404`.

### Task 7: Static Boundary Tests

Files:

- Modify `tests/unit/test_frontend_shell_files.py` only if a static boundary test is needed.

Assertions:

- No Customer Feedback Workbench button is introduced in TASK_311.
- No package orchestrator import/action is introduced.
- No frontend API client function is required in TASK_311 V1.

### Task 8: Documentation And Board Completion

Files:

- Modify `tasks/TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION.md`
- Modify `docs/task_311_customer_feedback_form_generation_plan.md`
- Modify `docs/task_board.md`

Implementation:

- Mark TASK_311 complete only after tests pass.
- Set next recommended task to TASK_312 and state that it requires separate task file / plan / approval.

## Validation Commands

Run:

```powershell
py -m pytest tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_customer_feedback_workbook_gateway.py -q
```

Run:

```powershell
py -m pytest tests/integration/test_customer_feedback_form_generation_api.py -q
```

Run regression:

```powershell
py -m pytest tests/unit/test_project_section2_sync_service.py tests/integration/test_project_section2_sync_api.py -q
```

Run static check if touched:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "customer_feedback or project_workbench"
```

Run:

```powershell
git diff --check
```

Manual smoke after implementation approval:

- Configure Template folder to a folder containing exactly one `.xlsx` file whose name contains `E-4243`.
- Call the Customer Feedback generation API for a known project.
- Confirm generated file exists.
- Confirm source template file was not modified.
- Confirm no Workbench Customer Feedback button appears.

## Risks And Mitigations

- Risk: multiple template versions exist in the Template folder.
  - Mitigation: block with ambiguous-template error instead of guessing.
- Risk: template field anchors are unclear.
  - Mitigation: write only verified safe fields and return warnings for skipped optional fields.
- Risk: Excel COM can hang.
  - Mitigation: automated tests use fake gateways; real smoke is manual/timeout controlled only.
- Risk: generated file is mistaken for official public-drive package.
  - Mitigation: TASK_311 outputs only to controlled generated/local output and does not publish.

## Stop Point

After TASK_311 implementation and validation, stop. TASK_312 package preview requires a separate task file, executable plan, and explicit approval.
