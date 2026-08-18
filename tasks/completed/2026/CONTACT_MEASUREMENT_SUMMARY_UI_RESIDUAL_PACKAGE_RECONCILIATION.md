# Contact Measurement Summary UI Residual Package Reconciliation

Date: 2026-07-22

Status: complete / accepted after Integrator packaging

Task: `CONTACT_MEASUREMENT_SUMMARY_UI_RESIDUAL_PACKAGE_RECONCILIATION`

Lane: `contact-measurement-summary-ui-residual-package-reconciliation`

Implementation authorization: authorized for the exact May Touch below

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none, per `docs/task_board.md`.
- Why allowed: Developer implementation, Reviewer implementation gate, and QA gate passed. This Integrator closeout packages only the approved two-file UI change and lane governance.

## User Goal

Assess and package the two-file Contact Measurement Summary UI residual as an independent UI corrective lane. The residual was explicitly excluded from accepted TASK_364B and must not be silently absorbed into an accepted task.

Exact residual paths:

1. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
2. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`

## Repository Evidence

- TASK_364C is complete/accepted at `b34f2c2cbcc3b27266b480d6ff76a604f06be452` and supplied the backend/API/storage CR coverage baseline. It excluded frontend client/R1/SummaryCard changes.
- TASK_364B is complete/accepted at `9ac410b7c029c294e3b72bb1aaeca2c15c4d4cbd`. Its accepted package included seven R1 frontend paths, the exact `frontend/src/api/client.ts` `+11` CR coverage type hunk, and one SummaryCard test fixture line.
- TASK_364B Integrator evidence and `docs/task_board.md` explicitly excluded SummaryCard production and the visual `8/2` SummaryCard test residual.
- Accepted HEAD exposes `ProjectPointProfileCrCoverage`, `cr_coverage`, `cr_selected`, and `cr_coverage_mode` in `frontend/src/api/client.ts`, so the current SummaryCard residual does not require new backend/API/client DTO work.
- Current residual numstat:
  - `ContactMeasurementPlanSummaryCard.tsx`: `13/2`.
  - `ContactMeasurementPlanSummaryCard.test.tsx`: `8/2`.
- Current UTF-8 physical lines including blanks:
  - `ContactMeasurementPlanSummaryCard.tsx`: `30`.
  - `ContactMeasurementPlanSummaryCard.test.tsx`: `48`.
- Superseded historical checkpoint: the earlier `28` / `43` line-count facts are no longer current.
- Current candidate SHA-256 fingerprints:
  - `ContactMeasurementPlanSummaryCard.tsx`: `3EB8F661CAB3533E7E931AF246B8A9E118716A58C64EB865630AFAB89AE57210`.
  - `ContactMeasurementPlanSummaryCard.test.tsx`: `E7C17B00BD3854998F1CC9F7177B4F0735A6E616901257F7A78A23DD966AF136`.
- Focused frontend test could not run in this worktree because `vitest` is not available on PATH from `node_modules`; future Reviewer/Developer/QA gates must rerun in an environment with frontend dependencies installed.

## Superseded Planning-First Reconciliation

Date: 2026-07-22

- Reviewer plan re-gate: passed.
- User approval: Developer planning-first approved only.
- Developer planning-first: docs-only complete.
- Historical state at that checkpoint: ready for Reviewer implementation-readiness gate.
- Historical authorization at that checkpoint: product implementation was not yet authorized.
- Current candidate numstat remains SummaryCard `13/2` and focused test `8/2`.
- Current line counts and SHA-256 fingerprints are the controlling source facts above.
- Vitest/build remain future implementation environment prerequisites because this worktree currently lacks the `vitest` executable.
- Loading/resolved/null-neutral, no error disambiguation, accessibility, 514px/desktop, browser/build/test, exact May Touch/locks/package isolation, and accepted TASK_364B/TASK_364C boundaries remain unchanged.

## Final Authorization Reconciliation

Date: 2026-07-22

- Reviewer implementation-readiness gate: passed.
- User approval: product implementation explicitly approved.
- Current state: implementation authorized / pending Developer implementation.
- Authorization is limited to:
  1. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
  2. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`
  3. this lane's governance documents and narrow board hunk.
- Current candidate numstat, physical lines, and SHA-256 fingerprints remain the controlling source facts above.
- Loading/resolved/null-neutral unavailable semantics, no fetch-error disambiguation, accepted `cr_coverage` display, accessibility, 514px/desktop no-overflow/no-overlap, console-clean, focused Vitest/build/controlled browser validation, line budget, rollback, hunk isolation, and package whitelist remain frozen.
- Vitest/build/browser require a complete preconfigured frontend environment before implementation can be sent to review.
- Client/model/parent/CSS/backend/API/schema, TASK_364B/TASK_364C accepted baselines, real DB/files, generated artifacts, dependencies, stage/commit/push, and external residuals remain locked.

## Planned UI Contract

