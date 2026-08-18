# TASK_321 Project Folder Required Forms Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace old TASK_313 package execution with a preview-first Project Folder `Required forms` generation workflow.

**Architecture:** Add a backend Project Folder Required Forms application service that previews and generates Test Record, Fee Form, and Customer Feedback Form into the local Official project folder. Reuse existing generation capabilities through staging-only ports, add safe final placement under the Official project folder, record generated-output status only after final placement succeeds, and expose the action only through the TASK_320 Required forms detail.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, SQLite repositories, React + TypeScript, Vitest, pytest, existing ConnLab Office gateways/services.

---

## Status

Implemented after explicit user approval. TASK_321 scope is complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Task file: `tasks/TASK_321_PROJECT_FOLDER_REQUIRED_FORMS_GENERATION.md`

## Required Context

Read before implementation:

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_321_PROJECT_FOLDER_REQUIRED_FORMS_GENERATION.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product UI guidance for Workbench UI changes
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

Historical reference only:

- `tasks/TASK_313_PROJECT_PACKAGE_ORCHESTRATOR_EXECUTE.md`

Do not implement old `/project-package/execute`.

## Current Code Reality

Existing useful services:

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - Generates Confirmed Matrix Test Record into controlled output/staging.
- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
  - Generates Fee Evaluation workbook and already registers `fee_evaluation` output in current direct export flows.
- `backend/application/customer_feedback_form_generation_service.py`
  - Generates Customer Feedback Form into controlled generated output.
- `backend/application/official_project_workspace_service.py`
  - Provides completed Official project workspace/folder path semantics.
- `backend/application/official_project_folder_check_service.py`
  - Provides Project Folder check semantics and current Required files state.
- `backend/application/project_output_record_service.py`
  - Registers and summarizes output records.
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - Derives TASK_320 Project Folder task rows.
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - Renders selected task details.

Important current gap:

- `ProjectOutputKind` currently lacks `customer_feedback_form`.
- `ProjectOutputRecord` does not currently expose a first-class final-file fingerprint field.
- Some existing generation/export flows register output records as part of direct-export behavior; TASK_321 must not use those side-effecting paths for staging.
- TASK_318 Official folder check currently treats Customer Feedback Form as deferred and does not read a `customer_feedback_form` output record.
- Old `ProjectPackagePreviewPanel` exists but must not become the Workbench surface for TASK_321.

## Target API Contract

Create:

```text
GET  /api/projects/{project_id}/project-folder/required-forms/preview
POST /api/projects/{project_id}/project-folder/required-forms/generate
```

Preview response:

```json
{
  "project_id": "project-1",
  "status": "ready",
  "official_project_folder_path": "D:/Test Project/DL-2026-05-011/...",
  "confirmed_matrix_id": "cm-1",
  "confirmed_revision": 1,
  "confirmed_fee_id": "fee-1",
  "confirmed_fee_revision": 1,
  "confirmed_fee_pricing_draft_edit_id": "draft-edit-1",
  "customer_feedback_template_path": "D:/Source/Template/E-4243.xlsx",
  "items": [
    {
      "key": "test_record",
      "label": "Test Record",
      "target_path": "D:/.../Submitted Material/DL-2026-05-011_Test_Record.docx",
      "status": "ready",
      "action": "generate",
      "message": "Ready to generate."
    },
    {
      "key": "fee_form",
      "label": "Fee Form",
      "target_path": "D:/.../DL-2026-05-011_Fee_Form.xls",
      "status": "ready",
      "action": "update",
      "message": "Existing ConnLab-generated file can be safely updated."
    }
  ],
  "blockers": [],
  "warnings": []
}
```

Generate request:

```json
{
  "expected_official_project_folder_path": "D:/Test Project/DL-2026-05-011/...",
  "expected_confirmed_matrix_id": "cm-1",
  "expected_confirmed_revision": 1,
  "expected_confirmed_fee_id": "fee-1",
  "expected_confirmed_fee_revision": 1,
  "expected_confirmed_fee_pricing_draft_edit_id": "draft-edit-1",
  "expected_customer_feedback_template_path": "D:/Source/Template/E-4243.xlsx",
  "expected_targets": [
    {
      "key": "test_record",
      "target_path": "D:/.../Submitted Material/DL-2026-05-011_Test_Record.docx"
    },
    {
      "key": "fee_form",
      "target_path": "D:/.../DL-2026-05-011_Fee_Form.xls"
    },
    {
      "key": "customer_feedback_form",
      "target_path": "D:/.../DL-2026-05-011_Customer_Feedback_Form.xlsx"
    }
  ]
}
```

