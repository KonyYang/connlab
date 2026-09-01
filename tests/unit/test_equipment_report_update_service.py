from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from backend.application.current_report_update_service import CurrentReportArtifact
from backend.application.equipment_report_update_service import (
    EquipmentListExternalOverride,
    EquipmentListUpdateCommand,
    EquipmentReportUpdateError,
    EquipmentReportUpdateService,
)
from backend.application.external_excel_read_service import (
    EquipmentCalibrationReadResult,
    EquipmentCalibrationRow,
)
from backend.infrastructure.office.equipment_id_document_reader import (
    EquipmentIdDocumentReadResult,
)


@dataclass
class _Workspace:
    local_workspace_path: str


class _WorkspaceStore:
    def __init__(self, root: Path) -> None:
        self.workspace = _Workspace(str(root))

    def get_by_project(self, _project_id: str) -> _Workspace:
        return self.workspace


class _SourceReader:
    def __init__(self, source: Path, references: tuple[str, ...]) -> None:
        self.result = EquipmentIdDocumentReadResult(source, references)

    def read(self, _source_path: Path) -> EquipmentIdDocumentReadResult:
        return self.result


class _CatalogReader:
    def __init__(self, workbook: Path, rows: tuple[EquipmentCalibrationRow, ...]) -> None:
        self.result = EquipmentCalibrationReadResult(str(workbook), ("All Equip.",), rows)

    def read_equipment_calibrations(self) -> EquipmentCalibrationReadResult:
        return self.result


class _CurrentReportUpdates:
    def __init__(self) -> None:
        self.commands: list[object] = []
        self.report = CurrentReportArtifact(
            status="ready",
            mode="official",
            file_name="DL-001 Report_Rev_A.docx",
            file_path=Path("report.docx"),
            file_sha256="r" * 64,
            history_root=Path("History/Report"),
        )

    def get_current_report(self, _project_id: str) -> CurrentReportArtifact:
        return self.report

    def update_equipment_list(self, command: object) -> str:
        self.commands.append(command)
        return "updated"


def _service(tmp_path: Path, references: tuple[str, ...], rows: tuple[EquipmentCalibrationRow, ...]):
    source = tmp_path / "EquipmentID.docx"
    source.write_bytes(b"equipment-source")
    workbook = tmp_path / "equipment.xlsx"
    workbook.write_bytes(b"equipment-catalog")
    updates = _CurrentReportUpdates()
    service = EquipmentReportUpdateService(
        workspace_store=_WorkspaceStore(tmp_path),
        source_reader=_SourceReader(source, references),
        catalog_reader=_CatalogReader(workbook, rows),
        current_report_updates=updates,
        today=lambda: date(2026, 8, 31),
    )
    return service, updates


def test_preview_matches_equipment_reference_and_warns_when_calibration_expired(
    tmp_path: Path,
) -> None:
    service, _updates = _service(
        tmp_path,
        ("Fixture Q-0033",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-Q-0033",
                equipment_name="Digital multimeter",
                manufacturer="Keysight",
                last_calibration_date="01 Jan 2025",
                calibration_due_date="01 Jan 2026",
                source_sheet="All Equip.",
            ),
        ),
    )

    preview = service.preview(project_id="P1")

    assert preview.status == "ready"
    assert preview.source_file_name == "EquipmentID.docx"
    assert preview.catalog_file_name == "equipment.xlsx"
    assert preview.rows[0].status == "matched"
    assert preview.rows[0].id_number == "DG-Q-0033"
    assert preview.rows[0].expired is True
    assert preview.requires_expired_acknowledgement is True
    assert any("expired" in warning.lower() for warning in preview.warnings)


def test_preview_formats_legacy_excel_iso_dates_for_the_report(tmp_path: Path) -> None:
    service, _updates = _service(
        tmp_path,
        ("DG-Q-0033",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-Q-0033",
                equipment_name="Test Probe",
                manufacturer="SunHo (SH9113)",
                last_calibration_date="2024-08-08T00:00:00+00:00",
                calibration_due_date="2025-08-07T00:00:00+00:00",
                source_sheet="All Equip.",
            ),
        ),
    )

    preview = service.preview(project_id="P1")

    assert preview.status == "ready"
    assert preview.rows[0].last_calibration == "08-Aug-2024"
    assert preview.rows[0].calibration_due == "07-Aug-2025"
    assert preview.rows[0].expired is True


