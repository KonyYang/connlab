# Project Workbench Runtime Console Information Architecture

> Created: 2026-05-16  
> Task: `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE`  
> Scope: Information architecture only. No UI, API, schema, backend, or frontend implementation.

## 1. Runtime Console Purpose

Project Workbench should become a runtime command console for active laboratory projects.

The console must answer:

```text
What needs attention now, why does it matter, and where should the operator go next?
```

Matrix-driven does not mean Matrix-first UI. Matrix is the execution authority map and runtime projection surface. The runtime model also includes step lifecycle, execution integrity, issue attention, setup support, and derived-output sync.

## 2. Authority Relationship

Approved principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Relationship:

- `Project` owns lifecycle identity, intake, LTR, folder, source evidence, and overall traceability.
- `Matrix` owns what should be tested.
- `Step` owns what is happening in execution.
- `Test Record`, `Report`, `Fee Evaluation`, and `Approval Package` are derived outputs.

Example runtime projection:

```text
Project: active
Matrix authority: v3 current
Group 3: in progress
Step 2: failed, evidence present, report unsynced
Approval package: stale, does not block retest
```

## 3. Workbench Runtime Information Hierarchy

Runtime Console information should be ordered by operational attention, not by implementation modules.

1. Project runtime header:
   - project identity;
   - LTR;
   - lifecycle readiness;
   - current Matrix authority;
   - last runtime update.
2. Runtime attention summary:
   - highest-priority issue;
   - active steps;
   - failed steps;
   - blocked steps;
   - missing data;
   - missing evidence/images;
   - report unsynced sections;
   - setup items that block derived outputs but may not block testing.
3. Matrix runtime projection:
   - group and step map;
   - status projection;
   - issue markers;
   - selected step entry.
4. Step Workspace:
   - selected step state;
   - data/evidence/report sync context;
   - actions appropriate to execution, not definition editing.
5. Runtime attention priority:
   - what must be handled first;
   - what can wait;
   - what blocks testing;
   - what only affects derived outputs;
   - what belongs to setup completeness.
6. Setup Manager/status entries:
   - source materials;
   - folder;
   - approval package;
   - fee evaluation;
   - generated records;
   - supporting evidence placement.

The primary runtime question is not "what does the table look like?" It is "what needs attention in the running project?"

## 4. Runtime Attention Priority Model

Runtime attention priority defines how Workbench expresses what deserves attention first when many runtime states, missing items, failures, warnings, and setup gaps coexist.

This is not notification implementation, backend priority engine design, enum implementation, React badge implementation, or alert system implementation. It is an information architecture ordering model.

The Runtime Console should behave like:

```text
Runtime command console
```

not:

```text
status stacking page
```

### 4.1 Runtime Attention Concept

Runtime attention is the operator-facing answer to:

```text
What is the most important issue to handle now?
```

It should summarize the highest-impact runtime concern without forcing the operator to read the entire Matrix. Attention is derived from runtime meaning, not visual loudness.

A minor setup gap should not compete with a failed active step unless that setup gap blocks the next required runtime action.

### 4.2 Priority Hierarchy

Recommended IA hierarchy:

```text
P0 - blocks execution
P1 - risks execution integrity
P2 - risks report/output integrity
P3 - runtime warning
P4 - setup completeness
```

P0 - blocks execution:

- no current Matrix authority when testing needs to start;
- active step cannot proceed because required method, condition, requirement, or group identity is missing;
- required sample/group identity is unresolved;
- blocking test data conflict prevents pass/fail decision;
- required retest decision is pending after failure.

P1 - risks execution integrity:

- step is in progress with missing required data;
- failed step has no disposition, retest decision, or responsible owner;
- evidence exists but is not linked to the active step;
- result text conflicts with normalized status;
- sequence or group mapping issue threatens execution-state meaning.

P2 - risks report/output integrity:

- report section is stale after step data/evidence change;
- generated test record is stale after Matrix authority change;
- fee evaluation is stale or missing price assumptions;
- approval package is stale against current Matrix/output records;
- derived output exists but traces to an older Matrix version.

P3 - runtime warning:

- optional evidence is missing;
- low-confidence source trace exists but does not block execution;
- duration/cost estimate is incomplete;
- step has comments that need review;
- setup action is recommended soon but does not block the current runtime action.

P4 - setup completeness:

- project folder needs cleanup or confirmation;
- source material placement is incomplete;
- approval package has not been prepared;
- fee file has not been generated;
- external resource validation is stale but no current runtime action depends on it.

### 4.3 Attention Surfacing Order

Surfacing order:

1. Show the highest active priority at project level.
2. Group related issues by runtime object: project, Matrix authority, group, step, derived output, setup surface.
3. Prefer execution-blocking issues over setup completeness.
4. Prefer selected or active group issues over inactive group warnings when priorities are equal.
5. Prefer issues with a direct next action over passive informational warnings.

The console should be able to express:

```text
Step 2 in Group 3 failed and needs disposition before execution can continue.
```

instead of only showing disconnected statuses.

### 4.4 Runtime Issue Escalation Direction

Escalation routes:

- P0/P1 execution issues route to Step Workspace, or Matrix change request when definition is the root cause.
- P2 output-integrity issues route to derived output status surfaces, such as report sync, test record, fee, or approval package.
- P3 warnings stay visible in runtime context but should not interrupt the primary action.
- P4 setup completeness issues route to Setup Manager/status entries.

Escalation should answer:

```text
Where should the operator go next to resolve this?
```

### 4.5 Blocking Categories

Issues that block testing:

- missing current Matrix authority;
- unresolved step identity, group identity, or required sequence meaning;
- missing required method, condition, or requirement for a step that is ready to execute;
- failed step requiring disposition before dependent steps continue;
- conflicting result/status data that prevents execution decision.

Issues that do not block testing but affect derived outputs:

- stale report draft;
- stale generated test record;
- stale approval package;
- stale fee evaluation;
- missing report section;
- output generated from old Matrix version.

Issues that belong to setup completeness:

- folder not created when testing can still proceed;
- source material not placed in final folder;
- approval package not assembled;
- fee form not generated;
- external resource validation not current when not needed for the current step.

Issues that belong to execution integrity:

- missing step data;
- missing required evidence/image for a step decision;
- failed step without disposition;
- result/status conflict;
- evidence not linked to the step it supports;
- runtime state inconsistent with Matrix authority.

## 5. Runtime vs Setup Boundary

Runtime owns what is happening now:

- step status;
- step lifecycle;
- test data state;
- evidence/image readiness;
- failure state;
- retest or blocked state;
- report sync state;
- current execution risks.

Setup owns supporting preparation and generated-output paths:

- project folder existence;
- source material placement;
- application form Section 2 write-back;
- test-record form generation;
- fee-evaluation file generation;
- approval package preview/execute;
- external resource configuration.

Rule:

```text
Setup supports execution. Setup must not occupy the runtime center unless it blocks the next runtime action.
```

## 6. Matrix Overview Responsibility

Matrix Overview is a projection and navigation surface, not an editor.

It should:

- show current Matrix authority version;
- show groups and step tokens;
- project runtime status onto step tokens;
- support selection/navigation into Step Workspace;
- expose issue markers for missing data, evidence, failure, and report sync;
- preserve technical context needed for execution:
  - test item;
  - section;
  - method;
  - condition;
  - requirement.

It should not own:

- direct condition/requirement editing;
- step mapping changes;
- sequence changes;
- template import;
- Excel-like bulk editing;
- direct record/report/file writes.

Definition changes route to Matrix Editor or a Matrix change request flow.

## 7. Step Workspace Responsibility

Step Workspace is the execution workspace for one selected step.

It should eventually contain:

- step identity:
  - project;
  - Matrix version;
  - group;
  - sequence;
  - token variant;
  - test item.
