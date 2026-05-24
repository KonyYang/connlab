# TASK 019 — Project Workbench Stepper

## Goal

Convert project detail page from parallel task cards into a sequential workflow workbench.

## Scope

Update:

```text
frontend/src/pages/ProjectWorkbenchPage.tsx
```

Add components:

```text
frontend/src/components/workflow/WorkflowStepper.tsx
frontend/src/components/workflow/WorkflowStepCard.tsx
frontend/src/components/workflow/NextActionPanel.tsx
frontend/src/components/project/ProjectSummaryPanel.tsx
```

## Workflow Steps

```text
1. Application Form
2. Precheck
3. LTR
4. Project Folder
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Show current project summary at top.
- Show workflow stepper below summary.
- Highlight current, blocked, ready, done, and warning states.
- Only show active step content in the main content panel.
- Every step must show next action or blocking reason.
- Do not display all forms at once.

## Out of Scope

- No new backend states unless required by existing data mapping.
- No Matrix or Report steps.

## Tests

- Add or update frontend static pytest checks.
- Run `npm run build`.

## Acceptance Criteria

- User can complete the same MVP workflow.
- Step order is visually obvious.
- Folder step is blocked until prerequisites are reasonable in UI.
- Frontend build passes.
