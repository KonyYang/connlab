# TASK_363A Accepted-Baseline Reconciliation Evidence

Date: 2026-07-17

Role: Planner

Status: `historical_blocker_resolved / task_362a_r5_head_baseline_accepted`

TASK_ID: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Audited Facts

- Current HEAD and `origin/master` are `ce7e78839b226fd525f104a3309ed20e3fb75f5e`.
- TASK_362A has committed package history in `614f4e5f`, `d4e2410d`, `6790d26d`,
  `9178748c`, `7f4f1b8c`, and `44f2073b`.
- Later HEAD commit `ce7e7883` records `fee_rules_v2026_07_16_r3` in both
  `fee_rules_v2026_07_16.json` and `fee_rule_extensions_v2026_07_16.json`.
- TASK_362A task/Integrator evidence declares r5 accepted behavior, but also describes
  approved closeout changes in the then-current worktree. No committed r5 identity is
  present in the audited HEAD history.
- The current dirty worktree changes only those two seed identities from r3 to r5,
  while the separate dirty active manifest points to the TASK_363A 2026-07-17 r6
  candidate. Dirty worktree presence is not accepted-baseline evidence.
- TASK_363A's reviewed safe-rebase implementation loads immutable prior seeds by the
  saved version id. Without committed r5 identity, an isolated r6 package fails closed.

## Ownership Decision

The exact r5 identity repair belongs to the already approved TASK_362A package owner,
not TASK_363A. This is the narrowest route because TASK_362A's accepted contract,
Reviewer/QA evidence, and Integrator evidence explicitly name r5 as its baseline.
No new business behavior or TASK_363A scope expansion is authorized.

## Legal Package Sequence

1. TASK_362A package owner / Integrator stages only the `version_id` r3-to-r5 hunk in
   the two 2026-07-16 seed files.
2. The baseline repair excludes `active_fee_rule_seed.json`, all TASK_363A 2026-07-17
   seed/matcher/rebase/test files, frontend/Test Points UI, release/dist, TASK_361L,
   and every unrelated worktree residual.
3. Integrator verifies the staged diff, both exact r5 identities, the 2026-07-16
   baseline manifest, loader/source-hash regression, and a clean post-commit HEAD.
4. Only after that commit may TASK_363A return through the Reviewer/QA package-
   isolation re-gates required by its Integrator evidence, then Integrator re-gate.

If the exact two-hunk package cannot be isolated, stop and request User/Planner
approval. Do not absorb broader TASK_362A or TASK_363A residuals.

## Scope Locks

No product seed, matcher, rebase, test, frontend, API client, release/dist, real DB,
or real file was modified by this Planner pass. Nothing was staged, committed, or
pushed. All current residuals remain preserved.

## Next Legal Role

Historical at time of audit: TASK_362A package owner / Integrator accepted-baseline
repair gate.

## Resolution

The exact TASK_362A r5 identity repair was subsequently accepted in local commit
`9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`. This evidence remains the historical
audit trail; it is no longer an active TASK_363A blocker. The current next role is
defined by the later TASK_363A package-boundary reconciliation evidence.
