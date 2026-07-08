# TASK_357B Basic Information Quantity Defaults

Status: complete/accepted by Integrator
Lane: `basic-information-quantity-defaults`
Owner Role: Planner / Reviewer
Created: 2026-07-08

## Purpose

Plan the Basic Information layer for project-level default test quantity fields that can later be imported into Matrix Step setup.

This lane follows `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`.

## User Goal

Basic Information should provide project-level defaults for test points, readings, and contact-point quantities. These defaults are convenience inputs only. Matrix Step setup remains the final confirmation and override authority.

## Scope

TASK_357B is a planned lane only. It defines implementation boundaries for:

- Basic Information draft and confirmed default quantity fields;
- API/read-model shape for those defaults;
- UI placement and concise labels;
- source metadata for later Matrix Step import;
- downstream handoff to TASK_357C.

It does not implement product code in this Planner pass.

## V1 Fields

Contract fields from TASK_357A:

- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`
- `total_readings`

TASK_357B should decide whether `total_readings` is stored as an explicit Basic Information default or only derived later. Planner recommendation: Basic Information may expose the first three as defaults and treat `total_readings` as derived/read-only unless Reviewer/User later approves direct entry.

## Authority Boundary

- Basic Information draft values may be used as defaults for Matrix Step setup.
- Confirmed Basic Information values are stronger defaults when available.
- Neither draft nor confirmed Basic Information is final downstream authority.
- Matrix Step setup is the final authority after import/override.
- Basic Information changes must not silently rewrite already confirmed Matrix Step quantities.

## May Touch

Planning/source-of-truth now:

- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_planner.md`
- `docs/task_board.md`

Future implementation May Touch draft, pending Reviewer/User approval:

- `backend/application/project_basic_information_service.py`
- Basic Information repository/model/API DTO files if required by the implementation plan.
- `backend/api/routes_project_basic_information.py`
- `backend/api/dependencies.py` only if service wiring changes are needed.
- `frontend/src/features/project-basic-information/**`
- `frontend/src/api/client.ts` only for typed Basic Information DTO changes.
- focused Basic Information backend/frontend tests.

## Must Not Touch

- Matrix Step setup implementation.
- Matrix draft/confirmed authority implementation.
- Fee Evaluation consumption/default-fill implementation.
- Test Record / Report reuse implementation.
- Matrix parser/import.
- LTR workbook/public-drive authority rules.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user.
- release/settings/template residual cleanup.
- unrelated dirty files.

## Locked Paths

- `frontend/src/features/matrix-editor/**`
- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/project_matrix_*`
- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
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

- Upstream: `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` accepted as contract/downstream basis.
- Downstream:
  - `TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI` imports Basic Information defaults and defines final Matrix Step authority.
  - `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION` waits for TASK_357C confirmed Matrix quantity authority.
  - `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT` remains later planning/future scope.

## Validation Gate

Reviewer plan gate should verify:

- Basic Information remains a default source, not final downstream authority.
- Draft and confirmed default policies match TASK_357A.
- UI/API/persistence boundaries are clear enough for Developer planning-first.
- Matrix Step, Fee, Test Record, Report, and future scope remain locked.
- Validation includes backend Basic Information tests, frontend UI/model tests, no silent Matrix/Fee mutation, build, diff/trailing scans, and forbidden-scope scans.

## Merge Gate

- Reviewer plan gate pass before Developer planning-first.
- User approval required before Developer planning-first.
- No Developer implementation until readiness/source-of-truth reconciliation and user approval.

## Source-Of-Truth Reconciliation

Date: 2026-07-08

TASK_357B was implementation authorized after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed docs-only.
- Reviewer implementation-readiness gate passed.
- User approved source-of-truth reconciliation and Developer implementation.

Implementation remains limited to Basic Information quantity defaults:

- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`
- `total_readings` derived/read-only or omitted per plan

Locked scope remains: no Matrix Step override, no Fee consumption, no Test Record/Report reuse, no LTR workbook/public-drive changes, no Matrix parser/import, no schema migration unless implementation proves necessity and re-gates it, no unrelated residual cleanup, no `.agents/**`, no `docs/project_management/**`, no remote push.

Integrator packaging/readiness accepted TASK_357B after Reviewer implementation pass, QA pass, package isolation, and validation. Remote push was not authorized and was not performed.
