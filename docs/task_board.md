# ConnLab Task Board

> Status: Phase 9 active
> Last Updated: 2026-04-29
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING`
> Current Phase: `Phase 9 - Operator Workflow UI Wiring`

---

## 1. Purpose

This board is stricter than a normal TODO list.

It is the shared execution control document for both humans and AI tools. It defines:

- required read order
- current mainline
- allowed active task
- phase status
- acceptance gates
- what must be updated after each completed task

If conversational memory conflicts with this board, this board wins.

---

## 2. Required Read Order For AI

Every new execution turn must read and obey documents in this order:

1. `AGENTS.md`
2. `docs/task_board.md`
3. current active task file in `tasks/`
4. only then expand any additional referenced docs if the task requires them

Control meaning:

- `AGENTS.md` defines stable rules, MVP boundaries, forbidden scope, and architecture constraints.
- `docs/task_board.md` defines what task is allowed right now.
- `tasks/TASK_XXX_*.md` defines the implementation target and acceptance criteria for that task.

Minimum operator prompt:

```text
Read AGENTS.md first, then docs/task_board.md, then only the current active task file.
Implement only the active task allowed by docs/task_board.md.
Do not skip ahead.
Before coding, state the current phase and active task ID.
After finishing, update docs/task_board.md with status, validation, and next step.
```

---

## 3. Execution Rules

1. Only one active implementation task is allowed at a time unless the board explicitly opens parallel work.
2. A task may move to `done` only after code, tests, and board update are all completed.
3. If a requested task is ahead of the current active task, AI must stop and report the mismatch.
4. If a task uncovers missing prerequisite work, the board must be updated before moving on.
5. Future-scope work is forbidden even if related files already exist in the repository.
6. Project-wide UI rule: any frontend UI, UX copy, layout, visual design, component, navigation, interaction, frontend smoke expectation, UI critique, UI audit, or UI polish work must use `$impeccable` before design or edits. Backend-only, parser-only, storage-only, Office gateway-only, database-only, and non-UI test work is exempt unless it changes UI behavior or user-facing copy.

---

## 4. Current Mainline

Current judgment as of 2026-04-26:

- Repository scaffold is complete.
- Configuration and logging foundation is complete.
- SQLite persistence foundation is complete.
- MVP domain model foundation is complete.
- MVP database models and repositories are complete.
- Project service and thin API foundation are complete.
- Application form parser foundation is complete.
- Deterministic precheck engine is complete.
- Intake/precheck API is complete.
- LTR registration/tracking module is complete.
- Folder generation preview is complete.
- Safe folder generation execution is complete.
- The project is entering shell integration and packaging.
- Minimal frontend shell is complete.
- MVP workflow integration is complete.
- Packaging notes and local run scripts are complete.
- The MVP task sequence is complete.
- Workbench UX modernization is approved as the next controlled phase.
- The UX baseline and decision record is complete.
- The product app shell and left navigation are complete.
- The project dashboard/table-oriented project registry is complete.
- The project detail page now uses a sequential workflow stepper.
- The precheck issue experience now uses business-readable summary and issue cards.
- The intake, LTR, and folder action panels now provide clearer operator guidance.
- Frontend workflow state and API usage are cleaned up.
- Frontend build and smoke validation guard is documented.
- Phase 5 documentation and board sync are complete.
- Phase 6A has been explicitly approved by the user.
- Phase 6A scope is revised around Outlook `.msg` package intake, application form selection, human confirmation, and direct `.docx` import.
- `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` is complete.
- `TASK_026_OFFICE_INTEGRATION_BOUNDARY` is complete.
- `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` is complete.
- `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` is complete.
- `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` is complete.
- `TASK_028A_INTAKE_STORAGE_BOUNDARY` is complete.
- Phase 6A validation is complete.
- Phase 6A plan was completed as split `.msg` import, intake storage, intake UI, confirmation, direct Word intake, and attachment-aware precheck tasks.
- Phase 7 has been explicitly approved by the user.
- `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_037_REAL_SAMPLE_BASELINE` is complete.
- `TASK_038_REAL_DOCX_PARSER_CALIBRATION` is complete.
- `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` is complete.
- `TASK_040_LTR_NUMBER_RULES` is complete.
- `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` is complete.
- `TASK_042_LTR_READINESS_SERVICE_AND_API` is complete.
- `TASK_043_LTR_REGISTRATION_PREVIEW` is complete.
- `TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD` is complete.
- `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC` is complete.
- `TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN` is complete.
- `TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES` is complete.
- `TASK_048_PROJECT_LIFECYCLE_GATING` is complete.
- `TASK_049_EXCEPTION_WORKFLOWS` is complete.
- `TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS` is complete.
- Phase 7 is complete for real sample baseline, parser calibration, LTR readiness/preview, folder evidence placement, lifecycle guards, exception workflows, lookup surfaces, validation, and documentation sync.
- Phase 8 has been explicitly approved by the user for DL-centric project identity hardening.
- `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY` is complete.
- Application `Project #` is optional metadata; internal IDs preserve pre-LTR continuity, and DL/LTR number is the business identity after registration.
- Phase 9 has been explicitly approved by the user after manual smoke testing.
- `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` is complete.
- Phase 9 is activated for frontend operator workflow wiring of existing Phase 7/8 backend capabilities.
- No Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, external LTR workbook mutation, or future-scope work is allowed in Phase 9.

Current stop point:

- `TASK_001_REPOSITORY_SCAFFOLD` is complete.
- `TASK_002_CONFIG_LOGGING` is complete.
- `TASK_003_SQLITE_DATABASE` is complete.
- `TASK_004_DOMAIN_MODELS_MVP` is complete.
- `TASK_005_DATABASE_MODELS_AND_REPOSITORIES` is complete.
- `TASK_006_PROJECT_SERVICE_AND_API` is complete.
- `TASK_007_APPLICATION_FORM_PARSER` is complete.
- `TASK_008_PRECHECK_ENGINE` is complete.
- `TASK_009_INTAKE_PRECHECK_API` is complete.
- `TASK_010_LTR_MODULE` is complete.
- `TASK_011_FOLDER_PREVIEW` is complete.
- `TASK_012_FOLDER_GENERATION` is complete.
- `TASK_013_MINIMAL_FRONTEND_SHELL` is complete.
- `TASK_014_MVP_WORKFLOW_INTEGRATION` is complete.
- `TASK_015_PACKAGING_NOTES` is complete.
- `TASK_016_UX_BASELINE_AND_DECISION_RECORD` is complete.
- `TASK_017_APP_SHELL_LEFT_NAV` is complete.
- `TASK_018_PROJECT_DASHBOARD` is complete.
- `TASK_019_PROJECT_WORKBENCH_STEPPER` is complete.
- `TASK_020_PRECHECK_ISSUE_EXPERIENCE` is complete.
- `TASK_021_INTAKE_LTR_FOLDER_UX` is complete.
- `TASK_022_FRONTEND_STATE_AND_API_CLEANUP` is complete.
- `TASK_023_FRONTEND_TEST_AND_BUILD_GUARD` is complete.
- `TASK_024_PHASE5_DOCS_AND_BOARD_SYNC` is complete.
- `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` is complete.
- `TASK_026_OFFICE_INTEGRATION_BOUNDARY` is complete.
- `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` is complete.
- `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` is complete.
- `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` is complete.
- `TASK_028A_INTAKE_STORAGE_BOUNDARY` is complete.
- `TASK_028B_INTAKE_PACKAGE_ASSET_CASE_STORAGE` is complete.
- `TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION` is complete.
- `TASK_030_FORM_SELECTION_AND_DRAFT_CREATION` is complete.
- `TASK_031A_INTAKE_INBOX_FRONTEND_UX` is complete.
- `TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX` is complete.
- `TASK_031C_INTAKE_CASE_REVIEW_FRONTEND_UX` is complete.
- `TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT` is complete.
- `TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT` is complete.
- `TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE` is complete.
- `TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC` is complete.
- `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_037_REAL_SAMPLE_BASELINE` is complete.
- `TASK_038_REAL_DOCX_PARSER_CALIBRATION` is complete.
- `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` is complete.
- `TASK_040_LTR_NUMBER_RULES` is complete.
- `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` is complete.
- `TASK_042_LTR_READINESS_SERVICE_AND_API` is complete.
- `TASK_043_LTR_REGISTRATION_PREVIEW` is complete.
- `TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD` is complete.
- `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC` is complete.
- `TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN` is complete.
- `TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES` is complete.
- `TASK_048_PROJECT_LIFECYCLE_GATING` is complete.
- `TASK_049_EXCEPTION_WORKFLOWS` is complete.
- `TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS` is complete.
- `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` is complete.
- `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY` is complete.
- `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` is complete.
- Current active implementation task: `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING`.

---

## 5. Phase Status

### Phase 0 - Repository Initialization

Goal:

- establish repository structure
- make FastAPI app importable
- add a passing smoke test

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T0-1 | `TASK_001_REPOSITORY_SCAFFOLD` | done | Scaffold, package init files, `/health`, smoke test completed on 2026-04-25 |

Acceptance gate:

- backend package exists
- minimal FastAPI app imports
- `/health` returns `{"status": "ok"}`
- smoke test passes

### Phase 1 - Backend MVP Foundation

Goal:

- establish configuration, logging, storage foundation, domain skeleton, and application-facing API flow for MVP

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T1-1 | `TASK_002_CONFIG_LOGGING` | done | `Settings.load()` and `configure_logging()` landed with tests on 2026-04-25 |
| T1-2 | `TASK_003_SQLITE_DATABASE` | done | SQLite engine, session factory, Base, `init_db()`, and tests completed on 2026-04-26 |
| T1-3 | `TASK_004_DOMAIN_MODELS_MVP` | done | Pure dataclass domain models and enums completed on 2026-04-26 |
| T1-4 | `TASK_005_DATABASE_MODELS_AND_REPOSITORIES` | done | SQLAlchemy models and repositories completed with temp SQLite tests on 2026-04-26 |
| T1-5 | `TASK_006_PROJECT_SERVICE_AND_API` | done | Project service and `/api/projects` create/list/detail routes completed on 2026-04-26 |

Acceptance gate:

- settings and logger are explicit
- database location comes from settings
- MVP domain objects exist as structured records
- project service and thin API route layer are established

### Phase 2 - Intake And Precheck Flow

Goal:

- parse application form
- run deterministic precheck
- expose intake/precheck API path

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T2-1 | `TASK_007_APPLICATION_FORM_PARSER` | done | DOCX parser with synthetic fixture tests completed on 2026-04-26 |
| T2-2 | `TASK_008_PRECHECK_ENGINE` | done | Deterministic precheck rules completed with rule tests on 2026-04-26 |
| T2-3 | `TASK_009_INTAKE_PRECHECK_API` | done | Upload, parse, precheck, latest, and issue resolve API completed on 2026-04-26 |

Acceptance gate:

- application form fields are parsed into structured records
- precheck is deterministic
- route layer stays thin

### Phase 3 - LTR And Folder Flow

Goal:

- support LTR registration/tracking
- support folder preview and safe generation

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T3-1 | `TASK_010_LTR_MODULE` | done | LTR registration, project lookup, search, and duplicate protection completed on 2026-04-26 |
| T3-2 | `TASK_011_FOLDER_PREVIEW` | done | Template scan, placeholder replacement, and conflict preview completed on 2026-04-26 |
| T3-3 | `TASK_012_FOLDER_GENERATION` | done | Safe folder generation, original application form copy, persistence, and overwrite protection completed on 2026-04-26 |

