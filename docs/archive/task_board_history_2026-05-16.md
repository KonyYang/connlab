# Task Board History Archive (2026-05-16)

Source: docs/task_board.md
Archived from marker: Prior completed note:

---

Prior completed note:

- `TASK_146_NEW_PROJECT_APPLY_LTR_ONLY_AND_COMPLETION_HANDOFF` is complete. New Project now applies/registers the LTR number and hands off to the Project workspace without previewing or generating the project folder. The completion API no longer returns folder fields, repeat completion for the same intake case returns the existing confirmed Project/LTR instead of creating a duplicate Project, and the frontend action now reads `Apply LTR Number`.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed, 4 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q` passed, 2 passed; `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task146_new_project_applies_ltr_before_project_handoff -q` passed, 8 passed; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

- `TASK_145_PHASE10C_VALIDATION_AND_BOARD_SYNC` is complete. The user-completed manual smoke test is recorded as Phase 10C manual validation evidence, targeted intake/New Project automated checks passed, frontend build passed, and the board is synced back to no active task pending the next explicit approval.
- Validation: broad selector `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py tests\unit\test_frontend_shell_files.py -q -k "msg or intake or task102 or task103 or task142 or task143 or task144 or project_setup"` returned 68 passed, 34 deselected, and 3 historical frontend shell expectation failures from older TASK_069/TASK_087/TASK_091 checks pulled in by the broad selector. Narrowed validation passed: `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q` passed, 50 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q` passed, 4 passed; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

- `TASK_144_PROJECT_SETUP_DRAFT_SCOPED_AUTOSAVE` is complete. New Project setup confirmation values are now persisted per intake case draft under `project_setup`, returned by case review APIs, included in review-field autosave, restored when switching/loading application drafts, and used by completion from the currently loaded draft-scoped state.
- Follow-up email source provenance display: the Email source panel now shows only the original source filename returned by the intake package response; the ConnLab storage path is no longer exposed in the UI.
- Follow-up email source filename wrapping: long filenames now wrap in the Email source panel, so suffixes such as `副本` stay visible instead of being clipped.
- Follow-up email source Unicode preservation: uploaded `.msg` display names now keep the original Unicode filename rather than the sanitized storage filename.
- Validation: `py -m pytest tests\unit\test_intake_case_review_service.py::test_review_service_persists_project_setup_per_draft tests\integration\test_manual_intake_api.py::test_review_fields_persists_requested_testing_rows tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q` passed, 3 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_143_EMAIL_PACKAGE_SELECTION_TIME_DRAFT_LOADING_HOTFIX` is complete. `.msg` import now preserves source and attachments without immediately selecting the first attachment or preparing a draft when selectable Word forms are present; duplicate handling runs after explicit application-form selection; new, opened, and replaced drafts all load into right-side `Application information`; the duplicate card now lives in the Attachments selection context and shows only the application-form filename plus `Load existing` and `Reinitialize`. Follow-up manual-smoke fix: duplicate resolution now reloads an existing selected review directly instead of calling blank draft preparation again, preventing the right-side editor from flashing and then clearing.
- Follow-up completion friction cleanup: removed the extra controlled-workbook acknowledgement checkbox from New Project setup; the workflow now treats this risk as accepted and sends the existing backend preview acknowledgement automatically.
- Follow-up completion dock cleanup: replaced the sticky autosave guidance with the final completion dock, moved LTR mode and specified-number input beside `Apply LTR Number and Create Folder`, and kept the left setup panel focused on workbook row metadata.
- Follow-up specified LTR input clarity: specified-number mode now keeps the input highlighted and completion blocked until the value matches `DL-YYYY-MM-NNN`, `DL-YYYY-MM-NNN` plus letter-led suffix, or a letter-led alphanumeric suffix token; a `?` help control explains accepted examples.
- Follow-up sample-table blocker clarity: required empty sample cells now highlight the whole cell with a non-obstructive tint instead of adding capsule borders or placeholder text that would obscure table content; each non-empty sample row independently checks Product Name and Quantity.
- Follow-up default application-form loading: `.msg` import now preselects the first `.docx` application form and immediately runs the selected-form import/duplicate path; emails with no application form still prepare the no-form draft path. Duplicate buttons now place `Load existing` on the right as the primary/recommended action.
- Follow-up import logic review: selected-form and no-form duplicate enforcement were rechecked against the backend services. A stale duplicate-card state was fixed so any successful prepared or selected draft load clears previous duplicate state before showing right-side `Application information`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"` passed, 3 passed and 52 deselected; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q` passed, 1 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q` passed, 2 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_new_project_page_chrome_is_minimal tests\unit\test_frontend_shell_files.py::test_task134_new_project_uses_ltr_workbook_commit_before_folder -q` passed, 3 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q` passed, 1 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable -q` passed, 2 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed -q` passed, 2 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed -q` passed, 3 passed; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

Prior completed note:

- `TASK_142_EMAIL_PACKAGE_DRAFT_IDENTITY_AND_DUPLICATE_RESOLUTION` is complete. `.msg` import no longer blocks on package-level duplicate identity before a draft exists; selected-form draft identity is checked by selected application form filename + email source filename + email source size; no-form email drafts are checked only against other no-form drafts; duplicate conflicts return structured business-safe details and the New Project UI renders inline actions to open, replace, or create a separate draft only when allowed.
- Validation: `py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q` passed, 36 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"` passed, 3 passed and 51 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only. Full `py -m pytest tests\unit tests\integration -q` currently reports 415 passed and 9 existing unrelated baseline failures in historical frontend shell checks, board phase checks, and the legacy LTR workbook snapshot expectation.

