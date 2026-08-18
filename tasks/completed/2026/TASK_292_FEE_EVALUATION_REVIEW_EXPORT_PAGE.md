# TASK_292 Fee Evaluation Review & Export Page

Status: complete (archived 2026-08-18; implementation integrated and covered by tests)

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_291 is complete on `docs/task_board.md`; the user explicitly approved implementing this TASK_292 plan.

## Goal

Move Fee Evaluation review out of the Workbench main content into an independent route:

```text
/projects/:projectId/fee-evaluation
```

Workbench remains focused on Matrix, Step Workspace, and compact derived-output status. Fee Evaluation V1 is a Review+Export surface: it shows fee draft status, review reasons, rule traceability, and Matrix basic-fill export. Pricing completion remains in the generated Excel file.

## Scope

- Add a Fee Evaluation page with:
  - back-to-Workbench action
  - project/LTR identity
  - draft status and review count
  - rule version, pricing effective date, generated time, output freshness
  - Matrix basic-fill export panel
  - full-width review table with filters and search
- Remove the full Fee Evaluation review table from `ProjectWorkbenchLayout`.
- Keep a compact Workbench Fee Evaluation summary with an `Open Fee Evaluation` action.
- Add typed frontend API client support for:

```text
POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export
```

## V1 Export Rules

- Always call export with `fill_mode: "matrix_basic"`.
- Use template path:

```text
D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls
```

- Use the latest generated project folder path as the output directory.
- Disable export if there is no active Matrix fee draft or no generated project folder.
- Allow review-required drafts to export because Matrix basic fill only fills Matrix group/test-item structure.
- Do not ask the operator to type arbitrary output directories in V1.

## Out Of Scope

- Backend fee calculation changes.
- Persistent fee-line edits.
- In-app price editing.
- Rule maintenance UI.
- New backend API or output-record behavior.
- Matrix editing changes.
- StepInstance, execution persistence, report generation, approval package changes.

## Acceptance

- `/projects/:projectId/fee-evaluation` loads as a first-class route.
- Workbench no longer renders the full fee review table under Matrix.
- Workbench summary opens the Fee Evaluation page when Matrix authority exists.
- Fee page can filter by all, review required, calculated, and no rule match.
- Export action calls the existing backend export endpoint with Matrix basic-fill settings.
- Export success shows output path.
- Timeout and validation errors show actionable business-readable messages.
- Related frontend tests, build, shell static checks, and browser smoke pass.
