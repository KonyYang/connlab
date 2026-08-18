# TASK_317E Temporary Project Stop And Safe Delete — Executable Plan

Status: Complete.

Date: 2026-06-13

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317E` completed. `TASK_317D` is complete with review corrections. Do not enter any TASK_319 public-drive/upload work without separate approval.

Allowed reason: The current Projects Registry still exposes the historical `Show cancelled` mechanism as a primary toolbar control. That conflicts with the post-TASK_317D model where active temporary projects belong in `Planning`, stopped projects are lifecycle history, and mistaken/duplicate temporary projects need guarded deletion rather than cancellation.

---

## 1. Task Understanding

### Goal

Replace the primary `Show cancelled` registry mechanism with lifecycle-accurate `Stopped` semantics and add a safe deletion path for mistaken or duplicate temporary projects.

### Inputs

- Current `ProjectStatus` enum, especially internal `CANCELLED = "cancelled"`.
- Current Project Registry queue model:

```text
All / Planning / Matrix Needed / Ready to Test / Folder Blocked / Completed
```

- Current TASK_317D temporary context persistence.
- Current Workbench temporary planning lifecycle mode.
- Existing records that make deletion unsafe:
  - LTR records,
  - Confirmed Matrix authority,
  - official workspace / project folder records,
  - project-scoped file assets,
  - request material collections,
  - ProjectOutputRecord,
  - confirmed fee/generated output records.

### Outputs

- `/projects` no longer shows `Show cancelled`.
- User-facing stopped lifecycle copy uses `Stopped`.
- Default registry view is `On-going`, meaning active registered DL/LTR work.
- Project Registry uses one compact macro Project view selector: `On-going`, `Planning`, `Completed`, and `All`; the `Project ID` header exposes a compact ascending/descending sort for DL/LTR year-month-sequence and TMP suffix order; the table footer shows the current view count.
- `Planning` is active temporary no-LTR work, and `On-going` is active registered DL/LTR work. They do not overlap.
- `Completed` includes completed, closed, failed, and stopped lookup/history records; `Stopped` remains a row `Status` value rather than a Project view option.
- `Matrix Needed`, `Ready to Test`, and `Folder Blocked` remain row `Status` values, not Project view options.
- Project Registry restores the same browser session's selected Project view, search text, Project ID sort direction, and page number when users open Workbench and return to `/projects`.
- Temporary Workbench exposes controlled `Stop project` and `Delete temporary project` paths.
- Backend delete preview and delete execution enforce server-side safety guards.
- Formal or artifact-bearing projects cannot be deleted; they can only be stopped.

### Modules

Likely backend modules:

- `backend/domain/enums.py`
- `backend/application/project_stop_service.py` or current lifecycle service if suitable
- `backend/application/temporary_project_delete_guard_service.py`
- `backend/api/routes_project.py` or a narrow project lifecycle route module
- `backend/infrastructure/storage/repositories/project.py`
- `backend/infrastructure/storage/repositories/project_temporary_context.py`
- repositories for LTR, Confirmed Matrix, official workspace, folder, request material, output records, confirmed fee

Likely frontend modules:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/project-dashboard.css`
- `frontend/src/workbench.css`

### Not Allowed

- No `archived` project status or archive concept.
- No public-drive upload/update/delete.
- No formal project delete.
- No LTR/DL recycling.
- No Matrix execution, StepInstance, evidence, report, AI, permissions, LAN, or multi-user expansion.
- No Projects overview row-level Delete/Stop buttons.
- No broad advanced filter system beyond the compact Project view selector needed for work and history lookup.

---

## 2. Product And UI Assessment

### Is `Show cancelled` still necessary?

As a primary toolbar button: no.

Reason:

- ConnLab's product model is project lifecycle, not archive management.
- The daily Projects screen should prioritize work in motion and projects likely to start.
- The operational states users care about should remain available as business-readable views:

```text
On-going / Planning / Completed / All
```

- `Stopped` projects are mostly lookup/history. They are not a daily work queue and should sit under the broader `Completed` lookup view.
- A primary `Show cancelled` checkbox visually over-emphasizes historical cleanup and makes stopped records look like a normal work-scope toggle.

### Should `Stopped` be a Project view option?

No.

`Stopped` is not an operational queue. It is one terminal/completed outcome, similar to future `Passed` or `Failed` result states, so it should be visible in the row `Status` column under `Completed` and `All`, not as a separate macro view.

### How should users find stopped projects?

