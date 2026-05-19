# TASK_233 Matrix Editor Step Description Special Rules Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_233_MATRIX_EDITOR_STEP_DESCRIPTION_SPECIAL_RULES`
- Allowed now: user supplied deterministic special-rule behavior and requested next-step progression.

## Goal

Keep TASK_232 baseline and introduce deterministic staged defaults for special families in Step preview:

- `LLCR`, `IR`, `DWV`, `mating/un-mating`

## Rule Design

For selected group, derive step rows sorted by step number. Then apply per-family staged description defaults:

1. Find rows matching current family by `Test Item` keyword rule.
2. If count == 1:
   - description default = `<Family Name>`
3. If count > 1:
   - first = `Initial <Family Name>`
   - last = `Final <Family Name>`
   - middle = `After <previous numeric step Test Item>`
4. Previous numeric step = current step number minus 1 in selected-group step map.
5. If previous-step item empty/missing:
   - fallback = `<Family Name>`

Override precedence:

- If user has `stepOutputOverrides[key].description`, keep it.
- Rule only controls default when no description override exists.

## Matching Strategy (MVP deterministic, alias-ready)

- Add a single alias-map constant keyed by family, for example:
  - `LLCR`: `LLCR`, `CR`, `Low level contact resistance`
  - `IR`: `IR`, `Insulation Resistance`
  - `DWV`: `DWV`, `Dielectric Withstanding Voltage`
  - `MATING`: `mating`, `un-mating`, `mating/un-mating`
- Matching uses case-insensitive normalized contains/token checks via one helper path.
- Rule engine consumes family IDs, not raw strings.

No fuzzy NLP, no model inference.

## Architecture Alignment

- Current task keeps alias map in frontend feature scope to stay within approved UI-only boundary.
- Design keeps a clean seam for future migration:
  - future backend/application can expose authoritative synonym dictionaries
  - frontend can switch source without rewriting staged rule flow
- No API contract change in TASK_233.

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- add family alias map + matcher helpers
- add staged-description default resolver in preview derivation
- keep existing requirement default and edit/override plumbing unchanged

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_233 static checks for:
  - family matcher helper presence
  - staged labels (`Initial`, `Final`, `After`)
  - previous-step fallback behavior

3. `frontend/src/workbench.css`
- no planned functional style changes; only tiny text-fit tweak if needed

## Risks

- Keyword matching may include false positives (e.g., short token `IR`). Mitigate by combining token and known phrase checks.
- Multiple rows sharing the same step number are already allowed in grid; staged labels must remain deterministic by sorted order and stable row order.
- Alias list growth can drift if unmanaged; mitigate by central map and single matcher helper entry.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task233 or task232 or matrix_editor"
```

## Out Of Scope

- persistence/API save of generated descriptions
- cross-group global sequencing logic
- advanced domain-semantic phrasing beyond specified staged templates
