# TASK_363A Source-Of-Truth Reconciliation Evidence

Date: 2026-07-18

Role: Planner

Status: `package_boundary_metadata_corrected / pending_reviewer_metadata_re_gate`

TASK_ID: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Reconciled Gate Facts

- Reviewer plan re-gate passed.
- The user approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness re-gate passed.
- The user explicitly approved product implementation.
- Developer implementation/fix, Reviewer implementation re-gate, and QA are complete.
- TASK_362A r5 baseline repair is accepted at
  `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`.
- Integrator found a later package-boundary contradiction for the production
  `measurement_plan_provider` composition hunk.
- Planner confirmed that exact hunk is authorized. The later count-only correction is
  now pending Reviewer package-boundary metadata re-gate before QA resumes.
- Latest QA found only a physical-line metadata mismatch; product validation remains
  green. The checked-out UTF-8 source fact is corrected to HEAD `1958` -> worktree
  `1960` under the frozen command convention, including blanks.

## Scope Preservation

This package-boundary reconciliation changes governance state only. The frozen exact Temperature and
force alias matrix, sole exact `Mating/Un-mating Force` `50/per sample` exception,
CPA/TPA/Automotive manual path, immutable seed activation/rollback, TASK_361L V2
provenance-aware safe rebase, May Touch list, and all locked paths are unchanged.

No product code, tests, seed, frontend, API client, schema, real database, real file,
stage, commit, or push action belongs to this Planner pass. Existing TASK_362A,
TASK_361L, release/dist, current Test Points UI changes, and other dirty residuals
remain external and excluded.

The accepted r5 identities remain TASK_362A-owned and are not part of TASK_363A.
TASK_363A may include only the audited `backend/api/dependencies.py` hunk inside
`_build_fee_evaluation_pricing_draft_service`: construct one Measurement Plan
adapter, reuse it for automatic defaults, and inject it as
`measurement_plan_provider`. The hunk is `6` additions / `4` deletions, net `+2`,
with corrected physical-line metadata `1958 -> 1960`. No other hunk in that oversized
composition file is authorized; module decomposition is a separate future lane.

## Validation

- Targeted docs diff-check and trailing-whitespace scan.
- Stale-status/count scan for obsolete baseline blocker, whole-file exclusion, and
  `2214 -> 2216` metadata wording.
- Targeted status confirms this pass changes only TASK_363A governance files and the
  exact TASK_363A board state.

## Next Legal Role

Reviewer package-boundary metadata re-gate.
