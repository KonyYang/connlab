from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

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


def test_preview_downloads_draft_when_no_official_workspace_exists(tmp_path: Path) -> None:
    service = _service(tmp_path, workspace=None)

    preview = service.preview(PreviewFeeFormPublicationCommand("P1", _values()))

    assert preview.mode == "download"
    assert preview.status == "ready"


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
    assert preview.target_path == workspace.official_folder_path / "DL-001 Fee Form.xls"


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
        file_gateway=_FileGateway(),
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
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / output_file_name
        path.write_text("confirmed fee", encoding="utf-8")
        return path


class _FileGateway:
    def fingerprint(self, path: Path) -> str:
        return "fingerprint"

    def publish(self, *, staged_path, target_path, conflict_action, history_dir, expected_target_fingerprint):
        staged_path.replace(target_path)
        return None


class _Outputs:
    def __init__(self) -> None:
        self.commands = []

    def register_output(self, command):
        self.commands.append(command)
        return command
