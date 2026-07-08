# TASK_358A Matrix Editor Quantity Defaults Simplification

Status: complete/accepted by Integrator
Lane: `matrix-editor-quantity-defaults-simplification`
Owner Role: Developer / Reviewer / QA / Integrator
Created: 2026-07-09

## Purpose

Plan the corrective simplification after TASK_357A-E: remove Basic Information as the quantity default entry surface and make Matrix Editor the single quantity-default and per-Step confirmation surface.

## User Goal

The quantity workflow should be:

```text
Matrix Editor default values entry
  -> Matrix Editor per-Step confirmation / override
  -> Fee / Test Record / Report passive consumption
```

Basic Information should not keep a `Quantity defaults` card or entry point.

## Scope

TASK_358A is authorized for Developer implementation after Reviewer plan gate, Developer planning-first, Reviewer implementation-readiness, and explicit user approval. It defines implementation boundaries for:

- removing the Basic Information `Quantity defaults` UI card/entry;
- preventing Basic Information from being the operator-facing quantity default entry surface;
- preserving existing persisted Basic Information values for compatibility and migration safety;
- moving the default-entry affordance into Matrix Editor near the Step quantity setup workflow;
- keeping Matrix Step per-Step confirmation/override as final authority;
- ensuring Fee/Test Record/Report continue to consume confirmed Matrix Step quantities unchanged.

This Planner reconciliation pass does not implement product code.

## Corrected Quantity Authority Contract

- Matrix Editor owns quantity default entry and per-Step confirmation/override.
- Matrix Step confirmed quantities remain the authority for downstream consumers.
- Basic Information is no longer a quantity default authoring surface.
- Existing Basic Information persisted keys may remain readable for compatibility, but must not be shown as active BI fields or used as the primary default path after this corrective lane.
- Fee, Test Record, and Report remain passive consumers of confirmed Matrix Step quantities.

## What To Remove From Basic Information

- Remove the Basic Information UI group/card titled `Quantity defaults`.
- Remove or update Basic Information frontend tests that expect `Test points / sample`, `Readings / point`, and `Contact points / sample` in Basic Information.
- Stop presenting Basic Information validation messages for quantity defaults in the Basic Information UI.

## What To Preserve For Compatibility

- Do not delete database schema or persisted values.
- Do not break reading older Basic Information records that contain `test_points_per_sample`, `readings_per_point`, or `contact_points_per_sample`.
- Do not require a migration to erase historical quantity default values.
- Backend Basic Information may keep tolerant read/cleaning behavior if needed to avoid breaking older records, but no active UI should invite new Basic Information quantity-default authoring.

## Matrix Editor Default Entry Boundary

The Matrix Editor should provide a compact default-entry affordance near the Step quantity setup area or bottom Matrix controls.

Planned behavior:

- Operator can set default `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample` in Matrix Editor.
- Defaults can be applied/copy-filled into visible Step quantity rows.
- Each Step row remains editable and must be saved through the existing Matrix Step quantity save flow.
- Applying defaults must not silently overwrite saved/manual overrides without clear operator action.
- `total_readings` remains derived/read-only.
- Defaults are a convenience for Matrix Step setup; confirmed Matrix Step quantities remain final downstream authority.

## May Touch

Planning/source-of-truth now:

- `tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md`
- `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md`
- `docs/task_board.md`

Future implementation May Touch draft, pending Reviewer/User approval:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx` only if validation/error surfaces need cleanup after removing the field group
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if API DTOs need a minimal Matrix-default payload/helper
- `backend/application/matrix_step_quantity_service.py`
- `backend/api/routes_matrix_step_quantities.py`
- focused Matrix Step quantity backend/API tests
- focused Basic Information regression tests
- TASK_358A developer/reviewer/QA evidence and board updates through normal lane flow

## Must Not Touch

- Do not delete schema/data or run destructive migrations.
- Do not remove compatibility reading for existing Basic Information quantity values unless Reviewer/User explicitly approve a migration.
- Do not change Fee default-fill semantics except regression verification.
- Do not change Test Record/Report consumer semantics except regression verification.
- Do not mutate confirmed Matrix Step quantities outside the existing Matrix Step quantity save/confirm path.
- Do not implement StepInstance/execution persistence.
- Do not change Matrix parser/import rules.
- Do not change LTR workbook/public-drive/real workbook/folder behavior.
- Do not clean release/settings/template residuals.
- Do not touch `.agents/**` or `docs/project_management/**`.

## Locked Paths

- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- Test Record / Report implementation paths except focused regression tests if needed
- Matrix parser/import implementation paths
- Basic Information storage schema/migrations
- Matrix Step quantity storage schema/migrations
- LTR/public-drive implementation paths
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

## Dependencies

- Upstream: TASK_357A-E are complete/accepted.
- This is a post-acceptance corrective lane that supersedes the TASK_357B product placement of Basic Information quantity defaults.
- It must preserve TASK_357C/D/E downstream authority semantics.

## Validation Gate

Reviewer plan gate should verify:

- Basic Information no longer exposes `Quantity defaults` as an operator entry surface.
- Existing Basic Information stored quantity keys remain harmless and compatible.
- Matrix Editor has a clear default-entry affordance near Step setup or bottom controls.
- Per-Step Matrix Step quantity rows remain final confirmation/override.
- Fee/Test Record/Report passive consumers still consume confirmed Matrix Step quantities.
- no schema deletion, StepInstance, full Report generation, Matrix parser/import, LTR/public-drive, or release/settings scope is introduced.

## Merge Gate

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation pass completed.
- Reviewer implementation gate passed.
- QA gate passed.
- Integrator packaging/readiness accepted the controlled TASK_358A package.
- QA is required after Reviewer implementation gate because this lane changes Basic Information and Matrix Editor UI behavior.

## Evidence

- Plan: `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- Planner evidence: `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md`
- Developer evidence: `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- Reviewer evidence: `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reviewer.md`
- Reconciliation evidence: `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reconciliation_planner.md`
- QA evidence: `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_qa.md`

## Source-Of-Truth Reconciliation

Date: 2026-07-09

Planner reconciliation records the following authorization chain:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.

TASK_358A is complete/accepted after Developer implementation, Reviewer pass, QA pass, and Integrator packaging/readiness. Scope remains limited to the corrective implementation described above: remove Basic Information `Quantity defaults` UI entry/card/tests; preserve backend/data compatibility without schema/data deletion; add compact transient Matrix Editor defaults inside `MatrixStepQuantityPanel`; apply defaults blank-only with no silent overwrite; keep Fee/Test Record/Report passive-consumer behavior unchanged.

## Integrator Acceptance

Date: 2026-07-09

TASK_358A was accepted by Integrator after package isolation and merge-gate validation. The accepted package is limited to the approved Basic Information UI removal, Matrix Editor defaults strip, focused frontend tests, TASK_358A evidence/docs, and board closeout. Remote push was intentionally not performed.
