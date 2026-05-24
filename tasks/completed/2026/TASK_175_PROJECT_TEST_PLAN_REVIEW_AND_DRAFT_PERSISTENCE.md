# TASK_175 Project Test Plan Review And Draft Persistence

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`
- Current active task in board at creation time: `none; TASK_174 complete`
- Why this task is allowed now: `TASK_174_PROJECT_TEST_PLAN_MATRIX_BASELINE` is complete and the user approved the next controlled task.
- Implementation gate: this task file defines the implementation scope; do not write implementation code until the user explicitly approves this task file, for example `批准执行 TASK_175`.

---

## 1. Purpose

Persist a Project-stage test-plan draft snapshot created from the TASK_174 Matrix preview, so ConnLab has a durable structured planning object for later Section 2, test record, fee evaluation, status tracking, and report dataset tasks.

The goal is not to implement a full Matrix module. The goal is to save and retrieve an operator-reviewable `ProjectTestPlan` draft without depending on New Project `ApplicationDraft` as live data.

---

## 2. Business Context

After TASK_174, ConnLab can preview Matrix-like product specification tables and extract test groups/steps. That preview is transient. The next controlled step is to preserve the reviewed or review-ready result as Project Management data.

Target business behavior:

1. Operator runs Matrix preview from a product specification.
2. ConnLab returns extracted groups and steps.
3. Operator can later review/correct the extracted structure.
4. ConnLab stores the test plan draft as Project-stage data linked to the Project and source document.
5. Later tasks read this draft instead of re-parsing Word/PDF files or reading New Project draft data.

---

## 3. Boundary With New Project Data

Rules:

- `ProjectTestPlanDraft` must attach to `Project`.
- It may store source traceability:
  - `source_case_id`
  - `source_draft_id`
  - `source_application_asset_id`
  - `source_spec_asset_id`
  - `source_document_path`
- These source fields are for audit/traceability only.
- No service in TASK_175 may mutate `IntakeCase`, `ApplicationDraft`, application-form source files, Section 2, test record files, fee files, or reports.
- Downstream flows should read Project-stage test-plan data, not live New Project draft data.

---

## 4. Scope

In scope:

- Add a narrow persistence model for Project test-plan draft snapshots.
- Store structured test-plan preview/edit payload as JSON.
- Support draft lifecycle status:
  - `draft`
  - `reviewed`
  - `superseded`
- Support create/update/read/list APIs for Project test-plan drafts.
- Preserve source traceability and version.
- Enforce Project ownership:
  - a draft must reference an existing Project.
  - draft reads are scoped by `project_id`.
- Add tests for repository, service, and API behavior.

Out of scope:

- No frontend/UI review page.
- No Section 2 preview or write-back.
- No test record template generation.
- No fee evaluation generation.
- No report generation.
- No AI interpretation.
- No PDF extraction.
- No `.doc` conversion.
- No normalized Matrix execution model beyond the JSON draft snapshot.
- No mutation of product specification, application form, public-drive files, or project folders.

---

## 5. Data Model Plan

Use a SQLite-backed draft snapshot table first. Do not normalize every group/step yet.

Proposed table:

```text
project_test_plan_drafts
  draft_id: str primary key
  project_id: str
  source_document_path: str
  source_document_name: str
  source_format: str
  source_asset_id: str | null
  source_case_id: str | null
  source_draft_id: str | null
  status: str
  version: int
  payload_json: text
  created_at: str
  updated_at: str
  reviewed_at: str | null
