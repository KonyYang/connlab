# TASK_219A Project Workbench Runtime Console Repositioning Plan

## 1. Task Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `none; TASK_219 ... complete`
- This document is the required first deliverable for `TASK_219A_PROJECT_WORKBENCH_RUNTIME_CONSOLE_REPOSITIONING`.
- Scope for this step: plan only, no implementation.

## 2. Model Fit Assessment

`GPT-5.3-codex` is suitable for TASK_219A implementation because it is a bounded frontend IA/copy/visibility refactor in existing Workbench components. It does not require backend domain modeling, persistence, or runtime engine work.

## 3. Exact Current Workbench Section Inventory

Current Project Workbench first screen (from `ProjectWorkbenchLayout.tsx`) contains:

1. Runtime Console main shell:
- topbar (project identity + runtime metrics + actions)
- authority sync strip
- readiness strip
- filter bar
- matrix overview area
- step workspace area
- bottom runtime surfaces (`Runtime Attention`, `Recent activity`, `Fee estimate`)

2. Output status:
- `ProjectWorkbenchDocumentStatusPanel` section

3. Lower supporting `details` stack (legacy-setup heavy):
- `Setup Manager: project folder` -> `ProjectFolderCreationPanel`
- `Output Status: approval package` -> `ApprovalPackagePanel`
- `Setup Manager: evidence placement` -> `ProjectWorkbenchEvidencePanel`
- `Read-only lookup` -> `ProjectLookupPanel`

## 4. Proposed Before/After IA

Before:
- Runtime Console upper half + large setup/process forms in lower half.
- Workbench visually still behaves partly like a preparation console.

After:
- Workbench remains Runtime Console-first.
- Lower half converted to compact `Runtime support` summary cards with optional collapsed advanced support actions.
- Manual path-entry flows are demoted from primary surface.

Target lower IA:

1. Keep visible:
- output freshness/status panel (`ProjectWorkbenchDocumentStatusPanel`)
- compact runtime support status row:
  - folder state
  - approval package state
  - evidence placement state
  - lookup diagnostics availability

2. Demote:
- full `ApprovalPackagePanel` form
- full `ProjectFolderCreationPanel`
- full `ProjectWorkbenchEvidencePanel`
- `ProjectLookupPanel`

Demotion mode:
- hidden by default in a single advanced/collapsed support container.
- no removal of existing route or API behavior.

## 5. File-Level Implementation Plan

Primary files:

1. `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Replace current 4 large `details` blocks with:
  - compact runtime support summary cards
  - one `Advanced support` collapsible container (optional) that nests legacy panels
- keep existing runtime top surfaces unchanged.

2. `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- expose small derived status flags/text needed by compact support summary:
  - folder readiness summary
  - approval preview/result summary state
  - evidence preview/place summary state
- no API contract changes.

3. `frontend/src/workbench.css`
- style new compact `Runtime support` band/cards.
- reduce visual dominance of setup workflows.

Optional touched files (if test snapshots/static checks require):
- `tests/unit/test_frontend_shell_files.py`

No changes planned in backend/API:
- no edits under `backend/`
- no edits in `frontend/src/api/client.ts` contract shapes

## 6. Removed vs Retained Operator Actions

Removed from primary Workbench viewport:
- direct large manual path-entry focus for approval package
- large folder/evidence setup panels as default visible blocks

Retained:
- runtime metrics, matrix overview, step workspace, attention, recent activity, fee summary
- output status visibility
- access to legacy support actions through collapsed advanced support section
- Matrix Editor navigation

Not changed:
- backend capability for preview/execute approval package
- backend capability for folder creation and evidence placement
- lookup capability

## 7. Risk List

1. Regression risk: users may think setup actions were removed.
- Mitigation: keep explicit `Advanced support` entry with clear labels.

2. Visibility risk: hidden blockers in legacy workflows.
- Mitigation: compact support cards show warning/error badges derived from current states.

3. CSS spillover risk in existing Workbench dense layout.
- Mitigation: new class namespace under `runtime-support-*`; avoid broad selectors.

4. Static test drift risk.
- Mitigation: update frontend shell tests only if expectations are directly impacted.

## 8. Validation Commands

Required:

```powershell
cd frontend
npm run build
```

Required when touched:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Board-state governance (if `docs/task_board.md` is updated in implementation stage):

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 9. Manual Smoke Path

1. Open one project Workbench page.
2. Confirm top Runtime Console remains unchanged and primary.
3. Confirm Matrix Editor navigation still works.
4. Confirm output status panel remains visible and readable.
5. Confirm lower half now presents compact support summaries first.
6. Expand advanced support and confirm folder/approval/evidence/lookup flows are still reachable.
7. Confirm no runtime route breakage.

## 10. Stop Condition For Plan Stage

Plan file created. No implementation code is changed in this step. Wait for explicit user approval before entering TASK_219A implementation.
