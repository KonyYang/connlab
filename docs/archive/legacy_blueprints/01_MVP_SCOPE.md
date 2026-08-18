# MVP Scope

## In Scope

### 1. Project Registry

- Create project manually or from parsed application form.
- Store project status and root folder path.
- Search/list projects.

### 2. Application Form Intake

- Import `.docx` application form.
- Extract key fields.
- Extract sample information rows.
- Store original file as a FileAsset.

### 3. Precheck

- Run deterministic rules.
- Produce PrecheckIssue records.
- Allow user to mark warning/error as confirmed/resolved.
- Export or display precheck summary.

### 4. LTR

- Register LTR number.
- Bind LTR to Project.
- Query LTR history.

### 5. Project Folder

- Preview folder tree from template.
- Generate project folder.
- Copy application form into request folder.
- Save ProjectFolderRecord.

## Out of Scope for MVP

- Matrix generation.
- Test Record generation.
- Excel result ingestion.
- Image asset auto-classification.
- Report generation.
- AI review.
- Multi-user permissions.
- LAN deployment.

## MVP Success Criteria

A non-programmer lab engineer can complete this workflow offline on Windows:

```text
Import application form -> see precheck issues -> confirm project -> register LTR -> generate project folder
```
