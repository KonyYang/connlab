# TASK_352 PDF Matrix Import Deterministic Preview Planner Evidence

Task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Role: Planner
Status: planned - Reviewer plan gate recommended, implementation not authorized
Date: 2026-07-05

## Scope

Planner Discovery Gate and planned lane creation for deterministic text-PDF Matrix import preview. This pass only updates task/plan/evidence/board documents and does not implement product code.

## Required Reads Completed

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `PRODUCT.md` / `DESIGN.md` via `$impeccable` context loader
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts`
- `tests/integration/test_project_test_plan_preview_api.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_qa.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`
- `pyproject.toml`
- Current `git status --short`

## Current Phase / Active Task / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task context: `TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL` is separately implementation-authorized / pending Developer implementation. TASK_352 is a planned future Matrix import lane and must not be mixed into TASK_351.
- Why allowed: the user and Orchestrator explicitly requested Planner Discovery / formal lane creation for PDF Matrix Import and explicitly forbade Developer implementation.

## Confirmed By User

- Add Matrix Editor PDF Matrix import capability.
- Follow existing Word `.docx` / `.doc` Matrix extraction rules/methods where possible.
- First version is text-PDF only.
- No scanned PDF / OCR.
- No AI parsing.
- User supplied four local sample PDF paths.
- User accepted that `GS-12-1507` and `PRODSPEC GS-12-1941` are text PDFs with extractable target Matrix tables.
- User accepted locator facts for two samples: `GS-12-1507` page 8 table 2; `PRODSPEC GS-12-1941` page 11 table 2.

## Confirmed By Repository Evidence

- `.pdf` currently has explicit deferred capability behavior in `ProjectTestPlanMatrixPreviewService`.
- The upload preview route and frontend import modal already support optional page/table/keyword locator fields and preview PDF iframe display.
- Existing Matrix parser accepts neutral tables/paragraphs and selected table index.
- TASK_350A established the compatibility-wrapper pattern by converting `.doc` then reusing existing Matrix preview/parser/commit flow.
- TASK_350B established stale locator Reparse/Replace behavior.
- TASK_350C preserved the existing import file selector flow without native confirm.
- `pyproject.toml` currently does not include an obvious PDF table extraction dependency.

## Inferred By Planner

- TASK_352 should be a formal planned lane because it touches backend parsing boundaries, API upload handling, temp preview tokens, frontend file accept behavior, and QA real-sample smoke.
- The implementation should introduce a deterministic PDF source gateway returning a Word-like neutral snapshot instead of creating a separate Matrix parser or UI workflow.
- A new dependency may be needed, but Developer planning and Reviewer implementation-readiness must validate it before implementation authorization.

## Not Yet Confirmed

No blocker prevents planned lane creation.

Implementation planning must still confirm:

- Deterministic PDF extraction dependency or in-house gateway approach.
- Fixture strategy for the provided PDFs.
- Whether V1 acceptance targets all four sample PDFs or only the two confirmed text-PDF locator cases plus graceful blockers.

## May Touch Draft

- `backend/application/project_test_plan_matrix_preview_service.py`
- New backend PDF gateway under `backend/infrastructure/files/` or `backend/infrastructure/office/`
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection changes
- `backend/modules/test_plan/product_spec_matrix_parser.py` only for adapter-facing compatibility tests, not parser rule changes
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if DTO/type changes are unavoidable
- `pyproject.toml` only if Reviewer approves a deterministic PDF extraction dependency
- Focused backend/frontend tests
- TASK_352 docs/evidence/board through normal lane flow

## Must Not Touch / Locked Paths

Must not touch:

- OCR/scanned-PDF engines
- AI parsing
- Excel Matrix import
- Matrix parser business rules unless separately approved
- Confirmed Matrix authority, Fee Evaluation, Test Record, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects registry/list
- Database schema/migrations unless separately justified and re-gated
- Real sample PDFs except read-only manual/QA smoke
- Real public-drive, workbook, LTR workbook, or project folder data
- Release/settings/basic-information residual cleanup
- `.agents/**`
- `docs/project_management/**`

Locked paths:

- `backend/modules/fee_evaluation/**`
- `frontend/src/features/fee-evaluation/**`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `dist_release/**`
- `packaging/**`
- Real user PDF sources, real `D:\Test Project/**`, real `D:\PublicProject/**`, public-drive roots, and workbook authority files.

## Validation Gate Draft

- Backend PDF gateway unit tests.
- Backend Matrix preview service/API tests for `.pdf` success, locator success/mismatch, no text/scanned-style blocker, no Matrix table, temp/token cleanup, `.docx` regression, and `.doc` regression.
- Frontend MatrixEditorWorkspace focused tests for `.pdf,.doc,.docx` accept, existing import modal/iframe, locator Reparse, stale Replace, Replace/Append/commit regression.
- Build and static checks: `npm run build`, `git diff --check`, trailing whitespace, forbidden-scope status scan.
- QA/manual read-only smoke for provided PDF samples if available.

## Discovery Gate Decision

Definition of Ready for planned lane creation: satisfied.

Definition of Ready for Reviewer plan gate: satisfied.

Definition of Ready for approved implementation: not yet. TASK_352 remains planned and non-executable until Reviewer plan gate, user approval for Developer planning-first, Developer planning-first, Reviewer implementation-readiness, explicit implementation approval, and source-of-truth reconciliation occur.

## Files Created / Updated

- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md`
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_planner.md`
- `docs/task_board.md`

## External Residuals Excluded

Current `git status --short` shows unrelated Settings/LTR, release/packaging, desktop release, and `temp_agents_stash.md` residuals. They are not part of TASK_352 and must not be packaged with this planned lane.

## Planner Validation Checkpoint

- `git diff --check -- docs/task_board.md tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md docs/task_352_pdf_matrix_import_deterministic_preview_plan.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_planner.md`: passed; PowerShell reported the existing LF-to-CRLF warning for `docs/task_board.md` only.
- Trailing whitespace scan on touched TASK_352 docs/board files: passed.
- Targeted TASK_352 status: `docs/task_board.md` modified; TASK_352 task, plan, and Planner evidence are new.
- Targeted product-code status still shows unrelated pre-existing backend/frontend/tests residuals, including Settings/LTR helper files, desktop release files, New Project test residual, and release tests. This Planner pass did not add TASK_352 product implementation changes and those residuals remain excluded from TASK_352.

## Stop Point

Updated 2026-07-06 after Reviewer B1: TASK_352 is planned_blocked on dependency/license decision. See `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_decision_planner.md`.

Recommended next role: User dependency/license decision.

Do not route Developer implementation.
