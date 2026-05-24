# ConnLab Phase 5 — Workbench UX Modernization Plan

> Version: v1.0  
> Suggested file path in repo: `docs/phase5_workbench_ux_plan.md`  
> Suggested task-board entry: `docs/task_board.md`  
> Phase type: Post-MVP UI/UX refinement  
> Scope: Frontend-first, no Matrix, no Report, no AI review

---

## 1. Executive Decision

The current project has completed the original MVP sequence from `TASK_001` through `TASK_015`. The backend MVP foundation is usable: project creation, application-form upload, deterministic precheck, LTR registration, folder preview/generation, local run scripts, frontend shell, and workflow integration are all present.

Therefore, the next stage should **not** start Matrix, Report, AI review, or deeper LIMS features yet. The best next phase is:

> **Phase 5 — Workbench UX Modernization**

Reason:

1. The MVP backend flow already exists.
2. The current frontend proves the workflow works, but it still looks and behaves like a prototype.
3. The user group includes non-programmer lab engineers.
4. ConnLab must become a workflow workbench, not another tool-style interface.
5. UI structure must be fixed before adding Matrix, Record, Result, Asset, and Report pages.

---

## 2. Current Project Completion Analysis

### 2.1 Completed MVP Task Chain

According to the current project task board, all 15 planned MVP tasks are complete:

| Area | Completed Tasks | Current Status |
|---|---:|---|
| Repository scaffold | TASK_001 | Complete |
| Config/logging/database foundation | TASK_002 - TASK_003 | Complete |
| Domain and storage models | TASK_004 - TASK_005 | Complete |
| Project API/service | TASK_006 | Complete |
| Application form parser | TASK_007 | Complete |
| Precheck engine | TASK_008 | Complete |
| Intake/precheck API | TASK_009 | Complete |
| LTR module | TASK_010 | Complete |
| Folder preview/generation | TASK_011 - TASK_012 | Complete |
| Minimal frontend and workflow integration | TASK_013 - TASK_014 | Complete |
| Packaging/run notes | TASK_015 | Complete |

The latest validation snapshot says:

```text
py -m pytest -p no:cacheprovider -> 40 passed
npm run build -> build passed
init_db.ps1 -> database initialized
```

This means the project is ready for a controlled post-MVP phase.

---

## 3. Current UI Problem Diagnosis

The current UI files show a minimal proof-of-workflow implementation:

```text
frontend/src/App.tsx
frontend/src/pages/ProjectListPage.tsx
frontend/src/pages/ProjectWorkbenchPage.tsx
frontend/src/styles.css
frontend/src/api/client.ts
```

### 3.1 Current UI Strengths

- It uses React + TypeScript.
- It has a small API client layer.
- It supports `/projects` and `/projects/:id`.
- It can create projects, upload forms, run precheck, register LTR, preview folder, and generate folder.
- It is already connected to backend API.

### 3.2 Current UI Weaknesses

| Problem | Current Symptom | Why It Matters |
|---|---|---|
| Not a workbench layout | Large hero + centered panels | Looks like landing page, not business system |
| No left navigation | User cannot understand system areas | Hard to expand into LIMS-like system |
| Task cards are parallel | Application/Precheck/LTR/Folder appear as independent cards | Real workflow is sequential |
| Error display is technical | `error: FORM-001...` list | Non-programmer users need business-language guidance |
| No project context panel | Project status is a line of text | Users need current project state at a glance |
| Folder step is too raw | Requires typing template path and target root | Lab users should not manually type long paths every time |
| No visual status system | Done/warning/pending/blocked not visually clear | Multi-project management needs strong status signals |

### 3.3 Main Conclusion

The current frontend fulfilled TASK_013/TASK_014 acceptance, but it is not yet an acceptable long-term ConnLab UI.

The next phase must convert it from:

```text
Prototype pages + cards
```

into:

```text
Left navigation + project dashboard + task-driven workbench
```

---

## 4. Phase 5 Goal

### 4.1 Phase Name

```text
Phase 5 — Workbench UX Modernization
```

### 4.2 Main Objective

Create a modern, LIMS-inspired, workflow-oriented frontend shell for ConnLab MVP without changing the backend business scope.

