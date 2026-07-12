# TASK_361C Contact Measurement Setup Workspace Planner Evidence

Date: 2026-07-12

Role: Planner

Status: implementation authorized; pending Developer implementation.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A/B are complete/accepted, including
TASK_361B local commit `8cafc79e`. The contract reserves TASK_361C for typed client,
dedicated setup workspace, and compact Matrix summary. The number/name is not
formally occupied elsewhere.

## User Goal

Move Contact Measurement Plan editing and independent confirmation out of the long
Matrix card into a dedicated operational workspace. Keep a concise Matrix summary,
separate plan confirmation from Matrix confirmation, and defer draft workbooks and
confirmed-consumer migration to TASK_361D/E.

## Repository Findings

- Current UI combines status, editing, coverage, save, formal workbook actions, and
  errors in `MatrixContactMeasurementPlanCard.tsx`.
- TASK_361B typed commands exist, but frontend client helpers do not.
- Accepted workspace GET lacks the readable target/impact/Matrix context required by
  the confirmed UX; opaque key parsing in React would violate product/architecture
  rules.
- TASK_360B exposes only current-session generated artifact metadata, not persistent
  recent artifact history.
- Basic Information provides the established dedicated project workspace navigation
  pattern.

## Planner Decision

TASK_361C remains one planned lane with two guarded checkpoints: additive read-only
workspace DTO adequacy, then frontend route/workspace/summary. This is the smallest
coherent slice. The backend exception cannot change storage, classifier/lifecycle
semantics, or commands and must receive explicit Reviewer plan approval.

V1 edits and saves one selected target at a time, reloading the revision fingerprint
after each command. No bulk mutation API is introduced. TASK_360B formal workbook
controls remain a separate compatibility row with unchanged confirmed-Matrix source;
draft artifact behavior is TASK_361D and formal migration is TASK_361E.

## Design Context

Register: product. The plan follows ConnLab's calm, dense, traceable workbench
language and the supplied TASK_360 design audit: one compact summary, one clear setup
action, dedicated inline workspace, restrained state color, standard controls, no
modal-first flow, no nested cards, no oversized controls, and no obstructing footer.

## Scope / Locks / Validation

Exact May Touch, locked paths, UI acceptance, backend/API regressions, focused
frontend tests, browser smoke, package isolation, and merge gates are recorded in
the task and plan. External parser/test and TASK_360Q/R/S residuals remain excluded.
This Planner pass changes governance documents only.

Initial Planner validation passed: docs diff-check reported only existing LF/CRLF
working-copy warnings; trailing-whitespace scan was clean; TASK_361B was reconciled
to accepted commit `8cafc79e`. The later source-of-truth reconciliation updates only
TASK_361C governance status and evidence. Targeted status shows only pre-existing
external parser/test and TASK_360Q/R/S residuals under product/future-task paths;
no backend, frontend, API-client, or test implementation file was changed by either
Planner pass.

## Authorization Reconciliation

- Reviewer plan gate passed with `reviewer_pass`.
- The user approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness passed with `reviewer_pass`.
- The user approved source-of-truth reconciliation and Developer implementation.
- Authorization is limited to the task's exact read-only workspace DTO bridge,
  typed client/route, dedicated setup workspace, compact Matrix summary,
  stale-safe single-target command integration, independent plan confirmation,
  TASK_360B frontend compatibility row, accessibility/responsive work, and focused
  tests.
- Schema/repository/lifecycle/command semantics, Matrix confirmation, TASK_360B
  backend behavior, TASK_361D/E, Fee/workbook consumer migration, Settings/LTR/
  public drive, parser/real files, and external residuals remain locked.

## Definition Of Ready

Satisfied for Developer implementation within the exact Authorized May Touch.
Blocking questions: none. Next legal role: Developer implementation pass.

## Evidence Paths

- `tasks/TASK_361C_CONTACT_MEASUREMENT_SETUP_WORKSPACE.md`
- `docs/task_361c_contact_measurement_setup_workspace_plan.md`
- `docs/lane_evidence/TASK_361C_contact-measurement-setup-workspace_planner.md`
- `docs/lane_evidence/TASK_361C_contact-measurement-setup-workspace_reconciliation_planner.md`
- `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_qa.md`
- `C:/Users/White/Documents/Codex/2026-06-11/new-chat-2/product-design-audit-task360-contact-plan/audit.md`
