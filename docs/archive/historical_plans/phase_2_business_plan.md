# ConnLab Phase 2 Business Implementation Plan

> Status: planning draft  
> Created: 2026-04-26  
> Basis: Phase 1 MVP technical foundation completed through `TASK_015_PACKAGING_NOTES`

> Update: The active next task sequence is now tracked as `Phase 5 - Workbench UX Modernization` in `docs/task_board.md`, starting with `TASK_016_UX_BASELINE_AND_DECISION_RECORD`. This document remains useful as a later business-intake planning reference, especially for real email/Word intake and human confirmation work.

---

## 1. Phase 2 Goal

Phase 2 moves ConnLab from a runnable technical skeleton to a business-credible laboratory workbench.

Phase 1 proved that these technical paths work:

```text
Project -> Application form -> Precheck -> LTR -> Project Folder
```

But that path is not yet the real business workflow. In real use, project creation should usually start from imported request material, such as email, Word application forms, and attachments. The user should not be expected to manually create a project first and then force the rest of the flow around it.

Phase 2 target workflow:

```text
Import request material -> Extract information -> Human confirmation -> Create/Update Project -> Precheck -> LTR -> Folder
```

The core product goal:

- A lab engineer can import real request material.
- ConnLab extracts structured project/request/sample/test information.
- The user reviews and confirms extracted data before project creation.
- The system keeps original files, extracted records, warnings, and downstream workflow records traceable.
- The UI uses a durable workbench layout suitable for future report and lab operations modules.

---

## 2. Lessons From Phase 1

Phase 1 was useful, but several findings should shape Phase 2.

### 2.1 What Worked

- Backend layering is usable: API -> application services -> domain/repositories.
- SQLite persistence is functional.
- Main entity tables exist and can persist workflow records.
- API and frontend can communicate through local dev scripts.
- Tests now include a real FastAPI dependency path after fixing the session dependency issue.
- Folder generation has preview and overwrite protection.

### 2.2 What Is Not Business-Ready

- Current project creation is manual and does not match real intake.
- Current DOCX parser is only a minimal proof; real sample extraction is not reliable yet.
- Current UI is a verification shell, not a product UI.
- Current precheck rules are not complete enough for real laboratory intake.
- Current LTR and folder flows are structurally present but not aligned with real operator decisions and exception paths.
- Current workflow does not model "extracted but not confirmed" data.

### 2.3 Blocking Defects vs. Business Gaps

Blocking defects must be fixed immediately:

- API 500 errors on real runtime paths.
- Data not persisted despite successful responses.
- Unsafe file overwrite or path handling.
- Scripts that cannot start the system.
- Tests that only cover fake paths while real paths fail.

Business gaps can become Phase 2 tasks:

- Real email/Word import.
- Accurate sample extraction.
- Better UI framework.
- More complete precheck rules.
- Real LTR state handling.
- Real folder template conventions.

---

## 3. Phase 2 Scope

### 3.1 In Scope

- Real intake entry based on imported request material.
- Email and Word request material abstraction.
- Attachment registration and traceability.
- Extracted data review before project creation.
- Reliable application form and sample extraction.
- Business-oriented precheck rule expansion.
- Workbench UI baseline with left navigation and right work area.
- Project list/table with filters and status badges.
- Project detail page with workflow steps and task panels.
- LTR and folder UI integrated into the project workbench.
- Regression tests for real workflow paths.

### 3.2 Explicitly Out Of Scope

These remain blocked unless a later phase explicitly opens them:

- Matrix planning.
- Test record generation.
- Report generation.
- AI review.
- Multi-user permissions.
- LAN deployment.
- Full installer.
- PyInstaller packaging.
- PyWebView desktop shell implementation.

### 3.3 Allowed Placeholders

The UI may show disabled future navigation items only if clearly marked unavailable:

- Matrix
- Reports
- Knowledge Base
- Settings beyond MVP runtime paths

Disabled placeholders must not call APIs or create fake data.

---

## 4. Target UI Framework

Phase 2 should treat UI structure as a product architecture concern, not as visual polish.

Recommended layout:

```text
+----------------------------------------------------------+
| Top Bar: product name, active project, environment status |
+----------------------+-----------------------------------+
| Left Navigation      | Main Work Area                    |
| - Intake             | - Page title / context            |
| - Projects           | - Primary action panel            |
| - Precheck           | - Data table / form / cards       |
| - LTR                | - Warnings / validation           |
| - Folders            | - Next action                     |
| - Settings           |                                   |
+----------------------+-----------------------------------+
```

### 4.1 UI Principles

