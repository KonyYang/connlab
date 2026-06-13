# TASK_317A Project Folder Preparation UI Blueprint Plan

Status: Draft for user review. Implementation is not approved.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Task file: `tasks/TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT.md`

## Goal

Create a reviewed UI blueprint for the Workbench `Project Folder` flow before TASK_317-TASK_320 add more file and folder capabilities.

## Scope

Documentation only:

- define user-facing naming,
- define target Project Folder information architecture,
- map TASK_317-TASK_320 into that structure,
- define acceptance criteria for later implementation tasks,
- update task board / plan index status.

No implementation code is approved in TASK_317A.

## Required Context

Follow:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product UI guidance

Use the user's supplied decisions:

- `Package` should become `Project Folder` in user-facing UI.
- `Submitted Material` and `Source Book` remain English labels.
- Real operation order includes Application Form Section 2 update.
- Buttons should follow the process, with one broad generate action plus single-file actions where necessary.
- Status visibility can initially follow: local project folder, request material, Submitted Material, confirmed fee, Section 2, public-drive upload.
- `Package` is too broad and should exit the user-facing Workbench flow over time.
- TASK_317 must not add request-material controls to the old Package UI. It must start from a minimum `Project Folder` single-task frame.
- `Confirmed Fee authority` and generated `Fee form` are separate states.
- Public-drive upload is not an enabled user action before TASK_319.
- `TASK_312_PROJECT_PACKAGE_ORCHESTRATOR_PREVIEW` is historical context only and must not be used as the execution reference for TASK_317-TASK_321.

Historical boundary:

- TASK_312's old `Project package` preview UI, panel placement, expected-output grouping, and TASK_313 package-execute assumptions are superseded for this series.
- Any readiness checks that remain useful must be restated in the `Project Folder` row model defined here.
- Later task files and plans should reference TASK_317A directly, not TASK_312, when defining the Workbench flow for TASK_318-TASK_321.
- TASK_318 is the replacement for TASK_312's user-facing readiness/check role in the new `Project Folder` model, not an enhancement of the old package preview. It must not extend the old `/project-package/preview` surface as the main product path or show a duplicate package-readiness panel beside `Project Folder` readiness.

## Fixed Folder Vocabulary

Use this tree as the shared vocabulary for TASK_317-TASK_320:

```text
Project Folder (Workbench tab and preparation flow)
  Local DL folder = {Project default save location}\{DL_NUMBER}
    Source Book
      Original request email, original attachments, raw reference material
    Official project folder = {DL_NUMBER} {Sample Description} {Test Item}
      E-mail
      Submitted Material
      Photos
      Test results
        Final Examination
```

Rules:

- `Project Folder` is the Workbench flow, not a single disk folder.
- `Local DL folder` contains `Source Book` and the `Official project folder`.
- `Submitted Material` is a child folder of the `Official project folder`.
- UI copy must name the affected layer when an action is specific, for example `Open official project folder`.
- ConnLab management details such as `.connlab`, manifest, SQLite, or internal workspace records stay out of the operator UI.

## Proposed UI Blueprint

### Top-Level Workbench

```text
Project Workbench
DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing

Current stage:
  Project Folder preparation

Next action:
  Confirm Fee before updating Submitted Material.
  [Open Fee Evaluation]

Tabs:
  Project Folder | Execution
```

TASK_317 or an immediate prerequisite must introduce this minimum frame before adding request-material controls. TASK_320 should only finish remaining cleanup; it must not be the first task that removes the old user-facing Package structure.

### Project Folder Tab

```text
Project Folder
Prepare local project files before public-drive submission.

Preparation tasks:
  1. Local project folder
     Status: Created / Not created / Needs repair
     Action: Create local project folder / Open project folder

  2. Request material
     Status: Missing / Collected / Needs review
     Action: Collect request material

  3. Confirmed Fee authority
     Status: Missing / Confirmed / Stale
     Action: Open Fee Evaluation
     Note: business authority state, not a generated file

  4. Required forms
     Status: Missing files / Ready / Stale
     Action: Generate missing files, only after authorities exist
     Detail actions:
       Generate Fee form
       Generate Test Record
       Generate Customer Feedback form

  5. Application Form Section 2
     Status: Not updated / Preview ready / Written / Stale
     Action: Preview Section 2 update / Update Section 2
     Note: controlled application-form write-back, not normal file generation

  6. Submitted Material
     Status: Missing files / Ready / Needs refresh
     Action: Check Submitted Material

  7. Public drive upload
     Status: Hidden or read-only before TASK_319
     Action after TASK_319: Upload to public drive
```

### Execution Tab

Keep current intent:

```text
Execution
Matrix execution map + Step workspace.
```

Do not mix Project Folder preparation with execution evidence, StepInstance persistence, report generation, or image workflows until those tasks are explicitly approved.

## Task Sequence Impact

### TASK_317

First introduce or reuse the minimum `Project Folder` single-task frame:

- user-facing active tab is `Project Folder`,
- the top of the page shows one current task, one reason, and one primary action,
- no old Package page button pile is used as the request-material landing surface,
- `Execution` remains the only home for Matrix/Step work surfaces.

