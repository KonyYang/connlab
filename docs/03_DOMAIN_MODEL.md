# Domain Model Snapshot

Last Updated: 2026-05-16
Status: current snapshot with historical MVP section

This document is a high-level domain map. It is not a database schema and does not authorize implementation of future objects by itself.

Current authority order:

1. `../AGENTS.md`
2. `docs/task_board.md`
3. active `tasks/TASK_XXX_*.md`
4. focused architecture/domain documents referenced by the active task

## Current Domain Principles

- Project is the lifecycle container and traceability center.
- Matrix is the execution authority map for what must be tested.
- Step-level execution data is future source-of-truth scope only when an approved task implements it.
- Runtime Projection and UI read models are not domain identity.
- Test Record, Report, Fee Evaluation, and Approval Package are derived outputs.
- Word and Excel are input/output formats, not the primary system data model.

## Historical MVP Objects

These objects formed the original baseline and remain part of the implemented product history.

### Project

Fields:

- id
- dl_number / ltr_number context
- title
- product_name
- requestor
- business_unit
- project_no (optional application reference only)
- status
- root_folder
- created_at
- updated_at

Historical statuses included:

- DRAFT
- PRECHECK_REQUIRED
- PRECHECK_PASSED
- LTR_REGISTERED
- FOLDER_CREATED

### ApplicationForm

Structured data extracted from or confirmed against request/application material.

Representative fields:

- form_no
- form_rev
- requested_by
- phone
- request_date
- email
- business_unit
- manufacturing_site
- project_no
- requested_completion_date
- test_type
- sample_status
- project_type
- description_of_requested_testing
- subcontract_allowed
- lab_performing_tests
- lab_personnel_assigned
- date_lab_received_samples
- estimated_completion_date
- sample_condition

### SampleInfo

Structured sample rows extracted from application forms.

Representative fields:

- product_name
- part_number_revision
- traceability_lot
- contact_base_material
- contact_plating
- contact_lubricant
- housing_material
- quantity

### PrecheckResult / PrecheckIssue

Deterministic quality-gate outputs for application/request material.

Precheck is not AI. It produces business-readable findings and confirmation state.

### LtrRecord

Local structured record for LTR registration/tracking, with workbook-authority behavior introduced in later tasks.

### ProjectFolderRecord

Structured record for previewed/generated project folders.

### FileAsset

Structured file reference for source material, attachments, evidence candidates, and generated outputs.

## Current Matrix Foundation Objects

### ProjectTestPlanDraft

Represents Project-scoped Matrix/test-plan draft data extracted, imported, reviewed, edited, or confirmed.

Current semantics:

- Project remains lifecycle container.
- Matrix draft represents execution authority candidates.
- Latest reviewed/confirmed authority is distinct from candidate edits.
- Candidate drafts must not supersede reviewed authority until confirm succeeds.
- Group identity must be explicit and stable.

### Matrix Authority

Matrix authority is the approved execution map for what must be tested. It is not the same as UI table display.

Authority identity should be derived from:

- Project
- Matrix authority/draft reference
- group identity
- sequence/token

## Current Output Ledger Objects

### ProjectOutputRecord

Tracks derived output versions and freshness context for generated/written artifacts.

Derived output categories include:

- Section 2 write-back
- test record
- fee evaluation
- approval package

Output records are not Matrix authority and do not own Step identity.

## Current Runtime Projection Objects

TASK_201-TASK_202 introduced backend-only, in-memory projection/read-model foundations.

### InteractiveStepTokenProjection

Read-model projection for displaying/selecting a Matrix step token.

It may carry:

- project reference
- matrix authority/draft reference
- group reference and group label
- raw token
- sequence number
- suffix / variant / suffix note
- technical row context
- lifecycle projection
- evidence projection
- report sync projection
- stale projection
- attention projection
- parser warnings

These are projection/read-model fields, not domain source of truth.

### RuntimeProjectionSummary / GroupRuntimeProjection

Read-model aggregation outputs for consuming already-supplied projection dimensions.

They are pure aggregation boundaries, not runtime engines.

## Future Execution Objects (Not Implemented Unless Approved)

The following remain controlled future scope:

- StepInstance
- TestDefinition
- TestGroup
- TestRecord as execution source object
- TestResult
- TestAsset
- LabReport
- AuditReport
- KnowledgeDocument
- AIReviewResult

StepInstance must not be introduced through UI token state, projection color, report sync marker, stale marker, or attention priority. Projection does not define domain identity.

