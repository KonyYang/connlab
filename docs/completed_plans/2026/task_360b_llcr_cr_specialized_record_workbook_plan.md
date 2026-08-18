# TASK_360B LLCR/CR Specialized Record Workbook Plan

## Discovery Summary

TASK_360B is the serial derived-output successor to accepted TASK_360A. It reads active confirmed Matrix Step contact snapshots and produces a new macro-free Excel record workbook. It does not change Matrix authority or the existing generic Word Test Record flow.

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK`.
- Role: Planner source-of-truth reconciliation.
- Why allowed: TASK_360A is accepted at `f9c34e5a`; Reviewer plan re-gate passed; the user approved Developer planning-first; Developer planning-first completed as docs-only; Reviewer implementation-readiness passed; and the user approved reconciliation plus Developer implementation.

## Confirmed By User

- The new output is LLCR/CR-specific Excel, structured by type, Group, Matrix Step, sample, and contact family/prefix.
- The legacy `D:/LabOfficeAuto/Test Project Confirm 20250423.xlsm` is business-structure reference material.
- Initial/After/Final record areas and statistics are needed where applicable.
- This must remain independent from the existing generic Test Record/Word output.
- Matrix parser, Fee rules, StepInstance, Report, LTR/public-drive, release, and Settings are excluded.

## Confirmed By Repository Evidence

- TASK_360A stores typed confirmed contact plans with `contact_kind`, coverage/included/override metadata, `readings_per_sample`, and family label/count/record-label/record-prefix values.
- Confirmed Matrix groups retain sample quantity and Group-Step identity.
- Fee reads contact-plan `readings_per_sample` passively; no TASK_360B behavior exists in Fee code.
- Existing generic Test Record is a confirmed-Matrix preview plus template-backed Word `.docx` generation flow.
- Existing Excel exports demonstrate app-managed output directories, contained downloads, non-overwrite behavior, and Office-gateway boundaries.
- Read-only XLSM inspection found project, Matrix, confirmation, and status sheets; `vbaProject.bin` exists but no approved macro-source extractor is installed.

## Planner Inference

- V1 should generate a new controlled `.xlsx`; no macro execution, macro copying, or modification of the legacy XLSM.
- A dedicated infrastructure gateway owns all workbook writes; routes and frontend only coordinate typed preview/generate requests.
- A server-generated fingerprint protects preview-before-write: generation rebuilds the projection and rejects stale confirmed snapshot data.
- A compact row inside the existing Contact Measurement Plan card is the right trigger, preserving Matrix as the primary work surface and avoiding a new output dashboard.

## Not Yet Confirmed

- Exact historical VBA source and cell-by-cell macro mapping are unavailable. V1 uses explicit new mapping rather than claiming macro parity.
- V1 does not infer Initial/After/Final phase labels from arbitrary Step tokens; it renders explicit source Step plus manual Initial/After/Final fields.
- Compound/non-numeric sample quantity expressions are preview blockers until a deterministic parser policy is separately approved.

These are not blockers for the planned lane because the conservative V1 behavior is explicit.

## Data Mapping

| Workbook field | Confirmed source | Mapping rule |
|---|---|---|
| Type | `contact_plan.contact_kind` | Separate LLCR and CR sections/sheets. |
| Group | confirmed group identity/label | One block per confirmed Group-Step target. |
| Step | `step_sequence`, token, suffix | Display source Step; do not create execution state. |
| Sample | group sample quantity | Expand only safe positive whole-number totals. |
| Contact id | `record_prefix` + index | One row per family count, per sample. |
| Contact label | `record_label` / family label | Preserve snapshot label; no text inference. |
| Readings/sample | derived snapshot value | Validate against included family-count sum. |
| Initial / After / Final | generated workbook cells | Blank manual entry; no import back in V1. |
| Statistics | generated record rows | Formula-backed only when applicable. |

## Preview-First Product Boundary

1. Preview reads confirmed authority, creates no file, and returns rows, blockers, warnings, confirmed revision, and fingerprint.
2. Generate accepts only a matching fingerprint, reprojects the snapshot, and fails cleanly if it changed.
3. Generation writes only under `data_dir/generated_llcr_cr_records`, with a non-overwriting name and contained download route.
4. The Contact Measurement Plan card presents a compact preview summary and Generate command only for ready preview. It does not reuse or relabel generic Test Record controls.

## Reviewer B1-B3 Fixed Implementation Contract

### B1: Workbook Construction, API, And UI

V1 is code-owned, not template-conditional. `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py` constructs a fresh macro-free workbook using the existing approved `openpyxl` product pattern. `LLCR_CR_RECORD_LAYOUT_V1` in that gateway is the sole layout source: fixed `Record Summary`, `LLCR Record`, and `CR Record` sheets; Group-Step headings; columns for type, group, source Step, sample, contact id, contact label, Initial, After, Final, Result, and Remarks; and block summary formulas that remain blank until manual measurement values exist. No binary template asset, Excel COM, Settings path, legacy XLSM, or VBA module is used.

The projection/service boundary is fixed at:

- `backend/application/confirmed_matrix_llcr_cr_record_projection.py`
- `backend/application/confirmed_matrix_llcr_cr_record_preview_service.py`
- `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py`
- `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`
- `backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py`
- focused `backend/api/dependencies.py` and `backend/api/main.py` wiring

`POST /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/preview` returns typed blocks, diagnostics, row counts, confirmed revision, and `preview_fingerprint` without writing. `POST /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/generate` requires that fingerprint and recomputes the projection. It writes only beneath `settings.data_dir / "generated_llcr_cr_record_files"` using `<project_id>_llcr_cr_record_r<confirmed_revision>.xlsx` plus a non-overwrite suffix. A contained download endpoint may return only files from that directory.

Frontend wiring is limited to `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts`, `MatrixContactMeasurementPlanCard.tsx`, focused Matrix Editor tests, and `frontend/src/workbench.css`. The card uses an inline operational row: Preview, short status/blocker text, compact projection table, then Generate when ready. No modal-first flow, no new dashboard, and no generic Test Record control reuse.

### B2: Family-Contact-Index Expansion

For each confirmed Group-Step section, evaluate persisted families in snapshot order:

1. A positive integer count is exactly text matching `^[1-9][0-9]*$`; it materializes.
2. Text `0` is omitted and produces no rows.
3. Blank, negative, decimal, scientific, or non-numeric count blocks that target as `review_required` with a family-level diagnostic. It never rounds.
4. Every materialized family expands per safe sample number and indexes `1..count`. The contact id is `record_prefix + index`; the structured `record_label` remains visible.
5. The target's derived `readings_per_sample` must equal the sum of materialized family counts. Mismatch blocks preview and prevents XLSX generation.

### B3: Prefix Collision Policy

For materialized included families, normalize `record_prefix` by trimming, uppercasing, and removing non-alphanumeric characters. Empty normalized prefixes block the target. Check collisions only inside one confirmed contact-plan snapshot and one record type, keyed by confirmed matrix id, confirmed group id, confirmed row id, Step sequence, and normalized suffix. A duplicate normalized prefix across two families in that section blocks the entire preview/export and returns both family ids/labels, target section key, record type, and normalized prefix. The same prefix is allowed in separate Group-Step sections because their section keys differ.

## Developer Planning-First Refinement

### Confirmed Authority And Projection

The projection reads exactly one active `ConfirmedMatrixSnapshot` for the requested project. It must never use a Matrix draft, Basic Information defaults, Fee data, a generic Test Record preview, or a generated workbook as authority.

Each output target is identified by `confirmed_matrix_id`, `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, normalized `step_suffix_note`, and `contact_plan.contact_kind`. Only an included `llcr` or `cr_specified_current` plan is a candidate. Excluded targets retain their confirmed reason in diagnostics and generate no section. Missing, unsupported, review-required, or unsafe targets are diagnostics, never guessed rows.