This phase is not "make the UI prettier". It is a product-architecture phase. The goal is to establish a durable workbench pattern before more real laboratory workflows are added.

### 4.3 Product Outcome

After this phase, a lab engineer should be able to open ConnLab and immediately understand:

```text
1. Which projects exist.
2. Which project needs attention.
3. What stage the project is in.
4. What the next action is.
5. What precheck problems must be resolved.
6. Whether LTR and folder generation are ready.
```

The interface must answer three questions on every page:

```text
What is the current state?
What is wrong or blocking?
What should I do next?
```

---

## 5. Scope Control

### 5.1 In Scope

- Replace landing-page style with workbench layout.
- Add left navigation.
- Improve project list/dashboard.
- Redesign project detail page as a workflow stepper.
- Improve precheck issue display.
- Improve application-form upload UX.
- Improve LTR and folder UX.
- Add frontend components and tests.
- Update task board and docs.

### 5.2 Out of Scope

Still forbidden in this phase:

```text
Matrix generation
Test Record generation
Excel result ingestion
Image asset classification
Report generation
Report audit
AI review
LAN deployment
Multi-user permissions
Full installer
```

Real-world email/Word intake hardening is also not implemented in this UX phase. It should be planned after the workbench shell is stable, because that feature needs a reliable review UI and status model first.

### 5.3 Backend Change Rule

This phase should be **frontend-first**.

Backend changes are allowed only when necessary to support already-existing MVP data display, such as:

- exposing project status more clearly;
- returning latest LTR/folder state;
- improving API response DTOs without adding new domain features.

No new business domain should be added.

### 5.4 Mandatory `$impeccable` Rule

All Phase 5 UX/UI work must use `$impeccable`.

Before any Phase 5 task that designs, changes, critiques, polishes, audits, or refactors frontend UI, the agent must:

1. Load the `$impeccable` skill context.
2. Read `PRODUCT.md`.
3. Read `DESIGN.md`.
4. Use `DESIGN.json` as the design-system sidecar when relevant.
5. Treat ConnLab as `register: product`.
6. Apply the product UI reference rules: familiar product patterns, restrained color, consistent component vocabulary, clear state, clear next action.

If `PRODUCT.md`, `DESIGN.md`, or `DESIGN.json` is missing or stale, the task must stop and refresh those files before changing UI code.

This rule applies to:

- app shell layout
- navigation
- dashboard
- project workbench
- workflow stepper
- issue display
- forms
- empty/loading/error states
- status badges
- spacing, typography, color, motion, and UX copy

It does not apply to backend-only bug fixes.

---

## 6. Target UI Architecture

### 6.1 Recommended Frontend Structure

```text
frontend/src/
├── api/
│   └── client.ts
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx
│   │   ├── Sidebar.tsx
│   │   └── TopBar.tsx
│   ├── project/
│   │   ├── ProjectCard.tsx
│   │   ├── ProjectStatusBadge.tsx
│   │   └── ProjectSummaryPanel.tsx
│   ├── workflow/
│   │   ├── WorkflowStepper.tsx
│   │   ├── WorkflowStepCard.tsx
│   │   └── NextActionPanel.tsx
│   ├── precheck/
│   │   ├── PrecheckIssueCard.tsx
│   │   ├── PrecheckSummary.tsx
│   │   └── IssueSeverityBadge.tsx
│   └── common/
│       ├── EmptyState.tsx
│       ├── LoadingState.tsx
│       └── ErrorMessage.tsx
├── pages/
│   ├── ProjectListPage.tsx
│   └── ProjectWorkbenchPage.tsx
├── styles.css
└── App.tsx
```

### 6.2 Target Layout

```text
┌────────────────────────────────────────────────────────────┐
│ ConnLab Top Bar                                            │
├───────────────┬────────────────────────────────────────────┤
│ Sidebar       │ Main Work Area                             │
│               │                                            │
│ Dashboard     │ Project Dashboard / Workbench              │
│ Projects      │                                            │
│ Precheck      │ Current project summary                    │
│ LTR           │ Workflow stepper                           │
│ Folder        │ Active step content                        │
│ Settings      │                                            │
└───────────────┴────────────────────────────────────────────┘
```

### 6.2.1 Recommended Information Architecture

Use a left-navigation laboratory workbench, not a landing page and not a toolbox.