Prior completed note:

- `TASK_141_EMAIL_PACKAGE_DUPLICATE_DETECTION_BACKEND` is complete. Manual `.msg` import now supports backend duplicate classification and explicit resolution actions (`open_existing`, `replace_existing`, `create_separate`). Duplicate imports without explicit resolution return structured `409` conflict detail. Replacement stages the new package before removing old unconfirmed package records and does not delete old stored files inside the uncommitted request; confirmed/project-linked packages remain protected.
- Validation: `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q` passed, 21 passed; `py -m pytest tests\unit tests\integration -q` currently has existing unrelated baseline failures in frontend shell historical checks, board-phase historical checks, and legacy LTR workbook snapshot expectation; `git diff --check` passed with LF/CRLF working-copy warnings only.

Prior completed note:

- `TASK_140_NEW_PROJECT_DRAFT_FRICTION_CLEANUP` is complete. New Project no longer shows `Cancel and remove draft`, form switching now directly replaces/rebinds the active unconfirmed creation draft, and the inline replacement confirmation panel is removed. Draft discard remains available in `Drafts / In Progress`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task096 or task102 or task103_application_form_import_is_explicit_and_confirmed or task103_new_project_page_chrome_is_minimal"` passed, 4 passed; `npm run build` passed from `frontend`; `py -m pytest tests\unit\test_frontend_shell_files.py -q` has existing unrelated baseline failures in `test_task087_intake_information_density_cleanup`, `test_task082_precheck_sample_rows_are_editable_with_icon_actions`, and `test_task091_intake_precheck_typography_uses_shared_ui_vocabulary`; `git diff --check` passed.

Prior completed note:

- `TASK_100_PROJECT_WORKBENCH_BOUNDARY_AFTER_FOLDER_CREATION` is complete. Project Workbench is now bounded to post-creation project status and source material management: creation-stage controls (application form upload, precheck run, local LTR commit, initial folder generation) are removed from Workbench, while evidence placement preview/place remains. Projects continue to use `Open`; Drafts / In Progress continue to use `Continue`.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q` passed, 53 passed; `npm run build` passed from `frontend`; `py -m pytest tests\unit tests\integration -q` passed, 409 passed.

Prior completed note:

- `TASK_099_LTR_REGISTERED_FREEZE_AND_EXCEPTION_PATH` is complete. Normal New Project/Precheck base-field editing is now frozen after the intake case is tied to a project with a registered LTR. The API exposes frozen state and returns a 409 revise/exception message when stale clients attempt to change frozen base fields; the New Project editor shows the same message, disables normal editing, and stops autosave in frozen state.
- Validation: `py -m pytest tests\unit\test_intake_case_review_service.py -q` passed, 14 passed; `py -m pytest tests\integration\test_manual_intake_api.py::test_review_fields_returns_conflict_after_registered_ltr -q` passed, 1 passed; `py -m pytest tests\unit\test_frontend_shell_files.py::test_task099_new_project_editor_exposes_ltr_registered_freeze_state -q` passed, 1 passed; `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q` passed, 66 passed; `py -m pytest tests\unit tests\integration -q` passed, 408 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_138_LTR_SUFFIX_TOKEN_STRICT_INPUT_AND_BOARD_CLEANUP` is complete. Suffix-token-only specified LTR input now validates the raw trimmed token, so internal spaces and other non-alphanumeric characters are rejected instead of normalized away. The stale pending TASK_133 rule-clarification block was replaced with implemented-rule notes for TASK_137/TASK_138.
- Validation: `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed, 35 passed; `py -m pytest tests\unit tests\integration -q` passed, 403 passed; `git diff --check` passed with LF/CRLF working-copy warnings only.

Prior completed note:

- `TASK_137_LTR_SPECIFIED_NUMBER_RULES_AND_YEAR_MONTH_GUARDS` is complete. `Use specified LTR number` now uses explicit category handling (base/full/suffix token), rejects invalid specified inputs with actionable errors, enforces base existence requirements for associated input, preserves replacement behavior for existing full numbers, and keeps year-sheet bootstrap plus duplicate guards on commit paths.
- Validation: `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed, 33 passed; `py -m pytest tests\unit tests\integration -q` passed, 401 passed.

