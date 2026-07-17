# TASK_363A Package-Boundary Metadata Correction Evidence

Date: 2026-07-18

Role: Planner

Status: `package_boundary_metadata_corrected / pending_reviewer_metadata_re_gate`

TASK_ID: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Reason For This Pass

QA passed all product validation but blocked on one governance metadata mismatch.
The task and Planner package-boundary evidence recorded `2214 -> 2216` physical lines,
while the repeatable QA command convention reports accepted HEAD `1958` and worktree
`1960`. This pass corrects only that source fact.

## Frozen Count Command And Convention

Use the checked-out UTF-8 physical-line metric, including blanks under the QA command
convention:

```powershell
git show HEAD:backend/api/dependencies.py | Measure-Object -Line
(Get-Content backend/api/dependencies.py -Encoding UTF8 | Measure-Object -Line).Lines
```

Recorded result:

- accepted HEAD: `1958`
- worktree candidate: `1960`
- delta: `+2`

## Unchanged Package Contract

- Exact diff remains `6` additions / `4` deletions, net `+2`.
- All fragments remain inside `_build_fee_evaluation_pricing_draft_service`.
- Allowed symbols/call sites remain the local `measurement_plan_adapter`, reuse as
  `ConfirmedMatrixFeeDraftService.contact_measurement_adapter`, and injection as
  `FeeEvaluationPricingDraftPersistenceService.measurement_plan_provider`.
- The pre-existing oversized composition-file exception remains narrow and contains
  no business logic.
- Every other `backend/api/dependencies.py` hunk and every external residual remains
  excluded.

## Product Validation Preserved

QA's disposable focused backend/API suite remains `148/148` passed. Missing or
changed Measurement Plan lineage remains typed blocked with zero saved snapshot; a
valid r5-to-r6 safe rebase preserves manual Unit Price while refreshing automatic
Units. No product defect or Developer fix is indicated.

## Scope Locks

No product code, tests, `backend/api/dependencies.py`, seed, frontend/API client,
real database/file, staging, commit, push, or external residual was modified by this
Planner pass.

## Validation

- Governance diff-check passed.
- Targeted trailing-whitespace scan passed.
- Current-source stale-count scan found no remaining `2214 -> 2216` assertion in the
  board, task, plan, Planner, reconciliation, package-boundary, or current QA wording.
- Exact product diff remains `6/4`, net `+2`; staging index remains empty.

## Next Legal Role

Reviewer package-boundary metadata re-gate. If passed, route QA re-gate before
Integrator packaging.
