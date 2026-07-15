from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ConfirmedMatrixFeeEvaluationExportNotFoundError,
    ConfirmedMatrixFeeEvaluationExportTimeoutError,
    ConfirmedMatrixFeeEvaluationExportUnavailableError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ExportConfirmedMatrixFeeEvaluationResult,
)
from backend.application.confirmed_matrix_fee_evaluation_export_timeout_service import (
    ConfirmedMatrixFeeEvaluationExportTimeoutService,
    FeeEvaluationExportProcessResult,
    command_from_payload,
    command_to_payload,
    result_from_payload,
    result_to_payload,
)
from backend.application.fee_evaluation_current_pricing_draft_guard import (
    CurrentFeePricingDraftRequiredError,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.application.fee_evaluation_export_lineage import (
    FeeEvaluationExportLineTrace,
)


def test_command_payload_round_trip_preserves_export_options(tmp_path: Path) -> None:
    command = ExportConfirmedMatrixFeeEvaluationCommand(
        project_id="P1",
        template_path=tmp_path / "template.xls",
        output_dir=tmp_path / "out",
        output_file_name="fee.xls",
        overwrite=True,
        allow_review_required=True,
        prepared_by="Operator",
        approved_by="Lead",
        connlab_user="ConnLab User",
        fill_mode="matrix_basic",
        pricing_draft_edit_id="fed-2",
        pricing_draft_generation=3,
        pricing_draft_payload_fingerprint="payload-fingerprint",
        pricing_draft_validation_token="validation-token",
    )

    restored = command_from_payload(command_to_payload(command))

    assert restored == command


def test_command_payload_round_trip_preserves_edited_values(tmp_path: Path) -> None:
    command = ExportConfirmedMatrixFeeEvaluationCommand(
        project_id="P1",
        template_path=tmp_path / "template.xls",
        output_dir=tmp_path / "out",
        fill_mode="matrix_basic",
        edited_values=FeeEvaluationEditedExportValues(
            rows=(
                FeeEvaluationEditedExportRow(
                    source_line_id="cmv-1:g1:cmr-1:1:0",
                    confirmed_group_id="cmg-1",
                    confirmed_row_id="cmr-1",
                    step_token="1",
                    step_index=0,
                    spend_time="1.5",
                    unit_price="20",
                    unit_type="per sample",
                    units="2",
                    base_fee="5",
                    discount="10%",
                    testing_fee="41",
                    notes="operator note",
                ),
            ),
            summary=FeeEvaluationEditedExportSummary(
                condition_confirmation_spend_time="0.5",
                external_cost="150",
                external_cost_note="tooling",
                lab_manpower_hourly_rate="200",
            ),
            manual_rows=(
                FeeEvaluationEditedManualRow(
                    row_kind="sample_preparation",
                    confirmed_group_id="cmg-1",
                    group_key="g1",
                    group_label="Group 1",
                    spend_time="0",
                    unit_price="8",
                    unit_type="per sample",
                    units="2",
                    base_fee="0",
                    discount="0%",
                    testing_fee="16",
                    notes="sample prep note",
                ),
            ),
        ),
    )

    restored = command_from_payload(command_to_payload(command))

    assert restored == command
    assert restored.edited_values is not None
    assert restored.edited_values.rows[0].notes == "operator note"
    assert restored.edited_values.manual_rows[0].confirmed_group_id == "cmg-1"
    assert restored.edited_values.manual_rows[0].group_key == "g1"
    assert restored.edited_values.manual_rows[0].group_label == "Group 1"


def test_command_payload_round_trip_preserves_basic_information_values(
    tmp_path: Path,
) -> None:
    command = ExportConfirmedMatrixFeeEvaluationCommand(
        project_id="P1",
        template_path=tmp_path / "template.xls",
        output_dir=tmp_path / "out",
        basic_information_values={
            "dl_number": "DL-BI",
            "product_description": "Connector from Basic Information",
            "requested_by": "Requester BI",
        },
    )

    restored = command_from_payload(command_to_payload(command))

    assert restored == command
    assert restored.basic_information_values == {
        "dl_number": "DL-BI",
        "product_description": "Connector from Basic Information",
        "requested_by": "Requester BI",
    }


def test_result_payload_round_trip_preserves_traceability() -> None:
    result = _result()

    restored = result_from_payload(result_to_payload(result))

    assert restored == result
    assert restored.line_traceability[0].matched_rule_version_id == "rules-v1"


def test_timeout_service_returns_success_result() -> None:
    service = ConfirmedMatrixFeeEvaluationExportTimeoutService(
        runner=_Runner(
            FeeEvaluationExportProcessResult(
                status="success",
                timed_out=False,
                exit_code=0,
                elapsed_seconds=1.0,
                stdout="{}",
                stderr="",
                payload={"result": result_to_payload(_result())},
            )
        )
    )

    result = service.export(_command())

    assert result.output_path == Path("C:/tmp/fee.xls")
    assert result.output_record_id == "por-1"
    assert result.line_traceability[0].confirmed_row_id == "cmr-1"


@pytest.mark.parametrize(
    ("status", "exc_type"),
    [
        ("business_error", ConfirmedMatrixFeeEvaluationExportError),
        ("not_found", ConfirmedMatrixFeeEvaluationExportNotFoundError),
        ("unavailable", ConfirmedMatrixFeeEvaluationExportUnavailableError),
        ("execution_failure", ConfirmedMatrixFeeEvaluationExportUnavailableError),
    ],
)
def test_timeout_service_maps_child_error_statuses(
    status: str, exc_type: type[Exception]
) -> None:
    service = ConfirmedMatrixFeeEvaluationExportTimeoutService(
        runner=_Runner(
            FeeEvaluationExportProcessResult(
                status=status,
                timed_out=False,
                exit_code=1,
                elapsed_seconds=1.0,
                stdout='{"status":"failure"}',
                stderr="stderr",
                payload={"error_message": "child failed"},
                error_message="child failed",
            )
        )
    )

    with pytest.raises(exc_type, match="child failed"):
        service.export(_command())


def test_timeout_service_maps_value_error() -> None:
    service = ConfirmedMatrixFeeEvaluationExportTimeoutService(
        runner=_Runner(
            FeeEvaluationExportProcessResult(
                status="value_error",
                timed_out=False,
                exit_code=1,
                elapsed_seconds=0.5,
                stdout="{}",
                stderr="",
                payload={"error_message": "bad path"},
                error_message="bad path",
            )
        )
    )

    with pytest.raises(ValueError, match="bad path"):
        service.export(_command())


def test_timeout_service_preserves_current_v2_conflict() -> None:
    service = ConfirmedMatrixFeeEvaluationExportTimeoutService(
        runner=_Runner(
            FeeEvaluationExportProcessResult(
                status="pricing_draft_conflict",
                timed_out=False,
                exit_code=1,
                elapsed_seconds=0.1,
                stdout="{}",
                stderr="",
                error_message="Reload and review before continuing.",
            )
        )
    )

    with pytest.raises(CurrentFeePricingDraftRequiredError, match="Reload and review"):
        service.export(_command())


def test_timeout_service_maps_timeout_with_cleanup_detail() -> None:
    service = ConfirmedMatrixFeeEvaluationExportTimeoutService(
        runner=_Runner(
            FeeEvaluationExportProcessResult(
                status="timeout",
                timed_out=True,
                exit_code=None,
                elapsed_seconds=90.0,
                stdout="partial stdout",
                stderr="partial stderr",
                payload={},
                manual_cleanup_warning="Inspect Excel manually.",
            )
        )
    )

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportTimeoutError) as exc_info:
        service.export(_command())

    assert exc_info.value.elapsed_seconds == 90.0
    assert exc_info.value.manual_cleanup_warning == "Inspect Excel manually."
    assert "timed out" in str(exc_info.value)


