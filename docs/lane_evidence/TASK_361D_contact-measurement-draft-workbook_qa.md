# TASK_361D Contact Measurement Draft Workbook - QA Evidence

Date: 2026-07-12
Role: QA / Smoke Owner
Lane: `contact-measurement-draft-workbook`
Result: `qa_pass`

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK.md`
- `docs/task_361d_contact_measurement_draft_workbook_plan.md`
- `docs/lane_evidence/TASK_361D_contact-measurement-draft-workbook_developer.md`
- `docs/lane_evidence/TASK_361D_contact-measurement-draft-workbook_reviewer.md`
- TASK_361D backend services/routes/artifact store/workbook gateway/tests
- TASK_361D frontend panel/model/workspace/tests

Board note: `docs/task_board.md` still contains older TASK_361D text, while the latest lane evidence and reviewer callback report `reviewer_pass`. QA used latest lane evidence plus actual working-tree diff as current gate source.

## Validation Commands

Focused backend:

```powershell
py -m pytest tests/unit/test_draft_measurement_plan_workbook_projection.py tests/unit/test_draft_measurement_plan_workbook_artifact_store.py tests/unit/test_draft_measurement_plan_workbook_gateway.py tests/unit/test_draft_measurement_plan_workbook_generation_service.py tests/integration/test_contact_measurement_plan_draft_workbook_api.py tests/unit/test_contact_measurement_plan_workspace_read_service.py tests/integration/test_contact_measurement_plan_workspace_api.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py -q
```

Result: `17 passed in 3.09s`.

Focused frontend:

```powershell
cd frontend
npm test -- useDraftMeasurementPlanWorkbookModel DraftMeasurementPlanWorkbookPanel ContactMeasurementSetupWorkspace useContactMeasurementPlanModel contactMeasurementPlanSelectors MatrixEditorWorkspace ContactMeasurementPlanSummaryCard --run
```

Result: `8 files / 63 tests passed`.

Build / compile / static:

- `py -m py_compile` on TASK_361D touched backend route/service/store/gateway/dependency modules: passed.
- `cd frontend; npm run build`: passed with existing Vite chunk-size warning only.
- `git diff --check -- <TASK_361D candidate files>`: passed with LF/CRLF normalization warnings only.
- UTF-8 trailing whitespace scan over TASK_361D candidate files: no matches.
- Line-count scan: largest TASK_361D Python file observed 203 lines; largest TASK_361D TSX/TS model file observed 65 lines.
- Forbidden-scope/status scan: no TASK_361D changes in Fee, authority storage/lifecycle semantics, TASK_361E, Matrix parser, public-drive/LTR, `.agents/**`, or `docs/project_management/**`. External parser/task-board/planning residuals remain excluded.

## Temp Artifact Smoke

All smoke used disposable temp directories only. No real user project, real public-drive/LTR workbook, VBA/XLSM/COM, or authority path was touched.

Ready/DRAFT path:

- Input: editable draft revision `draft-qa`, confirmed Matrix binding, one LLCR and one CR target.
- Observed: `ready DRAFT 2 7 True True`.
- Generate observed: `DRAFT`, `.xlsx` output, `latest` points to generated artifact, workbook has no VBA archive.
- Workbook banners/metadata observed:
  - `Record Summary!A1 = DRAFT`
  - `LLCR Record!A1 = DRAFT | Draft measurement plan`
  - `CR Record!A1 = DRAFT | Draft measurement plan`
  - summary metadata included revision `draft-qa`, matrix `matrix-qa`, layout `LLCR_CR_RECORD_LAYOUT_V1`.
- Stale fingerprint generate rejected and no extra workbook was produced: `stale_no_extra True 1`.

NEEDS REVIEW path:

- Input: editable draft revision with open `review_required` impact.
- Observed: `review_required NEEDS REVIEW`.
- Generated workbook summary and record banners showed `NEEDS REVIEW`.

No-output paths:

- Empty target set: `empty None False False`, generate blocked, `0` xlsx outputs.
- Blocked positive-integer validation case: `blocked None False False`, generate blocked, `0` xlsx outputs.
- Non-editable/confirmed source: preview and generate blocked, `0` xlsx outputs.

Artifact lifecycle:

- Retention smoke generated 12 artifacts with `retention_count=10`.
- Observed: `10` owned workbook files, `10` owned artifact manifests, `latest.json` present, latest points to newest artifact.
- Cleanup failure smoke forced retention cleanup to raise `OSError`.
- Observed warning: `Older draft artifacts could not be cleaned up.`
- Published output existed, `latest` still pointed to the new artifact, and resolving latest returned the new metadata.

## Controlled SQLite/API Smoke

Setup:

- Created disposable temp SQLite/data/projects/templates roots under OS temp.
- Seeded controlled confirmed Matrix snapshot for project `P1`.
- Used real FastAPI app dependencies with temp settings.

Flow:

1. `POST /api/projects/P1/contact-measurement-plan/revisions`
   - Result: `200`, editable revision created.
2. `POST /api/projects/P1/contact-measurement-plan/revisions/{revision_id}/draft-workbook/preview`
   - Result: `200`, `status=ready`, `output_label=DRAFT`, `row_count=8`, preview fingerprint present.
3. `POST .../generate` with stale fingerprint.
   - Result: `409`, `detail.code=draft_workbook_stale`.
4. `POST .../generate` with current preview fingerprint.
   - Result: `200`, `output_label=DRAFT`, valid download URL.
5. `GET /api/projects/P1/contact-measurement-plan/draft-workbook/artifacts/latest`
   - Result: `200`, latest artifact ID matched generated artifact.
6. `GET /api/projects/P1/contact-measurement-plan/draft-workbook/files/{artifact_id}`
   - Result: `200`, content type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, non-empty xlsx body.

Contained-path observation:

- Generated API artifact root was under the disposable temp `data/generated_contact_measurement_draft_workbooks/P1`.
- Workbook summary/record banners confirmed `DRAFT`.

## Browser Smoke

Setup:

- Seeded disposable repo-local runtime under `tmp/TASK_361D_qa_runtime`.
- Started backend on `127.0.0.1:8001` against the disposable SQLite database.
- Started Vite on `127.0.0.1:5175` with `/api` proxy to the disposable backend.
- Cleaned up the runtime directory and temporary Vite config after smoke.

URL:

```text
http://127.0.0.1:5175/projects/P1/contact-measurement-setup
```

Observations:

- Initial page showed Contact measurement setup, `Plan - not started`, and `Open measurement plan`.
- After clicking `Open measurement plan`, workspace showed `Plan 2 draft`, target editor, and inline `Draft measurement workbook` section.
- `Preview draft workbook` was enabled; `Generate draft workbook` was disabled before preview.
- After preview:
  - Section showed `DRAFT`.
  - Section showed `Plan 2, Matrix 1, 8 rows`.
  - Section showed a preview fingerprint prefix.
  - `Generate draft workbook` became enabled.
- After generate:
  - `Download draft workbook` link appeared.
  - Link target was `/api/projects/P1/contact-measurement-plan/draft-workbook/files/{artifact_id}`.
  - `download` filename was a contained `P1_contact_measurement_DRAFT_...xlsx` artifact name.
- Browser console warnings/errors after the smoke: `0`.

Screenshot artifact:

- `docs/lane_evidence/artifacts/TASK_361D_qa/task_361d_browser_draft_workbook_generated.png`

Cleanup-warning browser note:

- Normal browser path did not naturally produce a cleanup warning. Warning visibility and nonfatal latest/artifact integrity were verified by component coverage plus direct artifact-store smoke above. QA treats this as sufficient because inducing a cleanup failure in the live browser server would require artificial process-level monkeypatching outside normal operator flow.

## TASK_360B Regression / Scope

- Focused backend suite included `tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py` and `tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py`; both remained passing within the 17-test backend run.
- TASK_361D draft workbook uses editable measurement plan source and separate draft artifact root.
- TASK_360B confirmed preview/generation remains separate and unchanged by QA evidence.

## Product Source Changes By QA

QA did not modify product source or tests. QA wrote this evidence file and saved one screenshot artifact under `docs/lane_evidence/artifacts/TASK_361D_qa/`.

Temporary files/processes used for browser smoke were removed:

- `tmp/TASK_361D_qa_runtime`
- `tmp/vite.task361d.qa.config.mjs`

## Residual Risk

- Browser smoke covered normal DRAFT preview/generate/download-link path with disposable SQLite data.
- Live browser cleanup-warning path was not force-induced; covered by focused component/store/API behavior checks and recorded as non-blocking.
- External dirty residuals remain outside TASK_361D and must be excluded by Integrator packaging: TASK_360Q/R/S planning files, parser residuals, `docs/task_board.md`, and unrelated planning/status artifacts.

## QA Gate Result

`QA gate: pass`

Recommended next role: `Integrator packaging/readiness`

Integrator note: stage only TASK_361D candidate product/test/docs/evidence files and this QA evidence/artifact. Exclude external parser/task-board/planning residuals and unrelated dirty files.
