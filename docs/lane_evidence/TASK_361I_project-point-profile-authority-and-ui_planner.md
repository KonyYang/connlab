# TASK_361I Project Point Profile Authority And UI Planner Evidence

Date: 2026-07-14

Role: Planner

Status: implementation authorized / pending Developer implementation.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361H is complete/accepted at local commit
`9e4c9e45`, and no implementation lane is active. The user approved Discovery and a
planned-only first phase for project-wide Point Profile entry and confirmed summary.

## User Goal

Make Contact measurement setup profile-first. An operator can define arbitrary
project categories and counts even with no eligible Matrix targets, see the included
total, save and confirm profile revisions independently of Matrix, and see only the
confirmed profile in Matrix summary. Coverage, consumers, and workbooks stay out.

## Repository Evidence

- Existing family snapshots require `MeasurementPlanTargetSnapshotModel` ownership.
- Existing Measurement Plan draft opening requires an active confirmed Matrix.
- Current setup UI is target-first and exposes open-plan, impact, target, and draft
  workbook controls.
- Current Matrix summary exposes coverage, LLCR/CR readings, Matrix revision, and
  specialized workbook controls.
- TASK_361H already supplies freeform target categories but intentionally made no
  schema or project-level profile authority.

## Planner Decision

Create planned lane `project-point-profile-authority-and-ui`. Use three additive,
non-destructive profile tables with independent draft/confirmed/superseded revision
lifecycle, backend-owned monotonic `ppc-N` categories, TASK_361H-compatible
normalization, optimistic fingerprints, and project-only APIs. Rework setup and Matrix
summary around confirmed profile authority while leaving target/workbook/consumer
implementations unchanged.

## Scope And Safety

- Exact backend/frontend May Touch paths are in the task.
- Existing six-table Measurement Plan schema, target lifecycle, consumers, Fee,
  workbook generation, parser, LTR/public drive, real DB/files, and external residuals
  remain locked.
- Legacy target families are not rewritten or promoted. Optional uniform legacy data
  is suggestion-only and requires explicit operator import.
- No product code, schema, tests, migration, staging, commit, or push occurred in this
  Planner pass.

## Definition Of Ready

Satisfied for Reviewer plan gate. User workflow, data ownership, additive schema,
transaction order, DTOs, UX, compatibility, identity/normalization, stale handling,
May Touch, locks, validation, and merge gates are explicit. Blocking questions: none.

## Authorization Reconciliation

- Reviewer plan gate passed.
- The user approved Developer planning-first.
- Developer completed a docs-only planning-first pass.
- Reviewer implementation-readiness passed with no blocker.
- The user explicitly approved TASK_361I source-of-truth reconciliation and product
  implementation.
- Implementation authorization is limited to the three additive/non-destructive
  Point Profile authority tables and fail-closed migration; draft/confirmed/
  superseded lifecycle; backend `ppc-N` identity, normalization, fingerprint, stale,
  and atomic save/confirm; read-only legacy suggestion; typed profile API/DTO;
  profile-first setup UI; confirmed-only Matrix summary; direct-route style ownership;
  and focused temporary tests/browser smoke.
- Matrix Step Test Type/Sample Type, Group/Step coverage and overrides, Fee,
  TASK_360B/TASK_361D workbook behavior, Generic Test Record/Report, XLSM/VBA/COM,
  parser/import, LTR/public drive, real databases/files, and external residuals remain
  locked.

## Evidence Paths

- `tasks/TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI.md`
- `docs/task_361i_project_point_profile_authority_and_ui_plan.md`
- `docs/lane_evidence/TASK_361I_project-point-profile-authority-and-ui_planner.md`
- `docs/lane_evidence/TASK_361I_project-point-profile-authority-and-ui_reconciliation_planner.md`
- `docs/task_board.md`

## Next Legal Role

Developer implementation pass.
