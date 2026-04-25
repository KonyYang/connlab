# TASK 011 — Folder Generation Preview

## Goal

Preview project folder creation without writing files.

## Scope

- Template scanning.
- Placeholder replacement in preview.
- Conflict detection.

## Requirements

- Add `backend/modules/folder/folder_template_service.py`.
- Input: project, template path, target root.
- Output: FolderPlan with directories/files to create/copy.
- Detect existing target folder.
- Replace placeholders in folder/file names.

## Tests

- Preview simple template.
- Placeholder replacement works.
- Existing target path reports conflict.

## Out of Scope

- Do not actually copy files in this task.

## Acceptance Criteria

- API/service can show what would be created before generation.
