"""Standalone Fee downloads share the configured form and its normal writer."""
from typing import Protocol
from pathlib import Path
from backend.application.tools_matrix_snapshot import planning_snapshot
from backend.application.confirmed_matrix_fee_template_basic_fill_service import build_basic_fill_from_confirmed_snapshot
from backend.application.fee_evaluation_edited_export_values import FeeEvaluationEditedExportValues, edited_row_lookup


class PlanningFeeWriter(Protocol):
    def download(self, *, template: Path, basic_fill, edited_values: FeeEvaluationEditedExportValues) -> tuple[str, bytes]: ...


class ToolsFeeExportService:
    def __init__(self, writer: PlanningFeeWriter):
        self.writer = writer

    def export(self, *, matrix: dict, template: Path, edited_values: FeeEvaluationEditedExportValues):
        basic_fill = build_basic_fill_from_confirmed_snapshot(planning_snapshot(matrix))
        edited_row_lookup(edited_values, basic_fill)
        return self.writer.download(template=template, basic_fill=basic_fill, edited_values=edited_values)
