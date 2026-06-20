# TASK_330_PROJECT_BASIC_INFORMATION_AUTHORITY

## Status

Umbrella plan ready for user review. Implementation not started.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_329 is complete and there is no active implementation task. The user explicitly requested a new detailed plan and task file for a Project Workbench `Basic Information` authority feature.

## Executable Plan

- `docs/task_330_project_basic_information_authority_plan.md`

## Goal

Add `Basic Information` as a Project Workbench action and establish a confirmed project-level Basic Information snapshot used by formal downstream outputs.

The latest confirmed snapshot becomes the backend authority for:

- project folder Fee form identity fields,
- project folder Customer Feedback form identity/contact fields,
- copied LTR application Word write-back,
- future LTR workbook/report synchronization tasks.

## User-Facing Shape

Workbench top action order:

```text
Matrix Editor | Fee Evaluation | Basic Information | Generate/Update project folder
```

`Basic Information` opens a dedicated editable page or work area. The interaction may follow the broad pattern of `Fee Evaluation`: load current data, edit, save draft, confirm, then return to Workbench.

The Workbench right-side `Project Basic Information` card is summary-only:

- no editable fields,
- no duplicate DL Number / Product / Test Item already shown in the Workbench top identity,
- no `Edit` entry,
- optional `View` expansion to show all confirmed basic information as read-only,
- compact status such as confirmed/not confirmed, needs review, last confirmed time, and whether formal outputs use the latest confirmed version.

## Core Business Rules

1. Formal project folder outputs must use the latest confirmed Basic Information snapshot.
2. If no confirmed snapshot exists, project folder create/update must return an actionable blocker before mutating files.
3. Updating Basic Information and confirming it creates a new authoritative version.
4. Clicking `Update project folder` after a new confirmation must refresh formal outputs from the new version where safe.
5. Source changes from application form, Matrix date fields, or Fee total may mark Basic Information as `needs_review`, but must not silently overwrite confirmed values.
6. Existing projects without a confirmed snapshot must receive an assembled unconfirmed draft, not a silent confirmation.
7. Project-folder output refresh must obey managed-output fingerprint safety and must not overwrite manually changed or unmanaged files.

## Subtasks

TASK_330 must not be implemented as one large pass.

- `TASK_330A_PROJECT_BASIC_INFORMATION_AUTHORITY_DATA_API`
  - persistence, source assembly, merge priority, draft save, confirm, review status, and API.
- `TASK_330B_PROJECT_BASIC_INFORMATION_WORKBENCH_UI`
  - Workbench top action, dedicated editor page/work area, and read-only summary card.
- `TASK_330C_PROJECT_BASIC_INFORMATION_OUTPUT_CONSUMPTION`
  - project folder blocker, formal output consumption, managed-output safety, and output signatures.

## Inputs

- Project id.
- Existing project/LTR identity.
- Parsed application form data.
- Matrix authority-derived date fields when available.
- Current Fee authority total fee when available.
- Operator edits from Basic Information page.

## Outputs

- Draft Basic Information data.
- Confirmed Basic Information version.
- Review status and source-change metadata.
- Project folder create/update blockers or output source signatures.
- Formal file outputs that use the confirmed snapshot.

## In Scope

- Umbrella design and task split.
- Subtask-specific scope is defined in TASK_330A, TASK_330B, and TASK_330C.

## Out Of Scope

- No StepInstance implementation.
- No report generation implementation.
- No public-drive upload redesign.
- No LTR workbook writeback.
- No Matrix editing semantic changes.
- No Fee pricing authority semantic changes beyond reading confirmed Basic Information for formal outputs.
- No generic template-mapping UI.
- No direct frontend Office/filesystem/SQLite access.
- No automatic replacement of confirmed Basic Information from upstream source changes.

## Acceptance Criteria

- TASK_330 is split into 330A, 330B, and 330C.
- Each subtask has its own stop point and validation.
- The umbrella plan explicitly covers existing-project initialization, source merge priority, required confirmation fields, and managed-output refresh safety.
- User-facing copy remains operational and does not expose backend storage terms.

## Validation

After explicit subtask implementation approval, run the validation listed in the active subtask.

## Stop Point

Stop after plan review. Do not implement until the user explicitly approves TASK_330A.
