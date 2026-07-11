# TASK_360G Matrix Contact Plan Confirmation Persistence Planner Evidence

Date: 2026-07-11

Role: Planner

Status: implementation_authorized, pending Developer implementation pass.

## Discovery Outcome

The live failure is explained by two confirmed backend path differences and one UI reload gap:

1. Matrix Editor session confirmation returns `no_change` using signatures that omit Step quantities/contact plans.
2. Its session-confirm snapshot builder returns no `step_quantities`, unlike the existing direct authority and revision-flow builders.
3. The loaded draft target plans do not hydrate the transient common family-profile controls.

Draft and confirmed repositories already persist `contact_plan_json`; the issue is not a missing schema or storage capability. The planned correction is therefore a small session-confirm comparison/snapshot fix plus safe profile hydration. Fee and TASK_360B remain correctly confirmed-only consumers.

## Scope And Locks

- May Touch is limited to Matrix Editor session confirmation, an optional focused pure authority-signature helper, contact-plan selectors/workspace, focused tests, and governance docs.
- No schema/repository/route/API-client changes; no Fee logic, TASK_360B implementation, generic Test Record, parser/import, LTR/public-drive, StepInstance, Report, real workbook/folder, or release/settings work.

## Numbering And Dependency Note

`TASK_360D`, `TASK_360E`, and `TASK_360F` are already occupied by unrelated Matrix UI/parser tasks, so this lane uses `TASK_360G`. TASK_360C is complete/accepted in `5c1b10ab1aa85d478903d7e53947c23a6c7c9056`; it is an upstream basis, not a future gate for TASK_360G.

## Definition Of Ready

Satisfied. No blocking questions. Reviewer plan re-gate, user-approved docs-only Developer planning-first, and Reviewer implementation-readiness are complete; the user approved reconciliation plus implementation.

## Reviewer B1 Alignment

The TASK_360C board-closeout prerequisite was removed after source-of-truth reconciliation confirmed its Integrator acceptance. TASK_360G subsequently passed its Reviewer plan re-gate, docs-only Developer planning-first, and Reviewer implementation-readiness gate; user approval now authorizes implementation only within this lane's stated scope.

## Recommended Next Role

Developer implementation pass.

## Planning Validation

- Read board, TASK_360A/B/C evidence, current Matrix Editor session/confirmation code, direct authority/revision builders, Step quantity persistence, contact-plan selectors, Task 360B projection/QA evidence, and worktree status.
- Confirmed the planned TASK_360G identifiers were unused.
- Confirmed existing external Fee, parser, CSS, shell-test, UI hotfix, and documentation residuals remain outside this lane.