Acceptance gate:

- LTR is structured and persisted
- folder generation is previewable
- no unsafe overwrite behavior

### Phase 4 - Shell Integration And Packaging

Goal:

- add minimal frontend shell
- connect MVP workflow
- document packaging notes

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T4-1 | `TASK_013_MINIMAL_FRONTEND_SHELL` | done | Minimal React + TypeScript shell with project list/detail and MVP task cards completed on 2026-04-26 |
| T4-2 | `TASK_014_MVP_WORKFLOW_INTEGRATION` | done | Frontend workflow actions, backend full-flow test, and manual smoke checklist completed on 2026-04-26 |
| T4-3 | `TASK_015_PACKAGING_NOTES` | done | Windows local run scripts, README setup/run guide, and packaging notes completed on 2026-04-26 |

Acceptance gate:

- frontend remains minimal
- integration only covers MVP flow
- packaging notes reflect real repository state

### Phase 5 - Workbench UX Modernization

Goal:

- convert the MVP prototype frontend into a modern workflow-oriented ConnLab workbench
- establish left navigation, project dashboard, project workbench, workflow stepper, business-readable issue display, and frontend validation guard

Mandatory project-wide UI rule as applied in Phase 5:

- Use `$impeccable` for every UX/UI design, frontend interface change, visual polish, layout change, UX copy change, component extraction, audit, or critique.
- Before editing UI, load `$impeccable` context and follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Treat ConnLab as `register: product`.
- If the `$impeccable` context files are missing or stale, refresh them before UI work.
- Backend-only bug fixes are exempt from this rule.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T5-1 | `TASK_016_UX_BASELINE_AND_DECISION_RECORD` | done | UX decision record, status vocabulary, target layout, and component structure completed on 2026-04-26 |
| T5-2 | `TASK_017_APP_SHELL_LEFT_NAV` | done | Product app shell, left navigation, top context bar, and hero removal completed on 2026-04-26 |
| T5-3 | `TASK_018_PROJECT_DASHBOARD` | done | Searchable project registry, compact new project panel, status badges, and explicit empty/loading/error states completed on 2026-04-26 |
| T5-4 | `TASK_019_PROJECT_WORKBENCH_STEPPER` | done | Project summary, sequential workflow stepper, single active action panel, and blocked/ready/done/warning states completed on 2026-04-26 |
| T5-5 | `TASK_020_PRECHECK_ISSUE_EXPERIENCE` | done | Business-readable precheck summary, severity badges, issue cards, and mark-reviewed action completed on 2026-04-26 |
| T5-6 | `TASK_021_INTAKE_LTR_FOLDER_UX` | done | Upload metadata panel, latest LTR panel, tree-like folder preview, conflict display, and safer generate affordance completed on 2026-04-26 |
| T5-7 | `TASK_022_FRONTEND_STATE_AND_API_CLEANUP` | done | Workflow state derivation extracted, workbench page reduced, and raw fetch usage guarded to API client on 2026-04-26 |
| T5-8 | `TASK_023_FRONTEND_TEST_AND_BUILD_GUARD` | done | Frontend smoke checklist, root build script, README validation command, and static documentation checks completed on 2026-04-26 |
| T5-9 | `TASK_024_PHASE5_DOCS_AND_BOARD_SYNC` | done | Phase 5 decision record, board state, validation summary, and next-phase recommendation synced on 2026-04-26 |

Acceptance gate:

- left navigation workbench shell exists
- project dashboard is usable by non-programmer lab engineers
- project detail page uses sequential workflow stepper
- precheck issues are business-readable
- application/LTR/folder actions are easier to operate
- existing MVP backend workflow still works
- backend tests pass
- frontend build passes
- manual smoke checklist passes

---

### Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation

Goal:

- introduce the real intake boundary for request materials that usually arrive as an Outlook `.msg` package
- support direct Word `.docx` application form import through the same intake path
- enforce that one selected application form creates one project
- keep parser output as a draft until human review and confirmation
- establish OfficeFacade as the only Office integration boundary

Mandatory Phase 6A rules:

