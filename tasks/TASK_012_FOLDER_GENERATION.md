# TASK 012 — Folder Generation Execution

## Goal

Generate project folders from template after preview.

## Scope

- Copy template to target.
- Replace placeholders in paths.
- Copy original application form into request folder if available.
- Persist ProjectFolderRecord.
- Update Project status to FOLDER_CREATED.

## Requirements

- Use safe copy; never overwrite existing target folder.
- Return generated file/folder list.
- Log operations.
- Add API route:
  - `POST /api/projects/{project_id}/folder/preview`
  - `POST /api/projects/{project_id}/folder/generate`

## Tests

- Generate from temp template.
- Refuse overwrite.
- Persist folder record.

## Out of Scope

- No placeholder replacement inside Word/Excel contents yet.
- No report generation.

## Acceptance Criteria

- Folder generation completes offline and records target path.
