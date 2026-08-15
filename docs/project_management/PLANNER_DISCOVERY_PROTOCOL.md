# ConnLab Personal Planning Protocol

Last Updated: 2026-08-15
Status: normative for planned tasks

For a planned/complex task, the Orchestrator invokes one fresh read-only Planner before creating the
task host. Planning creates no implementation branch or worktree. The Orchestrator owns all durable
Task, Plan, Planner-evidence, and board writes after validating the Planner result.

Use a planned task whenever the request is not eligible for the strict simple-task boundary in
`EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`. Submission into an idle slot enters `running/planning` and
continues to hold the sole active slot. While occupied, another submission stores nothing.

The short plan must state:

- confirmed goal and repository facts;
- exact `may_touch` paths and file count;
- explicit non-goals and forbidden-category results;
- file-level implementation approach;
- targeted validation;
- risks and rollback;
- the requirement for explicit User approval.

Unknown information that materially changes scope, behavior, data/API authority, or validation is
asked in at most three concise questions. Otherwise the Planner makes bounded, stated assumptions.

After approval, use the canonical `Approve` entry in `scripts/run_task.ps1`, exact-stage the board,
make the approval commit, verify primary clean, and only then create/reuse the task host. Any new path
requires stopping for new User approval.
