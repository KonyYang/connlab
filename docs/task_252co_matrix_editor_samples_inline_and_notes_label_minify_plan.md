# TASK_252CO Plan - Matrix Editor Samples Inline And Notes Label Minify

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CO_MATRIX_EDITOR_SAMPLES_INLINE_AND_NOTES_LABEL_MINIFY` (planned, awaiting approval)
- Why allowed now: user requested a focused Step preview UI refinement and board has no active task.

## 1. Task Understanding

1. Goal:
   - `Samples` and the input field must stay on one line.
   - `Samples Notes` heading should be simplified to `Notes` or removed.
2. Input:
   - Current Matrix Editor Step preview rendering.
3. Output:
   - Inline samples row and simplified notes title with unchanged note content.
4. Modules:
   - `MatrixEditorWorkspace.tsx`, `workbench.css`, frontend shell static checks.
5. Not allowed:
   - No backend/parser/API changes.

## 2. Design

1. UI text/render:
   - Change sample-note heading text from `Samples Notes` to `Notes`.
   - Keep note paragraphs unchanged.
2. Layout:
   - Enforce one-line layout for `Samples` label + input using flex row container.
   - Keep responsive behavior by letting input take remaining width.
3. Test updates:
   - Add/update static assertion for new heading and inline samples class usage.

## 3. Risks and Mitigations

1. Risk: small viewport wraps row unexpectedly.
   - Mitigation: explicit no-wrap row style + flexible input width.
2. Risk: existing tests pinned to old heading string.
   - Mitigation: update static assertions in same task.

## 4. Validation Plan

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252co or matrix_editor"
```

```powershell
cd frontend
npm run build
```

## 5. Acceptance Gate

Do not implement until user explicitly approves this plan.
