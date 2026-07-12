# TASK_361G Contact Measurement Schema CHECK Compatibility Bootstrap Corrective Planner Evidence

Date: 2026-07-13

Role: Planner

Status: implementation authorized; pending Developer implementation. TASK_361E
remains paused_by_user.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361F is complete/accepted at
`983633b7041ca77afb5f80672cfa168fc8b5cb4b`. A later controlled operational smoke
proved a separate missing-CHECK startup blocker while preserving DB hash, size,
mtime, authority row counts, and index state. TASK_361G is unoccupied and is the next
legal TASK_361 sub-number.

## Evidence Read

- AGENTS, board, Planner/orchestration protocols, and TASK_361A-F context.
- TASK_361F accepted commit, task/plan/Reviewer/QA/operational evidence.
- Current authority migration CHECK and index validation order.
- Authority ORM CHECK expressions and focused schema/startup test boundaries.
- Current git status and external residuals.

This Planner pass did not open or modify the real SQLite database.

## Findings

- The new failure is pre-index: missing CHECK names stop the accepted migration before
  TASK_361F index bootstrap.
- Physical CHECK addition requires a SQLite table rebuild, which is explicitly
  forbidden.
- Exact-expression recognition can safely accept equivalent table CHECKs regardless
  name. Completely missing semantics require a separate enforcement mechanism.
- Canonical INSERT/UPDATE guard triggers, created only after exact row preflight and
  revalidated transactionally, provide non-destructive equivalent enforcement.
- The task freezes four canonical `trg_cmp_*_checks_*_v1` objects and exact relevant
  UPDATE columns so implementation cannot broaden write interception.
- Unknown/weaker/stronger CHECKs and wrong canonical triggers must remain fail-closed.

## Planner Decision

Create one backend-storage planned lane. The lane recognizes exact table CHECK
semantics, bootstraps exact guard triggers only when semantics are absent and all rows
are valid, preserves TASK_361F index behavior, and validates both in one atomic
startup migration. It never rebuilds tables or repairs data.

The task/plan freeze exact May Touch, locks, acceptance, temporary startup/API
regressions, and package isolation. TASK_361E remains paused and cannot absorb this
lane.

## Definition Of Ready

Satisfied for the bounded Developer implementation. Blocking questions: none.
Reviewer plan/readiness gates, user approvals, and docs-only planning-first are
complete. TASK_361E remains paused.

## Validation Summary

- Targeted board diff-check and no-index checks for TASK_361E/G governance documents
  passed with existing LF/CRLF working-copy warnings only.
- UTF-8 trailing-whitespace scan is clean.
- Board/task/plan/evidence status scans confirm TASK_361G is implementation-authorized
  and pending Developer implementation, TASK_361F is accepted at `983633b7`, and
  TASK_361E remains paused_by_user.
- Targeted product status contains only pre-existing parser/MCR test residuals; this
  Planner pass changed governance documents only.
- Parser/MCR, TASK_360Q/R/S, superpowers, TASK_361E planning files, operational QA,
  and all other external residuals remain excluded.
- No command in this pass opened or modified `data/connlab.sqlite3`.

## Evidence Paths

- `tasks/TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE.md`
- `docs/task_361g_contact_measurement_schema_check_compatibility_bootstrap_corrective_plan.md`
- `docs/lane_evidence/TASK_361G_contact-measurement-schema-check-compatibility-bootstrap-corrective_planner.md`
- `docs/task_board.md`

## Next Legal Role

Developer implementation pass.
