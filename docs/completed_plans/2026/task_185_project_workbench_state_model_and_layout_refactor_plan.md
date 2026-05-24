# TASK_185 Plan - Project Workbench State Model And Layout Refactor

## 1. Current Phase And Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task before creation: `TASK_184` complete.
- This plan is proposal-only. Implementation must wait for explicit approval: `批准执行 TASK_185`.

## 2. Goal

Reduce Project Workbench page complexity and establish a stage-oriented frontend architecture without changing current business behavior.

Core outcomes:

- route page becomes thin;
- workbench state and side effects move into one feature model hook;
- workbench visual composition moves into stage layout components;
- existing folder/evidence/approval flows remain behavior-compatible.

## 3. Current Pain

Current route page (`ProjectWorkbenchPage.tsx`) still mixes:

- multiple API loading paths;
- feature state containers;
- workflow side effects;
- large inline evidence rendering.

This directly conflicts with frontend architecture guidance that route pages should compose feature components and keep business orchestration in features/hooks/selectors.

## 4. Refactor Strategy

1. Build model hook first.
2. Move large rendering blocks into feature components.
3. Recompose route page around layout + model.
4. Keep all current operations and API contracts unchanged.
5. Validate with build + static guards.

## 5. Proposed File-Level Changes

### Add: `useProjectWorkbenchModel.ts`

Responsibility:

- load project/ltr/resources;
- manage folder-ready derived state;
- manage evidence preview/place states;
- manage approval package input/preview/execute states;
- expose callbacks and view-ready fields.

### Add: `ProjectWorkbenchLayout.tsx`

Responsibility:

- header/status strip;
- stage sections composition order;
- shared message/error surface rendering hooks from model.

### Add: `ProjectWorkbenchEvidencePanel.tsx`

Responsibility:

- render evidence preview/place UI now inline in route page;
- keep button enable/disable behavior and display text consistent.

### Update: `ProjectWorkbenchPage.tsx`

Responsibility after refactor:

- route-level loading boundary;
- inject `projectId`, `onBack`;
- call model hook;
- render layout.

### Approval package panel location

Preferred:

- relocate into `features/project-workbench/` for ownership clarity.

Fallback:

- keep component in current location and provide feature wrapper if static tests are sensitive.

## 6. Behavior Preservation Checklist

- Folder creation flow unchanged.
- Evidence placement preview/place unchanged.
- Approval package preview/execute unchanged.
- Project lookup panel remains accessible in Workbench (can be stage-positioned).
- No new backend endpoints or payload changes.

## 7. Risk Control

- Risk: accidental copy/text drift in evidence or approval panel.
  - Control: reuse existing strings and status logic.
- Risk: over-refactor beyond TASK_185.
  - Control: no Matrix review feature implementation in this task.
- Risk: static test break due to file relocation.
  - Control: update static tests minimally and only for changed ownership paths.

## 8. Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"
```

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 9. Output

When approved and implemented, TASK_185 should deliver a Workbench structure that is ready for:

- TASK_186 Matrix review surface;
- TASK_187 auto-carry document pipeline;
- TASK_188 stale/version indicators.
