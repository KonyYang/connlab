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

## Implementation Pass

Status: developer_implementation_complete - ready for Reviewer implementation gate.

### Implemented Boundary

- Added `ContactMeasurementPlanConfirmedConsumerAdapter`, a backend-only typed
  effective projection join keyed by confirmed Group/Row/Step/normalized suffix.
  It converts the approved confirmed target/family metadata into domain contact-plan
  facts without parsing `cmp-target:v1` in Fee or workbook consumers.
- Extended the existing read-only projection payload only with typed lineage fields
  required by that adapter. It does not change authority storage, lifecycle, commands,
  schema, feature-flag semantics, or any draft workspace behavior.
- Fee now consults the effective confirmed lookup only for the existing LLCR and
  specified-current CR rules. `complete`/partial/review/empty active authority has
  no legacy fallback: omitted or excluded targets become review-required with no
  contact units. `not_started` and `disabled` retain the frozen Confirmed Matrix
  contact-plan path. Current Matrix group sample quantity remains the multiplier.
- TASK_360B preview/generation now consumes the typed effective confirmed projection
  when composed through dependencies. Complete output is confirmed; compatible
  partial output is `PARTIAL COMPATIBLE`; corrupt/empty authority returns blocked or
  empty without an artifact. The existing formal route/client/artifact lifecycle and
  TASK_361D draft workflow remain separate.
- Formal summary metadata now includes confirmed plan revision, sequence, projection
  status, and omission diagnostics. Preview fingerprints include plan revision/status
  and diagnostics in addition to the existing source projection.

### Focused Tests And Verification

- Added adapter unit coverage for explicit lineage lookup and the only two legacy
  rollback states, plus formal effective projection coverage for partial-compatible
  and corrupt authority.
- Added Fee coverage proving an active partial authority omission does not fall back
  to legacy contact readings, and workbook gateway coverage for partial-compatible
  confirmed-plan metadata.
- Focused backend suite:
  `py -m pytest -p no:cacheprovider --basetemp=tmp\task_361e_full ... -q` ->
  `62 passed`, covering projection, adapter, Fee contexts/draft/API/export,
  formal projection/gateway/generation/API, Matrix session, and read-only Test Record
  preview regressions on temporary fixtures.
- `py_compile` passed for all touched backend modules and focused tests. Frontend is
  unchanged, so `npm run build` is not applicable to this backend-only pass.
- `git diff --check` passed with existing LF/CRLF warnings only. No real database,
  real workbook/folder, or formal generation endpoint was invoked; all tests use
  temporary SQLite and temporary artifact directories.

### Scope And Residuals

- No Fee rule/seed/pricing/default-fill/manual/export/UI behavior, frontend/API
  client, TASK_361D draft files, generic Test Record/Report, schema/repository/
  lifecycle, parser, LTR/public-drive, or external residual was modified.
- Existing board/governance, parser/MCR, TASK_360Q-R-S, and superpowers residuals
  remain external. No stage, commit, or push was performed.
