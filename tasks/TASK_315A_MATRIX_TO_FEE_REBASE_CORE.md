# TASK_315A_MATRIX_TO_FEE_REBASE_CORE

Status: Complete. Implemented after separate explicit user approval.

Executable plan: `docs/task_315a_matrix_to_fee_rebase_core_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Parent umbrella: `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`.

TASK_315A is the first executable slice of TASK_315. It only builds and verifies the pure backend Matrix-to-Fee rebase core. It must not wire the rebase into Matrix autosave, Matrix Cancel, Matrix Confirm, Fee Evaluation UI, API routes, or Project Folder readiness.

## Why This Task Is Allowed To Plan Now

`TASK_314A`, `TASK_314B`, and `TASK_314C` are complete. The next Matrix/Fee product gap is preserving Fee draft values when Matrix structure changes. Before touching persistence or UI workflow, the matching and transformation rules need a small, testable backend core.

This task was implemented after the user explicitly approved `TASK_315A`.

Completion summary: added a pure backend Matrix-to-Fee rebase core in `backend/application/matrix_fee_draft_rebase_service.py`. The service builds V1 rebase keys from group key/label, stable row lineage, step token, and 0-based step index; preserves edited Fee values onto target Matrix lineage; creates default rows for added Matrix rows; returns inactive removed rows for removed Matrix rows; and rebases report/sample preparation manual rows without matching by regenerated confirmed ids.

## Goal

Create a deterministic backend rebase core that transforms Fee Evaluation edited pricing values from a base Matrix context to a target Matrix draft context.

The rebase core must:

- preserve edited Fee row values for unchanged Matrix groups/steps;
- create default active Fee rows for added Matrix groups/steps;
- move removed Matrix rows into inactive removed-row metadata;
- preserve report-preparation manual rows globally;
- preserve sample-preparation manual rows by group key/label when the group remains;
- avoid matching by regenerated Confirmed Matrix ids;
- produce summary counts for preserved, added, and removed rows.

## Inputs

The TASK_315A service should operate on explicit value inputs or existing domain/value payloads. It must not load from repositories in this slice.

Inputs:

- base/source Fee edited values for the base Confirmed Matrix context;
- base/source Matrix row/group lineage metadata needed to build source rebase keys;
- target Matrix draft rows/groups and parsed step tokens;
- default Fee row values for target-only Matrix rows, supplied by the caller or a small adapter around existing default-row logic;
- fee manual rows from the source pricing draft.

## Outputs

The rebase core returns a value object containing:

- `active_rows`: target active Fee rows;
- `inactive_removed_rows`: source Fee rows no longer represented by the target Matrix;
- `manual_rows`: preserved or rebased manual rows;
- `summary`: preserved/added/removed counts and optional manual-row counts;
- diagnostic warnings for lineage-less fallback behavior where useful.

No database write, API response, or frontend payload is produced in TASK_315A.

## V1 Rebase Key

Do not match across Matrix revisions by confirmed UUIDs.

Use V1 key:

```text
group_key_or_label + stable_row_identity + step_token + step_index
```

Where:

- `group_key_or_label` prefers normalized group key, then normalized group label.
- `stable_row_identity` prefers `source_row_snapshot_id` when present, then persistent Matrix `draft_row_id`, then a normalized row signature fallback.
- `row_signature` fallback is normalized `test_item`, `source_section`, `method`, `condition`, and `requirement`.
- `step_token` is the numeric token display value.
- `step_index` is the existing 0-based parsed-token index within the Matrix cell, matching `MatrixBasicFillLine.step_index`.

Text-only Matrix edits to `test_item`, `method`, `condition`, or `requirement` must preserve Fee values when `source_row_snapshot_id` or `draft_row_id` is stable. Rows without stable lineage may become removed + added when their fallback row signature changes.

## In Scope

- Rebase key helper and normalization logic.
- Backend application service or pure helper module for the rebase transform.
- Value models for:
  - rebase source rows;
  - rebase target rows;
  - inactive removed rows;
  - rebase summary.
- Mapping logic for:
  - preserved active rows;
  - target-only default active rows;
  - source-only inactive removed rows;
  - report-preparation manual rows;
  - sample-preparation manual rows by normalized group key/label.
- Unit tests for the rebase core.

## Out Of Scope

- No pending rebase database table/repository.
- No Matrix autosave response extension.
- No Matrix Cancel cleanup wiring.
- No Matrix Confirm promotion.
- No confirm-time fallback.
- No FastAPI route changes.
- No Fee Evaluation UI changes.
- No pricing draft storage schema change beyond value-model planning.
- No Project Folder behavior change.
- No Confirm Fee behavior change.
- No Fee rule changes or new pricing-rule judgment.
- No Test Record, StepInstance, report generation, evidence/image, AI, permissions, LAN/server, or multi-user scope.

If implementation requires any out-of-scope production wiring, stop and split it into TASK_315B/C/D instead of expanding TASK_315A.

## Acceptance Criteria

- Matching target rows preserve source edited Fee values when V1 keys match.
- Text-only Matrix edits preserve Fee values when stable `source_row_snapshot_id` or `draft_row_id` exists.
- Lineage-less rows use row-signature fallback and may become removed + added when signature changes.
- Added Matrix groups create default active Fee rows.
- Added Matrix steps create default active Fee rows.
- Removed Matrix groups/steps become inactive removed rows and preserve previous edited values.
- Inactive removed rows are represented outside active rows.
- Rebase summary reports preserved, added, and removed counts.
- Inactive removed rows do not participate in Fee amount totals or active-row totals, but they do participate in the rebase summary `removed_count`.
- Report-preparation manual rows are preserved globally.
- Sample-preparation manual rows are preserved by normalized group key/label when the group remains.
- Sample-preparation manual rows for removed groups are not kept as active rows.
- No repository, API, frontend, Matrix autosave, Matrix Confirm, or Project Folder code is modified in TASK_315A.

## Required Validation

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

If existing Fee value models are touched:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_confirmed_fee_version_service.py -q
```

If static architecture guards are updated:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or matrix"
```

No frontend build is required for TASK_315A unless frontend files are changed, which should not happen in this slice.

## Stop Point

Validation: `py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q` (`11 passed`); `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_confirmed_fee_version_service.py -q` (`20 passed`).

Stop after TASK_315A completion. Do not proceed to TASK_315B, TASK_315C, TASK_315D, Matrix autosave integration, Matrix Confirm promotion, Fee UI, Project Folder, StepInstance, report, AI, permissions, LAN/server, or multi-user scope without separate explicit approval.