- Do not model one email as one project.
- Use `IntakePackage -> IntakeAsset -> IntakeCase -> IntakeDraft -> Confirm Project` as the planned flow.
- Parser output is draft data only.
- Office-related file reading/extraction must enter through `backend/infrastructure/office/`.
- Phase 6A does not implement Outlook inbox auto-scan, email sending, Matrix, Report, AI review, Excel result ingestion, permissions, LAN deployment, or folder template UX.
- `.msg` handling is split into source import, attachment extraction, and real-sample compatibility instead of one oversized task.
- Intake UI is split into inbox, package detail, and case review instead of one oversized task.
- Intake file storage gets its own boundary before persistence and attachment handling.
- UI changes in Phase 6A follow the project-wide `$impeccable` rule and the `PRODUCT.md` / `DESIGN.md` / `DESIGN.json` context.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T6A-1 | `TASK_025_PHASE6_SCOPE_REVISION_AND_BOARD_ACTIVATION` | done | Phase 6A scope opened, `TASK_026` activated, and static scope checks added on 2026-04-27 |
| T6A-2 | `TASK_026_OFFICE_INTEGRATION_BOUNDARY` | done | OfficeFacade, Word gateway snapshot, Office lifecycle boundary, and gateway placeholders completed on 2026-04-27 |
| T6A-3 | `TASK_027A_OUTLOOK_MSG_SOURCE_IMPORT_AND_MINIMAL_METADATA` | done | `.msg` source copy, minimal metadata read, source preservation on metadata failure completed on 2026-04-27 |
| T6A-4 | `TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION` | done | Fixture-supported attachment extraction, metadata, sha256, and non-destructive failures completed on 2026-04-27 |
| T6A-5 | `TASK_027C_REAL_MSG_SAMPLE_COMPATIBILITY` | done | Compatibility probe added; real sample validation documented as blocked until `.msg` fixtures are provided |
| T6A-6 | `TASK_028A_INTAKE_STORAGE_BOUNDARY` | done | IntakeStorage added for safe names, package/source/attachments/snapshots paths, non-overwrite copy, and sha256 |
| T6A-7 | `TASK_028B_INTAKE_PACKAGE_ASSET_CASE_STORAGE` | done | Added IntakePackage, IntakeAsset, IntakeCase, and IntakeDraft domain/storage persistence with tests on 2026-04-27 |
| T6A-8 | `TASK_029_APPLICATION_FORM_CANDIDATE_DETECTION` | done | Added deterministic application-form candidate scoring and asset role persistence with tests on 2026-04-27 |
| T6A-9 | `TASK_030_FORM_SELECTION_AND_DRAFT_CREATION` | done | Added human form selection service with IntakeCase/IntakeDraft creation and repository coverage on 2026-04-27 |
| T6A-10 | `TASK_031A_INTAKE_INBOX_FRONTEND_UX` | done | Added Intake sidebar route, inbox entry page, import boundary note, and preview queue UI on 2026-04-27 |
| T6A-11 | `TASK_031B_INTAKE_PACKAGE_DETAIL_FRONTEND_UX` | done | Added package detail route, source metadata panel, asset list, and form selection action placement on 2026-04-27 |
| T6A-12 | `TASK_031C_INTAKE_CASE_REVIEW_FRONTEND_UX` | done | Added case review route, selected form context, draft field review rows, manual override placement, and confirmation gate on 2026-04-27 |
| T6A-13 | `TASK_032_CONFIRM_INTAKE_CASE_TO_PROJECT` | done | Added intake confirmation service that creates Project, ApplicationForm, SampleInfo, FileAsset, and confirmed case linkage on 2026-04-27 |
| T6A-14 | `TASK_033_DIRECT_WORD_APPLICATION_FORM_IMPORT` | done | Added direct Word intake service that preserves `.doc/.docx`, creates direct intake package and asset, and reuses candidate detection on 2026-04-27 |
| T6A-15 | `TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE` | done | Registered supporting project attachments are passed into deterministic precheck context on 2026-04-27 |
| T6A-16 | `TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC` | done | Phase 6A validation summary, manual smoke checklist, backend tests, and frontend build synced on 2026-04-27 |

Acceptance gate:

- `.msg` intake can form a package with source email and assets
- direct `.docx` intake uses the same draft/review/confirm path
- users choose one application form candidate before project creation
- parser output remains editable draft data until confirmation
- confirmed cases create Project, ApplicationForm, SampleInfo, and FileAsset records
- supporting attachments are connected to precheck where relevant
- backend tests pass
- frontend build passes when UI tasks are touched
- manual smoke checklist covers the Phase 6A intake flow

---

### Phase 7 - Real LTR, Folder Evidence, And Lifecycle Governance

Goal:

- prove ConnLab can handle the real laboratory intake-to-registration path using real `.msg`, `.docx`, and LTR workbook samples
- calibrate real application form parsing before downstream automation
- introduce LTR readiness, number preview, local registration, optional workbook integration, evidence placement, lifecycle guards, exception handling, and lookup surfaces in controlled steps

Mandatory Phase 7 rules:

- Start with real sample baseline and parser calibration; do not start with Excel write.
- Keep original `.msg` and `.docx` samples out of Git unless explicitly sanitized.
- Treat `D:\Source\Office Auto\TestDocument\LTR_number.xls` as a local validation backup, not a hard-coded production source.
- Do not write to the real LTR workbook unless a later active task explicitly allows workbook write and settings enable it.
- The LTR workbook password must be configurable; the expected default may be `DGLAB`, but code and tests must not hard-code that value.
- Office/Excel/Word/Outlook access must stay behind `backend/infrastructure/office/`.
- Do not replace current `ProjectStatus` broadly before lifecycle guard requirements are proven.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan in Phase 7.
- Any Phase 7 frontend UI, UX copy, layout, workflow display, disabled-state reason, lookup panel, smoke checklist UX expectation, critique, audit, or polish work must use `$impeccable` before design or edits.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T7-1 | `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` | done | Phase 7 approved, board section added, and `TASK_037` activated on 2026-04-27 |
| T7-2 | `TASK_037_REAL_SAMPLE_BASELINE` | done | Real `.msg` and `.docx` baseline documented without committing originals on 2026-04-27 |
| T7-3 | `TASK_038_REAL_DOCX_PARSER_CALIBRATION` | done | Real-style parser coverage for footer form/revision, request fields, sample rows, requested testing, and lab section completed on 2026-04-28 |
| T7-4 | `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` | done | 19-field readiness catalog, source map, severity, fallback, and placeholder policy completed on 2026-04-28 |
| T7-5 | `TASK_040_LTR_NUMBER_RULES` | done | Pure LTR parsing, validation, formatting, suffix/W-prefix support, and monthly sequence rules completed on 2026-04-28 |
| T7-6 | `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` | done | Read-only `.xlsx` workbook snapshot gateway, explicit `.xls` unsupported adapter handling, and metadata/LTR number scan completed on 2026-04-28 |
| T7-7 | `TASK_042_LTR_READINESS_SERVICE_AND_API` | done | Readiness service/API, blockers, review-required fields, placeholder policy, and thin route completed on 2026-04-28 |
| T7-8 | `TASK_043_LTR_REGISTRATION_PREVIEW` | done | No-write registration preview, deterministic proposed DL number, readiness mapping, local/workbook conflict reporting, and API smoke completed on 2026-04-28 |
| T7-9 | `TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD` | done | Approved preview local commit, duplicate-safe registration, project status update, and notes-based audit snapshot completed on 2026-04-28 |
| T7-10 | `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC` | done | Config-gated OfficeFacade + Excel COM write boundary, real `.xls` layout probe, password config policy, and fake COM gateway tests completed on 2026-04-28 |
| T7-11 | `TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN` | done | Non-destructive renumber preview, local duplicate detection, folder/file asset path impacts, and conflict reporting completed on 2026-04-28 |
| T7-12 | `TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES` | done | Evidence placement preview/execution, real folder shape rules, no-overwrite copy, and API smoke completed on 2026-04-28 |
| T7-13 | `TASK_048_PROJECT_LIFECYCLE_GATING` | done | Project lifecycle guard service, guarded LTR/folder/evidence operations, and business-readable API blocks completed on 2026-04-28 |
| T7-14 | `TASK_049_EXCEPTION_WORKFLOWS` | done | Explicit no-form and multi-form package review, per-form case/draft creation, missing-info confirmation blocks, correction evidence preservation, and renumber reason coverage completed on 2026-04-29 |
| T7-15 | `TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS` | done | Read-only project lookup, sample summary, testing summary API, and structured-record search completed on 2026-04-29 |
| T7-16 | `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` | done | Phase 7 validation summary, manual smoke checklist, board sync, workbook limitations, and next recommendation completed on 2026-04-29 |

