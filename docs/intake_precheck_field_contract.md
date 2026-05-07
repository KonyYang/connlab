# Intake And Precheck Field Contract

> Task: `TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES`  
> Date: 2026-05-03  
> Scope: field contract and policy only, no runtime code changes

## 1. Purpose

This document defines the field contract for the real-business New Project Intake and Precheck flow. It is the authority for later parser, backend API, draft editing, precheck, and frontend UI tasks.

The contract is based on:

- `AGENTS.md`
- `docs/frontend_architecture_rules.md`
- `docs/intake_precheck_business_gap_audit.md`
- user-provided business rules on 2026-05-03
- read-only parser probe of `local/office files samples/E-3718_H Laboratory Test Request-Even.docx`

The sample Word file is local validation material only. Do not commit it into the repository unless the user explicitly approves it.

## 2. Project Creation Boundary

New Project creation is allowed only after the operator reviews and confirms `SECTION 1 TO BE COMPLETED BY THE REQUESTOR`.

`SECTION 2 TO BE COMPLETED BY THE TESTING LABORATORY` is not part of project creation precheck. It must not block New Project confirmation.

Project creation input sources:

- exported `.msg` request package
- direct `.docx` application form without email

Both sources must enter the same durable backend workflow:

```text
IntakePackage
  -> IntakeAsset
  -> IntakeCase
  -> IntakeDraft
  -> draft-level SECTION 1 precheck
  -> operator confirmation
  -> Project + ApplicationForm + SampleInfo + FileAsset
```

The frontend session is not the source of truth. The backend package/case/draft records are the recovery point for page navigation, refresh, and later workflow expansion.

Current New Project Intake uses one active Precheck review case before Project confirmation:

- Continuing to Precheck with the same selected application form reopens the same case and preserves saved draft corrections.
- Selecting a different application form before Project confirmation rebinds the reusable unconfirmed case to the new form and clears manual overrides.
- Importing a new email package or direct `.docx` source starts a clean Intake session.
- The Precheck page must not expose a multi-case switcher for the current New Project workflow.

TASK_098 update:

- Intake is source selection only. It imports or uploads request material, validates the selected application-form source, and creates the active Precheck case.
- Precheck is the confirmed application-data editing surface. Project creation uses corrected Precheck draft values, not the raw Word file values.
- After entering Precheck, normal workflow does not support switching to another application form. The operator should use `Save draft and exit` or `Exit without saving`; form replacement is not part of the MVP flow.
- The source `.msg` or `.docx` remains visible as traceability context, but it is not presented as the final submitted application record.

## 3. Field States

Use these field states in backend DTOs, frontend selectors, and UI copy.

| State | Meaning | Project confirmation behavior |
|---|---|---|
| `required_before_project` | Must be present before Project creation | error, blocks confirmation |
| `warning_before_project` | Should be reviewed before Project creation | warning, does not block confirmation |
| `auto_clear_with_warning` | Parsed source value is not allowed and should be cleared from the draft | warning after clear, does not block if clear succeeds |
| `editable_draft` | Operator may correct the draft value | save to draft before confirmation |
| `readonly_source` | Display source context only | not editable |
| `required_before_ltr` | May be missing at Project confirmation but must be resolved before LTR registration | warning before Project, later LTR blocker |
| `section2_excluded` | Belongs to lab section, not requestor section | excluded from pre-project precheck |

## 4. SECTION 1 Field Contract

### 4.1 Source Metadata

| Key | Label | State | Notes |
|---|---|---|---|
| `source_package_name` | Source package | `readonly_source` | `.msg` source filename or direct `.docx` source filename |
| `source_type` | Source type | `readonly_source` | `msg_import` or direct `.docx` intake |
| `selected_form_asset_id` | Selected application form | `readonly_source` | internal identity, not user-facing copy |
| `selected_form_name` | Selected application form | `readonly_source` | user-facing filename |

### 4.2 Template And LTR Header

| Key | Label | State | Notes |
|---|---|---|---|
| `form_no` | Form No. | `required_before_project` | expected `E-3718`; mismatch is an error |
| `revision` | Revision | `required_before_project` | expected `H`; mismatch is an error |
| `reference_doc` | Reference Doc. | `warning_before_project` | display when parsed; do not fabricate fallback values |
| `lab_test_request_number` | Lab Test Request Number | `auto_clear_with_warning` | source form must be blank before confirmation |

