# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective Planner Evidence

Date: 2026-07-13

Role: Planner

Status: implementation authorized; pending Developer implementation. TASK_361E
remains paused_by_user.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361B-D are complete/accepted. The user
explicitly paused TASK_361E and requested a separate corrective lane for a production
startup failure rooted in the accepted TASK_361B SQLite compatibility boundary.
TASK_361F is unoccupied and is the next legal TASK_361 sub-number.

## Evidence Read

- AGENTS, board, Planner/orchestration/parallel protocols, and TASK_361A-E context.
- TASK_361B task/plan and accepted schema/index/bootstrap contract.
- `backend/infrastructure/storage/database.py` initialization order.
- `contact_measurement_plan_authority_schema_migration.py` required names, strict
  index/check/FK validators, and failure messages.
- Authority ORM index/constraint declarations and focused schema tests.
- Matrix session dependency/API references and current git status.

No real SQLite database was opened, copied, or modified.

## Findings

- The runtime failure happens before Matrix Editor business actions: dependency
  construction calls `init_db()`, which calls the strict authority migration.
- Existing tables do not receive later index additions from `create_all()`.
- The migration currently detects missing names but provides no semantic
  compatibility recognition or safe bootstrap.
- This is a startup/schema compatibility corrective, not TASK_361E Fee/formal
  workbook consumer migration.

## Planner Decision

Create one backend-storage corrective lane. Future implementation may recognize an
exact equivalent unique-index semantic shape regardless of name, or create a missing
canonical index only after all duplicate preflights pass. It must revalidate after
DDL, be repeatable, preserve every authority row and non-index schema object, and
leave malformed/duplicate databases blocked without guessing or data repair.

The task/plan freeze exact May Touch, locks, acceptance, disposable-database API
regressions, and package isolation. TASK_361E is paused and cannot absorb this lane.

## Definition Of Ready

Satisfied for the bounded Developer implementation. Blocking questions: none.
Reviewer plan/readiness gates, user approvals, and docs-only planning-first are
complete. TASK_361E remains paused.

## Validation Summary

- Targeted board diff-check and no-index checks for TASK_361E/F governance documents
  passed with existing LF/CRLF working-copy warnings only.
- UTF-8 trailing-whitespace scan is clean.
- Board/task/plan/evidence status scans confirm TASK_361F is implementation-authorized
  and pending Developer implementation, while TASK_361E remains paused_by_user.
- Targeted product status contains only pre-existing parser/MCR test residuals; this
  Planner pass changed governance documents only.
- No command opened, copied, inspected, or modified `data/connlab.sqlite3` or another
  real database.
- Existing parser/MCR, TASK_360Q/R/S, superpowers, TASK_361E planning files, and all
  other external residuals remain excluded.

## Evidence Paths

- `tasks/TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE.md`
- `docs/task_361f_contact_measurement_schema_compatibility_bootstrap_corrective_plan.md`
- `docs/lane_evidence/TASK_361F_contact-measurement-schema-compatibility-bootstrap-corrective_planner.md`
- `docs/task_board.md`

## Next Legal Role

Developer implementation pass.