Acceptance gate:

- all real `.msg` and `.docx` samples have documented expected behavior
- parser handles real `.docx` forms well enough to create reviewable drafts
- LTR field catalog maps all 19 readiness fields to source/fallback/severity/policy
- LTR readiness check blocks incomplete registration correctly
- LTR number rules are deterministic and tested
- workbook snapshot is available before write
- LTR registration preview is available before commit
- local commit is traceable and duplicate-safe
- external workbook write, if enabled, is behind infrastructure gateway and safely releases Excel
- project folder evidence placement preserves original email, selected application form, attachments, specifications, LTR evidence, and correction evidence
- lifecycle guards prevent invalid next actions
- sample info and testing condition/method lookup is available
- no Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or future-scope feature slipped into Phase 7

---

### Phase 8 - DL-Centric Project Identity Hardening

Goal:

- downgrade application `Project #` / `project_no` from required project identity to optional metadata
- keep pre-LTR continuity on internal `project_id`, `intake_package_id`, and `intake_case_id`
- make post-registration operations and folder naming DL/LTR-centric

Mandatory Phase 8 rules:

- Do not use application `Project #` as a required business key.
- Do not remove compatibility response fields or folder placeholders in a breaking cleanup.
- Keep `{PROJECT_NO}` as an optional legacy placeholder only.
- Do not change LTR number allocation rules or write to the external LTR workbook.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T8-1 | `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY` | done | `project_no` is optional metadata across backend/API/frontend, intake confirmation no longer requires it, legacy SQLite constraint is relaxed, folder docs recommend DL-centric names, and tests/build passed on 2026-04-29 |

Acceptance gate:

- projects can be created without application `Project #`
- intake confirmation works without application `Project #`
- multiple projects with missing `project_no` are allowed
- lookup, summaries, and folder preview tolerate missing `project_no`
- frontend no longer presents Project No. as required identity
- no future-scope feature slipped into Phase 8

---

### Phase 9 - Operator Workflow UI Wiring

Goal:

- wire existing Phase 7/8 backend capabilities into the frontend operator workflow
- make readiness, preview, commit, exception, evidence, lookup, and lifecycle blocked states visible to lab operators
- preserve preview-before-write and DL-centric workflow identity in the UI

Mandatory Phase 9 rules:

- Use `$impeccable` for every frontend UI, UX copy, workflow display, disabled-state reason, lookup panel, browser smoke expectation, critique, audit, or polish task.
- Do not add new backend product behavior unless a Phase 9 task explicitly requires a thin API/client adjustment for existing backend behavior.
- UI must call backend APIs through `frontend/src/api/client.ts`.
- UI must not directly manipulate Office files, project folders, or external LTR workbooks.
- Do not write to the external LTR workbook in Phase 9.
- Do not implement Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or email sending in Phase 9.

Status table:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T9-1 | `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` | done | Phase 9 scope opened, task sequence added, and `TASK_054` activated on 2026-04-29 |
| T9-2 | `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING` | active | Wire LTR readiness, no-write preview, and local commit into the frontend workflow |
| T9-3 | `TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING` | pending | Wire no-form, multi-form, and missing-info exception workflows |
| T9-4 | `TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING` | pending | Wire evidence placement preview/execution and conflicts |
| T9-5 | `TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL` | pending | Add read-only lookup, sample summary, and testing condition/method panels |
| T9-6 | `TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI` | pending | Show backend lifecycle guard blocks as clear disabled-state reasons |
| T9-7 | `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC` | pending | Close Phase 9 with build, browser smoke checklist, docs sync, and next recommendation |

Acceptance gate:

- LTR readiness, preview, and local commit are usable from frontend without external workbook write
- intake exception workflows are visible and actionable
- evidence placement is previewed before execution
- lookup and summary surfaces are read-only and business-readable
- lifecycle guard blocks are visible as actionable disabled-state reasons
- frontend build passes
- relevant backend tests pass
- no Matrix, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, or external workbook mutation slipped into Phase 9

---

## 6. Completion Update Protocol

After finishing any task, AI must update this board in the same turn.

Minimum required updates:

1. change task status
2. update `Last Updated`
3. record validation result
4. record current stop point
5. activate the next allowed task or explain why the next task is blocked