- execution state:
  - not started;
  - in progress;
  - pass;
  - failed;
  - blocked;
  - waiting evidence;
  - report unsynced.
- required technical context:
  - method;
  - condition;
  - requirement;
  - step description.
- execution artifacts:
  - measurements/data;
  - images;
  - attachments/evidence;
  - comments;
  - actual completion time;
  - actual cost.
- derived-output relationships:
  - test record status;
  - report section sync;
  - fee impact.

This document defines responsibility only. It does not create data entry UI or backend persistence.

## 8. Runtime Status Model

Runtime status should be understood as layered conceptual state, not a single flat status list.

Identity readiness:

- no Matrix authority;
- Matrix candidate pending;
- Matrix authority current;
- Matrix authority stale or superseded.

Execution status:

- not started;
- ready;
- in progress;
- paused;
- blocked;
- pass;
- fail;
- retest required;
- waived or not applicable.

Evidence/data status:

- data missing;
- data present;
- evidence missing;
- evidence present;
- image missing;
- image present.

Derived output sync status:

- missing;
- current;
- stale;
- failed;
- manual;
- not applicable.

Project readiness projection:

- Draft;
- Test Ready;
- Authority Ready;
- Report Ready;
- Closed.

Project readiness is not the same as step execution status.

## 9. Step Token Interaction Model

Step token interaction is navigation into runtime state.

A token should:

- display sequence and variant;
- carry status projection;
- be selectable;
- open or focus Step Workspace;
- show compact markers for:
  - fail;
  - in progress;
  - missing data;
  - missing evidence;
  - report unsynced;
  - blocked.

Token interaction must not imply direct definition editing. Definition changes route to Matrix Editor or a Matrix change request flow.

## 10. Runtime Issue Surfacing Model

Issue groups:

- runtime attention priorities;
- execution blockers;
- failed steps;
- missing data;
- missing evidence/images;
- report sync gaps;
- setup blockers;
- source traceability warnings;
- Matrix authority warnings.

Surfacing hierarchy:

1. Highest-priority runtime attention summary.
2. Global runtime attention list ordered by priority.
3. Group-level issue projection.
4. Step token marker.
5. Step Workspace issue list.
6. Setup Manager status entry if the issue belongs to setup rather than execution.

Not every setup issue blocks testing.

## 11. Report Sync Visibility Model

Report sync is visibility, not report generation.

Report sync states should show:

- not started;
- section missing;
- data newer than report;
- evidence newer than report;
- synced/current;
- manual update required;
- sync failed.

Visibility relationships:

- Step updates can make report sections stale.
- Matrix authority changes can make report, record, fee, and approval outputs stale.
- Report is a derived output and must not become the primary data source.

This document does not implement report draft sync.

## 12. Project Lifecycle vs Matrix Execution

Relationship:

- Project lifecycle describes the whole project state.
- Matrix execution describes the test execution state inside the project.
- Step lifecycle describes the granular execution state.

`Test Ready` can precede `Authority Ready` or `Approval Package Ready`.

Setup completeness supports execution, but it is not automatically the same as execution readiness.

## 13. Runtime Navigation Flow

Runtime navigation should follow attention and responsibility:

1. Open Project Workbench.
2. Read runtime attention summary.
3. Review Matrix runtime projection.
4. Select group or step token needing attention.
5. Work in Step Workspace.
6. Resolve data/evidence/status/report sync issue or route to setup/definition surface.
7. Return to Matrix runtime projection and continue.

Branching rules:

- Definition issue: request Matrix change or open Matrix Editor.
- Setup issue: open Setup Manager/status entry.
- Execution issue: stay in Step Workspace.
- Output issue: open derived-output status surface.

## 14. Non-Implementation Boundary

This document intentionally does not define:

- database schema;
- status enums;
- API design;
- React components;
- CSS;
- badges;
- notifications;
- table virtualization;
- drawer behavior;
- StepInstance persistence.

Those require separate approved tasks.