- The left navigation expresses system modules.
- The right work area expresses the current task.
- Project workflow should be shown as steps, not loose buttons.
- Warnings and errors must be visually distinct.
- Status badges must be consistent across list and detail pages.
- Tables should be used for project lists and extraction results.
- Cards should be used for workflow step summaries and action panels.
- Destructive or filesystem actions require preview or confirmation.

### 4.2 Required UI Surfaces

- Intake Inbox: imported request materials and extraction status.
- Extraction Review: structured fields, sample rows, attachments, conflicts.
- Project List: table, filters, status badges, open workbench action.
- Project Workbench: step flow and current action panel.
- Precheck Panel: issue list, severity, field references, resolve/confirm action.
- LTR Panel: current LTR status and registration history.
- Folder Panel: template selection, preview tree, conflict status, generate action.

---

## 5. Target Business Data Flow

### 5.1 Real Intake Flow

```text
1. Import email or Word request material.
2. Store original material as FileAsset.
3. Extract request/application fields into a draft extraction record.
4. Extract samples into structured draft rows.
5. Register attachments and link them to the request.
6. Show extraction result to user.
7. User confirms, edits, or rejects extracted fields.
8. System creates or updates Project and ApplicationForm records.
9. System runs precheck.
```

### 5.2 Important State Distinction

Phase 2 should distinguish these states:

- Imported: raw material exists.
- Extracted: parser produced structured data.
- Needs Review: extraction has missing/conflicting fields.
- Confirmed: user accepted the intake data.
- Project Created: Project record exists.
- Precheck Completed: deterministic validation exists.
- LTR Registered: LTR record exists.
- Folder Created: project folder record exists.

Current Phase 1 records can remain, but Phase 2 likely needs an intake/draft concept before Project is created.

---

## 6. Proposed Phase 2 Task Sequence

The task sequence follows the Phase 1 operating model:

- one active task at a time
- task file first
- implementation only within task scope
- tests required
- board update after completion
- no future-scope shortcuts

### PHASE2_TASK_001_REAL_WORKFLOW_BASELINE

Goal:

- Document the real request intake workflow based on actual lab practice.

Scope:

- Define actor, input material, expected fields, decision points, and exception paths.
- Decide which request materials are primary: email, Word form, attachments.
- Define required field list for Project creation.
- Define when human confirmation is mandatory.

Deliverables:

- `docs/phase_2_workflow_baseline.md`
- Updated task board for Phase 2

Acceptance:

- The team can explain how a real request becomes a ConnLab project.
- Manual project creation is classified as fallback, not primary workflow.

### PHASE2_TASK_002_UI_WORKBENCH_BASELINE

Goal:

- Replace the verification shell with a durable application frame.

Scope:

- Left navigation.
- Top context/status bar.
- Main work area.
- Project table.
- Project workbench shell.
- Disabled placeholders for future modules only if clearly marked.

Out of scope:

- No new business APIs.
- No report, Matrix, AI, or advanced settings implementation.

Acceptance:

- UI no longer looks like a prototype form page.
- Existing MVP APIs still work.
- `npm run build` passes.

### PHASE2_TASK_003_INTAKE_IMPORT_MODEL

Goal:

- Add a model for imported request material before Project creation.

Scope:

- Introduce intake/import record concept.
- Persist source type, source path, original filename, import time, extraction status.
- Store original file as FileAsset or a dedicated import asset.
- Keep Project optional until confirmation.

Acceptance:

- A request material can be imported and persisted without creating a Project.
- The record can be listed in the Intake Inbox.

### PHASE2_TASK_004_WORD_APPLICATION_EXTRACTION_V2

Goal:

- Improve Word application form extraction against real files.

Scope:

- Add parser fixtures based on anonymized real forms.
- Extract requestor, contact, project number, business unit, site, requested testing.
- Extract sample rows reliably.
- Preserve parse warnings when fields are missing or ambiguous.

Acceptance:

- `sample_infos` is no longer empty for representative real forms.
- Parser failures are visible as structured warnings, not silent loss.

### PHASE2_TASK_005_EMAIL_IMPORT_GATEWAY

Goal:

- Add email import capability behind an infrastructure gateway.

Scope:

- Define `EmailImportGateway` or `OutlookMailGateway` interface.
- Support file-based `.eml` or exported email first if Outlook automation is risky.
- Extract sender, subject, body, received date, attachments.
- Register attachments for later parsing.

Out of scope:

- No direct UI or API calls to Outlook COM.
- No AI classification.

Acceptance:

- Email material can be imported into intake records.
- Attachments are traceable.

### PHASE2_TASK_006_EXTRACTION_REVIEW_UI

Goal:

- Let users review extracted fields before creating a project.

