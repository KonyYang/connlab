# TASK_365A Planner Evidence

## Status

Superseded by the 2026-07-19 user-acceptance/package-scope reconciliation. TASK_365A
is user accepted and pending Integrator packaging/readiness; no new product work is
authorized.

Plan approved by the user on 2026-07-19 / Developer implementation authorized.

## Discovery Result

- User outcome is explicit: canonical Class IIA MFG phase Condition and 336-hour to
  14-day Fee conversion.
- Existing Matrix extraction loses the second phase because it uses broad limited
  segment collection.
- Existing Fee Class IIA rule already owns `1000/day`; only explicit-day parsing is
  currently supported.
- No API, schema, frontend, seed, authority lifecycle, or real-data change is needed.
- Missing phase data remains Pending; no source fact is invented.

## Boundary Result

TASK_365A is independent from current TASK_364B but shares a dirty worktree with
other accepted/planned Fee work. Implementation therefore requires path and hunk
isolation. TASK_363C/D, TASK_364B, Current Rating page-continuation parsing, and all
external residuals are locked.

## Readiness

The lane has a testable acceptance path, concrete May Touch / Must Not Touch
boundaries, validation and merge gates, and explicit non-goals. User approval is
recorded; Developer implementation may proceed within those boundaries.
