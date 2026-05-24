# TASK_252CR Implementation Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `none`
- Why this plan is allowed now: user provided explicit UI refinement request for existing Matrix import preview flow; this document is for review/approval only and does not execute code changes yet.

## 1) Task Goal

Refine Matrix import confirmation UI so operators can read source context faster and reparse with consistent action affordances, without changing import data flow.

## 2) Input / Output

- Input: existing import modal UI state (`importPreview`, `locatorPage`, `locatorTableOnPage`, `locatorKeyword`, `importFile`).
- Output: improved modal layout and viewer URL options only.

No backend payload shape changes.

## 3) File-Level Change Plan

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
   - Keep title and filename in same row in dialog header structure.
   - Build preview iframe URL with PDF viewer parameters for:
     - open target page (`#page=<page>`)
     - fit-width zoom (`zoom=page-width`)
     - show navigation pane/thumbnails (`pagemode=thumbs`)
   - Keep fallback behavior when `locatorPage` is empty/invalid.
   - Keep existing reparse/apply handlers unchanged.
   - Adjust controls section markup to place `Page` and `Table on page` in a two-column row.

2. `frontend/src/workbench.css`
   - Add import-header inline layout class for single-line title+filename rendering with ellipsis safety.
   - Add two-column controls row style with responsive fallback.
   - Unify `.matrix-editor-import-reparse-button` with footer action system: height/min-width/typography/radius/primary blue palette.

3. `tests/unit/test_frontend_shell_files.py`
   - Add or update assertions that verify:
     - import modal contains new controls-row class usage
     - reparse button retains dedicated class and unified style tokens
     - no unintended removal of `Cancel/Replace/Append` action elements

## 4) Design Constraints

- Follow `PRODUCT.md` and `DESIGN.md`: operational tone, restrained palette, no decorative patterns.
- Respect frontend boundaries from `docs/frontend_architecture_rules.md`: no new API surface, no page-level workflow expansion.
- Keep this as UI-only hotfix scope.

## 5) Risk & Mitigation

1. PDF viewer fragment support variance across embedded browser engines.
   - Mitigation: build URL fragments with safe fallbacks; if fragment unsupported, existing PDF still renders.
2. Header single-line constraint may clip long filenames.
   - Mitigation: preserve `title` tooltip and ellipsis.
3. Button style unification may reduce visual distinction between reparse and commit.
   - Mitigation: keep reparse in controls pane and preserve clear position/context rather than introducing new copy.

## 6) Validation Plan

Automated:

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task252"
```

Manual:

1. Import `.docx`, verify header single-line presentation.
2. Verify preview opens at matrix page and displays width-fit page readability with left navigation thumbnails visible where engine supports it.
3. Verify `Page` + `Table on page` are side-by-side on desktop and stack on narrow widths.
4. Verify `Reparse` style consistency with footer action buttons and behavior unchanged.
5. Verify `Cancel/Replace/Append` and debounce reparse remain functional.

## 7) Out Of Scope

- Parser accuracy changes
- backend/API DTO changes
- new import file formats
- Matrix editor behavior outside import confirmation modal
