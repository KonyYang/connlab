from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.ltr_workbook_compatibility_service import (
    LtrWorkbookCompatibilityNotFoundError,
    LtrWorkbookCompatibilityService,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)
from backend.shared.config import LtrWorkbookSettings


def test_ltr_workbook_compatibility_reports_blockers_for_missing_file(tmp_path: Path) -> None:
    service = LtrWorkbookCompatibilityService(
        resource_store=_Store(
            _resource(tmp_path / "missing.xls", active=True),
        ),
        workbook_settings=LtrWorkbookSettings(
            write_enabled=False,
            modify_password=None,
            lock_dir=None,
            backup_dir=None,
        ),
        office=_FakeOffice(),
    )

    result = service.check()

    assert result.compatible is False
    assert any("does not exist" in reason for reason in result.blockers)
    assert any("password is not configured" in reason for reason in result.blockers)
    assert any("lock directory is not configured" in reason for reason in result.blockers)
    assert any("backup directory is not configured" in reason for reason in result.blockers)


def test_ltr_workbook_compatibility_reads_sheet_names_when_openable(tmp_path: Path) -> None:
    workbook = tmp_path / "LTR_number.xls"
    workbook.write_bytes(b"dummy")
    service = LtrWorkbookCompatibilityService(
        resource_store=_Store(_resource(workbook, active=True)),
        workbook_settings=LtrWorkbookSettings(
            write_enabled=True,
            modify_password="pw",
            lock_dir=tmp_path / "locks",
            backup_dir=tmp_path / "backups",
        ),
        office=_FakeOffice(sheet_names=("2026", "Readme")),
    )

    result = service.check()

    assert result.workbook_open_read_ok is True
    assert result.sheet_names == ("2026", "Readme")
    assert result.annual_sheet_names == ("2026",)
    assert result.compatible is True


def test_ltr_workbook_compatibility_requires_registered_resource() -> None:
    service = LtrWorkbookCompatibilityService(
        resource_store=_Store(None),
        workbook_settings=LtrWorkbookSettings(),
        office=_FakeOffice(),
    )

    with pytest.raises(LtrWorkbookCompatibilityNotFoundError, match="not registered"):
        service.check()


def test_ltr_workbook_compatibility_converts_open_errors_to_blockers(tmp_path: Path) -> None:
    workbook = tmp_path / "LTR_number.xls"
    workbook.write_bytes(b"dummy")
    service = LtrWorkbookCompatibilityService(
        resource_store=_Store(_resource(workbook, active=True)),
        workbook_settings=LtrWorkbookSettings(
            write_enabled=True,
            modify_password="pw",
            lock_dir=tmp_path / "locks",
            backup_dir=tmp_path / "backups",
        ),
        office=_FailingOffice(),
    )

    result = service.check()

    assert result.compatible is False
    assert any("Workbook open/read check failed" in reason for reason in result.blockers)


class _Store:
    def __init__(self, resource: ExternalResource | None) -> None:
        self._resource = resource

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        if resource_type is ExternalResourceType.LTR_WORKBOOK:
            return self._resource
        return None


def _resource(path: Path, *, active: bool) -> ExternalResource:
    return ExternalResource(
        resource_id="R1",
        resource_type=ExternalResourceType.LTR_WORKBOOK,
        path=path,
        active=active,
        validation_status=ExternalResourceValidationStatus.NOT_VALIDATED,
    )


class _FakeOffice:
    def __init__(self, sheet_names: tuple[str, ...] = ("2026",)) -> None:
        self._sheet_names = sheet_names

    def open_excel_workbook(self, source_path: Path, *, read_only: bool = False, modify_password=None):
        return _FakeHandle(self._sheet_names)


class _FailingOffice:
    def open_excel_workbook(
        self,
        source_path: Path,
        *,
        read_only: bool = False,
        modify_password=None,
    ):
        raise RuntimeError("Excel COM automation failed during workbook open.")


class _FakeHandle:
    def __init__(self, sheet_names: tuple[str, ...]) -> None:
        self.workbook = _FakeWorkbook(sheet_names)

    def close(self, save_changes: bool = False) -> None:
        return None


class _FakeWorkbook:
    def __init__(self, sheet_names: tuple[str, ...]) -> None:
        self.ReadOnly = True
        self.Worksheets = [_FakeSheet(name) for name in sheet_names]


class _FakeSheet:
    def __init__(self, name: str) -> None:
        self.Name = name