Prior completed note:

- `TASK_136_REVISION_H_NON_BLOCKING_IN_NEW_PROJECT_PRECHECK` is complete. SECTION 1 `Revision must be H` is now warning-only during New Project creation precheck and no longer blocks completion, while `Form No. must be E-3718` remains an error-level blocker.
- Validation: `py -m pytest tests\unit\test_intake_section1_precheck.py tests\integration\test_manual_intake_api.py -q` passed, 12 passed; `py -m pytest tests\unit tests\integration -q` passed, 394 passed.

Prior completed note:

- `TASK_135_LTR_WORKBOOK_YEAR_SHEET_BOOTSTRAP` is complete. External LTR workbook commit now supports a controlled bootstrap path for missing annual sheets: when enabled by settings and explicitly acknowledged by the operator, the commit flow copies a configured template sheet, clears configured data rows, verifies the target year sheet exists, and then continues the same locked backup + short transaction write path.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed, 23 passed; `py -m pytest tests\unit tests\integration -q` passed, 392 passed.

Prior completed note:

- `TASK_134_NEW_PROJECT_LTR_WORKBOOK_COMMIT_UI_INTEGRATION` is complete. New Project now requires an explicit controlled-workbook acknowledgement, confirms the intake case, commits the LTR workbook write through the TASK_133 API, records the workbook action/sheet/row/backup message, and then reuses New Project completion to generate the project folder with the committed LTR number. If folder generation fails after a workbook commit, retry skips duplicate case confirmation and duplicate workbook write.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py -q` passed, 56 passed; `npm run build` passed; `py -m pytest tests\unit tests\integration -q` passed, 389 passed.

Prior completed note:

- `TASK_133_LTR_WORKBOOK_WRITE_COMMIT` is complete. The backend now has an operator-confirmed LTR workbook write commit service and API that require preview acknowledgement, use the lock/backup/short transaction gateway, re-scan workbook-visible numbers inside the write transaction, support the approved specified-number classifications, replace existing workbook rows or append new rows, and register local LTR records only after a successful workbook save.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_excel_com_ltr_workbook_gateway.py tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_preview_service.py -q` passed, 34 passed; `py -m pytest tests\unit tests\integration -q` passed, 387 passed.

Prior completed note:

- `TASK_132_LTR_WORKBOOK_WRITE_PREVIEW` is complete. Confirmed project data and New Project setup confirmation values now map into a no-write LTR workbook A:Q row preview with workbook path, target sheet, target row when known, column values, and warnings.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_write_preview_service.py tests\integration\test_ltr_workbook_write_preview_api.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed, 14 passed; `py -m pytest tests\unit tests\integration -q` passed, 376 passed; `git diff --check` passed with CRLF working-copy warnings only.

Prior completed note:

- `TASK_131_LTR_WORKBOOK_LOCK_BACKUP_AND_SHORT_TRANSACTION_GATEWAY` is complete. LTR workbook write transactions now have an infrastructure-only gateway for exclusive lock acquisition, bounded wait/timeout, write-before backup, short COM write session execution, workbook close, and lock release.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q` passed, 9 passed; `py -m pytest tests\unit tests\integration -q` passed, 371 passed; `git diff --check` passed with CRLF working-copy warnings only.

Prior completed note:

- `TASK_130_EXTERNAL_EXCEL_STRUCTURE_PROBES` is complete. External Excel resources now have read-only `.xlsx` structure probes for expected sheets, headers, and date-like headers. The probes are connected to external resource validation for standard record and equipment calibration Excel files, while LTR workbook validation remains read-only through the existing snapshot gateway.
- Validation: `py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py tests\unit\test_ltr_workbook_snapshot_gateway.py -q` passed, 17 passed; `py -m pytest tests\unit tests\integration -q` passed, 367 passed.

Prior completed note:

- `TASK_129_SECRET_AND_LOCAL_SETTINGS_POLICY` is complete. LTR workbook local settings now expose a redacted safe summary, reject invalid positive-integer policy values, preserve local/env password loading without hard-coding secrets, and document the local secret policy plus future Windows Credential Manager direction.
- Validation: `py -m pytest tests\unit\test_config.py -q` passed, 6 passed; `py -m pytest tests\unit tests\integration -q` passed, 362 passed.

Prior completed note:

- `TASK_128_EXTERNAL_RESOURCE_REGISTRY_AND_VALIDATION` is complete. External resources now have SQLite-backed registration, active state, validation status, last validation time, and failure reason. Backend APIs can list, upsert, and validate `ltr_workbook`, `application_form_template`, `project_folder_template`, `standard_record_excel`, and `equipment_calibration_excel` without writing public-drive Excel files.
- Validation: `py -m pytest tests\unit\test_external_resource_service.py tests\integration\test_external_resource_api.py -q` passed, 9 passed; `py -m pytest tests\unit tests\integration -q` passed, 359 passed.

Prior completed note:

- `TASK_127_LOOKUP_OPTIONS_SAFE_UPDATE_AND_IMPORT` is complete. New Project setup confirmation `Location` and `Test Type in sheet` now use the existing database-backed lookup option service with required default backfill for new and existing databases. A local TOML import API updates/ disables lookup options without deleting old records and backs up SQLite before import.
- Validation: `py -m pytest tests\unit\test_lookup_options_service.py tests\integration\test_lookup_options_api.py tests\integration\test_new_project_completion_api.py -q` passed, 9 passed; `py -m pytest tests\unit tests\integration -q` passed, 350 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_126_NEW_PROJECT_SETUP_CONFIRMATION_REQUIRED_FIELDS_REWORK` is complete. LTR/setup confirmation controls now live in the left-side project setup card, obsolete blockers were loosened, and the main completion button remains in the Application information footer.
- Validation: `py -m pytest tests\unit tests\integration -q` passed, 347 passed; `npm run build` passed from `frontend`.

Prior completed note:

- `TASK_125_FULL_TEST_SUITE_HISTORICAL_EXPECTATION_SYNC` is complete. Historical test expectations now match current `.docx` intake, eligibility-gated form selection, candidate scoring, and task-board phase progression.
- Validation: `py -m pytest tests\unit tests\integration -q` passed, 347 passed.

Prior completed note:

- `TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION` is complete. New Project now has a one-action completion path for intake confirmation, LTR registration, folder preview, folder generation, and Workbench routing.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_local_commit_api.py -q` passed; `npm run build` passed from `frontend`. Follow-up TASK_125 full-suite stabilization is complete; `py -m pytest tests\unit tests\integration -q` now passes with 347 tests.

Prior completed note:

- `TASK_139_LTR_FROZEN_FIELD_REVISION_REQUEST_RECORD` is complete. Added a structured frozen-field revision request record path after LTR registration freeze with typed create/list/detail APIs, strict frozen-field validation against `IntakeCaseReviewService` authoritative keys, and persisted backend current-value snapshots plus operator proposed values/reason without mutating intake draft data, project identity, workbook, or folder.
- Validation: `py -m pytest tests\unit\test_frozen_field_revision_request_service.py tests\integration\test_frozen_field_revision_request_api.py tests\unit\test_intake_case_review_service.py -q` passed, 19 passed; `git diff --check` passed with LF/CRLF working-copy warnings only.

Next recommended action:

- `TASK_149_SETTINGS_EXTERNAL_RESOURCES_UI_AND_LOCAL_PATHS` is complete. Settings is now reachable from the sidebar, lists registry-backed external resources, supports manual path paste, active-state save, per-resource validation, and business-readable validation state. `project_output_root` is represented as a directory-style external resource and validates existing readable directories without requiring them to be non-empty. Local LTR workbook backup and lock directories are shown as local-machine settings still owned by TOML/environment configuration.
- Validation: `py -m pytest tests\integration\test_external_resource_api.py tests\unit\test_external_resource_service.py -q` passed, 12 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "settings or external"` passed, 1 passed and 56 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.
- TASK_149 manual usability follow-up is complete. Settings path rows now include a `...` browse entry beside the path input and show an inline desktop-shell guidance message when clicked. The current Web UI still uses manual path paste; no native file picker, upload flow, workbook write behavior, or folder generation behavior was added.
- Follow-up validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "settings or external"` passed, 1 passed and 56 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.
- `TASK_150_PROJECT_FOLDER_USES_CONFIGURED_RESOURCES` is complete. Project Workbench folder creation now resolves `project_folder_template` and `project_output_root` from Settings resources, shows configured resource state inline, blocks preview/generation when required resources are missing/inactive/invalid, and preserves existing preview-before-write plus conflict blocking behavior. Raw template/target path entry is no longer the normal business path.
- Validation: `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_external_resource_api.py -q` passed, 5 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder or settings"` passed, 6 passed and 52 deselected; `npm run build` passed from `frontend`; `git diff --check` passed with LF/CRLF working-copy warnings only.

- Phase 10E task sequence is complete.
- The next business mainline is no longer additional standard/equipment Excel expansion.
- The next business mainline is real-world LTR application against the configured public-drive workbook path.

- `TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION` is complete.

- Proposed Phase 10F task sequence:
  - `TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION`
  - `TASK_155_REAL_PUBLIC_DRIVE_LTR_WORKBOOK_COMPATIBILITY_BASELINE`
  - `TASK_156_REAL_LTR_APPLICATION_SMOKE_AND_FAILURE_HANDLING`
  - `TASK_160_NEW_PROJECT_LTR_ATOMIC_COMPLETION_GATE`
  - `TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN`
  - `TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION`
  - `TASK_157_LTR_WORKBOOK_SQLITE_RECONCILIATION_AND_AUDIT_CHECK`
- Recommended next action: use the dry-run result to select explicit no-LTR Project IDs for cleanup execution, or open the next controlled task.
- Do not implement code or any later task before the next task is explicitly approved.

- `TASK_162_NO_LTR_PROJECT_CLEANUP_EXECUTION` is complete. Added `NoLtrProjectCleanupService`, `project_cleanup_audit_records`, repository wiring, and `POST /api/cleanup/project-ltr/no-ltr-projects/execute`. The endpoint requires explicit Project IDs and a cleanup reason, re-checks that each Project has no registered LTR before mutation, marks eligible Projects as `cancelled`, and writes one audit row per changed Project. It does not physically delete rows, touch files, mutate workbook data, recycle LTR numbers, or handle invalid registered LTR records.
- Validation: `py -m pytest tests\unit\test_no_ltr_project_cleanup_service.py tests\integration\test_cleanup_api.py -q` passed (6 passed).
- Live cleanup execution after user approval: selected 25 `project_without_registered_ltr` candidates from dry-run, cancelled all 25, rejected 0, and wrote 25 cleanup audit records. Post-check status distribution in `data\connlab.sqlite3`: `cancelled=25`, `folder_created=1`, `ltr_registered=2`.

- `TASK_163_PROJECT_REGISTRY_CANCELLED_VISIBILITY_FILTER` is proposed. This task updates the Project Registry UI to hide `cancelled` Projects by default after TASK_162 cleanup, adds an explicit `Show cancelled` operator control, and keeps search, metrics, pagination, and empty states aligned with the visible registry scope. Plan: `docs/task_163_project_registry_cancelled_visibility_filter_plan.md`.
- `TASK_163_PROJECT_REGISTRY_CANCELLED_VISIBILITY_FILTER` is complete. Project Registry now hides `cancelled` Projects by default, adds a `Show cancelled` toolbar control, aligns metrics/search/pagination with visible scope, and shows dedicated scope empty-state guidance plus a hidden-cancelled count note.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard"` passed (`1 passed, 57 deselected`); `npm run build` from `frontend` passed.

