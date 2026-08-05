# ConnLab Personal Planning Protocol

Last Updated: 2026-08-06
Status: normative for planned tasks

Planning is performed in the current conversation. No Planner role conversation, lane, worktree,
or dispatch is created.

Use a planned task whenever the request is not eligible for the strict simple-task boundary in
`EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`. A queued planned intake stores only task ID, summary, and
kind. When activated it enters `running/planning` and continues to hold the sole active slot.

The short plan must state:

- confirmed goal and repository facts;
- exact `may_touch` paths and file count;
- explicit non-goals and forbidden-category results;
- file-level implementation approach;
- targeted validation;
- risks and rollback;
- the requirement for explicit User approval.

Unknown information that materially changes scope, behavior, data/API authority, or validation is
asked in at most three concise questions. Otherwise the current conversation makes bounded,
stated assumptions.

After approval, call `approve --approved-request-json` through
`scripts/connlab_personal_task.py`, exact-stage the board, make the approval commit, verify primary
clean, and only then implement. Any new path requires stopping for new User approval.
