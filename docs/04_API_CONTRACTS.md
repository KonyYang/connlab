# MVP API Contracts

These contracts guide implementation. Exact route names may evolve, but keep route bodies thin.

## Project

### POST /api/projects

Create project manually.

Request:

```json
{
  "dl_number": "DL-2025-09-054",
  "title": "EK550A Qualification",
  "product_name": "EK550",
  "requestor": "Fu Yang",
  "business_unit": "Power Solutions",
  "project_no": null
}
```

Response:

```json
{"project_id": "uuid", "status": "DRAFT"}
```

`project_no` is optional metadata from an application form. Before LTR registration, continuation uses `project_id`, `intake_package_id`, and `intake_case_id`; after registration, lab operations and folder naming should use `DL_NUMBER` / `ltr_number`.

### GET /api/projects

List projects with search/status filters.

### GET /api/projects/{project_id}

Return project detail.

## Intake

### POST /api/intake/application-form

Upload or register application form file and parse fields.

Response includes extracted ApplicationForm and SampleInfo rows.

## Precheck

### POST /api/precheck/{application_form_id}/run

Runs deterministic precheck.

Response:

```json
{
  "result_id": "uuid",
  "status": "WARNING",
  "issues": []
}
```

### PATCH /api/precheck/issues/{issue_id}/resolve

Mark issue as resolved/confirmed.

## LTR

### POST /api/projects/{project_id}/ltr

Register LTR number for a project.

## Folder

### POST /api/projects/{project_id}/folder/preview

Preview generated folder plan.

### POST /api/projects/{project_id}/folder/generate

Generate folder from template.
