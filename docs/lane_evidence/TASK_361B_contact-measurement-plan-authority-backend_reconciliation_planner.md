# TASK_361B Contact Measurement Plan Authority Backend Reconciliation

Date: 2026-07-12

Role: Planner

Status: implementation authorized; B5R helper scope reconciled; blocked pending
Developer B3R/B4R fixes

## Gate Chain Reconciled

1. TASK_361A completed and was accepted as the contract basis.
2. TASK_361B Planner lane creation completed.
3. Reviewer B1/B2 plan re-gate passed after the docs-only contract fix.
4. The user approved Developer planning-first.
5. Developer planning-first completed as docs-only.
6. Reviewer implementation-readiness passed with no implementation-design blocker.
7. The user approved source-of-truth reconciliation and Developer implementation,
   including the reviewed additive schema/migration/backend/API/test scope.

## Exact Authorized Scope

- Six additive non-destructive tables:
  `measurement_plan_roots`, `measurement_plan_revisions`,
  `measurement_plan_target_snapshots`, `measurement_plan_family_snapshots`,
  `measurement_plan_impacts`, and `measurement_plan_audits`.
- Fresh/existing SQLite migration, lazy active-confirmed-only idempotent bootstrap,
  provenance-based partial recovery, compatibility adapter, and non-destructive
  rollback.
- Stable `cmp-target:v1`, canonical non-null impact subject/identity keys, Group/Row
  source-lineage XOR manual-anchor constraints, canonical equality checks, and
  corruption blocking without guessed repair.
- `draft`, `needs_review`, `confirmed`, and `superseded` lifecycle, stale guards,
  immutable history, and audit records.
- Pure Matrix impact classifier and partial-compatible effective projection.
- Thin typed backend API and dependency wiring.
- Backend-only strict feature flag in `backend/shared/config.py`, explicit dependency
  injection, focused config coverage, and no operator-facing settings surface.
- Focused domain/migration/repository/bootstrap/lifecycle/classifier/projection/API
  tests using temporary SQLite and no real files.
- `backend/application/contact_measurement_plan_revision_fingerprint.py` only for
  deterministic editable-revision target/family optimistic-concurrency fingerprint.
- `backend/application/contact_measurement_plan_revision_snapshot_helpers.py` only
  for lifecycle-internal snapshot copy, canonical target replacement, and idempotent
  impact persistence.

The helper files are 46 and 193 lines and remain within the approved authority
module split. They do not expand TASK_361B into TASK_361C-E or any locked surface.

## Explicitly Not Authorized

- TASK_361C frontend client, dedicated setup workspace, or Matrix summary UI.
- TASK_361D draft workbook preview/generate/download or managed artifact lifecycle.
- TASK_361E Fee/specialized-workbook confirmed consumer migration.
- Settings UI/routes/local-config persistence, LTR/public configuration, legacy JSON
  deletion/rewrite, destructive migration, real workbook/folder mutation, generic
  Test Record, Matrix parser/import, Basic Information, StepInstance, Report,
  release/settings cleanup, `.agents/**`, or `docs/project_management/**`.
- External parser/test and TASK_360Q/R/S residuals.

## Stop Point

This Planner pass updates governance source-of-truth only. It does not implement,
route, commit, or push. B3R/B4R remain unresolved; QA/Integrator routing is blocked.

## Validation

- Task, plan, Planner/Developer/Reviewer evidence, and board were reconciled against
  the recorded Reviewer passes and user approval.
- Docs diff-check passed with existing LF/CRLF working-copy warnings only.
- Trailing-whitespace scan of reconciled governance documents returned no matches.
- Targeted status confirms this Planner pass changed governance documents only.
  Existing `mcr_text_normalizer` / `spec_section_text_extractor` product/test changes
  and TASK_360Q/R/S plan/task artifacts are external residuals and remain excluded.
- B5R path/line scan confirmed the two implemented helpers exist at the reconciled
  paths with 46 and 193 lines. Import/responsibility inspection found only TASK_361B
  identity and authority storage model/repository dependencies; no frontend, API
  client, Fee, workbook, parser, LTR, or TASK_361C-E dependency was introduced by
  these helper modules.
- Existing TASK_361B implementation files remain Developer-owned worktree changes;
  this Planner pass did not edit them or attempt B3R/B4R product fixes.

## Next Role

Developer fix pass for B3R/B4R, then Reviewer implementation re-gate.

Blocking summary: none.
