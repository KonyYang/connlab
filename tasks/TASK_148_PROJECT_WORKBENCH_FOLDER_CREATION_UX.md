# TASK_148 Project Workbench Folder Creation UX

> Status: complete
> Created: 2026-05-09
> Phase: Phase 10D - New Project completion handoff and Project workspace boundary

---

## 1. Why This Task Is Allowed

`TASK_147_LTR_APPLICATION_DUPLICATE_AND_SUFFIX_GUARDS` is complete. The task board currently recommends the next controlled Phase 10D boundary: move the initial project folder creation UX into Project Workbench now that New Project only applies the LTR number and hands off.

This task is allowed because it stays inside the approved MVP mainline:

- New Project remains the intake, application editing, and LTR application surface.
- Project Workbench becomes the surface for project workspace operations after LTR registration.
- Folder generation already exists in backend APIs; this task wires the correct Workbench UX boundary without introducing future-scope modules.

---

## 2. Goal

Make Project Workbench the operator-facing place to preview and create the initial project folder for an LTR-registered project.

After New Project applies an LTR number and routes to Project Workbench, the operator should be able to:

1. See that the project has an LTR number but no project folder yet.
2. Preview the folder creation plan.
3. Generate the project folder only when the preview has no conflicts.
4. See the generated folder state after success.
5. Continue with source material / evidence placement after folder creation.

---

## 3. Current Code Reality

Observed code state:

- `backend/api/routes_folder.py` already exposes:
  - `POST /api/projects/{project_id}/folder/preview`
  - `POST /api/projects/{project_id}/folder/generate`
- `backend/application/folder_service.py` already:
  - previews folder plans
  - blocks conflicts
  - creates `ProjectFolderRecord`
  - moves project status to `folder_created`
- `frontend/src/api/client.ts` already has:
  - `previewFolder`
  - `generateFolder`
  - `FolderRequest`
  - `FolderPlan`
  - `FolderGeneration`
- `frontend/src/pages/ProjectWorkbenchPage.tsx` currently shows folder status and evidence placement only.
- `frontend/src/components/workflow/FolderActionPanel.tsx` still exists from older workflow UI, but `TASK_100` intentionally removed creation-stage controls from Workbench when New Project still created the initial folder.

`TASK_146` changed the product boundary: New Project now applies LTR only. Therefore Workbench needs a narrow folder-creation capability again, but not the old full creation workflow.

---

## 4. Scope

Implement only the Project Workbench initial folder creation UX.

In scope:

- Add a Workbench folder creation panel for projects whose LTR is registered but folder is not created.
- Use the existing folder preview and generation API paths.
- Require preview before generation.
- Keep generation disabled when preview reports conflicts.
- Refresh project state after successful generation.
- Show generated folder path/status after success.
- Keep evidence placement disabled until folder exists, then available after folder creation.
- Keep New Project completion as LTR-only.
- Add/update tests for the Workbench folder creation boundary.

Out of scope:

- No Matrix, Test Record, Report Generation, AI review, email sending, permissions, LAN deployment, or Outlook inbox auto-scan.
- No arbitrary file manager operations, rename/delete/move folder actions, or overwrite strategy.
- No direct frontend filesystem access.
- No direct Office or SQLite access from frontend.
- No reintroduction of application form upload, precheck, or local LTR commit controls in Project Workbench.
- No OS-level "open folder" action unless an existing safe backend/desktop-shell capability already supports it. Browser-only UI should display the generated path instead.

---

## 5. UX Design

Project Workbench should remain a compact operational page, not a second New Project flow.

Proposed Workbench states:

- `ltr_registered`, no folder:
  - Status grid says `LTR Number registered: Yes (...)`
  - `Project folder: Not created`
  - Show a focused `Create project folder` panel.
  - Panel contains template path, target root, and LTR number context.
  - The LTR number should default from the latest registered LTR and should not require retyping in the normal path.
- folder preview ready:
  - Show the target project folder path.
  - Show concise folder/file preview items.
  - Show conflicts inline and keep `Create folder` disabled when conflicts exist.
- `folder_created`:
  - Show `Project folder: Created`.
  - Show generated or recorded folder path when available.
  - Hide the creation controls and enable evidence placement.

Button language:

- Preview action: `Preview folder`
- Write action: `Create folder`
- Evidence action remains separate: `Preview evidence placement` / `Place evidence`

This keeps the Workbench focused on project workspace setup and avoids making the page feel like another intake form.

---

## 6. Data And API Design

Preferred implementation path:

- Reuse existing `previewFolder(projectId, input)` and `generateFolder(projectId, input)` client calls.
- Add only the smallest missing read model if the UI cannot recover the persisted folder path after reload.

Potential new read-only API if needed:

```text
GET /api/projects/{project_id}/folder/latest
```

Response:

```json
{
  "folder_id": "string",
  "project_id": "string",
  "project_folder_path": "string",
  "created_on": "YYYY-MM-DD"
}
```