Primary navigation:

```text
Dashboard
Projects
Intake
Precheck
LTR
Folders
Settings
```

Rules:

- Dashboard summarizes project attention items.
- Projects is the main project registry.
- Intake is where imported request materials will later enter.
- Precheck, LTR, and Folders may deep-link to filtered project work items, but should not become disconnected tools.
- Future modules such as Matrix, Reports, AI Review, and Knowledge Base must remain absent or visibly disabled until explicitly opened by a later task.

### 6.2.2 Project Workbench Pattern

The project detail page should become the center of work.

Recommended structure:

```text
Project summary
Workflow stepper
Current action panel
Warnings / blockers
File and history context
```

The workbench should avoid showing all forms at once. A lab engineer should see the active step first, with blocked or completed steps summarized.

### 6.3 MVP Workflow Display

```text
Application Form  ->  Precheck  ->  LTR  ->  Project Folder
uploaded/done        warning       pending   locked/ready
```

Each step should have:

- title;
- short business description;
- status;
- next action button;
- blocking reason if not available.

---

## 7. UX Rules For ConnLab

### 7.1 UI Language Rule

Do not display internal messages as the primary user-facing text.

Bad:

```text
error: FORM-001: Form No. must be E-3718
```

Good:

```text
Form number is not confirmed
Expected: E-3718
Current: Not recognized
Action: Check the footer of the application form.
```

### 7.2 Status Vocabulary

Use consistent MVP statuses:

```text
not_started
ready
in_progress
passed
warning
failed
blocked
completed
```

### 7.3 Visual Severity

```text
Error   -> red    -> blocks next step
Warning -> amber  -> requires confirmation
Passed  -> green  -> may continue
Pending -> gray   -> waiting
Ready   -> blue   -> actionable
```

### 7.4 User Guidance Rule

Every page must answer:

```text
What is the current state?
What is wrong?
What should I do next?
```

### 7.5 LIMS Failure Modes To Avoid

These patterns often make lab systems fail in practice:

- Too many independent menu items with no obvious next action.
- Project creation too early, before imported request data has been reviewed.
- Raw backend errors shown as user instructions.
- All lifecycle actions placed on one overloaded detail page.
- Status values hidden in the database but not explained in the UI.
- Warning, error, and missing-data states using the same visual treatment.
- Generated folders or files without preview.
- Future modules exposed as if they already work.
- Parser output treated as truth before human confirmation.

Phase 5 should prevent the UI-specific failures now. Real intake confirmation will be handled in a later parser/intake phase.

### 7.6 Status And Next Action Model

For frontend display, derive a UI state from existing MVP records:

```text
not_started
ready
in_progress
passed
warning
failed
blocked
completed
```

Each workflow step should expose:

- `status`
- `label`
- `blockingReason`
- `nextActionLabel`
- `canRunAction`

This can be frontend-derived in Phase 5. Do not add backend state tables unless a specific task later requires it.

---

## 8. Suggested Task Board Update

Add this to `docs/task_board.md` after the MVP completion section.

```markdown
## Phase 5 - Workbench UX Modernization

### Goal

Convert the completed MVP prototype frontend into a modern workflow-oriented ConnLab workbench.

### Current Active Task

`TASK_016_UX_BASELINE_AND_DECISION_RECORD`

### Scope

- Left navigation shell
- Project dashboard
- Project workbench stepper
- Business-readable precheck issue panel
- Better upload/LTR/folder UX
- Frontend tests/build guard

### Out of Scope

- Matrix
- Report generation
- AI review
- Test result ingestion
- Image asset management
- Multi-user permissions

### Status Table

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T5-1 | `TASK_016_UX_BASELINE_AND_DECISION_RECORD` | todo | Establish target UX and approved component structure |
| T5-2 | `TASK_017_APP_SHELL_LEFT_NAV` | todo | Replace hero layout with app shell + sidebar |
| T5-3 | `TASK_018_PROJECT_DASHBOARD` | todo | Modern project list/search/status cards |
| T5-4 | `TASK_019_PROJECT_WORKBENCH_STEPPER` | todo | Sequential MVP workflow stepper |
| T5-5 | `TASK_020_PRECHECK_ISSUE_EXPERIENCE` | todo | Business-language issue cards and summary |
| T5-6 | `TASK_021_INTAKE_LTR_FOLDER_UX` | todo | Improve upload, LTR, and folder actions |
| T5-7 | `TASK_022_FRONTEND_STATE_AND_API_CLEANUP` | todo | Clean client/state patterns without adding scope |
| T5-8 | `TASK_023_FRONTEND_TEST_AND_BUILD_GUARD` | todo | Add frontend build/test guard and smoke checklist |
| T5-9 | `TASK_024_PHASE5_DOCS_AND_BOARD_SYNC` | todo | Update docs and task board after UX phase |
```

