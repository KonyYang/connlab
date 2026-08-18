# TASK_313B_OFFICIAL_PROJECT_WORKSPACE_PLAN

Status: Boundary corrections documented and accepted for planning. Implementation is still not approved.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_313B is a planning and scope-correction task before resuming TASK_313. It replaces the confusing user-facing `Package` concept with an operator-facing official project workspace model:

```text
Local DL workspace
  Source Book
  Official project folder
  .connlab internal manifest
Public drive upload target
```

Execution guide:

- `docs/task_313b_official_project_workspace_execution_guide.md`

## Goal

Define the next implementation sequence so ConnLab helps a lab operator create, complete, check, and upload a formal project folder without exposing backend/internal concepts.

## User-Facing Model

The operator should understand only:

- local project workspace
- Source Book
- official project folder
- Submitted Material
- public drive upload

The operator should not need to understand:

- package orchestrator
- backend staging
- internal generated-output cache
- SQLite records
- `.connlab` manifest
- API route names

## Local Folder Model

Example:

```text
DL-2025-11-074/
  Source Book/
    original request email
    original attachments
    manually added reference material

  DL-2025-11-074 Coolpower 3.40mm Pin Busbar To Socket PCB Qualification test/
    E-mail/
    Submitted Material/
    Photos/
    Test results/
      Final Examination/
    Customer Feedback Form.xlsx
    Fee Form.xlsx
    Test Report *.docx

  .connlab/
    manifest.json
    file-index.json
    upload-state.json
```

## Business Rules

- The local DL workspace is the operator-facing local project container.
- `Source Book` stores raw and reference material, including data ConnLab cannot yet process automatically.
- The official project folder is the local folder that can later be uploaded to the public drive.
- The official project folder should be created by copying the configured template folder and renaming the copied root folder.
- Source Book keeps original request email and original attachments.
- The official project folder keeps controlled copies in `E-mail` and `Submitted Material`.
- ConnLab must not silently delete files from the user's original source location.
- Only temporary import-cache files owned by ConnLab may be cleaned after explicit confirmation or a controlled retention rule.
- Public drive upload must be a separate, explicit action with preview and conflict detection.
- SQLite is ConnLab's application index.
- `.connlab/manifest.json` is a portable local workspace manifest/cache.
- The real file system remains the final authority for whether folders and files exist.
- ConnLab internal tracking files should not be presented as user workflow concepts.

## Boundary Corrections Documented Before Implementation

The TASK_313B direction is accepted for planning, and the required boundaries below are now documented as the baseline for follow-up tasks. Implementation remains not approved. Next step: create and review `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE` task file and executable plan.

### 1. Task Board Ordering

The task board must not simultaneously recommend TASK_314/TASK_315 and TASK_313B/TASK_316 as the next step.

Required decision:

- TASK_313, TASK_314, and TASK_315 remain deferred.
- The next recommended planning step is to finalize TASK_313B boundary corrections.
- The next implementation candidate after approval is TASK_316.

### 2. Workbench UI Must Be Front-Loaded

Do not wait until TASK_320 to simplify the Workbench.

TASK_316 must include a minimal single-primary-action Workbench frame for the new workspace flow:

- one current state title
- one reason
- one primary button
- diagnostics collapsed or secondary

TASK_320 may still do the full UI consolidation later, but TASK_316 must prevent newly added workspace features from appearing as another button stack.

### 3. File Copy And Move Rules

Use explicit file operation language.

Required rules:

- Source Book stores original imported request email and original attachments.
- Official project folder `E-mail` and `Submitted Material` store controlled copies.
- ConnLab never silently deletes files from the user's original file location.
- ConnLab-owned temporary import cache may be cleaned only after explicit confirmation or an approved retention rule.
- Any destructive delete/move behavior requires a separate approved task.

### 4. SQLite And `.connlab` Responsibilities

Avoid two competing truth sources.

Required rules:

- SQLite is the ConnLab application index and query source.
- `.connlab/manifest.json` is a portable workspace manifest/cache for the local folder.
- File existence and freshness checks must inspect the actual file system.
- If SQLite and `.connlab` disagree, the check must report a repairable inconsistency instead of guessing.

### 5. Official Folder Naming Rules

Every implementation task that creates paths must define:

- invalid character replacement
- whitespace normalization
- maximum segment/path length handling
- fallback when product description or test description is missing
- behavior when target folder already exists
- whether the configured template path is the template root itself or a parent containing exactly one template root

### 6. Public Drive Upload Safety

Public drive upload must be conservative.

Required rules:

- Auto-update is allowed only for files ConnLab previously uploaded and whose public-drive copy has not been modified by a human since that upload.
- If the public-drive file changed after ConnLab's last upload, mark it as conflict.
- Never silently overwrite public-drive files.
- Never delete public-drive files.
- Upload preview must show add/update/skip/conflict before writing.

