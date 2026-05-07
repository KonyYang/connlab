# New Project Single-Page Flow Redesign

> Task: `TASK_101_NEW_PROJECT_SINGLE_PAGE_FLOW_REDESIGN`  
> Date: 2026-05-05  
> Scope: UX/data-flow design and implementation split only. No runtime implementation.

## 1. Decision

The operator-facing New Project workflow will move from four frontend steps to one creation workbench:

```text
New Project
  Request email source
  Email attachments
  Editable application information
  LTR number option
  Apply LTR Number and Create Folder
  -> Projects / Project Workbench
```

The backend may remain split across intake, draft review, LTR, and folder services. The redesign changes the operator surface first, not the persistence model.

## 2. Product Scene

A lab coordinator works on a Windows workstation during normal lab administration, starting from one exported request email and checking structured project data before creating the LTR number and folder.

Theme and layout:

- Product register, restrained palette, dense workbench layout.
- Keep the existing app shell with left navigation and top bar.
- Use a single New Project page with two persistent work zones: source/attachments and application/completion.
- Avoid a wizard feeling. The page should show current source, current draft completeness, and the one completion action.

## 3. Page Model

The page-level view model should be explicit and typed:

```text
NewProjectCreationView
  request_package
  attachments[]
  application_draft
  required_field_state
  imported_application_source
  ltr_option
  folder_preview_state
  completion_state
```

This is a frontend/API contract shape, not a new domain object for TASK_101.

### Request Package

Normal New Project creation starts from one imported request email package.

Direct no-email entry is no longer the main UI path for this redesign. If retained later, it should appear as a controlled exception path that creates a durable source package record before the same editor opens.

### Attachments

Attachments are traceability material first.

Rules:

- Attachment rows show filename, type, source role, and application-form eligibility.
- Double-click opens or views the original stored file only.
- Double-click must never import attachment data into the editor.
- Valid application-form attachments show an explicit `Import` action.
- Import stores the source filename shown near the editor.
- If editor data is non-empty or dirty, importing another form requires explicit replacement confirmation.

### Application Editor

The application information editor replaces the current separate Precheck page as the normal project-creation editing surface.

Rules:

- Defaults blank after an email package import.
- Always editable.
- A valid application-form import fills SECTION 1 fields.
- If no valid application form exists, the operator manually fills the same fields.
- Required fields show direct field-level red state when blank.
- Filled required fields clear the red state.
- Do not use a separate warning/blocker panel for normal required-field guidance.
- The primary action remains disabled until required fields are complete, with concise text such as `5 required fields remaining`.
- Backend validation remains authoritative before LTR/folder execution.

### Required Field List

Use the existing SECTION 1 contract from `docs/intake_precheck_field_contract.md`.

Required before completion:

- `form_no`
- `revision`
- `requester`
- `phone`
- `request_date`
- `email`
- `business_unit`
- `manufacturing_site`
- `results_format`
- `requested_completion_date`
- `test_type`
- `sample_status`
- `project_type`
- at least one sample row
- sample `product_name`
- sample `part_number`
- sample `lot_or_traceability`
- sample `material`
- sample `plating`
- sample `housing_material`
- sample `quantity`
- `requested_testing`
- `post_testing_disposition`
- `confidential`
- `subcontract`
- `send_copies_recipients`

Warning-only fields remain editable but must not block completion:

- `project_no`
- `reference_doc`
- sample `revision`
- sample `manufacturing_lot_no`
- sample `lubricant`
- `additional_information`

SECTION 2 lab fields remain out of New Project creation.

## 4. LTR And Folder Completion

One primary action represents the business completion point:

```text
Apply LTR Number and Create Folder
```

The action is enabled only when required application fields are complete.

LTR section:

- `Auto assign next LTR number`
- `Use specified LTR number`
- Specified number enables one input and backend validation for numbering rules and conflicts.

Folder behavior:

- Preserve preview-before-write semantics internally.
- The page may present a simplified confirmation flow, but filesystem writes still require a preview/conflict result from backend services.
- Never overwrite an existing project folder unless a later task implements an explicit conflict strategy.