---

## 9. Concrete Implementation Tasks

The following tasks are written in the same style as existing `tasks/TASK_XXX_*.md` files. Create them one by one under `tasks/`.

---

# TASK 016 — UX Baseline And Decision Record

## Goal

Document the approved ConnLab workbench UX direction before changing frontend code.

## Scope

- Review current frontend pages.
- Record target layout: left navigation + right work area.
- Record UX rules for status, issue display, and workflow stepper.
- Add a short decision record to `docs/`.
- Update `docs/task_board.md` to activate Phase 5.

## Required Output

Create:

```text
docs/archive/historical_plans/phase5_workbench_ux_decision.md
```

## Must Include

- Why current UI is insufficient.
- Target layout diagram.
- Approved MVP workflow steps.
- Out-of-scope list.
- Component structure proposal.
- LIMS failure modes to avoid.
- Status and next-action vocabulary.

## Out of Scope

- No frontend implementation yet.
- No backend changes.
- No new dependencies.

## Acceptance Criteria

- Decision doc exists.
- Task board shows Phase 5 active.
- No source code behavior changes.

---

# TASK 017 — App Shell With Left Navigation

## Goal

Replace the current landing-page style shell with a modern app shell using left navigation and a main work area.

## Scope

Modify frontend only.

Create components:

```text
frontend/src/components/layout/AppShell.tsx
frontend/src/components/layout/Sidebar.tsx
frontend/src/components/layout/TopBar.tsx
```

Update:

```text
frontend/src/App.tsx
frontend/src/styles.css
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Left sidebar includes: Dashboard, Projects, Precheck, LTR, Folder, Settings.
- Disabled future placeholders may be shown but must not open future features.
- Main area renders current routes.
- Remove oversized hero layout.
- Preserve existing routes `/projects` and `/projects/:id`.

## Out of Scope

- No Matrix nav.
- No Report nav.
- No authentication.
- No backend changes.

## Acceptance Criteria

- App opens with left navigation.
- Existing project list and detail routes still work.
- `npm run build` passes.

---

# TASK 018 — Project Dashboard Redesign

## Goal

Redesign the project list page into a usable dashboard for lab engineers.

## Scope

Update:

```text
frontend/src/pages/ProjectListPage.tsx
```

Add components:

```text
frontend/src/components/project/ProjectCard.tsx
frontend/src/components/project/ProjectStatusBadge.tsx
frontend/src/components/common/EmptyState.tsx
frontend/src/components/common/ErrorMessage.tsx
frontend/src/components/common/LoadingState.tsx
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Show project list/dashboard with project number, product name, requestor, business unit, status.
- Prefer table or dense dashboard rows for project lists; use cards only for summary metrics or attention items.
- Add search input placeholder UI. If backend search is not available, filter client-side only.
- Keep create project form, but redesign it as a compact “New Project” panel.
- Show clear empty/loading/error states.

## Out of Scope

- No advanced filtering API unless already available.
- No pagination.
- No multi-user features.

## Acceptance Criteria

- User can still create a project.
- User can still open a project.
- Page is clearly a dashboard, not a landing page.
- `npm run build` passes.

---

# TASK 019 — Project Workbench Stepper

## Goal

Convert project detail page from parallel task cards into a sequential workflow workbench.

## Scope

Update:

```text
frontend/src/pages/ProjectWorkbenchPage.tsx
```

Add components:

```text
frontend/src/components/workflow/WorkflowStepper.tsx
frontend/src/components/workflow/WorkflowStepCard.tsx
frontend/src/components/workflow/NextActionPanel.tsx
frontend/src/components/project/ProjectSummaryPanel.tsx
```

