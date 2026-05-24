# TASK 026 鈥?Office Integration Boundary

## Goal

Establish the OfficeFacade / Office gateway boundary for Office-related file reading, extraction, and classification.

This task creates infrastructure boundaries only. It must not create projects, intake storage tables, UI, or end-to-end `.msg` import behavior.

## Current Phase

`Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

## Why This Task Is Allowed Now

`TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` opened Phase 6A and explicitly activated this task as the next controlled implementation step.

## Required Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/archive/historical_plans/ConnLab_Phase6_Implementation_Plan.md`
4. this task file
5. `docs/project_management/TASK_EXECUTION_SKILL.md`
6. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
7. `docs/project_management/TESTING_SKILL.md`

## Scope

Add:

```text
backend/infrastructure/office/
  __init__.py
  office_facade.py
  office_lifecycle.py
  outlook_msg_gateway.py
  word_document_gateway.py
  excel_workbook_gateway.py
  models.py
```

Add focused unit tests for:

- Office file classification.
- `WordDocumentSnapshot` extraction from a small generated `.docx`.
- Import boundary checks that application/api/frontend code does not directly import `win32com` or `docx`.

## Requirements

- `OfficeFacade` only reads, extracts, and classifies Office-related files.
- `OfficeFacade` must not create `Project`, `ApplicationForm`, `SampleInfo`, `IntakePackage`, or `FileAsset`.
- Word reading must use file-level parsing first.
- The Word gateway must create a `WordDocumentSnapshot` only; application form field parsing remains in the intake parser.
- Excel gateway is a boundary placeholder only in this task.
- COM fallback, if represented, must be centralized behind `OfficeLifecycleManager`.
- No module outside `backend/infrastructure/office/` may directly import `win32com`.
- No application/api/frontend module may directly import `docx`.
- Errors must be explicit and actionable.

## Out Of Scope

- No `.msg` attachment extraction implementation beyond boundary stubs.
- No Excel workbook business reading.
- No intake database tables.
- No API endpoints.
- No frontend pages.
- No project confirmation flow.
- No Outlook inbox automation.
- No email sending.
- No Matrix, Report, AI review, or folder template UX.

## Acceptance Criteria

- Office infrastructure package exists.
- `OfficeFacade` exposes the planned boundary methods.
- Unit tests cover basic file classification and Word snapshot behavior.
- Existing pytest suite passes.
- `docs/task_board.md` is updated after completion and the task stops.
