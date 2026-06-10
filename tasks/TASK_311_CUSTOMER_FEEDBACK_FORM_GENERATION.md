# TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_311 implementation is complete. TASK_312 requires a separate task file, executable plan, and explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The work is a bounded backend/API foundation task that creates a controlled Customer Feedback Form generator using existing project data, configured template-folder resources, and Office gateway patterns. It requires careful scope control around public-drive publishing, package orchestration, and Office automation, but it does not require new Matrix rules, frontend UI, StepInstance execution persistence, AI review, permissions, LAN deployment, or multi-user behavior.

## Goal

Add a controlled backend Customer Feedback Form generation foundation that can locate the existing Customer Feedback workbook template from the configured Template folder, copy it to a controlled local generated-output location, and return generated file metadata for later package flow.

This task prepares the Customer Feedback artifact needed by the project package chain. It does not orchestrate a full project package.

## Current Code Reality

- Settings already expose a `Template folder` resource through `project_folder_template`.
- Operators currently place business templates in that folder, for example `D:\Source\Template`.
- The Customer Feedback template is identified by business form number `E-4243` and is an `.xlsx` workbook.
- The project already has backend services and Office gateway boundaries for generated Word/Excel artifacts.
- `pyproject.toml` does not include an `.xlsx` writer dependency such as `openpyxl`; workbook writes must not introduce a new dependency without an explicit task.
- Existing Excel COM work has timeout/smoke constraints; real Office automation must stay behind infrastructure gateways and controlled validation.

## V1 User Contract

When Customer Feedback generation is requested:

1. ConnLab reads the configured Template folder path.
2. ConnLab locates exactly one Customer Feedback template in that folder:
   - file name contains `E-4243`
   - suffix is `.xlsx`
3. If no matching template exists, ConnLab returns an actionable readiness blocker.
4. If multiple matching templates exist, ConnLab returns an ambiguous-template blocker and does not guess which version is latest.
5. ConnLab copies the matched template into a controlled generated-output location.
6. ConnLab V1 performs a safe template copy and returns an explicit warning that verified Excel cell filling is deferred.
7. ConnLab returns generated file metadata and warnings.

The operation is explicit. It must not happen automatically when Matrix is confirmed, Fee is confirmed, Section 2 dates are synced, or a project folder is generated.

## In Scope

- Backend template discovery from the configured Template folder.
- Backend application service for Customer Feedback generation.
- Thin API route for Customer Feedback generation.
- Infrastructure gateway/facade for copying/writing the `.xlsx` workbook.
- Safe-copy workbook generation with explicit warning when verified field filling is deferred.
- Focused backend and API tests.
- Static boundary tests if needed.
- Update `docs/task_board.md` after implementation.

## Out Of Scope

- No Workbench button or frontend UI in TASK_311.
- No package preview or package execute.
- No public-drive publish or official package placement.
- No `ProjectOutputRecord` registration unless a later approved task adds it.
- No changes to Confirm Matrix, Confirm Fee, Section 2 sync, Test Record generation, Fee Form generation, or folder generation behavior.
- No Customer Feedback generation as a hidden side effect of another action.
- No new settings resource type unless the executable plan proves the existing Template folder cannot safely support this task.
- No new workbook-writer dependency.
- No StepInstance, execution persistence, evidence placement, report generation, AI review, permissions, multi-user, LAN deployment, or server authority migration.

## Template Discovery Contract

Source folder:

- Use the configured `project_folder_template` resource, shown to users as `Template folder`.
- Treat `D:\Source\Template` only as a current business example, not as a production hardcoded path.

Candidate file rule:

- Match files directly under the configured Template folder whose file name contains `E-4243` and whose suffix is exactly `.xlsx` case-insensitively.
- V1 does not accept `.xls`, `.xlsm`, `.csv`, or non-Excel files.
- V1 does not recursively search nested folders unless the executable plan explicitly chooses and tests that behavior.

Conflict handling:

- Zero candidates: readiness blocker.
- More than one candidate: ambiguous-template blocker.
- Do not infer latest by revision letter, modified time, filename order, or directory order in TASK_311.

## Data Source Contract

Allowed source data:

- Project identity.
- Latest/current LTR identity where already available through existing repositories/services.
- Current structured Application Form data when unambiguous.
- Structured Section 2 fields that already exist after TASK_310.

Disallowed source data:

- Unconfirmed Matrix Editor state.
- Local Office files as primary data sources, other than the Customer Feedback template itself.
- Hidden reads from public-drive package folders.
- Any data requiring StepInstance, TestResult, evidence, report, or package execution scope.

If required source data is missing or ambiguous, return a readiness blocker rather than guessing.

## API Requirements

- Add a backend endpoint under the project scope for Customer Feedback generation.
- The request must not require a template path in V1.
- The service must discover the template from the configured Template folder.
- The response must include generated path, output file name, selected template path, and warnings.
- Project not found should return `404`.
- Readiness blockers such as missing Template folder, missing template, ambiguous template, or missing project context should return `409`.

## Acceptance Criteria

- A unique `*E-4243*.xlsx` template in the configured Template folder is discovered and used.
- Missing Template folder returns an actionable blocker.
- Missing matching template returns an actionable blocker.
- Multiple matching templates return an ambiguous-template blocker.
- Generated output is a copy of the template, not a mutation of the source template.
- V1 performs safe-copy generation only; Customer Feedback cell filling is deferred until stable template anchors are verified in a later approved task.
- No public-drive placement occurs.
- No `ProjectOutputRecord` is registered.
- No Workbench UI or frontend action appears.
- No package preview/execute behavior appears.
- No Confirm Matrix, Confirm Fee, Section 2 sync, Test Record, Fee Form, or folder generation side effect is introduced.

## Required Validation

The executable plan must define exact commands. Expected coverage includes:

- Unit tests for template discovery success, missing Template folder, missing template, multiple templates, and generated output metadata.
- Unit tests or gateway tests proving the source template is not overwritten.
- API tests for success, `404` project missing, and `409` readiness blockers.
- Regression checks for existing TASK_306-TASK_310 behavior.
- `git diff --check`.

## Stop Point

After TASK_311 implementation and validation, stop. Do not proceed to TASK_312 without a separate task file / executable plan review and explicit approval.
