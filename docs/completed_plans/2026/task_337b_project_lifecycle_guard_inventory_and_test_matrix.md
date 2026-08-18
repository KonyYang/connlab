# TASK_337B Project Lifecycle Guard Inventory And Test Matrix

Last Updated: 2026-06-26
Status: ready_for_review
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Lane: guard-inventory
Role: Developer/Test

## 1. Purpose

This document inventories ConnLab project-scoped operations that must respect the lifecycle contract from `TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT`.

It is documentation and test planning only. It does not implement lifecycle guards, change routes, change services, create schema, or change frontend/runtime behavior.

## 2. Source Baseline

Inputs read for this lane:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`

Additional source scan:

- `backend/api/routes_*.py`
- related `backend/application/*` service names from route wiring
- existing lifecycle tests:
  - `tests/unit/test_project_lifecycle_service.py`
  - `tests/unit/test_project_lifecycle_management_service.py`
  - `tests/integration/test_project_lifecycle_gating_api.py`

Finding:

- `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md` was not present at execution time.
- The lane was still approved by `docs/task_board.md` and `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`.
- This lane therefore uses the approved board/evidence scope and does not create a task file because `tasks/` is not in this lane's `May Touch`.

## 3. Lifecycle Guard Rules From TASK_336

Lifecycle states:

```text
active
stopped
closed
```

Closure types:

```text
null
completed
administrative
```

Expected behavior:

| Operation class | Active | Stopped | Closed completed | Closed administrative |
|---|---|---|---|---|
| Read current state | Allow | Allow | Allow | Allow |
| Read-only preview that does not mutate files or records | Allow | Allow, unless it prepares a write-only workflow | Allow, unless it prepares a write-only workflow | Allow, unless it prepares a write-only workflow |
| Write DB project data | Allow by existing business rules | Block with lifecycle 409 | Block with lifecycle 409 | Block with lifecycle 409 |
| Write files, Office documents, public drive, or project folder | Allow by existing business rules | Block with lifecycle 409 | Block with lifecycle 409 | Block with lifecycle 409 |
| Stop project | Allow | Idempotent/no-op or business-specific reject to define in TASK_337A | Block | Block |
| Resume project | Not applicable | Allow | Block | Block |
| Close project | Allow | Allow | Block | Block |

Guard error contract:

```text
HTTP status: 409 Conflict
Error code: project_lifecycle_readonly
Stopped message: This project is stopped. Resume it before making changes.
Closed completed message: This project is closed as completed and is readonly.
Closed administrative message: This project is closed administratively and is readonly.
```

## 4. Inventory Classification

Classification keys:

| Key | Meaning |
|---|---|
| READ | Does not mutate ConnLab records, files, Office documents, public-drive files, or authoritative external workbooks |
| PREVIEW_READONLY | Calculates a plan or snapshot without mutation; allowed for readonly lifecycle states unless it starts a write-only workflow |
| PROJECT_WRITE | Mutates project-owned DB records or project lifecycle data |
| AUTHORITY_WRITE | Mutates Matrix, Fee, Basic Information, LTR, output record, or other authority data |
| FILE_WRITE | Creates, updates, deletes, copies, or repairs files/folders |
| OFFICE_WRITE | Writes Word/Excel through Office or document gateways |
| EXTERNAL_WRITE | Writes public-drive or external workbook authority |
| LIFECYCLE_ACTION | Stop/resume/close action itself |
| OUT_OF_SCOPE | Not project lifecycle scoped or maintenance/admin flow; should be reviewed separately before broad guarding |

## 5. Project Lifecycle Actions

| Route/service | Class | Active | Stopped | Closed | TASK_338 test expectation |
|---|---|---|---|---|---|
| `POST /api/projects/{project_id}/stop` -> `ProjectLifecycleManagementService.stop_project` | LIFECYCLE_ACTION | Allow | Define idempotent/reject behavior in backend lifecycle task | Block | API tests for active stop, stopped repeat handling, closed reject |
| Future resume route from TASK_336 | LIFECYCLE_ACTION | Not applicable | Allow | Block | API tests for stopped resume and closed reject |
| Future close-completed route from TASK_336 | LIFECYCLE_ACTION | Allow for formal/registered projects with manual confirmation/output summary | Allow for formal/registered stopped projects | Block | API tests for registered active/stopped allow, temporary/no-LTR reject or administrative default |
| Future close-administrative route from TASK_336 | LIFECYCLE_ACTION | Allow with required reason | Allow with required reason | Block | API tests for required reason and closed reject |
| `DELETE /api/projects/{project_id}/temporary` -> `delete_temporary_project` | PROJECT_WRITE | Allow by existing temporary-delete policy | Block unless future task explicitly permits cleanup for stopped temporary projects | Block | API tests for stopped/closed reject before deletion |
| `POST /api/projects` and `POST /api/projects/temporary` | PROJECT_WRITE | Not applicable to existing project lifecycle | Not applicable | Not applicable | No lifecycle guard; creation remains governed by New Project rules |

## 6. Authority Draft And Confirmation Guards

These operations must be blocked for stopped and closed projects because they mutate project authority, drafts, or confirmed state.

| Area | Route/service | Class | Active | Stopped/Closed expectation | Proposed tests |
|---|---|---|---|---|---|
| Basic Information | `PUT /api/projects/{project_id}/basic-information/draft` -> `ProjectBasicInformationService.save_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | Unit service guard + integration API stopped/closed cases |
| Basic Information | `POST /api/projects/{project_id}/basic-information/confirm` -> `ProjectBasicInformationService.confirm` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API test confirms no new confirmed snapshot |
| Matrix draft | `POST /api/projects/{project_id}/matrix-drafts` -> `ProjectMatrixDraftPersistenceService.create_from_source_import` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Matrix draft | `PUT /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}` -> `update_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | Unit/API tests preserve existing draft |
| Matrix authority | `POST /api/projects/{project_id}/matrix-drafts/{id}/confirm` -> `ConfirmedMatrixAuthorityService.confirm_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API test confirms no active snapshot changes |
| Matrix revision | `POST /api/projects/{project_id}/matrix-revisions` -> `MatrixRevisionFlowService.create_revision_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Matrix revision | `POST /api/projects/{project_id}/matrix-drafts/{id}/confirm-revision` -> `MatrixRevisionFlowService.confirm_revision_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Matrix editor session | `PUT /api/projects/{project_id}/matrix-editor/session/draft` -> `MatrixEditorSessionService.save_editor_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | Existing editor session tests extended for readonly states |
| Matrix editor session | `DELETE /api/projects/{project_id}/matrix-editor/session/draft` -> `discard_editor_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | Prove stopped cannot discard mutable draft state |
| Matrix editor session | `POST /api/projects/{project_id}/matrix-editor/session/confirm` -> `confirm_session` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Source matrix import | `POST /api/projects/{project_id}/matrix-import/commit` -> `MatrixImportCommitService.commit` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Legacy test-plan draft | `POST /api/projects/{project_id}/test-plan/drafts` -> `ProjectTestPlanDraftService.create_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Legacy test-plan draft | `PUT /api/projects/{project_id}/test-plan/drafts/{draft_id}` -> `update_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Legacy matrix edit | `PUT /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix` -> `ProjectTestPlanMatrixEditService.update_matrix_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Legacy matrix confirm | `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix/confirm` -> `ProjectTestPlanMatrixEditService.confirm_matrix_draft` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Fee pricing draft | `PUT /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft` -> `FeeEvaluationPricingDraftPersistenceService.save` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Fee pricing draft | `DELETE /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft` -> `discard` | AUTHORITY_WRITE | Allow by current rules | Block 409 | Prove stopped cannot discard mutable fee draft |
| Confirmed Fee | `POST /api/projects/{project_id}/confirmed-fee/versions` -> `ConfirmedFeeVersionService.confirm` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Output records | `POST /api/projects/{project_id}/output-records` -> `ProjectOutputRecordService.register_output` | AUTHORITY_WRITE | Allow for controlled service/internal use | Block direct external write | API stopped/closed cases if route remains public |

## 7. File, Office, Folder, And External Authority Guards

These operations must be blocked for stopped and closed projects because they write files, Office documents, public-drive targets, or external workbook authority.

| Area | Route/service | Class | Active | Stopped/Closed expectation | Proposed tests |
|---|---|---|---|---|---|
| Project folder | `POST /api/projects/{project_id}/folder/generate` -> `FolderService.generate_folder` | FILE_WRITE | Allow by current lifecycle gates | Block 409 | Existing folder API tests add stopped/closed states |
| Official workspace | `POST /api/projects/{project_id}/official-workspace/create` -> `OfficialProjectWorkspaceService.create` | FILE_WRITE | Allow by current rules | Block 409 | API tests prove no workspace record/file creation |
| Official folder repair | `POST /api/projects/{project_id}/official-folder/repair-folders` -> `OfficialProjectFolderCheckService.repair_folders` | FILE_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Request material | `POST /api/projects/{project_id}/request-material/collect` -> `ProjectRequestMaterialCollectionService.collect` | FILE_WRITE | Allow by current rules | Block 409 | Unit/API tests prove no copied files or collection record |
| Required forms | `POST /api/projects/{project_id}/project-folder/required-forms/generate` -> `ProjectFolderRequiredFormsService.generate` | FILE_WRITE/OFFICE_WRITE/AUTHORITY_WRITE | Allow by current rules | Block 409 | API tests for stopped/closed before staging/generation |
| Application Form write-back | `POST /api/projects/{project_id}/project-folder/application-form/write-back` -> `ProjectApplicationFormWriteBackService.write_back` | OFFICE_WRITE/AUTHORITY_WRITE | Allow by current rules | Block 409 | Unit/API tests prove Office port is not called |
| Section 2 sync | `POST /api/projects/{project_id}/section2-sync` -> `ProjectSection2SyncService.sync` | OFFICE_WRITE/PROJECT_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Section 2 write-back | `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-write-back` -> `Section2WriteBackService.write_back` | OFFICE_WRITE | Allow by current rules | Block 409 | Unit/API tests prove Word gateway not called |
| LTR registration | `POST /api/projects/{project_id}/ltr` -> `LtrService.register_ltr` | AUTHORITY_WRITE | Allow by current rules | Block 409 | Existing closed test expanded to stopped/closed lifecycle overlay |
| Local LTR commit | `POST /api/projects/{project_id}/ltr/commit` -> `LtrLocalCommitService.commit_project` | AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| LTR workbook commit | `POST /api/projects/{project_id}/ltr-workbook/write-commit` -> `LtrWorkbookWriteCommitService.commit_project` | EXTERNAL_WRITE | Allow by current rules | Block 409 | API tests prove workbook authority not touched |
| LTR Basic Information workbook sync | `POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/commit` -> `LtrWorkbookBasicInformationSyncService.commit` | EXTERNAL_WRITE | Allow by current rules | Block 409 | Unit/API tests prove gateway commit not called |
| Public-drive upload | `POST /api/projects/{project_id}/public-drive/upload` -> `PublicDriveUploadService.upload` | EXTERNAL_WRITE/FILE_WRITE | Allow by current rules | Block 409 | Unit/API tests prove file gateway not called |
| Approval package execute | `POST /api/projects/{project_id}/approval-package/execute` -> `ApprovalPackageService.execute` | FILE_WRITE/AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Customer Feedback generation | `POST /api/projects/{project_id}/customer-feedback/generate` -> `CustomerFeedbackFormGenerationService.generate` | FILE_WRITE/OFFICE_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Confirmed Matrix Fee export | `POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export` -> `ConfirmedMatrixFeeEvaluationExportService.export` | FILE_WRITE/OFFICE_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Confirmed Matrix Fee file generation | `POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/file/generate` -> `generate_confirmed_matrix_fee_file` | FILE_WRITE/OFFICE_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Confirmed Matrix Test Record draft | `POST /api/projects/{project_id}/confirmed-matrix/test-record-draft/generate` -> `ConfirmedMatrixTestRecordDocumentGenerationService.generate` | FILE_WRITE/OFFICE_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Matrix editor Test Record draft | `POST /api/projects/{project_id}/matrix-editor/test-record-draft/generate` -> `MatrixEditorTestRecordDocumentGenerationService.generate` | FILE_WRITE/OFFICE_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Test Record/Fee documents | `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-documents/generate` -> `TestRecordFeeDocumentGenerationService.generate` | FILE_WRITE/OFFICE_WRITE/AUTHORITY_WRITE | Allow by current rules | Block 409 | API stopped/closed cases |
| Evidence place | `POST /api/projects/{project_id}/evidence/place` -> `EvidencePlacementService.place_project` | FILE_WRITE | Future-scope-ish existing route; allow by current rules | Block 409 | API stopped/closed cases if route remains active |

## 8. Read-Only Or Preview Routes

These routes should stay available for stopped and closed projects if they do not mutate records or files. TASK_338 should verify representative cases and make exceptions explicit.

| Route/service | Class | Expected readonly behavior | Proposed tests |
|---|---|---|---|
| `POST /api/projects/{project_id}/folder/preview` -> `FolderService.preview_folder` | PREVIEW_READONLY | Allow for stopped/closed if no file writes occur | Existing folder preview tests add stopped/closed allow cases |
| `POST /api/projects/{project_id}/approval-package/preview` -> `ApprovalPackageService.preview` | PREVIEW_READONLY | Allow; package execution remains blocked | API stopped/closed allow preview + execute blocked |
| `POST /api/projects/{project_id}/evidence/placement-preview` | PREVIEW_READONLY | Allow if no file writes occur | API stopped/closed allow preview + place blocked |
| `POST /api/projects/{project_id}/ltr/renumber-preview` | PREVIEW_READONLY | Allow only if it remains pure preview | API stopped/closed allow or explicitly classify as write-preparation blocked |
| `POST /api/projects/{project_id}/ltr-workbook/write-preview` | PREVIEW_READONLY/EXTERNAL_READ | Allow only if workbook read is readonly and no lock/save/backup occurs | API stopped/closed allow preview; commit blocked |
| `POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/open-readonly` | READ/EXTERNAL_READ | Allow because it opens workbook readonly for inspection | API stopped/closed allow unless future policy blocks external app launch |
| `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix/validate` | PREVIEW_READONLY | Allow if it does not save or mutate draft state | API stopped/closed allow validation |
| `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-preview` | PREVIEW_READONLY | Allow if it only previews completion data | API stopped/closed allow preview |
| `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-dataset-preview` | PREVIEW_READONLY | Allow if it only builds dataset preview | API stopped/closed allow preview |
| `POST /api/projects/{project_id}/test-plan/source-candidates/{source_asset_id}/matrix-preview` | PREVIEW_READONLY | Allow if it only parses candidate without persistence | API stopped/closed allow preview |
| `POST /api/runtime-projection/read-only-snapshot` | READ | Allow; route is explicitly read-only | Existing runtime projection read-only tests can cover closed/stopped if project-bound |

Policy note:

If a preview currently mutates cache, selection state, draft state, output records, file locks, backups, or recent-path state, TASK_338 should reclassify that route as WRITE and guard it for stopped/closed projects.

## 9. New Project, Intake, Lookup, And Maintenance Boundaries

These routes are not primary targets for project lifecycle guards because they operate before a project exists, operate on intake packages/cases, or perform admin maintenance. They still need separate care if they reference an existing project.

| Area | Routes | TASK_337B classification |
|---|---|---|
| Intake import/upload/select/draft/precheck routes under `/api/intake-*`, `/api/application-forms/*`, `/api/precheck-issues/*` | Mostly intake package/case writes before project lifecycle exists | OUT_OF_SCOPE for project lifecycle guard; keep governed by intake/draft rules |
| `POST /api/intake-cases/{case_id}/complete-new-project` | Creates/formalizes project from intake case | OUT_OF_SCOPE for existing-project readonly guard; future tests should ensure it cannot mutate an already stopped/closed project if case is linked |
| Frozen field revision request | `POST /api/intake-cases/{case_id}/frozen-field-revision-requests` | OUT_OF_SCOPE for direct project writes; if project-linked revision workflow later applies changes, application path must be guarded |
| Lookup import/config and external resource settings | `/api/lookups/import-config`, `/api/external-resources/*` | OUT_OF_SCOPE global/admin settings, not project lifecycle |
| Cleanup routes | `/api/cleanup/project-ltr/no-ltr-projects/execute`, `/api/cleanup/intake-drafts/duplicate-history/execute` | OUT_OF_SCOPE maintenance; do not mix into TASK_338 without separate approval |
| Project creation | `POST /api/projects`, `POST /api/projects/temporary` | OUT_OF_SCOPE for existing project lifecycle; creation rules remain separate |

## 10. TASK_338 Recommended Test Matrix

TASK_338 should add a shared lifecycle fixture/helper, then cover a focused set of high-risk write categories before broad endpoint-by-endpoint expansion.

### 10.1 Shared Test Helper

Recommended helper responsibilities:

- create active project
- create stopped project
- create closed completed project
- create closed administrative project
- optionally create formal/registered vs temporary/no-LTR identity
- assert lifecycle block response:
  - status `409`
  - code `project_lifecycle_readonly`
  - lifecycle state and closure type where response supports structured fields
  - no downstream gateway/repository write called for unit tests

### 10.2 Minimum Unit Tests

| Service boundary | Active expectation | Stopped/closed expectation |
|---|---|---|
| Lifecycle guard service from TASK_337A | Allows read/preview and active writes | Blocks write classes with 409 contract |
| `ProjectBasicInformationService` | save/confirm current behavior unchanged | save/confirm blocked before repository write |
| `MatrixEditorSessionService` or `ProjectMatrixDraftPersistenceService` | draft/confirm current behavior unchanged | draft/confirm blocked before authority changes |
| `FeeEvaluationPricingDraftPersistenceService` and `ConfirmedFeeVersionService` | save/confirm current behavior unchanged | save/confirm blocked before repository write |
| `ProjectFolderRequiredFormsService` | generate current behavior unchanged | blocked before file/Office/output registration calls |
| `LtrWorkbookBasicInformationSyncService` or workbook commit service | commit current behavior unchanged | blocked before workbook gateway write |
| `PublicDriveUploadService` | upload current behavior unchanged | blocked before file copy/create calls |
| `ProjectApplicationFormWriteBackService` / `Section2WriteBackService` | current behavior unchanged | blocked before Office gateway calls |

### 10.3 Minimum Integration Tests

| Route group | Required tests |
|---|---|
| Basic Information | stopped and both closed types reject draft save and confirm |
| Matrix | stopped and closed reject draft save/import/confirm |
| Fee | stopped and closed reject pricing save/discard and confirmed fee creation |
| Project Folder | stopped and closed reject folder generation and required-forms generation |
| LTR | stopped and closed reject LTR register/local commit/workbook commit/basic-info sync commit; readonly workbook open remains allowed |
| Output generation | stopped and closed reject Test Record, Fee Form, Customer Feedback, Approval Package execute |
| Public-drive/Official folder | stopped and closed reject workspace create, repair folders, request material collect, public-drive upload |
| Readonly previews | stopped and closed can still load representative preview/read endpoints |
| Lifecycle actions | stopped can resume/close; closed cannot resume/stop/close again; completed close formal/registered default scope is enforced |

### 10.4 Regression Rule

Every guarded write path should include at least one assertion proving the downstream mutation did not occur:

- repository not called
- output record count unchanged
- file path not created
- fake Office gateway not called
- fake public-drive/file gateway not called
- external workbook gateway not called

## 11. Known Gaps For Reviewer

- The formal `TASK_337B` task file is missing; this lane used the approved board/evidence scope and did not create a task file because it was outside `May Touch`.
- Endpoint extraction found many `POST` preview routes. TASK_338 must classify each implementation by behavior, not HTTP verb alone.
- Existing lifecycle code uses `ProjectStatus.CANCELLED` for stopped semantics. TASK_336 says this is compatibility only and should not become the long-term product meaning.
- Existing tests cover some historical lifecycle gating but do not cover the new `active/stopped/closed completed/closed administrative` overlay.

## 12. Validation

Documentation validation for this lane:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path docs\task_337b_project_lifecycle_guard_inventory_and_test_matrix.md
Select-String -Path docs\task_337b_project_lifecycle_guard_inventory_and_test_matrix.md -Pattern 'ready_for_review' -Encoding UTF8
Select-String -Path docs\task_337b_project_lifecycle_guard_inventory_and_test_matrix.md -Pattern 'project_lifecycle_readonly' -Encoding UTF8
Select-String -Path docs\task_337b_project_lifecycle_guard_inventory_and_test_matrix.md -Pattern 'TASK_338 Recommended Test Matrix' -Encoding UTF8
Select-String -Path docs\task_337b_project_lifecycle_guard_inventory_and_test_matrix.md -Pattern 'Must not change product behavior' -Encoding UTF8
git diff --check -- docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md docs/lane_evidence/TASK_337B_guard-inventory_developer.md
```

Expected result:

- inventory document exists
- guard contract and test matrix are present
- no backend/frontend/runtime behavior files are changed by this lane
- whitespace check reports no errors; CRLF warnings, if any, are non-blocking

## 13. Stop Point

Stop after this guard inventory/test matrix and lane evidence are ready for review.

Do not execute `TASK_338`, `TASK_340`, backend lifecycle implementation, frontend Workbench implementation, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