Then add request material collection into the `Request material` row:

- Source Book stores original request email and attachments.
- Official project folder receives controlled copies only where approved.
- No silent deletion from original user locations.

### TASK_318

Add local official project folder checks and repair into:

- `Local project folder`,
- `Submitted Material`,
- `Required forms`.

It should turn missing folders/files into repairable row states instead of adding another broad panel.

TASK_318 supersedes the user-facing readiness responsibilities of TASK_312 for the Project Folder flow. TASK_312 may remain as historical compatibility, but TASK_318 must not depend on TASK_313 package execution assumptions and must not reuse TASK_312's old `Project package` panel placement, labels, or expected-output grouping as the operator experience.

The overlapping readiness checks must be restated this way:

- project folder check -> `Local project folder` and `Official project folder` health,
- Matrix check -> Project Folder prerequisite / authority signal,
- fee check -> `Confirmed Fee authority`, separate from generated Fee form,
- Section 2 check -> `Application Form Section 2` controlled preview/write-back row,
- Customer Feedback check -> `Required forms` readiness item,
- Submitted Material check -> `Submitted Material` completeness/check/repair row,
- public-drive state -> hidden or read-only until TASK_319.

It must keep Confirmed Fee authority separate from generated Fee form readiness. Missing authority routes to Fee Evaluation; missing or stale Fee form routes to generation only after authority exists.

It must keep Application Form Section 2 as a controlled preview/write-back row rather than hiding it inside a generic required-forms action.

### TASK_319

Add public-drive upload/update into:

- `Public drive upload`.

It should expose conflict/update/skip statuses only in that row and keep overwrite rules conservative.

Before TASK_319, the upload row must be hidden or read-only. No enabled upload/update button should appear in TASK_317 or TASK_318.

### TASK_320

Finalize Workbench UI:

- Finish remaining user-facing `Package` cleanup if any internal labels survived TASK_317-TASK_319.
- Remove redundant summary panels.
- Keep one top next action.
- Keep `Project Folder | Execution`.
- Ensure all row actions are process-based.

## Implementation Plan For This Documentation Task

### Step 1: Create TASK_317A task file

File:

- `tasks/TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT.md`

Content must include:

- goal,
- user story,
- user-facing naming contract,
- fixed folder terminology tree,
- target operator flow,
- Project Folder task list,
- next action rules,
- TASK_317-TASK_320 landing map,
- plugin/mode guidance,
- scope and out-of-scope,
- acceptance criteria,
- Model Fit Assessment.

Expected result:

- The task file is reviewable without opening chat history.

### Step 2: Create executable plan document

File:

- `docs/task_317a_project_folder_preparation_ui_blueprint_plan.md`

Content must include:

- required context,
- fixed folder vocabulary,
- proposed UI blueprint,
- task sequence impact,
- validation commands,
- review checklist,
- approval gate.

Expected result:

- A later implementer can use this plan to keep TASK_317-TASK_320 from adding disconnected Workbench panels.

### Step 3: Update task board

File:

- `docs/task_board.md`

Required changes:

- The current top recommendation should point to TASK_317A review before TASK_317.
- Add a short TASK_317A bullet near the TASK_316/TASK_313B section.
- State clearly that TASK_317A is documentation/planning only and implementation is not approved.
- State that the TASK_317A review corrections were incorporated: front-loaded Project Folder frame, folder hierarchy, Fee authority separation, Section 2 row, and no public-drive action before TASK_319.

Expected result:

- The next execution step is unambiguous.

### Step 4: Update plan index

File:

- `docs/task_plan_index.md`

Required changes:

- Mark TASK_317A as the latest proposed plan.
- Keep TASK_316 as the latest completed implementation plan.

Expected result:

- Future agents can find the current plan without relying on conversation history.

### Step 5: Validate documentation-only change

Run:

```powershell
git diff --check
```

Expected:

- No whitespace errors.
- CRLF warnings are acceptable if they match existing repository behavior.

Optional static validation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task313a or task316"
```

Expected:

- Existing frontend shell checks still pass.

## Review Checklist

Before approving TASK_317A, confirm:

- `Project Folder` is the preferred user-facing replacement for `Package`.
- `Workspace` is not used as a user-facing label in the Project Folder flow.
- `Project Folder`, `Local DL folder`, `Official project folder`, `Source Book`, and `Submitted Material` are defined as a fixed hierarchy.
- TASK_317 starts with the minimum Project Folder single-task frame before adding request-material controls.
- Confirmed Fee authority is separated from Fee form generation.
- The real sequence includes Application Form Section 2 update.
- Section 2 is treated as controlled preview/write-back, not a generic generated file.
- Public-drive upload is hidden or read-only until TASK_319 approves it.
- TASK_317, TASK_318, TASK_319, and TASK_320 each have a clear landing row.
- No implementation code is included in TASK_317A.
- Plugin/mode guidance is clear enough that the user does not need to manually select plugins.

## Approval Gate

After this plan is reviewed, the next allowed action is one of:

1. Revise TASK_317A documents.
2. Approve TASK_317A and create/review `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION`.

Do not implement TASK_317 until its own task file and executable plan are reviewed and approved.
