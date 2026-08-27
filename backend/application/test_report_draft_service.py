"""Create non-overwriting internal test-report drafts from confirmed authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import re
from typing import Protocol

from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand,
    ConfirmedMatrixTestRecordPreviewGroup,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewService,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
)


class TestReportDraftGenerationError(ValueError):
    """Raised when confirmed authority cannot generate a report draft."""

    __test__ = False


class TestReportDraftNotFoundError(LookupError):
    """Raised when the active confirmed Matrix cannot be found."""

    __test__ = False


@dataclass(frozen=True, slots=True)
class TestReportDraftData:
    """Semantic data written into one controlled E-3707_H draft."""

    project_id: str
    report_number: str
    product_name: str
    test_description: str
    applicable_specification: str
    received_samples_date: str
    description_part_number: str
    requestor: str
    project_leader: str
    confirmed_matrix_id: str
    groups: tuple[ConfirmedMatrixTestRecordPreviewGroup, ...]
    generated_on: date

    __test__ = False


class TestReportDraftWriter(Protocol):
    """Infrastructure boundary for editing a copied report template."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        report: TestReportDraftData,
    ) -> Path:
        """Generate a report draft and return the written path."""


@dataclass(frozen=True, slots=True)
class GenerateTestReportDraftCommand:
    """Inputs for one report draft generation."""

    project_id: str
    template_path: Path
    output_dir: Path


@dataclass(frozen=True, slots=True)
class TestReportDraftGenerationResult:
    """Generated draft location and source-authority identity."""

    project_id: str
    confirmed_matrix_id: str
    output_path: Path
    file_name: str
    confirmed_basic_information_version: int
    confirmed_basic_information_source_signature_hash: str

    __test__ = False


class TestReportDraftService:
    """Coordinate confirmed report data without exposing Word implementation details."""

    __test__ = False

    def __init__(
        self,
        *,
        preview_service: ConfirmedMatrixTestRecordPreviewService,
        basic_information_reader: ConfirmedBasicInformationReader,
        writer: TestReportDraftWriter,
    ) -> None:
        self._preview_service = preview_service
        self._basic_information = basic_information_reader
        self._writer = writer

    def generate(
        self,
        command: GenerateTestReportDraftCommand,
    ) -> TestReportDraftGenerationResult:
        """Generate one new draft in ConnLab-controlled storage."""
        template_path = Path(command.template_path)
        if template_path.suffix.lower() != ".docx":
            raise TestReportDraftGenerationError(
                f"Only .docx report templates are supported: {template_path}"
            )
        if not template_path.is_file():
            raise TestReportDraftGenerationError(
                f"Test report template does not exist: {template_path}"
            )

        basic_information = self._basic_information.get_latest_confirmed(
            command.project_id
        )
        if basic_information is None:
            raise TestReportDraftGenerationError(
                "Confirm Basic Information before generating a Test Report draft."
            )
        values = basic_information.values
        report_number = _required_value(values, "dl_number", "DL/LTR Number")
        product_name = _first_value(
            values,
            "product_description",
            "description_pn",
        )
        if not product_name:
            raise TestReportDraftGenerationError(
                "Confirmed Basic Information requires Product Description or Description P/N."
            )
        test_description = _required_value(values, "test_item", "Test Item")
        specification = _required_value(
            values,
            "applicable_specifications",
            "Applicable Specifications",
        )

        try:
            preview = self._preview_service.build_preview(
                BuildConfirmedMatrixTestRecordPreviewCommand(
                    project_id=command.project_id
                )
            )
        except ConfirmedMatrixTestRecordPreviewNotFoundError as exc:
            raise TestReportDraftNotFoundError(str(exc)) from exc
        if preview.preview_status != "ready" or not preview.groups:
            raise TestReportDraftGenerationError(
                "Active confirmed matrix has no reportable steps."
            )

        report = TestReportDraftData(
            project_id=command.project_id,
            report_number=report_number,
            product_name=product_name,
            test_description=test_description,
            applicable_specification=specification,
            received_samples_date=_value(values, "date_lab_received_samples"),
            description_part_number=_value(values, "description_pn"),
            requestor=_value(values, "requested_by"),
            project_leader=_value(values, "project_leader"),
            confirmed_matrix_id=preview.confirmed_matrix_id,
            groups=preview.groups,
            generated_on=date.today(),
        )
        project_dir = Path(command.output_dir) / _safe_file_component(command.project_id, 80)
        project_dir.mkdir(parents=True, exist_ok=True)
        file_name = _report_file_name(report)
        output_path = _reserve_non_overwriting_path(project_dir / file_name)
        try:
            written_path = self._writer.generate(
                template_path=template_path,
                output_path=output_path,
                report=report,
            )
        except (ValueError, FileNotFoundError, OSError) as exc:
            output_path.unlink(missing_ok=True)
            raise TestReportDraftGenerationError(str(exc)) from exc
        if Path(written_path) != output_path or not output_path.is_file():
            output_path.unlink(missing_ok=True)
            raise TestReportDraftGenerationError(
                "Test report writer did not produce the reserved draft path."
            )
        return TestReportDraftGenerationResult(
            project_id=command.project_id,
            confirmed_matrix_id=preview.confirmed_matrix_id,
            output_path=output_path,
            file_name=output_path.name,
            confirmed_basic_information_version=basic_information.version,
            confirmed_basic_information_source_signature_hash=(
                basic_information.source_signature_hash
            ),
        )


def _report_file_name(report: TestReportDraftData) -> str:
    report_number = _safe_file_component(report.report_number, 50)
    product_name = _safe_file_component(report.product_name, 80)
    test_description = _safe_file_component(report.test_description, 60)
    return (
        f"{report_number} {product_name} {test_description} "
        "Report_Rev_A_Draft.docx"
    )


def _reserve_non_overwriting_path(path: Path) -> Path:
    candidate = path
    index = 2
    while True:
        try:
            descriptor = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            candidate = path.with_name(f"{path.stem} ({index}){path.suffix}")
            index += 1
            continue
        os.close(descriptor)
        return candidate


def _safe_file_component(value: str, limit: int) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", " ".join(value.split()))
    cleaned = cleaned.strip(" .")[:limit].rstrip(" .")
    if not cleaned:
        raise TestReportDraftGenerationError("Report file identity is empty.")
    return cleaned


def _required_value(values: dict[str, str], key: str, label: str) -> str:
    value = _value(values, key)
    if not value:
        raise TestReportDraftGenerationError(
            f"Confirmed Basic Information requires {label}."
        )
    return value


def _first_value(values: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = _value(values, key)
        if value:
            return value
    return ""


def _value(values: dict[str, str], key: str) -> str:
    return str(values.get(key, "") or "").strip()