Generate response:

```json
{
  "project_id": "project-1",
  "status": "generated",
  "official_project_folder_path": "D:/Test Project/DL-2026-05-011/...",
  "items": [
    {
      "key": "test_record",
      "label": "Test Record",
      "target_path": "D:/.../Submitted Material/DL-2026-05-011_Test_Record.docx",
      "status": "generated",
      "source_path": "D:/.../generated_test_record.docx",
      "output_record_id": "por-..."
    }
  ],
  "warnings": []
}
```

## Task 1: Domain And API Types

**Files:**

- Modify: `backend/domain/enums.py`
- Modify: `backend/application/project_output_record_service.py`
- Modify: the project output SQLite repository/migration, or add a task-owned Required Forms managed-output repository
- Modify: `frontend/src/api/client.ts`
- Test: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add Customer Feedback output kind**

Add enum value:

```python
class ProjectOutputKind(StrEnum):
    SECTION2_WRITE_BACK = "section2_write_back"
    TEST_RECORD_FORM = "test_record_form"
    FEE_EVALUATION = "fee_evaluation"
    CUSTOMER_FEEDBACK_FORM = "customer_feedback_form"
    APPROVAL_PACKAGE = "approval_package"
```

- [ ] **Step 2: Include it in output status ordering**

In `backend/application/project_output_record_service.py`, update `_ORDERED_KINDS`:

```python
_ORDERED_KINDS = (
    ProjectOutputKind.SECTION2_WRITE_BACK,
    ProjectOutputKind.TEST_RECORD_FORM,
    ProjectOutputKind.FEE_EVALUATION,
    ProjectOutputKind.CUSTOMER_FEEDBACK_FORM,
    ProjectOutputKind.APPROVAL_PACKAGE,
)
```

- [ ] **Step 3: Add managed-output fingerprint support**

Implementation may choose either:

- Extend `ProjectOutputRecord` and its repository with `output_sha256`, `output_size_bytes`, and `source_context_signature`.
- Or add a task-owned Required Forms managed-output record/table keyed by project id + output kind + final path.

Required service contract:

- Preview/generate must be able to tell whether an existing final target is the last ConnLab-generated output for the same output kind and final path.
- Preview/generate must compare the current disk file fingerprint against the stored ConnLab-managed fingerprint before allowing safe update.
- If the source context has changed, preview/generate may still allow a controlled refresh when the existing target is ConnLab-managed and its disk fingerprint still matches the stored fingerprint. The refreshed output record must store the new source context and new fingerprint.
- The frontend must not know whether the metadata lives on `ProjectOutputRecord` or a task-owned table.

Acceptance tests must cover:

- missing metadata + existing file -> conflict,
- same context + unchanged fingerprint -> update allowed,
- same context + changed fingerprint -> conflict,
- different context + unchanged ConnLab-managed fingerprint -> controlled refresh allowed,
- different context + changed fingerprint -> conflict.

- [ ] **Step 4: Add frontend DTO types**

In `frontend/src/api/client.ts`, extend `ProjectOutputKind`:

```ts
export type ProjectOutputKind =
  | "section2_write_back"
  | "test_record_form"
  | "fee_evaluation"
  | "customer_feedback_form"
  | "approval_package";
```

Add Required Forms DTOs:

```ts
export type ProjectFolderRequiredFormsStatus =
  | "blocked"
  | "ready"
  | "current"
  | "conflict";

export type ProjectFolderRequiredFormKey =
  | "test_record"
  | "fee_form"
  | "customer_feedback_form";

export type ProjectFolderRequiredFormAction =
  | "generate"
  | "update"
  | "skip"
  | "conflict"
  | "blocked";

export type ProjectFolderRequiredFormPreviewItem = {
  key: ProjectFolderRequiredFormKey;
  label: string;
  target_path: string | null;
  status: "ready" | "current" | "blocked" | "conflict";
  action: ProjectFolderRequiredFormAction;
  message: string;
};

export type ProjectFolderRequiredFormsPreview = {
  project_id: string;
  status: ProjectFolderRequiredFormsStatus;
  official_project_folder_path: string | null;
  confirmed_matrix_id: string | null;
  confirmed_revision: number | null;
  confirmed_fee_id: string | null;
  confirmed_fee_revision: number | null;
  confirmed_fee_pricing_draft_edit_id: string | null;
  customer_feedback_template_path: string | null;
  items: ProjectFolderRequiredFormPreviewItem[];
  blockers: string[];
  warnings: string[];
};

export type ProjectFolderRequiredFormsGenerateTarget = {
  key: ProjectFolderRequiredFormKey;
  target_path: string;
};

export type ProjectFolderRequiredFormsGenerateRequest = {
  expected_official_project_folder_path: string;
  expected_confirmed_matrix_id: string;
  expected_confirmed_revision: number;
  expected_confirmed_fee_id: string;
  expected_confirmed_fee_revision: number;
  expected_confirmed_fee_pricing_draft_edit_id: string;
  expected_customer_feedback_template_path: string;
  expected_targets: ProjectFolderRequiredFormsGenerateTarget[];
};

export type ProjectFolderRequiredFormsGenerateItem = {
  key: ProjectFolderRequiredFormKey;
  label: string;
  target_path: string;
  status: "generated" | "updated" | "skipped" | "failed" | "conflict";
  source_path: string | null;
  output_record_id: string | null;
  message: string;
};

export type ProjectFolderRequiredFormsGenerateResponse = {
  project_id: string;
  status: "generated" | "partial" | "blocked" | "conflict";
  official_project_folder_path: string;
  items: ProjectFolderRequiredFormsGenerateItem[];
  warnings: string[];
};
```

- [ ] **Step 5: Add API client functions**

```ts
export function fetchProjectFolderRequiredFormsPreview(
  projectId: string
): Promise<ProjectFolderRequiredFormsPreview> {
  return requestJson<ProjectFolderRequiredFormsPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/project-folder/required-forms/preview`,
    { cache: "no-store" }
  );
}

