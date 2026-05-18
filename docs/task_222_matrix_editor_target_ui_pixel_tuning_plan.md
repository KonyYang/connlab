# TASK_222 Plan - Matrix Editor Target UI Pixel Tuning Pass

## 1. Task Goal

Perform pixel-level UI tuning for Matrix Editor after `TASK_221` structural convergence.

Primary outcome:

- closer visual match to `Matrix Edit Page.png`
- no architecture or behavior change

## 2. Inputs / Outputs

Inputs:

- current `ProjectMatrixEditorPage.tsx` from `TASK_221`
- current `workbench.css` Matrix Editor target selectors
- target image baseline

Outputs:

- refined Matrix Editor spacing, density, and typography
- optional static assertion updates for `TASK_222`
- task board/task status updates after completion

## 3. Constraints

Must keep:

- Definition Studio orientation
- `left library + center matrix + right step workspace + bottom support` structure
- disabled placeholder action policy

Must avoid:

- new interactions
- data model changes
- backend/API/domain updates

## 4. Pixel Tuning Checklist

### 4.1 Header

- tighten vertical rhythm in title/meta bands
- balance metric weight against title block
- normalize button heights and horizontal spacing
- align top row baselines

### 4.2 Action Bar

- make control row denser and more uniform
- reduce uneven wrapping at medium widths
- align search width and button cluster proportions

### 4.3 Left Test Library

- tighten list row height and section gaps
- harmonize header/search/input sizing with target
- improve category count column alignment

### 4.4 Matrix Grid

- tune table font sizes and header row heights
- tune fixed/important column widths
- improve token cell paddings for denser visual rhythm
- preserve dominant center width

### 4.5 Right Step Workspace

- tighten workspace card section spacing
- balance tabs, step table row height, and meta blocks
- tune note box and apply button placement

### 4.6 Bottom Supporting Panels

- balance template/reference panel heights and spacing
- reduce card padding variance
- align table/text rhythm in reference panel

## 5. File-Level Implementation Plan

### 5.1 `frontend/src/workbench.css`

Main tuning surface.

Expected edits:

- `matrix-editor-target-*`
- `matrix-editor-actionbar*`
- `matrix-editor-studio*`
- `matrix-editor-main-table*`
- `matrix-editor-step-workspace*`
- `matrix-editor-supporting*`

### 5.2 `frontend/src/pages/ProjectMatrixEditorPage.tsx`

Only minor JSX adjustments if needed for alignment hooks:

- class grouping refinements
- small text-label alignment changes

No behavior logic changes.

### 5.3 `tests/unit/test_frontend_shell_files.py`

Add/update `TASK_222` static assertions only if needed:

- assert presence of tuned structural selectors
- keep non-regression checks for Definition Studio focus

## 6. Risks And Controls

Risk:

- accidental redesign while tuning

Control:

- preserve existing section order and role boundaries
- make only density/spacing/typography changes

Risk:

- style spillover into runtime console

Control:

- scope edits to `matrix-editor-*` selectors only

## 7. Validation Plan

Required:

```powershell
cd frontend
npm run build
```

Targeted tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task222 or task221 or task220 or task219"
```

Recommended governance tests after board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 8. Manual Smoke Checklist

1. Open Matrix Editor from Workbench.
2. Compare header and action bar density against target image.
3. Verify left Test Library compactness and readability.
4. Verify Matrix Grid remains central and dominant.
5. Verify right Group/Step workspace remains contextual.
6. Verify bottom Templates/Reference panels are balanced.
7. Verify no new interactions are active.

## 9. Stop Point

This document is the plan deliverable for `TASK_222`.

Implementation code changes should start only after explicit user approval.