## Proposed Task Sequence

### TASK_313B - Official project workspace planning and terminology correction

Purpose:

- Update product/task terminology.
- Freeze `Package` as an internal/legacy term.
- Define user-facing names and Workbench states.
- Decide how TASK_313 should be rewritten or superseded.

Output:

- Updated task board.
- Updated task plan index.
- Follow-up task files for implementation slices.

No code implementation.

### TASK_316 - Local official project workspace foundation

Purpose:

- Add settings-backed local workspace root, official project folder template path, and public drive root path contract if current settings are insufficient.
- Create a local DL workspace folder named by DL number.
- Copy the configured official project folder template into the DL workspace.
- Rename the copied template root to `DL number + product description + test description`.
- Create or update `.connlab/manifest.json` to track workspace paths and template source.
- Add the minimal single-primary-action Workbench frame for this new workspace state so TASK_316 does not add another visible tool stack.

Primary user action:

```text
Create local project workspace
```

Out of scope:

- No public drive upload.
- No Test Record/Fee/Customer Feedback generation changes.
- No email parsing changes unless already available through current intake.

### TASK_317 - Source Book and request material collection

Purpose:

- Formalize `Source Book` as the raw-material area.
- On request email import, copy the original email and parsed attachments into `Source Book`.
- Copy the request email into official folder `E-mail`.
- Copy operator-selected submitted materials into official folder `Submitted Material`.
- Record source-to-target mappings in `.connlab/file-index.json` or equivalent structured storage.

Primary user action:

```text
Import request email
```

Out of scope:

- No AI classification.
- No automatic guess of ambiguous attachments without operator confirmation.

### TASK_318 - Official project folder readiness check and repair actions

Purpose:

- Replace `Package readiness` with `Official project folder check`.
- Check required folders and files:
  - official project folder root
  - `E-mail`
  - `Submitted Material`
  - `Photos`
  - `Test results`
  - `Test results/Final Examination`
  - request email
  - submitted attachments
  - Test Record
  - Fee Form
  - Customer Feedback Form
  - Section 2 sync state
- Show missing/outdated/ready states.
- Provide one current repair action at a time.

Primary user actions may include:

- `Create official project folder`
- `Collect submitted material`
- `Generate Test Record`
- `Generate Fee Form`
- `Prepare Customer Feedback Form`
- `Sync Section 2`
- `Refresh check`

Out of scope:

- No public drive upload.
- No execution evidence or photos automation beyond folder presence checks.

### TASK_319 - Public drive upload/update preview

Purpose:

- Add explicit local-to-public-drive upload/update action.
- Preview target public drive path.
- Compare local official project folder to public drive target.
- Show new/update/skip/conflict list.
- Block unsafe overwrite unless a later task explicitly approves conflict resolution.

Primary user action:

```text
Upload to public drive
```

Out of scope:

- No silent background upload.
- No deletion of public drive files.
- No LAN/server deployment assumptions.

### TASK_320 - Workbench single-task operator UI

Purpose:

- Finish the full Workbench simplification started in TASK_316.
- Replace remaining visible lifecycle tabs and checklist-heavy surfaces with a single-current-task Workbench.
- The page should answer:
  - What is this project's current state?
  - Why can or cannot the user continue?
  - Which one button should the user press next?
- Keep advanced details behind explicit expandable diagnostics.

Recommended visible states:

```text
Temporary project planning
Publish Matrix authority
Create local project workspace
Complete official project folder
Upload to public drive
Official project folder ready
Execution console
```

Out of scope:

- No new backend behavior unless implemented by prior tasks.
- No StepInstance/TestResult/evidence/report expansion.

## Impact On Existing TASK_313

Existing TASK_313 should not be implemented as currently written because it assumes a `project-package/execute` action that places files directly into the latest project folder's `Submitted Material`.

Recommended decision:

- Keep TASK_313 deferred.
- Rewrite or supersede TASK_313 after TASK_316-TASK_318 clarify the local workspace and official folder model.
- Rename the future execution task from `Execute package` to a user-facing action such as `Complete official project folder`.

## Acceptance Criteria For This Planning Task

- The plan distinguishes local workspace, official project folder, Source Book, internal manifest, and public drive upload.
- The plan stops using `Package` as the primary user-facing concept.
- The plan preserves explicit operator control before public drive upload.
- The plan keeps ConnLab internal files hidden from normal user workflow.
- The plan does not authorize implementation by itself.

## Stop Point

Stop after user reviews and approves this plan. Do not implement TASK_316, TASK_317, TASK_318, TASK_319, TASK_320, or revised TASK_313 without separate task approval.
