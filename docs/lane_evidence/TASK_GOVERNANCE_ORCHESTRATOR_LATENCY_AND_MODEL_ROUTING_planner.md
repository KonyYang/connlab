# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING — Planner Evidence

ROLE: Planner (inline in the permanent Orchestrator conversation)

STATUS: revision_3_contract_correction_ready

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