- `TASK_164_NEW_PROJECT_DRAFT_SCOPE_DUPLICATE_ONLY` is complete. New Project duplicate checks are now limited to draft/package scope. Confirmed-project duplicate conflict branch (`existing_confirmed_project_ltr`) was removed from intake selected-form flow, API mapping, frontend duplicate DTO union, and attachment-panel reminder/action wiring. Draft duplicate resolution behavior remains unchanged.
- Validation: `py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py -q` passed (`36 passed`); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate_scope or task147 or duplicate"` passed (`2 passed, 56 deselected`); `npm run build` from `frontend` passed.

- `TASK_165_PROJECTS_PAGE_REMOVE_DRAFTS_SURFACE` is complete. Projects page now removes the `Drafts / In Progress` section and related continue/discard actions. Draft data and backend APIs are preserved; this task is UI-scope cleanup only.
- Validation: `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard or projects_page_removes_drafts_surface_after_task163 or task100_workbench"` passed (`3 passed, 55 deselected`); `npm run build` from `frontend` passed.

- Product decision update (2026-05-10): do not add a separate Draft list/management surface in Projects or New Project for now. Draft recovery remains selection-time/import-time only (`Load existing` / `Reinitialize`) within New Project. This is intentional scope control to keep duplicate and workflow boundaries simple.

- `TASK_161_HISTORICAL_PROJECT_LTR_CLEANUP_DRY_RUN` is complete. Added a read-only cleanup audit service and `GET /api/cleanup/project-ltr/dry-run`, classifying no-registered-LTR projects, invalid registered LTR numbers, multiple registered LTRs per project, and orphan LTR records. No database mutation or workbook operation is performed. Live local dry-run found `total_projects=28`, `total_ltr_records=5`, and `project_without_registered_ltr=25`.
- Validation: `py -m pytest tests/unit/test_project_ltr_cleanup_audit_service.py -q` passed (1 passed); `py -m pytest tests/integration/test_cleanup_api.py -q` passed (1 passed).

- `TASK_160_NEW_PROJECT_LTR_ATOMIC_COMPLETION_GATE` is complete. New Project frontend completion now calls only backend `complete-new-project`; it no longer directly confirms intake cases or directly calls workbook write commit before backend orchestration. The failure regression now asserts workbook commit failure leaves no confirmed project link and no Project record, preventing new no-LTR Project Registry entries from this path.
- Validation: `py -m pytest tests/integration/test_new_project_completion_api.py -q` passed (5 passed); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or project"` passed (10 passed, 48 deselected); `npm run build` passed from `frontend`.

- `TASK_156_REAL_LTR_APPLICATION_SMOKE_AND_FAILURE_HANDLING` is complete. LTR authority commit failures now return clearer operator guidance for lock timeout/read-only/write-disabled/backup-failure classes, and direct workbook commit API now maps lock-timeout to `409 Conflict` with existing business failures kept as `400`. Real configured workbook compatibility baseline was manually verified at `D:\LabShare\LTR\LTR.xls` (`compatible=true`, no blockers).
- Validation: `py -m pytest tests/unit/test_ltr_excel_authority_adapter.py tests/integration/test_ltr_workbook_write_commit_api.py tests/integration/test_new_project_completion_api.py -q` passed (13 passed).
- `TASK_159_NEW_PROJECT_LTR_RESULT_VISIBILITY_AND_PROJECT_REGISTRY_PAGINATION` is complete (approved hotfix). New Project completion now writes a one-time result snapshot into session storage before redirect; Project Registry displays the latest apply result (LTR number + workbook sheet/row/backup when available) and supports dismiss. Project Registry `20 / page` is now real client-side pagination with Prev/Next page controls.
- Validation: `npm run build` passed from `frontend`.
- `TASK_155_REAL_PUBLIC_DRIVE_LTR_WORKBOOK_COMPATIBILITY_BASELINE` is complete. Added a read-only compatibility baseline service and API for configured `ltr_workbook` resources (`GET /api/external-resources/ltr-workbook/compatibility-baseline`) that checks resource registration/active state, file/open-read viability through the Office boundary, year-sheet presence, and write prerequisites (write enabled, password, lock/backup dirs), and reports blockers as actionable diagnostics.
- Validation: `py -m pytest tests\unit\test_ltr_workbook_compatibility_service.py tests\integration\test_ltr_workbook_compatibility_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py tests\integration\test_new_project_completion_api.py -q` passed (19 passed).
- Operational note update (2026-05-10): real configured workbook path is now active and compatibility baseline is manually verified; operator-smoke hardening moved from deferred state to completed under `TASK_156`.