def test_preview_accepts_not_applicable_calibration_dates(tmp_path: Path) -> None:
    service, _updates = _service(
        tmp_path,
        ("DG-L-0002",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-L-0002",
                equipment_name="Stereo Microscope",
                manufacturer="Nikon",
                last_calibration_date="Not applicable",
                calibration_due_date="Not applicable",
                source_sheet="All Equip.",
            ),
        ),
    )

    preview = service.preview(project_id="P1")

    assert preview.status == "ready"
    assert preview.rows[0].calibration_due == "Not applicable"
    assert preview.rows[0].expired is False


def test_unmatched_reference_is_published_as_an_id_only_manual_placeholder(
    tmp_path: Path,
) -> None:
    service, updates = _service(tmp_path, ("DG-Q-0851",), tuple())

    preview = service.preview(project_id="P1")
    result = service.update(
        EquipmentListUpdateCommand(
            project_id="P1",
            expected_report_sha256="r" * 64,
            expected_source_sha256=preview.source_sha256 or "",
            expected_catalog_sha256=preview.catalog_sha256 or "",
            acknowledge_expired=False,
            external_overrides=tuple(),
            updated_by="Lab User",
        )
    )

    assert preview.status == "ready"
    assert preview.blockers == tuple()
    assert preview.rows[0].status == "unmatched"
    assert preview.rows[0].id_number == "DG-Q-0851"
    assert preview.rows[0].item == ""
    assert any("complete it manually in Word" in warning for warning in preview.warnings)
    assert result == "updated"
    assert updates.commands[0].rows[0].id_number == "DG-Q-0851"


def test_unmatched_reference_accepts_a_complete_external_override(tmp_path: Path) -> None:
    service, _updates = _service(tmp_path, ("Customer fixture A",), tuple())

    ready = service.preview(
        project_id="P1",
        external_overrides=(
            EquipmentListExternalOverride(
                source_reference="Customer fixture A",
                item="Customer fixture",
                manufacturer="Customer supplied",
                id_number="N/A",
                last_calibration="N/A",
                calibration_due="N/A",
                reason="Customer-owned fixture is outside the laboratory calibration catalog.",
            ),
        ),
    )

    assert ready.status == "ready"
    assert ready.rows[0].status == "external"
    assert ready.rows[0].item == "Customer fixture"


def test_external_equipment_with_expired_calibration_requires_acknowledgement(
    tmp_path: Path,
) -> None:
    service, _updates = _service(tmp_path, ("Customer fixture A",), tuple())
    preview = service.preview(
        project_id="P1",
        external_overrides=(
            EquipmentListExternalOverride(
                source_reference="Customer fixture A",
                item="Customer fixture",
                manufacturer="Customer supplied",
                id_number="CF-001",
                last_calibration="01 Jan 2025",
                calibration_due="01 Jan 2026",
                reason="Customer-owned calibrated fixture.",
            ),
        ),
    )

    assert preview.status == "ready"
    assert preview.rows[0].expired is True
    assert preview.requires_expired_acknowledgement is True
    assert any("CF-001" in warning for warning in preview.warnings)


def test_external_equipment_rejects_an_unrecognizable_calibration_due_date(
    tmp_path: Path,
) -> None:
    service, _updates = _service(tmp_path, ("Customer fixture A",), tuple())

    preview = service.preview(
        project_id="P1",
        external_overrides=(
            EquipmentListExternalOverride(
                source_reference="Customer fixture A",
                item="Customer fixture",
                manufacturer="Customer supplied",
                id_number="CF-001",
                last_calibration="01 Jan 2025",
                calibration_due="sometime next year",
                reason="Customer-owned calibrated fixture.",
            ),
        ),
    )

    assert preview.status == "blocked"
    assert preview.rows[0].status == "unmatched"
    assert "recognizable Cal. Due date" in preview.blockers[0]


