# Phase 5 Workbench UX Decision Record

> Status: implemented baseline  
> Date: 2026-04-26  
> Completion task: `TASK_024_PHASE5_DOCS_AND_BOARD_SYNC`  
> Register: product UI  
> Scope: frontend-first workbench modernization

---

## 1. Decision Summary

ConnLab will move from the current prototype pages to a restrained, LIMS-inspired workbench UI.

The approved direction is:

```text
Left navigation + top context bar + main work area
```

This is a product UI, not a marketing surface. Design must serve laboratory tasks, reduce cognitive load, and make status plus next action obvious.

Phase 5 does not add new backend business scope. It reorganizes and clarifies the existing MVP workflow:

```text
Application Form -> Precheck -> LTR -> Project Folder
```

---

## 2. Why The Current UI Is Insufficient

The current UI completed the first technical goal: prove that the frontend can call the backend MVP flow. It is not acceptable as the long-term workbench.

Problems:

- It uses a large landing-page hero, which makes ConnLab feel like a demo page instead of a work tool.
- It has no persistent navigation, so users cannot see the system areas.
- Project actions are shown as parallel cards, but the real flow is sequential.
- Project status is displayed as plain text, not as a lifecycle signal.
- Precheck issues are shown too close to raw backend output.
- Folder generation asks users to type technical paths without enough guidance.
- Error, warning, pending, blocked, and completed states do not have a consistent visual language.
- The UI does not reliably answer what the user should do next.

The redesign must make ConnLab feel like a trusted laboratory operations tool, not a generic generated dashboard.

---

## 3. Physical Usage Scene

Primary scene:

```text
A lab engineer uses ConnLab on a Windows workstation during daytime lab administration, with email, Word documents, file folders, and project requests open nearby.
```

Design consequence:

- Use a light, calm interface.
- Prefer dense but readable layouts.
- Avoid theatrical motion.
- Avoid dark theme as a default.
- Use familiar navigation and form patterns.
- Use color for state and attention, not decoration.

---

## 4. Approved Layout

Target shell:

```text
+--------------------------------------------------------------+
| Top Bar: ConnLab, current context, local/offline status        |
+----------------------+---------------------------------------+
| Sidebar              | Main Work Area                        |
|                      |                                       |
| Dashboard            | Page title and primary task           |
| Projects             | Project table / workbench / panels    |
| Intake               | Status, warnings, next action         |
| Precheck             |                                       |
| LTR                  |                                       |
| Folders              |                                       |
| Settings             |                                       |
+----------------------+---------------------------------------+
```

Navigation rules:

- `Dashboard` summarizes attention items.
- `Projects` is the project registry and default daily work surface.
- `Intake` is present as a future real-request-material entry point, but Phase 5 does not implement real email or Word intake.
- `Precheck`, `LTR`, and `Folders` should guide users to project-scoped work, not become disconnected tools.
- Matrix, Report, AI Review, permissions, LAN deployment, and installer work remain out of scope.

---

## 5. Approved MVP Workflow Steps

Project workbench steps:

```text
1. Application Form
2. Precheck
3. LTR
4. Project Folder
```

Each step must show:

- current status
- next action
- blocking reason when action is unavailable
- concise business description
- relevant result summary

The project detail page should not show every form at once. It should show a workflow stepper and a focused current action panel.

---

## 6. Status And Next Action Vocabulary

Use this frontend status vocabulary for Phase 5:

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

Semantic color roles:

- `not_started`: neutral gray
- `ready`: restrained blue
- `in_progress`: blue with motion or progress text only when needed
- `passed`: green
- `warning`: amber
- `failed`: red
- `blocked`: red or strong amber, depending on severity
- `completed`: green or neutral confirmed state

Every workflow step should derive:

```text
status
label
blockingReason
nextActionLabel
canRunAction
```

This can be frontend-derived from existing MVP records in Phase 5. Do not add new backend state tables for this phase.

---

## 7. Issue Display Rules

Precheck issues must be written for lab staff.

Do not use raw technical messages as the main display.

Bad:

```text
FORM-001: Form No. must be E-3718
```

Approved display pattern:

```text
Title: Form number is not confirmed
Severity: Warning
Field: Form No.
Problem: The expected form number was not recognized.
Expected: E-3718
Action: Check the application form header or footer.
```

If backend data only provides a message, the frontend may derive a simple card from existing fields. It must not invent unsupported business facts.

---

## 8. Component Structure Proposal

Target structure:

```text
frontend/src/
  api/
    client.ts
  components/
    layout/
      AppShell.tsx
      Sidebar.tsx
      TopBar.tsx
    common/
      EmptyState.tsx
      ErrorMessage.tsx
      LoadingState.tsx
    project/
      ProjectStatusBadge.tsx
      ProjectSummaryPanel.tsx
    workflow/
      WorkflowStepper.tsx
      WorkflowStepCard.tsx
      NextActionPanel.tsx
      workflowState.ts
    precheck/
      PrecheckSummary.tsx
      PrecheckIssueCard.tsx
      IssueSeverityBadge.tsx
  pages/
    ProjectListPage.tsx
    ProjectWorkbenchPage.tsx
  App.tsx
  styles.css
```

Rules:

- `frontend/src/api/client.ts` remains the only API client entry.
- Pages should orchestrate screens, not contain all UI details.
- Repeated states and status mapping should move into helpers or small components.
- Avoid introducing Redux, React Query, component libraries, or routing libraries unless explicitly approved.

---

## 9. Visual Direction

Use a restrained product UI.

Design choices:

- Light interface, because the primary scene is daytime Windows lab administration.
- Tinted neutrals, not pure black or pure white.
- One primary accent for current navigation, primary actions, and focus.
- Semantic colors only for status and severity.
- System UI typography is acceptable and preferred for product familiarity.
- Tables and dense rows are appropriate for project lists.
- Cards are reserved for summaries, workflow panels, and issue details.
- No decorative glassmorphism.
- No gradient text.
- No colored side-stripe cards.
- No identical icon-card grids.
- Motion should be short and state-driven only.

---

## 10. LIMS Failure Modes To Avoid

Phase 5 must prevent these known failure patterns:

- A toolbox UI where users choose from many disconnected buttons.
- Future modules shown as active when they do not work.
- Project status hidden in backend values without explanation.
- Warnings and blocking errors styled the same way.
- Raw `Internal Server Error` or 404 text shown as user guidance.
- Folder generation without preview.
- All lifecycle actions stacked into one long page.
- Parser output treated as authoritative without future human confirmation.
- Manual project creation presented as the only long-term intake model.

---

## 11. Out Of Scope

Do not implement these in Phase 5:

- Matrix generation
- Test record generation
- Report generation
- Report audit
- AI review
- Knowledge base
- Multi-user permissions
- LAN deployment
- Full installer
- PyInstaller
- PyWebView shell
- Real email import
- Real Word parser hardening
- New backend workflow entities

Real email and Word intake should come after the workbench shell is stable, because it needs a reliable review and status UI.

---

## 12. Acceptance For Phase 5 UI Work

Each implementation task after this decision record must preserve:

- existing MVP API behavior
- backend test pass
- frontend build pass
- no future-scope navigation exposed as active
- clear current state, blocking reason, and next action

Phase 5 is successful when a non-programmer lab engineer can open ConnLab and understand:

- where projects are
- which project needs attention
- what stage a project is in
- what action is next
- whether precheck, LTR, and folder steps are ready, blocked, or complete

---

## 13. Implemented Phase 5 Result

Phase 5 implemented the approved workbench direction without adding future backend business scope.

Completed UI outcomes:

- Left navigation app shell with top context bar.
- Project registry dashboard with search, dense project table, status badges, and clear loading/empty/error states.
- Project workbench with project summary, sequential workflow stepper, and one active action panel.
- Business-readable precheck summary and issue cards.
- Application form action panel with uploaded metadata and next action guidance.
- LTR action panel with latest LTR / not registered state.
- Folder action panel with tree-like preview, conflict display, and disabled generate action when conflicts exist.
- Frontend state derivation extracted into `frontend/src/components/workflow/workflowState.ts`.
- Raw `fetch` usage guarded to `frontend/src/api/client.ts`.
- Frontend build command and manual smoke checklist documented.

Confirmed design-context alignment:

- `PRODUCT.md` still declares `register: product` and matches the offline laboratory workbench mission.
- `DESIGN.md` still matches the implemented restrained, warm, dense product UI.
- `DESIGN.json` remains valid design-system sidecar context for future `$impeccable` work.

Latest automatic validation:

```text
.\scripts\run_frontend_build.ps1 -> passed
py -m pytest -p no:cacheprovider -> 56 passed
```

Manual browser smoke status:

```text
docs\frontend_smoke_checklist.md -> documented
manual execution -> pending human confirmation
```

Reason: Codex validated code, build, and static guards in the terminal. Browser-based manual smoke requires a human run against the local dev servers.

---

## 14. Next Phase Recommendation

Do not start the next phase automatically. Phase 6 requires explicit user approval.

Recommended order:

1. `Phase 6A - Real Email/Word Intake And Human Confirmation`
2. `Phase 6B - Application Form Parser Hardening`
3. `Phase 6C - Folder Template Configuration UX`
4. `Phase 6D - Precheck Rule Expansion`

Preferred next step:

```text
Phase 6A - Real Email/Word Intake And Human Confirmation
```

Reason: the current UI now has enough structure to support the real intake problem: imported request material should be reviewed and confirmed by humans before project data becomes authoritative.
