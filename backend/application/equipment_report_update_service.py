"""Preview equipment sources and coordinate one controlled Equipment List update."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
from pathlib import Path
import re
from typing import Callable, Protocol

from backend.application.current_report_update_service import (
    CurrentReportArtifact,
    CurrentReportUpdateError,
    UpdateCurrentEquipmentListReportCommand,
)
class EquipmentReportUpdateError(ValueError):
    """Raised when an equipment-list update cannot be performed safely."""


class WorkspaceStore(Protocol):
    def get_by_project(self, project_id: str): ...


class EquipmentSourceReader(Protocol):
    def read(self, source_path: Path): ...


class EquipmentCatalogReader(Protocol):
    def read_equipment_calibrations(self): ...


class CurrentReportUpdates(Protocol):
    def get_current_report(self, project_id: str) -> CurrentReportArtifact: ...
    def update_equipment_list(self, command: UpdateCurrentEquipmentListReportCommand): ...


@dataclass(frozen=True, slots=True)
class EquipmentListExternalOverride:
    source_reference: str
    item: str
    manufacturer: str
    id_number: str
    last_calibration: str
    calibration_due: str
    reason: str


@dataclass(frozen=True, slots=True)
class EquipmentListReportRow:
    source_reference: str
    status: str
    item: str
    manufacturer: str
    id_number: str
    last_calibration: str
    calibration_due: str
    source_sheet: str | None
    expired: bool
    external_reason: str | None = None


@dataclass(frozen=True, slots=True)
class EquipmentListPreview:
    project_id: str
    status: str
    current_report: CurrentReportArtifact
    source_file_name: str | None
    source_sha256: str | None
    catalog_file_name: str | None
    catalog_sha256: str | None
    rows: tuple[EquipmentListReportRow, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    requires_expired_acknowledgement: bool


@dataclass(frozen=True, slots=True)
class EquipmentListUpdateCommand:
    project_id: str
    expected_report_sha256: str
    expected_source_sha256: str
    expected_catalog_sha256: str
    acknowledge_expired: bool
    external_overrides: tuple[EquipmentListExternalOverride, ...]
    updated_by: str


class EquipmentReportUpdateService:
    """Join one project EquipmentID.docx to the configured calibration catalog."""

    def __init__(
        self,
        *,
        workspace_store: WorkspaceStore,
        source_reader: EquipmentSourceReader,
        catalog_reader: EquipmentCatalogReader,
        current_report_updates: CurrentReportUpdates,
        today: Callable[[], date],
    ) -> None:
        self._workspaces = workspace_store
        self._source_reader = source_reader
        self._catalog_reader = catalog_reader
        self._reports = current_report_updates
        self._today = today

    def preview(
        self,
        *,
        project_id: str,
        external_overrides: tuple[EquipmentListExternalOverride, ...] = tuple(),
    ) -> EquipmentListPreview:
        report = self._reports.get_current_report(project_id)
        blockers = list(_report_blockers(report))
        warnings: list[str] = []
        rows: list[EquipmentListReportRow] = []
        source_file_name: str | None = None
        source_sha256: str | None = None
        catalog_file_name: str | None = None
        catalog_sha256: str | None = None

        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None:
            blockers.append("Create the official project folder before updating Equipment List.")
        else:
            source_path = Path(workspace.local_workspace_path) / "EquipmentID.docx"
            source_file_name = source_path.name
            try:
                source = self._source_reader.read(source_path)
                source_sha256 = _fingerprint(source.source_path)
            except FileNotFoundError:
                blockers.append(
                    "EquipmentID.docx was not found in the project folder."
                )
                source = None
            except (OSError, RuntimeError, ValueError) as exc:
                blockers.append(f"EquipmentID.docx cannot be read. {exc}")
                source = None

            try:
                catalog = self._catalog_reader.read_equipment_calibrations()
                catalog_path = Path(catalog.resource_path)
                catalog_file_name = catalog_path.name
                catalog_sha256 = _fingerprint(catalog_path)
            except (FileNotFoundError, OSError, RuntimeError, ValueError):
                blockers.append(
                    "Equipment calibration Excel is unavailable or does not match a supported "
                    "Equipment layout. Check the active path in Settings."
                )
                catalog = None

            if source is not None and catalog is not None:
                rows, row_blockers, row_warnings = self._project_rows(
                    source.references,
                    catalog.rows,
                    external_overrides,
                )
                blockers.extend(row_blockers)
                warnings.extend(row_warnings)

        requires_ack = any(row.expired for row in rows)
        return EquipmentListPreview(
            project_id=project_id,
            status="blocked" if blockers else "ready",
            current_report=report,
            source_file_name=source_file_name,
            source_sha256=source_sha256,
            catalog_file_name=catalog_file_name,
            catalog_sha256=catalog_sha256,
            rows=tuple(rows),
            blockers=tuple(blockers),
            warnings=tuple(warnings),
            requires_expired_acknowledgement=requires_ack,
        )

    def update(self, command: EquipmentListUpdateCommand):
        preview = self.preview(
            project_id=command.project_id,
            external_overrides=command.external_overrides,
        )
        if preview.blockers:
            raise EquipmentReportUpdateError(" ".join(preview.blockers))
        if (
            preview.source_sha256 != command.expected_source_sha256
            or preview.catalog_sha256 != command.expected_catalog_sha256
        ):
            raise EquipmentReportUpdateError(
                "EquipmentID.docx or Equipment calibration Excel changed after preview. "
                "Preview Equipment List again."
            )
        if preview.requires_expired_acknowledgement and not command.acknowledge_expired:
            raise EquipmentReportUpdateError(
                "Explicitly acknowledge the expired calibration warning before updating."
            )
        try:
            return self._reports.update_equipment_list(
                UpdateCurrentEquipmentListReportCommand(
                    project_id=command.project_id,
                    expected_report_sha256=command.expected_report_sha256,
                    rows=preview.rows,
                    updated_by=command.updated_by,
                )
            )
        except CurrentReportUpdateError as exc:
            raise EquipmentReportUpdateError(str(exc)) from exc

    def _project_rows(
        self,
        references: tuple[str, ...],
        catalog_rows: tuple[object, ...],
        external_overrides: tuple[EquipmentListExternalOverride, ...],
    ) -> tuple[list[EquipmentListReportRow], list[str], list[str]]:
        indexed: dict[str, list[object]] = {}
        for catalog_row in catalog_rows:
            keys = {equipment_reference_key(catalog_row.equipment_id)}
            if (catalog_row.equipment_name or "").strip():
                keys.add(equipment_reference_key(catalog_row.equipment_name))
            for key in keys:
                indexed.setdefault(key, []).append(catalog_row)
        overrides = {
            equipment_reference_key(item.source_reference): item
            for item in external_overrides
        }
        rows: list[EquipmentListReportRow] = []
        blockers: list[str] = []
        warnings: list[str] = []
        for reference in references:
            key = equipment_reference_key(reference)
            matches = indexed.get(key, [])
            if len(matches) == 1:
                catalog_row = matches[0]
                missing = [
                    label
                    for label, value in (
                        ("Item", catalog_row.equipment_name),
                        ("Manufacturer", catalog_row.manufacturer),
                        ("Last Cal.", catalog_row.last_calibration_date),
                        ("Cal. Due", catalog_row.calibration_due_date),
                    )
                    if not (value or "").strip()
                ]
                due_date = _parse_date(catalog_row.calibration_due_date)
                if not missing and due_date is None:
                    missing.append("a recognizable Cal. Due date")
                expired = _is_expired(catalog_row.calibration_due_date, self._today())
                row = EquipmentListReportRow(
                    source_reference=reference,
                    status="incomplete" if missing else "matched",
                    item=catalog_row.equipment_name or "",
                    manufacturer=catalog_row.manufacturer or "",
                    id_number=catalog_row.equipment_id,
                    last_calibration=catalog_row.last_calibration_date or "",
                    calibration_due=catalog_row.calibration_due_date or "",
                    source_sheet=catalog_row.source_sheet,
                    expired=expired,
                )
                rows.append(row)
                if missing:
                    blockers.append(
                        f"Calibration row for {catalog_row.equipment_id!r} is incomplete: "
                        f"{', '.join(missing)}. Correct the Equipment calibration Excel first."
                    )
                    continue
                if expired:
                    warnings.append(
                        f"Calibration is expired for {catalog_row.equipment_id} "
                        f"({catalog_row.calibration_due_date})."
                    )
                continue
            if len(matches) > 1:
                rows.append(_unresolved_row(reference, "ambiguous"))
                blockers.append(
                    f"Equipment reference {reference!r} matches multiple calibration rows."
                )
                continue
            override = overrides.get(key)
            if override is not None and _valid_external_override(override):
                due_date = _parse_date(override.calibration_due)
                if due_date is None and not _is_not_applicable(override.calibration_due):
                    rows.append(
                        EquipmentListReportRow(
                            source_reference=reference,
                            status="unmatched",
                            item=override.item.strip(),
                            manufacturer=override.manufacturer.strip(),
                            id_number=override.id_number.strip(),
                            last_calibration=override.last_calibration.strip(),
                            calibration_due=override.calibration_due.strip(),
                            source_sheet=None,
                            expired=False,
                            external_reason=override.reason.strip(),
                        )
                    )
                    blockers.append(
                        f"External equipment {override.id_number!r} requires a recognizable "
                        "Cal. Due date or N/A."
                    )
                    continue
                expired = due_date is not None and due_date < self._today()
                rows.append(
                    EquipmentListReportRow(
                        source_reference=reference,
                        status="external",
                        item=override.item.strip(),
                        manufacturer=override.manufacturer.strip(),
                        id_number=override.id_number.strip(),
                        last_calibration=override.last_calibration.strip(),
                        calibration_due=override.calibration_due.strip(),
                        source_sheet=None,
                        expired=expired,
                        external_reason=override.reason.strip(),
                    )
                )
                if expired:
                    warnings.append(
                        f"Calibration is expired for {override.id_number.strip()} "
                        f"({override.calibration_due.strip()})."
                    )
                continue
            rows.append(_unresolved_row(reference, "unmatched"))
            blockers.append(
                f"Equipment reference {reference!r} was not found. "
                "Provide a complete external-equipment entry and explanation."
            )
        return rows, blockers, warnings


_EQUIPMENT_TOKEN = re.compile(r"(?:DG-)?[QL]-\d{4}", flags=re.IGNORECASE)


def equipment_reference_key(value: str) -> str:
    """Normalize legacy Q/L identifiers while retaining exact-name matching."""
    cleaned = re.sub(r"\s+", " ", value.replace("\x07", " ").strip())
    token = _EQUIPMENT_TOKEN.search(cleaned)
    if token is None:
        return cleaned.casefold()
    matched = token.group(0).upper()
    return matched[3:] if matched.startswith("DG-") else matched


def _report_blockers(report: CurrentReportArtifact) -> tuple[str, ...]:
    if report.status == "ready":
        return tuple()
    if report.status == "ambiguous":
        return ("Keep exactly one current internal report before updating Equipment List.",)
    return ("Generate or publish the current internal report before updating Equipment List.",)


def _unresolved_row(reference: str, status: str) -> EquipmentListReportRow:
    return EquipmentListReportRow(
        source_reference=reference,
        status=status,
        item="",
        manufacturer="",
        id_number=reference,
        last_calibration="",
        calibration_due="",
        source_sheet=None,
        expired=False,
    )


def _valid_external_override(value: EquipmentListExternalOverride) -> bool:
    return all(
        field.strip()
        for field in (
            value.item,
            value.manufacturer,
            value.id_number,
            value.last_calibration,
            value.calibration_due,
            value.reason,
        )
    )


def _fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_expired(value: str | None, today: date) -> bool:
    parsed = _parse_date(value)
    return parsed is not None and parsed < today


def _parse_date(value: str | None) -> date | None:
    cleaned = (value or "").strip()
    if not cleaned or cleaned.casefold() in {"n/a", "na", "not applicable"}:
        return None
    for pattern in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d-%b-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ):
        try:
            return datetime.strptime(cleaned, pattern).date()
        except ValueError:
            continue
    return None


def _is_not_applicable(value: str | None) -> bool:
    return (value or "").strip().casefold() in {"n/a", "na", "not applicable"}
