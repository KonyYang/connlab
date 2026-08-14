# TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT

Status: `planned` / `ready_for_user_approval`

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
2. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
3. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
4. `tests/integration/test_connlab_serial_complex_recovery.py`

Task governance paths:

5. `tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md`
6. `docs/task_governance_nondestructive_evidence_topology_closeout_plan.md`
7. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md`
8. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md`
9. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md`
10. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md`
11. `docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md`
12. `docs/task_board.md`

## Must Not Touch

- Product, frontend, backend, API, database, schema, persistence or business-rule code.
- `scripts/connlab_serial_complex.py` state schema or role chain.
- Any second evidence ownership path, ref lifecycle, manifest, registry, lane or automation framework.
- Model routing, host creation, digest autocorrection, Close performance or board-history maintenance.
- Reset, restore, stash, rebase, cherry-pick, force ref updates, branch/worktree recreation or
  deletion, archive, retire, cleanup or push.

## Acceptance

- Four execution-role evidence files are committed on primary with exact commit/path/raw SHA-256 and
  identity/model audit fields.
- Task branch/worktree HEAD stays at the reviewed subject after every evidence and callback step.
- Evidence commits are absent from task-subject ancestry; verified integration succeeds normally.
- Code-mixed evidence, wrong path/hash/identity/model/subject/action/attempt, parent drift, dirty state,
  worktree drift or unknown commits fail closed with zero board/repository mutation.
- A real temporary-Git end-to-end exercises canonical Submit through human review and proves no
  forbidden recovery operation was used.
- Existing evidence-digest, blocker/resume, approval, complex Close and retained-closeout regressions
  remain green.

