# TASK_361D Contact Measurement Draft Workbook Developer Evidence

Date: 2026-07-12

Role: Developer

Status: ready_for_review - implementation complete pending Reviewer implementation gate.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A/B/C are accepted and TASK_361C is
recorded as accepted in local commit `5d754bb1`. Reviewer plan evidence is
`reviewer_pass`; the user explicitly approved this Developer planning-first pass.
This pass modifies only TASK_361D plan/evidence and does not authorize product work.

## Source-of-Truth Note

The current board and task text still say `planned-only; pending Reviewer plan gate`,
which is stale relative to the Reviewer evidence and user approval supplied for this
pass. I did not modify governance outside the user-authorized plan/evidence paths.
Planner reconciliation is required before any later implementation authorization.

## Refined Implementation Strategy

- Source only the current editable TASK_361B revision and its persisted targets,
  families, Matrix binding, fingerprint, and impacts. No confirmed-plan or Confirmed
  Matrix fallback is permitted.
- Classify projection as `ready`, `review_required`, `blocked`, or `empty` before any
  artifact reservation. `ready` labels output `DRAFT`; structurally-valid
  `review_required` labels it `NEEDS REVIEW`. `blocked` and `empty` have no preview
  fingerprint and cannot write.
- Preview and generation share a canonical, versioned serializer. Generation
  recomputes it and rejects an unequal fingerprint with typed stale `409` before
  creating output files.
- Reuse only pure TASK_360B contact expansion and macro-free `openpyxl` layout
  primitives. Keep confirmed lookup, routes, artifact store, client, filename, and
  Matrix compatibility behavior unchanged.
- Create a separate, contained draft artifact root with owned `.xlsx`/JSON-manifest
  pairs, atomic publication, strict project/artifact download resolution, latest
  pointer, ten-pair retention, and unknown-file-safe cleanup.
- Add one inline dense setup-workspace output panel and a dedicated model. It owns
  typed preview/generate/download state and busy locking; it does not move or reuse
  the Matrix-only TASK_360B confirmed compatibility row.

## Future May Touch

- The exact backend application, infrastructure, API, frontend, test, and governance
  paths already listed in `tasks/TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK.md`.
- No unlisted schema/repository/lifecycle/command, confirmed-consumer, or shared
  residual file is implicitly authorized. New code must preserve AGENTS module and
  service line-count limits.

## Locked Boundaries

No TASK_361B authority change, Matrix confirmation/persistence change, TASK_360B
confirmed behavior change, TASK_361E migration, generic Test Record, Fee, parser,
Basic Information, StepInstance/Report, LTR/public drive, real artifact mutation,
VBA/XLSM/COM, dependency change, release/settings cleanup, `.agents/**`, or
`docs/project_management/**` change is authorized.

## Validation Plan

- Temp-SQLite and temp-directory projection/service/store/gateway/API tests cover all
  status states, stale generation no-write, metadata/banner/layout, containment,
  retention, cleanup, and path traversal.
- Focused frontend/API-client tests cover inline status and actions, busy/stale/error
  recovery, latest/download, accessibility focus, and no confirmed-flow substitution.
- Regression includes TASK_360B confirmed preview/generate/download and TASK_361B/C
  authority/workspace suites, plus build, compile, diff/trailing/line-count/locked
  scope scans and controlled no-real-file browser smoke.

## Planning-First Validation

- Re-read AGENTS, task board, TASK_361D task/plan/Planner/Reviewer evidence, accepted
  TASK_361A/B/C context, TASK_360B projection/generation/artifact/layout boundaries,
  and current dedicated setup workspace model.
- Required TASK_361D plan/evidence files exist. Product code, schema, dependencies,
  API/client implementation, tests, and real files were not modified in this pass.
- `git diff --check` on the TASK_361D plan/evidence package passed. UTF-8 trailing
  whitespace scan returned no matches.
- Targeted status shows this pass adds only the TASK_361D Developer evidence and plan
  refinement. Existing parser/test changes, TASK_360Q/R/S files, board changes, and
  superpowers documents are external residuals and remain excluded.

## Next Role

Reviewer implementation-readiness gate after Planner source-of-truth reconciliation.

## Blocking Summary

No design blocker. Governance reconciliation is required because the task board/task
still record the pre-Reviewer-gate wording.

---

## Developer Implementation Pass

### Implemented Behavior

- Added a pure editable-revision-only draft workbook projection. It derives only from
  the existing TASK_361C workspace read boundary, rejects a non-current revision,
  classifies `ready`, `review_required`, `blocked`, and `empty`, and creates a
  canonical `draft-workbook:v1` preview fingerprint only for valid non-empty output.
- Added fingerprint-protected generation. Generation recomputes the projection before
  reserving an artifact and rejects stale fingerprints with no workbook write.
