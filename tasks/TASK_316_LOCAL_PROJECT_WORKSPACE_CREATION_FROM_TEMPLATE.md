# TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE`, complete.

Completion note: Implemented local official project workspace preview/create, safe template copy, `.connlab/manifest.json`, SQLite workspace index, API routes, and minimum single-primary-action Workbench UI. Review follow-up added completed-workspace preview recognition, registered-LTR authority preference over legacy `project.project_no`, application-form requested-testing naming input, Settings-page `Public Project locations` only for public-drive placement, Workbench path-blocker reminder without a shortcut button, and sidebar Projects restoration to the current Workbench context. Local workspace root and official project folder template remain installation-level settings, not ordinary operator Settings fields.

Executable plan:

- `docs/task_316_local_project_workspace_creation_from_template_plan.md`

## Goal

Add the first implementation slice for the official project workspace model:

1. configure or reuse the required path settings,
2. preview a local DL workspace and official project folder copied from template,
3. create the local workspace safely,
4. create a portable `.connlab/manifest.json`,
5. show the new workspace state in Project Workbench as one primary operator action.

The user-facing action is:

```text
Create local project workspace
```

## User Story

As a lab operator, I want ConnLab to create the local DL workspace and official project folder from the approved template, so I can prepare project files locally before uploading anything to the public drive.

## User-Facing Model

Show these concepts in UI:

- Local project workspace
- Source Book
- Official project folder
- Public drive upload path as a setting or future target

Do not show these concepts as workflow labels:

- Package
- Package execute
- Orchestrator
- Staging
- `.connlab`
- manifest
- SQLite
- API route names

## Required Settings Contract

TASK_316 must provide a single source of configured paths for:

- local project workspace root,
- official project folder template path,
- public drive root path.

Rules:

- Reuse existing settings mechanisms where possible.
- Do not create duplicate setting names for the same path.
- User-editable paths remain plain path settings, not database concepts.
- Missing or invalid local workspace root or official template path must return actionable blockers.
- Missing or invalid public drive root must be reported only as a warning or future-readiness issue in TASK_316. It must not block local workspace preview or creation.
- Public drive upload is not implemented in TASK_316, but the public drive root setting contract must be named and documented for later TASK_319.

## Folder Naming Contract

The official project folder name is built from:

```text
{DL_NUMBER} {PRODUCT_DESCRIPTION} {TEST_DESCRIPTION}
```

TASK_316 must define and test:

- invalid Windows filename character replacement,
- whitespace normalization,
- reserved device name avoidance when applicable,
- maximum folder-name segment handling,
- maximum full-path handling,
- fallback when product description is missing,
- fallback when test description is missing,
- behavior when the target local DL workspace exists,
- behavior when the target official project folder exists,
- whether the configured template path is the template root itself or a parent containing exactly one template root.

No overwrite is allowed.

Existing-path rules:

- If `{DL_NUMBER}/` already exists and contains no unsafe conflict, TASK_316 must allow adopt/continue rather than block the whole workflow.
- If `{DL_NUMBER}/Source Book/` is missing under an otherwise safe existing workspace, TASK_316 may create it.
- If `{DL_NUMBER}/.connlab/` is missing under an otherwise safe existing workspace, TASK_316 may create it.
- If `{DL_NUMBER}/.connlab/manifest.json` exists but disagrees with the file system, TASK_316 must report a repairable inconsistency.
- If the planned official project folder target name already exists, TASK_316 must block creation or defer to a later explicit repair/adopt task. It must not merge into or overwrite that folder in TASK_316.

## Local Folder Contract

Target structure:

```text
{LOCAL_WORKSPACE_ROOT}/
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
```

TASK_316 creates:

- the local DL workspace folder,
- `Source Book`,
- the official project folder copied from the configured template,
- `.connlab/manifest.json`.

If a safe local DL workspace already exists, TASK_316 continues from it and creates only missing ConnLab-managed pieces allowed by this task. This prevents real existing projects from being blocked just because the top-level `{DL_NUMBER}/` folder is already present.

TASK_316 does not collect request emails or attachments. That belongs to TASK_317.

## SQLite And `.connlab` Boundary

SQLite:

- ConnLab application index and normal query source.
- May store the project workspace record for UI/API lookup.

`.connlab/manifest.json`:

- Portable local workspace manifest/cache.
- Stores enough path and template metadata for repair and portability.

File system:

- Final authority for whether folders and files exist.
- Preview and readiness logic must inspect actual paths.

If SQLite and manifest disagree, TASK_316 may report a repairable inconsistency. It must not silently guess or overwrite.

## API Contract

Add preview and create endpoints under a workspace-specific route. Recommended route shape:

```text
GET  /api/projects/{project_id}/official-workspace/preview
POST /api/projects/{project_id}/official-workspace/create
```

The preview response must include:

- project id,
- DL number used,
- local workspace root,
- local DL workspace path,
- official project folder template path,
- official project folder path,
- Source Book path,
- manifest path,
- status: `ready`, `completed`, `blocked`, `adoptable`, `exists`, or `inconsistent`,
- blockers,
- warnings,
- planned created paths,
- template root interpretation.