Recommended completion note format:

```text
Completed:
- TASK_XXX_NAME

Validation:
- tests run
- key result

Next:
- next active task
- prerequisites or known limits
```

---

## 7. Current Validation Snapshot

Latest completed task:

- `TASK_052_PROJECT_NO_OPTIONAL_DL_CENTRIC_IDENTITY`

Validation result:

- `py -m pytest tests\unit\test_project_service.py tests\integration\test_project_api.py tests\integration\test_repositories.py tests\unit\test_intake_confirmation_service.py tests\unit\test_folder_template_service.py tests\unit\test_precheck_engine.py -q`
- result: `26 passed`
- `npm run build` from `frontend/`
- result: passed
- `py -m pytest -q`
- result: `210 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest -q`
- result: `203 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- Phase 7 validation summary:
- result: `docs/phase7_validation_summary.md` added with manual smoke checklist, known limitations, workbook write policy, and next recommendation
- Frontend build:
- result: not rerun for `TASK_051`; no frontend or UX-copy files changed
- `py -m pytest tests\unit\test_lookup_service.py tests\integration\test_lookup_api.py -q`
- result: `6 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\integration\test_intake_precheck_api.py tests\integration\test_project_lifecycle_gating_api.py tests\unit\test_ltr_readiness_service.py -q`
- result: `12 passed`
- `py -m pytest -q`
- result: `201 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_exception_workflow_service.py tests\integration\test_exception_workflow_api.py -q`
- result: `5 passed`
- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_intake_confirmation_service.py tests\unit\test_evidence_placement_service.py tests\unit\test_ltr_renumber_preview_service.py -q`
- result: `21 passed`
- `py -m pytest tests\integration\test_intake_package_repositories.py tests\integration\test_exception_workflow_api.py tests\integration\test_evidence_placement_api.py tests\integration\test_ltr_renumber_preview_api.py tests\integration\test_project_lifecycle_gating_api.py -q`
- result: `14 passed`
- `py -m pytest -q`
- result: `195 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_project_lifecycle_service.py tests\integration\test_project_lifecycle_gating_api.py -q`
- result: `9 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_local_commit_api.py tests\integration\test_folder_generation_api.py tests\integration\test_evidence_placement_api.py tests\integration\test_mvp_workflow_api.py -q`
- result: `7 passed`
- `py -m pytest -q`
- result: `187 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q`
- result: `4 passed`
- `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py tests\integration\test_folder_generation_api.py tests\unit\test_ltr_renumber_preview_service.py -q`
- result: `10 passed`
- `py -m pytest -q`
- result: `178 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_intake_storage.py tests\unit\test_msg_compatibility.py tests\unit\test_outlook_msg_attachment_extraction.py -p no:cacheprovider`
- result: `15 passed`
- `py -m pytest tests\unit\test_intake_storage.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `14 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_phase6_scope_activation.py -p no:cacheprovider`
- result: `11 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `10 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_phase6_scope_activation.py -p no:cacheprovider`
- result: `8 passed`
- `py -m pytest tests\unit\test_msg_compatibility.py tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_outlook_msg_source_import.py tests\unit\test_office_integration_boundary.py -p no:cacheprovider`
- result: `17 passed`
- `py -m pytest tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_outlook_msg_source_import.py tests\unit\test_office_integration_boundary.py -p no:cacheprovider`
- result: `14 passed`
- `py -m pytest tests\unit\test_outlook_msg_attachment_extraction.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `11 passed`
- `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_office_integration_boundary.py -p no:cacheprovider`
- result: `10 passed`
- `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `11 passed`
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_phase6_scope_activation.py -p no:cacheprovider`
- result: `10 passed`
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `13 passed`
- `py -m pytest tests\unit\test_phase6_scope_activation.py tests\unit\test_phase5_ux_decision.py -p no:cacheprovider`
- result: `7 passed`
- `py -m pytest tests\unit\test_intake_package_domain_models.py tests\integration\test_intake_package_repositories.py -q`
- result: `4 passed`
- `py -m pytest tests\unit\test_application_form_candidate_detector.py tests\integration\test_intake_package_repositories.py -q`
- result: `7 passed`
- `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_intake_package_repositories.py -q`
- result: `11 passed`
- `npm run build`
- result: `passed`
- `py -m pytest tests\unit\test_intake_confirmation_service.py tests\integration\test_intake_package_repositories.py -q`
- result: `10 passed`
- `py -m pytest tests\unit\test_direct_word_intake_service.py tests\integration\test_intake_package_repositories.py -q`
- result: `10 passed`
- `py -m pytest tests\unit\test_precheck_engine.py tests\integration\test_intake_precheck_api.py -q`
- result: `7 passed`
- safe real `.docx` parser coverage probe for `TASK_038_REAL_DOCX_PARSER_CALIBRATION`
- result: 2 real `.docx` files readable; parser now extracts footer form/revision, requested testing, and 3-4 sample rows without committing originals
- `py -m pytest -q`
- result: `114 passed`
- `py -m pytest tests\unit\test_ltr_field_catalog.py -q`
- result: `6 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\unit\test_ltr_field_catalog.py -q`
- result: `7 passed`
- `py -m pytest -q`
- result: `120 passed`
- `py -m pytest tests\unit\test_ltr_number_rules.py -q`
- result: `12 passed`
- `py -m pytest tests\integration\test_ltr_api.py tests\unit\test_ltr_field_catalog.py tests\unit\test_ltr_number_rules.py -q`
- result: `19 passed`
- `py -m pytest -q`
- result: `132 passed`
- `py -m pytest tests\unit\test_ltr_workbook_snapshot_gateway.py -q`
- result: `6 passed`
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_ltr_workbook_snapshot_gateway.py -q`
- result: `12 passed`
- safe real `.xls` workbook probe for `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY`
- result: `LTR_number.xls` detected as legacy `.xls` and rejected with explicit unsupported adapter error; no write attempted
- `py -m pytest -q`
- result: `138 passed`
- `py -m pytest tests\unit\test_ltr_readiness_service.py -q`
- result: `5 passed`
- `py -m pytest tests\integration\test_ltr_readiness_api.py -q`
- result: `1 passed`
- `py -m pytest tests\unit\test_ltr_field_catalog.py tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_snapshot_gateway.py tests\integration\test_ltr_api.py tests\integration\test_ltr_readiness_api.py -q`
- result: `26 passed`
- `py -m pytest -q`
- result: `144 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_ltr_registration_preview_service.py -q`
- result: `6 passed`
- `py -m pytest tests\integration\test_ltr_registration_preview_api.py -q`
- result: `1 passed`
- `py -m pytest tests\unit\test_ltr_registration_preview_service.py tests\unit\test_ltr_readiness_service.py tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_snapshot_gateway.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_readiness_api.py tests\integration\test_ltr_api.py -q`
- result: `32 passed`
- `py -m pytest tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py -q`
- result: `7 passed`
- `py -m pytest -q`
- result: `151 passed`
- `git diff --check`
- result: passed with line-ending warnings only
- `py -m pytest tests\unit\test_ltr_local_commit_service.py -q`
- result: `4 passed`
- `py -m pytest tests\integration\test_ltr_local_commit_api.py -q`
- result: `2 passed`
- `py -m pytest tests\unit\test_ltr_local_commit_service.py tests\unit\test_ltr_registration_preview_service.py tests\unit\test_ltr_readiness_service.py tests\unit\test_ltr_number_rules.py tests\integration\test_ltr_local_commit_api.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_readiness_api.py tests\integration\test_ltr_api.py -q`
- result: `33 passed`
- `py -m pytest -q`
- result: `158 passed`
- safe real `.xls` layout probe for `TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC`
- result: `LTR_number_解密版.xls` opened read-only through Excel COM; annual sheets `2020`-`2026` confirmed; A:Q registration columns and DL column D confirmed; no save/write attempted
- `py -m pytest tests\unit\test_config.py tests\unit\test_office_integration_boundary.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q`
- result: `15 passed`
- `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_registration_preview_service.py tests\unit\test_ltr_local_commit_service.py tests\integration\test_ltr_registration_preview_api.py tests\integration\test_ltr_local_commit_api.py -q`
- result: `28 passed`
- `py -m pytest tests\unit\test_ltr_workbook_snapshot_gateway.py tests\unit\test_ltr_number_rules.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q`
- result: `25 passed`
- `py -m pytest -q`
- result: `168 passed`
- `py -m pytest tests\unit\test_ltr_renumber_preview_service.py -q`
- result: `5 passed`
- `py -m pytest tests\integration\test_ltr_renumber_preview_api.py -q`
- result: `1 passed`
- `py -m pytest tests\unit\test_ltr_renumber_preview_service.py tests\integration\test_ltr_renumber_preview_api.py tests\integration\test_ltr_api.py tests\integration\test_folder_generation_api.py tests\unit\test_ltr_number_rules.py -q`
- result: `22 passed`
- `py -m pytest -q`
- result: `174 passed`
- `py -m pytest -q`
- result: `112 passed`
- `npm run build`
- result: `passed`
- `npm run build`
- result: `passed`
- `npm run build`
- result: `passed`
- `py -m pytest -q`
- result: `95 passed`
- manual browser smoke checklist
- result: not required for docs-only scope activation
- static documentation review for `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION`
- result: Phase 7 board section added and `TASK_037_REAL_SAMPLE_BASELINE` activated
- safe real sample probe for `TASK_037_REAL_SAMPLE_BASELINE`
- result: 4 `.msg` samples supported by current gateway; attachments extracted into temporary workspace only
- safe real `.docx` parser coverage probe for `TASK_037_REAL_SAMPLE_BASELINE`
- result: 2 real `.docx` files readable; current parser extracts 6-7 top-level fields, 0 lab fields, and 0 sample rows
- `py -m pytest tests\unit\test_application_form_parser.py -q`
- result: `4 passed`
- `py -m pytest tests\unit\test_precheck_engine.py tests\integration\test_intake_precheck_api.py -q`
- result: `7 passed`

