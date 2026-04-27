# ConnLab Task Board

> Status: Phase 6A validated
> Last Updated: 2026-04-27
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: `NONE_PHASE6A_VALIDATED`
> Current Phase: `Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`

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
- No Matrix, Report, AI review, or future-lifecycle work is allowed.

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
- Current active implementation task: none. Phase 6A is validated and stopped.

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

Mandatory Phase 5 UX rule:

- Use `$impeccable` for every Phase 5 UX/UI design, frontend interface change, visual polish, layout change, UX copy change, component extraction, audit, or critique.
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
- UI changes in Phase 6A still use `$impeccable` and the `PRODUCT.md` / `DESIGN.md` / `DESIGN.json` context.

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

- `TASK_035_PHASE6_VALIDATION_AND_DOCS_SYNC`

Validation result:

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

Known limits:

- no full installer or PyInstaller bundle implemented
- PyWebView remains a future packaging placeholder
- browser-based manual frontend smoke has not been executed by Codex
- `$impeccable` context is present in `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`
- no report generation, AI review, Matrix, or future-scope features
- OfficeFacade boundary and Word snapshot gateway are implemented
- `.msg` source import and minimal metadata are implemented
- `.msg` fixture-supported attachment extraction is implemented
- real `.msg` sample compatibility was validated against 3 local samples; all were classified as supported
- intake storage boundary is implemented
- intake persistence, candidate detection, review UI, and confirm flow are planned but not implemented

---

## 8. Next Recommended Action

Current recommendation:

- stop after Phase 6A validation

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
- intake database persistence is the next smallest step before candidate scoring or UI work

Active Phase 6A task:

- none

Reason:

- Intake package, asset, case, and draft metadata must persist before candidate scoring or UI work.

Do not start yet:

- any next phase or new feature before a new task plan is approved
- Outlook inbox auto-scan
- email sending
- any Matrix, Report, AI, or future-scope feature
