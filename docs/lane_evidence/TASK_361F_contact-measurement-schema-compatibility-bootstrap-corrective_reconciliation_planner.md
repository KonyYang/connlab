# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective Reconciliation

Date: 2026-07-13

Role: Planner

Status: implementation_authorized; pending Developer implementation. TASK_361E
remains paused_by_user.

## Reconciled Facts

- TASK_361B-D are complete/accepted and remain regression baselines.
- TASK_361F Reviewer plan gate passed with `reviewer_pass`.
- The user approved Developer planning-first.
- Developer completed planning-first as a docs-only refinement and reported no
  design blocker.
- Reviewer implementation-readiness passed with `reviewer_pass`.
- The user explicitly approved source-of-truth reconciliation and the bounded
  Developer implementation.
- The next legal role is Developer implementation within the exact authorized paths.
- TASK_361E remains paused and cannot absorb or proceed from this corrective lane.

## Scope Preserved

The authorized implementation boundary is limited to the existing Contact
Measurement Plan authority SQLite schema migration plus the focused temporary
schema/startup API regression tests named in the task. The authorization covers the
four exact unique semantics, alternate-name equivalent recognition, all missing-key
preflights before DDL, one contained transaction for canonical creation, post-DDL
revalidation, idempotency, partial-failure rollback, concurrency/locked-startup
errors, and `authority_corrupt` blockers.

Real `data/connlab.sqlite3`, every operator database, table/model/repository/lifecycle
redesign, frontend/API client, TASK_361D, paused TASK_361E, Fee/Test Record/Report
semantics, parser/import, LTR/public drive, real files, release/settings, `.agents/**`,
`docs/project_management/**`, remote push, and external residuals remain locked.

## Validation

- Re-read board, task, plan, Planner/Reviewer/Developer evidence, and orchestration
  protocol before reconciliation.
- This reconciliation changes governance documents only. No backend/frontend product
  code, migration implementation, tests, database, API client, or real file is
  changed or accessed.
- Targeted diff-check, UTF-8 trailing-whitespace scan, stale-status scan, and
  product-path status isolation are required before callback.

## Next Role

Developer implementation pass.

## Blockers

None.
