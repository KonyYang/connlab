# Official Project Workspace Execution Guide

Status: Boundary corrections documented and accepted for planning. Implementation is still not approved.

Date: 2026-06-12.

Applies after:

- `TASK_313A_PROJECT_WORKBENCH_LIFECYCLE_MODE_REDESIGN`
- `TASK_313B_OFFICIAL_PROJECT_WORKSPACE_PLAN`

## Purpose

This guide makes the follow-up sequence executable without slipping back into the old `Package` mental model.

Implementation is not approved. The boundary rules below are the accepted planning baseline that must be reflected in each active task file and executable plan.

The product direction is:

```text
ConnLab helps the operator create, complete, check, and upload an official project folder.
```

The user-facing model is:

```text
Local project workspace
  Source Book
  Official project folder
Public drive upload
```

`Package`, `package execute`, `orchestrator`, `staging`, `.connlab`, SQLite, API route names, and backend generated-output folders are not user-facing workflow concepts.

## Global Execution Rules

Every follow-up task must obey these rules:

1. Read `AGENTS.md`, `docs/task_board.md`, this guide, then the current `tasks/TASK_XXX_*.md`.
2. Create or update a task-specific executable plan before coding.
3. Get user approval before implementation.
4. Implement only the current approved task.
5. Add tests for the new behavior.
6. Run relevant validation.
7. Update `docs/task_board.md` before stopping.
8. Do not continue into the next task automatically.

Current ordering decision:

- TASK_313, TASK_314, and TASK_315 remain deferred.
- TASK_313B boundary corrections are documented and accepted for planning.
- TASK_316 is the next implementation candidate only after its own task file and executable plan are approved.

## Terminology Contract

Use these terms in UI:

- `Local project workspace`
- `Source Book`
- `Official project folder`
- `Submitted Material`
- `Public drive upload`

Avoid these terms in UI:

- `Package`
- `Package execute`
- `Project package`
- `Orchestrator`
- `Staging`
- `.connlab`
- `manifest`
- API paths

Technical docs may mention internal terms only when explaining implementation boundaries.

## Local Folder Contract

The intended local structure is:

```text
{DL_NUMBER}/
  Source Book/
  {DL_NUMBER} {PRODUCT_DESCRIPTION} {TEST_DESCRIPTION}/
    E-mail/
    Submitted Material/
    Photos/
    Test results/
      Final Examination/
    ...
  .connlab/
    manifest.json
    file-index.json
    upload-state.json
```

The official project folder is created by copying a configured template folder such as:

```text
D:/Source/Template/DL-XXXX-YY-ZZZ project/
```

The copied template root is renamed using:

```text
{DL_NUMBER} {PRODUCT_DESCRIPTION} {TEST_DESCRIPTION}
```

## File Operation Safety Contract

Every task that copies, imports, uploads, or cleans files must obey:

- Source Book stores original imported request email and original attachments.
- Official project folder `E-mail` and `Submitted Material` store controlled copies.
- ConnLab must not silently delete files from the user's original source location.
- Only ConnLab-owned temporary import-cache files may be cleaned after explicit confirmation or an approved retention rule.
- Destructive move/delete behavior requires a separate approved task.

Avoid vague phrases such as `move or collect` and `copy or move` in task files.

## State Authority Contract

Avoid competing truth sources:

- SQLite is ConnLab's application index and normal query source.
- `.connlab/manifest.json` is a portable local workspace manifest/cache.
- The real file system is the final authority for folder/file existence.
- Readiness checks must inspect the file system.
- If SQLite and `.connlab` disagree, show a repairable inconsistency instead of guessing.

## Official Folder Naming Contract

TASK_316 must define and test:

- illegal character replacement
- whitespace normalization
- maximum filename segment and full path handling
- fallback when product description or test description is missing
- behavior when target folder already exists
- whether the configured template path is the template root itself or a parent containing exactly one template root

## Public Drive Upload Safety Contract

TASK_319 must obey:

- Auto-update is allowed only for files ConnLab previously uploaded and whose public-drive copy has not been modified by a human since that upload.
- If a public-drive file changed after ConnLab's last upload, mark it as conflict.
- Never silently overwrite public-drive files.
- Never delete public-drive files.
- Upload preview must show add/update/skip/conflict before writing.

