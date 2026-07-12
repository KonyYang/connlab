# TASK_361G Contact Measurement Schema CHECK Compatibility Bootstrap Reconciliation

Date: 2026-07-13

Role: Planner

Status: implementation_authorized; pending Developer implementation. TASK_361E
remains paused_by_user.

## Reconciled Facts

- TASK_361F is complete/accepted at local commit `983633b7`.
- TASK_361G Reviewer plan gate passed with `reviewer_pass`.
- The user approved Developer planning-first, and Developer completed that pass as
  docs-only.
- Reviewer implementation-readiness passed with `reviewer_pass`.
- The user explicitly approved source-of-truth reconciliation and the bounded
  Developer implementation.
- The next legal role is Developer implementation within the exact authorized paths.
- TASK_361E remains paused and cannot absorb this corrective or resume from this gate.

## Authorized Implementation Boundary

Developer may implement only exact canonical trigger SQL, exact CHECK-equivalence
recognition, invalid-row preflight, atomic ordering with the accepted TASK_361F index
bootstrap, rollback/lock/idempotency behavior, and the temporary fixture/startup
regressions named by the task.

No real/operator database, API/client, unrelated product behavior, or real file may
be changed or accessed. Real `data/connlab.sqlite3`, Cancel DELETE, Test Record
generation, real `.docx`, table rebuild/data repair, TASK_361D/E, frontend/client,
Fee/Test Record/Report/formal workbook semantics, parser, LTR/public drive,
release/settings, `.agents/**`, `docs/project_management/**`, remote push, and
external residuals remain locked.

## Validation

- Re-read board, task, plan, Reviewer evidence, and orchestration protocol before
  reconciliation.
- This reconciliation changes governance documents only.
- Targeted board diff-check and no-index checks for TASK_361G governance documents
  passed with existing LF/CRLF working-copy warnings only.
- UTF-8 trailing-whitespace scan is clean.
- TASK_361G status scan confirms Reviewer plan/readiness passes, docs-only planning
  completion, user implementation approval, and implementation_authorized status.
- Targeted product status contains only pre-existing parser/MCR test residuals; no
  product/schema/test/API-client file changed in this Planner pass.
- No command opened, copied, or modified a real/operator database or generated a real
  Test Record file.

## Next Role

Developer implementation pass.

## Blockers

None.
