# TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT

Status: Proposed for review. Implementation is not approved.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: none. This task is a planning prerequisite before `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION`.

Executable plan:

- `docs/task_317a_project_folder_preparation_ui_blueprint_plan.md`

## Goal

Define the Project Workbench `Project Folder` information architecture before adding TASK_317-TASK_320 capabilities, so future features land in a single operator flow instead of becoming another stack of status cards and disconnected buttons.

## User Story

As a lab operator, I want the Workbench to show the one local project-folder preparation flow, so I can create the local project folder, collect request materials, generate required files, update Section 2, check Submitted Material, and later upload to the public drive without understanding ConnLab internal workspace/package concepts.

## Why This Task Exists

The current Package page is still confusing because it mixes:

- readiness checklist,
- package preview,
- secondary links,
- folder state,
- fee state,
- Section 2 state,
- future execution concepts.

TASK_317, TASK_318, TASK_319, and TASK_320 will add more file and folder capabilities. If the UI structure is not defined first, those tasks can easily add more panels and buttons to the current page. TASK_317A prevents that by defining the target UI contract first.

## TASK_317 Front-Loaded UI Rule

`TASK_317` must start from the minimum `Project Folder` single-task frame before adding request-material collection. Do not wait until `TASK_320` to remove the active user-facing `Package` surface, redundant overview/summary surface, or disconnected button stack.

Minimum frame required before TASK_317 request-material UI lands:

- user-facing tab label is `Project Folder`;
- top area shows one current task, one reason, and one primary action;
- request-material controls appear only inside the `Project Folder` task list/action area;
- execution-only Matrix/Step surfaces remain in `Execution`;
- old `Package` wording may remain only in internal code/API names until a later safe implementation task.

`TASK_320` is reserved for final polish and cleanup, not the first UI contraction.

## Historical TASK_312 Boundary

`TASK_312_PROJECT_PACKAGE_ORCHESTRATOR_PREVIEW` is a completed historical read-only package-preview slice. It must not be used as the execution reference for `TASK_317` through `TASK_321`.

For this series, use this task (`TASK_317A`) as the information-architecture and Workbench UI authority. If a later task needs readiness checks similar to old TASK_312 behavior, it must restate them in the new `Project Folder` vocabulary and row model instead of reusing the old `Project package` preview structure, labels, placement, or `TASK_313` package-execute assumptions.

`TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR` must be treated as the replacement for TASK_312's user-facing readiness role inside the new `Project Folder` flow, not as an enhancement of TASK_312. TASK_312 may remain in code or documentation as historical compatibility, but TASK_318 must not extend the old `/project-package/preview` surface, show a second package-readiness panel, or depend on TASK_313 package-execute assumptions.

## User-Facing Naming Contract

Use these names in user-facing UI:

- `Project Folder`
- `Local project folder`
- `Local DL folder`
- `Official project folder`
- `Source Book`
- `Submitted Material`
- `Request material`
- `Required forms`
- `Public drive upload`

Avoid these names in user-facing UI for this flow:

- `Package`
- `Project package`
- `Workspace`
- `Orchestrator`
- `.connlab`
- `manifest`
- `SQLite`
- API route names

`Package` may remain internally in existing code and API names until a later implementation task safely renames or hides it in the UI. TASK_317A only defines the UI direction.

## Folder Terminology Tree

Use this hierarchy consistently in task files, UI copy, API DTO review, and tests:

```text
Project Folder (Workbench tab and preparation flow)
  Local DL folder = {Project default save location}\{DL_NUMBER}
    Source Book
      Original request email, original attachments, raw reference material
    Official project folder = {DL_NUMBER} {Sample Description} {Test Item}
      E-mail
      Submitted Material
        Controlled copies of request attachments and generated Test Record files
      Photos
      Test results
        Final Examination
```

Important naming rule:

- `Project Folder` is the operator-facing Workbench flow, not a single disk folder.
- `Local DL folder` is the parent folder ConnLab prepares locally for one DL number.
- `Official project folder` is the folder that can later be submitted or uploaded.
- Buttons and status text must say which layer they affect. For example, `Create local project folder` may create the Local DL folder plus the Official project folder and Source Book, while `Open official project folder` opens only the controlled deliverable folder.
- `Submitted Material` is always a child of the Official project folder.
- `.connlab`, SQLite, manifest, or other ConnLab management files are not operator-facing concepts.

