# TASK_363A Package-Boundary Reconciliation Evidence

Date: 2026-07-18

Role: Planner

Status: `package_boundary_metadata_corrected / pending_reviewer_metadata_re_gate`

TASK_ID: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_363A completed implementation and bounded
fixes plus earlier Reviewer and QA package-isolation re-gates. Integrator stopped
because the production Measurement Plan provider wiring was authorized in the task
and plan but excluded as a whole file by QA evidence. This pass resolves only that
package boundary. No product implementation or package action is authorized here.

## Audited Facts

- The immutable TASK_362A r5 baseline is accepted at
  `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`; the prior baseline blocker is closed.
- `backend/api/dependencies.py` has one logical candidate composition change inside
  `_build_fee_evaluation_pricing_draft_service`, represented as three zero-context
  fragments (two default-context diff hunks).
- The pricing-draft persistence service already accepts `measurement_plan_provider`
  and uses it to build authority lineage. Production composition must supply it so a
  changed effective Measurement Plan fails closed.
- The hunk has `6` additions and `4` deletions, net `+2`. The checked-out UTF-8
  physical-line metric, including blanks under the QA command convention, is HEAD
  `1958` -> worktree `1960`.
- The staging index is empty. No TASK_363A commit or remote push occurred.

## Package Decision

The logical change belongs to the already authorized TASK_363A production wiring. Freeze the
following exact whitelist:

1. File: `backend/api/dependencies.py`.
2. Function: `_build_fee_evaluation_pricing_draft_service` only.
3. Construct local `measurement_plan_adapter` with
   `_confirmed_contact_measurement_consumer_adapter(session, get_settings())`.
4. Reuse that local for
   `ConfirmedMatrixFeeDraftService(contact_measurement_adapter=...)`.
5. Inject that same local through
   `FeeEvaluationPricingDraftPersistenceService(measurement_plan_provider=...)`.

No import, branch, validation, transformation, persistence operation, authority rule,
or other function may change. Any additional hunk in this file is out of scope.

## Oversized Composition Exception

`backend/api/dependencies.py` is a pre-existing oversized dependency-composition
root. The audited net `+2` wiring change contains no business logic and is required at
the production call site. Creating a separate helper would expand the package and
would not eliminate this call-site wiring. This narrow composition exception does not waive the
project line limit generally; decomposing the composition root is a separate future
lane.

## QA Isolation Correction

The earlier QA statement excluding the whole file is superseded. QA/Integrator may
stage the exact hunk above. They must continue excluding every other
`backend/api/dependencies.py` hunk/content, TASK_362A/TASK_361L/LTR/frontend/release
residual, accepted r5 seed pair, real DB/file path, and unrelated board hunk.

## Scope Locks

The alias/default/rebase business contract and existing Reviewer/QA product results
are unchanged. This pass does not modify product code, tests, frontend/API client,
seed, real database/file, stage, commit, or push state. It does not start another
lane or authorize broader composition refactoring.

## Validation

- Audited `git diff --unified=0 -- backend/api/dependencies.py` and confirmed three
  exact fragments under one function (`git diff` default context presents two hunks).
- Audited `git diff --numstat -- backend/api/dependencies.py`: `6 4`.
- Counted checked-out UTF-8 physical lines, including blanks under the frozen QA
  convention, with:
  `git show HEAD:backend/api/dependencies.py | Measure-Object -Line` and
  `(Get-Content backend/api/dependencies.py -Encoding UTF8 | Measure-Object -Line).Lines`.
  Result: HEAD `1958` -> worktree `1960`.
- Ran targeted governance diff-check, trailing-whitespace, stale-status, and status
  scans after reconciliation.

## Next Legal Role

Reviewer package-boundary metadata re-gate. After Reviewer pass, QA must rerun the
hunk-level package gate before Integrator packaging. Integrator acceptance remains
pending.
