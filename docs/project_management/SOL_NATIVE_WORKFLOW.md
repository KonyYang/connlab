# ConnLab Sol-Native Workflow

Status: normative. This is ConnLab's only task-execution workflow.

`AGENTS.md` contains always-loaded rules, `docs/task_board.md` contains compact machine state, and
`scripts/connlab_sol_task.py` is the only board writer. Historical task, Plan, role, and evidence files
do not participate in execution.

## User contract

Normal work starts when the User submits a requirement. After inspecting a completed result, the User
may say `关闭` or report an in-scope defect or adjustment. In-scope feedback resumes the same task
automatically; it does not require closing the task or opening a replacement. Proceed autonomously
through safe in-scope local work. Stop earlier only for:

- material expansion beyond the submitted behavior;
- a product choice with meaningfully different outcomes that current evidence cannot resolve;
- new external, destructive, costly, or irreversible authority;
- an unresolvable dirty-state or identity conflict;
- a repeated failure whose cause cannot be established safely.

Do not ask for routine Plan, role, test-command, bounded-fix, or clean-local-integration approval.
WIP is one; only explicit Close or Cancel releases it. When a task is `ready_for_close`, interpret the
next User message as follows:

- final `关闭` or an unmistakable cancellation: close or cancel the task;
- an in-scope defect, acceptance finding, or adjustment: run `Revise` and continue the same task;
- a materially unrelated request: keep WIP unless that message also explicitly closes or cancels the
  current task, in which case `CloseAndSubmit` may perform the atomic rollover.

For Micro and Standard tasks, `scope_paths` is an initial navigation aid rather than a frozen file
allowlist: Sol may touch additional files required by the same User-requested behavior when the exact
Git diff is reported and review attests `scope_ok`. Material behavior expansion still requires the
User. High-risk tasks retain an exact approved-path allowlist and fail closed on any extra path.

## Choose the lightest safe tier

### Micro

Use for a localized, unambiguous change at an existing seam with no high-risk fact.

```text
inspect relevant seam -> implement -> self-review exact diff -> targeted validation -> finish
```

No formal Plan, role chain, worktree, separate Reviewer, or independent QA. Do not load unrelated
documents or skills.

### Standard

Use for substantive product work without a high-risk fact.

```text
one Sol work unit: compact plan -> implement -> self-review -> targeted Developer checks
-> focused Reviewer -> bounded fix if needed -> one complete QA pass -> integrate -> finish
```

Planning and implementation remain one continuous unit. A bounded finding returns to that unit; it
does not recreate planning, approval, or role state.

### High risk

Use only for database/schema migration, permissions/security, authoritative external mutation,
destructive behavior, broad architecture change, or an unresolved material product decision.

```text
Planner -> Developer -> Reviewer -> QA -> Integrator -> finish
```

Use independent contexts and automatic compact handoffs. A worktree is optional isolation chosen from
actual risk, not a mandatory host. Routine plans still do not require User approval when they stay
inside the request and existing authority.

## Verification responsibilities

- **Developer:** use the smallest affected checks needed for implementation feedback, including TDD
  red/green checks where applicable. For Standard and High-risk tasks, do not pre-run the complete QA
  matrix. After the last code/test change, rerun only affected Developer checks; any later byte change
  invalidates those results.
- **Reviewer:** inspect requirements, exact diff, boundaries, safety, regressions, and Developer
  evidence. Run only finding- or risk-focused checks; do not repeat the full matrix by default.
- **QA:** on the clean reviewed state, run the risk-proportionate complete matrix once. This is the
  single final execution of full tests, build, typecheck, and browser checks selected for the task;
  omit any category that the change cannot affect. Do not manufacture state or edit fixtures/board
  data merely to make checks pass.
- **Integrator:** verify subject, scope, evidence, Git parents/tree, cleanliness, and actual integration.
  Do not rerun Developer/QA's full matrix by default. Stop immediately on a deterministic blocker.

`code-review`, TDD, diagnosis, codebase-design, and browser tools are methods invoked by their real
task trigger. They never create a second workflow.

## Board interface and recovery

Public commands are `Submit`, `Revise`, `Close`, and `CloseAndSubmit` through
`scripts/run_task.ps1`. Internal commands are:

- `inspect`: compact state and next action;
- `submit`: activate task, tier, scope, and starting HEAD;
- `checkpoint`: one meaningful recovery point or typed blocker, only when useful;
- `amend-scope`: for a running High-risk task only, replace an incorrect path manifest with the
  exact committed task diff after explicit User approval. It requires a clean worktree and cannot
  omit an observed file or pre-authorize a future path;
- `finish`: verify the clean exact subject, scope, proportional results, and validation;
- `revise`: on in-scope User feedback, return the same task from `ready_for_close` to `running`,
  invalidate its stale final report, and record a concise revision checkpoint;
- `close`: record the User decision and return to idle.
- `close-and-submit`: when one User message explicitly closes or cancels the current task and requests
  a complete next task, record the old decision and activate the next request in one locked board
  transition. It preserves WIP=1 and fails without writing on identity, request, state, cleanliness,
  or board-hash errors.

Routine callers use the compact structured result and `next_action`; they do not reread this document,
command help, or writer source before each transition. They invoke `Revise` automatically before
editing when feedback stays inside the active task. Use separate `Close` and `Submit` only when the
User supplied them as separate decisions.

Do not persist role begin/callback microstates, duplicate Plans, prompt hashes, model-route prose, or
separate evidence files by default. Git supplies HEAD and changed paths.

After a crash or reconnect, inspect the board, Git status/diff, and last useful checkpoint. Reuse
durable work and continue the next unfinished action. Do not recreate branches, worktrees, roles,
evidence, commits, or tests merely because the conversation restarted.

## Completion

`finish` records the exact subject, changed paths, scope result, proportional review/QA facts, and
concise validation. Report only the outcome, evidence needed to trust it, material caveats, and next
action. At `ready_for_close`, final Close releases WIP; in-scope feedback triggers `Revise` and resumes
execution without another planning or close ceremony.
