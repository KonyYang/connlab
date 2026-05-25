"""Word gateway for writing generated test-record documents."""

from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document

from backend.infrastructure.office.models import TestRecordDocumentWriteResult


class TestRecordDocumentGateway:
    """Generate test-record `.docx` files through the infrastructure boundary."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        source_document_name: str,
        groups: tuple,
        warnings: tuple[str, ...],
    ) -> TestRecordDocumentWriteResult:
        """Copy the template and append deterministic test-record content."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() != ".docx":
            raise ValueError(f"Only .docx template is supported: {template}")
        if not template.is_file():
            raise FileNotFoundError(f"Template does not exist: {template}")
        if not target.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        shutil.copy2(template, target)
        document = Document(target)
        document.add_paragraph("ConnLab Generated Test Record")
        document.add_paragraph(f"Source document: {source_document_name}")
        for group in groups:
            document.add_paragraph(f"Group: {group.group_label}")
            table = document.add_table(rows=1, cols=7)
            headers = table.rows[0].cells
            headers[0].text = "Seq"
            headers[1].text = "Test Item"
            headers[2].text = "Condition"
            headers[3].text = "Method"
            headers[4].text = "Reference"
            headers[5].text = "Judgement"
            headers[6].text = "Duration"
            for step in group.steps:
                row = table.add_row().cells
                row[0].text = "" if step.sequence is None else str(step.sequence)
                row[1].text = step.test_item or ""
                row[2].text = step.condition_summary or ""
                row[3].text = step.method_summary or ""
                row[4].text = step.reference_standard or ""
                row[5].text = step.judgement_criteria or ""
                row[6].text = step.duration_hint or ""
        if warnings:
            document.add_paragraph("Warnings:")
            for warning in warnings:
                document.add_paragraph(f"- {warning}")
        document.save(target)
        return TestRecordDocumentWriteResult(
            output_path=target,
            status="generated",
            group_count=len(groups),
            warning_count=len(warnings),
            warnings=(),
        )

    def generate_from_confirmed_matrix(
        self,
        *,
        output_path: Path,
        project_id: str,
        project_no: str,
        product_description: str,
        applicable_specification: str,
        confirmed_matrix_id: str,
        groups: tuple,
    ) -> Path:
        """Generate a Test Record draft from active ConfirmedMatrix preview groups."""
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        document = Document()
        document.add_heading("ConnLab Test Record Draft", level=1)
        document.add_paragraph(f"Project ID: {project_id}")
        document.add_paragraph(f"Project No.: {project_no}")
        document.add_paragraph(f"Product Description: {product_description}")
        document.add_paragraph(f"Applicable Specification: {applicable_specification}")
        document.add_paragraph(f"Confirmed Matrix: {confirmed_matrix_id}")
        document.add_paragraph("Start Date/Time:")
        document.add_paragraph("Complete Date/Time:")
        document.add_paragraph("Equipment ID No.:")
        document.add_paragraph("Tested By:")

        for group in groups:
            document.add_heading(f"Group Number: {group.group_label}", level=2)
            document.add_paragraph(
                f"Sample Quantity & Number: {group.sample_quantity_expression}"
            )
            table = document.add_table(rows=1, cols=7)
            headers = table.rows[0].cells
            headers[0].text = "Step"
            headers[1].text = "Token"
            headers[2].text = "Test items"
            headers[3].text = "Test Method"
            headers[4].text = "Test conditions"
            headers[5].text = "Remarks"
            headers[6].text = "Execution data"
            for step in group.steps:
                row = table.add_row().cells
                row[0].text = str(step.sequence)
                row[1].text = step.raw_token
                row[2].text = step.test_item
                row[3].text = step.method
                row[4].text = step.condition
                row[5].text = step.requirement
                row[6].text = ""

        document.save(target)
        return target
