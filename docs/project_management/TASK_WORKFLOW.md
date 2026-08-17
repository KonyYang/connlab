# ConnLab Sol-Native Task Workflow

Status: normative

This is the only task-execution workflow for ConnLab. Product and architecture rules live in
`AGENTS.md`; machine state lives in `docs/task_board.md`; `scripts/connlab_sol_task.py` is the only
board writer.

## User contract

Normal work has two User interactions:

1. submit the requirement;
2. inspect the completed result and say `关闭`.

Do not ask the User to approve a routine plan, role handoff, bounded technical fix, test command, or
clean local integration. Ask only when the requested scope must expand, a material product choice
cannot be inferred, new authority is required, or an irreversible/destructive action was not already
explicitly authorized.

WIP is one. A second submission while a task is active changes nothing. Only explicit Close or Cancel
releases the active slot.

## Three task tiers

Choose the least ceremonial tier that safely fits the real change. GPT-5.6 Sol may raise a tier when
inspection reveals risk; it must not downgrade a known high-risk fact.

### Micro

Use for a localized, unambiguous change with a clear existing seam and no database, authority,
security, destructive, external-mutation, or broad architecture risk.

```text
Sol implement -> self-review -> targeted validation -> ready for Close
```

Do not create a role chain, task host, formal Plan, separate Reviewer, or independent QA. Do not load
unrelated architecture or design material.

### Standard

Use by default for substantive product work that does not contain a high-risk fact.

```text
one Sol work unit: compact plan -> implement -> self-review -> complete Developer validation
-> independent Reviewer -> bounded fix if needed -> independent QA once
-> clean local integration -> ready for Close
```

Planning and development remain one continuous work unit. Reviewer checks both requirement fit and the
exact diff. QA runs the complete approved validation once; Reviewer uses only risk/finding-focused
checks. A bounded finding returns to the same Sol work unit without recreating planning or role state.

### High risk

Use when work includes database/schema migration, permissions or security, authoritative/public-drive
mutation, irreversible/destructive behavior, a broad architecture change, or a product decision that
cannot be inferred safely.

```text
Planner -> Developer -> Reviewer -> QA -> Integrator -> ready for Close
```

Use independent role contexts, but keep handoffs automatic. A plan does not need routine User approval
when it stays within the submitted requirement and the original request already grants the needed
authority. Stop for the User only on the exceptions in the User contract.

## Durable interface

Use `scripts/run_task.ps1` for User-facing Submit and Close. Use the new writer directly for internal
recovery checkpoints and final recording:

- `inspect`: return the compact active snapshot and next action;
- `submit`: activate one task and record its tier, scope, and starting HEAD;
- `checkpoint`: optionally persist one meaningful recovery point or typed blocker;
- `finish`: verify exact clean subject, changed paths, proportional role results, and validation;
- `close`: record the User decision and return to idle.

Do not persist role begin/invocation/callback microstates. A checkpoint is useful only when it prevents
meaningful work from being repeated after interruption.

The writer accepts three compact JSON payloads. Their exact field sets are:

- request: `schema`, `version`, `task_id`, `summary`, `tier`, `scope`, `scope_paths`, `risk_reasons`;
- checkpoint: `schema`, `version`, `task_id`, `stage`, `status`, `summary`, `requires_user`;
- report: `schema`, `version`, `task_id`, `subject`, `summary`, `scope_ok`, `changed_paths`,
  `validation`, `roles`, `integration`.

Use schema names `connlab.sol-task-request`, `connlab.sol-task-checkpoint`, and
`connlab.sol-task-report`, all at version `1`. Do not inspect retired writers to construct payloads.

## Scope and safety

- Treat the submitted requirement as the behavioral scope. Optional `scope_paths` tighten it; they do
  not authorize behavior outside the request.
- Preserve unrelated User changes. Do not silently restore, reset, stash, clean, delete, rebase, push,
  or overwrite external data.
- Derive HEAD and changed paths from Git. Do not hand-copy hashes into prose.
- Keep primary clean at Submit, Finish, and Close. Use an isolated worktree only when the selected
  high-risk work benefits from it; a worktree is not a mandatory role host.
- After reconnecting, inspect the compact board and Git diff, then continue the unfinished work. Do not
  recreate completed work merely because a conversation ended.

## Skills and model use

Use GPT-5.6 Sol for planning, implementation, review, recovery, and integration. Let the model choose
reasoning effort from the actual task.

Supporting skills are methods, not workflow gates. Invoke them when their normal trigger applies:
TDD for substantive behavior with a practical seam, code review for a meaningful diff, diagnosis for
hard unexplained failures, codebase design for structural seams, and browser/UI tools for observable UI
behavior. Do not load a skill solely because a file lives in a frontend or backend directory.

## Completion report

Report the requested result, exact changed paths, validation, review findings, and any residual risk.
Do not paste full test output, board JSON, model-routing tables, or duplicated Plan content. Stop at
`ready_for_close`; only the User's final Close releases WIP.
