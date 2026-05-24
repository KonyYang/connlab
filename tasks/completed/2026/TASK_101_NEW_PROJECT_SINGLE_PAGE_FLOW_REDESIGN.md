# TASK_101_NEW_PROJECT_SINGLE_PAGE_FLOW_REDESIGN

## Status

done

## Current Phase

Phase 10A follow-up redirection. This task supersedes the immediate execution of `TASK_099` and `TASK_100` until the New Project flow is redesigned around one page.

## Active Task Rule

Do not implement this task until `docs/task_board.md` explicitly marks `TASK_101_NEW_PROJECT_SINGLE_PAGE_FLOW_REDESIGN` as the current active task or a ready task approved by the user.

When active, this task is allowed because it stays inside MVP project creation:

- Project stage: New Project before Project management.
- Input: request email, attachments, application-form data, draft data, LTR option, folder creation intent.
- Output: an approved single-page flow design and implementation task split.
- Domain impact: intake package/case/draft, LTR registration, and folder creation orchestration only.
- MVP scope: intake, application-form confirmation, LTR registration, and project folder creation.

## User Decision Baseline

The user approved replacing the current four-step New Project frontend with a simpler single-page creation workbench.

Reason:

- A real project request normally starts from one email request package.
- Intake and Precheck are currently split across pages even though they are one operator job: confirm application information from request material.
- Creating/registering the LTR number and creating the project folder are the business completion point for New Project.
- Once an LTR number exists and the project folder is created, the project should move to `Projects` for ongoing management.

## Product Model

Target model:

```text
New Project page
  Request source + attachments
  Confirmed application information editor
  LTR number option
  Apply LTR Number and Create Folder
  -> Projects / Project Workbench
```

This replaces the frontend idea of:

```text
Intake -> Precheck -> LTR -> Folder
```

The backend may still keep separate services and persistence boundaries. The simplification is primarily the operator-facing workflow and orchestration.

## Required UX Rules

### Request Source

- Import source is simplified to request email import.
- Creating a project normally requires at least one email request package.
- Rare no-email cases may be handled later by creating/importing a title email or similar source package, but this task should define the rule before implementation.

### Attachments

- Attachments are displayed as email attachments.
- Double-clicking an attachment opens or views the original file.
- Double-clicking must not import data into the application information editor.
- If an attachment is recognized as a valid application form, show an explicit `Import` button on that attachment row or detail area.
- Only clicking `Import` may populate the application information editor.
- If the editor already contains user-entered or modified data, importing another application form must require confirmation before replacing current application information.
- The UI should show the current imported application-form source filename when data was imported.

### Application Information Editor

- The right-side detail/preview area should be replaced by or merged into the main application information editor.
- The editor defaults blank and is always editable.
- If a valid application form is imported, parsed SECTION 1 data fills the editor.
- If no application form exists in the email, the operator can manually fill the same fields.
- Manual fill must still be saved as structured draft data and later be able to generate an application form.
- Required fields display a red required state directly on the field when blank.
- Filled required fields clear the red state.
- Do not use a separate warnings/blockers panel for normal required-field guidance.
- The primary action remains disabled until required fields are complete, with concise text such as `5 required fields remaining`.
- Backend remains authoritative and must still validate required data before LTR/folder execution.

### Word Application Form Generation

- Do not generate or update the final Word application form during New Project creation unless a later task explicitly approves it.
- During New Project, store confirmed structured application data.
- Word application-form generation, template version migration, and SECTION 2 completion are more appropriate in Project management under a later `Start project` or project documentation workflow.
- This avoids losing information when transferring data between old and new Word template revisions.

### LTR Number And Folder Creation

- One primary creation action should represent the business completion point: apply/register LTR number and create the project folder.
- The action requires all required application fields to be complete.
- LTR number option should be one compact section:
  - `Auto assign next LTR number`
  - `Use specified LTR number`
- The specified-number option enables an input for user-created/associated/suffix-specific numbers.
- Backend must check numbering rule and conflicts.
- Folder creation still needs preview/confirmation semantics because it writes to the filesystem.
- The UI may present this as one simplified action, but implementation should preserve preview-before-write internally.

### Exit / Draft

- Draft behavior should be automatic for the current page case.
- Avoid exposing multiple save buttons.
- Keep a single destructive exit action such as `Cancel and remove draft`.
- Cancel removes all ConnLab-owned temporary records/files and returns to the main page.
- Until a new main page exists, returning to `Projects` is acceptable.

## Required Architecture Rules

- Frontend must not directly inspect Word files, Outlook files, SQLite, or folders.
- API routes remain thin and call application services.
- Application service orchestration may coordinate existing intake, LTR, and folder services, but should not become a god service.
- Existing backend services may stay split; the page-level flow can be unified without flattening backend boundaries.
- Continue to use typed API DTOs.
- Do not introduce a new frontend state library.

## Out Of Scope

- Do not implement the single-page UI in this design task unless this task is explicitly expanded to implementation.
- Do not implement Matrix, Report Generation, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or email sending.
- Do not implement full Project Workbench redesign here.
- Do not implement final Word application-form generation/migration here.
- Do not implement LTR registered freeze/exception until the single-page creation decision is reconciled.

## Deliverables

When implemented as a planning task, produce:

- Single-page New Project UX/data-flow design.
- Backend/API orchestration plan.
- Required field list and validation behavior.
- Attachment open/import behavior.
- Draft/cancel behavior.
- LTR option and folder creation execution model.
- Migration impact on existing Intake/Precheck components.
- Follow-up implementation task sequence.

Delivered in `docs/archive/historical_plans/new_project_single_page_flow_redesign.md`.

Follow-up task files refined by this task:

- `TASK_102_NEW_PROJECT_SINGLE_PAGE_INTAKE_APPLICATION_EDITOR`
- `TASK_103_APPLICATION_FORM_IMPORT_TO_EDITOR_NO_SILENT_REPLACE`
- `TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION`

## Acceptance Criteria

- The design clearly replaces the four-step frontend with one New Project page.
- Attachment open and application-form import are separate actions.
- Import never silently replaces edited application data.
- Required-field guidance is field-level red state, not a warning/blocker panel.
- Word application-form generation is deferred to Project management unless explicitly re-approved.
- LTR/folder completion routes the user into Projects/Project Workbench after success.
- `TASK_099` and `TASK_100` are not implemented before this redesign is resolved.

## Validation

Add or update documentation tests if the project uses static doc guards for task plans.

Recommended validation for planning-only implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

If implementation tasks are created in the same turn, add task-document tests for the new plan.

## Stop Rule

After completing this task, update `docs/task_board.md`, record validation, and stop. Do not start implementation tasks automatically.