## Settings Contract

Future tasks should ensure ConnLab can configure:

- local project workspace root
- official project folder template path
- public drive target root

If existing settings already support one of these paths, reuse the existing settings contract. Do not invent duplicate setting names.

## TASK_316 - Local Project Workspace Creation

### Goal

Create the local DL workspace and official project folder from the configured template.

Also create the minimum single-primary-action Workbench frame for the new workspace flow so the UI does not collect another stack of buttons before TASK_320.

### User Story

As a lab operator, I want to click one button to create the local project workspace, so I have a safe local folder that can later be completed and uploaded to the public drive.

### Inputs

- project id
- DL number
- product description
- test description
- configured local workspace root
- configured official project folder template path

### Outputs

- local DL workspace folder
- `Source Book` folder
- copied and renamed official project folder
- internal tracking record for paths and template source
- minimal Workbench state/action UI for workspace creation

### Required Behavior

- Preview target paths before creating.
- Validate local workspace root.
- Validate template path.
- Copy the entire template folder.
- Rename copied template root.
- Never overwrite an existing workspace or official folder.
- Return actionable blockers.
- Show one primary Workbench action for this state.
- Keep diagnostics collapsed or secondary.
- Apply and test the official folder naming contract.

### Out Of Scope

- No public drive upload.
- No request email collection.
- No Test Record/Fee/Customer Feedback generation.
- No Section 2 write-back.

### Minimum Tests

- missing local workspace root blocks preview/create
- missing template path blocks preview/create
- existing target blocks create
- successful create copies template and creates `Source Book`
- internal tracking record contains workspace and official folder paths
- Workbench shows one workspace creation primary action instead of a stack of workspace buttons

### Stop Point

Stop after local workspace creation is implemented and validated.

## TASK_317 - Source Book And Request Material Collection

### Goal

Collect imported request email and parsed attachments into the local workspace and official project folder.

### User Story

As a lab operator, I want imported request materials to be organized automatically, so I do not manually drag files between E-mail, Submitted Material, and raw reference folders.

### Inputs

- existing local workspace
- existing official project folder
- imported request email
- parsed attachments
- operator-selected useful submitted materials when ambiguity exists

### Outputs

- raw request material stored under `Source Book`
- controlled request email copy stored under official folder `E-mail`
- controlled selected submitted material copies stored under official folder `Submitted Material`
- file mapping record

### Required Behavior

- Block when local workspace is missing.
- Block when official project folder is missing.
- Preserve raw material traceability in `Source Book`.
- Copy request email into `E-mail`.
- Copy useful submitted materials into `Submitted Material`.
- Never silently delete files from the user's original source location.
- Ask for operator selection when attachment classification is ambiguous.
- Record source-to-target mappings.

### Out Of Scope

- No AI attachment classification.
- No public drive upload.
- No report or evidence workflow.

### Minimum Tests

- missing workspace blocks collection
- missing official folder blocks collection
- email target path is correct
- submitted material target path is correct
- original source files are not deleted
- ambiguous attachments require explicit selection
- mapping record is written

### Stop Point

Stop after material collection is implemented and validated.

## TASK_318 - Official Project Folder Check And Repair

### Goal

Replace `Package readiness` with a business-readable official project folder check.

### User Story

As a lab operator, I want ConnLab to tell me what is missing from the official project folder and give me one repair action, so I can finish the folder without understanding internal services.

### Inputs

- local workspace state
- official folder path
- file mapping record
- Confirmed Matrix authority
- Confirmed Fee authority
- Section 2 sync status
- Test Record generation state
- Fee Form generation state
- Customer Feedback Form state

### Outputs

- readiness/check result
- current blocker
- current repair action

### Required Checks

- local workspace exists
- `Source Book` exists
- official project folder exists
- `E-mail` exists
- request email exists under `E-mail`
- `Submitted Material` exists
- submitted materials exist under `Submitted Material`
- `Photos` exists
- `Test results` exists
- `Test results/Final Examination` exists
- Test Record present/current
- Fee Form present/current
- Customer Feedback Form present/current
- Section 2 synced/current

### Repair Actions

Expose only the most relevant current action:

- `Create local project workspace`
- `Collect submitted material`
- `Generate Test Record`
- `Generate Fee Form`
- `Prepare Customer Feedback Form`
- `Sync Section 2`
- `Refresh check`