```

Payload shape should match TASK_174 preview response closely:

```json
{
  "groups": [
    {
      "group_key": "group_1",
      "group_label": "Group 1",
      "source_table_index": 21,
      "extraction_status": "extracted",
      "steps": []
    }
  ],
  "warnings": [],
  "blockers": []
}
```

Rationale:

- JSON snapshot is sufficient for early review and downstream preview tasks.
- It avoids premature normalized Matrix schema design.
- A later task can normalize after real review/edit needs are proven.

---

## 6. Application Service Plan

Expected service:

```text
ProjectTestPlanDraftService
```

Responsibilities:

- create a draft from a preview/edit payload;
- list drafts by project;
- get one draft by project and draft id;
- update draft payload/status;
- mark prior active drafts as `superseded` only when creating a new active version for the same project/source;
- reject unknown project ids;
- reject invalid status transitions.

Important first-version rule:

- Keep one latest active draft per `project_id + source_document_path`.
- Preserve older drafts as `superseded`, not deleted.

---

## 7. API Plan

Proposed endpoints:

```text
POST /api/projects/{project_id}/test-plan/drafts
GET  /api/projects/{project_id}/test-plan/drafts
GET  /api/projects/{project_id}/test-plan/drafts/{draft_id}
PUT  /api/projects/{project_id}/test-plan/drafts/{draft_id}
```

Create request:

```json
{
  "source_document_path": "C:\\...",
  "source_document_name": "PRODSPEC ... .docx",
  "source_format": ".docx",
  "source_asset_id": null,
  "source_case_id": null,
  "source_draft_id": null,
  "status": "draft",
  "payload": {
    "groups": [],
    "warnings": [],
    "blockers": []
  }
}
```

Update request:

```json
{
  "status": "reviewed",
  "payload": {
    "groups": [],
    "warnings": [],
    "blockers": []
  }
}
```

Response:

```json
{
  "draft_id": "string",
  "project_id": "string",
  "version": 1,
  "status": "draft",
  "source_document_path": "C:\\...",
  "payload": {},
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "reviewed_at": null
}
```

---

## 8. Expected Files

Backend:

- `backend/domain/enums.py`
  - add `ProjectTestPlanDraftStatus` only if status enum belongs in domain.

- `backend/domain/models.py`
  - add `ProjectTestPlanDraft` dataclass if consistent with current domain style.

- `backend/infrastructure/storage/models.py`
  - add SQLAlchemy row model.

- `backend/infrastructure/storage/repositories/project_test_plan.py`
  - add repository for draft records.

- `backend/application/project_test_plan_draft_service.py`
  - add application use-case service.

- `backend/api/routes_project_test_plan_drafts.py`
  - add thin API route.

- `backend/api/dependencies.py`
  - add service wiring.

- `backend/api/main.py`
  - include route.

Tests:

- `tests/unit/test_project_test_plan_draft_service.py`
- `tests/integration/test_project_test_plan_draft_api.py`
- repository coverage can be included in the integration test or a dedicated repository test if needed.

Docs:

- update `docs/task_board.md` after implementation and validation.

---

## 9. Validation Plan

Targeted tests:

```powershell
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

Related smoke:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

Optional broader backend run:

```powershell
py -m pytest tests\unit tests\integration -q
```

Known current repository note:

- Full test suite currently has 6 historical failures unrelated to Phase 11 test-plan work, recorded in TASK_174 completion notes.

---

## 10. Acceptance Criteria

- A Project test-plan draft can be created for an existing Project.
- Creating a new draft for the same `project_id + source_document_path` supersedes the prior active draft.
- Drafts can be listed by Project.
- A draft can be read by `project_id + draft_id`.
- A draft can be updated from `draft` to `reviewed`.
- Unknown Project IDs are rejected.
- Cross-project draft reads are rejected.
- Payload JSON preserves groups, steps, warnings, blockers, and source traceability.
- No New Project `ApplicationDraft` data is mutated.
- No Office files are written.
- No Section 2, test record, fee, or report output is generated.
- Targeted tests pass.
- `docs/task_board.md` is updated after implementation and validation.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- summarize validation;
- stop;
- do not start `TASK_176` without explicit user approval.

---

## 12. Completion Notes

Implemented:

- Added `ProjectTestPlanDraftStatus` and `ProjectTestPlanDraft` domain types.
- Added SQLite-backed `project_test_plan_drafts` table and repository.
- Added `ProjectTestPlanDraftService` for Project-scoped draft create/list/read/update.
- Added active-draft control:
  - creating a new draft for the same `project_id + source_document_path` supersedes prior `draft`/`reviewed` records;
  - prior drafts are preserved as `superseded`, not deleted.
- Added Project-scoped APIs:
  - `POST /api/projects/{project_id}/test-plan/drafts`
  - `GET /api/projects/{project_id}/test-plan/drafts`
  - `GET /api/projects/{project_id}/test-plan/drafts/{draft_id}`
  - `PUT /api/projects/{project_id}/test-plan/drafts/{draft_id}`
- Preserved New Project boundary:
  - no `IntakeCase` mutation;
  - no `ApplicationDraft` mutation;
  - no Office file writes;
  - no Section 2/test record/fee/report output.

Validation:

- `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q` passed, 7 passed.
- `py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q` passed, 7 passed.
