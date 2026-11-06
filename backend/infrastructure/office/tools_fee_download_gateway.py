"""Produce a download in an owned temporary directory; never publish a project file."""
from pathlib import Path
from tempfile import TemporaryDirectory
from backend.infrastructure.office.fee_evaluation_workbook_gateway import FeeEvaluationWorkbookGateway


class ToolsFeeDownloadGateway:
    def download(self, *, template, basic_fill, edited_values):
        with TemporaryDirectory(prefix='connlab-planning-fee-') as directory:
            target = Path(directory) / ('Planning Fee Form' + template.suffix.lower())
            FeeEvaluationWorkbookGateway().generate_matrix_basic_fill(
                template_path=template, output_path=target, basic_fill=basic_fill,
                review_required=True, prepared_by=None, approved_by=None,
                edited_values=edited_values,
            )
            return target.name, target.read_bytes()
