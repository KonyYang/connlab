# TASK_308_CONFIRMED_FEE_VERSION_FOUNDATION

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_308 implementation is complete. TASK_309 requires a separate task file, executable plan, and explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The task is a bounded backend/application/storage foundation task that follows existing ConnLab patterns from Confirmed Matrix, Fee Evaluation pricing draft persistence, and output-record versioning. It requires careful authority-boundary design, but it does not require new UI design, Excel workbook editing, StepInstance execution persistence, public-drive package execution, AI review, permissions, or multi-user behavior.

## Goal

Create a backend foundation for a versioned Confirmed Fee authority record.

Confirmed Fee is the operator-approved pricing authority that future package tasks can trust when deciding whether a Fee Form is ready for official project-package placement.

TASK_308 must snapshot the current Fee Evaluation pricing state against the active Confirmed Matrix authority and active fee rule version. It is the data foundation only; the operator-facing `Confirm Fee` UI and stale warning presentation are TASK_309.

## Current Code Reality

- Fee Evaluation preview/edit UI exists and can save local pricing drafts through TASK_301.
- Fee Form direct download can export current edited values through TASK_300/TASK_305.
- Fee rule version identity is available through the active fee rule library.
- Active Confirmed Matrix identity and revision are already used by Fee Evaluation draft, export, and pricing-draft stale checks.
- No Confirmed Fee authority record exists yet.

## Inputs

The Confirmed Fee foundation should derive from existing structured sources:

- `project_id`
- active Confirmed Matrix authority:
  - `confirmed_matrix_id`
  - `confirmed_revision`
- active fee rule version id
- current Fee Evaluation pricing draft/edit state, including:
  - expected pricing draft edit id from the saved draft being confirmed
  - edited pricing rows
  - manual rows such as `Report preparation` and `Sample preparation`
  - condition confirmation time
  - external cost
  - external cost note
  - lab manpower hourly rate
  - row Notes
- current calculated totals needed for package readiness:
  - testing fee total
  - working hours
  - lab manpower cost
  - external cost
  - grand cost
- confirmer metadata:
  - confirmed by
  - optional comment/note if already supported by the selected command shape

## Outputs

- A versioned Confirmed Fee authority record persisted in SQLite.
- Repository/service read model for latest Confirmed Fee by project.
- Confirm command/service that creates a new Confirmed Fee revision from the current pricing draft state.
- Explicit binding fields:
  - project id
  - confirmed fee id
  - confirmed fee revision
  - confirmed Matrix id
  - confirmed Matrix revision
  - fee rule version id
  - pricing draft edit id
  - pricing effective date/value if already available from the existing fee context
- Snapshot payload that preserves enough edited pricing data for later package export/readiness checks.
- Tests proving the record is created, versioned, and bound to the correct Matrix/rule version.

## Authority Semantics

Confirmed Fee is an authority approval record for pricing readiness, not a generated workbook file.

- It must not write or overwrite Excel files.
- It must not register or replace `ProjectOutputRecord`.
- It must not move files into a project folder or public-drive package.
- It must not silently confirm or alter the active Matrix.
- It must not recompute pricing rules beyond reading the current structured pricing draft/totals needed for the snapshot.

Future tasks may use Confirmed Fee as a guard:

- TASK_309: UI confirmation and stale status.
- TASK_313: package preview/execute readiness.

## Stale Binding Requirement

The Confirmed Fee record must carry the binding values needed for future stale checks.

A Confirmed Fee version is current only when the current project state still matches:

- active Confirmed Matrix id
- active Confirmed Matrix revision
- active fee rule version id

If any of those values changes, later read models must be able to report the Confirmed Fee as stale. TASK_308 may expose this comparison in a backend read model if it is naturally small, but the operator-facing stale UI belongs to TASK_309.

## Scope

In scope:

- Backend domain/application/storage foundation for Confirmed Fee versions.
- SQLite repository/model support if needed.
- Thin API route only if it is needed to exercise the foundation and support TASK_309 without redesign.
- Tests for create/read/version/binding behavior.
- Documentation/task-board updates after implementation.

Out of scope:

- No frontend `Confirm Fee` button or status UI.
- No Fee Evaluation page layout or copy changes.
- No Excel workbook writing changes.
- No Fee Form generation changes.
- No ProjectOutputRecord changes.
- No package orchestrator.
- No public-drive placement.
- No Customer Feedback Form generation.
- No Section 2 sync.
- No StepInstance, execution persistence, report generation, AI review, permission, multi-user, or LAN/server authority migration.
- No automatic rule-update workflow.

## Implementation Preconditions

Before implementation, the agent must:

1. Read `AGENTS.md`.
2. Read `docs/task_board.md`.
3. Read this task file.
4. Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
5. Create `docs/task_308_confirmed_fee_version_foundation_plan.md`.
6. Wait for explicit user approval before writing implementation code.

## Acceptance Criteria

- Confirmed Fee version foundation exists with stable identifiers and revisioning.
- Creating a Confirmed Fee snapshot from a project with active Confirmed Matrix and current fee pricing draft succeeds.
- Creating a Confirmed Fee snapshot must bind to the expected saved pricing draft edit id; if the latest saved draft does not match the expected id, confirmation fails with an actionable conflict.
- Creating a new Confirmed Fee after a prior confirmation increments revision or otherwise creates an ordered version history consistent with local repository patterns.
- The snapshot stores/returns the binding tuple: confirmed Matrix id, confirmed Matrix revision, fee rule version id.
- The snapshot stores/returns the pricing draft edit id that was confirmed.
- The snapshot stores/returns current totals required for later readiness checks.
- The snapshot preserves edited pricing values and notes needed for later Fee Form/package use.
- Missing active Confirmed Matrix returns an actionable error.
- Missing or stale current fee pricing draft returns an actionable error or review-required status, as selected in the executable plan.
- No Excel file is generated as a side effect.
- No ProjectOutputRecord is registered as a side effect.
- No frontend UI changes are introduced.
- Existing Fee Evaluation draft/export tests remain passing.

## Required Validation

The executable plan must define the exact test commands, but expected coverage includes:

- Unit tests for Confirmed Fee service.
- Repository tests for create/read/version behavior.
- API tests if a route is added.
- Regression tests for existing Fee Evaluation pricing draft/export behavior.
- `git diff --check`.

## Stop Point

After TASK_308 implementation and validation, stop. Do not proceed to TASK_309 without a separate task file / executable plan review and explicit approval.
