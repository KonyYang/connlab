# TASK_219C_DERIVED_OUTPUT_STATUS_CONSOLE_ALIGNMENT

## Status

Draft task document. Pending user review and explicit approval.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. This task should run after `TASK_219A` clarifies the Workbench Runtime Console IA and after `TASK_219B` if model boundaries are needed first.

## Why This Task Is Allowed Now

The business conclusion says these outputs are generated after Matrix Edit:

- test record
- fee evaluation
- Section 2 completion date

The current code already has output status infrastructure:

- backend `routes_project_output_records.py`
- frontend `getProjectOutputStatusSummary`
- frontend `ProjectWorkbenchDocumentStatusPanel`
- frontend `deriveWorkbenchVersionStatus`

However, current Workbench copy and lower approval package form still imply the operator manually prepares output paths as a normal workflow. The Runtime Console should show derived output state and any stale/missing/failure reasons, not expose generated outputs as a large manual assembly process.

## Model Fit Assessment

`GPT-5.3-codex` is suitable because this task is a narrow contract/copy/UI alignment slice around existing output status DTOs and frontend rendering. It does not require implementing generation engines.

## Objective

Align Workbench derived-output presentation with Matrix-driven runtime direction.

The console should treat:

- Section 2 completion date/write-back
- Test Record
- Fee Evaluation
- Approval Package

as output status records derived from Matrix authority and project lifecycle state.

## Existing Code Context

Backend:

- `backend/api/routes_project_output_records.py`
- `backend/application/project_output_record_service.py`
- `backend/infrastructure/storage/repositories/project_output_record.py`
- `backend/api/routes_approval_package.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Current frontend status keys:

- `section2`
- `test_record`
- `fee_evaluation`
- `approval_package`

Current backend output kinds include:

- `section2_write_back`
- `test_record_form`
- `fee_evaluation`
- `approval_package`

## Scope

Allowed:

- frontend copy and rendering changes for derived output status
- selector cleanup for status reasons and labels
- typed client alignment if existing DTO names are unclear
- backend response documentation update if needed
- tests for status label/selector behavior
- create an implementation plan document before code

Forbidden:

- implementing actual test record generation
- implementing actual fee evaluation generation
- implementing actual Section 2 Word write-back automation
- changing output record persistence semantics
- adding new output kinds without proving current kinds are insufficient
- expanding approval package placement workflow

## Required First Deliverable

Before coding, create:

```text
docs/task_219c_derived_output_status_console_alignment_plan.md
```

The plan must include:

- current output status lifecycle
- current UI labels and why they conflict with new positioning
- proposed derived-output status copy
- selector changes
- test plan
- risk that backend generation is not implemented in this slice

Stop after writing the plan and wait for explicit user approval.

## Implementation Guidance After Approval

Expected direction:

- Rename user-facing copy from "Downstream status" to a Runtime Console output state label such as "Derived outputs" or "Output sync".
- Make reasons business-readable and avoid implying manual path entry is required for generated outputs.
- Show states as `Current`, `Stale`, `Missing`, `Manual`, or `Failed` with clear explanations.
- Keep path display secondary and optional.
- Approval package should be represented as package readiness/status, not a primary manual form.

## Acceptance Criteria

- Workbench output area communicates generated/derived state, not manual preparation workflow.
- Status labels are business-readable.
- Missing generated outputs do not ask the user to manually type paths as the default next action.
- Existing `ProjectOutputStatusSummary` API remains compatible.
- No generation engine is implemented.
- `npm run build` passes.
- Selector/unit/static tests cover the revised labels or status mapping where practical.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Recommended:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

If backend contract documentation is touched:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

