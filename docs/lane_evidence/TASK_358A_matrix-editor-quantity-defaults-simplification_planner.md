# TASK_358A Planner Evidence - Matrix Editor Quantity Defaults Simplification

Date: 2026-07-09
Role: Planner
Task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION`
Lane: `matrix-editor-quantity-defaults-simplification`
Status: `planned_ready_for_reviewer_plan_gate`

## Current Phase / Active Task / Why Allowed

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES` is complete/accepted.

Why allowed: User/Orchestrator requested a post-acceptance corrective simplification for the quantity authority workflow after TASK_357A-E. Planner is allowed to run Discovery Gate and create planned lane source-of-truth. Developer implementation is not authorized.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_357B Basic Information quantity defaults QA evidence
- TASK_357C Matrix Step quantity setup QA evidence
- TASK_357D / TASK_357E accepted board/evidence context
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `backend/application/project_basic_information_service.py`
- `backend/application/matrix_step_quantity_service.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts`
- focused Basic Information / Matrix Step quantity tests by targeted search
- current `git status --short`

## Confirmed By User

- Remove the Basic Information `Quantity defaults` feature card/entry.
- Basic Information should no longer be the quantity-default input surface.
- Add the default value entry to Matrix Editor near the bottom or Step setup area.
- Matrix Editor per-Step setup remains final confirmation/override.
- Fee/Test Record/Report remain passive consumers of confirmed Matrix Step quantities.
- Do not break existing persisted data or downstream consumers.
- Do not touch LTR/public-drive, Matrix parser, StepInstance, full Report generation, release/settings, `.agents/**`, or `docs/project_management/**`.

## Confirmed By Repository Evidence

- TASK_357B implemented Basic Information `Quantity defaults` in frontend config and tests.
- `ProjectBasicInformationService` validates optional non-negative quantity defaults.
- TASK_357C implemented Matrix Step quantity setup and imports Basic Information defaults.
- Matrix Editor has `MatrixStepQuantityPanel`, `matrixStepQuantitySelectors`, and API client helpers for load/save.
- TASK_357D/E consumers are based on confirmed Matrix Step quantities and do not treat Basic Information or Fee as downstream authority.
- Current worktree has external backend/frontend/tests/release/settings residuals that must remain excluded.

## Inferred By Planner

- This should be a corrective lane, not a rollback of TASK_357C/D/E.
- Schema/data deletion is unnecessary and risky.
- Existing Basic Information quantity values should remain readable for historical compatibility but not exposed as active BI fields.
- Matrix Editor defaults should be an operator convenience for filling Step rows, not a second persisted authority.
- Applying defaults should fill blank/manual-required rows by default and avoid silent overwrite of manual overrides.

## Not Yet Confirmed

No blocker for planned lane creation.

Implementation-level decisions left for Developer planning-first:

1. Exact UI placement: bottom action area versus inside/above `MatrixStepQuantityPanel`.
2. Apply/copy semantics: blank-only default fill versus explicit overwrite action.
3. Whether Matrix Editor defaults are transient UI state or require a scoped draft-level helper. Default recommendation is no schema unless proven necessary and re-gated.

## Created Files

- `tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md`
- `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md`

## Updated Files

- `docs/task_board.md`

## Scope Decision

TASK_358A is planned only.

Implementation is not authorized.

Recommended correction:

- remove Basic Information quantity-default UI;
- preserve existing Basic Information data compatibility;
- add Matrix Editor default-entry affordance around Step quantity setup;
- keep per-Step saved quantities as final authority;
- keep Fee/Test Record/Report passive-consumer semantics unchanged.

## Validation Summary

- `git diff --check -- docs/task_board.md tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md` passed with the existing `docs/task_board.md` LF/CRLF warning only.
- Trailing whitespace scan for touched TASK_358A docs/board returned no matches.
- Targeted status confirms this Planner pass changed `docs/task_board.md` and created TASK_358A task/plan/evidence only.
- External residuals remain excluded from TASK_358A: `backend/api/dependencies.py`, `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`, `tests/unit/test_confirmed_matrix_fee_draft_service.py`, `tests/unit/test_fee_rule_matcher.py`, Settings/LTR/template resource files, desktop/release files, New Project test residuals, and release/template resource tests.
- No product implementation file was modified by this Planner pass.

## Stop Point

Stop after planned lane creation.

Recommended callback target: ConnLab Orchestrator.

Recommended next role: Reviewer plan gate.
