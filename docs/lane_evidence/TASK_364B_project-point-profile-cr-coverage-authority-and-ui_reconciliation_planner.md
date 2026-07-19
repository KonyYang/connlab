# TASK_364B Final User Acceptance And Package Reconciliation

Date: 2026-07-19

Role: Planner source-of-truth and package-scope reconciliation

Status: `QA package passed / pending Integrator packaging/readiness`

TASK_ID: `TASK_364B_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_AND_UI`

Lane: `project-point-profile-cr-coverage-authority-and-ui`

## Gate Facts

- Developer completed the corrective R1 implementation.
- Reviewer focused implementation acceptance passed.
- QA passed backend/API `46`, frontend `12 files / 91 tests`, py_compile, frontend
  build, scoped diff/trailing/staging scans, and controlled `514x831` browser smoke.
- The user explicitly accepted TASK_364B.
- No Developer, Reviewer, or QA rerun is required before packaging unless Integrator
  finds an actual package-boundary conflict.

## Accepted Behavior

- The LLCR heading remains; there is no separate CR section and no LLCR checkbox column.
- Each category row owns one native labelled CR checkbox; a new row starts selected.
- All selected derives `follow_llcr`; any excluded row derives `custom`.
- Pointer and Space toggle exactly once, Tab reaches the checkbox, Enter follows the
  Chromium native no-op semantic, and disabled busy state performs no action.
- Confirm, Cancel, reload, and existing Point Profile behavior remain unchanged.
- The effective `514x831` viewport has no horizontal overflow or overlap and the fresh
  page console is clean.

## Exact Product Whitelist

Integrator may hunk-stage only:

1. `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`
2. `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
3. `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`
4. `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
5. `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`
6. `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`
7. `frontend/src/contact-measurement-plan.css`, exact TASK_364B R1 hunks only

The files are mixed with broader worktree history where applicable. Integrator must use
hunk-level staging and must not stage any whole mixed file merely because it is listed.

## Governance And Artifact Whitelist

- `tasks/TASK_364B_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_AND_UI.md`
- `docs/task_364b_project_point_profile_cr_coverage_authority_and_ui_plan.md`
- `docs/task_364b_r1_inline_cr_table_corrective_plan.md`
- TASK_364B Planner, Developer, Reviewer, QA, and this reconciliation evidence
- exact TASK_364B `docs/task_board.md` hunks
- `docs/lane_evidence/artifacts/TASK_364B_qa/controlled_514_native_checkbox.png`

The PNG is included under the existing lane-evidence artifact policy as the controlled
user-acceptance proof. No temporary Vite harness, Chrome profile, log, or other QA
runtime artifact is eligible.

## Excluded And Locked

- `ContactMeasurementPlanSummaryCard.tsx` and its test
- backend, API routes, API client, DTO, storage, and confirmed summary authority
- Matrix Group sample totals and Measurement Plan target authority
- Fee, workbook, Generic Test Record/Report, parser/import, and LTR/public drive
- real database, workbook, project folder, or generated file operations
- TASK_363C, TASK_363D, TASK_365A/B/C, and all other dirty residuals
- `.agents/**`, `docs/project_management/**`, release/dist, remote push

## Package Validation

- exact staged whitelist and hunk ownership
- staged diff-check and UTF-8 trailing-whitespace scan
- forbidden-path and forbidden-content scan
- artifact whitelist contains only the controlled PNG
- staging contains no backend/API/client/summary or external lane file
- no real-data/file mutation

## Reconciliation Validation

- Governance UTF-8 trailing-whitespace scan: clean.
- Tracked board and seven scoped frontend candidate diff-check: passed; only existing
  LF/CRLF normalization notices were emitted.
- No-index diff-check for the untracked task/plans/Planner/reconciliation evidence:
  passed with LF/CRLF notices only.
- Historical validation at this checkpoint found TASK_364B user accepted / pending
  Integrator. That direct route is superseded by the package-boundary reconciliation
  below; current status is Integrator blocked pending TASK_364C.
- QA artifact directory contains only
  `controlled_514_native_checkbox.png` (`23435` bytes).
- `ContactMeasurementPlanSummaryCard.tsx` and its test remain modified external files
  and are explicitly excluded from the package whitelist.
- Staging is empty. This pass changed governance docs only and did not access real data
  or modify product/test files.

## Superseding Package-Boundary Reconciliation

Integrator found an actual package conflict after this acceptance record: the seven R1
frontend hunks import CR coverage DTO fields absent from accepted HEAD. The exact
`frontend/src/api/client.ts` candidate is only an 11-addition type hunk, but its matching
backend/API/storage authority remains unaccepted (596 additions and 17 deletions across
eight product files and four focused tests after the authorized schema assertion). The eighth product hunk is the required
one-line `database.py` profile-table exclusion. No commit in repository history provides
that runtime contract.

Path B is selected. TASK_364C is the serial backend/API/storage authority-baseline
package lane. QA later proved that the client hunk cannot typecheck without excluded R1
consumers/fixtures, so it is deferred to TASK_364B. The prior direct-to-Integrator
recommendation remains superseded. TASK_364B stays user accepted but blocked until
TASK_364C is accepted and the client-plus-consumer R1 package passes re-gate.

## Next Legal Role

## TASK_364C Dependency Release And Client Boundary

- TASK_364C is complete/accepted at
  `b34f2c2cbcc3b27266b480d6ff76a604f06be452`; the backend/API authority dependency is
  released.
- Remaining R1 source boundary: seven accepted R1 files/hunks plus exact client +11 and
  exactly one `cr_coverage` fixture line in
  `ContactMeasurementPlanSummaryCard.test.tsx`.
- The seven R1 files total 343 additions / 23 deletions; adding client +11 and the one
  fixture line yields expected source numstat 355 additions / 23 deletions.
- `ContactMeasurementPlanSummaryCard.tsx` and the other current 8/2 test visual hunks
  remain excluded, as do backend, downstream lanes, and external residuals.
- Reviewer must reproduce the hunk whitelist and isolated frontend build/typecheck
  before QA or Integrator routing.

## Reviewer Client-Plus-Consumer Re-Gate Reconciliation

- Reviewer reproduced the exact nine-path hunk isolate from accepted HEAD `b34f2c2c`.
- Source numstat is 355 additions / 23 deletions.
- Focused frontend validation passed 5 files / 61 tests; `npm run build`, including
  `tsc -b`, passed with only the existing Vite chunk-size warning.
- SummaryCard production, Summary visual 8/2 test hunks, backend/API/schema, and external
  residuals remained excluded.

## QA Exact Package Pass Reconciliation

- QA rebuilt the exact nine-path package from accepted TASK_364C HEAD `b34f2c2c`.
- Exact whitelist and source numstat `355/23` passed; client is `11/0`; SummaryCard
  fixture compatibility is exactly `1/0`.
- Focused frontend validation passed 5 files / 61 tests; isolated `npm run build`
  including `tsc -b` passed with only the existing Vite chunk-size warning.
- Controlled 514x831 browser smoke showed the LLCR/native CR checkbox, exactly-once
  pointer toggle, no horizontal overflow, and no console error. Automated Space/Enter
  dispatch remains a non-blocking tooling residual; prior physical-keyboard smoke is
  retained.

Next legal role: Integrator packaging/readiness for TASK_364B only. No new product
implementation or package expansion is authorized.
