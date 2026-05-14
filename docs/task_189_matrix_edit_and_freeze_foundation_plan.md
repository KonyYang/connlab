# TASK_189 Plan - Matrix Edit And Freeze Foundation

## 1. Execution Gate (Anti-Skip Protocol)

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task ID from board: `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION`.
- Why this task is allowed now:
  - `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION` is complete.
  - Board now marks TASK_189 as next controlled task pending approval.
  - User explicitly requested execution of TASK_189.

This file is the required pre-implementation review artifact.  
No implementation code is included in this step.

## 2. Required Inputs Read

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION.md`
4. `docs/matrix_test_plan_data_management_decisions.md`
5. `docs/task_188_project_workbench_version_and_stale_status_plan.md`
6. `docs/task_188_project_output_version_ledger_correction_plan.md`
7. `docs/02_ARCHITECTURE_RULES.md`
8. `docs/frontend_architecture_rules.md`
9. `TASK_EXECUTION_SKILL.md`
10. `TASK_REVIEW_CHECKLIST.md`

Frontend/UI rule check:
- `$impeccable` loaded for product register context (`PRODUCT.md` + `DESIGN.md`).

## 3. Task Understanding (Step 1)

### 3.1 Goal

Build the first controlled Matrix editing and freeze/confirm foundation for Project Workbench:
- edit Matrix group/step data safely;
- validate step token parsing + step-sequence continuity;
- block confirmation on validation blockers;
- confirm one draft as current project planning authority;
- let downstream output staleness rely on persisted output ledger behavior.

### 3.2 Inputs

- `ProjectTestPlanDraft` active draft (`payload_json`, `status`, `version`).
- Matrix step tokens from existing or edited group-step rows.
- Current project output status summary from output ledger.

### 3.3 Outputs

- Updated or newly revised Project test-plan draft payload (structured groups/steps).
- Validation report with blockers/warnings.
- Confirmed draft state (`reviewed` status used as confirmed authority state in this phase).
- Workbench UI entry point for edit + validate + confirm flow.

### 3.4 Involved Modules

Backend:
- `backend/application/project_test_plan_*`
- `backend/api/routes_project_test_plan_drafts.py` (or sibling matrix-edit route module)
- `backend/modules/test_plan/*` (new step-token parser/validator utility)
- existing `backend/application/project_output_record_service.py` (read-path integration only)

Frontend:
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`
- new matrix-edit feature components/selectors/hooks under `frontend/src/features/project-workbench/`

Tests:
- new unit/integration tests for parser + service + API
- static frontend shell test additions for TASK_189 feature wiring

### 3.5 Explicitly Out of Scope

- Word/Excel import expansion
- test record filled-form import
- image/evidence step management
- fee mapping overhaul
- report generation
- AI review
- multi-user approval/permission workflow

## 4. Technical Design (Step 2)

## 4.1 Draft Authority And Version Strategy

Decision for TASK_189:
- Use existing `ProjectTestPlanDraftStatus.REVIEWED` as the confirmed/frozen authority state.
- Do not add a new enum value in this task.

Revision rule:
- If a draft in `reviewed` state is edited, create a **new draft candidate version** (status `draft`) without superseding the current `reviewed` authority.
- The existing `reviewed` draft remains the Project test-plan authority while the candidate draft is edited and validated.
- Only after `confirm_matrix_draft` succeeds should the previous `reviewed` draft become `superseded` and the candidate become the new `reviewed` authority.
- Do not mutate a reviewed draft in place.

Reason:
- preserves historical traceability;
- prevents unconfirmed edits from making downstream outputs stale too early;
- enables output ledger stale detection only after the project owner confirms the new authority Matrix.

Authority selection rule after TASK_189:
- Project test-plan authority = latest `reviewed` draft for the Project.
- `draft` = editable candidate only.
- `superseded` = historical draft, not authority.
- Existing Workbench/read-model logic that previously used "first non-superseded draft" must be updated or guarded so a draft candidate does not replace the reviewed authority before confirm.

## 4.2 Matrix Editable Payload Shape

Persistence carrier remains `ProjectTestPlanDraft.payload_json` in TASK_189.

Normalized shape target:

```text
payload.groups[]
  group_key
  group_label
  sample_size (optional)
  steps[]
    sequence               # parsed integer
    raw_token              # original token
    suffix_note            # trailing non-digit text
    test_item
    section
    method
    condition
    requirement
    step_description
    duration_value
    duration_unit
    source_trace
    note
payload.warnings[]
payload.blockers[]
```

No separate group/step SQL tables in TASK_189.

## 4.3 Step Token Parser + Continuity Validator

Add a deterministic parser utility module (under `backend/modules/test_plan/`) with rules:
- separators: comma, whitespace, newline
- leading digits => `sequence`
- trailing text => `suffix_note`
- token parsing retains `raw_token`

Examples:
- `3(a)` -> `sequence=3`, `suffix_note="(a)"`
- `4b` -> `sequence=4`, `suffix_note="b"`

Per-group blockers:
- first sequence not `1`
- duplicate sequence
- missing sequence gap
- invalid token without leading integer

Group can include repeated `test_item`; identity is group + sequence.

Confirmability classification:

Blockers:
- missing group identity (`group_number`, `group_key`, or equivalent stable group label)
- missing step sequence
- invalid step token
- duplicate step sequence inside one group
- non-continuous step sequence inside one group
- missing `test_item` for a step

Warnings:
- missing `method`
- missing `condition`
- missing `requirement`
- missing `duration_value` / `duration_unit`
- missing `source_trace`
- missing `step_description` when `test_item` is present

Rationale:
- sequence and test item are required to generate stable group record forms and import results later;
- method, condition, requirement, duration, and source trace are important planning data, but real projects may need to confirm the Matrix before all details are complete.

## 4.4 Application Service Design

Add a focused service, planned name:
- `ProjectTestPlanMatrixEditService`

Planned commands:
- `UpdateMatrixDraftCommand`
- `ValidateMatrixDraftCommand`
- `ConfirmMatrixDraftCommand`

Planned behaviors:

1. `prepare_editable_draft`
- validates project/draft ownership
- if source draft is `reviewed`, creates a new `draft` candidate version from its payload
- does not supersede the reviewed authority
- if source draft is already `draft`, returns the existing editable draft

2. `update_matrix_payload`
- validates project/draft ownership
- normalizes incoming groups/steps
- requires target draft status to be `draft`
- updates the draft payload without changing authority

3. `validate_matrix_draft`
- runs token parsing + continuity checks
- checks required fields for confirmability
- returns blockers/warnings + normalized view

4. `confirm_matrix_draft`
- fails when blockers exist
- requires target draft status to be `draft` or an already valid `reviewed` draft
- supersedes the previous reviewed authority for the Project only after validation passes
- updates target draft status to `reviewed`
- returns confirmed draft summary

Dependency rule:
- API -> MatrixEditService -> Draft service/repositories + Output ledger read model only.

## 4.5 API Design

Use task-provided candidate routes:

- `PUT  /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix`
- `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix/validate`
- `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix/confirm`

Response model principles:
- typed Pydantic responses only
- include `draft_id`, `version`, `status`, `authority_draft_id`, `authority_version`, `blockers`, `warnings`
- return actionable error detail on invalid tokens or sequence gaps

## 4.6 Output Ledger Interaction

TASK_189 does not write output files.  
Stale behavior must only happen after a confirmed authority change:
- editing a candidate `draft` must not make downstream outputs stale;
- validating a candidate `draft` must not make downstream outputs stale;
- once a candidate draft is confirmed as `reviewed`, the previous reviewed authority becomes superseded and existing output records tied to that previous draft read as `stale` through the persisted output ledger.

No new output-kind types in TASK_189.

## 4.7 Frontend UX/Architecture Plan

Register: `product` (Workbench task surface).

UI strategy:
- keep Matrix overview panel as first surface
- add edit entry point (`Edit Matrix draft`)
- use group selector + step detail panel
- avoid giant spreadsheet editing surface
- show validation blockers above confirm action

Frontend boundary plan:
- keep route page thin
- add feature-level editor model/hook in `features/project-workbench`
- API access only through `api/client.ts`

High-level component split:
- `ProjectWorkbenchMatrixEditPanel` (container)
- `MatrixGroupList` (group navigation)
- `MatrixStepEditor` (selected group step rows + detail controls)
- selector/helper for confirm availability and blocker rendering

## 5. File-Level Change Plan

Planned new/updated files (subject to implementation detail confirmation):

Backend:
- `backend/modules/test_plan/matrix_step_token_parser.py` (new)
- `backend/application/project_test_plan_matrix_edit_service.py` (new)
- `backend/api/routes_project_test_plan_drafts.py` (extend) or `routes_project_test_plan_matrix_edit.py` (new)
- `backend/api/dependencies.py` (wire service)
- `backend/api/main.py` (router include if new route file)

Frontend:
- `frontend/src/api/client.ts` (new matrix edit/validate/confirm DTOs + API funcs)
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` (editor state orchestration)
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx` (entry + summary integration)
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixEditPanel.tsx` (new)
- `frontend/src/workbench.css` (scoped styles for editor/detail panel)

Tests:
- `tests/unit/test_matrix_step_sequence_validation.py` (new)
- `tests/unit/test_project_test_plan_matrix_edit_service.py` (new)
- `tests/integration/test_project_test_plan_matrix_edit_api.py` (new)
- `tests/unit/test_frontend_shell_files.py` (TASK_189 wiring assertions)

Docs:
- `docs/task_board.md` (update only after implementation + validation complete)

## 6. Risks And Mitigations

1. Reviewed-draft in-place edits may break traceability  
Mitigation: enforce reviewed-draft edit => fork new draft version.

2. Payload shape divergence from legacy preview data  
Mitigation: parser/normalizer in service, strict typed request schema, fallback-safe defaults.

3. UI complexity growing into spreadsheet behavior  
Mitigation: group-step detail panel only; keep compact matrix overview.

4. Cross-layer leakage  
Mitigation: keep validation/business logic in application + module utilities, not in route/page JSX.

## 7. Validation Plan

Backend unit:

```powershell
python -m pytest tests\unit\test_matrix_step_sequence_validation.py tests\unit\test_project_test_plan_matrix_edit_service.py -q
```

Backend integration:

```powershell
python -m pytest tests\integration\test_project_test_plan_matrix_edit_api.py -q
```

Frontend:

```powershell
cd frontend
npm run build
```

Frontend static:

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"
```

Board guard:

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 8. Acceptance Criteria Mapping

- editable Matrix group/step flow exists for active draft
- token parsing preserves suffix note and validates numeric sequence continuity
- confirm is blocked when blockers exist
- confirmed authority state uses persisted draft status (`reviewed`)
- downstream stale semantics continue to rely on output ledger + active draft context
- Workbench remains matrix-first and non-spreadsheet-heavy

## 9. Stop Condition

After implementation, tests, and board update for TASK_189:
- stop;
- do not proceed to TASK_190+ without explicit user approval.