This endpoint is only for displaying persisted folder state after reload. It must not create or mutate folders.

If existing evidence preview or project detail already exposes enough persisted folder information safely, this new endpoint can be skipped.

---

## 7. Frontend Design And File-Level Plan

Expected frontend files:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`
  - Owns Workbench state loading and refresh.
  - Calls folder preview/generate APIs through `frontend/src/api/client.ts`.
  - Keeps route-level logic thin.
- `frontend/src/features/project-workbench/ProjectFolderCreationPanel.tsx` or a similarly scoped component
  - New focused Workbench component for initial folder creation.
  - Avoids growing `ProjectWorkbenchPage.tsx` with large JSX blocks.
- `frontend/src/workbench.css`
  - Add restrained Workbench panel styles if existing classes are insufficient.
- `frontend/src/api/client.ts`
  - Add `getLatestProjectFolder` only if the persisted folder path cannot be loaded through existing APIs.

Existing `frontend/src/components/workflow/FolderActionPanel.tsx` should not be reintroduced wholesale if it carries old multi-step workflow assumptions. It can be used as a reference, but the Workbench should get a narrow folder-only component.

---

## 8. Backend Design And File-Level Plan

Expected backend files only if a folder-state read endpoint is needed:

- `backend/api/routes_folder.py`
  - Add `GET /latest` response DTO.
- `backend/application/folder_service.py`
  - Add a read-only method to fetch the latest folder record for a project if repository support exists or can be added narrowly.
- repository implementation file
  - Add a latest-folder lookup only if no equivalent exists.
- tests under `tests/integration` or `tests/unit`
  - Cover latest-folder read behavior if added.

No backend write-path redesign is planned. Existing preview/generate lifecycle guards should remain authoritative.

---

## 9. Tests And Validation Plan

Backend validation:

```powershell
py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q
```

Frontend/static validation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder"
```

Frontend build:

```powershell
cd frontend
npm run build
```

If a new folder latest endpoint is added, include targeted tests for:

- latest folder missing before generation
- latest folder returned after generation
- unknown project returns 404

Manual smoke expectation:

1. Import or create a New Project package.
2. Apply LTR number.
3. Confirm the app routes to Project Workbench.
4. Confirm Workbench shows LTR registered and folder not created.
5. Preview folder with a valid template and target root.
6. Confirm conflict preview blocks folder creation.
7. Confirm clear preview allows `Create folder`.
8. Confirm successful creation refreshes status to folder created.
9. Confirm evidence placement becomes available after folder creation.

---

## 10. Risks

- Workbench currently has tests asserting folder creation controls are absent because `TASK_100` removed them. Those tests must be updated to the new `TASK_146`/`TASK_148` boundary without reintroducing old application/precheck/LTR controls.
- If the UI needs persisted folder path after reload, the backend may need a narrow read-only endpoint. This should be kept separate from mutation logic.
- Browser UI cannot reliably open local Windows folders without a desktop shell or explicit backend action. This task should avoid misleading "open folder" behavior unless a safe existing route already exists.
- Reusing the old `FolderActionPanel` too broadly could accidentally bring back old workflow assumptions. Prefer a focused component.

---

## 11. Acceptance Criteria

- Project Workbench can preview and create the initial project folder for an LTR-registered project.
- Folder generation remains blocked when preview has conflicts.
- After successful folder generation, project state refreshes to folder-created UI.
- Evidence placement remains unavailable before folder creation and available after folder creation.
- New Project remains LTR-only and does not create folders.
- Workbench does not reintroduce application upload, precheck run, or LTR commit controls.
- Targeted backend/frontend tests pass.
- `docs/task_board.md` is updated after implementation with validation results.

---

## 12. Approval Gate

The user approved implementation with:

```text
批准执行 TASK_148
```

---

## 13. Completion Notes

Implemented:

- Project Workbench now exposes a focused `ProjectFolderCreationPanel` for LTR-registered projects without a folder.
- The panel previews folder generation, blocks creation on conflicts, creates the folder through the existing API, refreshes Workbench state, and then enables evidence placement.
- New Project remains LTR-only; folder generation is not moved back into New Project.
- Backend folder API now exposes a read-only `GET /api/projects/{project_id}/folder/latest` endpoint so Workbench can show the recorded folder path after reload.
- Workbench does not reintroduce application upload, precheck, or LTR commit controls.

Validation:

- `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q`: passed, 4 passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder"`: passed, 4 passed, 52 deselected.
- `py -m pytest tests\integration\test_new_project_completion_api.py -q`: passed, 4 passed.
- `npm run build` from `frontend`: passed.
- `git diff --check`: passed with CRLF working-copy warnings only.

Known non-TASK_148 validation note:

- Full `py -m pytest tests\integration\test_new_project_completion_api.py tests\unit\test_frontend_shell_files.py -q` still has 4 existing static frontend assertion failures in Intake/Precheck/Draft historical expectations. The failures are outside the TASK_148 Workbench/folder scope.