Scope:

- Intake detail page.
- Field review table/form.
- Sample rows table.
- Attachment list.
- Confirm/create project action.
- Missing/conflicting field indicators.

Acceptance:

- User can inspect extracted data and create a Project only after confirmation.

### PHASE2_TASK_007_PRECHECK_RULES_BUSINESS_V2

Goal:

- Expand precheck rules to match real intake expectations.

Scope:

- Required requestor/contact fields.
- Sample completeness.
- Requested testing specificity.
- Attachment dependency checks.
- Subcontract/lab section checks.
- Severity mapping: error/warning/info.

Acceptance:

- Precheck output is understandable to lab staff.
- Issues include field references and actionable messages.

### PHASE2_TASK_008_PROJECT_WORKBENCH_STATUS_FLOW

Goal:

- Make project status transitions explicit and visible.

Scope:

- Define allowed transitions from intake confirmation through folder creation.
- Show status badges and next recommended action.
- Avoid hidden status changes.

Acceptance:

- Project list and detail page show consistent status.
- User can understand what is complete and what is blocked.

### PHASE2_TASK_009_LTR_BUSINESS_FLOW_V2

Goal:

- Align LTR flow with real registration/tracking needs.

Scope:

- Confirm LTR number rules.
- Add edit/cancel/history if needed by business.
- Show duplicate and status conflict clearly.
- Connect LTR status to project workbench.

Acceptance:

- LTR handling reflects actual lab process, not just a single create call.

### PHASE2_TASK_010_FOLDER_TEMPLATE_BUSINESS_V2

Goal:

- Align folder generation with real folder naming and template conventions.

Scope:

- Confirm template root structure.
- Confirm placeholders.
- Add template selection UI.
- Show preview tree with conflicts.
- Keep overwrite protection.

Acceptance:

- Lab engineer can generate expected folder structure without code.

### PHASE2_TASK_011_END_TO_END_BUSINESS_SMOKE

Goal:

- Validate the Phase 2 business path end to end.

Scope:

- Import request material.
- Review extraction.
- Create Project.
- Run precheck.
- Register LTR.
- Preview/generate folder.
- Verify SQLite persistence.
- Verify manual frontend checklist.

Acceptance:

- A non-programmer can complete the real intake-to-folder workflow using UI.

---

## 7. Recommended Phase 2 Task Board Policy

Before implementation begins, create a new board section or new board file with:

- Current Phase: `Phase 2 - Business Intake And Workbench`
- Current Active Task: `PHASE2_TASK_001_REAL_WORKFLOW_BASELINE`
- Explicit blocked list for future modules
- Completion protocol identical to Phase 1

Recommended read order:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `docs/archive/historical_plans/phase_2_business_plan.md`
4. current `tasks/PHASE2_TASK_XXX_*.md`
5. any real-form or workflow reference docs required by the task

---

## 8. Risk Controls

### 8.1 Avoid Rebuilding Too Much At Once

Do not combine UI redesign, email import, parser rewrite, precheck rewrite, and LTR changes in one task. That creates unreviewable work.

### 8.2 Keep Raw Material Traceable

Imported emails, Word files, and attachments must be retained as original assets. Structured extraction should not replace source material.

### 8.3 Human Confirmation Is Mandatory

The system should not silently create authoritative project records from uncertain extraction. Parsed data should remain draft until confirmed.

### 8.4 Use Fixtures From Real Documents

Parser quality cannot be judged from synthetic documents alone. Use anonymized real request forms and email samples as test fixtures.

### 8.5 Keep Future Scope Blocked

Do not implement Matrix, reports, AI review, or permissions during Phase 2 unless the task board explicitly changes scope.

---

## 9. Phase 2 Entry Checklist

Before starting implementation:

- Confirm Phase 1 smoke still passes.
- Confirm `GET /api/projects` returns 200 in real runtime.
- Confirm SQLite contains expected tables.
- Collect at least 2-3 anonymized real Word application forms.
- Collect at least 2-3 anonymized request emails or exported email samples.
- Confirm real folder template expectations.
- Decide whether email import starts with `.eml` files, Outlook export, or live Outlook integration.
- Update task board to activate `PHASE2_TASK_001_REAL_WORKFLOW_BASELINE`.

---

## 10. Definition Of Phase 2 Done

Phase 2 is done when:

- Real request material can be imported.
- Extracted data can be reviewed before project creation.
- Sample information is extracted for representative real forms.
- Precheck issues are business-meaningful.
- UI has a stable left-navigation workbench layout.
- A lab engineer can complete the intake-to-folder workflow without code.
- Backend tests, frontend build, and manual smoke checklist pass.
