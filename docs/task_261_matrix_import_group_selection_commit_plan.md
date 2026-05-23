# TASK_261 Matrix Import Group Selection Commit Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` (planned, awaiting approval)
- Why this task is allowed now:
  - `docs/task_board.md` shows `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` complete.
  - Board now points to `TASK_261` as the current planned task.
  - `docs/matrix_authority_to_test_record_smoke_flow_plan.md` recommends `TASK_261` as the next controlled task.

This document is a plan only. No implementation should start until user approval.

Model fit:

- Recommended model: `GPT-5.3-codex`, reasoning `medium`.
- Why: bounded backend orchestration + typed API + deterministic validation + focused tests.

## 1) Goal

Create a backend import-commit boundary that takes a parsed Matrix preview plus selected group keys, persists the full immutable Source Matrix, and creates a project-specific selected-only `ProjectMatrixDraft`.

The goal is workflow correctness:

```text
Import Matrix -> Group Selection -> SourceMatrix + selected ProjectMatrixDraft
```

Contract intent:

- Source lineage remains full and immutable.
- Draft editing surface remains selected-only.
- Repeated same-input commit is idempotent and returns `commit_status=reused`.

Preview input strategy for TASK_261:

- Implement `preview_payload` mode only in this task.
- `preview_token` mode is deferred and should not be part of TASK_261 acceptance.

## 2) File-Level Change Plan

1. Application service
   - Add `backend/application/matrix_import_commit_service.py`.
   - Define command/input:
     - `project_id`
     - `selected_group_keys`
     - `preview_payload` (untrusted input, strict structural validation)
     - optional source metadata from preview context
   - Inject:
     - project store
     - Source Matrix import persistence boundary
     - Project Matrix Draft persistence boundary
   - Orchestrate:
     - validate project and payload/group contract
     - normalize selected keys (trim only, case-sensitive)
     - detect duplicate selected keys and reject with typed 422
     - persist full Source Matrix import/snapshot
     - create selected-only project draft through a dedicated selected-only builder path
     - idempotency check: same project + same normalized payload fingerprint + same normalized selected keys -> reuse existing draft and return `commit_status=reused`.

   Selected-only draft construction rule (explicit):

   - Do not call `create_from_source_import` directly, because current draft service builds full-group draft with `is_selected` flags.
   - Add a dedicated selected-only draft creation path for TASK_261:
     - groups: only selected groups are persisted
     - cells: only selected-group cells are persisted
     - rows: keep all non-group-specific rows needed for editing

2. API route
   - Add `backend/api/routes_matrix_import_commit.py`.
   - Route:
     - `POST /api/projects/{project_id}/matrix-import/commit`
   - Request body:
     - `selected_group_keys: list[str]`
     - `preview_payload: dict`
   - Response body:
     - `source_import_id`
     - `source_snapshot_id`
     - `project_matrix_draft` aggregate
     - `selected_group_keys_committed`
     - `commit_status: "created" | "reused"`
   - Route must call application service only.
   - Error mapping:
     - `404`: project not found
     - `409`: deterministic conflict where reuse is not possible
     - `422`: empty/unknown/duplicate selected keys, malformed payload contract

3. Dependency wiring
   - Update `backend/api/dependencies.py`:
     - add a provider for `MatrixImportCommitService`
     - reuse existing repositories/services from same request session
   - Update `backend/api/main.py`:
     - include the new import-commit router
   - No frontend UI wiring in this task.

4. Tests
   - Add `tests/unit/test_matrix_import_commit_service.py`.
   - Add `tests/integration/test_matrix_import_group_selection_commit_api.py`.
   - Reuse small in-memory preview payload fixtures.
   - Include at least:
     - selected subset creates selected-only draft
     - full source still stores unselected groups
     - sample quantity survives
     - empty selected groups -> 422
     - unknown selected group -> 422
     - duplicate selected keys -> 422
     - repeated same-input commit -> `commit_status=reused`
     - route does not bypass service
     - selected-only assertion:
       - unselected groups absent from `ProjectMatrixDraft.groups`
       - unselected-group cells absent from `ProjectMatrixDraft.cells`

5. Documentation
   - Mark `tasks/TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT.md` complete after implementation.
   - Update `docs/task_board.md` with deliverables, validation, and next recommended task.

## 3) Transaction Boundary

Preferred behavior: full source import persistence and ProjectMatrixDraft creation should be atomic from the API caller perspective.

