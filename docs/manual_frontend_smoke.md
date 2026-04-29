# Manual Frontend Smoke Checklist

This file is retained for compatibility. The current Phase 5 checklist is:

```text
docs\frontend_smoke_checklist.md
```

Use the current checklist after starting the backend and frontend dev servers.

## Startup

1. From repository root, run `py -m uvicorn backend.api.main:app --reload`.
2. From `frontend/`, run `npm run dev`.
3. Open the Vite URL and confirm `/projects` loads.

## MVP Flow

1. Create a project with product name, requestor, and optional business unit. Leave project number empty to confirm it is optional.
2. Open the created project workbench and confirm the project status is visible.
3. Upload a DOCX application form.
4. Run precheck and confirm status plus issue list are visible.
5. Register an LTR number and confirm latest LTR status is visible.
6. Enter a template path and target root, then preview the project folder.
7. If the preview has no conflict, generate the folder and confirm generated path count is visible.

## Expected Scope

- The flow covers only Project -> Application form -> Precheck -> LTR -> Folder.
- Matrix, Report, AI review, permissions, and packaging are intentionally absent.
