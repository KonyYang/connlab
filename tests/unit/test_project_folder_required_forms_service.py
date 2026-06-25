from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    edited_values_to_json,
)
from backend.application.project_folder_required_forms_service import (
    GenerateRequiredFormsCommand,
    ProjectFolderRequiredFormsService,
    RequiredFormsContextMismatchError,
    RequiredFormsGenerateTarget,
)
from backend.api.dependencies import _FeeFormTemplateContextReader
from backend.application.project_output_record_service import ProjectOutputRecordError
from backend.application.official_project_folder_check_service import (
    OfficialFolderCheckItem,
    OfficialFolderCheckPreview,
)
from backend.application.project_output_record_service import (
    ProjectOutputStatusItem,
    ProjectOutputStatusSummary,
)
from backend.domain import (
    ApplicationForm,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)


def test_preview_blocks_without_completed_official_folder(tmp_path: Path) -> None:
    service = _service(tmp_path, workspace=None)

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert "Official project folder" in preview.blockers[0]


def test_preview_blocks_when_confirmed_matrix_authority_is_missing(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path, matrix_snapshot=None)

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert any("Matrix" in blocker for blocker in preview.blockers)


def test_preview_blocks_when_confirmed_fee_authority_is_missing(tmp_path: Path) -> None:
    service = _service(
        tmp_path,
        fee_result=_FeeResult(status="missing", latest_confirmed_fee=None),
    )

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert any("Fee" in blocker for blocker in preview.blockers)


def test_preview_blocks_when_confirmed_fee_authority_is_stale(tmp_path: Path) -> None:
    service = _service(
        tmp_path,
        fee_result=_FeeResult(status="stale", latest_confirmed_fee=_FeeVersion()),
    )

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert any("Fee" in blocker for blocker in preview.blockers)


def test_preview_blocks_when_confirmed_basic_information_is_missing(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path, basic_information=None)

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert any("Basic Information" in blocker for blocker in preview.blockers)


