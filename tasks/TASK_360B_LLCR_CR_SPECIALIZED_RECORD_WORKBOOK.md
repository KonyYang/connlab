# TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK

## Status

Complete/accepted by Integrator.

## Lane

`llcr-cr-specialized-record-workbook`

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK`.
- Role: Planner source-of-truth reconciliation.
- Why allowed: Reviewer plan re-gate passed, the user approved Developer planning-first, Developer planning-first completed as docs-only, Reviewer implementation-readiness passed, and the user explicitly approved reconciliation plus Developer implementation. This pass changes governance records only.

## Goal

Generate a dedicated LLCR/CR Excel record workbook from the active confirmed Matrix contact snapshot. It expands by type, Group, Matrix Step, sample, and structured contact family/prefix. It is separate from the generic `Test record` action and must not change generic Test Record or Word behavior.

## Authority And Workflow Contract

- Input authority is the active `ConfirmedMatrixSnapshot` only. Draft Matrix, Basic Information, Fee, and legacy macro data are not authority.
- A target requires included LLCR/CR contact coverage, usable structured families, and a valid positive `readings_per_sample` equal to the sum of included family counts.
- The matching confirmed Group provides the sample quantity. V1 expands only a safely interpretable positive whole-number total; ambiguity is a preview blocker, never a guessed output.
- Each generated row represents one Group-Step, sample, contact family, and family contact index. It displays `record_prefix` plus index and `record_label`.
- Initial, After, and Final are manual workbook columns/blocks. V1 does not infer lifecycle phases from arbitrary Matrix Step tokens.
- Preview returns the projection, blockers/warnings, row counts, confirmed revision, and fingerprint without writing a file.
- Generate requires the fingerprint, recomputes the projection, rejects stale/blocked state, and writes a non-overwriting macro-free `.xlsx` inside an app-managed generated-file directory only.
- Completed values are not imported back into Matrix, Fee, generic Test Record, Report, or StepInstance in V1.

## Legacy Workbook Boundary

- `D:/LabOfficeAuto/Test Project Confirm 20250423.xlsm` is read-only reference material only.
- Discovery observed `GetLTRNum`, `TestMatrix`, `ConfirmSpec`, and `Test Status`; `ConfirmSpec` uses test metadata and numbered sample columns.
- `xl/vbaProject.bin` is present, but this pass did not execute, extract, copy, or modify the macro source.
- V1 uses a new controlled macro-free `.xlsx` layout inspired by the observed business structure, not macro-parity or macro hosting.

## May Touch For Future Implementation

- Confirmed-contact projection, preview, and generation application services.
- Dedicated infrastructure Excel workbook gateway with code-owned `LLCR_CR_RECORD_LAYOUT_V1`; no external template asset.
- Focused FastAPI route, dependency, router registration, contained download handling, and tests.
- `frontend/src/api/client.ts`; `MatrixContactMeasurementPlanCard`, focused selectors/tests, `MatrixEditorWorkspace` wiring/tests, and scoped Matrix Editor CSS.
- TASK_360B docs/evidence/board.

## Must Not Touch / Locked Paths

- No generic Test Record action, route, preview, Word gateway, template, document generation, or output-semantic change.
- No Matrix contact authority mutation, Fee rule/default-fill change, Matrix parser/import, Basic Information, StepInstance/execution persistence, full Report, LTR/public-drive, or real workbook/folder mutation.
- No writable use, copy, or macro execution of the legacy XLSM.
- No release/settings cleanup, `.agents/**`, `docs/project_management/**`, commit, or push.

## Validation Gate Draft

- Projection tests: target filtering, Group-Step order, family-index expansion, LLCR/CR separation, totals, prefix collision handling, and review blockers.
- Gateway tests in temporary directories: expected sheets, headers, blocks, manual measurement cells, summary formulas, no macro payload, and non-overwrite behavior.
- API tests: no-write preview, matching fingerprint requirement, stale/blocked/not-found responses, safe generation, and contained download paths.
- Frontend tests: compact Contact Measurement Plan action/preview, blockers, Generate readiness, and no generic Test Record route call.
- Regression: TASK_360A contact authority, Fee passive consumption, and generic Test Record preview/document generation.
- Focused `pytest`, focused `npm test`, `npm run build`, diff/trailing/forbidden-scope/no-real-mutation scans.

## Reviewer B1-B3 Resolved Contract

### B1: Packageable Workbook And Inline Preview Boundary

- Workbook construction is fixed: `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py` creates a new `.xlsx` with `openpyxl.Workbook`. There is no external template, no copied template asset, and no `.xlsm`/VBA runtime dependency.
- The gateway owns the code-defined `LLCR_CR_RECORD_LAYOUT_V1`: fixed `Record Summary`, `LLCR Record`, and `CR Record` sheets; Group-Step heading blocks; fixed record columns `Record Type`, `Group`, `Matrix Step`, `Sample`, `Contact ID`, `Contact Label`, `Initial`, `After`, `Final`, `Result`, and `Remarks`; and block footer formulas for populated/manual measurement statistics. Blank type sheets remain visible and say no ready targets.
- The layout source is code-owned by TASK_360B in the gateway. This matches existing macro-free `openpyxl` product gateways for customer-feedback and Fee workbook generation, while avoiding any Settings or package-data change for an external template.
- Exact future files: `backend/application/confirmed_matrix_llcr_cr_record_projection.py`, `backend/application/confirmed_matrix_llcr_cr_record_preview_service.py`, `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py`, `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`, `backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py`, focused `backend/api/dependencies.py` and `backend/api/main.py`, `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts`, `MatrixContactMeasurementPlanCard.tsx`, focused Matrix Editor tests, and `frontend/src/workbench.css`.
- API contract: `POST /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/preview`; `POST /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/generate` with `preview_fingerprint`; and a contained generated-file download endpoint. Generate recomputes the projection and rejects a stale fingerprint.
- Files are written only to `settings.data_dir / "generated_llcr_cr_record_files"` as `<project_id>_llcr_cr_record_r<confirmed_revision>.xlsx`, with deterministic non-overwrite suffixing. No project-folder, public-drive, LTR, or user-supplied path is accepted.
- UI remains calm and inline: `MatrixContactMeasurementPlanCard` gains one dense `LLCR/CR record workbook` action row with Preview, a concise status/blocker line, an inline small projection summary after preview, and Generate only when ready. It is not modal-first and does not reuse the generic Test Record action.

### B2: Deterministic Family Expansion

- Materialized families are the persisted snapshot order where `included` is true and `count_per_sample` is a positive integer text matching `^[1-9][0-9]*$`.
- `count_per_sample == "0"` means omitted: it emits no record rows and is not part of prefix collision checking.
- Blank, negative, decimal, scientific, non-numeric, or otherwise non-integer counts make that Group-Step target `review_required`/blocked with a family-level diagnostic. Preview returns no ready export while any target is blocked; generation creates no XLSX.
- Each materialized family expands deterministically for every safe sample number and contact index `1..count_per_sample`. Contact id is `<record_prefix><index>` and display text retains the structured family label/record label.
- `readings_per_sample` must equal the sum of materialized family counts. A mismatch blocks preview/export; no rounding, coercion, or fallback is allowed.

### B3: Prefix Collision Scope And Outcome

- Normalize a materialized prefix by trimming, uppercasing, and removing non-alphanumeric characters. An empty normalized prefix is a target-level blocker.
- Collision scope is one confirmed contact-plan snapshot and record type, keyed by confirmed matrix id, confirmed group id, confirmed row id, Step sequence, and normalized Step suffix. The check considers materialized included families only.
- Two different families with the same normalized prefix in that scope block preview/export. The diagnostic includes target section key, record type, normalized prefix, and both family ids/labels; no partial workbook is generated.
- The same normalized prefix may recur in separate Group-Step blocks because their section keys are distinct.
- Required validation includes exact positive/zero/decimal count behavior, prefix normalization, same-block collision rejection, separate-block prefix reuse, stale preview rejection, and no-output-on-blocker behavior.

## Authorization And Merge Gate

- Reviewer plan re-gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation is authorized only within this task's scope and locks.
- Developer implementation completed.
- Reviewer implementation re-gate passed after B1 fix.
- QA gate passed, including temporary-directory artifact smoke.
- Integrator package isolation/readiness accepted the controlled TASK_360B package.
- Remote push intentionally not performed.

## Definition Of Ready

Definition of Ready, implementation readiness, Reviewer implementation gate, QA gate, and Integrator package/readiness gate are satisfied. The lane is complete/accepted.

## Integrator Acceptance

- Accepted package scope: active confirmed-snapshot LLCR/CR projection, preview/generate/download API, managed artifact lifecycle, macro-free `openpyxl` workbook gateway/layout, typed API client, inline Matrix Contact Measurement Plan UI/model/tests, task/plan/evidence, and board closeout.
- Validation accepted: backend/API/authority/generic Test Record suite `59 passed`; frontend Matrix card/model/workspace suite `3 files / 44 tests passed`; `npm run build` passed with existing Vite chunk-size warning only; `py_compile` passed; cached diff, trailing whitespace, staged whitelist, forbidden-path/content, line-count, no-VBA/XLSM/COM, and no-real-mutation scans passed.
- QA temp-dir artifact smoke confirmed preview no-write behavior, stale preview rejection, contained app-managed `.xlsx` output, fixed sheets/headers/formulas, no `vbaProject.bin`, and cleanup of temporary artifacts.
- Excluded residuals: external Fee rule/seed/test changes, generic Test Record/top action semantics, TASK_360A unrelated source, Matrix parser/import, StepInstance, Report, LTR/public-drive, release/settings/desktop/packaging, `.agents/**`, `docs/project_management/**`, and temp artifacts.

## Blocking Questions

None for the planned lane. Measurement-result import or StepInstance execution persistence is explicitly future scope.