Known limits:

- no full installer or PyInstaller bundle implemented
- PyWebView remains a future packaging placeholder
- browser-based manual frontend smoke has not been executed by Codex
- `$impeccable` context is present in `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`
- no report generation, AI review, Matrix, or future-scope features
- OfficeFacade boundary and Word snapshot gateway are implemented
- `.msg` source import and minimal metadata are implemented
- `.msg` fixture-supported attachment extraction is implemented
- real `.msg` sample compatibility baseline now covers 4 local samples; all were readable by the current gateway
- intake storage boundary is implemented
- intake persistence, candidate detection, review UI, and confirm flow are planned but not implemented
- Phase 7 is complete; no later phase is active until explicit user approval
- real `.msg` / `.docx` originals must not be committed
- external LTR workbook write remains disabled and out of scope until a later explicit task
- parser now has generated real-style regression coverage and real-sample probe coverage for footer form/revision, request fields, sample rows, requested testing, and lab section; original real `.docx` files remain local and uncommitted
- LTR readiness field catalog is defined as pure Python only; readiness evaluation, API, preview, commit, and workbook integration remain out of scope
- LTR number rules are defined as pure Python only; workbook snapshot, readiness service, preview, commit, and workbook write remain out of scope
- LTR workbook snapshot gateway is read-only; `.xlsx` package snapshots are supported, legacy `.xls` is explicitly unsupported until a later adapter task, and workbook write remains out of scope
- LTR readiness service/API is implemented; it evaluates confirmed project/form/sample/evidence data plus an optional proposed LTR number, but it does not preview, commit, or write workbook data
- LTR registration preview is implemented as no-write/no-commit; API supports `local_only` preview and service supports optional read-only workbook snapshot injection for conflict and fingerprint context
- `DL` is generated during preview and should be `pending_preview` before a candidate number exists; it is not expected to be present in the mailed application attachment
- LTR local commit is implemented; it recomputes preview-equivalent data, requires operator confirmation, stores audit JSON in `LtrRecord.notes`, updates project status through `LtrService`, and does not call workbook write
- LTR Excel COM write boundary is implemented behind `OfficeFacade`; write remains disabled by default and password/path are configuration-driven
- Normal LTR preview no longer calculates or reserves a candidate number; final normal DL allocation happens inside the Excel COM write session after reading workbook data
- LTR renumber preview is implemented as non-destructive planning only; it reports affected folder/file asset paths and blocks future execution when target paths or local LTR numbers conflict
- LTR workbook password handling is a future adapter/write requirement: default may be configured as `DGLAB`, but password must not be hard-coded and missing/invalid password must not create local registered state
- `$impeccable` is now a project-wide rule for all frontend/UI and UX-copy work, not only Phase 5 or Phase 6A
- application `Project #` / `project_no` is now optional metadata; current workflow continuity relies on internal IDs before LTR registration and DL/LTR number after registration
- existing SQLite databases with legacy `projects.project_no NOT NULL UNIQUE` are relaxed by a narrow `init_db()` migration; no general migration framework has been added