`lab_test_request_number` policy:

- If blank, no issue.
- If non-blank, backend should preserve an audit warning and clear the draft value before confirmation.
- UI should tell the operator that the request form had a pre-filled Lab Test Request Number and the draft was cleared.
- This should not require a modal. Use an inline warning near the source/template check and in the issue summary.

### 4.3 Requestor And Project Intake Fields

All requestor-side fields in SECTION 1 need confirmation before creating the Project, except `Project #`, which is warning-only because ConnLab is DL/LTR-centric after registration.

| Key | Label | State | Persist target |
|---|---|---|---|
| `requester` | Requested By | `required_before_project` | `Project.requestor`, `ApplicationForm.requester` |
| `phone` | Phone # | `required_before_project` | `ApplicationForm.phone` |
| `request_date` | Date | `required_before_project` | `ApplicationForm.request_date` |
| `email` | Email | `required_before_project` | `ApplicationForm.email` |
| `business_unit` | Business Unit | `required_before_project` | `Project.business_unit`, `ApplicationForm.business_unit` |
| `manufacturing_site` | Mfg. Site | `required_before_project` | `ApplicationForm.manufacturing_site` |
| `project_no` | Project # | `warning_before_project` | `Project.project_no`, `ApplicationForm.project_number` |
| `results_format` | Results Format | `required_before_project` | `ApplicationForm.results_format` |
| `requested_completion_date` | Requested Testing Completion Date | `required_before_project` | `ApplicationForm.requested_completion_date` |
| `test_type` | Test Type | `required_before_project` | `ApplicationForm.test_type` |
| `sample_status` | Test Sample Status | `required_before_project` | `ApplicationForm.sample_status` |
| `project_type` | Project Type | `required_before_project` | `ApplicationForm.project_type` |

## 5. Sample Row Contract

Sample information is real product information and must be editable during Precheck review.

Rules:

- At least one sample row is required.
- All sample rows are editable.
- Operator may add sample rows.
- Operator may delete sample rows.
- Deleting the last remaining sample row is not allowed.
- Operator may copy a whole sample row into a new row.
- Copying one field value should be a frontend clipboard convenience, not a backend draft operation.
- Text quantities such as `20 pcs` must be preserved in draft review.

Sample draft row fields:

| Key | Label | State | Notes |
|---|---|---|---|
| `row_id` | Row ID | `readonly_source` | stable draft row identity; not user-facing |
| `product_name` | Product Name | `required_before_project` | may populate Project product name fallback |
| `part_number` | Part Number | `required_before_project` | required product identity |
| `revision` | Revision | `warning_before_project` | warning if blank |
| `lot_or_traceability` | Traceability Lot/No. | `required_before_project` | required |
| `manufacturing_lot_no` | Manufacturing Lot/No. | `warning_before_project` | parser may not support yet |
| `material` | Contact Base Material | `required_before_project` | required |
| `plating` | Contact Plating | `required_before_project` | required |
| `lubricant` | Contact Lubricant | `warning_before_project` | parser may not support yet |
| `housing_material` | Housing Material | `required_before_project` | required |
| `quantity` | Quantity | `required_before_project` | preserve source text; numeric parsing is later normalization |

Persist policy:

- `SampleInfo.quantity` currently accepts integer or null. Draft should keep original text first.
- Later implementation must either add a raw quantity field or preserve non-numeric quantity in a draft/audit field before converting to Project sample records.
- Do not silently coerce `20 pcs` to null without a warning.

## 6. Requested Testing, Disposition, And Recipients

| Key | Label | State | Persist target |
|---|---|---|---|
| `requested_testing` | Description of Requested Testing | `required_before_project` | `ApplicationForm.requested_testing` |
| `post_testing_disposition` | Post-Testing Sample Disposition | `required_before_project` | `ApplicationForm.post_testing_disposition` |
| `confidential` | Confidential tests or samples? | `required_before_project` | `ApplicationForm.confidential` |
| `subcontract` | Can testing be subcontracted? | `required_before_project` | `ApplicationForm.subcontract`, `ApplicationForm.subcontract_allowed` |
| `additional_information` | Additional Information | `warning_before_project` | `ApplicationForm.additional_information` |
| `send_copies_recipients` | Send copies of test results/reports to | `required_before_project` | `ApplicationForm.send_copies_recipients` |

