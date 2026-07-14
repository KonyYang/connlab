# TASK_361J Package Scope Reconciliation Evidence

Date: 2026-07-15

Role: Planner

Status: package scope reconciled / pending Integrator package re-gate.

## Trigger

Integrator found that the implemented TASK_361J JSX references
`.contact-measurement-button*` classes whose definitions live in pre-existing mixed
CSS hunks. Excluding those definitions produces a non-self-contained package; taking
the files wholesale would absorb unrelated residuals. The user explicitly authorized
the required button-style hunks as TASK_361J package inputs.

## Package Ownership Decision

TASK_361J now owns only these previously mixed dependencies:

- `frontend/src/contact-measurement-plan.css`: `contact-measurement-button`,
  `contact-measurement-action-group`, primary, secondary, compact, disabled,
  focus/hover, and responsive rules used by the simplified editor;
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`:
  current class references required by Add row, Delete row, Cancel, and Confirm; and
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`:
  its former Back-button class hunk is recorded as historical overlap only. The Back
  action has been removed, so it must not be reintroduced merely for packaging.

Integrator may stage these files at hunk level so the final commit contains both the
implemented controls and their required styling. This is not wholesale file ownership.

## Gates Preserved

- Developer implementation and focused fix passes remain complete.
- Reviewer implementation re-gates remain `reviewer_pass`.
- QA keyboard-delete re-smoke remains `qa_pass`.
- No Developer rerun or product behavior change is required by this reconciliation.
- TASK_361J remains pending Integrator and is not complete/accepted.

## Exclusions Preserved

Do not include unrelated CSS, workspace/editor, or board hunks; TASK_361F evidence;
TASK_361H artifacts; Fee rules/pricing/UI; TASK_360B/TASK_361D workbooks; Generic Test
Record/Report; Matrix Step or parser behavior; LTR/public drive; real databases/files;
`.agents/**`; or `docs/project_management/**`.

## Validation

- Confirmed current `ProjectPointProfileEditor.tsx` references the authorized button
  classes for Add, Delete, Cancel, and Confirm.
- Confirmed `contact-measurement-plan.css` contains the corresponding action-group,
  button state, compact, and responsive definitions.
- Confirmed `ContactMeasurementSetupWorkspace.tsx` no longer references the removed
  Back action, so its prior class hunk is historical only.
- Governance-only pass: no product, schema, API client, or test implementation was
  modified; no staging, commit, or push occurred.

## Next Legal Role

Integrator package re-gate with hunk-level staging and locked-residual exclusion.
