# TASK_357E Test Record / Report Reuse Matrix Step Quantities Plan

Status: complete/accepted by Integrator
Task: `TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES`
Lane: `test-record-report-reuse-matrix-step-quantities`
Date: 2026-07-08
Role: Planner

## 1. Current Phase / Active Task / Why Allowed

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES` is complete/accepted. `docs/task_board.md` records downstream TASK_357E as a separate required lane.

Current role: Planner.

Why allowed: User/Orchestrator requested the next planned downstream lane after TASK_357A/B/C/D acceptance. This is a Planner Discovery / formal lane creation pass only; no Developer implementation is authorized.

## 2. User Goal Restatement

Test Record and Report-derived outputs should reuse confirmed Matrix Step quantities. Matrix Step setup is the final authority for per-step `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, and derived `total_readings`. Basic Information remains a default source only, and Fee Evaluation remains a passive consumer rather than a source for Test Record / Report quantities. This lane must not implement StepInstance/execution persistence or unrelated Matrix/Fee/LTR/public-drive behavior.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_qa.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_qa.md`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/application/test_record_fee_dataset_preview_service.py`
- Test Record / Report / runtime projection file inventory from targeted search
- current `git status --short`

## 4. Confirmed By User

- TASK_357A/B/C/D are complete/accepted.
- TASK_357E should be the next planned lane.
- Test Record / Report should reuse confirmed Matrix Step quantities.
- Matrix Step quantity authority is the source.
- Basic Information remains default source only.
- Fee Evaluation remains passive and must not become Test Record / Report quantity authority.
- Do not change StepInstance/execution persistence unless separately proven and gated.
- Do not change Matrix parser/import, LTR/public-drive, Fee default-fill, or Basic Information defaults in this lane.

## 5. Confirmed By Repository Evidence

- Board records TASK_357D complete/accepted and says downstream TASK_357E requires a separate lane.
- `ConfirmedMatrixSnapshot` includes `step_quantities`.
- `ConfirmedMatrixStepQuantity` carries group/row/step identity, `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, source/review metadata, and confirmation timestamp.
- `ConfirmedMatrixTestRecordPreviewService` already reads the active Confirmed Matrix snapshot and maps confirmed Matrix cells into Test Record preview steps.
- `ConfirmedMatrixTestRecordDocumentGenerationService` generates Word Test Record drafts from the confirmed Matrix preview and confirmed Basic Information header metadata.
- `TestRecordFeeDatasetPreviewService` is an older/read-only draft dataset preview path and still uses draft payload data rather than confirmed Matrix Step quantity authority.
- TASK_357D accepted scope explicitly excluded Test Record / Report reuse, leaving this as a clean downstream lane.

## 6. Inferred By Planner

- TASK_357E should be backend-led because the core authority projection belongs near confirmed Matrix/Test Record services, not in React.
- A shared Step quantity projection helper may be appropriate if both Test Record preview and later Report consumers need the same facts.
- V1 should prioritize concrete Test Record preview/document-generation reuse because repository evidence shows existing Test Record services. Report should be treated as report-ready projection/read-model boundary unless a current approved Report generation surface is identified in Developer planning-first.
- Missing/review-required Step quantity facts should be surfaced as review metadata or warning rows, not hidden by Basic Information or Fee fallback.

## 7. Not Yet Confirmed

No blocker for a planned lane.

Implementation-level details left for Developer planning-first:

1. Exact Test Record output placement for quantity facts: preview DTO fields, Word template fields/comments, or warnings-only metadata.
2. Whether Report V1 has a concrete existing consumer or should stop at a shared report-ready projection boundary.
3. Exact review metadata wording for missing/review-required/ambiguous Step quantities.

## 8. Planning Risk

- Over-expanding this lane into StepInstance/execution persistence would violate AGENTS scope.
- Treating Basic Information or Fee edits as downstream authority would invert the accepted TASK_357A contract.
- Implementing full Report generation here would likely cross future Report scope without an approved lane.
- Writing quantity logic directly into API routes or frontend would create the UI/business coupling AGENTS forbids.

## 9. Reuse Contract

Source priority:

1. Active confirmed Matrix Step quantities from `ConfirmedMatrixSnapshot.step_quantities`.
2. If no Step quantity authority exists for an output row, surface review-required or existing Test Record behavior according to Developer planning-first; do not read Basic Information as final authority.
3. Do not consume Fee Evaluation edited units as Test Record / Report quantity authority.

Quantity fields:

- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`
- derived/display `total_readings`