Success behavior:

- Persist confirmed structured application data.
- Register/commit the LTR number through the approved backend path.
- Create the project folder through the approved folder service.
- Route to Projects or the new Project Workbench for the created project.

## 5. Word Form Generation

Do not generate or update a final Word application form during New Project creation.

During New Project:

- Store confirmed structured application data.
- Preserve the imported request email and attachments.
- Preserve the imported application-form source filename when applicable.

Later Project management may generate or migrate Word application forms in a separate approved task.

## 6. Backend/API Orchestration Plan

Future implementation should add a thin creation orchestration boundary without flattening existing services.

Proposed application service methods:

```text
NewProjectCreationService.load_creation(package_id)
NewProjectCreationService.update_application_draft(package_id, draft_patch)
NewProjectCreationService.import_application_form(package_id, asset_id, replace_confirmed)
NewProjectCreationService.preview_completion(package_id, ltr_option)
NewProjectCreationService.complete(package_id, ltr_option, folder_confirmation)
NewProjectCreationService.cancel_and_remove_draft(package_id)
```

Proposed API DTOs:

```text
NewProjectCreationViewResponse
UpdateNewProjectApplicationDraftRequest
ImportApplicationFormIntoDraftRequest
NewProjectCompletionPreviewRequest
NewProjectCompletionPreviewResponse
CompleteNewProjectRequest
CompleteNewProjectResponse
CancelNewProjectDraftResponse
```

Dependency direction:

```text
frontend page -> features/new-project -> api/client.ts
api routes -> NewProjectCreationService
NewProjectCreationService -> existing intake, draft, LTR, folder services
infrastructure gateways -> Office/filesystem work
```

The orchestrator must coordinate, not absorb, existing business logic.

## 7. Draft And Cancel

Draft behavior should be automatic for the current creation package.

Rules:

- Avoid multiple save buttons.
- Field edits persist as draft data through the page workflow.
- Keep one destructive action: `Cancel and remove draft`.
- Cancel removes ConnLab-owned intake package records, draft records, stored imported files, and temporary package storage.
- Cancel must not touch original Outlook files or arbitrary source paths.
- Until a redesigned main page exists, returning to `Projects` is acceptable.

## 8. Migration Impact

Current surfaces to migrate gradually:

- `IntakeInboxPage` source and attachment components become the left zone of the single New Project page.
- `IntakeCaseReviewPage` field configs, sample editing, requested testing, and lower panels become the application editor zone.
- Precheck issue summary is not used for normal missing required fields on this page.
- Existing backend draft precheck remains authoritative, but UI required guidance is field-level.
- Existing `Save draft and exit` / `Exit without saving` copy should be replaced by automatic draft persistence plus `Cancel and remove draft` when the single-page flow is implemented.

## 9. Implementation Sequence

Do not implement these during TASK_101.

1. `TASK_102_NEW_PROJECT_SINGLE_PAGE_INTAKE_APPLICATION_EDITOR`
   Build the single-page shell, request source/attachments zone, editable application editor, automatic draft persistence, field-level required state, and disabled completion affordance. No LTR/folder execution.

2. `TASK_103_APPLICATION_FORM_IMPORT_TO_EDITOR_NO_SILENT_REPLACE`
   Add explicit import from valid application-form attachments into the editor, source filename display, double-click open/view separation, and replacement confirmation.

3. `TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION`
   Add LTR option selection, backend completion preview, LTR registration, folder creation, success routing, and cancel cleanup within one business completion action.

## 10. Acceptance Checklist

- The four-step frontend model is replaced by one New Project page design.
- Attachment open/view and application-form import are separate actions.
- Import cannot silently replace edited application data.
- Required-field guidance is direct field-level red state.
- Word application-form generation is deferred to Project management.
- LTR/folder completion is one primary business action with preview-before-write preserved internally.
- TASK_099 and TASK_100 remain paused until the single-page creation flow is implemented or explicitly re-planned.