- `TASK_154_PHASE10F_SCOPE_AND_BOARD_ACTIVATION` is complete. Phase 10F is now formally activated and the business mainline is explicitly focused on real public-drive LTR workbook operations (`LTR.XLS`/configured workbook path) instead of further standard/equipment Excel expansion.
- Validation: board/document sync only (no runtime code changes and no test scope required for this activation task).

- `TASK_153_LTR_AUTHORITY_SERVER_CUTOVER_SEAM` is complete. Added explicit LTR authority seam (`LtrAuthorityPort`), Excel authority adapter wiring, New Project authority-based orchestration dependency, static boundary tests preventing route-level workbook/COM leakage, and migration note document `docs/ltr_authority_cutover_seam.md`.
- Validation: `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (14 passed); `py -m pytest tests\unit\test_ltr_authority_boundary.py tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr or authority"` passed (10 passed, 50 deselected).

- `TASK_152_STANDARD_AND_EQUIPMENT_RESOURCE_READ_MODELS` is complete. Added read-only structured models and APIs for configured `standard_record_excel` and `equipment_calibration_excel` resources, with query filtering and sheet/header-based XLSX parsing through OfficeFacade/ExcelWorkbookGateway without write behavior.
- Validation: `py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py -q` passed (12 passed); `py -m pytest tests\unit\test_external_excel_read_service.py -q` passed (3 passed); `py -m pytest tests\integration\test_external_resource_api.py tests\integration\test_external_excel_read_api.py -q` passed (6 passed).

- `TASK_151_NEW_PROJECT_LTR_WORKBOOK_AUTHORITY` is complete. New Project `complete-new-project` now commits through workbook-authority LTR write service, uses workbook-visible numbers for auto allocation, supports specified-number/suffix-token input pass-through, returns workbook write metadata (path/sheet/row/backup), and blocks local LTR registration when workbook write fails.
- Validation: `py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q` passed (39 passed); `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed (5 passed); `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr"` passed (8 passed, 50 deselected); `npm run build` passed from `frontend`.

Planning note:

- Phase 10E recognizes the current lab reality: public-drive Excel files remain authoritative for LTR numbering and other shared lab resources, while ConnLab stores structured local records and prepares for a future server/database authority.
- Development should use local simulated public-drive paths configured through Settings, not hard-coded paths and not the real public-drive workbook.
- Phase 10F shifts the mainline from architecture expansion back to operational closure on the real LTR workbook business path.
- Standard/equipment Excel read-model work is no longer the immediate priority; real LTR application behavior against the configured workbook path is.

Prior completed note:

- `TASK_148_PROJECT_WORKBENCH_FOLDER_CREATION_UX` is complete. Project Workbench now owns initial project folder creation after LTR registration: it previews folder generation, blocks conflicts, creates the folder through existing APIs, refreshes project state, shows the recorded folder path, and then enables evidence placement. A read-only `GET /api/projects/{project_id}/folder/latest` endpoint supports persisted folder-path display after reload. New Project remains LTR-only and does not create folders.
- Validation: `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q` passed, 4 passed; `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder"` passed, 4 passed and 52 deselected; `py -m pytest tests\integration\test_new_project_completion_api.py -q` passed, 4 passed; `npm run build` passed from `frontend`; `git diff --check` passed with CRLF working-copy warnings only.
- Known validation note: full `tests\unit\test_frontend_shell_files.py` still has 4 historical static assertion failures in Intake/Precheck/Draft expectations, outside TASK_148 Workbench/folder scope.

Backlog note:

- `TASK_147` implemented confirmed Project/LTR duplicate reminders for imported email/application-form identity matches. `Import as new anyway` remains deferred unless explicitly approved in a future task.

Implemented LTR number rule clarification:

- `TASK_137` implemented specified-number classification for base DL numbers, full base-plus-suffix numbers, and suffix-token-only input.
- `TASK_138` tightens suffix-token-only input so any non-alphanumeric character, including internal spaces, is rejected instead of normalized away.

Do not start yet:

- Outlook inbox auto-scan
- email sending
- any Matrix, Report, AI review, LAN deployment, permissions, or future-scope feature
