# Current Session State

Last updated: 2026-05-04 (TASK_092)

## Read First In A New Conversation

Read these files in order:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/archive/historical_plans/current_session_state.md`
4. The active or recommended task file under `tasks/`

Follow the Anti-Skip Protocol in `AGENTS.md`: state current phase, active task id, and why the task is allowed before implementing.

## Current Execution State

- Current phase: `Phase 10A - Intake Entry Completion`.
- Active implementation task: none.
- Latest completed controlled task: `TASK_092_INTAKE_ATTACHMENT_DOWNLOAD_ACTION`.
- Latest hotfixes/polish:
  - TASK_092: Intake attachment details now shows a working Download `<a>` link instead of disabled placeholder buttons. Download is available through `GET /api/intake-assets/{asset_id}/download`; stored_path is never exposed to the frontend.
  - DOCX parser now preserves the application-form two-column requested-testing table (`Tests to be Performed` + `Applicable Specifications`) and extracts `Additional Information` from the real heading-plus-following-block structure after skipping Confidential/Subcontracted controls. Attachment details preview renders requested testing in the same table style as `Test Sample Information`, followed by a separate Additional Information block using the same compact preview typography.
  - Intake Attachment details requested-testing preview now mirrors the Precheck information structure: it shows `Description of Requested Testing` and `Additional Information`, and no longer displays report-copy recipients in the attachment preview surface.
  - Intake left column now keeps `Import source` and `Email information` at natural height while allowing the `Attachments` panel to consume remaining vertical space and scroll when needed.
  - Attachment details previews now use one unified header for DOCX, PDF, MSG, image, Excel, metadata-only, and unsupported attachments; operator-facing preview pages no longer show duplicated outer `Attachment details`, `File size`, or raw `Role` rows.
  - real Outlook `.msg` attachment extraction filters inline body images, preserves embedded Outlook items as `.msg`, hides source email from the Intake Attachments list, and labels `.msg` rows as `MSG`.
  - Intake form selection preserves `manual_overrides_json` only when the existing case already belongs to the same selected application form asset; reusable cases rebound to a different asset clear overrides.
  - Attachment details `Test Sample Information` now matches the application-form / Precheck sample columns, including combined `Part Number / Revision`, combined traceability/lot label, contact base material, contact plating, contact lubricant, housing material, and quantity.
  - Intake attachment list hides role subtitles and displays long filenames as up to two medium-weight lines.
  - New Project workflow stepper no longer shows the redundant `New Project Step ...` title row; the shared stepper keeps step labels on one line in narrow windows and prevents connector lines from crossing label text.
  - Intake and Precheck now share UI typography/action tokens and semantic classes for panel titles, preview titles, section titles, primary actions, secondary actions, and compact actions.
  - App shell UI was simplified: TopBar title only, Sidebar brand simplified, disabled placeholder nav items retained by user decision.
- Recommended next controlled task: pending user decision.
- Do not start a new task unless the user explicitly approves it in the new conversation.

## Important Frontend Architecture State

- Intake route page is now a coordinator. Business display pieces live under `frontend/src/features/intake/`:
  - `IntakeSourcePanel.tsx`
  - `AttachmentList.tsx`
  - `AttachmentPreviewPanel.tsx`
  - `intakeSelectors.ts`
  - `intakeSession.ts`
- New Project workflow shell is shared through `frontend/src/components/workflow/NewProjectWorkflow.tsx` and `new-project-workflow.css`.
- Precheck feature components/config/selectors live under `frontend/src/features/precheck/`.
- Keep future field/table changes out of route pages where possible. Use feature components, configs, selectors, or hooks.
- `$impeccable` is project-wide for frontend/UI changes. Read `PRODUCT.md`, `DESIGN.md`, `DESIGN.json`, `docs/02_ARCHITECTURE_RULES.md`, and `docs/frontend_architecture_rules.md` before UI work.

## Deferred Cleanup Backlog

- Intake CSS dead-style cleanup should be done in a later focused UI cleanup pass after the current Intake preview/layout polish is stable. Candidate unused or legacy selectors in `frontend/src/intake-inbox.css` include `.attachment-details-heading`, `.attachment-meta-grid`, `.detail-file-icon`, and `.metadata-preview-grid`. Before deleting, verify no loading, empty, error, metadata-only, image, or responsive branch still renders them; then run `py -m pytest tests\unit\test_frontend_shell_files.py -q` and `npm run build`.

## Current Validation Baseline

Recent validations recorded in `docs/task_board.md`:

- `py -m pytest tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`: `45 passed` after TASK_092 attachment download.
- `npm run build` from `frontend/`: passed after TASK_092 attachment download.
- `py -m pytest -q`: `302 passed` after TASK_092 attachment download.
- `py -m pytest tests\unit\test_application_form_parser.py tests\unit\test_intake_asset_preview_service.py tests\unit\test_frontend_shell_files.py -q`: `48 passed` after the parser structural alignment.
- `py -m pytest tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py -q`: `8 passed` after the parser structural alignment.
- `npm run build` from `frontend/`: passed after the parser structural alignment.
- `git diff --check`: currently blocked by pre-existing trailing whitespace in `docs/archive/external_ai/2026-05-03_ConnLab_UI_淇敼璁板綍.md`; TASK_091 files were not reported with whitespace errors.

If the new conversation continues implementation, rerun relevant targeted tests first and update this file only when another task finishes or a new important constraint appears.

## User Decisions And Rejected Paths

- Do not add a confirmation dialog or extra API for preserving/discarding manual overrides. The accepted behavior is backend-only:
  - same selected form asset keeps manual overrides.
  - different/rebound selected form asset clears manual overrides.
- Disabled Sidebar placeholder entries `Reports`, `Templates`, and `Reference Library` are currently accepted by the user as placeholders, despite future-scope caution.
- Do not show disabled `Precheck` or `LTR Number` stage items in the global Sidebar; they are part of the New Project workflow, not global navigation.
- Keep copied-workbook LTR write hardening blocked until explicit approval for a new phase.

## Strictly Do Not Start Yet

- copied-workbook LTR write hardening
- Outlook inbox auto-scan
- email sending
- Matrix
- Report generation
- AI review
- LAN deployment
- permissions

## Current Working Tree Notes

At the time this state file was written, the working tree includes uncommitted changes from recently completed/reviewed tasks. Treat them as intentional unless the user says otherwise.

Known changed areas include:

- `backend/application/intake_asset_preview_service.py`
- `backend/application/intake_form_selection_service.py`
- `backend/modules/intake/application_form_parser.py`
- `backend/modules/intake/application_form_parser_patterns.py`
- `docs/task_board.md`
- `tasks/TASK_088_ATTACHMENT_DETAILS_PREVIEW_COMPLETION.md`
- `tasks/TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION.md`
- `tests/unit/test_intake_asset_preview_service.py`
- `tests/unit/test_frontend_shell_files.py`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/TopBar.tsx`
- `frontend/src/components/workflow/NewProjectWorkflow.tsx`
- `frontend/src/components/workflow/new-project-workflow.css`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/styles.css`
- `docs/archive/external_ai/2026-05-03_ConnLab_UI_淇敼璁板綍.md`

There is also `docs/archive/external_ai/AI prompt.md`; it is a user/other-AI note, not a required architecture document.
