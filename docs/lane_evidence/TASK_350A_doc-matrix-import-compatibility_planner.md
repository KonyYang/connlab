# TASK_350A Doc Matrix Import Compatibility - Planner Evidence

Task: `TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY`
Lane: `doc-matrix-import-compatibility`
Role: Planner
Status: planned - ready for Reviewer plan gate; implementation not authorized
Date: 2026-07-04

## Gate

Planner Discovery Gate / formal lane creation.

## Sources Read

- `AGENTS.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_word_document_gateway.py`
- Current `git status --short`

## Repository Facts

- Matrix Editor upload input currently accepts only `.docx`.
- Matrix preview upload route currently rejects non-`.docx` uploads.
- Matrix preview application service currently treats `.doc` as a deferred blocker requiring a future Word COM conversion/read gateway.
- OfficeFacade and WordDocumentGateway are the existing Office automation boundary.
- WordDocumentGateway already uses Word COM for table locations and PDF export with close/quit cleanup.
- Existing Matrix preview flow already supports page/table locator fields, PDF preview token, and group selection after `.docx` preview.
- No active/formal `TASK_349A_DOCX_MATRIX_PARSER_BUGFIX` or similarly named parser-bugfix task/evidence was found by filename search. Existing parser work appears historical/completed.

## User-Confirmed Facts

- Add `.doc` compatibility without breaking `.docx`.
- Convert `.doc` to temporary `.docx` through Word COM / Office gateway.
- Reuse existing `.docx` Matrix preview/parser/PDF/group-selection/commit flow.
- Clean temporary conversion files.
- Return business-readable errors for Word COM unavailable, open failure, or conversion failure.
- Do not implement PDF parsing.
- Do not change Matrix parser rules or Matrix authority/Fee/Test Record semantics.

## Planner Decision

Create a formal planned lane:

- Task: `TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY`
- Lane: `doc-matrix-import-compatibility`
- Status: `planned`
- Next role: Reviewer plan gate

The lane is independent from parser bugfix work as long as it only converts `.doc` to `.docx` and feeds the existing `.docx` flow. If implementation reveals a parser defect after conversion, the lane must stop and route a separate parser bugfix or Reviewer-approved dependency.

## May Touch

- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py` only if needed for deferred-blocker removal or metadata consistency.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts` only if type changes are necessary.
- Focused backend/frontend tests.
- TASK_350A task, plan, evidence, and board docs.

## Must Not Touch / Locked

- Database schema/migrations.
- Matrix parser business rules unless separately approved.
- Confirmed Matrix authority, Fee Evaluation, Test Record generation.
- Folder workflow, Intake/LTR workflow, Project lifecycle, Projects registry.
- Real user documents outside controlled temp/fixture paths.
- `.agents/**`, `docs/project_management/**`, release/packaging residuals, Basic Information residuals, Settings/LTR residuals, and unrelated dirty files.

## Current External Residuals Excluded

Current worktree contains unrelated modified/untracked files, including but not limited to:

- Intake/form selection and duplicate-resolution backend residuals.
- New Project / specified-LTR / precheck frontend residuals.
- `frontend/src/api/client.ts` and `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` existing dirty hunks.
- Release/packaging/desktop residuals and `temp_agents_stash.md`.

This Planner pass does not package or approve those residuals. Future TASK_350A implementation must isolate any hunks in shared files from unrelated residuals before review/integration.

## Files Created / Updated

- `tasks/TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY.md`
- `docs/task_350a_doc_matrix_import_compatibility_plan.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_planner.md`
- `docs/task_board.md`

## Validation

- `git diff --check -- docs/task_board.md tasks/TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY.md docs/task_350a_doc_matrix_import_compatibility_plan.md docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_planner.md`: passed with Git CRLF warning for `docs/task_board.md` only.
- Trailing whitespace scan on touched TASK_350A docs/board/evidence: no matches.
- Targeted status: Planner-created files are `tasks/TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY.md`, `docs/task_350a_doc_matrix_import_compatibility_plan.md`, `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_planner.md`, plus modified `docs/task_board.md`.
- Product-code status still shows pre-existing external residuals under backend/frontend/tests, including `frontend/src/api/client.ts` and `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`; this Planner pass did not edit product code and does not package those residuals.

## Next Role

Reviewer plan gate.

## Stop Point

Stop after planned lane creation and callback. Do not route Developer and do not write product code.