The create response must include:

- project id,
- created or existing workspace record id,
- local DL workspace path,
- official project folder path,
- Source Book path,
- manifest path,
- created paths,
- warnings.

Create must re-run preview before writing and reject stale or blocked conditions.

Create may proceed from `ready` or `adoptable`. It must reject `blocked`, `exists`, and `inconsistent` states unless a later task explicitly implements repair/adopt for those cases.

## File Operation Recovery Contract

Template copy must avoid leaving half-created official folders.

Rules:

- Copy the resolved official template root into a ConnLab-owned temporary directory under the same local DL workspace.
- After the copy succeeds, rename the temporary directory to the final official project folder path.
- Write `.connlab/manifest.json` and any SQLite workspace index only after the official folder rename succeeds.
- If copy fails, remove only the ConnLab-owned temporary directory created during this run.
- If final rename fails, remove the ConnLab-owned temporary directory when possible and return an actionable error.
- Never remove user-created existing folders or files.
- A failed create must not leave a final official project folder path that makes the next preview permanently look like a successful existing project.

## Workbench UI Contract

TASK_316 must add the minimum single-primary-action Workbench frame for the new workspace state.

Backend preview is allowed for any project with a DL number so settings, naming, and file-system blockers can be inspected.

The Workbench primary action is narrower. When a project has a DL number and an active Confirmed Matrix but no completed local project workspace, the Workbench default surface should show:

- one state title,
- one business-readable reason,
- one primary button: `Create local project workspace`,
- diagnostics collapsed or visually secondary.

It must not add a new row of workspace buttons, a duplicated checklist-first page, or another `Package` panel.

This is the minimum UI guard before TASK_320 finishes the full Workbench simplification.

## In Scope

- Settings contract for local workspace root, official project folder template path, and public drive root path.
- Backend domain/application/infrastructure support for workspace preview and creation.
- Template copy from configured official project folder template.
- Official folder name planning and validation.
- `.connlab/manifest.json` creation.
- SQLite-backed workspace index if needed for lookup.
- Thin FastAPI routes and typed Pydantic responses.
- Frontend API client support.
- Minimal Workbench single-primary-action state for workspace creation.
- Pytest and Vitest coverage.
- Task board update after implementation approval and completion.

## Out Of Scope

- No public drive upload or update.
- No request email or attachment collection.
- No submitted material copy.
- No Test Record, Fee Form, or Customer Feedback generation changes.
- No Section 2 write-back changes.
- No execution evidence, photos automation, StepInstance, TestResult, report generation, AI review, permissions, LAN, or multi-user scope.
- No destructive move/delete behavior.
- No hidden background creation from Confirm Matrix, Confirm Fee, or Matrix Editor.
- No implementation before explicit user approval of this task and plan.

## Acceptance Criteria

- A project with a DL number can preview the local workspace path and official project folder path before creation, even before Workbench chooses to show it as the primary action.
- Missing local workspace root blocks preview/create with an actionable message.
- Missing or invalid template path blocks preview/create with an actionable message.
- Missing or invalid public drive root does not block local preview/create in TASK_316; it appears as a warning or future-readiness issue only.
- The official folder name is sanitized and remains business-readable.
- Missing product or test description uses defined fallbacks instead of producing an empty or broken folder name.
- Existing safe local DL workspace is adoptable/continuable; TASK_316 may create missing `Source Book` or `.connlab` pieces.
- Existing planned official project folder blocks create or is deferred to a later explicit repair/adopt flow; no overwrite or merge occurs.
- Manifest/file-system disagreement is reported as repairable inconsistency.
- Template copy failure cleans only ConnLab-owned temporary paths and does not leave the final official folder path as a half-created project.
- Successful create copies the template folder, creates `Source Book`, creates `.connlab/manifest.json`, and records the workspace in ConnLab's index.
- Preview/create inspect the real file system before deciding status.
- Workbench shows only one workspace creation primary action when the project has a DL number, active Confirmed Matrix, and no completed local workspace.
- User-facing Workbench copy does not use `Package`, `.connlab`, `manifest`, task IDs, or API route names.

## Validation Plan

Backend:

- `py -m pytest tests/unit/test_official_project_workspace_naming.py tests/unit/test_official_project_workspace_service.py -q`
- `py -m pytest tests/integration/test_official_project_workspace_api.py -q`

Frontend:

- `cd frontend; npm test -- --run ProjectWorkbench officialWorkspace --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or official_workspace"`

General:

- `git diff --check`

Browser smoke after implementation approval:

- Open a DL project with active Confirmed Matrix and no local workspace.
- Confirm Workbench shows one `Create local project workspace` action.
- Confirm diagnostics are not the main surface.
- Create workspace using temporary/local settings.
- Confirm the local folder structure exists and no public drive action runs.

## Stop Point

Stop after this task file and executable plan are reviewed. Do not implement TASK_316 until the user explicitly approves implementation. Do not continue into TASK_317, TASK_318, TASK_319, TASK_320, or revised TASK_313 in the same turn.
