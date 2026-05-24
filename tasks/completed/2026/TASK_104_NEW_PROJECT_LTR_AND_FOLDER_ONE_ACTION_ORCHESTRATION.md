# TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION

## Status

done

## Purpose

Implement the final New Project creation action after the single-page editor is stable.

Reference design: `docs/archive/historical_plans/new_project_single_page_flow_redesign.md`.

## Scope

- Add compact LTR number option:
  - `Auto assign next LTR number`
  - `Use specified LTR number`
- Validate required application data before registration.
- Enable the specified-number input only for the specified-number option.
- Check LTR numbering rules and conflicts through backend services.
- Preview/check LTR and folder creation effects before filesystem write.
- Preserve folder preview-before-write internally even if the UI presents one simplified completion flow.
- Register/commit LTR and create the project folder as the business completion point.
- Route to Projects/Project Workbench after success.

## Required Backend Boundary

- Add a thin orchestration application service only if needed.
- The orchestrator coordinates existing intake/draft, LTR, and folder services.
- It must not absorb parser, numbering, persistence, or filesystem rules into a god service.
- API routes remain thin and return typed DTOs.

## Out Of Scope

- Do not implement Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, or copied/external workbook write hardening.
- Do not implement final Word application-form generation.
- Do not implement TASK_099 LTR freeze/exception behavior.

## Validation

Required:

```powershell
py -m pytest tests\unit tests\integration -q
npm run build
```

## Stop Rule

Stop after implementation and update `docs/task_board.md`.


