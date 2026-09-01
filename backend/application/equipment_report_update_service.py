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
                if not source.references:
                    blockers.append(
                        "EquipmentID.docx does not contain any equipment references."
                    )
                else:
                    rows, row_warnings = self._project_rows(
                        source.references,
                        catalog.rows,
                        external_overrides,
                    )
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
    ) -> tuple[list[EquipmentListReportRow], list[str]]:
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
        warnings: list[str] = []
        for reference in references:
            key = equipment_reference_key(reference)
            matches = indexed.get(key, [])
            override = overrides.get(key)
            if len(matches) == 1:
                catalog_row = matches[0]
                issues: list[str] = []
                item = (catalog_row.equipment_name or "").strip()
                manufacturer = (catalog_row.manufacturer or "").strip()
                id_number = (catalog_row.equipment_id or "").strip()
                if not item:
                    issues.append("Item")
                if not manufacturer:
                    issues.append("Manufacturer")
                if not id_number:
                    issues.append("ID Number")
                last_calibration = _safe_report_date(
                    catalog_row.last_calibration_date,
                    label="Last Cal.",
                    issues=issues,
                )
                calibration_due = _safe_report_date(
                    catalog_row.calibration_due_date,
                    label="Cal. Due",
                    issues=issues,
                )
                expired = bool(calibration_due) and _is_expired(
                    calibration_due,
                    self._today(),
                )
                row = EquipmentListReportRow(
                    source_reference=reference,
                    status="incomplete" if issues else "matched",
                    item=item,
                    manufacturer=manufacturer,
                    id_number=id_number,
                    last_calibration=last_calibration,
                    calibration_due=calibration_due,
                    source_sheet=catalog_row.source_sheet,
                    expired=expired,
                )
                if issues:
                    external_row, external_warning = _external_override_row(
                        reference,
                        override,
                        self._today(),
                    )
                    rows.append(external_row or row)
                    if external_warning:
                        warnings.append(external_warning)
                    if external_row is not None:
                        warnings.append(
                            f"Calibration row for {catalog_row.equipment_id!r} is incomplete: "
                            f"{', '.join(issues)}. The confirmed preview correction will be used."
                        )
                    else:
                        warnings.append(
                            f"Calibration row for {catalog_row.equipment_id!r} is incomplete: "
                            f"{', '.join(issues)}. Unconfirmed cells will remain blank; "
                            "correct them in this preview or manually in Word."
                        )
                    continue
                rows.append(row)
                if expired:
                    warnings.append(
                        f"Calibration is expired for {catalog_row.equipment_id} "
                        f"({row.calibration_due})."
                    )
                continue
            if len(matches) > 1:
                external_row, external_warning = _external_override_row(
                    reference,
                    override,
                    self._today(),
                )
                rows.append(external_row or _unresolved_row(reference, "ambiguous"))
                if external_warning:
                    warnings.append(external_warning)
                if external_row is not None:
                    warnings.append(
                        f"Equipment reference {reference!r} matches multiple calibration rows. "
                        "The confirmed preview correction will be used."
                    )
                else:
                    warnings.append(
                        f"Equipment reference {reference!r} matches multiple calibration rows. "
                        "Unconfirmed cells will remain blank; correct them in this preview or "
                        "manually in Word."
                    )
                continue
            external_row, external_warning = _external_override_row(
                reference,
                override,
                self._today(),
            )
            if external_row is not None:
                rows.append(external_row)
                if external_warning:
                    warnings.append(external_warning)
                continue
            rows.append(_unresolved_row(reference, "unmatched"))
            if external_warning:
                warnings.append(external_warning)
            warnings.append(
                f"Equipment reference {reference!r} was not found. "
                "It will be added with ID only; complete it manually in Word."
            )
        return rows, warnings


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


def _external_override_row(
    reference: str,
    override: EquipmentListExternalOverride | None,
    today: date,
) -> tuple[EquipmentListReportRow | None, str | None]:
    if override is None or not _valid_external_override(override):
        return None, None
    invalid_dates = [
        label
        for label, value in (
            ("Last Cal.", override.last_calibration),
            ("Cal. Due", override.calibration_due),
        )
        if _parse_date(value) is None and not _is_not_applicable(value)
    ]
    if invalid_dates:
        return (
            None,
            f"External correction for {reference!r} has invalid "
            f"{', '.join(invalid_dates)}. The correction was skipped; complete it in the "
            "preview or manually in Word.",
        )
    calibration_due = _format_report_date(override.calibration_due)
    expired = _is_expired(calibration_due, today)
    row = EquipmentListReportRow(
        source_reference=reference,
        status="external",
        item=override.item.strip(),
        manufacturer=override.manufacturer.strip(),
        id_number=override.id_number.strip(),
        last_calibration=_format_report_date(override.last_calibration),
        calibration_due=calibration_due,
        source_sheet=None,
        expired=expired,
        external_reason=override.reason.strip(),
    )
    warning = (
        f"Calibration is expired for {row.id_number} ({row.calibration_due})."
        if expired
        else None
    )
    return row, warning


def _safe_report_date(
    value: str | None,
    *,
    label: str,
    issues: list[str],
) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        issues.append(label)
        return ""
    if _is_not_applicable(cleaned):
        return cleaned
    parsed = _parse_date(cleaned)
    if parsed is None:
        issues.append(f"invalid {label}")
        return ""
    return parsed.strftime("%d-%b-%Y")


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
    try:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00")).date()
    except ValueError:
        pass
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


def _format_report_date(value: str | None) -> str:
    cleaned = (value or "").strip()
    parsed = _parse_date(cleaned)
    return parsed.strftime("%d-%b-%Y") if parsed is not None else cleaned
