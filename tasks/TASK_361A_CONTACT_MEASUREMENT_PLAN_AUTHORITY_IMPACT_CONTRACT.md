# TASK_361A Contact Measurement Plan Authority Impact Contract

## Status

Complete/accepted as a contract and downstream planning basis. Reviewer plan gate
passed, the user approved Developer planning-first, Developer planning-first
completed as docs-only, Reviewer implementation-readiness passed, and the user
approved source-of-truth reconciliation on 2026-07-12.

This closeout does not authorize or record any schema, migration, API, UI, test,
workbook, or other product implementation.

## Lane

`contact-measurement-plan-authority-impact-contract`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Upstream: TASK_360A/B/C/G are complete/accepted.
- Role: Planner contract preparation.
- Why allowed: Discovery confirms the new independent plan lifecycle cannot safely be implemented through the existing Matrix-bound contact plan alone.

## Contract Goal

Define the product and data authority boundary for an independently drafted and confirmed Contact Measurement Plan, deterministic Matrix impact analysis, review-draft creation, draft workbook output, and confirmed-only downstream consumption.

## Contract Deliverables

1. Plan version lifecycle and state-transition table.
2. Stable Group-Step target identity and Matrix binding contract.
3. Exact impact taxonomy for text, sample quantity, unrelated Steps, and structural contact-target changes.
4. Effective confirmed projection during `Needs review`.
5. Draft/review/confirm stale fingerprint rules.
6. Non-destructive schema, constraints, migration/bootstrap, rollback, and audit proposal.
7. API/DTO command and read-model contract.
8. Matrix summary and dedicated setup workspace state/interaction contract.
9. Draft versus formal workbook lineage and labeling contract.
10. Downstream TASK_361B-E scope and package boundaries.

## May Touch

- `tasks/TASK_361A_CONTACT_MEASUREMENT_PLAN_AUTHORITY_IMPACT_CONTRACT.md`
- `docs/task_361a_contact_measurement_plan_authority_impact_contract_plan.md`
- `docs/lane_evidence/TASK_361A_contact-measurement-plan-authority-impact-contract_planner.md`
- `docs/task_361_contact_measurement_plan_independent_lifecycle_discovery_plan.md`
- `docs/lane_evidence/DISCOVERY_contact-measurement-plan-independent-lifecycle_planner.md`
- `docs/task_board.md` through normal Planner flow

## Must Not Touch / Locked Paths

- No backend, frontend, tests, API client, schema, migration, workbook, or real-file change.
- No Matrix parser, Fee behavior, generic Test Record, LTR/public-drive, Basic Information, Folder Actions, StepInstance, Report, release/settings, or unrelated cleanup.
- `.agents/**`, `docs/project_management/**`, remote push, and destructive git operations remain locked.

## Validation Gate

- Contract traces every user-confirmed rule to a lifecycle state, impact outcome, and downstream visibility rule.
- Stable identity handles imported and manually created targets without relying on regenerated confirmed/draft ids.
- Schema proposal defines non-destructive migration, legacy bootstrap, unique constraints, active/draft invariants, audit metadata, and rollback behavior.
- API contract separates save draft, impact review, accept suggestions, confirm plan, draft workbook, and confirmed consumer reads.
- UX contract keeps Matrix summary compact and setup as a dedicated page, with no modal-first or nested-card design.
- `git diff --check`, trailing whitespace, planned-only status, and forbidden product-path scans pass.

## Merge Gate

Satisfied for the contract package only. Each downstream lane retains its own
Discovery, Reviewer, user-approval, implementation-readiness, QA, and Integrator
gates. TASK_361A itself is contract-only and does not authorize implementation.

## Definition Of Ready

Satisfied and accepted for downstream planning. No implementation authorization is
implied.

## Blocking Questions

None for contract planning.
