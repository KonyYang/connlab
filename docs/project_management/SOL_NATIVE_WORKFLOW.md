# ConnLab Task Workflow — GPT-6 Astra

Status: normative. This is ConnLab's only task-execution workflow.

The User-selected model is GPT-6 Astra. This file's historical name and the writer's `sol_*` routes,
schemas, mode, and command names remain stable for compatibility; they do not select a model.
The optional [Chinese usage guide](GPT6_ASTRA_USAGE_GUIDE.md) explains this workflow to the User.

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

- final `关闭`: close the completed task, commit the board-only close transition, and run the safe
  `origin/master` publication gate; an unmistakable cancellation closes and commits locally without
  publication;
- an in-scope defect, acceptance finding, or adjustment: run `Revise` and continue the same task;
- a materially unrelated request: keep WIP unless that message also explicitly closes or cancels the
  current task, in which case `CloseAndSubmit` may perform the atomic rollover.

For Micro and Standard tasks, `scope_paths` is an initial navigation aid rather than a frozen file
allowlist: Astra may touch additional files required by the same User-requested behavior when the exact
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
one Astra work unit: compact plan -> implement -> self-review -> targeted Developer checks
-> focused Reviewer -> bounded fix if needed -> one complete QA pass -> integrate -> finish
```

Planning and implementation remain one continuous unit. A bounded finding returns to that unit; it
does not recreate planning, approval, or role state.
The focused review may be a distinct pass by the current agent; record it as such. An independent
review requires an actual separate context. Do not create role agents merely to populate report keys.

### High risk

Use only for database/schema migration, permissions/security, authoritative external mutation,
destructive behavior, broad architecture change, or an unresolved material product decision.

```text
Planner -> Developer -> Reviewer -> QA -> Integrator -> finish
```

Use independent contexts and automatic compact handoffs. A worktree is optional isolation chosen from
actual risk, not a mandatory host. Routine plans still do not require User approval when they stay
inside the request and existing authority.
The independent contexts here are a project requirement for high-risk execution. When the environment
permits delegation, assign bounded roles using its agent tools and pass compact context. A general
skill's same-agent default does not replace this requirement. If independent contexts are unavailable,
report the actual limitation and continue only work that does not depend on the missing check; do not
claim an independent pass occurred. Do not create user-visible tasks for internal role work.

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

## Astra efficiency and evidence

Use a short outcome, relevant context, scope, and observable acceptance criteria. Select implementation
details autonomously. Group related tests into coherent behavior slices; preserve useful failure-before-
fix evidence without requiring one assertion per tool call. Documents and literal edits normally need
diff/link or focused checks, not new test suites. These project-specific choices take precedence over
generic skill preferences while respecting higher-priority instructions and actual permissions.

Choose the final test matrix from the affected dependency paths. Complete it once on the final reviewed
state; new edits or findings justify rerunning affected checks. An unrelated failed test is not a passing
suite: report it separately and substantiate any claim that it predates this task.

Use `scripts/run_tests.ps1` for the current full gate. It excludes `office_integration` from Python tests,
then runs frontend tests and build sequentially. `-Suite Python` and `-Suite Frontend` select a side;
`-Suite Office` explicitly runs installed-Office integration checks when relevant. Narrow public-seam
tests remain appropriate during implementation. Check the actual interpreter before testing; do not
recreate Python environments as a routine model-upgrade step.

Batch independent read-only discovery. Use structured argument lists or a serialized payload file for
complex commands; never hand-compose unescaped JSON in PowerShell. For Git writes, inspect the actual
permission boundary and request the needed access before executing a known-to-fail command.

User updates steer the existing task. Recovery reads current board/Git and useful evidence, rather than
replaying successful transitions. Report outcome, verification, and material remaining work in concise
Chinese. If timing is requested, distinguish tool durations from approximate stage intervals; use existing
timestamps only. Name self-review and independent review accurately.

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
- `close`: record the User decision and return to idle. The public `run_task.ps1` wrapper then creates
  one exact board-only close commit. For `completed` only, it invokes
  `connlab_publish_closed_task.py`; `cancelled` is committed locally and never published.
- `close-and-submit`: when one User message explicitly closes or cancels the current task and requests
  a complete next task, record the old decision and activate the next request in one locked board
  transition. It preserves WIP=1 and fails without writing on identity, request, state, cleanliness,
  or board-hash errors. It does not automatically commit or publish because the next task is active.

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

For a completed terminal Close, publication is a separate fail-closed Git gate after the local close
commit. It requires the expected HEAD on clean `master`, an idle board whose matching `last_closed`
disposition is `completed`, a first-parent diff containing only `docs/task_board.md`, and upstream
`origin/master`. It fetches first, permits only a fast-forward ordinary push, then verifies the
advertised remote SHA with `ls-remote`. It never force-pushes, rebases, resets, stashes, or cleans.
Remote, network, or authentication failure returns a typed blocker while preserving the valid local
close commit; the task remains closed locally and GitHub synchronization remains pending.