Downstream behavior:

- Test Record preview/document generation may display or carry these quantities as planned test setup facts.
- Report support should be a reusable projection boundary for future Report generation, unless existing code provides an approved concrete report consumer.
- StepInstance/execution data remains out of scope. These are planned/confirmed Matrix quantities, not actual execution results.

## 10. May Touch

Future implementation May Touch draft:

- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/application/test_record_fee_dataset_preview_service.py` only if legacy draft dataset preview needs the same projection contract
- a focused backend application helper for confirmed Matrix Step quantity projection, if Developer planning-first shows reuse is cleaner than duplicating logic
- `backend/api/routes_confirmed_matrix_test_record_preview.py` only if response DTOs expose quantity metadata
- `backend/api/routes_confirmed_matrix_test_record_generation.py` only if generated document response metadata changes
- `backend/api/routes_test_record_fee_dataset_preview.py` only if dataset preview response metadata changes
- `backend/infrastructure/office/test_record_document_gateway.py` only if the Test Record Word writer must place quantity metadata into existing template cells or comments
- focused backend unit/integration tests for Test Record preview/document generation and quantity projection
- frontend Matrix Editor Test Record preview/generation tests only if response metadata or user-visible warnings change
- TASK_357E developer/reviewer/QA evidence and board updates through normal lane flow

## 11. Must Not Touch

- Fee Evaluation default-fill or Fee-side quantity editing.
- Matrix Step setup authoring UI or authority mutation.
- Matrix Step quantity storage schema/migration.
- Basic Information quantity defaults or Basic Information mutation.
- StepInstance / execution persistence.
- full Report generation implementation unless a later gate explicitly narrows and approves it.
- Matrix parser/import rules.
- LTR workbook/public-drive authority rules.
- real workbook files, real folders, or public-drive data.
- release/settings/template residual cleanup.
- unrelated dirty files.

## 12. Locked Paths

- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `frontend/src/features/fee-evaluation/**`
- `frontend/src/features/matrix-editor/**` except focused Test Record preview/generation UI tests if Reviewer approves metadata wiring
- `backend/application/matrix_step_quantity_service.py`
- Matrix Step quantity storage models/repositories except read-only type imports if unavoidable
- `backend/application/project_basic_information_service.py`
- `frontend/src/features/project-basic-information/**`
- Matrix parser/import implementation paths
- LTR/public-drive implementation paths
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

## 13. Dependencies

- TASK_357A defines the authority contract.
- TASK_357B provides Basic Information defaults only.
- TASK_357C provides confirmed Matrix Step quantity authority.
- TASK_357D confirms Fee is only a passive consumer and not an authority for Test Record / Report.

Serial dependency: TASK_357E implementation should wait for TASK_357A/B/C/D acceptance, which is now satisfied.

Parallelization: no parallel implementation lane is recommended until TASK_357E plan gate clarifies the Report boundary. Test Record and Report-specific wiring could be split later if Developer planning-first finds concrete Report scope exceeds a read-model boundary.

## 14. Validation Gate Draft

Backend unit tests:

- Test Record preview includes or exposes Step quantity metadata from confirmed Matrix Step quantities.
- Missing confirmed Step quantity facts surface review-required metadata/warnings instead of Basic Information fallback.
- Review-required Step quantity records remain review-required downstream.
- Test Record generation consumes the same preview/projection facts without mutating Matrix Step authority.
- Fee Evaluation edited units do not influence Test Record / Report quantity facts.

Backend integration/API tests:

- Confirmed Matrix Test Record preview endpoint returns expected quantity metadata or warnings.
- Test Record generation endpoint remains compatible and, if applicable, writes quantity facts into the existing output path without real template/user-file mutation outside temp fixtures.
- Existing Test Record preview/generation regressions pass.

Frontend tests only if UI metadata changes:

- Matrix Editor Test Record preview/generation messaging shows compact review cues if backend exposes them.
- Existing Test Record preview/generation actions remain available under current lifecycle/readiness gates.

General validation:

- focused pytest for touched Test Record services/routes.
- focused frontend tests if frontend touched.
- `npm run build` if frontend touched.
- `py -m py_compile` for touched backend modules.
- `git diff --check`.
- trailing whitespace scan.
- forbidden-scope scan for Fee, Matrix Step mutation, Basic Information, Matrix parser/import, StepInstance, LTR/public-drive, real folders/workbooks, release/settings residuals, `.agents/**`, and `docs/project_management/**`.

## 15. Merge Gate Draft

- Reviewer plan gate pass before Developer planning-first.
- User approval required before Developer planning-first.
- Developer planning-first evidence must refine Test Record DTO/document placement, Report projection boundary, review metadata policy, tests, and package isolation.
- Reviewer implementation-readiness pass before implementation authorization.
- User approval and source-of-truth reconciliation before Developer implementation.
- QA required if Test Record output/preview behavior changes.
- Integrator packaging must isolate TASK_357E files from existing release/settings/template residuals.

## 16. Definition Of Ready

Definition of Ready for planned lane creation is satisfied:

- user goal and scenario are clear;
- board state and upstream dependencies are verified;
- existing Test Record services and confirmed Matrix Step quantity domain facts were checked;
- May Touch / Must Not Touch / Locked Paths are concrete;
- validation and merge gates are named;
- non-goals prevent StepInstance, full Report generation, Fee, Basic Information, Matrix parser, and LTR/public-drive scope creep.

Lane remains planned only. Implementation is not authorized.

## 17. Recommendation

Create planned TASK_357E and route next to Reviewer plan gate.

Blocking questions: none.

## 18. Developer Planning-First Update - 2026-07-08

Status: Developer planning-first complete. Product implementation remains not authorized.

### 18.1 Source-Of-Truth Note

`docs/task_board.md` still contains older wording that lists TASK_357E as planned for Reviewer plan gate, but `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reviewer.md` records `reviewer_plan_gate_pass`, and the User/Orchestrator delegation approves Developer planning-first. This pass is docs-only and does not start implementation.

### 18.2 Repository Facts Confirmed By Developer

- `ConfirmedMatrixSnapshot.step_quantities` is already available in `backend/domain/confirmed_matrix_authority_models.py`.
- `ConfirmedMatrixTestRecordPreviewService` currently maps active confirmed Matrix groups/rows/cells into preview groups and steps, including parsed step token sequence/raw token/suffix, but it does not attach Step quantity facts.
- `routes_confirmed_matrix_test_record_preview.py` currently exposes step fields `sequence`, `raw_token`, `test_item`, `section`, `method`, `condition`, and `requirement`.
- `ConfirmedMatrixTestRecordDocumentGenerationService` generates Word drafts from the preview service result, so preview-level quantity projection is the safest single source for document generation.
- `TestRecordDocumentGateway.generate_from_confirmed_matrix(...)` currently writes the existing group/step preview facts into the template-backed document. It has no quantity-specific placement today.
- `TestRecordFeeDatasetPreviewService` is legacy draft-payload based. It should remain out of V1 unless implementation discovers a compatibility requirement; it must not become a competing authority.
- No concrete current full Report generation consumer was identified for confirmed Matrix Step quantities. Report support should stop at a reusable projection/read-model boundary in this lane.

### 18.3 Implementation Strategy

Use a backend-led shared projection:

1. Add a focused application helper such as `backend/application/confirmed_matrix_step_quantity_projection.py`.
2. The helper consumes active `ConfirmedMatrixSnapshot.step_quantities` plus parsed preview step tokens and produces read-only quantity facts keyed by:
   - `confirmed_group_id`
   - `confirmed_row_id`
   - `step_sequence`
   - normalized `step_suffix_note`
3. Extend `ConfirmedMatrixTestRecordPreviewStep` with an optional quantity projection, not editable fields.
4. Route/API DTO should expose quantity metadata only if implementation changes user-visible preview/API behavior.
5. Document generation should reuse the same preview/projection facts. V1 should prefer carrying metadata through the existing `groups` object; only touch the Word gateway if a clear template placement exists and tests can assert it safely.
6. Report V1 should not add full Report generation. If a later Report consumer appears, it should consume the same projection helper.

### 18.4 Proposed Projection Shape

Recommended backend dataclass shape:

```python
@dataclass(frozen=True, slots=True)
class ConfirmedMatrixStepQuantityProjection:
    step_token: str
    step_sequence: int
    step_suffix_note: str | None
    test_points_per_sample: str | None
    readings_per_point: str | None
    contact_points_per_sample: str | None
    total_readings: str | None
    status: Literal["ready", "review_required", "missing", "not_applicable"]
    source: str | None
    review_reason: str | None
```

Policy:

- `total_readings` is derived as `test_points_per_sample * readings_per_point` only when both fields are valid non-negative decimals.
- `contact_points_per_sample` is carried as authority metadata, not used as a substitute for total readings.
- Missing Step quantity for a parsed Matrix Step should be `missing` or `review_required` depending on rule applicability; implementation should avoid inventing values from Basic Information or Fee.
- Existing `review_required=True` Step quantity records remain `review_required` downstream.
- Non-quantity-relevant Test Record rows may use `not_applicable` or omit the projection if that keeps DTO compatibility cleaner.

### 18.5 Test Record Consumer Policy

V1 concrete consumer: confirmed Matrix Test Record preview/document generation.

- Preview should expose quantity facts or compact warnings per Step.
- Generated Test Record document should reuse preview facts. If exact template cells are not available, V1 may preserve document layout and expose warning/metadata through the service result/API rather than writing ad hoc text into the Word body.
- Existing LLCR requirement splitting must remain compatible with projected quantity metadata.
- No Step execution result, evidence, pass/fail, image, or StepInstance lifecycle state is introduced.

### 18.6 Report Boundary Decision

No approved concrete full Report consumer exists in current repository scope. TASK_357E should only create a report-ready projection boundary that later Report work can reuse. Implementation should stop and request Planner/User re-gate if it needs:

- full Report generation,
- Report template placement,
- StepInstance/execution persistence,
- actual measured result fields,
- report approval lifecycle.

### 18.7 Exact Future May Touch

Recommended implementation May Touch:

- `backend/application/confirmed_matrix_step_quantity_projection.py` (create)
- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/application/confirmed_matrix_test_record_document_generation_service.py` only to pass through preview quantity metadata if needed
- `backend/api/routes_confirmed_matrix_test_record_preview.py` only if response DTO exposes quantity metadata/warnings
- `backend/api/routes_confirmed_matrix_test_record_generation.py` only if generation response metadata changes
- `backend/infrastructure/office/test_record_document_gateway.py` only if tested template-safe placement is implemented
- `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/integration/test_confirmed_matrix_test_record_preview_api.py` if route DTO changes
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py` if generation response changes
- focused gateway tests only if the Word gateway is touched
- frontend Matrix Editor Test Record tests only if user-visible API metadata or copy changes
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_developer.md`

Keep `backend/application/test_record_fee_dataset_preview_service.py` out of V1 unless a focused compatibility test proves the legacy draft preview must expose the same projection. If touched, Developer evidence must justify it explicitly.

### 18.8 Must Not Touch / Locked Paths

Locked:

- Fee Evaluation default-fill, Fee draft, Fee export, and Fee-side quantity editing.
- Matrix Step quantity setup service, storage models, repositories, schema/migration, or authoring UI.
- Basic Information mutation or use as final Test Record/Report authority.
- StepInstance/execution persistence, execution data, images, evidence, and lifecycle.
- Full Report generation, Report templates, Report approval lifecycle, and report output placement.
- Matrix parser/import rules.
- LTR workbook/public-drive authority and real workbook/folder/public-drive data.
- release/settings/template residual cleanup.
- `.agents/**` and `docs/project_management/**`.

### 18.9 Validation Plan

Backend unit tests:

- Preview step includes ready Step quantity projection when active confirmed Step quantity matches group/row/step/suffix.
- Preview reports missing/review-required quantity projection when a parsed Step token has no matching Step quantity record.
- Preview preserves review-required Step quantity records with review reason.
- Preview derives `total_readings` only from valid `test_points_per_sample * readings_per_point`.
- Preview does not read Basic Information defaults or Fee edited units.
- Existing LLCR requirement splitting and token order tests still pass.
- Document generation passes the same preview groups/projections to the writer without mutating Matrix Step authority.

API tests if DTO changes:

- `GET /api/projects/{project_id}/confirmed-matrix/test-record-preview` returns quantity metadata/warnings.
- Existing no-active and empty-preview responses remain compatible.

Frontend tests only if UI changes:

- Existing Test Record preview/generation controls remain available under current readiness gates.
- Compact review-required message appears only if backend exposes user-visible quantity warnings.

General validation:

- focused pytest for touched Test Record services/routes.
- `py -m py_compile` for touched backend modules.
- `npm test -- MatrixEditorWorkspace --run` and `npm run build` if frontend touched.
- `git diff --check`.
- trailing whitespace scan on touched files.
- line-count scan for new/touched Python files.
- forbidden-scope scan for Fee, Matrix Step setup/storage mutation, Basic Information mutation, StepInstance, full Report generation, Matrix parser/import, LTR/public-drive, real folders/workbooks, `.agents/**`, `docs/project_management/**`, release/package residuals.

### 18.10 Package Isolation Risks

- Existing `backend/api/dependencies.py`, release/settings/template helpers, desktop packaging files, TASK_357A docs, and `temp_agents_stash.md` are external residuals and must remain excluded.
- `frontend/src/features/matrix-editor/**` is broadly active in earlier lanes; touch it only if response metadata creates a real UI regression target.
- `test_record_fee_dataset_preview_service.py` is legacy draft-based. Including it without a current confirmed-authority need would blur source authority.

### 18.11 Developer Recommendation

Recommended next role: Reviewer implementation-readiness gate.

Blocking summary: none for planning-first.

Implementation remains unauthorized until Reviewer readiness passes, User approves implementation, and source-of-truth reconciliation records implementation authorization.

## 19. Planner Source-Of-Truth Reconciliation - 2026-07-08

Status: complete/accepted by Integrator.

Reconciled gate chain:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only planning.
- Reviewer implementation-readiness passed.
- User approved continuation, source-of-truth reconciliation, and Developer implementation.

Implementation authorization scope:

- backend shared confirmed Matrix Step quantity projection helper;
- Test Record preview/document generation as V1 concrete consumer;
- optional DTO/API metadata only if exposed by existing Test Record path;
- Report support limited to projection/read-model boundary only unless a concrete approved consumer exists;
- confirmed Matrix Step quantities are authority;
- Basic Information remains defaults only;
- Fee remains passive and is not downstream authority.

Locks preserved:

- no StepInstance/execution persistence;
- no full Report generation;
- no Fee default-fill changes;
- no Matrix Step setup/storage mutation or schema changes;
- no Basic Information mutation or final authority consumption;
- no Matrix parser/import changes;
- no LTR/public-drive/real workbook/folder changes;
- no release/settings residual cleanup;
- no `.agents/**` or `docs/project_management/**`;
- no remote push.

Developer implementation pass, Reviewer gate, QA gate, and Integrator packaging/readiness are complete.

## 20. Integrator Acceptance - 2026-07-08

Status: complete/accepted by Integrator.

Accepted package:

- confirmed Matrix Step quantity projection helper.
- Test Record preview/API quantity metadata.
- Test Record document-generation pass-through of the same preview quantity objects.
- focused Test Record preview/document/API tests.
- TASK_357E task, plan, Developer/Reviewer/QA/reconciliation evidence.
- `docs/task_board.md` closeout isolated from external residuals.

Validation summary:

- focused Test Record preview/document/API suite: 30 passed.
- py_compile passed for touched backend modules/routes.
- frontend build passed with existing Vite chunk-size warning only.
- staged diff, whitespace, line-count, whitelist, and forbidden-scope checks passed.

Remote push was intentionally not performed.