def test_preview_includes_basic_information_context_and_owner_suffix(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    preview = service.preview("P1")
    feedback = _item(preview.items, "customer_feedback_form")

    assert preview.confirmed_basic_information_version == 2
    assert preview.confirmed_basic_information_source_signature_hash == (
        "394f0d9772b800b7086b0d43d7a5bb748f33efafc474c39e9e25d4dc481712fe"
    )
    assert preview.source_context_signature == _same_context()
    assert feedback.target_path is not None
    assert feedback.target_path.name == "DL-001 Customer Feedback Form_Even Yang.xlsx"


def test_preview_source_context_includes_fee_template_identity(tmp_path: Path) -> None:
    service = _service(
        tmp_path,
        fee_template_reader=_FeeTemplateReader("fee-template:custom@sha256:abc"),
    )

    preview = service.preview("P1")

    assert preview.source_context_signature == (
        "matrix:CM1@1|fee:CF1@1|pricing:PD1|"
        "basic:2@394f0d9772b800b7086b0d43d7a5bb748f33efafc474c39e9e25d4dc481712fe|"
        "fee-template:custom@sha256:abc|fee-output:matrix_basic_with_basic_information"
    )


def test_xls_fee_template_context_is_stable_when_office_metadata_changes(
    tmp_path: Path,
) -> None:
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    template = templates_dir / "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    template.write_bytes(b"ole-metadata-version-1")
    reader = _FeeFormTemplateContextReader(templates_dir)

    first_context = reader.preview_template_context("P1")
    template.write_bytes(b"ole-metadata-version-2")
    second_context = reader.preview_template_context("P1")

    assert first_context == second_context
    assert "@sha256:" not in first_context


def test_preview_places_test_record_under_submitted_material(tmp_path: Path) -> None:
    service = _service(tmp_path)

    preview = service.preview("P1")
    item = _item(preview.items, "test_record")

    assert "Submitted Material" in str(item.target_path)
    assert item.action == "generate"


def test_preview_places_fee_and_customer_feedback_at_official_root(tmp_path: Path) -> None:
    service = _service(tmp_path)

    preview = service.preview("P1")
    fee = _item(preview.items, "fee_form")
    feedback = _item(preview.items, "customer_feedback_form")

    assert fee.target_path is not None
    assert feedback.target_path is not None
    assert fee.target_path.parent == preview.official_project_folder_path
    assert feedback.target_path.parent == preview.official_project_folder_path


def test_preview_conflicts_untracked_existing_business_form_target(tmp_path: Path) -> None:
    service = _service(tmp_path, existing_targets={"fee_form"})

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert _item(preview.items, "fee_form").action == "conflict"
    assert _item(preview.items, "fee_form").status == "conflict"
    assert _item(preview.items, "fee_form").existing_sha256 is None


def test_preview_conflicts_existing_business_form_when_record_path_differs(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService()
    output_store.items.append(
        ProjectOutputStatusItem(
            output_kind=ProjectOutputKind.FEE_EVALUATION,
            status=ProjectOutputStatus.CURRENT,
            output_path=str(tmp_path / "legacy" / "old_fee.xls"),
            source=ProjectOutputSource.SYSTEM_GENERATED,
            draft_id="draft-1",
            draft_version=1,
            reason="current",
            updated_at="2026-06-14T00:00:00+00:00",
            output_sha256="legacy",
            output_size_bytes=1,
            source_context_signature="old-context",
        )
    )
    service = _service(
        tmp_path,
        existing_targets={"fee_form"},
        output_service=output_store,
    )

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert _item(preview.items, "fee_form").action == "conflict"
    assert _item(preview.items, "fee_form").status == "conflict"
    assert _item(preview.items, "fee_form").existing_sha256 is None


def test_preview_marks_same_context_unchanged_managed_target_current(tmp_path: Path) -> None:
    service = _service(
        tmp_path,
        managed_targets={"fee_form": "same_context_unchanged_fingerprint"},
    )

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert _item(preview.items, "fee_form").action == "skip"
    assert _item(preview.items, "fee_form").status == "current"


def test_preview_allows_controlled_refresh_for_changed_context_when_target_is_unmodified(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path,
        managed_targets={"fee_form": "changed_context_unchanged_fingerprint"},
    )

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert _item(preview.items, "fee_form").action == "update"


def test_preview_conflicts_when_managed_target_was_manually_changed(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path,
        managed_targets={"fee_form": "same_context_changed_fingerprint"},
    )

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert _item(preview.items, "fee_form").action == "conflict"


def test_generate_rejects_stale_preview_context(tmp_path: Path) -> None:
    service = _service(tmp_path)
    command = _ready_command(tmp_path, expected_confirmed_revision=999)

    with pytest.raises(RequiredFormsContextMismatchError):
        service.generate(command)


def test_generate_rejects_stale_basic_information_context(tmp_path: Path) -> None:
    service = _service(tmp_path)
    command = _ready_command(tmp_path, expected_basic_information_version=99)

    with pytest.raises(RequiredFormsContextMismatchError):
        service.generate(command)


def test_generate_rejects_if_basic_information_changes_between_preview_and_write(
    tmp_path: Path,
) -> None:
    changed_snapshot = ConfirmedBasicInformationSnapshot(
        project_id="P1",
        version=3,
        values={
            "dl_number": "DL-001",
            "product_description": "Changed Connector",
            "test_item": "Qualification Test",
            "requested_by": "Requester BI",
            "project_leader": "Even Yang",
        },
        source_signature='{"dl_number":"DL-001","changed":true}',
        confirmed_at="2026-06-20T00:01:00+00:00",
        confirmed_by="Lab User",
    )
    service = _service(
        tmp_path,
        basic_information=(_default_basic_information(), changed_snapshot),
    )

    with pytest.raises(RequiredFormsContextMismatchError):
        service.generate(_ready_command(tmp_path))


def test_generate_passes_basic_information_to_staging_generator(tmp_path: Path) -> None:
    generator = _Generator(tmp_path)
    service = _service(tmp_path, generator=generator)

    service.generate(_ready_command(tmp_path))

    assert generator.basic_information_by_key["fee_form"]["dl_number"] == "DL-001"
    assert (
        generator.basic_information_by_key["fee_form"]["product_description"]
        == "Connector from Basic Info"
    )
    assert generator.basic_information_by_key["fee_form"]["requested_by"] == "Requester BI"
    assert generator.basic_information_by_key["fee_form"]["location"] == "Dongguan"
    assert (
        generator.basic_information_by_key["customer_feedback_form"]["requestor_email"]
        == "requester@example.test"
    )
    assert (
        generator.basic_information_by_key["customer_feedback_form"]["project_leader"]
        == "Even Yang"
    )
    assert generator.confirmed_fee_by_key["fee_form"].confirmed_fee_id == "CF1"
    assert generator.confirmed_fee_by_key["fee_form"].pricing_snapshot_json == (
        _pricing_snapshot_json()
    )


def test_generate_reuses_safe_fee_form_artifact_without_calling_generator(
    tmp_path: Path,
) -> None:
    reusable = _write_text(tmp_path / "generated_fee" / "current.xls", "reusable fee")
    generator = _Generator(tmp_path)
    service = _service(
        tmp_path,
        generator=generator,
        reusable_fee_form_reader=_ReusableFeeFormReader(reusable),
    )

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "generated"
    assert _item(result.items, "fee_form").source_path == reusable
    assert _final_path(tmp_path, "fee_form").read_text(encoding="utf-8") == "reusable fee"
    assert "fee_form" not in generator.basic_information_by_key
    assert _timing_labels(result) == [
        "required_forms.preview",
        "required_forms.validate_context",
        "customer_feedback_form.generate",
        "customer_feedback_form.place",
        "customer_feedback_form.register_output",
        "fee_form.reuse_lookup",
        "fee_form.place",
        "fee_form.register_output",
        "test_record.generate",
        "test_record.place",
        "test_record.register_output",
        "required_forms.total",
    ]


def test_generate_falls_back_to_fee_form_generator_when_reuse_is_unavailable(
    tmp_path: Path,
) -> None:
    generator = _Generator(tmp_path)
    service = _service(
        tmp_path,
        generator=generator,
        reusable_fee_form_reader=_ReusableFeeFormReader(None),
    )

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "generated"
    assert generator.basic_information_by_key["fee_form"]["dl_number"] == "DL-001"
    assert _item(result.items, "fee_form").source_path != _final_path(tmp_path, "fee_form")
    assert "fee_form.generate" in _timing_labels(result)


def test_generate_registers_context_bound_outputs_as_current_without_active_draft(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService(active_draft_id=None)
    service = _service(tmp_path, output_service=output_store)

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "generated"
    fee = output_store.latest(ProjectOutputKind.FEE_EVALUATION)
    assert fee is not None
    assert fee.status is ProjectOutputStatus.CURRENT
    assert fee.source is ProjectOutputSource.SYSTEM_GENERATED
    assert fee.draft_id is None
    assert fee.source_context_signature == _same_context()


def test_generate_blocks_before_copy_when_target_exists(tmp_path: Path) -> None:
    service = _service(tmp_path, existing_targets={"test_record"})

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "partial"
    assert _item(result.items, "test_record").status == "conflict"
    assert _item(result.items, "fee_form").status == "generated"
    assert _item(result.items, "customer_feedback_form").status == "generated"
    assert _final_path(tmp_path, "test_record").read_text(encoding="utf-8") == "manual"


def test_generate_skips_same_context_unchanged_managed_target(tmp_path: Path) -> None:
    output_store = _OutputStatusService()
    service = _service(
        tmp_path,
        output_service=output_store,
        managed_targets={"fee_form": "same_context_unchanged_fingerprint"},
    )

    result = service.generate(_ready_command(tmp_path))

    assert _item(result.items, "fee_form").status == "skipped"
    latest = output_store.latest(ProjectOutputKind.FEE_EVALUATION)
    assert latest is not None
    assert latest.status is ProjectOutputStatus.CURRENT


def test_generate_recreates_deleted_form_files_from_existing_output_records(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService()
    service = _service(
        tmp_path,
        output_service=output_store,
        managed_targets={
            "test_record": "same_context_unchanged_fingerprint",
            "fee_form": "same_context_unchanged_fingerprint",
            "customer_feedback_form": "same_context_unchanged_fingerprint",
        },
    )
    _final_path(tmp_path, "fee_form").unlink()
    _final_path(tmp_path, "customer_feedback_form").unlink()

    preview = service.preview("P1")
    assert preview.status == "ready"
    assert _item(preview.items, "fee_form").action == "generate"
    assert _item(preview.items, "customer_feedback_form").action == "generate"

    result = service.generate(
        _ready_command(
            tmp_path,
            expected_targets=(
                RequiredFormsGenerateTarget("fee_form", _final_path(tmp_path, "fee_form")),
                RequiredFormsGenerateTarget(
                    "customer_feedback_form",
                    _final_path(tmp_path, "customer_feedback_form"),
                ),
            ),
        )
    )

    assert result.status == "generated"
    assert _item(result.items, "fee_form").status == "generated"
    assert _item(result.items, "customer_feedback_form").status == "generated"
    assert _final_path(tmp_path, "fee_form").is_file()
    assert _final_path(tmp_path, "customer_feedback_form").is_file()
    assert output_store.latest(ProjectOutputKind.FEE_EVALUATION).status is ProjectOutputStatus.CURRENT
    assert (
        output_store.latest(ProjectOutputKind.CUSTOMER_FEEDBACK_FORM).status
        is ProjectOutputStatus.CURRENT
    )


def test_generate_recreates_business_forms_when_legacy_underscore_records_exist(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService()
    legacy_fee_path = _official_root(tmp_path) / "DL-001_Fee_Form.xls"
    legacy_feedback_path = _official_root(tmp_path) / "DL-001_Customer_Feedback_Form_Alice.xlsx"
    for kind, path in (
        (ProjectOutputKind.FEE_EVALUATION, legacy_fee_path),
        (ProjectOutputKind.CUSTOMER_FEEDBACK_FORM, legacy_feedback_path),
    ):
        output_store.items.append(
            ProjectOutputStatusItem(
                output_kind=kind,
                status=ProjectOutputStatus.CURRENT,
                output_path=str(path),
                source=ProjectOutputSource.SYSTEM_GENERATED,
                draft_id="draft-1",
                draft_version=1,
                reason="current",
                updated_at="2026-06-14T00:00:00+00:00",
                output_sha256="legacy",
                output_size_bytes=1,
                source_context_signature="matrix:CM1@1|fee:CF1@1|pricing:PD1",
            )
        )
    service = _service(
        tmp_path,
        output_service=output_store,
        managed_targets={"test_record": "same_context_unchanged_fingerprint"},
    )

    preview = service.preview("P1")
    assert preview.status == "ready"
    assert _item(preview.items, "test_record").action == "skip"
    assert _item(preview.items, "fee_form").action == "generate"
    assert _item(preview.items, "customer_feedback_form").action == "generate"

    result = service.generate(
        _ready_command(
            tmp_path,
            expected_targets=(
                RequiredFormsGenerateTarget("fee_form", _final_path(tmp_path, "fee_form")),
                RequiredFormsGenerateTarget(
                    "customer_feedback_form",
                    _final_path(tmp_path, "customer_feedback_form"),
                ),
            ),
        )
    )

    assert result.status == "generated"
    assert _final_path(tmp_path, "fee_form").is_file()
    assert _final_path(tmp_path, "customer_feedback_form").is_file()


def test_generate_continues_when_output_tracking_registration_fails(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService(fail_register_for={"test_record"})
    service = _service(tmp_path, output_service=output_store)

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "generated"
    assert _item(result.items, "test_record").status == "generated"
    assert _item(result.items, "fee_form").status == "generated"
    assert _item(result.items, "customer_feedback_form").status == "generated"
    assert _item(result.items, "test_record").output_record_id is None
    assert _final_path(tmp_path, "fee_form").is_file()
    assert _final_path(tmp_path, "customer_feedback_form").is_file()
    assert any("output tracking was not updated" in warning for warning in result.warnings)


def test_generate_accepts_command_with_only_writable_targets_when_some_items_are_current(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService()
    service = _service(
        tmp_path,
        output_service=output_store,
        managed_targets={"fee_form": "same_context_unchanged_fingerprint"},
    )
    command = _ready_command(
        tmp_path,
        expected_targets=(
            RequiredFormsGenerateTarget("test_record", _final_path(tmp_path, "test_record")),
            RequiredFormsGenerateTarget(
                "customer_feedback_form",
                _final_path(tmp_path, "customer_feedback_form"),
            ),
        ),
    )

    result = service.generate(command)

    assert result.status == "generated"
    assert [item.key for item in result.items] == [
        "customer_feedback_form",
        "test_record",
    ]
    assert _item(result.items, "test_record").status == "generated"
    assert _item(result.items, "customer_feedback_form").status == "generated"


def test_generate_refreshes_changed_context_when_managed_target_is_unmodified(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService()
    service = _service(
        tmp_path,
        output_service=output_store,
        managed_targets={"fee_form": "changed_context_unchanged_fingerprint"},
    )

    result = service.generate(_ready_command(tmp_path))

    assert _item(result.items, "fee_form").status == "updated"
    latest = output_store.latest(ProjectOutputKind.FEE_EVALUATION)
    assert latest is not None
    assert latest.source_context_signature == _same_context()


def test_generate_rejects_fee_form_reuse_when_template_context_changes(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path,
        managed_targets={"fee_form": "same_context_unchanged_fingerprint"},
        fee_template_reader=_FeeTemplateReader("fee-template:changed@sha256:new"),
    )

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert _item(preview.items, "fee_form").action == "update"


def test_generate_conflicts_when_managed_target_changes_between_preview_and_write(
    tmp_path: Path,
) -> None:
    gateway = _FileGateway(mutate_before_update=True)
    service = _service(
        tmp_path,
        managed_targets={"fee_form": "changed_context_unchanged_fingerprint"},
        file_gateway=gateway,
    )

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "conflict"
    assert _item(result.items, "fee_form").status == "conflict"


def test_generate_places_three_files_and_registers_outputs(tmp_path: Path) -> None:
    output_store = _OutputStatusService()
    service = _service(tmp_path, output_service=output_store)

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "generated"
    assert _item(result.items, "test_record").target_path.parent.name == "Submitted Material"
    assert _item(result.items, "fee_form").target_path.parent == _official_root(tmp_path)
    assert _item(result.items, "customer_feedback_form").target_path.parent == _official_root(
        tmp_path
    )
    assert output_store.latest(ProjectOutputKind.TEST_RECORD_FORM).status is ProjectOutputStatus.CURRENT
    assert output_store.latest(ProjectOutputKind.FEE_EVALUATION).status is ProjectOutputStatus.CURRENT
    assert (
        output_store.latest(ProjectOutputKind.CUSTOMER_FEEDBACK_FORM).status
        is ProjectOutputStatus.CURRENT
    )


def test_generate_reports_partial_failure_and_does_not_mark_missing_outputs_current(
    tmp_path: Path,
) -> None:
    output_store = _OutputStatusService()
    service = _service(
        tmp_path,
        output_service=output_store,
        file_gateway=_FileGateway(fail_on_key="fee_form"),
    )

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "partial"
    assert (
        output_store.latest(ProjectOutputKind.CUSTOMER_FEEDBACK_FORM).status
        is ProjectOutputStatus.CURRENT
    )
    assert output_store.latest(ProjectOutputKind.TEST_RECORD_FORM) is None
    assert output_store.latest(ProjectOutputKind.FEE_EVALUATION) is None


def test_generate_reports_blocked_when_first_final_placement_fails(tmp_path: Path) -> None:
    output_store = _OutputStatusService()
    service = _service(
        tmp_path,
        output_service=output_store,
        file_gateway=_FileGateway(fail_on_key="customer_feedback_form"),
    )

    result = service.generate(_ready_command(tmp_path))

    assert result.status == "blocked"
    assert _item(result.items, "customer_feedback_form").status == "failed"
    assert output_store.latest(ProjectOutputKind.CUSTOMER_FEEDBACK_FORM) is None


def _pricing_snapshot_json() -> str:
    return edited_values_to_json(
        FeeEvaluationEditedExportValues(
            rows=tuple(),
            summary=FeeEvaluationEditedExportSummary(
                condition_confirmation_spend_time="0",
                external_cost="0",
                external_cost_note="",
                lab_manpower_hourly_rate="200",
            ),
        )
    )


@dataclass(frozen=True, slots=True)
class _Matrix:
    confirmed_matrix_id: str = "CM1"
    revision: int = 1


@dataclass(frozen=True, slots=True)
class _FeeVersion:
    confirmed_fee_id: str = "CF1"
    revision: int = 1
    pricing_draft_edit_id: str = "PD1"
    pricing_snapshot_json: str = _pricing_snapshot_json()


@dataclass(frozen=True, slots=True)
class _FeeResult:
    status: str
    latest_confirmed_fee: _FeeVersion | None


class _WorkspaceRepo:
    def __init__(self, workspace: OfficialWorkspaceRecord | None) -> None:
        self.workspace = workspace

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return self.workspace


class _FolderCheck:
    def __init__(self, tmp_path: Path, *, status: str = "ready") -> None:
        self.tmp_path = tmp_path
        self.status = status

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        official = _official_root(self.tmp_path)
        return OfficialFolderCheckPreview(
            project_id=project_id,
            status=self.status,
            local_workspace_path=self.tmp_path / "DL-001",
            official_project_folder_path=official,
            required_folders=tuple(),
            required_files=tuple(),
            blockers=tuple() if self.status == "ready" else ("Folder check blocked.",),
            warnings=tuple(),
            next_action="none",
        )


class _MatrixReader:
    def __init__(self, snapshot: _Matrix | None = _Matrix()) -> None:
        self.snapshot = snapshot

    def get_active_snapshot(self, project_id: str) -> _Matrix | None:
        return self.snapshot


class _FeeReader:
    def __init__(
        self,
        result: _FeeResult = _FeeResult(status="current", latest_confirmed_fee=_FeeVersion()),
    ) -> None:
        self.result = result

    def get_latest(self, project_id: str) -> _FeeResult:
        return self.result


class _TemplateReader:
    def __init__(self, tmp_path: Path) -> None:
        self.template_path = tmp_path / "template" / "E-4243.xlsx"
        self.template_path.parent.mkdir(parents=True, exist_ok=True)
        self.template_path.write_bytes(b"template")

    def preview_template(self, project_id: str) -> Path:
        return self.template_path


class _FeeTemplateReader:
    def __init__(
        self,
        context: str = "fee-template:E-176.xls@sha256:fee-template-hash",
    ) -> None:
        self.context = context

    def preview_template_context(self, project_id: str) -> str:
        return self.context


class _Generator:
    def __init__(self, tmp_path: Path) -> None:
        self.root = tmp_path / "stage"
        self.basic_information_by_key: dict[str, dict[str, str]] = {}
        self.confirmed_fee_by_key: dict[str, object] = {}

    def generate(
        self,
        *,
        project_id: str,
        key: str,
        target_name: str,
        basic_information: ConfirmedBasicInformationSnapshot,
        confirmed_fee: object,
    ) -> Path:
        self.basic_information_by_key[key] = dict(basic_information.values)
        self.confirmed_fee_by_key[key] = confirmed_fee
        path = self.root / project_id / target_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{key}:{target_name}", encoding="utf-8")
        return path


class _ReusableFeeFormReader:
    def __init__(self, path: Path | None) -> None:
        self.path = path
        self.calls: list[tuple[str, str, Path]] = []

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        self.calls.append((project_id, source_context_signature, final_target_path))
        return self.path


class _FileGateway:
    def __init__(
        self,
        *,
        fail_on_key: str | None = None,
        mutate_before_update: bool = False,
    ) -> None:
        self.fail_on_key = fail_on_key
        self.mutate_before_update = mutate_before_update

    def create_new(self, source: Path, target: Path, *, key: str) -> None:
        if self.fail_on_key == key:
            raise OSError("copy failed")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(source.read_bytes())

    def update_managed(
        self,
        source: Path,
        target: Path,
        *,
        key: str,
        expected_existing_sha256: str,
    ) -> None:
        if self.mutate_before_update:
            target.write_text("operator edit", encoding="utf-8")
        if self.fail_on_key == key:
            raise OSError("update failed")
        from backend.application.project_folder_required_forms_service import compute_sha256

        if compute_sha256(target) != expected_existing_sha256:
            from backend.application.project_folder_required_forms_service import (
                RequiredFormsTargetChangedError,
            )

            raise RequiredFormsTargetChangedError("target changed")
        target.write_bytes(source.read_bytes())


class _OutputStatusService:
    def __init__(
        self,
        items: tuple[ProjectOutputStatusItem, ...] = tuple(),
        *,
        fail_register_for: set[str] | None = None,
        active_draft_id: str | None = "draft-1",
    ) -> None:
        self.items = list(items)
        self.fail_register_for = fail_register_for or set()
        self.active_draft_id = active_draft_id

    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        return ProjectOutputStatusSummary(
            project_id=project_id,
            active_draft_id=self.active_draft_id,
            active_draft_version=1 if self.active_draft_id else None,
            items=tuple(self.items),
        )

    def register_output(self, command):
        from backend.domain import ProjectOutputRecord

        key_by_kind = {
            ProjectOutputKind.TEST_RECORD_FORM: "test_record",
            ProjectOutputKind.FEE_EVALUATION: "fee_form",
            ProjectOutputKind.CUSTOMER_FEEDBACK_FORM: "customer_feedback_form",
        }
        if key_by_kind.get(command.output_kind) in self.fail_register_for:
            raise ProjectOutputRecordError("draft_id is required unless status is manual or failed.")
        record = ProjectOutputRecord(
            output_record_id=f"por-{len(self.items) + 1}",
            project_id=command.project_id,
            output_kind=command.output_kind,
            status=command.status,
            source=command.source,
            output_path=command.output_path,
            draft_id=command.draft_id,
            draft_version=1,
            output_sha256=command.output_sha256,
            output_size_bytes=command.output_size_bytes,
            source_context_signature=command.source_context_signature,
            created_at="2026-06-14T00:00:00+00:00",
            updated_at="2026-06-14T00:00:00+00:00",
        )
        self.items.append(
            ProjectOutputStatusItem(
                output_kind=record.output_kind,
                status=record.status,
                output_path=record.output_path,
                source=record.source,
                draft_id=record.draft_id,
                draft_version=record.draft_version,
                reason="current",
                updated_at=record.updated_at,
                output_sha256=record.output_sha256,
                output_size_bytes=record.output_size_bytes,
                source_context_signature=record.source_context_signature,
            )
        )
        return record

    def latest(self, kind: ProjectOutputKind) -> ProjectOutputStatusItem | None:
        for item in reversed(self.items):
            if item.output_kind is kind:
                return item
        return None


def _service(
    tmp_path: Path,
    *,
    workspace: OfficialWorkspaceRecord | None | str = "default",
    existing_targets: set[str] | None = None,
    managed_targets: dict[str, str] | None = None,
    output_service: _OutputStatusService | None = None,
    file_gateway: _FileGateway | None = None,
    matrix_snapshot: _Matrix | None = _Matrix(),
    fee_result: _FeeResult = _FeeResult(
        status="current",
        latest_confirmed_fee=_FeeVersion(),
    ),
    basic_information: (
        ConfirmedBasicInformationSnapshot
        | tuple[ConfirmedBasicInformationSnapshot | None, ...]
        | None
        | str
    ) = "default",
    generator: _Generator | None = None,
    reusable_fee_form_reader: _ReusableFeeFormReader | None = None,
    fee_template_reader: _FeeTemplateReader | None = None,
) -> ProjectFolderRequiredFormsService:
    _prepare_official_folder(tmp_path)
    output_service = output_service or _OutputStatusService()
    managed_targets = managed_targets or {}
    for key, scenario in managed_targets.items():
        path = _final_path(tmp_path, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("managed old", encoding="utf-8")
        from backend.application.project_folder_required_forms_service import compute_sha256

        stored_sha = compute_sha256(path)
        if scenario in {
            "same_context_changed_fingerprint",
            "changed_context_changed_fingerprint",
        }:
            path.write_text("operator changed", encoding="utf-8")
        output_service.items.append(
            ProjectOutputStatusItem(
                output_kind=_kind_for_key(key),
                status=ProjectOutputStatus.CURRENT,
                output_path=str(path),
                source=ProjectOutputSource.SYSTEM_GENERATED,
                draft_id="draft-1",
                draft_version=1,
                reason="current",
                updated_at="2026-06-14T00:00:00+00:00",
                output_sha256=stored_sha,
                output_size_bytes=len("managed old".encode("utf-8")),
                source_context_signature=(
                    "old-context"
                    if scenario.startswith("changed_context")
                    else _same_context()
                ),
            )
        )
    for key in existing_targets or set():
        path = _final_path(tmp_path, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("manual", encoding="utf-8")
    if workspace == "default":
        workspace = _workspace(tmp_path)
    if basic_information == "default":
        basic_information = _default_basic_information()
    return ProjectFolderRequiredFormsService(
        workspace_repository=_WorkspaceRepo(workspace),
        folder_check_service=_FolderCheck(tmp_path),
        confirmed_matrix_reader=_MatrixReader(matrix_snapshot),
        confirmed_fee_reader=_FeeReader(fee_result),
        basic_information_reader=_BasicInformationReader(basic_information),
        customer_feedback_template_reader=_TemplateReader(tmp_path),
        fee_form_template_context_reader=fee_template_reader or _FeeTemplateReader(),
        application_form_reader=_ApplicationFormReader(),
        generator=generator or _Generator(tmp_path),
        reusable_fee_form_reader=(
            reusable_fee_form_reader or _ReusableFeeFormReader(None)
        ),
        file_gateway=file_gateway or _FileGateway(),
        output_status_service=output_service,
    )


def _ready_command(
    tmp_path: Path,
    *,
    expected_confirmed_revision: int = 1,
    expected_basic_information_version: int = 2,
    expected_targets: tuple[RequiredFormsGenerateTarget, ...] | None = None,
) -> GenerateRequiredFormsCommand:
    return GenerateRequiredFormsCommand(
        project_id="P1",
        expected_official_project_folder_path=_official_root(tmp_path),
        expected_confirmed_matrix_id="CM1",
        expected_confirmed_revision=expected_confirmed_revision,
        expected_confirmed_fee_id="CF1",
        expected_confirmed_fee_revision=1,
        expected_confirmed_fee_pricing_draft_edit_id="PD1",
        expected_confirmed_basic_information_version=expected_basic_information_version,
        expected_confirmed_basic_information_source_signature_hash=(
            "394f0d9772b800b7086b0d43d7a5bb748f33efafc474c39e9e25d4dc481712fe"
        ),
        expected_customer_feedback_template_path=tmp_path / "template" / "E-4243.xlsx",
        expected_targets=expected_targets
        or (
            RequiredFormsGenerateTarget("test_record", _final_path(tmp_path, "test_record")),
            RequiredFormsGenerateTarget("fee_form", _final_path(tmp_path, "fee_form")),
            RequiredFormsGenerateTarget(
                "customer_feedback_form",
                _final_path(tmp_path, "customer_feedback_form"),
            ),
        ),
    )


def _workspace(tmp_path: Path) -> OfficialWorkspaceRecord:
    return OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-001",
        local_workspace_path=tmp_path / "DL-001",
        source_book_path=tmp_path / "DL-001" / "Source Book",
        official_folder_path=_official_root(tmp_path),
        manifest_path=tmp_path / "DL-001" / ".connlab" / "manifest.json",
        template_source_path=tmp_path / "template",
        created_at="2026-06-14T00:00:00+00:00",
    )


def _prepare_official_folder(tmp_path: Path) -> None:
    (_official_root(tmp_path) / "Submitted Material").mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _official_root(tmp_path: Path) -> Path:
    return tmp_path / "DL-001" / "DL-001 Connector Qualification test"


def _final_path(tmp_path: Path, key: str) -> Path:
    root = _official_root(tmp_path)
    names = {
        "test_record": root / "Submitted Material" / "DL-001 Test Record.docx",
        "fee_form": root / "DL-001 Fee Form.xls",
        "customer_feedback_form": root / "DL-001 Customer Feedback Form_Even Yang.xlsx",
    }
    return names[key]


def _kind_for_key(key: str) -> ProjectOutputKind:
    return {
        "test_record": ProjectOutputKind.TEST_RECORD_FORM,
        "fee_form": ProjectOutputKind.FEE_EVALUATION,
        "customer_feedback_form": ProjectOutputKind.CUSTOMER_FEEDBACK_FORM,
    }[key]


def _item(items: tuple[object, ...], key: str):
    for item in items:
        if getattr(item, "key") == key:
            return item
    raise AssertionError(f"Missing item {key}")


def _timing_labels(result) -> list[str]:
    return [item.label for item in result.timings]


def _same_context() -> str:
    return (
        "matrix:CM1@1|fee:CF1@1|pricing:PD1|"
        "basic:2@394f0d9772b800b7086b0d43d7a5bb748f33efafc474c39e9e25d4dc481712fe|"
        "fee-template:E-176.xls@sha256:fee-template-hash|"
        "fee-output:matrix_basic_with_basic_information"
    )


class _ApplicationFormReader:
    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [
            ApplicationForm(
                form_id="F1",
                project_id=project_id,
                form_no="E-3718",
                revision="H",
                requester="Requester",
                assigned_personnel="Alice",
            )
        ]


class _BasicInformationReader:
    def __init__(
        self,
        snapshot: (
            ConfirmedBasicInformationSnapshot
            | tuple[ConfirmedBasicInformationSnapshot | None, ...]
            | None
        ),
    ) -> None:
        self.snapshots = list(snapshot) if isinstance(snapshot, tuple) else [snapshot]

    def get_latest_confirmed(
        self, project_id: str
    ) -> ConfirmedBasicInformationSnapshot | None:
        if len(self.snapshots) > 1:
            return self.snapshots.pop(0)
        return self.snapshots[0]


def _default_basic_information() -> ConfirmedBasicInformationSnapshot:
    return ConfirmedBasicInformationSnapshot(
        project_id="P1",
        version=2,
        values={
            "dl_number": "DL-001",
            "product_description": "Connector from Basic Info",
            "test_item": "Qualification Test",
            "requested_by": "Requester BI",
            "location": "Dongguan",
            "lab_performing_tests": "Dongguan",
            "phone": "123456",
            "requestor_email": "requester@example.test",
            "project_leader": "Even Yang",
            "date_lab_received_samples": "20 Jun 2026",
            "estimated_completion_date": "25 Jun 2026",
        },
        source_signature='{"dl_number":"DL-001"}',
        confirmed_at="2026-06-20T00:00:00+00:00",
        confirmed_by="Lab User",
    )
