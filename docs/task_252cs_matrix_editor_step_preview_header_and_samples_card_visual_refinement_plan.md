# TASK_252CS Implementation Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `none`
- Why this plan is allowed now: user requested a bounded Matrix Editor Step preview UI refinement; plan prepared for review before implementation.

## 1) Task Goal

Refine Step preview visual hierarchy by emphasizing group identity (`Group N`) and removing redundant labels, while aligning Samples card background treatment with the panel style.

## 2) Input / Output

- Input: existing selected group preview state (`selectedGroup`, `selectedGroupPreviewRows`, `selectedGroupSamplesValue`, notes state).
- Output: updated header and card styles only.

No data model, API, or parser changes.

## 3) File-Level Change Plan

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
   - Replace current top plain group number text with `Group {index/name}` presentation.
   - Remove `Step preview` heading node.
   - Remove `Selected group` badge node.
   - Keep step count text and row rendering logic unchanged.

2. `frontend/src/workbench.css`
   - Add/adjust Step preview header typography class for enlarged `Group N`.
   - Remove/disable styles tied only to removed label/badge if no longer referenced.
   - Align Samples card background with same tone used in adjacent Step preview note/card area.

3. `tests/unit/test_frontend_shell_files.py`
   - Add/update static assertions for:
     - presence of `Group` prefix in Step preview header markup
     - absence of `Step preview` and `Selected group` label strings in Step preview block
     - expected Samples card class/style token presence

## 4) Risks & Mitigation

1. Group identifier source ambiguity (index vs display name).
   - Mitigation: reuse current displayed group identifier source and prepend `Group`.
2. Removing text labels may reduce context in edge states.
   - Mitigation: preserve step count and group prefix as primary context.
3. Background color changes could impact contrast.
   - Mitigation: stay within existing design tokens/tints already used in same panel.

## 5) Validation Plan

Automated:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task252"
```

```powershell
cd frontend
npm run build
```

Manual:

1. Open Matrix Editor and select a group with steps.
2. Verify top line shows `Group N` with larger text.
3. Verify `Step preview` and `Selected group` are gone.
4. Verify step count remains shown as `<n> steps`.
5. Verify Samples card background matches intended panel color style and readability remains good.

## 6) Out Of Scope

- Changing step ordering logic
- Changing sample merge/note logic
- Any backend reparse/import behavior
