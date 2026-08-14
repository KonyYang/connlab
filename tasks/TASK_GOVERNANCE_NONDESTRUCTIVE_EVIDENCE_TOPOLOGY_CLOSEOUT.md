# TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT

Status: `blocked` / `bounded_scope_amendment_pending_user_approval`

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

Make complex-role evidence durable without advancing the task branch/worktree beyond the exact
Developer subject. The normal Developer -> Reviewer -> QA -> Integrator chain must reach verified
integration without branch-pointer repair or destructive Git recovery.

## Confirmed Repository Facts

- `record-integration` correctly requires `branch_head == subject_commit` and a clean registered task
  worktree at that HEAD.
- The current temporary-repository happy-path fixture already commits role evidence on primary while
  the task branch remains at the subject, but the production skill/protocol does not make that
  ownership rule normative or fail closed around it.
- Evidence refs already bind repository path, commit and raw SHA-256; callbacks and integration store
  the accepted ordered refs in the board.
- `scripts/connlab_serial_complex.py` is a pure transition/schema module and needs no change.

## Selected Evidence Ownership Model

Use one model only: **primary sequential evidence-only commits**, interleaved with the existing
board-only authority commits. Do not create an evidence worktree, retained evidence ref, registry,
manifest, lifecycle, role, approval stage or writer command.

For each execution role, primary advances as:

```text
begin-role board commit
-> record-invocation board commit
-> exact one-path role evidence commit
-> consume-callback board commit
```

The task branch/worktree remains clean at the exact implementation subject throughout Reviewer, QA,
Integrator, evidence persistence and integration.

## Exact May Touch

Implementation/protocol/test paths:

1. `scripts/connlab_personal_task.py`
2. `scripts/connlab_serial_evidence_topology.py`
3. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
4. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
5. `tests/integration/test_connlab_nondestructive_evidence_topology.py`
6. `tests/integration/test_connlab_serial_complex_recovery.py`
7. `tests/unit/test_connlab_serial_complex_orchestrator_contract.py`

Task governance paths:

8. `tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md`
9. `docs/task_governance_nondestructive_evidence_topology_closeout_plan.md`
10. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md`
11. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md`
12. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md`
13. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md`
14. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md`
15. `docs/task_board.md`

The two added test paths are fixture-only exceptions. The recovery fixture must replace its
uncommitted sentinel Plan with a real committed Plan without adding a production bypass. The unit
fixture must resolve the real primary rather than treating its linked task worktree as primary.
Neither edit may change production behavior or broaden the verifier. The new verifier module targets
at most 300 lines and has a hard limit of 500;
`connlab_personal_task.py` must remain at or below 500 lines. The new integration test must remain at
or below 500 lines.

## Must Not Touch

- Product, frontend, backend, API, database, schema, persistence or business-rule code.
- `scripts/connlab_serial_complex.py` state schema or role chain.
- Any second evidence ownership path, ref lifecycle, manifest, registry, lane or automation framework.
- Model routing, host creation, digest autocorrection, Close performance or board-history maintenance.
- Reset, restore, stash, rebase, cherry-pick, force ref updates, branch/worktree recreation or
  deletion, archive, retire, cleanup or push.

## Acceptance

- Planner evidence remains the committed prefix. Every later callback evidence, including bounded
  fix-loop evidence, is committed on primary and dynamically matched in board order to its durable
  invocation; no role count or evidence-count allowlist is permitted.
- Every evidence has exact commit/path/raw SHA-256 and identity/model audit fields.
- Task branch/worktree HEAD stays at the reviewed subject after every evidence and callback step.
- Evidence commits are absent from task-subject ancestry; verified integration succeeds normally.
- Code-mixed evidence, wrong path/hash/identity/model/subject/action/attempt, parent drift, dirty state,
  worktree drift or unknown commits fail closed with zero board/repository mutation.
- A real temporary-Git end-to-end exercises canonical Submit through human review and proves no
  forbidden recovery operation was used.
- Existing evidence-digest, blocker/resume, approval, complex Close and retained-closeout regressions
  remain green.