## Target Operator Flow

The main Project Folder flow should follow this business order:

1. Confirm DL number.
2. Confirm Matrix authority.
3. Create local project folder.
4. Collect request email and attachments into Source Book and controlled project folders.
5. Confirm Fee authority in Fee Evaluation.
6. Generate or refresh derived required files:
   - Customer Feedback form,
   - Fee form from the Confirmed Fee authority,
   - Test Record,
   - other required forms approved by later tasks.
7. Preview and write back Application Form Section 2 from confirmed project data.
8. Check Submitted Material completeness.
9. Upload or update the public-drive project folder after TASK_319 approves that capability.

## Target Workbench Structure

For a project with DL number and active Confirmed Matrix, the Workbench should present:

```text
Header:
  DL number + Sample Description + Test Item

Next Action:
  One blocking action, one reason, one primary CTA

Tabs:
  Project Folder | Execution

Project Folder:
  A. Preparation task list
  B. Current action panel
  C. Project folder outputs and checks

Execution:
  Matrix execution map + Step workspace
```

The `Project Folder` tab replaces the user-facing meaning of the old `Package` tab.

## Project Folder Task List

The Project Folder tab should show a compact task list, not a wall of cards.

Recommended rows:

1. `Local project folder`
   - Created / Not created / Needs repair.
   - Shows the Local DL folder path and the Official project folder path in details.
   - Primary action: `Create local project folder` when missing.

2. `Request material`
   - Request email imported / Missing.
   - Attachments collected / Needs review.
   - Primary action after TASK_317: `Collect request material`.

3. `Confirmed Fee authority`
   - Missing / Confirmed / Stale against active Matrix.
   - This is a business authority state, not a file-output state.
   - Primary action: `Open Fee Evaluation` until a Confirmed Fee authority exists.

4. `Required forms`
   - Customer Feedback form.
   - Fee form generated from Confirmed Fee authority.
   - Test Record.
   - Other approved derived files.
   - Primary action: `Generate missing files` only after required authorities exist.
   - Single-file actions may be available inside the row details.
   - Must not include Fee confirmation or Section 2 write-back as part of a broad generation action.

5. `Application Form Section 2`
   - Not updated / Preview ready / Written / Stale.
   - This is a controlled application-form write-back, not a normal generated file.
   - Primary action: `Preview Section 2 update` or `Update Section 2` when approved by the relevant implementation task.

6. `Submitted Material`
   - Ready / Missing files / Needs refresh.
   - Primary action after TASK_318: `Check Submitted Material`.

7. `Public drive upload`
   - Not configured / Ready to upload / Uploaded / Conflict.
   - Primary action after TASK_319: `Upload to public drive`.
   - Before TASK_319, this row must be hidden or read-only with no clickable upload/update button.

## Next Action Rules

Show only one primary action at the top. Suggested priority:

1. Missing DL number: `Register DL`.
2. Missing active Matrix authority: `Open Matrix`.
3. Missing local project folder: `Create local project folder`.
4. Missing request material: `Collect request material`.
5. Missing Confirmed Fee authority: `Open Fee Evaluation`.
6. Confirmed Fee exists but Fee form is missing or stale: `Generate Fee form`.
7. Other required forms missing or stale: `Generate missing files`.
8. Section 2 is missing or stale: `Preview Section 2 update` or `Update Section 2`.
9. Submitted Material incomplete: `Check Submitted Material`.
10. Public drive not uploaded after TASK_319 approves upload: `Upload to public drive`.
11. Everything ready: `Open official project folder`.

The top action should explain the blocking reason in business language.

## Button Model

The UI should support:

- one primary top action,
- a row-level action for the selected preparation task,
- secondary single-file actions only inside expanded row details.

Examples:

- `Create local project folder`
- `Collect request material`
- `Generate missing files`
- `Generate Fee form`
- `Generate Test Record`
- `Generate Customer Feedback form`
- `Preview Section 2 update`
- `Update Section 2`
- `Check Submitted Material`
- `Upload to public drive`
- `Open official project folder`

Do not show a broad row of unrelated action buttons.

Do not let `Generate missing files` silently:

- confirm Fee authority,
- update or overwrite Application Form Section 2,
- upload to the public drive,
- collect request material,
- repair folder conflicts.