The projection preserves confirmed group and row order, parsed Step-token order, persisted family order, and sample/contact index order. `readings_per_sample` is a validation fact, not another input: it must equal the sum of materialized included family counts.

### Exact Preview, Generate, And Download Contract

```text
POST /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/preview
  request: empty body
  response: LlcrCrRecordWorkbookPreviewResponse

POST /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/generate
  request: { preview_fingerprint: string }
  response: LlcrCrRecordWorkbookGenerateResponse

GET /api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/files/{artifact_id}
  response: macro-free .xlsx bytes
```

The preview response contains `project_id`, `status` (`ready`, `blocked`, `review_required`, or `empty`), confirmed matrix id/revision, nullable fingerprint, ordered sections, row count, and structured diagnostics. A section contains its confirmed Group-Step identity, record type, group label, source Step display, safe sample count, readings per sample, included family summaries, and projected rows. Diagnostics contain stable code, severity, concise message, and target/family identity when known.

Generate recomputes the projection before writing. A mismatch with the supplied fingerprint or a changed active snapshot returns a typed stale-preview conflict and writes nothing. Its response returns only an opaque `artifact_id`, `file_name`, and project-scoped `download_url`, never an absolute local path.

The artifact store writes only under `settings.data_dir / "generated_llcr_cr_record_files"`, uses non-overwriting `.xlsx` names, and accepts no user path. Download validates the opaque identifier, project ownership, extension, containment, and separator-free basename before serving. No schema or `ProjectOutputRecord` extension is part of V1. Generated artifacts remain managed local outputs; retention cleanup is future scope and must not be implicit deletion.