## Workflow Steps

```text
1. Application Form
2. Precheck
3. LTR
4. Project Folder
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Show current project summary at top.
- Show workflow stepper below summary.
- Highlight current/blocked/ready/done states.
- Only show active step content in the main content panel.
- Do not display all forms at once.
- Every step must show next action or blocking reason.

## Out of Scope

- No new backend states unless required by existing data mapping.
- No Matrix/Report steps.

## Acceptance Criteria

- User can complete the same MVP workflow.
- Step order is visually obvious.
- Folder step is blocked until prerequisites are reasonable in UI.
- `npm run build` passes.

---

# TASK 020 — Precheck Issue Experience

## Goal

Make precheck results understandable for non-programmer lab engineers.

## Scope

Add components:

```text
frontend/src/components/precheck/PrecheckSummary.tsx
frontend/src/components/precheck/PrecheckIssueCard.tsx
frontend/src/components/precheck/IssueSeverityBadge.tsx
```

Update precheck display in:

```text
frontend/src/pages/ProjectWorkbenchPage.tsx
```

## Requirements

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.

Convert technical issue display into business-readable cards:

- issue title;
- severity;
- field/category;
- what is wrong;
- expected value if available;
- suggested action.

If backend issue only has `message`, derive a simple display from current fields without changing backend schema.

## Out of Scope

- No AI explanation.
- No new precheck rules.
- No backend rule changes.

## Acceptance Criteria

- Precheck issues are no longer shown as raw list items only.
- Errors and warnings are visually distinct.
- User can understand what to fix next.
- `npm run build` passes.

---

# TASK 021 — Intake, LTR, And Folder UX Refinement

## Goal

Improve the three MVP action panels: upload application form, register LTR, preview/generate folder.

## Scope

Frontend only unless a tiny API DTO display fix is necessary.

## Requirements

### Application Form

- Use `$impeccable` before designing or editing UI.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Use clear upload panel.
- Show uploaded form metadata.
- Show next action after upload.

### LTR

- Show latest LTR clearly.
- Show “not registered / registered” status.
- Keep simple registration input.

### Folder

- Show folder preview as a tree-like preview.
- Display conflict status clearly.
- Disable generate button when conflict exists.
- Avoid overwhelming users with raw paths first.

## Out of Scope

- No file picker integration with Windows shell.
- No template management page.
- No automatic LTR application.

## Acceptance Criteria

- Existing API calls still work.
- User sees clear action state for each MVP step.
- `npm run build` passes.

---

# TASK 022 — Frontend State And API Cleanup

## Goal

Clean frontend state and API usage after the UI refactor so code remains maintainable.

## Scope

- Keep `frontend/src/api/client.ts` as the only API client entry.
- Avoid duplicating fetch logic in pages.
- Extract repeated status mapping helpers.
- Extract workflow state derivation helper.

Suggested file:

```text
frontend/src/components/workflow/workflowState.ts
```

## Requirements

- Use `$impeccable` before designing or editing UI cleanup.
- Follow `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`.
- Keep pages readable.
- Avoid giant component files.
- Do not change backend contracts unless necessary.

## Out of Scope

- No Redux or global state library.
- No React Query unless explicitly approved.
- No new backend features.

## Acceptance Criteria

- ProjectWorkbenchPage is smaller and easier to read.
- API calls stay centralized.
- `npm run build` passes.

---

# TASK 023 — Frontend Build And Smoke Guard

## Goal

Add minimal frontend validation so future UI changes do not silently break MVP flow.

## Scope

- Use `$impeccable` before changing frontend validation UX or smoke checklist wording.
- Add or update a smoke checklist.
- Add a script/check that runs frontend build.
- Update README with frontend validation command.
- Optional: add simple component tests only if test framework already exists or is explicitly added.

## Recommended File

```text
docs/archive/validation_summaries/frontend_smoke_checklist.md
```

## Smoke Checklist Must Cover

- project list loads;
- project can be created;
- project detail opens;
- application form upload UI appears;
- precheck panel appears;
- LTR panel appears;
- folder preview/generate panel appears;
- no Matrix/Report UI exposed as active features.

## Out of Scope

- No end-to-end browser automation yet.
- No Playwright/Cypress unless explicitly approved.

## Acceptance Criteria

- `npm run build` passes.
- `docs/archive/validation_summaries/frontend_smoke_checklist.md` exists.
- README points to frontend validation.

---

# TASK 024 — Phase 5 Docs And Board Sync

## Goal

Close Phase 5 properly by updating docs and task board.

## Scope

Update:

```text
docs/task_board.md
docs/archive/historical_plans/phase5_workbench_ux_decision.md
README.md if needed
```

## Requirements

- Use `$impeccable` before final UX documentation sync.
- Confirm `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json` still match the implemented UI direction.
- Mark Phase 5 tasks complete or accurately blocked.
- Record latest validation:
  - backend pytest result;
  - frontend build result;
  - manual smoke result.
- State next recommended phase.

## Suggested Next Phase Candidates

Do not automatically start them. Only recommend.

```text
Phase 6A — Application Form Real-World Parser Hardening
Phase 6B — Folder Template Configuration UX
Phase 6C — Precheck Rule Expansion
Phase 6D — Real Email/Word Intake And Human Confirmation
```

## Out of Scope

- No implementation changes unless correcting documentation paths.

## Acceptance Criteria

- Board reflects real project state.
- No active task ambiguity remains.
- Next phase requires explicit approval.

---

## 10. Recommended Execution Order

Run tasks in this order:

```text
TASK_016_UX_BASELINE_AND_DECISION_RECORD
TASK_017_APP_SHELL_LEFT_NAV
TASK_018_PROJECT_DASHBOARD
TASK_019_PROJECT_WORKBENCH_STEPPER
TASK_020_PRECHECK_ISSUE_EXPERIENCE
TASK_021_INTAKE_LTR_FOLDER_UX
TASK_022_FRONTEND_STATE_AND_API_CLEANUP
TASK_023_FRONTEND_TEST_AND_BUILD_GUARD
TASK_024_PHASE5_DOCS_AND_BOARD_SYNC
```

Do not combine tasks until TASK_017 and TASK_018 are stable.

---

## 11. Codex Prompt For Next Task

Use this exact prompt when starting Phase 5:

```text
Read AGENTS.md first.
Then read docs/task_board.md.
Then read tasks/TASK_016_UX_BASELINE_AND_DECISION_RECORD.md.

