"""Excel gateway for fee-evaluation workbook generation."""

from __future__ import annotations

from pathlib import Path

from backend.application.test_record_fee_dataset_preview_service import (
    TestRecordFeeDatasetPreview,
)
from backend.infrastructure.office.models import FeeEvaluationWorkbookWriteResult
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


class FeeEvaluationWorkbookGateway:
    """Generate fee-evaluation workbooks through a COM-only Excel boundary."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        preview: TestRecordFeeDatasetPreview,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Write fee-evaluation content using Excel COM when available."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() not in {".xls", ".xlsx"}:
            raise ValueError(f"Unsupported fee template type: {template}")
        if not template.is_file():
            raise FileNotFoundError(f"Template does not exist: {template}")
        if not target.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        try:
            import win32com.client  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise OfficeAutomationUnavailable(
                "Excel COM automation is required for fee template generation."
            ) from exc

        excel = win32com.client.DispatchEx("Excel.Application")
        workbook = None
        try:
            excel.Visible = False
            excel.DisplayAlerts = False
            workbook = excel.Workbooks.Open(str(template))
            summary = preview.fee_dataset.summary if preview.fee_dataset is not None else None
            sheet = workbook.Worksheets.Item(1)
            sheet.Cells(1, 1).Value = "ConnLab Generated Fee Evaluation"
            sheet.Cells(2, 1).Value = f"Project ID: {preview.project_id}"
            sheet.Cells(3, 1).Value = f"Draft ID: {preview.draft_id}"
            if summary is not None:
                sheet.Cells(4, 1).Value = f"Group count: {summary.group_count}"
                sheet.Cells(5, 1).Value = f"Step count: {summary.step_count}"
                sheet.Cells(6, 1).Value = (
                    f"Explicit duration days: {summary.explicit_duration_days}"
                )
            workbook.SaveAs(str(target))
        finally:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
            excel.Quit()

        return FeeEvaluationWorkbookWriteResult(
            output_path=target,
            status="generated",
            warnings=("Pricing values are not calculated by ConnLab.",),
        )
