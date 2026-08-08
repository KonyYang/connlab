# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING — Planner Evidence

ROLE: Planner (inline in the permanent Orchestrator conversation)

STATUS: integration_reconciliation_amendment_pending_user_approval

TASK_ID: `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING`

## Identity

- No Planner agent, thread, branch, lane, host, or worktree was created.
- The current permanent Orchestrator conversation
  `019fb3d4-12a5-73b3-be8e-e59686fa39a9` performed the read-only Discovery and plan review.
- Board activation commit: `6227acb7cfccaab276194d2a7cbda96bc1f09a89`.
- Initial Plan commit: `a97b918672c2887baf5324d14bb1ba093674a1a9`.
- Revision-2 Plan ref:
  `docs/task_governance_orchestrator_latency_and_model_routing_plan.md@b70e78d14987a0c8a50400475e19a9e2243be530#27ce7b4cc39c6e0a42ec43828c7afceeff03d63e90e6e88f3a075e86d5d7cdb1`.
- Exact approved-request SHA-256:
  `b3caa75c1cf2678fec1b2d06ced4bb9e551b49e75767aba3564d6f7537b7b19c`.
- Primary HEAD before this evidence commit: `b70e78d14987a0c8a50400475e19a9e2243be530`.
- Board SHA-256 before Planner-ready transitions:
  `59ea9c1133c1843271ae0fd602be3d5e744698ddec4c8f0718e4b2d1342bc23c`.

## Review Findings Resolved

1. Defined the legal inline Planner `planning -> awaiting_user_approval` event path using the existing
   state machine, real current-thread identity, and committed evidence; no agent or synthetic result.
2. Froze exact Submit/Approve/Close entry contracts and executable positive/negative test obligations.
3. Fixed model audit locations at explicit dispatch parameters, fixed role-evidence fields, and the
   Integrator/final `ACTUAL_MODEL_ROUTING` table without changing board schema.
4. Corrected rollback to a separately authorized, parent-verified `git revert -m 1` of the exact merge.
5. Made QA low/medium selection deterministic; this Task routes QA to Terra medium.

No implementation path was edited and User approval remains required.

## Revision 3 Approved-Request Correction

- User approved Revision 2, but the exact `scripts/run_task.ps1 -Action Approve` call returned
  `BLOCKED_APPROVED_SCOPE_INVALID` with identical before/after board SHA-256 and no file change.
- Repository proof: Submit classification uses the ten-key
  `scripts/connlab_serial_complex.py::FORBIDDEN_KEYS`, while Approve validation uses the nine-key
  `scripts/connlab_serial_board.py::FORBIDDEN_KEYS` and rejects `push_or_release`.
- Revision 3 removes only that invalid Approve key, updates the approved-request hash, and adds the
  precise cross-copy negative to the existing bounded test obligation.
- Implementation May Touch, Must Not Touch, model routing, QA route, rollback, WIP, and all product/
  runtime/schema boundaries are unchanged.

The corrected approved payload was passed read-only through
`scripts.connlab_serial_board.approved_payload` before this amendment was committed. A new exact User
approval is required; no host or role may be created before it.

## Bounded Integration Reconciliation Discovery

User-authorized planning-only Discovery confirmed the following immutable facts:

- primary was clean at `82370aeb1690f1a6e1ebda7d37048f5f926d7570` before this three-file
  amendment, with committed board blob SHA-256
  `9083399d2a3a091afc634ab3253df86e8f3c0754fd73558bdc0b959b0c336d88`, physical Windows
  worktree/CAS SHA-256 `295974ff98e874862d2505e8ff05ebab6977d738f74e40a6937bcbe165bc6696`, and exact
  `INTEGRATION_BLOCKED` authority;
- QA subject is `ad7dac819268ae77781709b626aea4f624a7a740`;
- the original lane is clean and immutable at
  `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- `ad7dac81..f7770b6a` is the exact linear Reviewer/QA/Integrator evidence-only range;
- existing merge `093d48966b15c536b7411b3cc4cdca1e1e0d4faf` has exact parents
  `a632f01c...` and `f7770b6a...` and tree `891f0cd2...`;
- `82370aeb...` is the direct first-parent child of that merge and changes only
  `docs/task_board.md` to record the blocker;
- all five existing evidence refs in the board resolve to the exact committed bytes and declared
  SHA-256 values.

The root cause has two independent halves: the normal contract requires lane HEAD equal the QA
subject, and repository proof requires primary HEAD equal the merge. A generic descendant allowance,
two-step resume/record sequence, or another merge would violate the User boundary.

The amendment therefore specifies one task-specific reviewed executor artifact on a new same-task
reconciliation worktree. It preserves the original lane and merge, is not installed/merged/cherry-
picked into primary, and can perform only one exact CAS board transition through the existing sole
writer. The exact future code/test scope is four paths; reconciliation evidence uses four fixed
task-derived paths. Developer, Reviewer, QA, and Integrator route to
`gpt-5.6-sol / medium / risk:integration_conflict` and cannot write the board. Integrator alone may
execute after the full evidence chain is committed and clean.

Success atomically consumes the blocker and records `head_sha=f7770b6a`,
`integrated_commit=093d4896`, `phase=human_review`,
`state=implemented_pending_human_review`, `worktree_lifecycle=integrated`, complete evidence refs,
and `blocker=null`. Every drift is zero-write blocked. Exact replay is a no-op only on complete
committed target proof.

No board, runtime, test, original lane, merge, role evidence, product, remote, or retained resource was
modified during planning. Only the Task, Plan, and this Planner evidence are authorized in the current
turn. The amendment remains pending exact User approval.