class _Runner:
    def __init__(self, result: FeeEvaluationExportProcessResult) -> None:
        self.result = result
        self.commands: list[ExportConfirmedMatrixFeeEvaluationCommand] = []

    def run(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> FeeEvaluationExportProcessResult:
        self.commands.append(command)
        return self.result


def _command() -> ExportConfirmedMatrixFeeEvaluationCommand:
    return ExportConfirmedMatrixFeeEvaluationCommand(
        project_id="P1",
        template_path=Path("C:/tmp/template.xls"),
        output_dir=Path("C:/tmp"),
        fill_mode="matrix_basic",
    )


def _result() -> ExportConfirmedMatrixFeeEvaluationResult:
    return ExportConfirmedMatrixFeeEvaluationResult(
        project_id="P1",
        output_path=Path("C:/tmp/fee.xls"),
        output_format="xls",
        status="generated",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=2,
        pricing_rule_version_id="rules-v1",
        pricing_effective_from="2026-06-03",
        prepared_by="Operator",
        approved_by=None,
        output_record_id="por-1",
        line_traceability=(
            FeeEvaluationExportLineTrace(
                line_id="line-1",
                group_key="g1",
                group_label="Group 1",
                confirmed_group_id="cmg-1",
                confirmed_row_id="cmr-1",
                source_row_id="smr-1",
                row_order=1,
                matched_rule_id="rule-1",
                matched_rule_version_id="rules-v1",
                step_tokens=("1",),
                cell_value="1 X",
            ),
        ),
        warnings=("Matrix basic fill only.",),
    )
