# TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY

Status: complete - Integrator accepted
Lane: doc-matrix-import-compatibility
Owner: Developer / Reviewer / QA / Integrator
Created: 2026-07-04

## Goal

Allow Matrix Editor `Import Matrix` to accept legacy Word `.doc` files as a compatibility input. The `.doc` file must be opened read-only through the backend Office / Word COM gateway, converted into a temporary `.docx`, and then passed through the existing `.docx` Matrix preview, PDF preview, page/table locator, group selection, and commit flow.

## Why This Is A Formal Lane

This is not a parser rewrite or a quick UI tweak. It crosses Matrix import upload handling, Office COM gateway behavior, temporary file cleanup, frontend file accept behavior, and business-readable failure handling. It must preserve the current `.docx` flow while adding `.doc` as a compatibility wrapper only.

## Current Facts

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` currently uses a hidden file input with `accept=".docx"`.
- `backend/api/routes_project_test_plan.py` currently rejects upload suffixes other than `.docx` with `Only .docx is supported.`.
- `backend/application/project_test_plan_matrix_preview_service.py` currently treats `.doc` as deferred with the blocker: `Legacy .doc product specifications require a Word COM conversion/read gateway in a later task.`
- `backend/infrastructure/office/office_facade.py` already wraps Word document operations and recognizes `.doc` as an Office file kind.
- `backend/infrastructure/office/word_document_gateway.py` currently reads/parses/export-previews only `.docx`, and already contains Word COM helpers for table locations, PDF export, and header reads.
- No formal `TASK_349A_DOCX_MATRIX_PARSER_BUGFIX` source-of-truth file was found during Planner filename search; TASK_350A is independent as long as parser rules remain locked.

## Scope

In scope:

- Accept `.doc,.docx` from Matrix Editor Import Matrix.
- For `.doc`, use backend Office / Word COM gateway conversion into a temporary `.docx`.
- Reuse the existing `.docx` preview/parser/PDF/table-location/group-selection/commit flow after conversion.
- Return business-readable errors when Word COM is unavailable, the `.doc` cannot be opened, conversion fails, or temp cleanup encounters a blocking condition.
- Preserve existing `.docx` behavior and regression tests.

Out of scope:

- Direct PDF parsing.
- Matrix parser rule changes.
- Confirmed Matrix authority, Fee, Test Record, lifecycle, or Matrix business semantic changes.
- Frontend or API route direct Office automation.
- Real user document mutation beyond temporary fixture files.

## May Touch

Future implementation may touch:

- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py` only if needed to remove the `.doc` deferred blocker or keep service-level metadata consistent.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts` only if response/request typing must change; default expectation is no client contract change beyond existing upload helper use.
- Focused backend tests under `tests/unit/` and `tests/integration/`.
- Focused frontend tests under `frontend/src/features/matrix-editor/`.
- TASK_350A task, plan, evidence, and `docs/task_board.md` through normal lane flow.

## Must Not Touch

- Database schema or migrations.
- Matrix parser business rules unless a separate approved dependency is created.
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Workbench lifecycle or Projects registry behavior.
- Real user documents outside controlled temp or fixture paths.
- `.agents/**`, `docs/project_management/**`, release/packaging residuals, and unrelated dirty files.

## Locked Paths

- `backend/infrastructure/storage/**` schema/migration files.
- `backend/modules/test_plan/product_spec_matrix_parser.py` unless Reviewer explicitly approves a parser dependency.
- Confirmed Matrix / Fee / Test Record modules not already part of the existing import flow.
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**` except no Workbench file is expected.
- `frontend/src/pages/ProjectListPage.tsx`
- `.agents/**`
- `docs/project_management/**`

## Validation Gate

Developer must update evidence and run focused validation proving:

- `.docx` upload still follows the original path and existing tests remain green.
- `.doc` upload invokes a conversion gateway, receives a temporary `.docx`, and returns a Matrix preview through the existing parser.
- `.doc` conversion failures map to a business-readable error and leave no temp `.doc` / converted `.docx` leak.
- Page/table selection, Table Title / Content Keyword, Replace/Append, and group selection still reuse the existing logic.
- Frontend file input accepts `.doc,.docx` and still calls the same preview helper.
- `npm run build` passes, or any unrelated pre-existing build blocker is explicitly documented.
- If Windows + Word COM is available, a manual disposable `.doc` smoke is recorded; otherwise the manual Word smoke remains a documented residual while mocked gateway tests cover behavior.

## Merge Gate

- Reviewer plan gate passed per Orchestrator routing context.
- Developer planning-first completed and updated TASK_350A plan/developer evidence.
- Reviewer implementation-readiness passed per Orchestrator routing context.
- User approved TASK_350A reconciliation and Developer implementation.
- Planner source-of-truth reconciliation marks implementation authorized / pending Developer implementation; implementation is not complete.
- Reviewer implementation gate must verify no parser rule or Matrix authority semantics changed.
- QA must verify `.docx` regression, `.doc` compatibility behavior, and temp cleanup/error handling.
- Integrator may package only TASK_350A-scoped files and must exclude current external residuals.

## Source-Of-Truth Reconciliation

Reconciled on 2026-07-04:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`.
- Reviewer implementation-readiness passed.
- User approved reconciliation and Developer implementation.
- TASK_350A is implementation authorized / pending Developer implementation, not complete.

## Integrator Closeout

Closed on 2026-07-04:

- Reviewer implementation re-gate passed.
- QA gate passed with no blocking findings.
- Integrator accepted the package after focused backend tests, MatrixEditorWorkspace frontend tests, compileall, frontend build, staged diff check, staged whitelist/forbidden-path checks, trailing whitespace scan, and static no-real-doc/no-forbidden-scope scans.
- Package includes only TASK_350A backend Office conversion/upload compatibility files, focused tests, MatrixEditorWorkspace accept-list hunk, task/plan/evidence docs, and `docs/task_board.md` closeout.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` is limited to `accept=".docx"` -> `accept=".doc,.docx"`.
- External API-client/New Project/LTR duplicate/release/packaging/temp-stash/Settings/LTR/Basic Information residuals, `.agents/**`, `docs/project_management/**`, real user docs, Workbench, Projects, public folder, parser-rule, direct PDF parsing, Confirmed Matrix, Fee, Test Record, and lifecycle semantic changes were excluded.
- Remote push was intentionally not performed.