V1 should use one compact Project view selector, not a broad advanced filter system and not a second lifecycle filter. Stopped records are found through `Completed` or `All`, with `Status` showing `Stopped`.

Preferred UI:

```text
[On-going ▼]

Footer:
Showing 1-20 of 20 On-going projects
```

Placement:

- as a compact unlabeled dropdown near the search/filter tools,
- no separate visible `Lifecycle` label,
- no counts inside the dropdown options,
- Project ID sorting stays scoped to the table result set and does not become a broad filter builder,
- result counts appear in the table footer,
- no persistent hidden-count note,
- same-session return from Workbench restores the user's current Project view state.

Specific business readiness facts such as `Matrix Needed`, `Ready to Test`, and `Folder Blocked` remain visible in the table `Status` column.

The existing disabled advanced `Filter` button should not be implemented as part of TASK_317E. It may remain disabled or be handled by a future dedicated filter task. TASK_317E must replace `Show cancelled`, not create a generic column/value filter builder.

Default:

```text
On-going
```

Completed:

- completed projects remain accessible through the `Completed` Project view.
- all historical records remain accessible through `All`.

---

## 3. Backend Design

### 3.1 User-Facing Status Mapping

Keep storage compatibility:

```python
ProjectStatus.CANCELLED == "cancelled"
```

Expose UI/read-model label:

```text
Stopped
```

No DB-wide rename is required in TASK_317E.

### 3.2 Delete Preview Service

Create a backend application service, for example:

```python
TemporaryProjectDeleteGuardService.preview(project_id: str) -> TemporaryProjectDeletePreview
```

DTO:

```python
@dataclass(frozen=True, slots=True)
class TemporaryProjectDeletePreview:
    project_id: str
    can_delete: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    recommended_action: Literal["delete", "stop"]
```

Guard checks:

- project exists,
- project has no registered LTR/DL,
- project status is not `cancelled`,
- project has no active Confirmed Matrix,
- project has no official workspace or formal project folder,
- project has no ConnLab-owned temporary workspace or temporary project folder in V1,
- project has no project folder record,
- project has no project-scoped file assets,
- project has no ProjectOutputRecord,
- project has no request material collection that represents formal submitted-material handling,
- project has no confirmed fee authority,
- project has no future public-drive operation record if such a repository exists.

Guard meaning:

- Formal or controlled project artifacts always block deletion and should recommend `stop`. These include registered LTR/DL, active Confirmed Matrix, official workspace/folder, project-scoped file assets, ProjectOutputRecord, confirmed fee/generated output, submitted-material/package records, and public-drive operation records.
- Temporary-only planning material also blocks deletion in V1 if it has already created a ConnLab-owned temporary workspace/folder or file-backed temporary drafts. The conservative V1 behavior is to ask the operator to use `Stop project`, or to defer safe temporary-material cleanup to a later approved task.

Use repository count/existence methods. Do not inspect frontend state.

### 3.3 Delete Execution

Endpoint:

```http
DELETE /api/projects/{project_id}/temporary
```

Execution rules:

- call preview first,
- refuse with blockers if `can_delete` is false,
- delete only ConnLab-owned safe temporary records when no formal or V1 temporary workspace/file-backed blockers exist,
- delete project temporary context,
- delete temporary-only planning drafts only if they are database-only, have no confirmed authority, no formal output lineage, and no file-backed workspace/material side effects,
- delete project row last,
- use one transaction,
- do not delete files on disk,
- do not mutate public-drive or LTR workbook.

If existing repositories lack safe delete methods, add narrow methods only for required temporary records.

### 3.4 Stop Execution

Endpoint:

```http
POST /api/projects/{project_id}/stop
```

V1 may implement:

```python
project.status = ProjectStatus.CANCELLED
```

Response should expose user-facing:

```text
status_label = "Stopped"
```

Request should accept an optional operator-facing stop reason. If reason/operator audit can reuse existing cleanup audit records safely, do so. If not, document a follow-up lifecycle event/audit task rather than adding a broad event system here, and do not claim full audit coverage in response copy or documentation.

---

## 4. Frontend Design

### 4.1 Projects Registry

Remove:

- `Show cancelled`,
- `N cancelled projects hidden`,
- empty state that says `Enable "Show cancelled"...`.

Add a single Project view state:

```ts
type RegistryView =
  | "all"
  | "planning"
  | "completed"
  | "ongoing";
```

Recommended labels:

```text
On-going
Planning
Completed
All
```

