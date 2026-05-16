# Controlled Future Extension Map

Last Updated: 2026-05-16
Status: current controlled roadmap boundary

This document separates approved next direction from still-deferred future scope.

Current authority order:

1. `AGENTS.md`
2. `docs/task_board.md`
3. active task file
4. current focused design documents

## Already Established Direction

Matrix-driven Laboratory Execution Phase is no longer generic future scope. It is the approved next product direction.

Approved principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Current runtime governance:

- `docs/runtime_governance_freeze_rule.md`
- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/step_centric_domain_foundation.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`
- `docs/runtime_projection_service_and_read_model_boundary.md`
- `docs/first_runtime_implementation_slice_planning.md`

## Current Implementation Direction After TASK_202

Prefer consumer-first runtime slices:

- read-only runtime projection adapter slice
- minimal runtime consumer prototype
- immutable runtime summaries
- fake/static runtime refresh prototypes
- runtime projection consumption validation

Avoid for now:

- runtime engines
- orchestration systems
- lifecycle persistence systems
- complex StepInstance graphs
- execution state machines
- projection ontology expansion

## Controlled Future Objects

These remain future scope unless explicitly approved by a task.

### StepInstance

Future execution data and lifecycle object.

Not yet allowed by default:

- persistence
- ORM model
- API route
- lifecycle state machine
- report/evidence ownership engine

### TestRecord

Currently a derived output workflow exists. A future source-of-truth execution record model requires separate approval.

### TestResult

Structured result data imported from instruments, Excel, or operator input. Not yet implemented as execution source of truth.

### TestAsset

Images, charts, raw files, and evidence bound to Project/Group/Step execution state. Current evidence placement is setup/output support, not Step-owned runtime storage.

### LabReport

Future report dataset and report generation system built from Project, Matrix authority, execution data, evidence, and derived output state.

Word remains an export format, not the master data source.

### ReportAudit / AI Review

Deterministic checks should precede AI review:

- requirement/result consistency
- pass/fail correctness
- table and figure numbering
- method/version consistency

AI remains deferred unless explicitly approved.

### KnowledgeBase

Future structured library for:

- standards
- product specifications
- historical reports
- method templates
- requirement rules

## UI Future Direction

Project Workbench should become Runtime Console by baseline replacement, not incremental beautification of the current setup-heavy shell.

Matrix Editor should be a separate Definition Studio for Matrix definition/import/editing, not embedded back into Workbench.

