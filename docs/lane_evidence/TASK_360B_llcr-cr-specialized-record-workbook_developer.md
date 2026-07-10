# TASK_360B Developer Planning-First Evidence

Status: developer planning-first complete. Implementation is not authorized.
Date: 2026-07-10
Role: Developer

## Gate Context

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK`.
- Lane: `llcr-cr-specialized-record-workbook`.
- Why this pass is allowed: the task board records TASK_360B as the active planned lane, the Reviewer plan re-gate passed, and the user approved Developer planning-first only.

## Repository Facts Rechecked

- TASK_360A persists structured `contact_plan` authority with contact kind, target coverage and exclusion reason, included families, label, count, record label, record prefix, and derived `readings_per_sample`. Matrix confirmation copies it into `ConfirmedMatrixSnapshot.step_quantities`.
- The Fee bridge is a passive consumer of that confirmed snapshot and is outside TASK_360B mutation scope.
- Existing generic Test Record is a separate confirmed-Matrix Word preview/document-generation route and frontend control. It is not a specialized LLCR/CR workbook surface and will remain untouched.
- Existing Matrix Contact Measurement Plan is the appropriate local, secondary action surface. It is already adjacent to the Matrix functional area and supports the required operational inline direction.
- No specialized LLCR/CR record workbook implementation, workbook route, or controlled artifact store currently exists.

## Implementation-Readiness Decision

The future package is implementable without a schema migration, legacy XLSM/VBA dependency, Excel COM, public-drive setting, or generic Test Record change. It uses one code-owned macro-free `openpyxl` gateway and one app-managed local artifact directory. The plan now fixes the workbook sheets, block columns, guarded formulas, authority mapping, typed preview/generate/download boundary, and UI placement.

### Authority And Validation Rules

- Active confirmed Matrix snapshot is the sole source. Draft data, Basic Information defaults, Fee values, generic Test Record projections, and generated workbook values never become fallbacks.
- Only included `llcr` and `cr_specified_current` contact-plan targets produce candidate sections. Excluded targets retain confirmed exclusion metadata as diagnostics and do not generate records.
- Included family counts materialize only when positive integers. Zero produces no rows. Blank, negative, decimal, scientific, and non-numeric counts are review blockers with no rounding.
- Materialized family sums must equal confirmed `readings_per_sample`; otherwise preview and generation are blocked.
- Prefix collisions compare normalized values only inside one confirmed Group-Step and contact type. The same prefix is valid in another section. No generated repair changes confirmed prefixes.

### Product Flow

1. The inline Contact Measurement Plan row requests a no-write preview.
2. The typed preview returns ready, blocked, review-required, or empty state with concise diagnostic text and a fingerprint only when ready.
3. Generate requires that matching fingerprint and reprojects the active confirmed snapshot. A changed snapshot is rejected before writing.
4. Generate returns an opaque artifact identifier and project-scoped download URL, not a local path. Download is constrained to the managed generated-output directory.
5. Generic Test Record controls and the legacy XLSM/VBA reference stay untouched.

## Exact Future Package

- Backend projection, preview, and generation services under `backend/application/confirmed_matrix_llcr_cr_record_*.py`.
- A contained local artifact store at `backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py`.
- A single fresh-workbook `openpyxl` gateway at `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`.
- One dedicated route module plus minimal dependency/main registration hunks.
- Typed API-client helpers, a focused Matrix Editor model hook, the existing Contact Measurement Plan card and Matrix Editor wiring, scoped styles, and focused tests.
- No package hunk in generic Test Record, top Test record, Fee, Matrix parser/import, Basic Information, LTR/public-drive, StepInstance, Report, settings/release, `.agents/**`, or `docs/project_management/**`.

## Future Test And Validation Plan

- Projection tests: confirmed-only filtering, ordering, included/excluded targets, positive integer expansion, zero omission, no rounding, readings-sum mismatch, prefix collision scope, and stale fingerprint construction.
- Gateway tests in temporary directories: exact sheet order, headers, guarded formulas, macro-free `.xlsx`, non-overwrite names, and no external template or Office dependency.
- Preview/generation/API tests: no-write preview, blocked/review DTOs, stale rejection without artifact, contained project-scoped download, and no arbitrary path input.
- Frontend tests: inline placement, Preview then Generate state, short blocker rendering, download action, disabled/loading behavior, and regression proving generic Test Record stays unaffected.
- Gate commands: focused `pytest`, focused `npm test`, `npm run build`, `py_compile`, `git diff --check`, trailing-whitespace, Python line-count, dependency scan for no VBA/XLSM/Excel COM, and no-real-workbook/public-drive mutation scan.

## Planning-Pass Validation

- Required TASK_360B task, plan, Planner evidence, Planner B1-B3 fix evidence, and Reviewer evidence were read.
- `$impeccable` product context, `PRODUCT.md`, `DESIGN.md`, `docs/02_ARCHITECTURE_RULES.md`, and `docs/frontend_architecture_rules.md` were read for the future inline UI boundary.
- This pass changes only the TASK_360B plan and this Developer evidence. Product implementation, dependencies, generated workbooks, schema, API, frontend, and tests remain untouched.

## Recommendation

Recommended next role: Reviewer implementation-readiness re-gate.

Blocking summary: none for planning-first. Implementation remains unauthorized pending Reviewer readiness, later user approval, and source-of-truth reconciliation.

## Developer Implementation Pass - 2026-07-10

Status: ready_for_review. Implementation complete pending Reviewer implementation gate.

### Implemented Scope

- Added a confirmed-snapshot-only LLCR/CR record projection. It consumes active `ConfirmedMatrixSnapshot.step_quantities.contact_plan` only, preserves confirmed ordering, recognizes included `llcr` and `cr_specified_current` targets, and does not read draft Matrix, Basic Information, Fee, generic Test Record, or generated workbook data.
- Added deterministic materialization rules: positive integer family counts expand per sample, zero families are omitted, decimals/negative/blank/non-numeric counts become review-required diagnostics with no rounding, family sums must equal `readings_per_sample`, and normalized prefix collisions block only in the same confirmed Group-Step/type section.
- Added a code-owned macro-free `openpyxl` workbook gateway. It writes only fresh `.xlsx` workbooks with fixed `Record Summary`, `LLCR Record`, and `CR Record` sheets, Group-Step blocks, fixed manual-entry columns, and guarded statistics formulas.
- Added no-write preview, fingerprint-protected generation, contained artifact resolution, and project-scoped download routes. Generation reprojects before writing, rejects stale fingerprints, returns no absolute path, and writes only below `data_dir/generated_llcr_cr_record_files/<project>`.
- Added typed frontend API helpers and a focused Matrix Editor hook. The existing Contact Measurement Plan card now contains a compact inline Preview, Generate, and Download row with concise blocked/review messaging. The top generic Test Record UI remains unchanged.

### TASK_360B Changed Files

- `backend/application/confirmed_matrix_llcr_cr_record_projection.py`
- `backend/application/confirmed_matrix_llcr_cr_record_preview_service.py`
- `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py`
- `backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py`
- `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`
- `backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- Focused TASK_360B backend, integration, hook, and card tests.

### Validation

- TDD red/green cycles were recorded for the new projection, workbook gateway, generation/artifact lifecycle, API route, frontend model hook, and inline card row.
- `py -m pytest tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_llcr_cr_specialized_record_workbook_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q`
  - Passed: 58 tests.
- `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard useLlcrCrSpecializedRecordWorkbookModel --run`
  - Passed: 3 files / 43 tests.
- `py -m py_compile` for all new TASK_360B backend modules plus dependency/main wiring
  - Passed.
- `npm run build`
  - Passed. Existing Vite chunk-size warning remains.
- `git diff --check`
  - Passed with existing LF/CRLF warnings only.
- Trailing-whitespace scan for all TASK_360B implementation/test files
  - No matches.
- Python line-count check
  - Largest new file is `backend/application/confirmed_matrix_llcr_cr_record_projection.py` at 248 lines, below the 500-line hard limit.
- Static boundary scans
  - No VBA/XLSM/Excel COM, PyMuPDF, LTR/public-drive, or real-drive path references in new TASK_360B implementation files.
  - No feature-level `fetch()` calls outside `frontend/src/api/client.ts`.

### Forbidden Scope And Residuals

- No generic Test Record/top Test record, Fee rule, Matrix parser/import, Basic Information, StepInstance, full Report, LTR/public-drive, real workbook/folder, release/settings, `.agents/**`, or `docs/project_management/**` implementation behavior was changed.
- Existing `backend/modules/fee_evaluation/*`, Fee tests, and `docs/task_board.md` worktree residuals remain external and excluded from TASK_360B.
- Browser smoke was not run in this Developer thread. Reviewer or QA should smoke the Matrix Editor inline preview/generate/download row against a safe confirmed contact-plan fixture. No real workbook, public-drive, or LTR file was created or mutated by these tests.

### Recommendation

Recommended next role: Reviewer implementation gate.

Blocking summary: none known. The implementation is ready for scope, artifact, API, and UI review.

## Reviewer B1 Developer Fix Pass - 2026-07-10

Status: ready_for_review. This pass resolves only the same-section normalized prefix collision diagnostic detail blocker.

### Fix

- `LlcrCrRecordDiagnostic` now carries `first_family_id`, `first_family_label`, `second_family_id`, and `second_family_label` in addition to the existing target identity and normalized prefix.
- Projection retains the earlier materialized family identity/label while checking normalized prefixes, then records both sides when the later family collides. The collision remains a no-write `blocked` preview state; separate Group-Step prefix reuse remains permitted.
- The dedicated API response and `frontend/src/api/client.ts` DTO expose all four fields as typed nullable metadata.
- The inline Contact Measurement Plan row now formats a collision as operator-readable pair text, for example `HP (hp) conflicts with High Power duplicate (hp_alt).`, rather than leaving the user with only a generic blocker label.

### Regression Coverage

- Projection regression verifies both IDs and labels are populated for a same-section collision.
- API regression verifies the preview response is blocked, writes no workbook, and returns both conflicting families.
- Component regression verifies the inline card renders both family names and IDs.

### Validation

- `py -m pytest tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_llcr_cr_specialized_record_workbook_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q`
  - Passed: 59 tests.
- `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard useLlcrCrSpecializedRecordWorkbookModel --run`
  - Passed: 3 files / 44 tests.
- `npm run build`
  - Passed with the existing Vite chunk-size warning only.
- `py -m py_compile` for the updated TASK_360B projection, route, preview, and generation modules
  - Passed.

### Scope Check

- No generic Test Record, Fee, Matrix parser/import, StepInstance, Report, VBA/XLSM/COM, LTR/public-drive, or other locked-scope behavior changed.
- Existing external Fee and board residuals remain excluded. Browser smoke remains a QA residual.

### Re-Gate Recommendation

Recommended next role: Reviewer implementation re-gate.

Blocking summary: none known. B1 now reports both conflicting contact families through projection, API/client DTOs, and concise inline UI copy.