Recipient policy:

- The field represents report recipient names or email aliases.
- It should be confirmed like other SECTION 1 content.
- Do not show fixed recipient chips as real data.

## 7. SECTION 2 Exclusion Policy

These fields belong to the testing laboratory section and are excluded from pre-project deterministic precheck:

| Key | Label | State |
|---|---|---|
| `lab` | Lab Performing the Tests | `section2_excluded` |
| `assigned_personnel` | Assigned Personnel | `section2_excluded` |
| `received_date` | Received Date | `section2_excluded` |
| `estimated_completion_date` | Estimated Completion Date | `section2_excluded` |
| `sample_condition` | Sample Condition | `section2_excluded` |

They may become LTR or lab workflow fields later, but they must not block New Project confirmation.

## 8. Lookup Option Contract

Frontend must not hard-code option lists in route pages.

Lookup groups required for Precheck review:

- `business_unit`
- `manufacturing_site`
- `results_format`
- `test_type`
- `sample_status`
- `project_type`
- `post_testing_disposition`

Policy:

- Options should be loaded from a backend lookup API.
- The backend source should be soft-coded so operators or future admin tooling can add/remove options.
- SQLite lookup table with seed defaults is preferred over frontend constants.
- If a draft value is not present in the current lookup list, UI must preserve and display the draft value.

Proposed endpoint for the next implementation task:

```text
GET /api/lookups/intake-precheck
```

## 9. Direct DOCX Intake Policy

Direct `.docx` is a first-class no-email entry path.

Application-form entry gate:

- Only `.docx` files can activate Intake `Continue to Precheck`.
- The selected Word document must have header table cell `(1,2)` containing `Laboratory Testing Request`.
- Backend validation is authoritative. The frontend may display the disabled reason, but it must not inspect local files or bypass the backend gate.
- When the header marker is missing or different, the Intake footer should show the observed `(1,2)` cell text, limited to a short cleaned value. Blank content should display as `empty`.
- `.doc` files may appear as stored attachments only; they are not valid application-form entry sources for Precheck.

It must create the same durable workflow records as `.msg` import:

```text
IntakePackage(source_type=direct_docx)
IntakeAsset(asset_role=selected_application_form)
IntakeCase(status=needs_review)
IntakeDraft(parsed_fields_json)
```

It must not create `Project` until the operator confirms Precheck review.

## 10. Draft-Level Precheck Policy

New Project Precheck must run before Project creation.

Scope:

- SECTION 1 only
- form metadata
- Lab Test Request Number clear-with-warning policy
- requestor and project intake fields
- sample rows
- requested testing, disposition, confidentiality, subcontract, additional information, and recipients

Excluded:

- `LAB_SECTION.estimated_completion_date`
- all SECTION 2 lab fields

Issue levels:

| Level | Behavior |
|---|---|
| `error` | blocks Project confirmation |
| `warning` | allows Project confirmation after visible operator review |
| `info` | display only |

UI feedback should use:

- top issue summary with counts
- inline field highlights
- row-level sample warnings/errors
- click or focus behavior to jump to fields
- no modal as the primary issue list

## 11. Source MSG Display Policy

The imported source `.msg` file is the source package, not an attachment.

Rules:

- Do not list the source `.msg` package in the Attachments list.
- Attachments list should show files extracted from the email package.
- If an email attachment is itself a `.msg`, display it as an attachment with `MSG` type.
- Source package metadata belongs in the email/source information panel.

## 12. Next Task Recommendations

Recommended next sequence:

1. `TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API`
2. `TASK_080_REAL_E3718_REVH_PARSER_CALIBRATION`
3. `TASK_081_UNIFIED_DIRECT_DOCX_INTAKE_BACKEND`
4. `TASK_082_DRAFT_REVIEW_AND_SAMPLE_EDIT_BACKEND`
5. `TASK_083_DRAFT_LEVEL_PRECHECK_BEFORE_PROJECT_CONFIRM`
6. `TASK_084_INTAKE_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION`
7. `TASK_085_PRECHECK_BUSINESS_UI_COMPLETION`
8. `TASK_086_INTAKE_BUSINESS_UI_COMPLETION`
9. `TASK_087_ROUTE_STATE_AND_WORKFLOW_SESSION_HARDENING`