- The SummaryCard remains a compact operational Matrix summary card, not a separate editor or modal.
- Header remains `Test points` with the existing `Setup` button; loading only disables the button and does not introduce a new write path.
- This lane consumes only the accepted upstream `summary` / `loading` contract from `useProjectPointProfileSummaryModel`.
- It does not implement, promise, or claim a distinct fetch-failure state. The accepted upstream model currently drops request failures and exposes `summary=null` after loading for both legal absence and fetch failure.
- The `summary=null` UI must use neutral unavailable / not-available wording. It must not claim that authority is empty, confirmed absent, successfully loaded, or failed.
- Loading remains limited to disabling the existing `Setup` button and preserving a stable summary surface.
- The unavailable state does not show target coverage, Matrix revision, workbook preview, or generation controls.
- Confirmed state renders a semantic `dl` summary with exactly these V1 rows:
  - `LLCR`: confirmed Project Point Profile total points per sample.
  - `CR`: confirmed CR coverage summary from accepted TASK_364B client contract:
    - `follow_llcr`: `Same as LLCR · N points / sample`;
    - `custom`: selected category count plus CR points per sample;
    - missing coverage: `Not set`.
  - `IR`: `Not set`.
  - `DWV`: `Not set`.
- The existing category bullet list and visible confirmed revision label are removed from this card to reduce Matrix summary clutter.
- IR/DWV are display-only placeholders for not-yet-owned point profile coverage; this lane does not introduce IR/DWV authority, editing, Fee, or workbook behavior.
- Accessibility: keep `section aria-label="Test points"`, use semantic `dt`/`dd`, and keep the `Setup` button keyboard-accessible.
- Responsive contract: 514px and desktop layouts must avoid horizontal overflow, overlap, clipped text, or a non-clean console.
- Real fetch-error propagation is deferred to a future independent lane. That future lane would need separate user approval because it must touch `useProjectPointProfileSummaryModel` and/or its parent data boundary.

## Exact Future May Touch

Product:

1. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`

Tests:

2. `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`

Governance:

3. `tasks/CONTACT_MEASUREMENT_SUMMARY_UI_RESIDUAL_PACKAGE_RECONCILIATION.md`
4. `docs/contact_measurement_summary_ui_residual_package_reconciliation_plan.md`
5. `docs/lane_evidence/CONTACT_MEASUREMENT_SUMMARY_UI_RESIDUAL_PACKAGE_RECONCILIATION_planner.md`
6. Narrow `docs/task_board.md` status hunk.

## Must Not Touch / Locked Paths

- `frontend/src/api/client.ts`, selectors, model hooks, editor components, setup workspace, CSS, and other Contact Measurement files unless a future Reviewer gate proves an unavoidable build dependency.
- `useProjectPointProfileSummaryModel` and parent data-loading paths; no error channel or model contract change is authorized here.
- TASK_364B/TASK_364C accepted source reopening.
- Fee/default-fill residuals.
- Accepted Spec parser package and TASK_365A/B/C parser code.
- Backend/API/schema/database, Matrix persistence/confirmation, Fee, LTR, release packaging, public-drive or real-file paths.
- Historical governance residuals, TASK_364A/TASK_363D untracked docs, generated artifacts, and all other dirty worktree residuals.
- Stage, commit, push, real DB access, public-drive access, and normal app/browser smoke using operator config.

## Validation Gate

Future implementation must validate:

- Focused frontend test:
  `npm test -- --run ContactMeasurementPlanSummaryCard --watch=false`
- Frontend build:
  `npm run build`
- Browser smoke using a disposable or isolated fixture only:
  - confirmed LLCR and CR rows render correctly;
  - `follow_llcr` and custom CR coverage are distinguishable;
  - loading disables `Setup`;
  - `summary=null` renders neutral unavailable / not-available wording without asserting success or failure;
  - 514px and desktop have no overflow/overlap;
  - console is clean.
- `git diff --check` on the exact May Touch paths.
- UTF-8 trailing whitespace scan.
- Staging-empty and exact scope scan.

## Definition Of Ready

DoR is satisfied for Reviewer plan re-gate:

- User explicitly requested this independent planned-only lane.
- The exact residual paths and accepted TASK_364B/TASK_364C boundary are known.
- Accepted HEAD already contains the CR coverage DTO/client shape needed by the residual.
- The lane is UI-only and can be reviewed without backend/API/schema/database work.

Product implementation is authorized only for the exact May Touch above.

## Integrator Closeout

Date: 2026-07-23

- Developer implementation, Reviewer implementation gate, and QA gate passed.
- Integrator reran the focused SummaryCard plus Matrix parent regression: `2 files / 50 tests passed`.
- `npm run build` passed with the existing Vite chunk-size warning only.
- Accepted candidate hashes are SummaryCard `727D95A7C0BDF404B12C4B5E1E917F0394B9AB6318FB2982D0157CA72843C893` and focused test `1C0710AC49459A3BD5C29DD4C04B215C06AEFADBD42EB7C40711C996E3B8161B`; current physical lines are `30` and `110`.
- The accepted package remains limited to the two SummaryCard paths and this lane's governance. Model, parent, client, CSS, backend, and all external residuals remain excluded.
- The controlled browser fixture and native-button Enter regression are recorded in QA evidence. The in-app browser transport limitation remains non-blocking; no custom keyboard behavior is added.
- Remote push is not performed. This closeout activates no follow-up product lane.

## Next Legal Role

User / Orchestrator task selection. Do not automatically activate Fee/default-fill or future error-propagation work.
