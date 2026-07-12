# Contact Measurement Plan Independent Lifecycle Discovery Evidence

Date: 2026-07-12

Role: Planner

Status: discovery_complete

## Outcome

The requested independent Contact Measurement Plan lifecycle is a formal multi-lane program, not a UI-only refactor. Existing contact plans are embedded in Matrix Step quantity rows and confirmed only through Matrix authority. Independent confirmation, review drafts, retained old confirmed plans, partial formal-consumer compatibility, and draft workbook lineage require a new authority contract and a reviewed non-destructive schema addition.

## Recommended Split

- TASK_361A: authority and impact-analysis contract, planned only.
- TASK_361B: authority backend, schema/migration, impact analysis, API.
- TASK_361C: dedicated setup workspace and compact Matrix summary.
- TASK_361D: draft workbook preview/generation/labeling.
- TASK_361E: confirmed consumer migration and regressions.

## Design Evidence

The external audit and ConnLab product guidance support a compact Matrix summary and a dedicated non-modal workspace. The current embedded card mixes too many responsibilities and visually ties plan confirmation to Matrix confirmation.

## Schema Finding

Schema is necessary but not authorized. Current regenerated Matrix ids and embedded `contact_plan_json` cannot by themselves express independent immutable plan revisions and stable review lineage. TASK_361A must define stable target identity, constraints, migration/bootstrap, and rollback before TASK_361B can be approved.

## Not Yet Confirmed

Stable target key representation, family snapshot storage shape, and eager-backfill versus compatibility-adapter migration remain open technical contract decisions. They are non-blocking for TASK_361A and blocking for TASK_361B implementation authorization.

## DoR

- Discovery: satisfied.
- TASK_361A: ready as planned contract-only lane.
- TASK_361B-E: not ready for implementation pending accepted contract and their own gates.
- Blocking questions: none for TASK_361A.

## Validation

Read AGENTS, board, Planner/parallel/orchestration protocols, PRODUCT/DESIGN/frontend architecture, TASK_360A/B/C/G task/plan/evidence, current Matrix quantity/contact plan storage and services, current specialized workbook projection/generation/artifact boundary, Matrix Editor UI/routing, tests, git history/status, and the supplied product design audit.