### Fixed Macro-Free Workbook Layout

`LLCR_CR_RECORD_LAYOUT_V1` remains a constant in `llcr_cr_specialized_record_workbook_gateway.py`. The gateway constructs a new `openpyxl.Workbook`, removes the default sheet, and creates this exact sheet order:

1. `Record Summary`: title in `A1`, project and confirmed identity in `A3:B6`, then the ordered section summary table at `A8` with `Type`, `Group`, `Source Step`, `Samples`, `Readings / sample`, `Generated rows`, and `Status`.
2. `LLCR Record`: only ordered `llcr` Group-Step blocks.
3. `CR Record`: only ordered `cr_specified_current` Group-Step blocks.

Each record block has a merged Group-Step heading, a metadata row, and fixed `A:K` columns: `Type`, `Group`, `Source Step`, `Sample`, `Contact ID`, `Contact Label`, `Initial`, `After`, `Final`, `Result`, `Remarks`. `A:F` are snapshot-projected values; `G:K` are blank manual-entry cells. Its summary row uses guarded formulas which remain visibly blank until manual values exist:

```excel
Initial average: =IF(COUNT(G{first}:G{last})=0,"",AVERAGE(G{first}:G{last}))
After average:   =IF(COUNT(H{first}:H{last})=0,"",AVERAGE(H{first}:H{last}))
Final average:   =IF(COUNT(I{first}:I{last})=0,"",AVERAGE(I{first}:I{last}))
Result count:    =IF(COUNTA(J{first}:J{last})=0,"",COUNTIF(J{first}:J{last},"PASS")&"/"&COUNTA(J{first}:J{last}))
```

No formula creates execution state, decides pass/fail, or writes back into ConnLab. The gateway includes no Excel COM, template asset, VBA, or legacy XLSM payload.

### Expansion And Prefix Details

Every included family is validated before one record row is materialized. Only `^[1-9][0-9]*$` expands to indexes `1..count`; exactly `0` omits that family; blank, negative, fractional, scientific, and non-numeric text create a `review_required` diagnostic with no rounding. Normalized prefix is `trim -> uppercase -> remove non-alphanumeric`; empty normalized prefix blocks the target. A collision blocks only between materialized included families in the same confirmed Group-Step identity and record type. Reuse in a different Group-Step section or type sheet is permitted. No automatic prefix or ID repair is allowed.

### Inline Product Placement

The existing `MatrixContactMeasurementPlanCard` is the sole future UI placement. A compact row after its current plan actions exposes Preview, short state text, a compact section/row summary, Generate only for a current ready fingerprint, then Download after generation. Blocked/review states render concise inline diagnostics. There is no modal-first path, dashboard, or reuse of generic Test Record/top Test record UI or copy.

## Exact Future May Touch