Current phase is Phase 5 - Workbench UX Modernization.
Implement only TASK_016.
Do not implement Matrix, Report, AI review, or any future-scope feature.
Do not modify backend behavior.
Before making changes, summarize the current active task and its out-of-scope items.
After finishing, update docs/task_board.md with status and next active task.
```

---

## 12. Phase 5 Acceptance Gate

Phase 5 is complete only when:

```text
1. Left navigation workbench shell exists.
2. Project dashboard is usable by non-programmer lab engineers.
3. Project detail page uses sequential workflow stepper.
4. Precheck issues are business-readable.
5. Application/LTR/Folder actions are easier to operate.
6. Existing MVP backend workflow still works.
7. Backend tests pass.
8. Frontend build passes.
9. Manual smoke checklist passes.
10. docs/task_board.md is updated.
```

---

## 13. Recommended Next Phase After Phase 5

Do not start immediately. Choose after UI refactor is stable.

### Option A — Parser Hardening

Best if real application forms parse poorly.

Focus:

```text
more robust DOCX table parsing
field confidence score
manual correction form
attachment registration
```

### Option B — Folder Template Configuration

Best if folder generation is still too technical.

Focus:

```text
template registry
default target root
placeholder preview
template validation
```

### Option C — Precheck Rule Expansion

Best if lab users want more early quality control.

Focus:

```text
more rules
issue confirmation workflow
precheck summary export
estimated completion date helper
```

Recommended order:

```text
Phase 5 -> Real Intake/Parser Hardening -> Folder Template UX -> Precheck Rule Expansion
```

Reason: Better parsing improves all downstream precheck and project creation quality.

---

## 14. Final Expert Recommendation

The MVP backend is now good enough to support real UI workflow refinement. The next step should not be new business features. It should be to make ConnLab look and behave like a real lab workbench.

The correct immediate next move is:

```text
Start Phase 5 with TASK_016.
```

Then implement the left-navigation workbench design in small controlled steps.
