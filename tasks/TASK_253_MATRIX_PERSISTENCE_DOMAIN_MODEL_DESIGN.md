# TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN`.

## Why This Task Is Allowed Now

The Matrix Editor import and preview work has exposed the next architecture boundary: Matrix can no longer remain a UI-only draft/preview surface. The user explicitly approved entering the Matrix persistence design stage before implementation.

This task is design-only. It does not implement database tables, API routes, repositories, or frontend persistence wiring.

## Model Fit Assessment

`GPT-5.3-codex` with medium reasoning is suitable.

Reason:

- The task is an architecture/design document with bounded domain-model scope.
- It requires analyzing existing Matrix direction and persistence boundaries, not implementing a broad code change.
- It explicitly avoids database implementation and downstream consumers.

## Objective

Define the Matrix persistence domain model before implementation.

The design must clarify:

- Source Matrix
- Project Matrix Draft
- Confirmed Matrix
- Matrix Version
- Group Selection Projection
- Source Metadata
- Matrix Revision Flow

## Business Rules

1. A project can have only one active confirmed matrix at a time.
2. Imported full source matrix must be stored long term for traceability.
3. Project execution uses selected groups projection, not necessarily the full source matrix.
4. Unselected groups are hidden from execution views by default but remain traceable.
5. Matrix draft is editable; confirmed matrix is not directly editable.
6. Changes after confirmation require a new draft/revision and reconfirmation.
7. Sample Quantity / Sample Size is group-level data, not a normal test step row.
8. Source metadata must preserve source file name, source format, source spec number, source revision, parse time, parser version, warnings/blockers, and selected groups.
9. Matrix Library, historical reuse, fee/duration/equipment/report consumers are non-goals for this task, with fields/boundaries only reserved.

## Deliverable

Design document:

`docs/task_253_matrix_persistence_domain_model_design.md`

## Validation

Design review only:

- Confirmed no implementation files changed.
- Confirmed no database schema or API contract was introduced.
- Confirmed downstream consumers remain out of scope.
