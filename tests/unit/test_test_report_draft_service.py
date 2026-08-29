from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.confirmed_matrix_test_record_preview_service import (
    ConfirmedMatrixTestRecordPreview,
    ConfirmedMatrixTestRecordPreviewGroup,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewStep,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_basic_information_service import (
    ProjectBasicInformationSampleRow,
)
from backend.application.test_report_draft_service import (
    GenerateTestReportDraftCommand,
    TestReportDraftGenerationError,
    TestReportDraftNotFoundError,
    TestReportDraftService,
)


def test_generates_report_model_from_confirmed_basic_information_and_active_matrix(
    tmp_path: Path,
) -> None:
    writer = _Writer()
    service = TestReportDraftService(
        preview_service=_PreviewService(_preview()),
        basic_information_reader=_BasicInformationReader(_basic_information()),
        writer=writer,
    )

    result = service.generate(
        GenerateTestReportDraftCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path / "generated_test_reports",
        )
    )

    report = writer.calls[0]["report"]
    assert report.report_number == "DL-2026-05-011"
    assert report.product_name == "Coolpower HDF 3.40mm"
    assert report.test_description == "Qualification Testing"
    assert report.applicable_specification == "GS-12-2113 Rev.7"
    assert report.received_samples_date == "2026-05-20"
    assert report.start_test_date == "2026-06-01"
    assert report.finish_test_date == "2026-07-15"
    assert report.description_part_number == "10179696-0001LF"
    assert report.requestor == "MP Cao"
    assert report.project_leader == "Even Yang"
    assert [row.product_name for row in report.sample_rows] == ["Pin", "Socket"]
    assert [row.lubricant for row in report.sample_rows] == ["No", "Yes"]
    assert report.confirmed_matrix_id == "cmv-1"
    assert report.groups == _preview().groups
    assert result.output_path.parent == tmp_path / "generated_test_reports" / "P1"
    assert result.file_name == (
        "DL-2026-05-011 Coolpower HDF 3.40mm Qualification Testing "
        "Report_Rev_A_Draft.docx"
    )
    assert result.confirmed_basic_information_version == 3


def test_uses_non_overwriting_draft_name(tmp_path: Path) -> None:
    output_dir = tmp_path / "generated_test_reports"
    project_dir = output_dir / "P1"
    project_dir.mkdir(parents=True)
    existing = project_dir / (
        "DL-2026-05-011 Coolpower HDF 3.40mm Qualification Testing "
        "Report_Rev_A_Draft.docx"
    )
    existing.write_bytes(b"manual draft")
    service = TestReportDraftService(
        preview_service=_PreviewService(_preview()),
        basic_information_reader=_BasicInformationReader(_basic_information()),
        writer=_Writer(),
    )

    result = service.generate(
        GenerateTestReportDraftCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=output_dir,
        )
    )

    assert result.output_path.name.endswith("Report_Rev_A_Draft (2).docx")
    assert existing.read_bytes() == b"manual draft"


def test_requires_confirmed_basic_information(tmp_path: Path) -> None:
    service = TestReportDraftService(
        preview_service=_PreviewService(_preview()),
        basic_information_reader=_BasicInformationReader(None),
        writer=_Writer(),
    )

    with pytest.raises(TestReportDraftGenerationError, match="Confirm Basic Information"):
        service.generate(
            GenerateTestReportDraftCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
            )
        )


def test_requires_active_confirmed_matrix(tmp_path: Path) -> None:
    service = TestReportDraftService(
        preview_service=_PreviewService(None),
        basic_information_reader=_BasicInformationReader(_basic_information()),
        writer=_Writer(),
    )

    with pytest.raises(TestReportDraftNotFoundError, match="Active confirmed matrix"):
        service.generate(
            GenerateTestReportDraftCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
            )
        )


def test_rejects_empty_active_matrix(tmp_path: Path) -> None:
    service = TestReportDraftService(
        preview_service=_PreviewService(
            ConfirmedMatrixTestRecordPreview(
                project_id="P1",
                confirmed_matrix_id="cmv-empty",
                preview_status="empty",
                groups=(),
            )
        ),
        basic_information_reader=_BasicInformationReader(_basic_information()),
        writer=_Writer(),
    )

    with pytest.raises(TestReportDraftGenerationError, match="no reportable steps"):
        service.generate(
            GenerateTestReportDraftCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
            )
        )


class _PreviewService:
    def __init__(self, preview: ConfirmedMatrixTestRecordPreview | None) -> None:
        self._preview = preview

    def build_preview(self, command):
        if self._preview is None:
            raise ConfirmedMatrixTestRecordPreviewNotFoundError(
                "Active confirmed matrix not found."
            )
        return self._preview


class _BasicInformationReader:
    def __init__(self, snapshot: ConfirmedBasicInformationSnapshot | None) -> None:
        self._snapshot = snapshot

    def get_latest_confirmed(self, project_id: str):
        return self._snapshot if project_id == "P1" else None


class _Writer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(self, **kwargs) -> Path:
        self.calls.append(kwargs)
        kwargs["output_path"].write_bytes(b"draft")
        return kwargs["output_path"]


def _template(tmp_path: Path) -> Path:
    path = tmp_path / "E-3707_H Laboratory Test Report.docx"
    path.write_bytes(b"template")
    return path


def _basic_information() -> ConfirmedBasicInformationSnapshot:
    return ConfirmedBasicInformationSnapshot(
        project_id="P1",
        version=3,
        values={
            "dl_number": "DL-2026-05-011",
            "product_description": "Coolpower HDF 3.40mm",
            "test_item": "Qualification Testing",
            "applicable_specifications": "GS-12-2113 Rev.7",
            "date_lab_received_samples": "2026-05-20",
            "start_test_date": "2026-06-01",
            "finish_test_date": "2026-07-15",
            "description_pn": "10179696-0001LF",
            "requested_by": "MP Cao",
            "project_leader": "Even Yang",
        },
        source_signature='{"source":"confirmed"}',
        confirmed_at="2026-05-21T00:00:00+00:00",
        confirmed_by="tester",
        sample_rows=(
            ProjectBasicInformationSampleRow(
                product_name="Pin",
                part_number="PN-PIN",
                lot_or_traceability="202510",
                material="C1100",
                plating="Ag",
                lubricant="No",
                housing_material="NA",
                row_index=0,
            ),
            ProjectBasicInformationSampleRow(
                product_name="Socket",
                part_number="PN-SOCKET",
                lot_or_traceability="202510",
                material="C19010",
                plating="Au",
                lubricant="Yes",
                housing_material="NA",
                row_index=1,
            ),
        ),
    )


def _preview() -> ConfirmedMatrixTestRecordPreview:
    return ConfirmedMatrixTestRecordPreview(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        preview_status="ready",
        groups=(
            ConfirmedMatrixTestRecordPreviewGroup(
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="5",
                step_count=2,
                steps=(
                    ConfirmedMatrixTestRecordPreviewStep(
                        sequence=1,
                        raw_token="1",
                        test_item="Visual Examination",
                        section="6.1",
                        method="EIA-364-18",
                        condition="10x min magnification",
                        requirement="No detrimental condition",
                    ),
                    ConfirmedMatrixTestRecordPreviewStep(
                        sequence=2,
                        raw_token="2",
                        test_item="LLCR",
                        section="6.2",
                        method="EIA-364-23",
                        condition="20mV max, 100mA max",
                        requirement="Initial ≤ 0.25mΩ",
                    ),
                ),
            ),
        ),
    )
