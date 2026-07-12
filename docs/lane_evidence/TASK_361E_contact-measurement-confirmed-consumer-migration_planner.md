# TASK_361E Contact Measurement Confirmed Consumer Migration Planner Evidence

Date: 2026-07-12

Role: Planner

Status: implementation authorized; pending Developer implementation.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A-D are complete/accepted, including
TASK_361D local commit `0fa429f53662addfe7fac86a12f73aad836c95fa`. The accepted
contract reserves TASK_361E as the serial-final confirmed-consumer migration lane.
The id and lane are otherwise unoccupied.

## Confirmed Goal

Move Fee LLCR/CR readings and TASK_360B formal specialized workbook source from
legacy Confirmed Matrix contact JSON to the effective confirmed independent
Measurement Plan projection. Keep TASK_361D draft artifacts, Fee rules, generic Test
Record, Report, schema/lifecycle, and frontend/client behavior outside this lane.

## Repository Findings

- The effective projection is confirmed-only and already enforces compatible-target
  omission and no editable-draft leakage.
- Fee currently reads contact readings from Confirmed Matrix Step quantities and can
  fall back to text when structured facts are absent.
- Formal TASK_360B preview currently reads active Confirmed Matrix contact plans.
- TASK_361D draft output has separate source, labels, routes, artifact root, manifest,
  latest/download, client, and setup-workspace panel.
- The frozen contract permits legacy compatibility only before independent bootstrap
  or when the feature is explicitly disabled; corrupt active authority cannot fall
  back.

## Planner Decision

Create one backend-only planned lane. A typed consumer adapter joins effective plan
targets to current Matrix context. Fee changes only contact-reading source. Formal
workbook keeps existing routes/UI/artifacts but changes internal authority source and
adds confirmed-plan/partial-compatible lineage metadata. No frontend/API client or
schema change is planned.

## Scope And Validation

Exact status rules, Fee no-bypass behavior, formal workbook partial-compatible
policy, legacy rollback, May Touch, locks, tests, and package isolation are recorded
in the task and plan. TASK_361D, Fee rule/seed/frontend, generic Test Record, Report,
parser, LTR/public drive, real files, and external residuals remain excluded.

## Definition Of Ready

Reviewer implementation-readiness re-gate passed. The user explicitly approved
source-of-truth reconciliation and Developer implementation after TASK_361F was
accepted at `983633b7` and TASK_361G at `cd41c3e3` with Integrator evidence
`e769f524`. Blocking questions remain none. Implementation authorization is limited
to the task-defined backend consumer migration and focused regressions.

## Validation Summary

- `git show --stat 0fa429f53662addfe7fac86a12f73aad836c95fa` confirmed
  TASK_361D Integrator acceptance and package boundaries; remote push remains absent.
- Board/task/plan/evidence record Reviewer plan pass, user-approved docs-only
  planning-first completion, the lifted pause, accepted TASK_361F/TASK_361G
  prerequisites, Reviewer readiness pass, and explicit implementation approval.
- `git diff --check` and no-index documentation checks passed with existing LF/CRLF
  working-copy warnings only.
- UTF-8 trailing-whitespace scan is clean.
- Targeted product-path status shows only pre-existing Matrix parser/test residuals;
  no backend consumer, Fee, workbook, API-client, frontend, or test implementation
  was changed by this Planner pass.
- TASK_360Q/R/S, parser/test changes, superpowers plans, and all other external
  residuals remain excluded.

## Evidence Paths

- `tasks/TASK_361E_CONTACT_MEASUREMENT_CONFIRMED_CONSUMER_MIGRATION.md`
- `docs/task_361e_contact_measurement_confirmed_consumer_migration_plan.md`
- `docs/lane_evidence/TASK_361E_contact-measurement-confirmed-consumer-migration_planner.md`
- `docs/task_board.md`

## Next Legal Role

Developer implementation pass for TASK_361E.