### Out Of Scope

- No public drive upload.
- No evidence/image data persistence.
- No report generation expansion.
- No automatic photo import.

### Minimum Tests

- each missing item maps to the expected blocker
- each blocker maps to one repair action
- future execution evidence is not required
- ready state requires all approved required items
- UI copy contains no `Package`

### Stop Point

Stop after readiness check and repair-action selection are implemented and validated.

## TASK_319 - Public Drive Upload/Update

### Goal

Upload or update the local official project folder to the configured public drive location through an explicit operator action.

### User Story

As a lab operator, I want to review what will be uploaded to the public drive before ConnLab writes shared files, so I can avoid accidental overwrites or missing submissions.

### Inputs

- local official project folder
- configured public drive root
- readiness result from TASK_318
- upload-state record

### Outputs

- upload preview
- upload result
- updated upload-state record

### Required Behavior

- Preview public drive target before write.
- Show add/update/skip/conflict lists.
- Block overwrite conflicts by default.
- Allow auto-update only when ConnLab previously uploaded the file and the public-drive copy has not changed since that upload.
- Mark public-drive files changed by humans as conflicts.
- Do not delete public drive files.
- Do not silently upload in the background.
- Record upload target and timestamp.

### Out Of Scope

- No server/LAN deployment.
- No permission model.
- No automatic scheduled sync.
- No public drive deletion or cleanup.

### Minimum Tests

- missing public drive root blocks preview/upload
- missing local folder blocks preview/upload
- target absent copies folder
- target exists with conflict blocks upload
- human-modified public-drive file is marked conflict
- unchanged files are skipped
- upload-state records target and timestamp

### Stop Point

Stop after public-drive upload preview/update is implemented and validated.

## TASK_320 - Single-Task Workbench UI

### Goal

Make Project Workbench an operator-facing single-task page.

TASK_316 already starts the minimum frame. TASK_320 finishes the full simplification across all states.

### User Story

As a lab operator, I want Workbench to tell me exactly what this project needs next, so I can click the next action without understanding lifecycle internals.

### Visible State Order

The Workbench should derive one current state:

```text
Temporary project planning
Publish Matrix authority
Create local project workspace
Complete official project folder
Upload to public drive
Official project folder ready
Execution console
```

### UI Rule

The default page shows:

- one short title
- one reason
- one primary button
- optional collapsed diagnostics

Avoid default tabs, repeated checklists, repeated secondary buttons, and internal task names.

### Out Of Scope

- No new backend behavior beyond prior tasks.
- No StepInstance/TestResult/evidence/report/AI/permission/multi-user scope.
- No new Matrix Editor behavior.
- No new Fee Evaluation behavior.

### Minimum Tests

- no DL shows planning action
- DL without active Matrix shows Matrix authority action
- active Matrix without workspace shows create workspace action
- incomplete official folder shows one repair action
- ready local folder not uploaded shows upload action
- uploaded current folder shows ready state
- no `Package`, `placeholder`, `read-only in this task`, or task IDs appear in user-facing Workbench copy

### Stop Point

Stop after Workbench UI is implemented, browser-smoked, and task board is updated.

## TASK_313 Rewrite Guidance

Do not resume the old TASK_313 as written.

After TASK_316-TASK_318, rewrite or supersede TASK_313 around:

```text
Complete official project folder
```

not:

```text
Execute package
```

The future task should generate or update approved official-folder contents inside the local official project folder. Public drive upload remains TASK_319.

## Cross-Task Validation Matrix

| Area | Required Validation |
| --- | --- |
| Folder creation | pytest with temporary directories |
| Template copy | no-overwrite tests |
| Settings paths | missing/invalid path tests |
| Material collection | mapping and ambiguity tests |
| Readiness check | blocker-to-action tests |
| Public drive upload | preview/conflict tests with temp dirs |
| Workbench UI | Vitest selector/page tests |
| Browser smoke | current project route after each UI task |
| Static copy guards | no `Package` in user-facing Workbench copy after TASK_320 |

## Required Handoff At Each Task End

Each task final response should include:

- task id completed
- validation commands and pass/fail result
- task board updated or not
- current stop point
- next recommended task

Do not start the next task in the same turn.