## TASK_317-TASK_320 Landing Map

`TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION` must first land the minimum `Project Folder` single-task frame, then add:

- `Request material` row,
- Source Book copy rules,
- request email and attachment collection state.

`TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR` should land in:

- `Local project folder`,
- `Submitted Material`,
- missing required folder/file checks,
- repairable inconsistency actions.
- `Required forms` derived-file readiness only where TASK_318 explicitly approves checks.

TASK_318 replaces the user-facing completeness/readiness responsibility formerly represented by TASK_312's `Project package` preview. It should not add another package preview panel or enhance the old package-preview endpoint as its main product surface. Any checks for project folder, Matrix authority, Confirmed Fee authority, Section 2, Customer Feedback form, Test Record, Fee form, and Submitted Material must be expressed through the `Project Folder` task rows. Reuse of lower-level helper logic is allowed only if the new API/UI contract remains `Project Folder`-first.

`TASK_319_PUBLIC_DRIVE_UPLOAD_UPDATE` should land in:

- `Public drive upload`,
- conflict/update/skip status,
- upload/update primary action when ready.

Before TASK_319 is implemented and approved, no public-drive upload/update button should be visible as an enabled action.

`TASK_320_FINAL_SINGLE_TASK_WORKBENCH_UI` should:

- finish any remaining old user-facing `Package` naming cleanup,
- preserve `Project Folder | Execution` tabs already introduced before or during TASK_317,
- collapse or remove redundant summary surfaces,
- ensure the page always answers current state, blocker, and next action.

## Plugin And Mode Guidance

The user does not need to manually open plugins for normal execution.

Recommended default:

- Use `$impeccable` automatically for ConnLab UI/UX copy and layout decisions.
- Use Browser automatically for local Workbench smoke tests.
- Use Superpowers writing/execution skills automatically for task planning and implementation control.

Use these only when explicitly useful:

- Product Design: use for a higher-level interaction flow review or alternative UI concepts.
- Figma: use only if the user wants a visual wireframe or editable mockup before implementation.
- GitHub / linear: use only if the user asks to create issues, PRs, or external tracker tasks.
- Creative Production / Slack: not needed for this flow.

Plan mode is optional. ConnLab task rules already require task file + plan review before implementation.

Goal mode is optional and should be used only if the user wants a long-running objective with explicit progress tracking or budget.

## Scope

This task may create or update planning documents only:

- task file,
- executable plan,
- task board / plan index status.

This task must not change:

- frontend implementation,
- backend API,
- database schema,
- file-system operations,
- Office gateways,
- project folder generation behavior.

## Acceptance Criteria

- A task file exists for TASK_317A.
- An executable plan exists for TASK_317A.
- The task board clearly states that TASK_317A is the next review step before TASK_317.
- The UI naming contract removes `Package` and `Workspace` from the future user-facing Project Folder flow.
- The document defines `Project Folder`, `Local DL folder`, `Official project folder`, `Source Book`, and `Submitted Material` as a fixed hierarchy.
- The plan requires TASK_317 to start with the minimum `Project Folder` single-task UI frame before adding request-material controls.
- The plan maps TASK_317-TASK_320 into the Project Folder UI structure.
- The plan separates Confirmed Fee authority from Fee form generation.
- The plan treats Application Form Section 2 as a controlled preview/write-back row, not a normal generated file.
- The plan prevents public-drive upload/update from appearing as an enabled action before TASK_319.
- The plan states plugin/mode usage so the user does not need to manually select plugins.

## Validation

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task_board or task316 or task313a"
git diff --check
```

If no existing test covers the new planning document, a document-only validation with `git diff --check` is acceptable for TASK_317A. Implementation tasks after this must add functional tests.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because the work is bounded to product/UI information architecture, task sequencing, and repository documentation. It does not require high-risk file operations, Office automation, database migration, or production code changes. The main risk is scope creep into implementation; this task explicitly forbids code changes and requires user approval before TASK_317 implementation.

## Out Of Scope

- Collecting request emails or attachments.
- Moving or copying any real project files.
- Generating Test Record, Fee form, Customer Feedback form, or Section 2 content.
- Public-drive upload or sync.
- Repairing existing project folder inconsistencies.
- Renaming existing API/backend package concepts.
- Implementing the final UI.