- Added an app-contained draft artifact store under
  `generated_contact_measurement_draft_workbooks/<project>/`, strict ids, JSON sidecar
  manifests, latest pointer, pair retention of 10, unknown-file preservation, and
  project-confined download resolution.
- Added a macro-free draft gateway with the existing fixed LLCR/CR sheet names and
  headers. It visibly writes `DRAFT` or `NEEDS REVIEW` on the summary and each record
  section, and includes draft plan/Matrix metadata without claiming confirmed output.
- Added the dedicated typed draft preview/generate/latest/download router and narrow
  dependency/main wiring. Existing TASK_360B confirmed routes, artifact root,
  filenames, client calls, and Matrix compatibility row remain untouched.
- Added typed API-client helpers plus one compact inline setup-workspace panel. It
  previews the current editable revision, exposes explicit generation/download,
  shows concise status/diagnostics, clears stale preview state after a stale error,
  and disables conflicting plan actions while draft work is busy.

### Changed Files

- `backend/application/draft_measurement_plan_workbook_projection.py`
- `backend/application/draft_measurement_plan_workbook_preview_service.py`
- `backend/application/draft_measurement_plan_workbook_generation_service.py`
- `backend/infrastructure/files/draft_measurement_plan_workbook_artifact_store.py`
- `backend/infrastructure/office/draft_measurement_plan_workbook_gateway.py`
- `backend/api/routes_contact_measurement_plan_draft_workbook.py`
- `backend/api/dependencies.py`, `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/contact-measurement-plan/DraftMeasurementPlanWorkbookPanel.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/contact-measurement-plan.css`
- focused TASK_361D unit/integration/frontend tests listed in the task plan
- TASK_361D Developer evidence

### Validation

- TDD red/green cycles were recorded for draft projection, manifest store, macro-free
  gateway, stale no-write generation, and inline preview UI.
- `py -m pytest tests/unit/test_draft_measurement_plan_workbook_projection.py
  tests/unit/test_draft_measurement_plan_workbook_artifact_store.py
  tests/unit/test_draft_measurement_plan_workbook_gateway.py
  tests/unit/test_draft_measurement_plan_workbook_generation_service.py
  tests/unit/test_contact_measurement_plan_workspace_read_service.py
  tests/integration/test_contact_measurement_plan_workspace_api.py -q` -> 9 passed.
- `py -m pytest tests/integration/test_contact_measurement_plan_draft_workbook_api.py
  -q` -> 2 passed.
- `npm test -- DraftMeasurementPlanWorkbookPanel ContactMeasurementSetupWorkspace
  useContactMeasurementPlanModel contactMeasurementPlanSelectors MatrixEditorWorkspace
  ContactMeasurementPlanSummaryCard --run` -> 7 files, 61 tests passed.
- `py -m py_compile` for all TASK_361D backend modules plus dependencies/main ->
  passed. New Python module line counts are 203, 51, 121, and 74, all below the
  AGENTS hard limit.
- `npm run build` -> passed; existing Vite chunk-size warning only.
- `git diff --check` -> passed with existing LF/CRLF warnings only. UTF-8 trailing
  whitespace scan was clean.

### Scope and Residuals

- No schema, migration, repository, lifecycle, authority, Matrix confirmation, Fee,
  TASK_361E, LTR/public-drive, real workbook/folder, VBA/XLSM/COM, or TASK_360B
  confirmed path was modified.
- Browser smoke is deferred to QA because this pass did not start a controlled
  disposable Matrix-authority fixture server. Existing parser/test, TASK_360Q/R/S,
  board, and superpowers-plan dirty entries remain external residuals and were not
  cleaned up.

## Next Role

Reviewer implementation gate.

---

## Developer Fix Pass: Reviewer B1/B2

Status: ready_for_review - B1/B2 fixed; pending Reviewer implementation re-gate.

### B1: Validated Artifact Ownership and Publication Safety

- Added one strict owned-pair validator used by resolve, latest, and retention cleanup.
  A candidate pair must satisfy contained parent, exact owned filename/id format,
  manifest version, artifact id, project binding, and manifest filename equality.
- Cleanup now considers only validated pairs. Forged or malformed same-stem
  `.json`/`.xlsx` files remain untouched.
- Publication creates the workbook, manifest, and latest pointer before best-effort
  retention cleanup. A cleanup `OSError` no longer invalidates the published pair or
  leaves `latest.json` pointing at a removed artifact.

### B2: Shared Fixed Layout and Complete Draft Metadata

- Extracted `llcr_cr_record_workbook_layout.py` as the shared Group-Step layout
  primitive. Both the unchanged confirmed gateway and the draft gateway now use its
  fixed headers, record blocks, guarded statistics formulas, and column widths.
- Draft summary now carries plan revision/fingerprint, source Matrix id/revision,
  Matrix binding fingerprint, preview fingerprint, layout version, review diagnostic
  count, generated UTC time, and generated row count.
