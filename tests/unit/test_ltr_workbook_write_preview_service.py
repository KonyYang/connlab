from datetime import date, datetime
from pathlib import Path

import pytest

from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWritePreviewError,
    LtrWorkbookWritePreviewService,
    PreviewLtrWorkbookWriteCommand,
)
from backend.domain import ApplicationForm, Project, ProjectStatus, SampleInfo
from backend.infrastructure.office.models import LtrWorkbookFormat, LtrWorkbookSnapshot
from backend.shared.config import LtrWorkbookSettings


def test_ltr_workbook_write_preview_maps_new_project_setup_to_columns(
    tmp_path: Path,
) -> None:
    """Preview maps confirmed project data and setup confirmation into A:Q."""
    workbook = tmp_path / "LTR_number.xls"
    service = LtrWorkbookWritePreviewService(
        project_store=_ProjectStore(),
        application_form_store=_FormStore(),
        sample_store=_SampleStore(),
        workbook_settings=LtrWorkbookSettings(path=workbook),
        snapshot_provider=_SnapshotProvider(workbook),
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrWorkbookWriteCommand(
            ltr_number="DL-2026-05-007",
            plan_date=date(2026, 5, 7),
            test_item="Qualification bend testing",
            sample_description="CoolPower connector samples",
            location="AIPG Guangzhou",
            test_type_in_sheet="Qualification",
            project_leader="Alice",
        ),
    )

    values_by_column = {column.column: column.value for column in preview.columns}
    assert preview.workbook_path == workbook
    assert preview.target_sheet == "2026"
    assert preview.target_row == 4
    assert preview.warnings == ()
    assert values_by_column == {
        "A": "May",
        "B": 2,
        "C": 7,
        "D": "DL-2026-05-007",
        "E": "New Product Development",
        "F": "CoolPower connector samples",
        "G": "Qualification bend testing",
        "H": "Qualification",
        "I": "Alice",
        "J": "AIPG Guangzhou",
        "K": "Alice",
        "L": None,
        "M": None,
        "N": "Keep in the Lab",
        "O": "No",
        "P": None,
        "Q": "PO pending",
    }


def test_ltr_workbook_write_preview_allows_unknown_row_without_snapshot(
    tmp_path: Path,
) -> None:
    """Preview remains no-write when no workbook snapshot is available."""
    service = LtrWorkbookWritePreviewService(
        project_store=_ProjectStore(),
        application_form_store=_FormStore(),
        sample_store=_SampleStore(),
        workbook_settings=LtrWorkbookSettings(path=tmp_path / "LTR_number.xls"),
    )

    preview = service.preview_project("P1", _command())

    assert preview.target_sheet == "2026"
    assert preview.target_row is None
    assert "Workbook snapshot is unavailable" in preview.warnings[0]


def test_ltr_workbook_write_preview_accepts_suffixed_dl_but_rejects_w_prefix(
    tmp_path: Path,
) -> None:
    """Preview accepts standard DL suffixes but rejects W-prefix values."""
    service = LtrWorkbookWritePreviewService(
        project_store=_ProjectStore(),
        application_form_store=_FormStore(),
        sample_store=_SampleStore(),
        workbook_settings=LtrWorkbookSettings(path=tmp_path / "LTR_number.xls"),
    )

    preview = service.preview_project("P1", _command(ltr_number="DL-2026-05-007A9"))
    assert preview.row_data.dl_number == "DL-2026-05-007A9"

    with pytest.raises(LtrWorkbookWritePreviewError, match="DL-YYYY-MM-NNN"):
        service.preview_project("P1", _command(ltr_number="W123"))


def test_ltr_workbook_write_preview_requires_setup_values(tmp_path: Path) -> None:
    """Required setup confirmation fields remain explicit in preview."""
    service = LtrWorkbookWritePreviewService(
        project_store=_ProjectStore(),
        application_form_store=_FormStore(),
        sample_store=_SampleStore(),
        workbook_settings=LtrWorkbookSettings(path=tmp_path / "LTR_number.xls"),
    )

    with pytest.raises(LtrWorkbookWritePreviewError, match="Test Item"):
        service.preview_project("P1", _command(test_item=" "))


def _command(
    *,
    ltr_number: str = "DL-2026-05-007",
    test_item: str = "Qualification bend testing",
) -> PreviewLtrWorkbookWriteCommand:
    """Return a complete preview command."""
    return PreviewLtrWorkbookWriteCommand(
        ltr_number=ltr_number,
        plan_date=date(2026, 5, 7),
        test_item=test_item,
        sample_description="CoolPower connector samples",
        location="AIPG Guangzhou",
        test_type_in_sheet="Qualification",
        project_leader="Alice",
    )


class _ProjectStore:
    def get(self, project_id: str) -> Project | None:
        return Project(
            project_id=project_id,
            project_no="PRJ-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
            business_unit="Power Solutions",
        )


class _FormStore:
    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [
            ApplicationForm(
                form_id="F1",
                project_id=project_id,
                form_no="E-3718",
                revision="H",
                requester="Alice",
                project_type="New Product Development",
                post_testing_disposition="Keep in the Lab",
                subcontract_allowed=False,
                additional_information="PO pending",
            )
        ]


class _SampleStore:
    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        return [
            SampleInfo(
                sample_id="S1",
                project_id=project_id,
                product_name="Connector",
                part_number="PN-001",
            )
        ]


class _SnapshotProvider:
    def __init__(self, workbook_path: Path) -> None:
        self._workbook_path = workbook_path

    def get_snapshot(self) -> LtrWorkbookSnapshot:
        return LtrWorkbookSnapshot(
            workbook_path=self._workbook_path,
            workbook_format=LtrWorkbookFormat.XLS,
            size_bytes=10,
            modified_time=datetime(2026, 5, 7, 12, 0, 0),
            sheet_names=("2026",),
            readable_sheet_names=("2026",),
            sheet_strategy="test",
            existing_ltr_numbers=("DL-2026-05-001", "DL-2026-05-002"),
        )
