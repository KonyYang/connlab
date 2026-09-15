from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_to_json,
)
from backend.application.fee_form_publication_service import (
    ExecuteFeeFormPublicationCommand,
    FeeFormPublicationService,
    PreviewFeeFormPublicationCommand,
)
from backend.infrastructure.files.test_record_publication_gateway import TestRecordPublicationGateway as PublicationGateway


def test_preview_downloads_draft_when_no_official_workspace_exists(tmp_path: Path) -> None:
    service = _service(tmp_path, workspace=None)

    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))

    assert preview.mode == "download"
    assert preview.status == "ready"


def test_preview_downloads_draft_when_recorded_official_folder_is_missing(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    workspace.official_folder_path.rmdir()
    service = _service(tmp_path, workspace=workspace)

    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))

    assert preview.mode == "download"
    assert preview.status == "ready"
    assert preview.blockers == ()


def test_preview_downloads_draft_when_current_values_are_not_confirmed(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path, workspace=_workspace(tmp_path))

    preview = service.preview(
        PreviewFeeFormPublicationCommand("P1", _values(external_cost="99"))
    )

    assert preview.mode == "download"
    assert preview.status == "ready"


def test_preview_offers_official_target_for_current_confirmed_fee(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    service = _service(tmp_path, workspace=workspace)

    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))

    assert preview.mode == "official"
    assert preview.status == "ready"
    assert preview.target_path == workspace.official_folder_path / "DL-001 Fee Form.xlsx"


def test_execute_publishes_confirmed_fee_form_and_registers_final_path(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    service = _service(tmp_path, workspace=workspace)
    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))

    result = service.execute(
        ExecuteFeeFormPublicationCommand(
            project_id="P1",
            current_values=_values(),
            preview_token=preview.preview_token,
            conflict_action="none",
            staging_dir=tmp_path / "staging",
        )
    )

    assert result.target_path.read_text(encoding="utf-8") == "confirmed fee"
    assert service._outputs.commands[-1].output_path == str(result.target_path)
    assert list((tmp_path / "staging").iterdir()) == []


def test_failed_generation_releases_empty_stage_and_preserves_official_file(tmp_path, caplog):
    import logging
    from backend.shared.operation_diagnostics import failure_details
    caplog.set_level(logging.INFO, logger="connlab.operations")
    workspace = _workspace(tmp_path)
    target = workspace.official_folder_path / "DL-001 Fee Form.xlsx"
    target.write_text("operator original", encoding="utf-8")
    service = _service(tmp_path, workspace=workspace)

    class FailingGenerator:
        def generate(self, **kwargs):
            assert kwargs["output_dir"].is_dir()
            raise RuntimeError("Excel unavailable")

    service._generator = FailingGenerator()
    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))
    with pytest.raises(RuntimeError, match="Excel unavailable") as caught:
        service.execute(ExecuteFeeFormPublicationCommand(
            "P1", _values(), preview.preview_token, "archive", tmp_path / "staging"
        ))
    assert target.read_text(encoding="utf-8") == "operator original"
    assert service._outputs.commands == []
    assert list((tmp_path / "staging").iterdir()) == []
    assert failure_details(caught.value)["stage"] == "generate_fee_workbook"
    assert "operation_failed" in caplog.text


def test_official_fee_archive_keeps_previous_file_and_registers_new_output(tmp_path):
    workspace = _workspace(tmp_path)
    target = workspace.official_folder_path / "DL-001 Fee Form.xlsx"
    target.write_text("operator original", encoding="utf-8")
    service = _service(tmp_path, workspace=workspace)
    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))
    result = service.execute(ExecuteFeeFormPublicationCommand(
        "P1", _values(), preview.preview_token, "archive", tmp_path / "staging"
    ))
    assert result.archive_path.read_text(encoding="utf-8") == "operator original"
    assert target.read_text(encoding="utf-8") == "confirmed fee"
    assert service._outputs.commands[-1].output_path == str(target)
    assert list((tmp_path / "staging").iterdir()) == []


def _values(*, external_cost: str = "0") -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0",
            external_cost=external_cost,
            external_cost_note="",
            lab_manpower_hourly_rate="200",
        ),
    )


def _workspace(tmp_path: Path):
    official = tmp_path / "DL-001 Official"
    official.mkdir()
    return SimpleNamespace(
        dl_number="DL-001",
        official_folder_path=official,
        local_workspace_path=tmp_path / "DL-001",
    )


def _service(tmp_path: Path, *, workspace) -> FeeFormPublicationService:
    fee = SimpleNamespace(
        confirmed_fee_id="fee-1",
        confirmed_fee_revision=2,
        pricing_draft_edit_id="draft-1",
        pricing_snapshot_json=edited_values_to_json(_values()),
    )
    outputs = _Outputs()
    service = FeeFormPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        confirmed_fee_reader=_FeeReader(fee),
        basic_information_reader=_BasicInformationReader(),
        generator=_Generator(),
        file_gateway=PublicationGateway(resource_label="Fee Form"),
        output_service=outputs,
    )
    service._outputs = outputs
    return service


class _WorkspaceStore:
    def __init__(self, workspace) -> None:
        self.workspace = workspace

    def get_by_project(self, project_id: str):
        return self.workspace


class _FeeReader:
    def __init__(self, fee) -> None:
        self.fee = fee

    def get_latest(self, project_id: str):
        return SimpleNamespace(status="current", latest_confirmed_fee=self.fee)


class _BasicInformationReader:
    def get_latest_confirmed(self, project_id: str):
        return SimpleNamespace(
            version=3,
            source_signature_hash="basic-hash",
            values={"dl_number": "DL-001", "product_description": "Connector"},
        )


class _Generator:
    def generate(self, *, project_id, output_dir, output_file_name, confirmed_fee, basic_information):
        from backend.application.confirmed_matrix_fee_evaluation_export_policy import require_output_dir

        require_output_dir(output_dir)
        path = output_dir / output_file_name
        path.write_text("confirmed fee", encoding="utf-8")
        return path


class _Outputs:
    def __init__(self) -> None:
        self.commands = []

    def register_output(self, command):
        self.commands.append(command)
        return command
