# Matrix Editor Responsive Breakpoint Implementation Plan

> **For agentic workers:** This is a single-task inline implementation plan for a narrowly scoped CSS correction.

**Goal:** Keep Matrix Editor's main grid and Group Step Workspace side by side until the viewport is genuinely narrow.

**Architecture:** Preserve the existing React structure and responsive behavior. Change only the Matrix Editor media-query threshold in the feature's existing global workbench stylesheet, plus the existing frontend shell assertion that protects the breakpoint.

**Tech Stack:** React, TypeScript, CSS, Vitest, Vite.

## Global Constraints

- Do not change Matrix Editor component logic, API calls, data models, or persisted behavior.
- Keep ConnLab product UI rules and the existing left-navigation workbench shell.
- The single-column layout remains active at `max-width: 1024px`.

---

### Task 1: Adjust Matrix Editor Responsive Breakpoint

**Files:**
- Modify: `frontend/src/workbench.css:8814`
- Test: `tests/unit/test_frontend_shell_files.py:3683`

**Interfaces:**
- Preserve `.matrix-editor-studio` two-column layout above `1024px`.
- Preserve `.matrix-editor-step-workspace { width: 100%; }` in the narrow single-column layout.

- [x] Update the frontend shell assertion to expect `@media (max-width: 1024px)`.
- [x] Run the focused shell test and confirm it fails before CSS is updated.
- [x] Change the CSS media query from `1180px` to `1024px`.
- [x] Run the focused frontend test and confirm it passes.
- [x] Run the frontend build to catch CSS/TypeScript integration regressions.

## Validation

```powershell
cd frontend
npm test -- --run ../tests/unit/test_frontend_shell_files.py
npm run build
```

The Python shell test command above is the repository-level equivalent when validating the existing frontend shell assertions:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```
