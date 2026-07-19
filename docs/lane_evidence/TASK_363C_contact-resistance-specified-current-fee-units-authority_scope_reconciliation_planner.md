# TASK_363C B4 Scope Reconciliation - Planner Evidence

Date: 2026-07-19

Role: Planner source-of-truth and scope reconciliation

Status: `superseded_by_persisted_attestation_dependency_decision`

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Trigger And Verified Facts

- Reviewer B3 was completed by the Developer: the two obsolete CR text/legacy fallback
  tests now require typed review and no automatic Unit Price, Units, or Testing Fee
  without structured CR authority. The full focused file passed `77` tests.
- The CR focused unit/API/V2 candidate suite passed `17` tests before the B4
  persistence probe.
- The disposable B4 probe used no real database or files and showed that
  `load_rebase_candidate()` returns `blocked` when confirmed Measurement Plan
  revision/id/fingerprint changes.
- Root cause is the strict `_same_non_rule_lineage()` comparison in
  `backend/application/fee_rule_transition_safe_rebase.py`, which rejects that change
  before prior-default fingerprint, ordered row identity, current defaults, and field
  provenance can be safely revalidated.
- The accepted TASK_361L contract states that a valid V2 whose canonical context or
  defaults changes while source rows remain safely matchable is `rebase_required`;
  malformed, mixed, unsafe, missing, corrupt, stale, or divergent authority is
  `blocked`.

## Superseding Planner Decision

Reviewer proved this policy-only proposal insufficient: no saved prior defaults or
exact target projection exists to validate a genuine CR readings change. Planner
therefore selected option 2 and created planned-only TASK_363D. The policy-only May
Touch and readiness conclusion below are withdrawn and must not authorize work.

## Withdrawn Narrow Policy Contract

This historical proposal would have allowed a Measurement Plan-only change only when:

1. Confirmed Matrix id/revision and fee-rule version are unchanged.
2. Point Profile status/revision/id/fingerprint are unchanged.
3. Old/current Measurement Plan status is the same usable status: `complete`,
   `partial_compatible`, or `needs_review` where the exact CR target is unaffected and
   has no relevant diagnostic.
4. Old/current Measurement Plan revision/id/fingerprint attestations are present.
5. Prior defaults fingerprint and ordered row identities revalidate.
6. Current exact CR authority/default rows remain safely matchable and provenance
   merge is valid.

It is not executable because genuine changed defaults cannot satisfy item 5 without a
persisted historical attestation. TASK_363D now owns that missing boundary. Missing,
corrupt, stale, omitted, excluded, affected, wrong-kind, mixed/divergent, malformed,
unattested, or otherwise unsafe authority remains `blocked` and writes nothing.

## Scope Locks

- TASK_364B and all its frontend/backend/test residuals.
- LLCR and Project Point Profile behavior.
- Fee rules, seeds, pricing, discounts, and public DTO/API client/frontend.
- Measurement Plan schema, lifecycle, commands, targets, and setup UI.
- TASK_361L persistence/token/CAS/consumer production modules in TASK_363C.
- workbooks, Generic Test Record/Report, Matrix parser/import, LTR/public drive,
  real database/files/artifacts, release/dist, and all external dirty residuals.

## Definition Of Ready

Superseded and not ready for execution. Current source of truth is TASK_363C dependency
reconciliation plus planned-only TASK_363D.

## Validation Summary

- Existing reported product validation retained: B3 focused file `77 passed`; CR
  focused unit/API/V2 candidate `17 passed`; py_compile/diff/trailing/physical-line
  checks passed.
- This Planner action modifies governance documents only, does not access real data or
  files, and does not stage, commit, or push.

## Next Legal Role

This policy-only proposal was blocked by Reviewer because V2 lacks persisted prior
defaults/target projection. Current source of truth is the TASK_363D dependency
Discovery evidence. Next legal role: Reviewer plan gate for TASK_363D.
