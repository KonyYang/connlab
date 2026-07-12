# TASK_361E Contact Measurement Confirmed Consumer Migration Developer Evidence

Date: 2026-07-12

Role: Developer

Status: developer_planning_first_complete - pending Reviewer implementation-readiness gate. Product implementation is not authorized.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A-D are accepted, with TASK_361D at
local commit `0fa429f53662addfe7fac86a12f73aad836c95fa`. Reviewer plan evidence is
`reviewer_pass`; the user approved this docs-only planning-first pass.

## Refined Strategy

- Use one typed internal confirmed-consumer adapter between the effective confirmed
  projection and Fee/TASK_360B. It owns Group/Row/Step/suffix lineage matching,
  current Matrix sample/display context, effective target facts, omissions, and
  diagnostics. Consumers never parse opaque stable keys or query authority storage.
- Fee changes only LLCR/CR readings source. Under active-root partial/review/empty/
  corrupt states, incompatible or missing eligible targets are review-required with
  no units/testing fee and no legacy/text fallback. Non-contact quantities and all
  pricing/default/export/UI behavior stay unchanged.
- TASK_360B keeps its stable route/client/artifact/layout lifecycle while changing
  only internal confirmed source selection. `complete` is `CONFIRMED`; compatible
  partial/review output is `PARTIAL COMPATIBLE`; no-root/disabled may use the frozen
  legacy adapter, while corrupt/empty active-root output never does.
- TASK_361D editable draft workbooks, routes, artifacts, client, and UI remain
  completely isolated from formal consumers.

## Exact Future Scope

Only task-listed backend adapter/projection, narrow Fee contact-context, formal
workbook source/metadata, dependency, and focused backend/API test paths may change.
No frontend/API client, Fee pricing/rules/default-fill/manual/export/UI, generic Test
Record/Report, schema/repository/lifecycle, Matrix parser/persistence, LTR/public
drive, real files, or external residual cleanup is allowed.

## Validation Plan

Temp SQLite and temp-dir tests cover adapter statuses/identity, Fee no-bypass/sample
multiplier, formal compatible-only/stale/no-output/rollback, and draft isolation.
Regression covers existing TASK_360B, TASK_361D, Fee export, generic Test Record, and
TASK_361B. Build/compile/diff/trailing/line-count/forbidden-scope/no-real-mutation
checks are required.

## Planning-First Validation

- Re-read AGENTS, board, TASK_361E task/plan/Planner/Reviewer evidence, accepted
  TASK_361A-D context, effective projection, Fee contact context, and TASK_360B
  preview service.
- This pass updates only TASK_361E plan/evidence. No product code, tests, schema,
  dependency, API client, or real file changed.
- `git diff --check` on TASK_361E plan/evidence passed and UTF-8 trailing whitespace
  scan was clean. Targeted status shows existing parser/test, TASK_360Q-R-S, board,
  and superpowers entries are external residuals; this pass added only TASK_361E plan
  refinement and Developer evidence.

## Next Role

Reviewer implementation-readiness gate after Planner source-of-truth reconciliation.

## Blocking Summary

No design blocker. The board/task still show planned-only language and require
reconciliation before any implementation authorization.
