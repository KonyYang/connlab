"""Read-only compatibility baseline checks for real LTR workbook operations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.domain import ExternalResource, ExternalResourceType
from backend.shared.config import LtrWorkbookSettings
from backend.infrastructure.office import OfficeFacade, OfficeAutomationUnavailable


class LtrWorkbookCompatibilityNotFoundError(LookupError):
    """Raised when LTR workbook resource is not registered."""


@dataclass(frozen=True, slots=True)
class LtrWorkbookCompatibilityResult:
    """Compatibility baseline result for real workbook operations."""

    compatible: bool
    resource_path: str | None
    extension: str | None
    workbook_open_read_ok: bool
    workbook_read_only: bool | None
    sheet_names: tuple[str, ...]
    annual_sheet_names: tuple[str, ...]
    write_enabled: bool
    modify_password_configured: bool
    lock_dir_configured: bool
    backup_dir_configured: bool
    blockers: tuple[str, ...]
    notes: tuple[str, ...]


class ExternalResourceStorePort(Protocol):
    """Storage behavior required by workbook compatibility checks."""

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        """Return one configured external resource by type."""


class LtrWorkbookCompatibilityService:
    """Check real workbook compatibility through existing Office boundary only."""

    def __init__(
        self,
        resource_store: ExternalResourceStorePort,
        workbook_settings: LtrWorkbookSettings,
        office: OfficeFacade | None = None,
    ) -> None:
        self._resources = resource_store
        self._settings = workbook_settings
        self._office = office or OfficeFacade()

    def check(self) -> LtrWorkbookCompatibilityResult:
        """Return a read-only compatibility baseline report."""
        resource = self._resources.get_by_type(ExternalResourceType.LTR_WORKBOOK)
        if resource is None:
            raise LtrWorkbookCompatibilityNotFoundError(
                "External resource is not registered: ltr_workbook"
            )

        path = Path(resource.path)
        blockers: list[str] = []
        notes: list[str] = []
        sheet_names: tuple[str, ...] = ()
        annual_sheets: tuple[str, ...] = ()
        workbook_open_read_ok = False
        workbook_read_only: bool | None = None

        if not resource.active:
            blockers.append("LTR workbook resource is inactive.")
        if not path.is_file():
            blockers.append(f"LTR workbook file does not exist: {path}")

        extension = path.suffix.lower() or None
        if extension not in {".xls", ".xlsx"}:
            blockers.append(f"Unsupported workbook extension: {extension or '<none>'}")

        if not blockers:
            try:
                handle = self._office.open_excel_workbook(path, read_only=True)
                try:
                    workbook_open_read_ok = True
                    workbook_read_only = bool(getattr(handle.workbook, "ReadOnly", False))
                    sheet_names = tuple(
                        str(sheet.Name) for sheet in handle.workbook.Worksheets
                    )
                    annual_sheets = tuple(
                        name for name in sheet_names if re.fullmatch(r"\d{4}", name)
                    )
                finally:
                    handle.close(save_changes=False)
            except (
                OfficeAutomationUnavailable,
                FileNotFoundError,
                OSError,
                RuntimeError,
                ValueError,
                Exception,
            ) as exc:
                blockers.append(f"Workbook open/read check failed: {exc}")

        if not annual_sheets and workbook_open_read_ok:
            blockers.append("No annual year sheets were detected (expected names like 2026).")

        write_enabled = bool(self._settings.write_enabled)
        modify_password_configured = bool(self._settings.modify_password)
        lock_dir_configured = self._settings.lock_dir is not None
        backup_dir_configured = self._settings.backup_dir is not None

        if not write_enabled:
            notes.append("Write is disabled in local settings.")
        if not modify_password_configured:
            blockers.append("Workbook modify password is not configured.")
        if not lock_dir_configured:
            blockers.append("Workbook lock directory is not configured.")
        if not backup_dir_configured:
            blockers.append("Workbook backup directory is not configured.")

        return LtrWorkbookCompatibilityResult(
            compatible=len(blockers) == 0,
            resource_path=str(path),
            extension=extension,
            workbook_open_read_ok=workbook_open_read_ok,
            workbook_read_only=workbook_read_only,
            sheet_names=sheet_names,
            annual_sheet_names=annual_sheets,
            write_enabled=write_enabled,
            modify_password_configured=modify_password_configured,
            lock_dir_configured=lock_dir_configured,
            backup_dir_configured=backup_dir_configured,
            blockers=tuple(blockers),
            notes=tuple(notes),
        )
