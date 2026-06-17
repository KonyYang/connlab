"""Timeout-aware wrapper for production Fee Evaluation workbook exports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ConfirmedMatrixFeeEvaluationExportNotFoundError,
    ConfirmedMatrixFeeEvaluationExportTimeoutError,
    ConfirmedMatrixFeeEvaluationExportUnavailableError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ExportConfirmedMatrixFeeEvaluationResult,
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


@dataclass(frozen=True, slots=True)
class FeeEvaluationExportProcessResult:
    """Structured parent result from a subprocess export attempt."""

    status: str
    timed_out: bool
    exit_code: int | None
    elapsed_seconds: float
    stdout: str
    stderr: str
    payload: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    manual_cleanup_warning: str | None = None


class FeeEvaluationExportProcessRunner(Protocol):
    """Subprocess runner port for production Fee Evaluation exports."""

    def run(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> FeeEvaluationExportProcessResult:
        """Run one export command behind a process timeout boundary."""


class ConfirmedMatrixFeeEvaluationExportTimeoutService:
    """Expose the export service contract through a subprocess timeout wrapper."""

    def __init__(self, *, runner: FeeEvaluationExportProcessRunner) -> None:
        self._runner = runner

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        """Run one export through the configured process runner."""
        result = self._runner.run(command)
        if result.status == "success":
            payload = result.payload.get("result", result.payload)
            return result_from_payload(payload)
        message = _error_message(result)
        if result.status == "business_error":
            raise ConfirmedMatrixFeeEvaluationExportError(message)
        if result.status == "not_found":
            raise ConfirmedMatrixFeeEvaluationExportNotFoundError(message)
        if result.status == "value_error":
            raise ValueError(message)
        if result.status == "timeout" or result.timed_out:
            warning = (
                result.manual_cleanup_warning
                or "Fee Evaluation export timed out. Excel cleanup is uncertain."
            )
            raise ConfirmedMatrixFeeEvaluationExportTimeoutError(
                message
                or f"Fee Evaluation export timed out after "
                f"{result.elapsed_seconds:.1f} seconds.",
                elapsed_seconds=result.elapsed_seconds,
                manual_cleanup_warning=warning,
            )
        raise ConfirmedMatrixFeeEvaluationExportUnavailableError(message)


def command_to_payload(command: ExportConfirmedMatrixFeeEvaluationCommand) -> dict[str, Any]:
    """Convert an export command to JSON-safe data."""
    return {
        "project_id": command.project_id,
        "template_path": str(command.template_path),
        "output_dir": str(command.output_dir) if command.output_dir else None,
        "output_file_name": command.output_file_name,
        "overwrite": command.overwrite,
        "allow_review_required": command.allow_review_required,
        "prepared_by": command.prepared_by,
        "approved_by": command.approved_by,
        "connlab_user": command.connlab_user,
        "fill_mode": command.fill_mode,
        "edited_values": _edited_values_to_payload(command.edited_values),
    }


def command_from_payload(payload: dict[str, Any]) -> ExportConfirmedMatrixFeeEvaluationCommand:
    """Rebuild an export command from JSON-safe data."""
    fill_mode = str(payload.get("fill_mode") or "fee_draft")
    if fill_mode not in {"fee_draft", "matrix_basic"}:
        raise ValueError(f"Unsupported fee evaluation export fill mode: {fill_mode}")
    output_dir = payload.get("output_dir")
    return ExportConfirmedMatrixFeeEvaluationCommand(
        project_id=str(payload["project_id"]),
        template_path=Path(str(payload["template_path"])),
        output_dir=Path(str(output_dir)) if output_dir else None,
        output_file_name=_optional_str(payload.get("output_file_name")),
        overwrite=bool(payload.get("overwrite", False)),
        allow_review_required=bool(payload.get("allow_review_required", False)),
        prepared_by=_optional_str(payload.get("prepared_by")),
        approved_by=_optional_str(payload.get("approved_by")),
        connlab_user=_optional_str(payload.get("connlab_user")),
        fill_mode=fill_mode,  # type: ignore[arg-type]
        edited_values=_edited_values_from_payload(payload.get("edited_values")),
    )


def result_to_payload(result: ExportConfirmedMatrixFeeEvaluationResult) -> dict[str, Any]:
    """Convert an export result to JSON-safe data."""
    return {
        "project_id": result.project_id,
        "output_path": str(result.output_path),
        "output_format": result.output_format,
        "status": result.status,
        "confirmed_matrix_id": result.confirmed_matrix_id,
        "confirmed_revision": result.confirmed_revision,
        "pricing_rule_version_id": result.pricing_rule_version_id,
        "pricing_effective_from": result.pricing_effective_from,
        "prepared_by": result.prepared_by,
        "approved_by": result.approved_by,
        "output_record_id": result.output_record_id,
        "line_traceability": [
            _line_trace_to_payload(line) for line in result.line_traceability
        ],
        "warnings": list(result.warnings),
    }


def result_from_payload(payload: dict[str, Any]) -> ExportConfirmedMatrixFeeEvaluationResult:
    """Rebuild an export result from JSON-safe data."""
    return ExportConfirmedMatrixFeeEvaluationResult(
        project_id=str(payload["project_id"]),
        output_path=Path(str(payload["output_path"])),
        output_format=str(payload["output_format"]),
        status=str(payload["status"]),
        confirmed_matrix_id=str(payload["confirmed_matrix_id"]),
        confirmed_revision=int(payload["confirmed_revision"]),
        pricing_rule_version_id=str(payload.get("pricing_rule_version_id") or ""),
        pricing_effective_from=_optional_str(payload.get("pricing_effective_from")),
        prepared_by=_optional_str(payload.get("prepared_by")),
        approved_by=_optional_str(payload.get("approved_by")),
        output_record_id=_optional_str(payload.get("output_record_id")),
        line_traceability=tuple(
            _line_trace_from_payload(line)
            for line in payload.get("line_traceability", [])
        ),
        warnings=tuple(str(warning) for warning in payload.get("warnings", [])),
    )


def _line_trace_to_payload(line: FeeEvaluationExportLineTrace) -> dict[str, Any]:
    return {
        "line_id": line.line_id,
        "group_key": line.group_key,
        "group_label": line.group_label,
        "confirmed_group_id": line.confirmed_group_id,
        "confirmed_row_id": line.confirmed_row_id,
        "source_row_id": line.source_row_id,
        "row_order": line.row_order,
        "matched_rule_id": line.matched_rule_id,
        "matched_rule_version_id": line.matched_rule_version_id,
        "step_tokens": list(line.step_tokens),
        "cell_value": line.cell_value,
    }


def _line_trace_from_payload(payload: dict[str, Any]) -> FeeEvaluationExportLineTrace:
    return FeeEvaluationExportLineTrace(
        line_id=str(payload["line_id"]),
        group_key=str(payload["group_key"]),
        group_label=str(payload["group_label"]),
        confirmed_group_id=str(payload["confirmed_group_id"]),
        confirmed_row_id=str(payload["confirmed_row_id"]),
        source_row_id=_optional_str(payload.get("source_row_id")),
        row_order=int(payload["row_order"]),
        matched_rule_id=_optional_str(payload.get("matched_rule_id")),
        matched_rule_version_id=_optional_str(payload.get("matched_rule_version_id")),
        step_tokens=tuple(str(token) for token in payload.get("step_tokens", [])),
        cell_value=_optional_str(payload.get("cell_value")),
    )


def _error_message(result: FeeEvaluationExportProcessResult) -> str:
    raw = (
        result.error_message
        or result.payload.get("error_message")
        or result.payload.get("message")
    )
    if raw:
        return str(raw)
    if result.status == "timeout" or result.timed_out:
        return (
            "Fee Evaluation export timed out after "
            f"{result.elapsed_seconds:.1f} seconds."
        )
    return "Fee Evaluation export failed in a subprocess."


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _edited_values_to_payload(
    edited_values: FeeEvaluationEditedExportValues | None,
) -> dict[str, Any] | None:
    if edited_values is None:
        return None
    return {
        "rows": [
            {
                "source_line_id": row.source_line_id,
                "confirmed_group_id": row.confirmed_group_id,
                "confirmed_row_id": row.confirmed_row_id,
                "step_token": row.step_token,
                "step_index": row.step_index,
                "spend_time": row.spend_time,
                "unit_price": row.unit_price,
                "unit_type": row.unit_type,
                "units": row.units,
                "base_fee": row.base_fee,
                "discount": row.discount,
                "testing_fee": row.testing_fee,
                "notes": row.notes,
            }
            for row in edited_values.rows
        ],
        "summary": {
            "condition_confirmation_spend_time": (
                edited_values.summary.condition_confirmation_spend_time
            ),
            "external_cost": edited_values.summary.external_cost,
            "external_cost_note": edited_values.summary.external_cost_note,
            "lab_manpower_hourly_rate": edited_values.summary.lab_manpower_hourly_rate,
        },
        "manual_rows": [
            {
                "row_kind": row.row_kind,
                "confirmed_group_id": row.confirmed_group_id,
                "group_key": row.group_key,
                "group_label": row.group_label,
                "spend_time": row.spend_time,
                "unit_price": row.unit_price,
                "unit_type": row.unit_type,
                "units": row.units,
                "base_fee": row.base_fee,
                "discount": row.discount,
                "testing_fee": row.testing_fee,
                "notes": row.notes,
            }
            for row in edited_values.manual_rows
        ],
    }


def _edited_values_from_payload(payload: Any) -> FeeEvaluationEditedExportValues | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("Fee Evaluation edited export payload is invalid.")
    summary = payload.get("summary") or {}
    return FeeEvaluationEditedExportValues(
        rows=tuple(
            FeeEvaluationEditedExportRow(
                source_line_id=str(row.get("source_line_id") or ""),
                confirmed_group_id=str(row.get("confirmed_group_id") or ""),
                confirmed_row_id=str(row.get("confirmed_row_id") or ""),
                step_token=str(row.get("step_token") or ""),
                step_index=int(row.get("step_index") or 0),
                spend_time=str(row.get("spend_time") or ""),
                unit_price=str(row.get("unit_price") or ""),
                unit_type=str(row.get("unit_type") or ""),
                units=str(row.get("units") or ""),
                base_fee=str(row.get("base_fee") or ""),
                discount=str(row.get("discount") or ""),
                testing_fee=str(row.get("testing_fee") or ""),
                notes=str(row.get("notes") or ""),
            )
            for row in payload.get("rows", [])
        ),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time=str(
                summary.get("condition_confirmation_spend_time") or ""
            ),
            external_cost=str(summary.get("external_cost") or ""),
            external_cost_note=str(summary.get("external_cost_note") or ""),
            lab_manpower_hourly_rate=str(summary.get("lab_manpower_hourly_rate") or ""),
        ),
        manual_rows=tuple(
            FeeEvaluationEditedManualRow(
                row_kind=str(row.get("row_kind") or ""),
                confirmed_group_id=str(row.get("confirmed_group_id") or ""),
                group_key=str(row.get("group_key") or ""),
                group_label=str(row.get("group_label") or ""),
                spend_time=str(row.get("spend_time") or ""),
                unit_price=str(row.get("unit_price") or ""),
                unit_type=str(row.get("unit_type") or ""),
                units=str(row.get("units") or ""),
                base_fee=str(row.get("base_fee") or ""),
                discount=str(row.get("discount") or ""),
                testing_fee=str(row.get("testing_fee") or ""),
                notes=str(row.get("notes") or ""),
            )
            for row in payload.get("manual_rows", [])
        ),
    )
