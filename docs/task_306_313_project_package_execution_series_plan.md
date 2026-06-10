# TASK_306-TASK_313 Project Package Execution Series Plan

## Status

Controlled series registered. TASK_306, TASK_307, TASK_308, TASK_309, and TASK_310 are complete. TASK_311 requires a task file, executable plan, and explicit approval before implementation.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current board context: TASK_306, TASK_307, TASK_308, TASK_309, and TASK_310 are complete. TASK_311 is the next planned follow-up and must start with task definition and executable planning.

## Goal

Move ConnLab from separate Matrix / Test Record / Fee Evaluation / Folder capabilities toward a controlled project package preparation chain:

```text
Project Workbench folder entry
  -> Matrix Editor Test Record draft preview entry
  -> Confirm Fee authority
  -> Fee stale guard
  -> Section 2 sync
  -> Customer Feedback form generation
  -> package preview
  -> package execute
```

The series keeps Project as the lifecycle container, Matrix as the execution authority map, and generated Word/Excel files as derived delivery artifacts.

## Transition Authority Principle

ConnLab is currently in a transition stage from manual public-drive project-file management toward structured project-package support.

The existing public-drive project folder remains the business authority for the officially reviewed and permanently retained project package. ConnLab must support this workflow instead of silently replacing it with a local-database-only or app-only package model.

V1 package work must distinguish three surfaces:

- Official public-drive package: the reviewed folder that follows current lab file-placement rules and remains the permanent business record.
- Local ConnLab workspace: working files, temporary drafts, raw preparation material, structured cache data, and generated candidates used before formal publication.
- Package preview/execute flow: an explicit operator-controlled bridge from confirmed ConnLab data and generated artifacts into the official public-drive folder.

The package chain must preserve manual review expectations:

- No hidden publishing side effects from Confirm Matrix, Confirm Fee, folder creation, or draft generation.
- No automatic promotion of local working files into the official package without preview and operator confirmation.
- Temporary Office lock files, scratch copies, and intermediate preparation files are working material, not official package deliverables.
- SQLite remains a structured workstation cache and automation aid during this phase; it does not supersede the public-drive package authority.

The observed formal sample package under `C:\Users\White\Desktop\AI information\Projects\DL-2025-11-073\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test` should be treated as a business-authority reference sample for placement categories such as `Submitted Material`, `Test results`, `Photos`, `E-mail`, and top-level formal outputs.

## Series Tasks

### TASK_306_PROJECT_FOLDER_PANEL_WORKBENCH_ENTRY

Complete.

Expose the existing `ProjectFolderCreationPanel` in Project Workbench so operators can preview and generate the project folder from the Workbench without navigating elsewhere.

V1 is frontend wiring only. It does not create a package orchestrator and does not generate Test Record, Fee Form, Customer Feedback Form, or evidence placement.

### TASK_307_MATRIX_EDITOR_TEST_RECORD_DRAFT_PREVIEW_ENTRY

Complete.

Add a `Test record` action to Matrix Editor so operators can download and inspect a Test Record draft generated from the current Matrix Editor page state at click time, including unconfirmed visible edits. V1 captures this by sending a bounded current UI state payload, similar to Fee Evaluation `Fee Form`, without forcing a Matrix draft save first.

Important boundary: this is an immediate draft preview/download for operator review before Confirm Matrix. It must not require selecting historical draft versions, export all revisions, register a current project output, save the Matrix draft as a side effect, create a Confirmed Matrix authority snapshot, publish to the project folder, or move anything into the official public-drive package. The downloaded file must be visibly marked as Preview / Unconfirmed Matrix draft. The Workbench Test Record remains the active Confirmed Matrix authority version for later package preview/execute tasks.

### TASK_308_CONFIRMED_FEE_VERSION_FOUNDATION

Complete.

Added a Confirm Fee backend foundation that snapshots the current saved Fee Evaluation pricing draft, active Confirmed Matrix id/revision, active fee rule version, and current totals into a versioned confirmed fee authority record.

### TASK_309_FEE_CONFIRM_UI_AND_STALE_GUARD

Complete.

Added the operator-facing Confirm Fee action and confirmed/stale/local-unconfirmed status in Fee Evaluation. Confirm Fee saves the current visible pricing draft first, requires the returned saved pricing draft id, then creates a Confirmed Fee authority version from full `All Group` totals. The page shows unconfirmed saved changes when the latest saved pricing draft id differs from the latest Confirmed Fee pricing draft id, and local edits after confirmation also mark the page unconfirmed.

### TASK_310_PROJECT_SECTION2_SYNC_FROM_CONFIRMED_MATRIX

Complete.

Added an explicit sync operation that copies Confirmed Matrix schedule fields into Application Form Section 2 fields:

- `sample_received_date` -> `received_date`
- `estimated_completion_date` -> `estimated_completion_date`

This is not an implicit side effect of Confirm Matrix.

V1 scope is structured-data sync only. It updates Application Form Section 2 date fields in SQLite from active Confirmed Matrix authority values. It does not write the Word application form, register a ProjectOutputRecord, generate Customer Feedback, publish to public drive, or start package orchestration. It blocks ambiguous multiple Application Form targets and requires POST sync to match the previewed Confirmed Matrix id/revision.

### TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION

Planned follow-up.

Add a controlled Customer Feedback Form generator from `E-4243_D Customer Feedback Form.xlsx`, copying the template and filling safe project identity fields.

This task owns the form generator only. It does not orchestrate the full project package.

### TASK_312_PROJECT_PACKAGE_ORCHESTRATOR_PREVIEW

Planned follow-up.

Add a read-only package preview that lists required inputs, generated outputs, evidence placement candidates, target folder paths, blockers, and conflicts before any file operation.

### TASK_313_PROJECT_PACKAGE_ORCHESTRATOR_EXECUTE

Planned follow-up.

Execute the approved package plan by reusing existing application services and gateways:

- project folder generation or verified existing folder
- confirmed-Matrix Test Record generation
- confirmed Fee Form export
- Customer Feedback Form generation
- evidence placement

The orchestrator must call application services directly, not call backend HTTP routes from backend code.

## Cross-Series Boundaries

- Do not make Confirm Matrix generate downstream files as hidden side effects.
- Do not make FolderService call Fee Export, Test Record generation, or evidence placement internally.
- Do not implement StepInstance, TestResult, image upload, AI review, permissions, LAN deployment, or multi-user behavior.
- Do not implement Matrix/Fee automatic default filling in this series.
- Do not add a generic tools page.
- Do not overwrite templates or existing project output files without existing preview/conflict guards.
- Office operations must remain behind existing infrastructure gateways and timeout boundaries where applicable.

## Current Assumptions

- `ProjectFolderCreationPanel` already exists and can be reused for TASK_306.
- `TestRecordDraftGenerationButton` already exists but is confirmed-Matrix based.
- Fee Evaluation edit/export/persistence is complete through TASK_305.
- Customer Feedback Form generation is future scope until TASK_311.
- Clarizen tracking and lab execution are intentionally deferred until the project package chain is stable.
