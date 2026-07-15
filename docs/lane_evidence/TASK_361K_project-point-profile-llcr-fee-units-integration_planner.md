# TASK_361K Project Point Profile LLCR Fee Units Integration Planner Evidence

Date: 2026-07-15

Role: Planner

Status: Developer implementation complete / Reviewer implementation gate passed /
pending QA; not Integrator-accepted.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361J is complete/accepted, the board had
no active implementation lane, and the user explicitly requested a separate planning
lane for confirmed Point Profile to LLCR Fee Units integration.

## Confirmed User Outcome

- Project Point Profile is the project-level LLCR default.
- Confirmed `P / 1-4` means `4 readings/sample`.
- LLCR Units must multiply readings/sample by the Fee row's applicable Matrix group
  sample quantity.
- Draft profile data is not authority.
- Target-specific confirmed Measurement Plan precedence and no-double-counting must be
  explicit.
- Missing/corrupt/stale/non-authoritative states are review-required with no fallback.
- No real DB/file access or product implementation is permitted in this pass.

## Repository Evidence

- TASK_361K task/plan/evidence paths were unused; the identifier is available.
- The active board records TASK_361J complete/accepted and no implementation lane.
- The Fee seed maps `Contact Resistance (Low Level)` to `fee_rule_llcr`,
  `per_reading`, and unit `reading`.
- `build_reading_result()` computes current Units as Matrix group sample quantity times
  readings/specimen. Existing tests prove `5 x 6 = 30`.
- Missing readings currently produces `Enter readings/specimen`, matching the supplied
  real read-only smoke.
- Reviewer read-only inspection confirmed that current
  `build_step_quantity_contexts()` emits `Confirm Matrix Step quantity` before default
  fill when a parsed token has no `ConfirmedMatrixStepQuantity`; a late profile
  fallback would therefore fail the intended no-Step-quantity case.
- TASK_361E currently gives exact included effective Measurement Plan targets
  precedence and blocks fallback for active-root omissions/exclusions/corruption.
- Point Profile read storage already has active confirmed revision, revision sequence,
  fingerprint, canonical expression-derived count, and draft/confirmed separation.
- No Fee composition currently reads the Point Profile.

## Planner Decision

Create one backend-only planned lane. Add a typed confirmed Point Profile consumer
adapter and compose it into all production Fee draft builders. For LLCR only, exact
target-specific confirmed Measurement Plan values remain higher-priority; the project
profile is used only when Measurement Plan is not-started/disabled. Active-root
omissions and every unusable profile state remain review-required. CR and non-LLCR
rows are unchanged.

Reviewer B1 resolution: under Measurement Plan `not_started`/`disabled`, LLCR alone
builds a matched profile context directly from each parsed Confirmed Matrix LLCR
token/line. It does not read, require, or fall back to
`ConfirmedMatrixStepQuantity`/legacy Step contact quantities, so their absence cannot
emit `Confirm Matrix Step quantity`. The current Confirmed Matrix group sample
quantity remains mandatory. Active-root omission/exclusion/affected/corrupt states
are resolved first and remain typed blockers with no profile fallback. CR
specified-current and non-LLCR context construction are unchanged.

The frozen formula is:

```text
units = confirmed_profile_readings_per_sample * confirmed_matrix_group_sample_quantity
```

Selected source lineage must reach existing Fee field metadata with profile revision
id/sequence/fingerprint. No API-client or frontend change is required.

## Scope And Safety

Future May Touch is limited to a new read-only adapter, narrow Fee quantity selection/
context, dependency/export-child/rebase composition, focused temporary tests, and
TASK_361K governance. Point Profile schema/parser/editor/lifecycle, Measurement Plan
authority semantics, Fee rules/pricing/UI/manual edits, workbooks, generic outputs,
Matrix parser/import, LTR/public drive, real DB/files, `.agents/**`, and
`docs/project_management/**` remain locked.

The existing working-tree TASK_361F operational evidence and TASK_361H image artifacts
are external residuals and must not enter the future TASK_361K package.

## Definition Of Ready

Satisfied for bounded implementation. Formula, LLCR-only no-Step-quantity construction,
source precedence, no-fallback states, lineage, production composition points, file
ownership, acceptance, disposable validation, and explicit non-goals are concrete.
No blocker question remains. User implementation approval is recorded.

## Validation Performed

- Re-read AGENTS, board, Planner/orchestration/parallel protocols, ROLE registry,
  TASK_351/357D/361E/361I/J facts, Fee draft/default-fill/quantity composition code,
  Point Profile read/repository facts, focused unit/integration tests, and git status.
- Confirmed TASK_361K identifier/path availability.
- Resolved Reviewer B1 by freezing disposable regressions for: usable confirmed
  profile with `not_started` and `disabled` Measurement Plan plus no Step quantity;
  invalid group sample quantity review/no-write; and active-root omission with no
  profile/text/legacy fallback.
- Confirmed existing product residuals are unrelated and no real DB/file was accessed.
- Planner pass changes governance docs only; no backend/frontend/schema/test/API-client
  implementation, staging, commit, or push occurred.

## Source-Of-Truth Reconciliation

- Reviewer initial plan gate blocked on B1; Planner fixed the written contract.
- Reviewer plan re-gate passed and closed B1.
- User approved Developer planning-first only.
- Developer completed planning-first as docs-only and recorded no product, test,
  schema, API-client, real DB/file, stage, commit, or push action.
- Board/task/plan/evidence are now aligned to Reviewer implementation-readiness next.
- Reviewer implementation-readiness initially blocked on metadata source propagation;
  Developer completed the docs-only planning fix.
- Reviewer implementation-readiness re-gate passed.
- User explicitly approved TASK_361K product implementation.
- Final authorization is limited to the reviewed LLCR consumer integration,
  homogeneous source/lineage propagation, production composition, and disposable
  tests. All existing locked paths remain locked.
- Developer completed the authorized implementation and recorded `94 passed` across
  the focused disposable backend suite.
- Reviewer reviewed the actual diff and passed the implementation gate with no product
  blocker.
- Current state is pending QA; no complete/accepted claim is made.

## Next Legal Role

QA gate.