This is not the advanced `Filter` feature. Keep the broad `Filter` affordance disabled unless a separate approved task implements it.

Default:

```ts
ongoing
```

Filtering:

- `all`: all registry rows.
- `planning`: active temporary no-LTR rows.
- `completed`: completed/closed/failed/stopped rows.
- `ongoing`: active registered DL/LTR rows that are not completed or stopped.
- `Matrix Needed`, `Ready to Test`, `Folder Blocked`, and `Stopped` are status labels inside rows, not Project view filters.

View behavior:

- The old top queue pill bar is removed.
- The visible `Lifecycle` label is removed.
- Selector options show view names only.
- Project ID sort toggles ascending/descending order for registered DL/LTR IDs and temporary TMP IDs.
- The table footer shows the current selected view count.
- Returning from Workbench restores the user's selected Project view, search text, sort direction, and page number within the same browser session.
- Stopped rows never classify into Planning or On-going views. They appear under Completed/All with Status `Stopped`, and detailed readiness labels stay in the Status column.

### 4.2 Status Copy

Replace user-visible `Cancelled` with:

```text
Stopped
```

Do not change internal enum strings in this task.

### 4.3 Workbench Lifecycle Area

Temporary Planning mode should show a low-priority lifecycle area:

```text
Project lifecycle
Stop project
Delete temporary project
```

Delete button:

- enabled only if backend preview says `can_delete`,
- disabled with blocker reasons otherwise,
- requires confirmation.

Stop button:

- available for active projects where stopping is allowed,
- requires confirmation,
- says the project record will be kept.

Registered or artifact-bearing Workbench states:

- expose `Stop project` as a low-priority lifecycle entry,
- do not expose `Delete temporary project`,
- preserve LTR/DL, Matrix, folder, file asset, output, and request-material records.

Stopped mode:

- show review-only summary,
- no Matrix/Fee planning actions,
- no Convert to Formal Project,
- no execution/package active actions.

---

## 5. Tests

### Backend Unit Tests

Add tests for delete guard:

- safe temporary no-LTR project can delete,
- registered LTR project cannot delete,
- active Confirmed Matrix blocks delete,
- official workspace/folder blocks delete,
- ProjectOutputRecord blocks delete,
- FileAsset records block delete,
- stopped project cannot delete again and recommends stop/review,
- stop service maps to internal `cancelled`.

### Backend Integration Tests

Add API tests:

- `GET /api/projects/{id}/delete-preview`
- `DELETE /api/projects/{id}/temporary`
- `POST /api/projects/{id}/stop`

### Frontend Tests

Add or update:

- Projects page no longer contains `Show cancelled`,
- Projects page contains the compact Project view selector, Project ID sort, and footer count,
- stopped user-facing copy appears instead of Cancelled,
- stopped rows are hidden by default,
- Completed view can show stopped rows with Status `Stopped`,
- Workbench temporary delete lifecycle area appears for temporary projects,
- stopped no-LTR Workbench remains review-only.

---

## 6. Risks And Controls

Risk: accidental deletion of meaningful project history.

Control:

- backend guard is authoritative,
- delete only no-LTR temporary projects with no formal artifacts,
- confirmation required,
- no filesystem/public-drive deletion in V1.

Risk: confusing stopped vs completed.

Control:

- keep stopped visible as a Status value inside `Completed` and `All`,
- use copy that explains stopped means work will not continue.

Risk: scope creep into full advanced filters.

Control:

- implement only the compact Project view selector needed to replace `Show cancelled`,
- do not add arbitrary column/value filter builder.

---

## 7. Validation Plan

Backend:

```powershell
py -m pytest tests\unit\test_temporary_project_delete_guard_service.py tests\integration\test_temporary_project_lifecycle_api.py
```

Frontend/static:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py
cd frontend
npm test -- --run ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors --watch=false
npm run build
```

Manual smoke:

1. Open `/projects`.
2. Confirm `Show cancelled` is gone.
3. Confirm stopped projects are not shown in the default `On-going` view.
4. Use the Project view selector to show `Completed`, then confirm stopped rows appear with Status `Stopped`.
5. Open active temporary project and inspect lifecycle actions.
6. Delete a safe mistaken temporary project.
7. Confirm formal/artifact-bearing project delete is blocked.
8. Stop a project and confirm it leaves the `On-going` view and appears under `Completed`/`All` with Status `Stopped`.

---

## 8. Completion Point

Implementation is complete and ready for review or merge-preparation checks.

Do not enter TASK_319.
