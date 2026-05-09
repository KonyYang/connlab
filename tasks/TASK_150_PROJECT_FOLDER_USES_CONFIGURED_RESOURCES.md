# TASK_150 Project Folder Uses Configured Resources

> Status: proposed
> Created: 2026-05-09
> Phase: Phase 10E - External resource settings and LTR workbook authority

---

## 1. Purpose

Connect Project Workbench folder creation to configured resources instead of asking the operator to type template and target paths every time.

`TASK_148` moved folder creation into Project Workbench, but the panel still accepts raw `template_path` and `target_root`. That is useful for early wiring, but not acceptable for non-programmer lab users.

---

## 2. Dependencies

Depends on `TASK_149` if `project_output_root` and Settings UI are added there.

---

## 3. Scope

In scope:

- Use configured `project_folder_template` as the default folder template.
- Use configured `project_output_root` as the default target root.
- Keep optional override fields only if the active task explicitly decides they are needed for debugging.
- Show configured resource validation state near folder creation.
- Block folder preview/generation when required configured resources are missing or invalid.
- Preserve explicit preview-before-write behavior.

Out of scope:

- No native folder picker.
- No overwrite or conflict resolution strategy.
- No evidence placement changes except preserving existing behavior.
- No LTR workbook changes.

---

## 4. UX Plan

Workbench folder creation should show:

- LTR number context.
- Template source label from Settings.
- Output root label from Settings.
- `Preview folder` action.
- `Create folder` action only after clear preview.

The operator should not need to understand full filesystem paths during the normal path, but the path should remain visible for traceability.

---

## 5. Backend Plan

Preferred path:

- Add or reuse a read model that returns active configured resources needed by folder creation.
- Keep existing `POST /folder/preview` and `POST /folder/generate` contracts stable if possible.
- If the frontend still sends paths, it should send values resolved from Settings, not user-typed values.

Future-compatible option:

- Add `POST /api/projects/{project_id}/folder/preview-configured`
- Add `POST /api/projects/{project_id}/folder/generate-configured`

Only choose this option if it reduces duplication and keeps the API safer.

---

## 6. Tests And Validation

Expected validation:

```powershell
py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_external_resource_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or folder or settings"
cd frontend
npm run build
```

Manual smoke:

1. Configure local project folder template and output root in Settings.
2. Apply LTR from New Project.
3. Open Project Workbench.
4. Confirm folder panel uses configured paths.
5. Preview and create folder without retyping paths.

---

## 7. Acceptance Criteria

- Normal Workbench folder creation uses Settings-managed resources.
- Missing/invalid Settings resources block folder preview/generation with clear copy.
- Raw path entry is no longer the normal business path.
- Existing conflict blocking still works.

