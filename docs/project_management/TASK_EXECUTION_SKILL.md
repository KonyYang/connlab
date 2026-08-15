# ConnLab Personal Task Execution

Last Updated: 2026-08-15
Status: normative V2 execution entry

1. Read `AGENTS.md`, `docs/task_board.md`, and any active Task, Plan, and evidence.
2. State the current phase, active task ID, and why the requested action is legal.
3. Inspect with `scripts/connlab_personal_task.py` and respect WIP=1. A new submission while occupied
   is zero-write; after Close, the User submits it again.
4. Use only `scripts/run_task.ps1` for the User-facing `Submit`, `Approve`, and `Close` actions.
5. Route a strict simple task directly in primary. Route every planned/complex task through one
   read-only Planner, explicit User approval, and then Developer -> Reviewer -> QA -> Integrator.
6. Commit each authority transition before the next write-capable action. Modify only approved
   `may_touch` paths and keep the task host at the exact reviewed subject.
7. Run the validation frozen by the approved scope. A blocking finding returns to Developer only
   when its fix remains inside that scope; otherwise stop for the User.
8. After verified local integration, stop at `implemented_pending_human_review`.
9. Only explicit User `关闭` authorizes retained closeout and WIP release.

Detailed payload schemas, role evidence topology, model routing, recovery, and integration gates live
only in `SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`; do not restate or improvise them here. Never push,
destructively clean, resume frozen legacy automation, or start another task automatically.