def test_preview_can_match_an_exact_equipment_name(tmp_path: Path) -> None:
    service, _updates = _service(
        tmp_path,
        ("Digital multimeter",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-Q-0033",
                equipment_name="Digital multimeter",
                manufacturer="Keysight",
                last_calibration_date="01 Jan 2026",
                calibration_due_date="01 Jan 2027",
                source_sheet="All Equip.",
            ),
        ),
    )

    preview = service.preview(project_id="P1")

    assert preview.status == "ready"
    assert preview.rows[0].id_number == "DG-Q-0033"


def test_preview_blocks_an_incomplete_calibration_catalog_row(tmp_path: Path) -> None:
    service, _updates = _service(
        tmp_path,
        ("DG-Q-0033",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-Q-0033",
                equipment_name="Digital multimeter",
                manufacturer=None,
                last_calibration_date="01 Jan 2026",
                calibration_due_date="01 Jan 2027",
                source_sheet="All Equip.",
            ),
        ),
    )

    preview = service.preview(project_id="P1")

    assert preview.status == "blocked"
    assert preview.rows[0].status == "incomplete"
    assert "Manufacturer" in preview.blockers[0]


def test_update_rechecks_sources_and_requires_expired_acknowledgement(tmp_path: Path) -> None:
    service, updates = _service(
        tmp_path,
        ("DG-Q-0033",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-Q-0033",
                equipment_name="Digital multimeter",
                manufacturer="Keysight",
                last_calibration_date="01 Jan 2025",
                calibration_due_date="01 Jan 2026",
                source_sheet="All Equip.",
            ),
        ),
    )
    preview = service.preview(project_id="P1")

    with pytest.raises(EquipmentReportUpdateError, match="acknowledge"):
        service.update(
            EquipmentListUpdateCommand(
                project_id="P1",
                expected_report_sha256="r" * 64,
                expected_source_sha256=preview.source_sha256,
                expected_catalog_sha256=preview.catalog_sha256,
                acknowledge_expired=False,
                external_overrides=tuple(),
                updated_by="Lab User",
            )
        )

    result = service.update(
        EquipmentListUpdateCommand(
            project_id="P1",
            expected_report_sha256="r" * 64,
            expected_source_sha256=preview.source_sha256,
            expected_catalog_sha256=preview.catalog_sha256,
            acknowledge_expired=True,
            external_overrides=tuple(),
            updated_by="Lab User",
        )
    )

    assert result == "updated"
    assert len(updates.commands) == 1
    assert updates.commands[0].rows[0].id_number == "DG-Q-0033"


def test_update_rejects_when_equipment_source_changes_after_preview(tmp_path: Path) -> None:
    service, _updates = _service(
        tmp_path,
        ("DG-Q-0033",),
        (
            EquipmentCalibrationRow(
                equipment_id="DG-Q-0033",
                equipment_name="Digital multimeter",
                manufacturer="Keysight",
                last_calibration_date="01 Jan 2026",
                calibration_due_date="01 Jan 2027",
                source_sheet="All Equip.",
            ),
        ),
    )
    preview = service.preview(project_id="P1")
    (tmp_path / "EquipmentID.docx").write_bytes(b"changed-equipment-source")

    with pytest.raises(EquipmentReportUpdateError, match="changed after preview"):
        service.update(
            EquipmentListUpdateCommand(
                project_id="P1",
                expected_report_sha256="r" * 64,
                expected_source_sha256=preview.source_sha256 or "",
                expected_catalog_sha256=preview.catalog_sha256 or "",
                acknowledge_expired=False,
                external_overrides=tuple(),
                updated_by="Lab User",
            )
        )


def test_missing_external_files_do_not_disclose_absolute_paths(tmp_path: Path) -> None:
    service, _updates = _service(tmp_path, ("DG-Q-0033",), tuple())
    (tmp_path / "EquipmentID.docx").unlink()
    (tmp_path / "equipment.xlsx").unlink()

    preview = service.preview(project_id="P1")

    assert preview.status == "blocked"
    assert any(message == "EquipmentID.docx was not found in the project folder." for message in preview.blockers)
    assert all(str(tmp_path) not in message for message in preview.blockers)
