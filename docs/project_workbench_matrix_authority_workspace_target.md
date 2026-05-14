# Project Workbench Matrix Authority Workspace Target

> Created: 2026-05-14  
> Scope: Product and UX target for the Matrix-first Project Workbench after TASK_189 authority semantics are complete.

## 1. Purpose

This document records the target Workbench direction agreed after reviewing the current Project Workbench UI and the real laboratory Matrix workflow.

It is not an implementation task by itself. Future Workbench tasks must use this document as a constraint source when reshaping the Project Workbench around Matrix authority, group/step planning, downstream output status, and later test execution evidence.

## 2. Core Decision

A confirmed Project should have exactly one current Matrix authority.

Other Matrix versions are:

- draft candidates waiting for review/confirmation;
- superseded historical versions;
- source evidence files such as Word specifications or Excel Matrix files.

The Project Workbench must therefore be organized around the current confirmed Matrix authority, not around a toolbox of unrelated document actions.

## 3. Future Workbench Shape

The target first screen should answer:

- Which Matrix version is the confirmed authority?
- Is there an unconfirmed candidate draft?
- What groups, test items, and step sequences are included?
- Which steps have blockers or warnings?
- Which downstream outputs are current or stale against the confirmed authority?
- What is the next action for the project owner?

Target layout:

```text
Project header
  DL number | product | requestor | Matrix authority version | status

Matrix authority bar
  Confirmed Matrix vN | Candidate draft vN+1 if present | output freshness

Main work area
  Left or top: group navigation
  Center: Matrix overview table
  Right: selected group/step inspector

Downstream strip
  Section 2 | Test record | Fee evaluation | Approval package | future report
```

## 4. Matrix Overview Role

The Matrix overview must remain a first-class work surface because lab engineers understand the project fastest from a table like the source Matrix:

- rows show test items and technical context;
- columns show groups;
- cells show step sequences;
- sample size and duration/fee hints can appear in summary rows or compact footers.

The overview is for global understanding and navigation. It must not become a giant Excel replacement.

Rules:

- preserve a wide, readable Matrix overview;
- keep left technical columns visible where practical: `Test Items`, `Section`, `Test Method`, `Condition`, `Requirement`;
- show group columns with step tokens such as `1,8`, `3(a)`, `4(b)`;
- use click selection to drive detail editing;
- use small status marks for blockers/warnings instead of heavy color blocks;
- avoid per-cell complex controls.

## 5. Group And Step Inspector

Complex edits belong in a detail inspector, not inside every Matrix cell.

The inspector should support:

- selected group identity and sample size;
- selected step sequence, raw token, and suffix note;
- test item;
- method, condition, requirement;
- step description;
- duration value/unit;
- source trace;
- validation blocker/warning list;
- downstream linkage for the selected step when later tasks add records, results, and images.

Future result/image features should attach through this inspector or a step detail panel, not through the Matrix overview cells.

## 6. Downstream Output Placement

Downstream outputs should not occupy large permanent panels on the first screen.

They should be summarized as a compact status strip:

```text
Section 2: current
Test record: stale
Fee evaluation: missing
Approval package: stale
Report: not started
```

Clicking an output status can open the corresponding workflow panel. By default, the main visual weight belongs to Matrix authority and group/step planning.

## 7. Existing Workbench Areas To Demote

The following current areas should be demoted, collapsed, or moved behind stage actions:

- Project workbench boundary explanation;
- Project folder creation once folder state is recorded;
- read-only lookup summary;
- approval package form;
- evidence placement controls.

These features remain useful, but they should not compete with the Matrix authority work surface.

## 8. Required Additions

Future Workbench redesign should add:

- Matrix authority status bar;
- candidate draft indicator;
- version history access;
- validation summary;
- Matrix overview table;
- group/step inspector;
- duration summary;
- downstream output dependency strip;
- source trace panel;
- later extension points for step record results and image/evidence links.

## 9. UX Guardrails

- Matrix is the primary project planning view, but Project remains the system center.
- Do not expose multiple competing Matrix choices as equal options; the user should see one confirmed authority and at most one editable candidate.
- Do not hide the source evidence path; original Word/Excel/PDF files remain evidence.
- Do not make approval package, folder creation, or evidence placement the first visual priority after Matrix authority exists.
- Do not implement future report, AI, historical reuse, image management, or record import features as part of the first layout task.

## 10. Recommended Next Task

The next frontend task after TASK_189 corrections should be:

```text
TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE
```

Its purpose should be a layout and information-architecture refactor only:

- make Matrix the primary work surface;
- distinguish authority and candidate in the Workbench;
- convert downstream document actions into compact status/entry points;
- preserve existing API contracts and backend behavior;
- avoid adding new business features.
