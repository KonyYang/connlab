# TASK_361C Contact Measurement Setup Workspace - QA Evidence

Date: 2026-07-12

Role: QA / Smoke Owner

Task: `TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE`

Lane: `contact-measurement-setup-workspace`

Gate: QA gate

## Scope Read

- Read `AGENTS.md`; current phase remains Phase 11 controlled Project Workbench / Matrix / Approval Package foundation.
- Read `docs/task_board.md`; board names TASK_361C as active and still has older implementation-authorized wording, while latest Reviewer evidence is `reviewer_pass` after B1/B2 fix. QA used latest Reviewer evidence plus actual diff/status as the operative gate source.
- Read `tasks/TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE.md`.
- Read `docs/task_361c_contact_measurement_setup_workspace_plan.md`.
- Read TASK_361C Planner, reconciliation, Developer, and Reviewer evidence:
  - `docs/lane_evidence/TASK_361C_contact-measurement-setup-workspace_planner.md`
  - `docs/lane_evidence/TASK_361C_contact-measurement-setup-workspace_reconciliation_planner.md`
  - `docs/lane_evidence/TASK_361C_contact-measurement-setup-workspace_developer.md`
  - `docs/lane_evidence/TASK_361C_contact-measurement-setup-workspace_reviewer.md`
- Re-read TASK_361B QA/accepted context as upstream authority backend basis.
- Inspected current worktree status and TASK_361C candidate boundaries.

QA did not modify product source, product tests, task board, real user DBs, real project folders, real LTR/workbook files, or public-drive paths. This file is QA evidence only.

## Candidate Package / External Residuals

Observed TASK_361C candidate package includes:

- read-only backend workspace service and additive route/dependency composition;
- focused backend workspace/API tests;
- frontend typed client helpers, route/page, contact-measurement-plan feature files, scoped CSS, Matrix summary integration, and focused tests;
- removal of the old runtime `MatrixContactMeasurementPlanCard` surface.

External residuals visible and excluded from TASK_361C packaging:

- `backend/modules/test_plan/mcr_text_normalizer.py`
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_mcr_text_normalizer.py`
- `tests/unit/test_spec_section_text_extractor.py`
- TASK_360Q/R/S task files and unrelated superpowers plan files
- `docs/task_board.md` governance residual

Forbidden-scope path scan found only those external parser residuals under locked parser paths. TASK_361C diff-context scan hit the expected TASK_360B compatibility row text (`Specialized record workbook`, `Generate workbook`, `Download workbook`) in Matrix UI; this is accepted scope and remains outside the dedicated setup workspace.

## Validation Commands

Backend workspace/projection/API suite:

```powershell
py -m pytest tests/unit/test_contact_measurement_plan_workspace_read_service.py tests/unit/test_contact_measurement_plan_projection_service.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_contact_measurement_plan_workspace_api.py -q
```

Result: `12 passed in 7.10s`.

Frontend focused suite:

```powershell
cd frontend
npm test -- ContactMeasurementSetupWorkspace useContactMeasurementPlanModel contactMeasurementPlanSelectors MatrixEditorWorkspace ContactMeasurementPlanSummaryCard --run
```

Result: `6 files / 60 tests passed`.

Python compile:

```powershell
py -m py_compile backend/application/contact_measurement_plan_workspace_read_service.py backend/api/routes_contact_measurement_plan.py backend/api/dependencies.py
```

Result: passed, exit code `0`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed with the existing Vite chunk-size warning only.

Diff/trailing/line checks:

- `git diff --check -- <TASK_361C candidate files>` passed with LF/CRLF warnings only.
- UTF-8 trailing whitespace scan over candidate paths found no matches.
- Line-count scan: backend read service 221 lines; route module 431 lines; frontend feature files checked were below 328 lines.

## Controlled Temp SQLite / API Smoke

Used disposable `tmp/TASK_361C_qa_runtime` and OS/temp-backed SQLite only. The temp runtime was removed after smoke. No real user project/DB/file path was touched.

Command smoke:

```text
api_smoke_statuses 200 not_started 200 200 200 409 200 200 200
workspace_context Group 1 Low level contact resistance cmv-1
family_edit_reloaded True High Power QA custom-1
stale_reapply_confirm contact_measurement_plan_conflict True confirmed complete
```

Covered:

- typed summary/workspace returns operator-readable Group/Step/Matrix context;
- `Open measurement plan` creates editable revision;
- selected-target PATCH accepts full family payload including custom family;
- successful save reloads fingerprint;
- stale old fingerprint returns typed `409/contact_measurement_plan_conflict`;
- re-apply with refreshed fingerprint succeeds;
- independent `Confirm measurement plan` confirms plan and effective projection becomes `complete`.

## Isolated Browser Smoke

To avoid the already-running localhost `8000/5173` processes and any risk of default real DB use, QA started:

- temp backend: `127.0.0.1:8001` with `CONNLAB_DATA_DIR`, `CONNLAB_PROJECTS_DIR`, `CONNLAB_TEMPLATES_DIR`, and `CONNLAB_DATABASE_PATH` under `tmp/TASK_361C_qa_runtime`;
- temp frontend: `127.0.0.1:5175` using a temporary `tmp` Vite config proxying `/api` to `8001`.

The temporary processes were stopped and temp runtime/config/logs were removed after smoke.

Observed browser results:

- Matrix Editor opened for `P1` and showed compact `Contact Measurement Plan` summary beside Project Schedule.
- Old long editable `MatrixContactMeasurementPlanCard` was absent from the runtime surface.
- TASK_360B controls appeared only as separate Matrix-only compatibility row: `Specialized LLCR/CR record`, `Preview specialized record`, `Generate workbook`.
- `Contact measurement setup` navigated to `/projects/P1/contact-measurement-setup` as a dedicated page, not a modal.
- Initial setup page moved focus to the page heading and showed `Open measurement plan`.
- After opening the plan, workspace showed readable target context: `Group 1`, `Low level contact resistance`, `Step 1`, included status, families, counts, labels, prefixes, and no raw fingerprints.
- Full selected-target family editor was present: include toggles, label, record label, count, prefix, custom add/remove.
- Browser custom-family add/edit/save succeeded; save reloaded the workspace and readings changed from `4` to `5`.
- Stale recovery was reproduced by external temp API PATCH while browser had local dirty edits. Browser save showed alert `Contact measurement plan changed. Reload before continuing.` with explicit `Reload latest`, `Discard local edits`, and `Re-apply saved edits`; local edited values remained visible.
- `Re-apply saved edits` succeeded and showed `Saved edits reapplied to the latest plan.`
- `Confirm measurement plan` confirmed the independent plan. Returning to Matrix showed summary `Confirmed`, coverage `1 / 1 targets`, `LLCR: 6`, `Plan 2`, `Matrix 1`.
- Matrix `Confirm Matrix` stayed a separate disabled Matrix action and was not triggered by plan confirmation.
- Browser console error/warning log after smoke: `[]`.

Narrow viewport residual:

- Attempted to set the in-app browser viewport to `514 x 900`, but the page still reported `window.innerWidth` / document client width as `1366`; viewport override did not take effect in this browser session.
- In-app browser screenshot capture also failed with `Timed out running CDP command "Page.captureScreenshot"`.
- This is recorded as a non-blocking tooling residual. Responsive/narrow behavior remains covered by focused component/CSS tests and source inspection, but QA could not honestly claim a true 514px browser pass in this thread.

## QA Decision

`qa_pass`

Recommended next role/action: Integrator packaging/readiness.

Blocking summary: none.

Residual risk / packaging note: Integrator should isolate the TASK_361C package from visible external MCR/parser and TASK_360Q/R/S residuals. Browser narrow-width screenshot/viewport smoke remains a tooling residual, not an observed product defect.
