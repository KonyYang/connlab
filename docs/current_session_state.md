# Current Session State

Last updated: 2026-05-04

## Read First In A New Conversation

Read these files in order:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/current_session_state.md`
4. The active or recommended task file under `tasks/`

Follow the Anti-Skip Protocol in `AGENTS.md`: state current phase, active task id, and why the task is allowed before implementing.

## Current Execution State

- Current phase: `Phase 10A - Intake Entry Completion`.
- Active implementation task: none.
- Latest completed controlled task: `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION`.
- Latest hotfixes/polish:
  - real Outlook `.msg` attachment extraction filters inline body images, preserves embedded Outlook items as `.msg`, hides source email from the Intake Attachments list, and labels `.msg` rows as `MSG`.
  - Intake form selection preserves `manual_overrides_json` only when the existing case already belongs to the same selected application form asset; reusable cases rebound to a different asset clear overrides.
  - Attachment details `Test Sample Information` now matches the application-form / Precheck sample columns, including combined `Part Number / Revision`, combined traceability/lot label, contact base material, contact plating, contact lubricant, housing material, and quantity.
  - Intake attachment list hides role subtitles and displays long filenames as up to two medium-weight lines.
  - New Project workflow stepper no longer shows the redundant `New Project Step ...` title row; the shared stepper keeps step labels on one line in narrow windows and prevents connector lines from crossing label text.
  - App shell UI was simplified: TopBar title only, Sidebar brand simplified, disabled placeholder nav items retained by user decision.
- Recommended next controlled task: `TASK_091_INTAKE_PRECHECK_MANUAL_SMOKE_AND_UI_POLISH_BACKLOG`.
- Do not start the next task unless the user explicitly approves it in the new conversation.

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

## Current Validation Baseline

Recent validations recorded in `docs/task_board.md`:

- `py -m pytest -q`: `292 passed` after the manual-overrides hotfix.
- `py -m pytest tests\unit\test_intake_asset_preview_service.py tests\unit\test_application_form_parser.py tests\unit\test_intake_form_selection_service.py -q`: `22 passed` after the Attachment details sample-column correction.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`: `35 passed` after the latest New Project stepper polish.
- `npm run build` from `frontend/`: passed after the latest New Project stepper polish.
- `git diff --check`: passed with CRLF working-copy warnings only after backend hotfixes.

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
- `docs/Other_AI_Modified/2026-05-03_ConnLab_UI_修改记录.md`

There is also `docs/Other_AI_Modified/AI prompt.md`; it is a user/other-AI note, not a required architecture document.
