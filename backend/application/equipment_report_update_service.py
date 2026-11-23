"""Preview equipment sources and coordinate one controlled Equipment List update."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import logging
from pathlib import Path
import re
from typing import Callable, Protocol

from backend.application.current_report_update_service import (
    CurrentReportArtifact,
    CurrentReportFileConflictError,
    CurrentReportUpdateError,
    UpdateCurrentEquipmentListReportCommand,
)
from backend.application.external_excel_read_service import ExternalExcelReadError, ExternalExcelReadNotFoundError


logger = logging.getLogger(__name__)
EQUIPMENT_IDS_HELP = "Enter one ID per line as editable text, using four digits, for example DG-Q-0913 or DG-L-0002."
_REPORT_SAVE_ACCESS = (
    "ConnLab could not save the updated report or its backup. Close the report in Word, then retry. "
    "If it still fails, ask the folder owner for write access to the report folder and History/Report."
)


class EquipmentReportUpdateError(ValueError):
    """Raised when an equipment-list update cannot be performed safely."""


class EquipmentSelectionError(ValueError):
    """A selection file needs to be corrected or replaced before retrying."""


class WorkspaceStore(Protocol):
    def get_by_project(self, project_id: str): ...


class EquipmentSourceReader(Protocol):
    def read(self, source_path: Path): ...
    def save_missing(self, source_path: Path, *, content: bytes | None = None,
                     references_text: str | None = None): ...


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
    catalog_source_path: Path | None = None


@dataclass(frozen=True, slots=True)
class EquipmentListUpdateCommand:
    project_id: str
    expected_report_sha256: str
    expected_source_sha256: str
    expected_catalog_sha256: str
    acknowledge_expired: bool
    external_overrides: tuple[EquipmentListExternalOverride, ...]
    updated_by: str


@dataclass(frozen=True, slots=True)
class EquipmentListOneClickResult:
    status: str
    update: object | None = None
    rows: tuple[EquipmentListReportRow, ...] = tuple()


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

    def update_one_click(
        self, *, project_id: str, updated_by: str,
        content: bytes | None = None, references_text: str | None = None,
    ) -> EquipmentListOneClickResult:
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None:
            raise EquipmentReportUpdateError("Create the official project folder before updating Equipment List.")
        try:
            report = self._reports.get_current_report(project_id)
        except OSError as exc:
            raise EquipmentReportUpdateError(
                "ConnLab could not read the current Internal Report. Open it from the project folder in Word. "
                "If Word cannot open it, restore the folder connection or ask the folder owner for read access."
            ) from exc
        if blockers := _report_blockers(report):
            raise EquipmentReportUpdateError(" ".join(blockers))
        root = Path(workspace.local_workspace_path)
        source_path = root / "EquipmentID.docx"
        if not self._prepare_selection(source_path, content=content, references_text=references_text):
            return EquipmentListOneClickResult("source_required")
        preview = self.preview(project_id=project_id)
        if preview.blockers:
            raise EquipmentReportUpdateError(" ".join(preview.blockers))
        # A second stable read confirms the Settings catalog identity as well as its bytes.
        def revalidate() -> None:
            current = self.preview(project_id=project_id)
            current_workspace = self._workspaces.get_by_project(project_id)
            if (current.blockers or current_workspace is None
                or Path(current_workspace.local_workspace_path) != root
                or current.source_sha256 != preview.source_sha256
                or current.catalog_sha256 != preview.catalog_sha256
                or current.catalog_source_path != preview.catalog_source_path
                or current.rows != preview.rows):
                raise EquipmentReportUpdateError("Equipment sources changed during update. Retry Update Equipment List.")
        try:
            result = self._reports.update_equipment_list(UpdateCurrentEquipmentListReportCommand(
                project_id=project_id,
                expected_report_sha256=preview.current_report.file_sha256 or "",
                rows=preview.rows, updated_by=updated_by, revalidate_sources=revalidate,
            ))
        except PermissionError as exc:
            raise EquipmentReportUpdateError(_REPORT_SAVE_ACCESS) from exc
        except CurrentReportFileConflictError as exc:
            if isinstance(exc.__cause__, PermissionError):
                raise EquipmentReportUpdateError(_REPORT_SAVE_ACCESS) from exc
            raise
        except OSError as exc:
            raise EquipmentReportUpdateError(
                "ConnLab could not save the report or create its History/Report backup. "
                "Open the project folder in File Explorer and confirm there is space to save a Word copy there."
            ) from exc
        except ValueError as exc:
            raise EquipmentReportUpdateError(str(exc)) from exc
        return EquipmentListOneClickResult("completed", result, preview.rows)

    def _prepare_selection(self, source_path: Path, *, content: bytes | None, references_text: str | None) -> bool:
        supplied = content is not None or references_text is not None
        existing_selection = (
            "EquipmentID.docx already exists in the project folder. Click Update Equipment List again to use it."
        )
        try:
            validate_path = getattr(self._source_reader, "validate_path", None)
            if validate_path:
                validate_path(source_path)
            source_path.lstat()
        except FileNotFoundError:
            if not source_path.parent.is_dir():
                raise EquipmentReportUpdateError(
                    "The registered project folder is unavailable. Open it in File Explorer or restore its drive connection."
                ) from None
            if not supplied:
                return False
        except OSError as exc:
            raise EquipmentReportUpdateError(
                "ConnLab could not access EquipmentID.docx in the project folder. "
                "Open it in Word and confirm it is a regular .docx file stored directly in that folder."
            ) from exc
        else:
            if supplied:
                raise EquipmentReportUpdateError(existing_selection)
            return True

        try:
            self._source_reader.save_missing(source_path, content=content, references_text=references_text)
        except FileExistsError as exc:
            raise EquipmentReportUpdateError(existing_selection) from exc
        except OSError as exc:
            raise EquipmentReportUpdateError(
                "ConnLab could not save EquipmentID.docx. Ask the folder owner for write access to the project folder, then retry."
            ) from exc
        except EquipmentSelectionError as exc:
            raise EquipmentReportUpdateError(
                f"{exc} Click Update Equipment List again, then select the corrected file in Provide equipment IDs."
            ) from exc
        except ValueError as exc:
            raise EquipmentReportUpdateError(str(exc)) from exc
        return True

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
        catalog_source_path: Path | None = None

        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None:
            blockers.append("Create the official project folder before updating Equipment List.")
        else:
            source_path = Path(workspace.local_workspace_path) / "EquipmentID.docx"
            source_file_name = source_path.name
            try:
                validate_path = getattr(self._source_reader, "validate_path", None)
                if validate_path:
                    validate_path(source_path)
                before = _fingerprint(source_path)
                source = self._source_reader.read(source_path)
                source_sha256 = _fingerprint(source.source_path)
                if source_sha256 != before:
                    raise ValueError("Equipment selection changed while it was read. Retry the update.")
            except FileNotFoundError:
                blockers.append(
                    "EquipmentID.docx was not found in the project folder."
                )
                source = None
            except EquipmentSelectionError as exc:
                blockers.append(f"{exc} Save the corrected EquipmentID.docx in the project folder, then retry.")
                source = None
            except ValueError as exc:
                blockers.append(str(exc))
                source = None
            except (OSError, RuntimeError) as exc:
                logger.warning("Could not read the project equipment selection: %s", exc, exc_info=True)
                blockers.append(
                    "ConnLab could not read EquipmentID.docx. Open it in Word from the project folder. "
                    "If it cannot open, restore the file or ask the folder owner for read access."
                )
                source = None

            try:
                catalog = self._catalog_reader.read_equipment_calibrations()
                catalog_path = Path(catalog.resource_path)
                catalog_source_path = catalog_path
                catalog_file_name = catalog_path.name
                before = _fingerprint(catalog_path)
                catalog = self._catalog_reader.read_equipment_calibrations()
                if Path(catalog.resource_path) != catalog_path:
                    raise ValueError("The configured equipment workbook changed while reading.")
                catalog_sha256 = _fingerprint(catalog_path)
                if catalog_sha256 != before:
                    raise ValueError("The equipment workbook changed while reading.")
            except (ExternalExcelReadError, ExternalExcelReadNotFoundError) as exc:
                blockers.append(str(exc))
                catalog = None
            except (LookupError, OSError, RuntimeError, ValueError):
                blockers.append(
                    "ConnLab could not read the calibration workbook during the update. Open the file shown in "
                    "Settings > Equipment calibration Excel in Excel on this computer, then retry."
                )
                catalog = None

            if source is not None and catalog is not None:
                if not source.references:
                    blockers.append(
                        f"EquipmentID.docx does not contain any equipment IDs. {EQUIPMENT_IDS_HELP}"
                    )
                else:
                    rows, row_warnings = resolve_equipment_rows(
                        source.references,
                        catalog.rows,
                        external_overrides,
                        today=self._today(),
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
            catalog_source_path=catalog_source_path,
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


def resolve_equipment_rows(
    references: tuple[str, ...],
    catalog_rows: tuple[object, ...],
    external_overrides: tuple[EquipmentListExternalOverride, ...] = (),
    *,
    today: date,
) -> tuple[list[EquipmentListReportRow], list[str]]:
    """Resolve ordered references using the same calibration rules for projects and Tools."""
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
    seen: set[str] = set()
    for reference in references:
        key = equipment_reference_key(reference)
        if key in seen:
            continue
        seen.add(key)
        matches = indexed.get(key, [])
        override = overrides.get(key)
        if matches:
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
                allow_not_calibrated=bool(re.fullmatch(r"L-\d{4}", equipment_reference_key(id_number))),
            )
            calibration_due = _safe_report_date(
                catalog_row.calibration_due_date,
                label="Cal. Due",
                issues=issues,
            )
            expired = bool(calibration_due) and _is_expired(
                calibration_due,
                today,
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
                    today,
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
        external_row, external_warning = _external_override_row(
            reference,
            override,
            today,
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
        return ("Multiple Internal Reports were found. Open the project folder and keep one current report before updating Equipment List.",)
    return ("No current Internal Report was found. Generate the Internal Report or publish the managed draft before updating Equipment List.",)


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
    allow_not_calibrated: bool = False,
) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        issues.append(label)
        return ""
    if _is_not_applicable(cleaned):
        return cleaned
    if allow_not_calibrated and " ".join(cleaned.split()).casefold() == "not calibrated":
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
