# TASK_149 Settings External Resources UI And Local Paths

> Status: proposed
> Created: 2026-05-09
> Phase: Phase 10E - External resource settings and LTR workbook authority

---

## 1. Purpose

Create the operator-facing Settings page for ConnLab external resource paths.

The current business reality is that several authoritative or shared resources live on a public drive, while each developer or operator may use local substitute paths during development and testing. The UI must let a non-programmer configure and validate those paths without editing environment variables or TOML by hand.

---

## 2. Current Code Reality

Existing backend support:

- `TASK_128` added SQLite-backed external resource records.
- Existing resource types:
  - `ltr_workbook`
  - `application_form_template`
  - `project_folder_template`
  - `standard_record_excel`
  - `equipment_calibration_excel`
- Existing API:
  - `GET /api/external-resources`
  - `PUT /api/external-resources/{resource_type}`
  - `POST /api/external-resources/{resource_type}/validate`

Current gaps:

- Sidebar `Settings` is disabled.
- No Settings route/page exists.
- Browser UI cannot open native file pickers for arbitrary local paths yet, so development phase should support manual path paste.
- Project folder output root is not currently modeled as an external resource type.
- Local machine paths such as workbook backup and lock directories are still only in `connlab.local.toml` / environment settings.

---

## 3. Scope

In scope:

- Enable the Settings navigation route.
- Add a Settings page focused on external resources.
- Add frontend API client methods for listing, saving, and validating external resources.
- Render a table or compact operational list with:
  - resource label
  - current path
  - public/shared or local-machine category
  - active state
  - validation status
  - last checked
  - validation failure reason
  - Save and Validate actions
- Support manual path input and paste.
- Add `project_output_root` as a directory-style external resource if needed by folder generation.
- Clearly label development local paths as substitutes for public-drive paths.

Out of scope:

- No native OS file picker.
- No PyWebView shell integration.
- No LTR workbook write behavior changes.
- No project folder creation behavior changes.
- No server-side centralized settings service.
- No Matrix, Report, AI review, email sending, permissions, or LAN deployment.

---

## 4. Resource Model

Proposed user-facing groups:

Shared/public resources:

- LTR workbook
- Project folder template
- Project output root
- Application form template
- Standard record Excel
- Equipment calibration Excel

Local machine resources:

- LTR workbook backup directory
- LTR workbook lock directory

If local machine resources do not fit the existing external resource registry, this task should document the split and keep them read-only or deferred rather than forcing them into the wrong model.

---

## 5. UX Plan

Settings should feel like an operational configuration page, not a developer console.

Recommended layout:

- Page title: `Settings`
- Section: `External resources`
- Dense rows grouped by `Shared resources` and `Local machine paths`
- Each row exposes a single path field, status badge, and actions.
- Validation copy should be business-readable:
  - `Valid`
  - `Missing`
  - `Invalid Excel structure`
  - `Expected folder`
  - `Expected Excel file`

Development guidance copy should be concise:

```text
Use local paths during development. Switch to public-drive paths before production use.
```

---

## 6. Tests And Validation

Expected validation:

```powershell
py -m pytest tests\integration\test_external_resource_api.py tests\unit\test_external_resource_service.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "settings or external"
cd frontend
npm run build
```

Manual smoke:

1. Open Settings.
2. Paste local development paths for LTR workbook, project folder template, project output root, standard Excel, and equipment Excel.
3. Save each path.
4. Validate each path.
5. Confirm valid/invalid state is visible without reading logs.

---

## 7. Acceptance Criteria

- Settings page is reachable from sidebar.
- External resources can be listed, edited, saved, and validated from UI.
- `project_output_root` is represented or explicitly deferred with a documented reason.
- UI copy distinguishes shared/public resources from local machine paths.
- No workbook write behavior changes occur in this task.
- Task board is updated after implementation.