Implementation plan must decide the concrete transaction mechanism based on current service/repository boundaries:

- If existing services share the same SQLAlchemy session in dependency wiring, commit both in one request transaction.
- If existing services own separate commit boundaries, refactor only as much as needed to prevent partial source-without-draft or draft-without-source outcomes.

Acceptance requires a rollback test if implementation touches repository transaction behavior.

## 4) Selected Group Semantics

- `selected_group_keys` is required and non-empty.
- Keys are normalized by trimming whitespace.
- Duplicate keys are rejected with 422.
- Selected group ordering in the draft follows source group order, not request order.
- Unselected groups must not appear in `ProjectMatrixDraft.groups` or draft cells.
- Key matching is case-sensitive in this task.

## 5) Source vs Draft Authority

Source Matrix:

- immutable import lineage
- full imported matrix
- all groups
- all rows
- sparse source cells

ProjectMatrixDraft:

- editable project execution projection
- selected groups only
- group-level sample quantity expression
- sparse non-empty draft cells for selected groups only

ConfirmedMatrix remains out of scope for this task.

## 6.1 Idempotency Key

Idempotency fingerprint for this task:

- `project_id`
- canonical hash of normalized `preview_payload`
- normalized `selected_group_keys` sequence

When fingerprint matches a prior successful commit, return existing artifacts with `commit_status=reused`.

Persistence/query design (chosen for TASK_261):

- Use **Option A** with explicit schema support.
- Add dedicated persistence field `task261_commit_fingerprint` on `source_matrix_import_records`.
- Add DB migration and SQLAlchemy model/domain/repository updates for this field.
- Add repository lookup method: find Source Matrix import by `project_id + task261_commit_fingerprint`.
- If matched import exists, resolve existing draft by `project_id + source_import_id` and return reused result.
- Do not overload existing business fields such as warnings/blockers/selected_group_keys for fingerprint storage.

Source snapshot id return design:

- Preferred: adjust SourceMatrix persistence result to return both `import_id` and `snapshot_id`.
- Minimal fallback: persist returns `import_id`, then service performs one repository read `get_snapshot_by_import(import_id)` to retrieve `snapshot_id` for API response.

## 7) Out Of Scope

- Group Selection View UI.
- Matrix Editor layout changes.
- Confirmed Matrix creation.
- Runtime projection consumer changes.
- Test Record preview.
- StepInstance.
- Execution records.
- Evidence/image handling.
- Report, fee, duration, equipment, AI review, LAN, permissions, deployment.

## 8) Implementation Steps

1. Add `MatrixImportCommitService` command/response DTOs and validation helpers.
2. Wire reuse lookup and idempotency behavior.
3. Add route request/response DTOs and error mapping.
4. Add dependency and router registration.
5. Implement unit tests first for validation and idempotency logic.
6. Implement integration tests for API contract and persistence outcome.
7. Run task-specific tests and existing related regression suites.

## 9) Validation Plan

```powershell
py -m pytest tests\unit\test_matrix_import_commit_service.py -q
```

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\integration\test_project_test_plan_preview_api.py -q
```

```powershell
py -m pytest tests\unit\test_source_matrix_persistence_service.py tests\unit\test_project_matrix_draft_persistence_service.py -q
```

## 10) Risks

- Existing `SourceMatrixImportPersistenceService` is currently tied to legacy draft-based flow. Reusing it directly may require an adapter to avoid introducing fake/legacy `draft_id` semantics in this new commit boundary.
- Idempotent reuse may need a lightweight lookup index; if no suitable existing lookup exists, behavior may degrade into conflict-only mode unless a minimal repository query is added.
- Payload-mode fallback increases input attack surface; strict structural validation is mandatory if token flow is not yet available.
- Without the dedicated selected-only builder, implementation will fail acceptance because current draft creation path includes unselected groups.
- Schema migration is now in-scope for TASK_261 due to fingerprint persistence. Migration + repository backward-compatibility tests are required.

## 11) Review Checklist

- Full Source Matrix is persisted.
- ProjectMatrixDraft is selected-only.
- Sample quantity expression survives.
- Unselected source groups remain traceable only through SourceMatrix.
- API route calls application service only.
- Existing preview APIs are unchanged.
- No frontend UI is introduced.
- No ConfirmedMatrix/TestRecord/runtime execution scope is introduced.
- `commit_status` and idempotency behavior are covered by integration tests.
- Fingerprint persistence includes migration, model mapping, repository query test coverage.
