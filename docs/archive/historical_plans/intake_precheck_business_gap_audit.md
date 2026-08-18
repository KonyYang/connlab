# Intake And Precheck Business Gap Audit

> Task: `TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT`  
> Date: 2026-05-02  
> Scope: audit only, no runtime code changes

## 1. Current Control State

Current phase:

- `Phase 10A - Intake Entry Completion`

Current active task:

- none before this audit; `TASK_077` was explicitly approved by the user for documentation-only analysis

Why this audit is allowed:

- Intake and Precheck are now real business entry screens.
- The user reported concerns about layout, backend behavior, and missing fields.
- `TASK_076` already established frontend architecture rules.
- Auditing gaps before implementation prevents broad unreviewable UI rewrites.

Do not start in this audit:

- copied-workbook LTR write hardening
- Outlook inbox auto-scan
- email sending
- Matrix, Report, AI review, LAN deployment, permissions, or future-scope work

## 2. Real Flow Observed In Code

Primary `.msg` flow:

```text
IntakeInboxPage
  -> importMsgPackage(file)
  -> backend stores IntakePackage + IntakeAsset records
  -> operator selects one Word attachment
  -> selectIntakeApplicationForm(package_id, asset_id)
  -> backend parses selected .docx into IntakeDraft.parsed_fields_json
  -> IntakeCaseReviewPage loads getIntakeCaseReview(package_id)
  -> operator may patch review fields
  -> confirmIntakeCase(case_id)
  -> backend creates Project + ApplicationForm + SampleInfo + FileAsset records
```

Secondary direct Word/manual paths:

- Direct Word upload is visible in the Intake UI, but currently not wired to a no-project backend import path.
- `createManualIntake()` exists in the API client and backend, but it is not wired into the current Intake page.
- Legacy project-scoped `uploadApplicationForm(project_id, file)` still exists for an already-created project workbench, but it is not the same as New Project intake.

## 3. Architecture Assessment

The system is still controllable:

- Frontend API calls are centralized in `frontend/src/api/client.ts`.
- UI does not directly touch Office, SQLite, external workbooks, or project folders.
- Selected Word binding now has an explicit backend API.
- Parser output, draft overrides, confirmation, and persisted project records have separate backend services.

The main risk is concentrated in two large route pages:

- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/pages/IntakeCaseReviewPage.tsx`

These pages currently mix:

- route-level state
- workflow state
- field definitions
- business copy
- temporary controls
- formatting helpers
- large nested JSX
- API orchestration

This violates the target rule from `docs/frontend_architecture_rules.md`: pages should compose feature components and feature hooks, not keep accumulating fields and workflow logic.

## 4. High-Priority Findings

### F1. Precheck UI Required Fields Do Not Match Backend Confirmation Rules

Current frontend:

- `PROJECT_FIELDS` marks many fields as required in `IntakeCaseReviewPage.tsx`, including phone, date, email, business unit, manufacturing site, project number, results format, requested completion date, test type, sample status, and project type.

Current backend confirmation:

- `IntakeCaseReviewService._required_fields = ("product_name", "requester")`
- `IntakeConfirmationService._required_project_fields = ("product_name", "requester")`

Impact:

- The UI visually implies stricter confirmation requirements than the backend enforces.
- Operators may think fields are blocking when they are only review fields.
- Later LTR readiness may need many of these fields, but the project can already be created without them.

Recommended fix:

- Define a shared review field policy for `required_for_project_confirmation`, `required_for_precheck_quality`, and `required_for_ltr_readiness`.
- Expose these states through the case review response or a dedicated frontend config aligned to backend policy.

### F2. Precheck UI Contains Reference/Mock Business Content In Real Data Areas

Current frontend examples:

- fallback Form No. uses `E-7818`
- template warning shows `E_3778_Rev-H`
- requested testing table includes fixed rows such as `DG-00-048_Rev2`
- recipients are hard-coded: `Andy Liu`, `Jane Smith`, `Quality Team`, `HYP Cao`

Impact:

- Operators may trust reference values as real extracted data.
- The screen mixes sample content with parsed `.docx` data.
- This directly conflicts with `docs/frontend_architecture_rules.md` copy/mock rules.

Recommended fix:

- Remove or clearly disable reference-only content.
- Render `send_copies_recipients` from parsed draft fields when available.
- Do not show fixed recipient chips or fixed test rows as editable real data until backend supports them.

### F3. Several Visible Controls Are Not Wired To Backend Behavior

Current frontend examples:

- direct Word upload button sets an error saying it is not wired
- sample row `Edit`, `Copy`, `Delete` buttons have no persistence path
- requested testing `+ Add Row` has no persistence path
- template update button is disabled and has no backend operation
- attachment details `Download` is disabled

Impact:

- The UI looks more complete than the workflow actually is.
- Operators may try to use controls that cannot persist changes.
- Future fixes may be tempted to add local-only state without backend contract.

Recommended fix:

- Either remove inactive controls or render them as clearly unavailable with the reason.
- For real controls, add backend contract first, then wire UI through feature hooks.

### F4. Direct Word And Manual Intake Entry Are Conceptually Mixed

Current state:

- `IntakeInboxPage` shows `Upload application form` and accepts `.doc,.docx`.
- The handler only stores the filename in app session and shows an error.
- Backend supports no-email manual JSON intake, not direct Word intake through that button.
- Project-scoped Word upload exists separately in the workbench.

Impact:

- The operator sees a direct Word path but cannot complete it.
- The business distinction between exported `.msg`, direct `.docx`, and manual no-email entry is unclear.

Recommended fix:

- Decide whether New Project supports direct `.docx` as a first-class no-email path.
- If yes, add a direct Word intake API that creates package, asset, selected case, and draft before project creation.
- If no, remove or relabel the button until the task is explicitly implemented.

### F5. Lab Test Request Number Blocker Is Display-Only

Current backend parser:

- extracts `lab_test_request_number`

Current frontend:

- always shows a blocker banner saying Lab Test Request Number must be blank
- does not appear to check the parsed value before showing the banner
- no backend confirmation blocker currently enforces this condition in case confirmation

Impact:

- The banner may be shown even when the source document is clean.
- A non-blank value may not actually block confirmation.

Recommended fix:

- Make `lab_test_request_number` an explicit review field and backend-derived blocker.
- Render the blocker only when a value is present.

### F6. Parser Extracts More Fields Than Confirmation Persists Meaningfully

Parser and selected-form draft include:

- form metadata
- reference document
- lab test request number
- requestor section
- project/test metadata
- disposition/confidential/subcontract
- additional information
- send-copies recipients
- sample rows

Confirmation persists only a subset into `Project`, `ApplicationForm`, `SampleInfo`, and `FileAsset`.

Known gaps:

- `request_date` is not converted into `ApplicationForm.request_date` in confirmation.
- lab section fields from selected-form draft are not currently included in `_draft_payload`.
- `send_copies_recipients` is parsed into draft but not persisted into `ApplicationForm` by confirmation.
- sample rows do not include manufacturing lot or lubricant even though the UI shows those columns.

Impact:

- Data can appear in Precheck review but be lost when confirming into project records.
- LTR readiness and later lookup may miss values the operator thought were confirmed.

Recommended fix:

- Create a field lifecycle map from parser key to review field to confirmation persistence target to LTR readiness source.

### F7. Precheck Page Is Not Running The Deterministic Precheck Engine

Current Precheck step in New Project:

- case review page validates missing draft fields for confirmation
- it does not run `PrecheckEngine`
- deterministic precheck still exists in the older project workbench flow after project creation

Impact:

- The label "Precheck" currently means human review/confirmation, not the deterministic precheck engine.
- Operators may assume deterministic rule checks have run before project creation.

Recommended fix:

- Decide whether New Project Precheck should run deterministic checks before project confirmation.
- If yes, add a draft-level precheck service that can run on selected-form draft data before creating a Project.
- If no, rename the step to "Review & Confirm" or explicitly show deterministic precheck as a later project-scoped step.

## 5. Field Gap Matrix

| Field / Section | Parser | Draft Review API | Frontend Display | Confirmation Persistence | Gap |
|---|---:|---:|---:|---:|---|
| form_no / revision | yes | yes | yes | yes, with fallback | UI fallback uses wrong-looking reference values |
| reference_doc | yes | yes | yes | no direct confirmation persistence | visible but may be lost |
| lab_test_request_number | yes | draft only | banner only | no blocker | should drive real blocker |
| requester | yes | required | required | Project.requestor + ApplicationForm.requester | aligned |
| phone | yes | optional | marked required | ApplicationForm.phone not persisted by confirmation | policy mismatch |
| request_date | yes | optional | marked required | not parsed to date in confirmation | data loss |
| email | yes | optional | marked required | ApplicationForm.email | policy mismatch |
| business_unit | yes | optional | marked required | Project + ApplicationForm | policy mismatch |
| manufacturing_site | yes | optional | marked required | not persisted by confirmation | data loss |
| project_no | yes | optional | marked required | Project.project_no + ApplicationForm.project_number | UI required conflicts with DL-centric optionality |
| results_format | yes | optional | marked required | not persisted by confirmation | data loss |
| requested_completion_date | yes | optional | marked required | not persisted by confirmation | data loss |
| test_type | yes | optional | marked required | not persisted by confirmation | data loss |
| sample_status | yes | optional | marked required | not persisted by confirmation | data loss |
| project_type | yes | optional | marked required | not persisted by confirmation | data loss |
| post_testing_disposition | yes | optional | read-only select | not persisted by confirmation | data loss |
| requested_testing | yes | optional | partly real, partly fixed rows | ApplicationForm.requested_testing | fixed row confusion |
| confidential | yes | optional | read-only radio | not persisted by confirmation | data loss |
| subcontract | yes | optional | read-only radio | not persisted by confirmation as text/bool | data loss |
| additional_information | yes | optional | read-only textarea | not persisted by confirmation | data loss |
| send_copies_recipients | yes | not returned as explicit field | fixed chips | not persisted by confirmation | mock content and data loss |
| sample product / part / revision / lot / material / plating / housing / quantity | yes | yes | yes | mostly yes | manufacturing lot and lubricant are UI-only columns |
| lab / assigned personnel / received date / estimated completion / sample condition | parser supports | not in selected-form draft | not shown in case review | not persisted by confirmation | missing from New Project flow |

## 6. Recommended Task Sequence

Do not implement all fixes in one task. Use this sequence:

1. `TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_DATA_LIFECYCLE`
   - Define the authoritative field lifecycle map.
   - Classify each field as confirmation-required, precheck-warning, LTR-readiness, persisted, display-only, or future.
   - Decide direct `.docx` and manual intake behavior.

2. `TASK_079_PRECHECK_DRAFT_REVIEW_CONTRACT_ALIGNMENT`
   - Align backend review response with field policy.
   - Add explicit blocker/warning states for Lab Test Request Number and missing business fields.
   - Preserve/persist fields that operators confirm.

3. `TASK_080_INTAKE_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION`
   - Extract `features/intake` and `features/precheck`.
   - Move field configs, selectors, and feature hooks out of route pages.
   - Keep behavior stable.

4. `TASK_081_INTAKE_ENTRY_PATH_COMPLETION`
   - Either implement direct `.docx` as a no-email package path or remove the visible button.
   - Clarify `.msg`, `.docx`, and manual-entry entry modes.

5. `TASK_082_PRECHECK_REVIEW_UI_COMPLETION`
   - Remove mock/reference content.
   - Wire real recipient/requested-testing/sample controls only where backend supports persistence.
   - Improve blocker, warning, save, and confirm feedback.

6. `TASK_083_DRAFT_LEVEL_DETERMINISTIC_PRECHECK_DECISION`
   - Decide and implement whether deterministic precheck runs before project confirmation or remains project-scoped after confirmation.

## 7. Information Needed From User

I can proceed with `TASK_078` from code alone, but these inputs would make the implementation safer:

1. A current real or sanitized E-3718 Rev H application form with representative filled fields.
2. A marked-up screenshot or note saying which Precheck fields are truly required before project creation.
3. Clarification on direct `.docx` intake: should a no-email Word file create the same package/case/draft flow as `.msg`?
4. The real allowed values for dropdowns:
   - Business Unit
   - Manufacturing Site
   - Results Format
   - Test Type
   - Test Sample Status
   - Project Type
   - Post-Testing Sample Disposition
5. Whether `Send copies of test results/reports to` should be persisted now, and where it should appear later.
6. Whether sample row edit/copy/delete is required in MVP, or should remain read-only until a later task.
7. Whether Lab Test Request Number being non-blank must hard-block project confirmation.
8. Whether New Project Precheck should run deterministic rules before confirmation, or only review extracted fields.

## 8. Acceptance Criteria For The Next Implementation Phase

Before broad UI completion starts, the next task should produce:

- one authoritative Intake/Precheck field map
- one backend-aligned required/warning/blocker policy
- one decision on direct `.docx` intake
- one decision on draft-level deterministic precheck
- no UI mock content in real data sections
- no route page growth without feature extraction

