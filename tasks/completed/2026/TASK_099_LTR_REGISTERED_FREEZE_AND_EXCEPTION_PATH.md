# TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10B - LTR workbook write hardening`
- Current Active Task on board: `TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH`
- Why this task was allowed: this task was previously paused until the single-page New Project redesign was resolved. `TASK_101` through `TASK_104` completed the single-page New Project path, and `TASK_133` through `TASK_138` completed controlled external LTR workbook commit and specified-number hardening. The freeze rule now has a stable point to attach to: after successful LTR registration/workbook commit.

## Step 1 Plan (For Review Only)

This document is the executable implementation plan for review.
No coding changes are allowed before explicit user approval.

## Purpose

Freeze normal editing of creation-base data after LTR registration succeeds, and route later corrections through a controlled revise/exception path instead of silently reopening New Project or Precheck editing.

## User Decision Baseline

The user previously approved this rule:

- After LTR registration succeeds, do not allow normal rollback to edit Precheck base fields.
- Later changes should use a revise/exception path.
- Product name and testing description are especially sensitive because they affect project folder and report naming.
- The LTR workbook/table may be updated often, but that does not mean the creation workflow should reopen earlier steps silently.

## Scope

Backend/API:

1. Identify the authoritative post-LTR state:
   - registered local LTR record
   - committed external workbook write when present
   - New Project completion state if applicable
2. Block normal edits to frozen creation-base fields after LTR registration.
3. Return business-readable blocked reasons from backend services/API when stale UI attempts to save frozen fields.
4. Use an existing exception/revision status or narrow marker if already present. If no suitable model exists, add only a minimal placeholder response/status for future revise flow, not a full management UI.

Frontend:

1. Display frozen fields as read-only when a project or intake case is already LTR-registered.
2. Show a concise operational message: changes require revise/exception handling.
3. Remove or disable any normal edit/save affordance that would imply the user can change frozen base data directly.
4. Keep the New Project page and Workbench visually consistent with existing product UI:
   - calm, dense, operational
   - no modal-first flow
   - disabled state must explain the reason

Documentation:

1. Record which fields are frozen after LTR registration.
2. Record which fields remain informational/non-frozen, if any.
3. Record that the actual revise/exception workflow is future controlled work unless already supported by existing primitives.

## Frozen Field Candidate Set

Confirm in implementation against existing data model and UI field config:

- product name
- requested testing / test item / testing description
- sample description and sample rows that affect LTR/project identity
- project setup confirmation values written to LTR workbook:
  - location
  - test type in sheet
  - project leader
- fields used in project folder naming:
  - DL/LTR number
  - project number when present
  - product name
  - requestor
  - date/business unit when used by template placeholders

## Out Of Scope

1. Do not implement Matrix, Report, AI review, LAN, permissions, Outlook auto-scan, or email sending.
2. Do not implement a full revision management UI.
3. Do not mutate external LTR workbook beyond already-approved write commit behavior.
4. Do not redesign the full New Project page.
5. Do not introduce a broad audit/event system unless a narrow existing record can be reused safely.

## Proposed File-Level Changes

Likely backend files:

1. `backend/application/new_project_application_draft_service.py`
   - Guard updates to frozen draft/application fields after LTR registration.
2. `backend/application/new_project_completion_service.py`
   - Preserve post-LTR completion behavior and avoid duplicate writes.
3. Existing LTR/project repositories or stores
   - Read current LTR state for guard decisions.
4. Relevant API route tests
   - Assert stale edit attempts receive actionable 400/409 style business errors.

Likely frontend files:

1. `frontend/src/features/new-project/*`
   - Render frozen fields read-only/disabled when backend state indicates LTR registered.
   - Show inline blocked reason near the affected editor/action area.
2. `frontend/src/api/client.ts`
   - Add typed fields only if backend response needs a new guard/blocked reason.
3. `tests/unit/test_frontend_shell_files.py`
   - Static guard for read-only/blocked copy and absence of normal edit affordance in frozen state.

Documentation:

1. `docs/task_board.md`
   - Activate/complete task status and record validation.
2. New or existing workflow doc if needed:
   - record frozen field policy and future revise/exception boundary.

## Detailed Execution Design

1. Backend discovery:
   - locate existing application draft update endpoint/service
   - locate how project/LTR registration state is read
   - identify field keys persisted from New Project editor
2. Backend guard:
   - add a small function or service helper that determines whether base edits are frozen
   - reject frozen-field changes after registered LTR
   - include field names and a business-readable reason
3. Frontend state:
   - consume existing or added guard response
   - render disabled/read-only controls for frozen fields
   - keep copy concise and operational
4. Tests:
   - backend unit/integration test for frozen edit rejection
   - frontend static test for visible blocked copy
   - existing New Project completion tests must keep passing

## UI Design Constraints

Using `$impeccable` product register:

- This is a workbench state/guard change, not a new page.
- Use restrained status color and text together.
- Do not use modal-first confirmation for normal frozen state.
- Do not add nested cards or decorative warning blocks.
- Frozen-state copy must be operational, for example: `LTR registered. Base application fields require revise/exception handling.`

## Risks And Mitigations

1. Risk: frontend-only freeze could be bypassed by stale sessions.
   - Mitigation: backend guard is authoritative.
2. Risk: freezing too many fields could block harmless notes.
   - Mitigation: define explicit frozen field set and leave non-identity notes editable only if existing behavior supports it.
3. Risk: adding a full exception workflow expands scope.
   - Mitigation: only expose blocked reason and future path marker unless existing exception primitive is already available.
4. Risk: duplicate LTR/workbook writes during retry paths.
   - Mitigation: do not change TASK_134/TASK_133 duplicate-write safeguards.

## Validation Plan

Required:

```powershell
py -m pytest tests\integration\test_new_project_completion_api.py tests\unit\test_frontend_shell_files.py -q
py -m pytest tests\unit tests\integration -q
npm run build
```

Optional targeted tests after code discovery:

```powershell
py -m pytest tests\unit\test_new_project_application_draft_service.py -q
```

## Approval Gate

After user explicitly replies with approval, Step 2 implementation will start.

## Implementation Summary

- Backend review responses now expose `base_editing_frozen`, `frozen_field_keys`, and `frozen_reason` when an intake case is confirmed to a project that already has a registered LTR.
- Backend review-field updates now reject actual changes to frozen base fields with HTTP 409 and a business-readable revise/exception message.
- New Project editor now displays the frozen-state message, disables normal field/table editing, and stops autosave when the case is frozen.
- Non-frozen note fields remain service-level editable when frozen values are unchanged.

## Validation

```powershell
py -m pytest tests\unit\test_intake_case_review_service.py -q
py -m pytest tests\integration\test_manual_intake_api.py::test_review_fields_returns_conflict_after_registered_ltr -q
py -m pytest tests\unit\test_frontend_shell_files.py::test_task099_new_project_editor_exposes_ltr_registered_freeze_state -q
py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q
py -m pytest tests\unit tests\integration -q
npm run build
```

Result:

- targeted review service tests: `14 passed`
- targeted API freeze test: `1 passed`
- targeted frontend freeze test: `1 passed`
- related integration/frontend suite: `66 passed`
- full backend suite: `408 passed`
- frontend build: passed