---

## 8. Next Recommended Action

Current recommendation:

- stop after Phase 8 identity hardening and wait for explicit user approval before activating another task

Why this is next:

- `TASK_003` established the SQLite engine, session factory, Base, and `init_db()`
- `TASK_004` established pure MVP domain models and enums
- `TASK_005` established SQLAlchemy models and repositories
- `TASK_006` established project service and thin project API
- `TASK_007` established structured DOCX parser output
- `TASK_008` established deterministic precheck rules
- `TASK_009` exposed parser + precheck flow through API
- `TASK_010` established LTR registration/tracking
- `TASK_011` established safe folder preview
- `TASK_012` established safe folder generation with persistence and overwrite protection
- `TASK_013` established the minimal React + TypeScript shell
- `TASK_014` connected the MVP workflow through backend and frontend
- `TASK_015` documented local Windows run scripts and packaging status
- the defined MVP task sequence is complete
- `docs/ConnLab_Phase5_Workbench_UX_Plan.md` defines the approved UX modernization direction
- `TASK_016` established the approved UX decision record
- `TASK_017` established the product app shell and left navigation
- `TASK_018` established the searchable project registry/dashboard
- `TASK_019` established the sequential project workbench stepper
- `TASK_020` established business-readable precheck issue review
- `TASK_021` established clearer intake, LTR, and folder operation panels
- `TASK_022` cleaned up frontend workflow state derivation and centralized API usage checks
- `TASK_023` established frontend build and manual smoke validation guards
- `TASK_024` completed Phase 5 documentation and board sync
- Phase 5 implementation is complete
- the user explicitly approved executing the Phase 6 implementation plan
- `TASK_025` opened Phase 6A and activated the Office integration boundary task
- `TASK_026` established OfficeFacade, Word document snapshots, and gateway boundaries
- `TASK_027A` established controlled `.msg` source preservation and minimal metadata parsing
- `TASK_027B` established fixture-supported attachment extraction and metadata
- `TASK_027C` documented real `.msg` compatibility status and missing fixture blocker
- `TASK_028A` established controlled intake file storage
- `TASK_036` activated Phase 7 without implementing product behavior
- `TASK_037` documented real `.msg` and `.docx` baseline behavior without committing original samples
- `TASK_038` improved deterministic parser coverage for generated real-style `.docx` layouts
- `TASK_039` defined the authoritative 19-field LTR readiness catalog and placeholder policy
- `TASK_040` defined pure deterministic LTR number parsing, validation, formatting, suffix/W-prefix handling, and monthly sequence rules
- `TASK_041` added the read-only workbook snapshot gateway and explicit legacy `.xls` unsupported handling
- `TASK_042` added the readiness service/API so incomplete LTR registration data blocks preview or registration
- `TASK_043` added no-write registration preview with deterministic proposed number, readiness field mapping, conflict reporting, and snapshot context
- `TASK_044` added local-only commit with operator confirmation and traceable audit notes
- `TASK_045` added the config-gated OfficeFacade + Excel COM workbook write boundary and patched normal preview so final normal numbering is allocated only inside write access
- `TASK_046` added non-destructive renumber/folder rename impact preview and conflict reporting
- `TASK_047` added deterministic evidence placement preview/execution for email, forms, specs, LTR evidence, corrections, and no-overwrite copy behavior
- `TASK_048` added lifecycle operation guards around existing project statuses for LTR, folder, and evidence operations
- `TASK_049` added explicit no-form, multi-form, missing-info, correction evidence, and renumber reason workflow behavior
- `TASK_050` added read-only project lookup, sample summary, and testing condition/method summary from structured records
- `TASK_051` closed Phase 7 with validation summary, manual smoke checklist, known limitations, workbook write policy, and next recommendation
- `TASK_052` downgraded application Project # to optional metadata and preserved DL-centric project identity

Active Phase 8 task:

- `NONE_PENDING_USER_APPROVAL`

Reason:

- Phase 8 identity hardening is complete and the board must not silently activate any later scope.

Do not start yet:

- any later phase task before explicit user approval and a new task board activation
- Outlook inbox auto-scan
- email sending
- any Matrix, Report, AI review, LAN deployment, permissions, or future-scope feature