- Both LLCR and CR record sheets always contain a visible `DRAFT` or `NEEDS REVIEW`
  banner, including a no-section sheet. Manifest metadata now carries the same source,
  review, layout, and generation traceability facts.

### Fix-Pass Tests and Validation

- New red regression: forged same-stem pair was deleted by cleanup. After the fix,
  strict cleanup preservation and post-publication cleanup-failure/latest consistency
  pass.
- New red regression: draft workbook lacked metadata, CR blank-sheet banner, formula,
  and width assertions. After shared-layout extraction, draft and confirmed gateway
  regression suite passes.
- `py -m pytest` draft projection/artifact/gateway/generation/API plus confirmed
  gateway/generation regression -> 14 passed.
- Focused frontend suite -> 7 files, 61 tests passed. `npm run build` passed with
  existing Vite chunk-size warning only. `py_compile` passed.
- `git diff --check` passed with existing LF/CRLF warnings only; UTF-8 trailing
  whitespace, locked-content scan, and line-count checks passed. No TASK_360B route,
  client, artifact, or authority semantic change was made.

## Next Role

Reviewer implementation re-gate. Do not route QA or Integrator from this Developer
fix pass.

---

## Developer Fix Pass: Reviewer B3 Frontend Feature Boundary

Status: ready_for_review - B3 fixed; pending Reviewer implementation re-gate.

- Added `useDraftMeasurementPlanWorkbookModel.ts` and focused hook regression. The
  hook owns typed latest-artifact refresh, preview, generate, busy/error state, stale
  feedback, and non-fatal cleanup warning state.
- Reworked `DraftMeasurementPlanWorkbookPanel.tsx` into declarative presentation. It
  consumes the hook output and callbacks, reports busy to its parent, and no longer
  imports API helpers or owns the complete asynchronous workflow.
- Hook red test first failed because the approved model file was absent; after
  implementation it verifies latest refresh, preview, generation, and cleanup-warning
  propagation. Component regression still proves visible warning and download.

### B3 Validation

- `npm test -- useDraftMeasurementPlanWorkbookModel DraftMeasurementPlanWorkbookPanel
  ContactMeasurementSetupWorkspace useContactMeasurementPlanModel
  contactMeasurementPlanSelectors MatrixEditorWorkspace
  ContactMeasurementPlanSummaryCard --run` -> 8 files, 63 tests passed.
- `npm run build` -> passed; existing Vite chunk-size warning only.
- Isolated-temp draft and confirmed workbook/API regression -> 15 passed.
- `git diff --check` passed with existing LF/CRLF warnings only; trailing whitespace
  scan clean; direct API-client import scan for the panel clean. No backend,
  authority, TASK_360B, or TASK_361E change was made in this B3 fix.

## Next Role

Reviewer implementation re-gate. Do not route QA or Integrator from this Developer
fix pass.

---

## Developer Fix Pass: Reviewer B1/B2 Warning and Summary-Region Follow-up

Status: ready_for_review - B1/B2 follow-up fixed; pending Reviewer implementation re-gate.

### B1: Visible Non-Fatal Cleanup Warning

- Retention cleanup remains best-effort after the workbook, manifest, and latest
  pointer are safely published. A cleanup `OSError` now returns the concise
  non-sensitive warning `Older draft artifacts could not be cleaned up.` instead of
  being silently discarded.
- The warning flows through artifact metadata, generation result, typed generate API
  response, typed client DTO, and the inline draft-workbook panel while preserving the
  download link to the valid newly published artifact.

### B2: Non-Overlapping Summary Regions

- Draft summary metadata occupies fixed rows 3 through 13. The draft-only disclaimer
  is row 15 and the section table begins at row 18, so source/review/layout/generated
  metadata cannot be overwritten by later content.
- The precise workbook regression asserts plan fingerprint, source Matrix id, Matrix
  binding fingerprint, layout version, disclaimer, and section-table start cells.

### Follow-Up Validation

- Red tests reproduced the missing cleanup-warning result property and the summary
  overlap. Focused artifact/gateway/generation/API regression is green: 9 passed.
- Isolated workspace temp rerun of draft and confirmed projection/artifact/gateway/
  generation/API suite: 15 passed. The initial shared-temp rerun hit a Windows
  `pytest-of-White` access denial during setup only; it was rerun with
  `--basetemp=tmp\\task_361d_pytest` and passed.
- Focused frontend suite: 7 files, 62 tests passed. `npm run build` and `py_compile`
  passed, with only the existing Vite chunk-size warning.
- `git diff --check` passed with existing LF/CRLF warnings only; trailing whitespace,
  line-count, and exact-path forbidden-scope scans are clean. The full shared client
  file contains pre-existing LTR/public-drive/confirmed helpers, while its TASK_361D
  hunk contains only draft-workbook helpers and `cleanup_warning`.

## Next Role

Reviewer implementation re-gate. Do not route QA or Integrator from this Developer
fix pass.
