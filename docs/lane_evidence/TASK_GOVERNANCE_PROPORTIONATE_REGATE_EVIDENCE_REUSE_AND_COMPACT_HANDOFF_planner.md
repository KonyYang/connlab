# TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF Planner Evidence

Status: `planned_pending_user_approval`

Date: 2026-08-01

Role: permanent Planner

Planning base: `4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff`

## Dispatch And Authority Audit

- Permanent Orchestrator formally authorized planning after TASK_368E local Integrator acceptance.
- Primary was reverified clean on `master@4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff`.
- No remote branch contains the planning base/accepted TASK_368E closeout HEAD; push remains
  unauthorized.
- Production `scripts/connlab_execution_gate.ps1 -Intent Inspect` returned `ALLOW_INSPECT`,
  `execution_state=complete`, token owner null, and valid authority digest.
- Board records `Current Active Task: None`, empty queue, null active/paused/Quick Fix/parallel
  records, and no next task activation.
- No file/task with this TASK ID existed before this planning pass.
- No branch/worktree/token/queue/role dispatch was created or acquired.

## Sources Read

- `AGENTS.md`, especially sections 13-20, and the current active board/JSON.
- `.agents/skills/connlab-planner/SKILL.md` and
  `.agents/skills/connlab-lane-orchestrator/SKILL.md`.
- `PLANNER_DISCOVERY_PROTOCOL`, `EXECUTION_WIP_AND_QUICK_FIX_POLICY`,
  `PARALLEL_EXECUTION_MODEL`, `PARALLEL_LANE_OPERATIONS_GUIDE`, and
  `LANE_ORCHESTRATION_PROTOCOL`.
- `TASK_EXECUTION_SKILL`, `TASK_REVIEW_CHECKLIST`, `scripts/run_task.ps1`,
  `scripts/connlab_execution_gate.ps1`, `scripts/connlab_lane_worktree.ps1`, and
  `scripts/archive_completed_markdown.py`.
- Current governance tests for execution gate/recovery, WIP/Quick Fix, worktree, permanent roles,
  and Markdown archive.
- Prior `TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH` task/plan pattern.
- The binding read-only Discovery callback and the observed long-lived Orchestrator context
  truncation reported during Discovery.

## Discovery Classification

### Confirmed by User

- Reviewer re-gate is impact/evidence proportionate after a bounded blocker fix.
- Reuse binds exact commits, paths/dependencies, commands, environment/fixtures, prior pass, and
  committed evidence hash.
- Any unsafe or unknown fact forces full re-gate.
- QA remains an independent final full risk-proportionate safety net.
- Role-local validation sharding does not change WIP ownership.
- Board history, handoffs, reads, callbacks, and commentary must be compact and enforceable.
- Capsule is reference-only; callback is seven fields; silence window is 60 seconds; unchanged wait
  snapshots are suppressed.

### Confirmed by Repository

- WIP/token/worktree/role separation already exists and remains authoritative.
- Execution JSON contains active ownership but no command-evidence reuse manifest.
- Current board is 2465 physical lines / 779616 bytes at planning base, with Git blob
  `c5d8a905036ae61f437a86890ffdcfa8b69b7b4b` and SHA-256
  `cf5708a46c21b4724aa282fcae6153ed57a06033de6a781bbccf9bdaffa15ba1`.
- The board mixes the current JSON/summary with long completed history and stale historical Current
  headings, including `Current Validation Snapshot` content centered on TASK_094.
- Existing task/plan archive does not archive board history.
- Current `run_task.ps1` embeds a full worktree listing and repeated orchestration contract text.
- Existing seven-field callback test omits a strict rejection contract and does not yet assert the
  `BLOCKER` field.
- No current helper validates reusable review evidence, minimal reads, capsule budgets, cadence,
  board summary agreement, or board round-trip migration.

### Planner Inference

- Reviewer evidence must be separate from execution JSON to avoid creating a second execution
  authority or bloating every board transition.
- Direct dependencies must be declared exact inputs; heuristic dependency discovery is unsafe.
- Three focused helpers are preferable to enlarging the execution gate/archive helper.
- Board migration belongs to primary Integrator after lane review/QA, not Developer.
- A 4096-byte capsule and 400-line/65536-byte active-board budget are conservative, executable
  defaults that directly address the measured failure mode without constraining evidence files.

### Not Yet Confirmed

- Explicit User approval.
- Approval/worktree base, role evidence commits, test totals, and migration output hashes.

These are future gate outputs. They do not change scope or acceptance and therefore do not block
formal planning.

## Definition Of Ready Assessment

- Goal, operator effect, non-goals, architecture, exact interfaces, fail-closed triggers, migration,
  rollback, paths, role owners, tests, lane identity, and gates are explicit.
- Current authority is terminal/clean and no shared active owner exists.
- The implementation branch/worktree is deliberately not created before approval. Its exact
  planned identity is fixed; the future approval-governance HEAD must be recorded as base before
  Create.
- The task is ready for User review, not implementation. Status remains
  `planned_pending_user_approval`.

## Planning Risks And Mitigations

- False reuse: opt-in manifest and mandatory stable full-regate reasons.
- Evidence spoof/staleness: committed blob/hash/ancestry validation.
- Split board authority: one JSON authority, generated summary, archive marked historical.
- Critical context omission: exact references and fail-closed full-read fallback.
- Shard ambiguity: one immutable input and deterministic fail-closed aggregate.
- Live board conflict: Integrator-only guarded apply on primary.

## Scope Decision

- Full governance task, not Quick Fix.
- One isolated lane after User approval, WIP=`1`, no parallel exception.
- Exact May Touch/Must Not Touch/Locked Paths and phase ownership are in the task/plan.
- Required gates are Developer, independent Reviewer, mandatory QA, and Integrator.

## Stop Point

Return to User for exact task/plan approval. Do not approve, activate, queue, take a token, create a
branch/worktree, or dispatch implementation.