export function generateProjectFolderRequiredForms(
  projectId: string,
  input: ProjectFolderRequiredFormsGenerateRequest
): Promise<ProjectFolderRequiredFormsGenerateResponse> {
  return requestJson<ProjectFolderRequiredFormsGenerateResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/project-folder/required-forms/generate`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}
```

- [ ] **Step 6: Add static guard**

Add a test in `tests/unit/test_frontend_shell_files.py`:

```python
def test_task321_required_forms_contract_is_project_folder_not_package() -> None:
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    assert "customer_feedback_form" in client_source
    assert "/project-folder/required-forms/preview" in client_source
    assert "/project-folder/required-forms/generate" in client_source
    assert "/project-package/execute" not in client_source
```

- [ ] **Step 7: Run tests**

Run:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task321"
cd frontend
npm run build
```

Expected: static guard passes and TypeScript builds.

## Task 2: Backend Preview Service

**Files:**

- Create: `backend/application/project_folder_required_forms_service.py`
- Modify: `backend/application/official_project_folder_check_service.py`
- Test: `tests/unit/test_project_folder_required_forms_service.py`
- Test: `tests/unit/test_official_project_folder_check_service.py`

- [ ] **Step 1: Write preview dataclasses**

Create:

```python
@dataclass(frozen=True, slots=True)
class RequiredFormPreviewItem:
    key: str
    label: str
    target_path: Path | None
    status: str
    action: str
    message: str


@dataclass(frozen=True, slots=True)
class RequiredFormsPreview:
    project_id: str
    status: str
    official_project_folder_path: Path | None
    confirmed_matrix_id: str | None
    confirmed_revision: int | None
    confirmed_fee_id: str | None
    confirmed_fee_revision: int | None
    confirmed_fee_pricing_draft_edit_id: str | None
    customer_feedback_template_path: Path | None
    items: tuple[RequiredFormPreviewItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
```

- [ ] **Step 2: Define ports**

Include protocols:

```python
class OfficialWorkspaceReader(Protocol):
    def preview(self, project_id: str) -> object:
        """Return TASK_316 official workspace preview."""


class OfficialFolderCheckReader(Protocol):
    def preview(self, project_id: str) -> object:
        """Return TASK_318 official folder check preview."""


class ConfirmedMatrixReader(Protocol):
    def get_active_snapshot(self, project_id: str) -> object | None:
        """Return active Confirmed Matrix authority snapshot."""


class ConfirmedFeeReader(Protocol):
    def get_latest(self, project_id: str) -> object:
        """Return latest Confirmed Fee read result."""


class CustomerFeedbackTemplateReader(Protocol):
    def preview_template(self, project_id: str) -> Path:
        """Return unique Customer Feedback template path or raise readiness error."""
```

If existing services expose different method names, adapt the concrete dependency wrapper in `backend/api/dependencies.py`, not the core service logic.

- [ ] **Step 3: Write failing tests**

Test cases:

```python
def test_preview_blocks_without_completed_official_folder(tmp_path: Path) -> None:
    service = make_service(workspace_status="blocked")
    preview = service.preview("P1")
    assert preview.status == "blocked"
    assert "Official project folder" in preview.blockers[0]


def test_preview_places_test_record_under_submitted_material(tmp_path: Path) -> None:
    service = make_ready_service(tmp_path)
    preview = service.preview("P1")
    item = item_by_key(preview, "test_record")
    assert "Submitted Material" in str(item.target_path)
    assert item.action == "generate"


def test_preview_places_fee_and_customer_feedback_at_official_root(tmp_path: Path) -> None:
    service = make_ready_service(tmp_path)
    preview = service.preview("P1")
    fee = item_by_key(preview, "fee_form")
    feedback = item_by_key(preview, "customer_feedback_form")
    assert fee.target_path.parent == preview.official_project_folder_path
    assert feedback.target_path.parent == preview.official_project_folder_path


def test_preview_blocks_existing_target_conflict(tmp_path: Path) -> None:
    service = make_ready_service(tmp_path, existing_targets={"fee_form"})
    preview = service.preview("P1")
    assert preview.status == "conflict"
    assert item_by_key(preview, "fee_form").action == "conflict"


def test_preview_allows_safe_update_for_unchanged_managed_target(tmp_path: Path) -> None:
    service = make_ready_service(
        tmp_path,
        managed_targets={"fee_form": "same_context_unchanged_fingerprint"},
    )
    preview = service.preview("P1")
    assert preview.status == "ready"
    assert item_by_key(preview, "fee_form").action == "update"


def test_preview_allows_controlled_refresh_for_changed_context_when_target_is_unmodified(
    tmp_path: Path,
) -> None:
    service = make_ready_service(
        tmp_path,
        managed_targets={"fee_form": "changed_context_unchanged_fingerprint"},
    )
    preview = service.preview("P1")
    assert preview.status == "ready"
    assert item_by_key(preview, "fee_form").action == "update"


def test_preview_conflicts_when_managed_target_was_manually_changed(
    tmp_path: Path,
) -> None:
    service = make_ready_service(
        tmp_path,
        managed_targets={"fee_form": "same_context_changed_fingerprint"},
    )
    preview = service.preview("P1")
    assert preview.status == "conflict"
    assert item_by_key(preview, "fee_form").action == "conflict"
```

- [ ] **Step 4: Implement preview**

Rules:

- Use completed Official project folder path from TASK_316 workspace preview.
- Require `Submitted Material` directory for Test Record target.
- Require active Confirmed Matrix snapshot.
- Require latest Confirmed Fee status `current`.
- Resolve Customer Feedback template path through existing Customer Feedback readiness/template logic.
- Plan targets:
  - `{DL}_Test_Record.docx` under `Submitted Material`
  - `{DL}_Fee_Form.xls` under Official project folder root
  - `{DL}_Customer_Feedback_Form.xlsx` under Official project folder root
- If target does not exist, action is `generate`.
- If target exists and matching managed-output metadata confirms same output kind, same path, same source context, and unchanged disk fingerprint, action is `update`.
- If target exists and is unmanaged, missing metadata, different source context, or fingerprint-changed, mark conflict.

- [ ] **Step 5: Update TASK_318 Official folder check for Customer Feedback**

Rules:

- Add `ProjectOutputKind.CUSTOMER_FEEDBACK_FORM` to the Official folder check read model.
- Customer Feedback Form must remain `deferred` before TASK_321 has a project-local output.
- Customer Feedback Form becomes `ready` only when:
  - latest `customer_feedback_form` output status is current,
  - the recorded final path exists,
  - the final path is under the Official project folder root,
  - the disk file fingerprint still matches managed-output metadata when that metadata is available.
- Template existence alone never makes Customer Feedback Form ready.

Tests:

```python
def test_customer_feedback_remains_deferred_without_project_output(tmp_path: Path) -> None:
    check = make_official_folder_check(tmp_path, customer_feedback_record=None)
    preview = check.preview("P1")
    assert file_item(preview, "customer_feedback_form").status == "deferred"


def test_customer_feedback_ready_when_current_output_exists(tmp_path: Path) -> None:
    check = make_official_folder_check(tmp_path, customer_feedback_record="current_existing")
    preview = check.preview("P1")
    assert file_item(preview, "customer_feedback_form").status == "ready"


def test_customer_feedback_missing_when_current_output_missing_on_disk(
    tmp_path: Path,
) -> None:
    check = make_official_folder_check(tmp_path, customer_feedback_record="missing_file")
    preview = check.preview("P1")
    assert file_item(preview, "customer_feedback_form").status == "missing"
```

- [ ] **Step 6: Run service tests**

Run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/unit/test_official_project_folder_check_service.py -q
```

Expected: preview tests pass.

## Task 3: Safe Final Placement And Generate Service

**Files:**

- Modify: `backend/application/project_folder_required_forms_service.py`
- Create: `backend/infrastructure/files/project_folder_required_forms_gateway.py`
- Test: `tests/unit/test_project_folder_required_forms_service.py`

- [ ] **Step 1: Add placement gateway**

Create gateway methods:

```python
class ProjectFolderRequiredFormsFileGateway:
    """Safely place generated required forms into the Official project folder."""

    def create_new(self, source: Path, target: Path) -> None:
        """Copy one new file to target and fail if target already exists."""
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            with source.open("rb") as input_file:
                shutil.copyfileobj(input_file, output)

    def update_managed(
        self,
        source: Path,
        target: Path,
        *,
        expected_existing_sha256: str,
    ) -> None:
        """Replace a ConnLab-managed target only if it is still unchanged."""
        current_sha256 = compute_sha256(target)
        if current_sha256 != expected_existing_sha256:
            raise RequiredFormsTargetChangedError(str(target))
        temporary = target.with_name(f".{target.name}.connlab-tmp")
        try:
            shutil.copyfile(source, temporary)
            if compute_sha256(target) != expected_existing_sha256:
                raise RequiredFormsTargetChangedError(str(target))
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    def remove_if_created(self, path: Path) -> None:
        """Best-effort cleanup for files created by the current run."""
        try:
            path.unlink()
        except FileNotFoundError:
            return
```

- [ ] **Step 2: Add generate command/result dataclasses**

```python
@dataclass(frozen=True, slots=True)
class RequiredFormsGenerateTarget:
    key: str
    target_path: Path


@dataclass(frozen=True, slots=True)
class GenerateRequiredFormsCommand:
    project_id: str
    expected_official_project_folder_path: Path
    expected_confirmed_matrix_id: str
    expected_confirmed_revision: int
    expected_confirmed_fee_id: str
    expected_confirmed_fee_revision: int
    expected_confirmed_fee_pricing_draft_edit_id: str
    expected_customer_feedback_template_path: Path
    expected_targets: tuple[RequiredFormsGenerateTarget, ...]


@dataclass(frozen=True, slots=True)
class RequiredFormsGenerateItem:
    key: str
    label: str
    target_path: Path
    status: str
    source_path: Path | None
    output_record_id: str | None
    message: str
```

- [ ] **Step 3: Write generate tests**

Test cases:

```python
def test_generate_rejects_stale_preview_context(tmp_path: Path) -> None:
    service = make_ready_service(tmp_path)
    command = ready_command(tmp_path, expected_confirmed_revision=999)
    with pytest.raises(RequiredFormsContextMismatchError):
        service.generate(command)


def test_generate_blocks_before_copy_when_target_exists(tmp_path: Path) -> None:
    service = make_ready_service(tmp_path, existing_targets={"test_record"})
    command = ready_command(tmp_path)
    with pytest.raises(RequiredFormsConflictError):
        service.generate(command)
    assert not generated_final_files(tmp_path)


def test_generate_updates_unchanged_managed_target(tmp_path: Path) -> None:
    service, output_store = make_ready_service_with_managed_target(
        tmp_path,
        managed_targets={"fee_form": "same_context_unchanged_fingerprint"},
    )
    result = service.generate(ready_command(tmp_path))
    assert item_by_key(result, "fee_form").status == "updated"
    assert output_store.latest(ProjectOutputKind.FEE_EVALUATION).status is ProjectOutputStatus.CURRENT


def test_generate_refreshes_changed_context_when_managed_target_is_unmodified(
    tmp_path: Path,
) -> None:
    service, output_store = make_ready_service_with_managed_target(
        tmp_path,
        managed_targets={"fee_form": "changed_context_unchanged_fingerprint"},
    )
    result = service.generate(ready_command(tmp_path))
    assert item_by_key(result, "fee_form").status == "updated"
    latest = output_store.latest(ProjectOutputKind.FEE_EVALUATION)
    assert latest.status is ProjectOutputStatus.CURRENT
    assert latest.source_context_signature == current_source_context_signature()


def test_generate_conflicts_when_managed_target_changes_between_preview_and_write(
    tmp_path: Path,
) -> None:
    service = make_service_with_target_mutation_before_replace(tmp_path)
    result = service.generate(ready_command(tmp_path))
    assert result.status == "conflict"
    assert item_by_key(result, "fee_form").status == "conflict"


def test_generate_places_three_files_and_registers_outputs(tmp_path: Path) -> None:
    service, output_store = make_ready_service_with_output_store(tmp_path)
    result = service.generate(ready_command(tmp_path))
    assert result.status == "generated"
    assert final_path(result, "test_record").parent.name == "Submitted Material"
    assert final_path(result, "fee_form").parent == official_root(tmp_path)
    assert final_path(result, "customer_feedback_form").parent == official_root(tmp_path)
    assert output_store.latest(ProjectOutputKind.TEST_RECORD_FORM).status is ProjectOutputStatus.CURRENT
    assert output_store.latest(ProjectOutputKind.FEE_EVALUATION).status is ProjectOutputStatus.CURRENT
    assert output_store.latest(ProjectOutputKind.CUSTOMER_FEEDBACK_FORM).status is ProjectOutputStatus.CURRENT


def test_generate_reports_partial_failure_and_does_not_mark_missing_outputs_current(
    tmp_path: Path,
) -> None:
    service, output_store = make_service_with_copy_failure_after_first_file(tmp_path)
    result = service.generate(ready_command(tmp_path))
    assert result.status == "partial"
    assert output_store.latest(ProjectOutputKind.TEST_RECORD_FORM).status is ProjectOutputStatus.CURRENT
    assert output_store.latest(ProjectOutputKind.FEE_EVALUATION) is None
```

- [ ] **Step 4: Implement generate**

Algorithm:

1. Re-run `preview(project_id)`.
2. Compare preview context and expected targets.
3. If mismatch, raise context mismatch before generation.
4. If preview status is not `ready`, return/raise blocked or conflict before generation.
5. Generate/stage all three artifacts using staging-only generator ports.
   - Do not call generation/export paths that register output records as a side effect.
   - If an existing generator cannot be used without output-record side effects, add a small adapter or parameter so staging generation is output-record-free.
6. Verify all staging files exist.
7. For each item:
   - use no-overwrite create when the target is absent,
   - use fingerprint-checked safe update when the target is unchanged and ConnLab-managed,
   - allow changed source context only as a controlled refresh when the existing target still matches the stored ConnLab-managed fingerprint,
   - return conflict when the target is unmanaged or changed.
8. Register output records after each final create/update succeeds, storing final path, source context signature, SHA-256, and size.
9. If copy fails after previous files copied, return partial result with created paths and warning. Do not delete user-owned pre-existing files.

- [ ] **Step 5: Run service tests**

Run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
```

Expected: all preview/generate tests pass.

## Task 4: FastAPI Routes And Dependencies

**Files:**

- Create: `backend/api/routes_project_folder_required_forms.py`
- Modify: `backend/api/dependencies.py`
- Modify: API app/router registration file used by the project
- Test: `tests/integration/test_project_folder_required_forms_api.py`

- [ ] **Step 1: Add Pydantic DTOs**

Create response/request DTOs matching the Target API Contract.

Use string paths at the API boundary. Convert to `Path` only in route/service mapping.

- [ ] **Step 2: Add routes**

Route skeleton:

```python
router = APIRouter(
    prefix="/api/projects/{project_id}/project-folder/required-forms",
    tags=["project-folder-required-forms"],
)


@router.get("/preview", response_model=ProjectFolderRequiredFormsPreviewResponse)
def preview_required_forms(
    project_id: str,
    service: ProjectFolderRequiredFormsService = Depends(
        get_project_folder_required_forms_service
    ),
) -> ProjectFolderRequiredFormsPreviewResponse:
    return _to_preview_response(service.preview(project_id))


@router.post("/generate", response_model=ProjectFolderRequiredFormsGenerateResponse)
def generate_required_forms(
    project_id: str,
    request: ProjectFolderRequiredFormsGenerateRequest,
    service: ProjectFolderRequiredFormsService = Depends(
        get_project_folder_required_forms_service
    ),
) -> ProjectFolderRequiredFormsGenerateResponse:
    command = _to_generate_command(project_id, request)
    return _to_generate_response(service.generate(command))
```

- [ ] **Step 3: Map errors**

Required mappings:

- Project not found -> `404`
- Not ready/blockers -> `409`
- Preview context mismatch -> `409`
- Target conflict -> `409`
- Generation gateway/Office unavailable -> `503`
- Unexpected value errors from malformed input -> `422`

- [ ] **Step 4: Integration tests**

Test cases:

```python
def test_required_forms_preview_api_returns_project_folder_contract(client):
    response = client.get("/api/projects/P1/project-folder/required-forms/preview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert "items" in payload


def test_required_forms_generate_api_rejects_stale_context(client):
    response = client.post(
        "/api/projects/P1/project-folder/required-forms/generate",
        json=stale_request_payload(),
    )
    assert response.status_code == 409


def test_no_old_project_package_execute_route(client):
    response = client.post("/api/projects/P1/project-package/execute", json={})
    assert response.status_code in {404, 405}
```

- [ ] **Step 5: Run API tests**

Run:

```powershell
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
```

Expected: API tests pass.

## Task 5: Workbench Required Forms UI

**Files:**

- Modify: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Modify: `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- Modify: `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- Modify: `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Test: `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- Test: `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- Test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

- [ ] **Step 1: Add model state**

Add to `useProjectWorkbenchModel`:

```ts
requiredFormsPreview: ProjectFolderRequiredFormsPreview | null;
requiredFormsLoading: boolean;
requiredFormsGenerating: boolean;
requiredFormsError: string | null;
onRefreshRequiredForms: () => Promise<void>;
onGenerateRequiredForms: () => Promise<void>;
```

- [ ] **Step 2: Load preview**

Load preview only for active Matrix / Project Folder mode projects, using the existing Workbench load pattern.

On generate success, refresh:

- `requiredFormsPreview`
- `outputStatusSummary`
- `officialFolderCheckPreview`
- `publicDriveUploadPreview` if it has already been loaded

- [ ] **Step 3: Update selector**

`deriveRequiredFormsTask` should prefer the new preview when present:

- `ready` -> action `required_forms_generate`, status warning/ready depending item actions.
- `current` -> ready.
- `blocked` -> blocked/warning with blocker messages.
- `conflict` -> blocked.

Keep generated-output status as fallback when preview is not loaded.

- [ ] **Step 4: Extend action target**

Add:

```ts
| "required_forms_generate"
| "required_forms_refresh"
```

Handle in `ProjectWorkbenchLayout`:

```ts
if (actionTarget === "required_forms_generate") {
  void onGenerateRequiredForms();
  return;
}
if (actionTarget === "required_forms_refresh") {
  void onRefreshRequiredForms();
  return;
}
```

- [ ] **Step 5: Render Required forms detail**

In `ProjectFolderTaskList.tsx`, add a Required forms detail section that shows:

- status summary
- Test Record target path
- Fee Form target path
- Customer Feedback Form target path
- blockers/warnings
- one action button when task action target is generate/refresh

Use operator-facing text only:

```text
Required forms
Test Record
Fee Form
Customer Feedback Form
Generate required forms
Refresh required forms
```

Do not render:

```text
Package
Execute package
Project package
TASK_313
.connlab
manifest
SQLite
```

- [ ] **Step 6: Frontend tests**

Add tests:

```tsx
it("shows Generate required forms only from the Required forms detail", () => {
  render(<ProjectFolderTaskList ... />);
  fireEvent.click(screen.getByRole("button", { name: /Required forms/ }));
  expect(screen.getByRole("button", { name: "Generate required forms" })).toBeTruthy();
  expect(screen.queryByText("Execute package")).toBeNull();
});

it("shows Test Record in Submitted Material and Fee/Customer Feedback at root", () => {
  render(<ProjectFolderTaskList ... requiredFormsPreview={readyPreview} />);
  fireEvent.click(screen.getByRole("button", { name: /Required forms/ }));
  expect(screen.getByText(/Submitted Material/)).toBeTruthy();
  expect(screen.getByText(/Fee_Form/)).toBeTruthy();
  expect(screen.getByText(/Customer_Feedback_Form/)).toBeTruthy();
});
```

- [ ] **Step 7: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- --run ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --watch=false
npm run build
```

Expected: tests and build pass.

## Task 6: Static Guards, Documentation, And Final Validation

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`
- Modify: `tasks/TASK_321_PROJECT_FOLDER_REQUIRED_FORMS_GENERATION.md`
- Modify: `docs/task_321_project_folder_required_forms_generation_plan.md`

- [ ] **Step 1: Add static guards**

Add guards:

```python
def test_task321_does_not_restore_package_execute() -> None:
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    layout_source = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "project-workbench"
        / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    task_list_source = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "project-workbench"
        / "ProjectFolderTaskList.tsx"
    ).read_text(encoding="utf-8")
    assert "/project-package/execute" not in client_source
    assert "Execute package" not in layout_source
    assert "Execute package" not in task_list_source
```

- [ ] **Step 2: Run complete validation**

Run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_request_material_collection_service.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task321 or project_workbench or required_forms"
cd frontend
npm test -- --run ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --watch=false
npm run build
git diff --check
```

Expected:

- all targeted backend tests pass
- Workbench frontend tests pass
- build passes
- diff check has no whitespace errors, CRLF warnings are acceptable

- [ ] **Step 3: Browser smoke**

Use Browser or system Chrome fallback:

```text
Open http://localhost:5173/projects/<active-matrix-project-id>
Select Project Folder
Select Required forms
Check 740px width:
  no page-level horizontal scroll
  long target paths wrap/stay contained
  Generate required forms appears only when preview is ready
  no Package / Execute package wording appears
```

- [ ] **Step 4: Update task board**

After implementation and validation only, update `docs/task_board.md`:

```text
TASK_321 complete.
Old TASK_313 remains historical/deferred and is superseded by TASK_321 for Required forms generation.
Next task requires separate approval.
```

## Self-Review

Spec coverage:

- Old TASK_313 is explicitly retained as historical reference and not implemented.
- Required forms placement is split correctly: Test Record in `Submitted Material`, Fee Form and Customer Feedback Form at Official project folder root.
- Preview-before-write and stale-context rejection are required.
- Customer Feedback receives its own output kind.
- ConnLab-managed Required forms can be safely regenerated only when target fingerprint and source context still match.
- Staging generators must be output-record-free; TASK_321 alone marks Required forms outputs current after final placement.
- TASK_318 Official folder check must read `customer_feedback_form` output status so Customer Feedback Form can become ready after generation.
- TASK_320 Required forms detail is the only UI entry.
- Public drive upload and Section 2 remain out of scope.

Placeholder scan:

- No implementation step uses open-ended TODO/TBD language.
- Each task lists concrete files, commands, and expected outcomes.

Type consistency:

- API names use `ProjectFolderRequiredForms*`.
- User-facing copy uses `Required forms` / `Generate required forms`.
- Internal package terms are forbidden in UI and route contract.

## Stop Point

TASK_321 implementation is complete. Old TASK_313 remains historical/deferred and is superseded by TASK_321 for Required forms generation.

Validation completed:

- `py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_request_material_collection_service.py -q`
- `py -m pytest tests/integration/test_project_folder_required_forms_api.py -q`
- `cd frontend; npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task321 or task320 or task318"`
- `cd frontend; npm run build`
