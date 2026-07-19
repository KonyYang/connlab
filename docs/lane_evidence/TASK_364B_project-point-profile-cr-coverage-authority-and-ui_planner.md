# TASK_364B Planner Evidence

## Status

`user accepted / Integrator blocked pending TASK_364C authority baseline`

Initial plan and corrective R1 are implemented. Focused Reviewer acceptance and QA
passed, including controlled native-checkbox behavior at `514x831`; the user explicitly
accepted TASK_364B. Integrator then found that the R1 package is not self-contained
against accepted HEAD because the CR coverage authority/API/client baseline remains
unaccepted.

## Current Package-Boundary Status (2026-07-19)

Planned-only TASK_364C must establish the missing baseline through Reviewer/QA/
Integrator package gates before TASK_364B returns to package re-gate. The prior direct
Integrator route is superseded. No product implementation, staging, or commit is
authorized by this status update.

## Current Phase / Active Task / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- Board action: TASK_364B packaging/readiness only; no new product lane is active.
- TASK_364B remains separate from accepted TASK_363C/D/365C and pending TASK_365A/B.
- This pass changed governance files only. No product, schema, API, frontend, test,
  real database, or external artifact was modified.

## Initial User-Confirmed Facts (Superseded Where R1 Conflicts)

- CR selection is project-wide, not per Matrix group.
- Different groups only change totals through their sample quantities downstream.
- CR custom coverage selects complete categories only.
- CR follows LLCR by default and diverges only through Customize CR.
- HP/LP are examples, not built-in or universal rules.

## Repository Evidence

- Point Profile revisions already contain ordered category snapshots with stable
  `ppc-N` identities, exact expressions, prefixes, and counts.
- Direct Confirm is the accepted atomic authority boundary.
- Workspace/summary and typed frontend Point Profile boundaries already exist.
- Current schema bootstrap is dedicated, transactional, additive, and fail-closed.
- Current Measurement Plan CR/LLCR target concepts do not satisfy the requested
  project-wide whole-category policy and remain locked.

## Initial Planning Result (Superseded Where R1 Conflicts)

- One additive selection snapshot table; absence means follow, presence means custom.
- Per-row command selection supports new categories without label matching or a
  preliminary save.
- New V3 fingerprints cover mode and stable selected ids; old fingerprints remain
  opaque.
- One inline CR section in the existing Point Profile card and one concise confirmed
  CR line in Matrix summary.
- Matrix-group totals and every downstream consumer are deferred.

## Initial Discovery Classification

- User-confirmed goal: complete.
- Repository facts: confirmed from current models, migration, repository, lifecycle,
  read/API, client, model, editor, and summary files.
- Planner inference: new categories start unselected after custom mode is active;
  documented as a non-blocking assumption.
- Blocking questions: none for the authority/UI task.

## Initial Next Gate (Completed)

Developer implements TASK_364B only, using TDD and the approved May Touch/locked-path
contract. The user approval phrase was `批准 TASK_364B 实施`.

## R1 User Acceptance Corrective

### Confirmed By User

- Keep the top LLCR heading and points/sample summary.
- Main table columns are `Point category`, `Range`, and `CR`, plus the existing action
  column; no LLCR checkbox column is displayed.
- Remove the separate CR coverage section and its mode buttons.
- New categories start selected for CR.
- Every category selected normalizes to `follow_llcr`; any excluded category means
  `custom`.

### Repository Reconciliation

- The accepted backend/API contract already supports this behavior; no schema,
  fingerprint, route, client DTO, or summary change is needed.
- The current frontend keeps explicit mode state and a duplicated CR section. R1 can
  replace that state with a pure row-derived mode and move existing row booleans into
  the table.
- This is frontend-only and disjoint from the now accepted TASK_363B package.

### R1 Handoff (Completed)

- Developer completed the inline CR table, checked-by-default new row, and row-derived
  follow/custom mode without changing the accepted backend/API/summary contract.
- Automated frontend regression passed `91/91`; production build passed.
- Reviewer/QA repeated the responsive check at an effective `514x831` viewport. Pointer
  and Space toggled exactly once, Tab reached the native checkbox, Enter followed the
  Chromium no-op semantic, busy state blocked action, layout did not overflow, and the
  fresh page console was clean.

### R1 Scope And Gate

- Exact frontend May Touch, TDD order, responsive criteria, and locked paths are in
  `docs/task_364b_r1_inline_cr_table_corrective_plan.md`.
- No product file was changed during R1 planning.
- Historical R1 status: Reviewer/QA/user acceptance complete. The former direct
  Integrator route is superseded by TASK_364C package-boundary review.