- Create `backend/application/confirmed_matrix_llcr_cr_record_projection.py`.
- Create `backend/application/confirmed_matrix_llcr_cr_record_preview_service.py`.
- Create `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py`.
- Create `backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py`.
- Create `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`.
- Create `backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py`.
- Modify only necessary provider/registration hunks in `backend/api/dependencies.py` and `backend/api/main.py`.
- Modify `frontend/src/api/client.ts` and create `frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts`.
- Modify `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, their focused tests, and scoped `frontend/src/workbench.css`.
- Create focused unit and integration tests for the named projection, preview, generation, artifact store, gateway, route, and frontend model/card boundaries.
- Update TASK_360B plan/evidence/board only through normal lane flow.

All new Python files must remain below the AGENTS hard limit. Layout, projection, artifact ownership, and routes must stay separate rather than growing generic Test Record or Matrix services.

## May Touch Draft

- `backend/application/confirmed_matrix_llcr_cr_record_projection.py`
- `backend/application/confirmed_matrix_llcr_cr_record_preview_service.py`
- `backend/application/confirmed_matrix_llcr_cr_record_generation_service.py`
- `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`
- code-owned `LLCR_CR_RECORD_LAYOUT_V1` inside that gateway; no external template asset
- focused route/dependency/main wiring for preview, generate, and contained download
- `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`, focused selectors/tests, `MatrixEditorWorkspace` wiring/tests, and scoped `frontend/src/workbench.css`
- focused backend/frontend tests and TASK_360B docs/evidence/board

## Must Not Touch / Locked Paths

- Existing generic Test Record preview/route/Word gateway/template/document generation/action copy.
- Matrix contact-plan persistence and Matrix Confirm behavior.
- Fee default-fill rules/UI, Matrix parser/import, Basic Information, StepInstance/execution, full Report, LTR/public-drive, real files/folders, release/settings, `.agents/**`, and `docs/project_management/**`.
- Legacy `D:/LabOfficeAuto/Test Project Confirm 20250423.xlsm`.

## Validation And Merge Gates

- Unit: filtering, order, positive/zero/decimal expansion behavior, type separation, totals, prefix normalization, same-section collision rejection, separate-section prefix reuse, review blockers, and stale preview rejection.
- Gateway: temporary-directory `.xlsx` structure, cells/formulas, no macro payload, no overwrite.
- API: no-write preview, stale fingerprint rejection, blocker/no-result behavior, contained download.
- Frontend: card placement, preview readiness, blocker copy, and generic Test Record isolation.
- Regression: TASK_360A, Fee passive consumption, generic Test Record preview/document.
- Build/test: focused `pytest`, focused `npm test`, `npm run build`, `git diff --check`, trailing whitespace, forbidden-scope, no-real-mutation.
- Merge: Reviewer plan re-gate passed; Developer planning-first and readiness gates passed; implementation is now authorized; then Reviewer implementation gate, QA temp-dir smoke, and Integrator package isolation.

## Parallel / Serial Assessment

TASK_360B is serial after TASK_360A. It can remain independent of future StepInstance, Report, and generic Test Record work because it only creates a manual-entry derived workbook and does not import measurements.

## Definition Of Ready

Definition of Ready, implementation readiness, Reviewer implementation gate, QA gate, and Integrator package/readiness gate are satisfied. TASK_360B is complete/accepted.

## Blocking Questions

None for the planned lane.

## Integrator Acceptance

- Status: complete/accepted by Integrator.
- Accepted scope: confirmed-snapshot-only LLCR/CR projection; preview/generate/download route and typed client; macro-free code-owned `openpyxl` workbook layout; app-managed artifact store; inline Matrix Contact Measurement Plan workbook row; focused backend/frontend tests; TASK_360B task/plan/evidence/board closeout.
- Excluded scope: external Fee rule/seed/test residuals, generic Test Record/top `Test record` behavior, TASK_360A unrelated source, Matrix parser/import, StepInstance, Report, LTR/public-drive, release/settings/desktop/packaging, `.agents/**`, `docs/project_management/**`, temp artifacts, real workbook/folder mutation, and remote push.
- Validation accepted: backend/API/authority/generic Test Record suite `59 passed`; frontend Matrix card/model/workspace suite `3 files / 44 tests passed`; frontend build passed with existing Vite chunk-size warning only; py_compile passed; diff-check/trailing/staged whitelist/forbidden-path/content/line-count/no-real-mutation scans passed.
- Browser smoke remains a non-blocking tooling residual because bundled Chromium is missing and system Chrome launch is blocked by EPERM; QA temp-dir artifact smoke and focused frontend/API tests passed.
