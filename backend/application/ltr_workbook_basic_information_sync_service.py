"""Synchronize existing LTR workbook rows from confirmed Basic Information."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from numbers import Number
from pathlib import Path
import re
from typing import Protocol

from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWriteColumnPreview,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.office import (
    LtrWorkbookExistingRow,
    LtrWorkbookRowData,
    LtrWorkbookRowPointer,
)
from backend.modules.ltr import LtrNumberError, parse_ltr_number


class LtrWorkbookBasicInformationSyncError(ValueError):
    """Raised when LTR workbook Basic Information sync cannot proceed."""


class LtrRecordStore(Protocol):
    """Local LTR lookup behavior required by Basic Information sync."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return local LTR records for one project."""


class LtrWorkbookTransactionGatewayPort(Protocol):
    """Workbook transaction behavior required by Basic Information sync."""

    def open_transaction(self):
        """Open a transaction context without implicit save."""

    def open_read_only_transaction(self):
        """Open a read-only transaction context for preview."""

    def run_short_transaction(self, operation):
        """Run one locked write transaction and save after operation success."""


class LtrWorkbookReadonlyOpenGatewayPort(Protocol):
    """Read-only workbook viewer behavior required by Basic Information sync."""

    def open_at_cell(
        self,
        *,
        workbook_path: Path,
        sheet_name: str,
        row_number: int,
        column_number: int,
    ) -> str:
        """Open a workbook read-only and select one cell."""


@dataclass(frozen=True, slots=True)
class PreviewLtrWorkbookBasicInformationSyncCommand:
    """Command for LTR workbook Basic Information sync preview."""

    project_id: str


@dataclass(frozen=True, slots=True)
class CommitLtrWorkbookBasicInformationSyncCommand:
    """Command for LTR workbook Basic Information sync commit."""

    project_id: str
    operator_confirmed: bool
    preview_acknowledged: bool
    expected_confirmed_basic_information_version: int
    expected_confirmed_basic_information_source_signature_hash: str


@dataclass(frozen=True, slots=True)
class OpenLtrWorkbookBasicInformationReadonlyCommand:
    """Command for opening the LTR workbook at the exact DL row."""

    project_id: str


@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationSyncPreview:
    """Preview of one existing LTR workbook row sync."""

    project_id: str
    ltr_number: str
    workbook_path: Path | None
    target_sheet: str | None
    target_row: int | None
    row_data: LtrWorkbookRowData | None
    columns: tuple[LtrWorkbookWriteColumnPreview, ...]
    comparison_values: tuple["LtrWorkbookBasicInformationSyncComparisonValue", ...]
    confirmed_basic_information_version: int | None
    confirmed_basic_information_source_signature_hash: str | None
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def status(self) -> str:
        """Return the typed preview state."""
        return "blocked" if self.blockers else "ready"


@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationSyncComparisonValue:
    """Current workbook value and pending Basic Information value for one field."""

    field_name: str
    label: str
    current_value: object
    pending_value: object
    changed: bool


@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationSyncResult:
    """Result of one committed LTR workbook row sync."""

    project_id: str
    ltr_number: str
    workbook_path: Path
    backup_path: Path
    sheet_name: str
    row_number: int
    confirmed_basic_information_version: int
    confirmed_basic_information_source_signature_hash: str


@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationReadonlyOpenResult:
    """Result of opening one LTR workbook row read-only."""

    project_id: str
    ltr_number: str
    workbook_path: Path
    sheet_name: str
    row_number: int
    column_number: int
    selected_cell: str
    message: str


@dataclass(frozen=True, slots=True)
class _WorkbookSignature:
    path: str
    size: int | None
    modified_ns: int | None


@dataclass(frozen=True, slots=True)
class _CachedExactLtrRow:
    signature: _WorkbookSignature
    sheet_name: str
    row_number: int
    ltr_number: str


class LtrWorkbookBasicInformationSyncService:
    """Preview and commit existing LTR workbook row sync from Basic Information."""

    def __init__(
        self,
        *,
        ltr_store: LtrRecordStore,
        basic_information_reader: ConfirmedBasicInformationReader,
        transaction_gateway: LtrWorkbookTransactionGatewayPort,
        readonly_open_gateway: LtrWorkbookReadonlyOpenGatewayPort | None = None,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
    ) -> None:
        """Create the sync service."""
        self._ltrs = ltr_store
        self._basic_information = basic_information_reader
        self._transaction = transaction_gateway
        self._readonly_open = readonly_open_gateway
        self._lifecycle_write_guard = lifecycle_write_guard
        self._exact_ltr_row_cache: dict[
            tuple[str, str, str], _CachedExactLtrRow
        ] = {}

    def preview(
        self, command: PreviewLtrWorkbookBasicInformationSyncCommand
    ) -> LtrWorkbookBasicInformationSyncPreview:
        """Preview an existing LTR workbook row update without saving."""
        ltr = self._latest_registered_ltr(command.project_id)
        try:
            basic = self._require_basic_information(command.project_id)
            with self._transaction.open_read_only_transaction() as context:
                return self._build_preview(
                    project_id=command.project_id,
                    ltr=ltr,
                    basic_information=basic,
                    context=context,
                )
        except LtrWorkbookBasicInformationSyncError as exc:
            return _blocked_preview(
                project_id=command.project_id,
                ltr_number=ltr.ltr_number,
                blocker=str(exc),
            )

    def commit(
        self, command: CommitLtrWorkbookBasicInformationSyncCommand
    ) -> LtrWorkbookBasicInformationSyncResult:
        """Write confirmed Basic Information to the existing workbook row."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT,
        )
        if not command.preview_acknowledged:
            raise LtrWorkbookBasicInformationSyncError(
                "LTR workbook Basic Information sync preview must be acknowledged."
            )
        if not command.operator_confirmed:
            raise LtrWorkbookBasicInformationSyncError("Operator confirmation is required.")
        ltr = self._latest_registered_ltr(command.project_id)
        basic = self._require_basic_information(command.project_id)
        if (
            basic.version != command.expected_confirmed_basic_information_version
            or basic.source_signature_hash
            != command.expected_confirmed_basic_information_source_signature_hash
        ):
            raise LtrWorkbookBasicInformationSyncError(
                "Basic Information changed after preview. Refresh before syncing."
            )

        def _operation(context):
            preview = self._build_preview(
                project_id=command.project_id,
                ltr=ltr,
                basic_information=basic,
                context=context,
            )
            _ensure_ready_preview(preview)
            _ensure_preview_has_changes(preview)
            pointer = context.session.write_registration_row(
                preview.target_sheet,
                preview.target_row,
                preview.row_data,
            )
            return preview, pointer, context.workbook_path, context.backup_path

        preview, pointer, workbook_path, backup_path = self._transaction.run_short_transaction(
            _operation
        )
        return LtrWorkbookBasicInformationSyncResult(
            project_id=command.project_id,
            ltr_number=preview.ltr_number,
            workbook_path=workbook_path,
            backup_path=backup_path,
            sheet_name=pointer.sheet_name,
            row_number=pointer.row_number,
            confirmed_basic_information_version=basic.version,
            confirmed_basic_information_source_signature_hash=basic.source_signature_hash,
        )

    def _require_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> None:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(project_id, operation)

    def open_readonly_at_ltr(
        self, command: OpenLtrWorkbookBasicInformationReadonlyCommand
    ) -> LtrWorkbookBasicInformationReadonlyOpenResult:
        """Open the configured workbook read-only at the exact registered DL row."""
        if self._readonly_open is None:
            raise LtrWorkbookBasicInformationSyncError(
                "LTR workbook read-only opener is not configured."
            )
        ltr = self._latest_registered_ltr(command.project_id)
        with self._transaction.open_read_only_transaction() as context:
            target_sheet, target_row = self._locate_exact_ltr_row(
                ltr=ltr,
                context=context,
            )
            workbook_path = context.workbook_path
            try:
                selected_cell = self._readonly_open.open_at_cell(
                    workbook_path=workbook_path,
                    sheet_name=target_sheet,
                    row_number=target_row,
                    column_number=_LTR_DL_COLUMN_NUMBER,
                )
            except Exception as exc:
                raise LtrWorkbookBasicInformationSyncError(str(exc)) from exc
        return LtrWorkbookBasicInformationReadonlyOpenResult(
            project_id=command.project_id,
            ltr_number=ltr.ltr_number,
            workbook_path=workbook_path,
            sheet_name=target_sheet,
            row_number=target_row,
            column_number=_LTR_DL_COLUMN_NUMBER,
            selected_cell=selected_cell,
            message=f"Opened LTR workbook read-only at {selected_cell}.",
        )

    def _build_preview(
        self,
        *,
        project_id: str,
        ltr: LtrRecord,
        basic_information: ConfirmedBasicInformationSnapshot,
        context,
    ) -> LtrWorkbookBasicInformationSyncPreview:
        target_sheet, target_row = self._locate_exact_ltr_row(
            ltr=ltr,
            context=context,
        )
        current_row = _read_registration_row(
            context.session,
            sheet_name=target_sheet,
            row_number=target_row,
        )
        row_data = _row_data_from_basic_information(
            basic_information,
            ltr_number=ltr.ltr_number,
            row_number=target_row,
        )
        columns = _column_previews(row_data)
        return LtrWorkbookBasicInformationSyncPreview(
            project_id=project_id,
            ltr_number=ltr.ltr_number,
            workbook_path=context.workbook_path,
            target_sheet=target_sheet,
            target_row=target_row,
            row_data=row_data,
            columns=columns,
            comparison_values=_comparison_values(
                current_row=current_row,
                pending_columns=columns,
            ),
            confirmed_basic_information_version=basic_information.version,
            confirmed_basic_information_source_signature_hash=(
                basic_information.source_signature_hash
            ),
        )

    def _locate_exact_ltr_row(self, *, ltr: LtrRecord, context) -> tuple[str, int]:
        sheet_name = _target_sheet_name(ltr.ltr_number)
        workbook_path = Path(context.workbook_path)
        signature = _workbook_signature(workbook_path)
        target = _ltr_lookup_token(ltr.ltr_number)
        cache_key = (signature.path, sheet_name, target)
        cached = self._exact_ltr_row_cache.get(cache_key)
        if cached is not None and cached.signature == signature:
            cached_cell = _read_ltr_number_cell(
                context.session,
                sheet_name=sheet_name,
                row_number=cached.row_number,
            )
            if _ltr_lookup_token(cached_cell) == target:
                return cached.sheet_name, cached.row_number
            self._exact_ltr_row_cache.pop(cache_key, None)

        matches = [
            row_number
            for row_number, value in _read_ltr_number_cells(
                context.session,
                sheet_name=sheet_name,
            )
            if _ltr_lookup_token(value) == target
        ]
        if len(matches) > 1:
            self._exact_ltr_row_cache.pop(cache_key, None)
            raise LtrWorkbookBasicInformationSyncError(
                f"Duplicate exact LTR rows found in workbook: {ltr.ltr_number}"
            )
        if not matches:
            self._exact_ltr_row_cache.pop(cache_key, None)
            raise LtrWorkbookBasicInformationSyncError(
                f"Registered LTR row not found in workbook: {ltr.ltr_number}"
            )
        row_number = matches[0]
        self._exact_ltr_row_cache[cache_key] = _CachedExactLtrRow(
            signature=signature,
            sheet_name=sheet_name,
            row_number=row_number,
            ltr_number=target,
        )
        return sheet_name, row_number

    def _latest_registered_ltr(self, project_id: str) -> LtrRecord:
        records = [
            record
            for record in self._ltrs.list_by_project(project_id)
            if record.status is LtrStatus.REGISTERED
        ]
        if not records:
            raise LtrWorkbookBasicInformationSyncError(
                "Registered LTR is required before synchronizing LTR workbook."
            )
        return max(
            records,
            key=lambda record: (
                record.registered_on is not None,
                record.registered_on,
                record.ltr_number,
            ),
        )

    def _require_basic_information(
        self, project_id: str
    ) -> ConfirmedBasicInformationSnapshot:
        snapshot = self._basic_information.get_latest_confirmed(project_id)
        if snapshot is None:
            raise LtrWorkbookBasicInformationSyncError(
                "Confirm Basic Information before synchronizing LTR workbook."
            )
        return snapshot


def _row_data_from_basic_information(
    basic_information: ConfirmedBasicInformationSnapshot,
    *,
    ltr_number: str,
    row_number: int,
) -> LtrWorkbookRowData:
    values = basic_information.values
    parsed = _parse_ltr(ltr_number)
    return LtrWorkbookRowData(
        month=calendar.month_abbr[parsed.month or 1],
        total=max(row_number - 2, 0),
        monthly_number=parsed.sequence or 0,
        dl_number=_required(values, ("dl_number",), "DL/LTR Number"),
        project_type=_project_type_to_ltr_value(
            _required(values, ("project_type",), "Project Type")
        ),
        description_pn=_required(
            values,
            ("description_pn",),
            "Description P/N",
        ),
        test_item=_required(values, ("test_item",), "Test Item"),
        test_type=_required(values, ("test_type_in_sheet",), "Test Type in sheet"),
        requested_by=_text(values.get("requested_by")),
        location=_required(values, ("location",), "Mfg. Site"),
        project_leader=_required(values, ("project_leader",), "Project Leader"),
        test_result=_text(values.get("test_result")),
        failed_item=_text(values.get("failed_item")),
        sample_deposition=_text(values.get("sample_deposition")),
        sub_contract=_text(values.get("sub_contract")),
        test_fee=_text(values.get("test_fee")),
        remarks_po=_text(values.get("remarks_po")),
    )


def _blocked_preview(
    *,
    project_id: str,
    ltr_number: str,
    blocker: str,
) -> LtrWorkbookBasicInformationSyncPreview:
    return LtrWorkbookBasicInformationSyncPreview(
        project_id=project_id,
        ltr_number=ltr_number,
        workbook_path=None,
        target_sheet=None,
        target_row=None,
        row_data=None,
        columns=(),
        comparison_values=(),
        confirmed_basic_information_version=None,
        confirmed_basic_information_source_signature_hash=None,
        blockers=(blocker,),
    )


def _ensure_ready_preview(preview: LtrWorkbookBasicInformationSyncPreview) -> None:
    if preview.blockers or preview.target_sheet is None or preview.target_row is None:
        blocker = "; ".join(preview.blockers) or "LTR workbook preview is blocked."
        raise LtrWorkbookBasicInformationSyncError(blocker)
    if preview.row_data is None:
        raise LtrWorkbookBasicInformationSyncError("LTR workbook row data is missing.")


def _ensure_preview_has_changes(preview: LtrWorkbookBasicInformationSyncPreview) -> None:
    if not any(value.changed for value in preview.comparison_values):
        raise LtrWorkbookBasicInformationSyncError(
            "LTR workbook is already up to date."
        )


def _column_previews(
    row_data: LtrWorkbookRowData,
) -> tuple[LtrWorkbookWriteColumnPreview, ...]:
    return tuple(
        LtrWorkbookWriteColumnPreview(
            column=chr(ord("A") + index),
            field_name=field_name,
            value=value,
        )
        for index, (field_name, value) in enumerate(
            zip(_LTR_ROW_FIELD_NAMES, row_data.as_excel_row(), strict=True)
        )
    )


def _comparison_values(
    *,
    current_row: tuple[object, ...],
    pending_columns: tuple[LtrWorkbookWriteColumnPreview, ...],
) -> tuple[LtrWorkbookBasicInformationSyncComparisonValue, ...]:
    current_by_field = {
        field_name: current_row[index] if index < len(current_row) else None
        for index, field_name in enumerate(_LTR_ROW_FIELD_NAMES)
    }
    pending_by_field = {column.field_name: column.value for column in pending_columns}
    values: list[LtrWorkbookBasicInformationSyncComparisonValue] = []
    for field_name, label in _LTR_SYNC_COMPARISON_FIELDS:
        current_value = current_by_field.get(field_name)
        pending_value = pending_by_field.get(field_name)
        values.append(
            LtrWorkbookBasicInformationSyncComparisonValue(
                field_name=field_name,
                label=label,
                current_value=current_value,
                pending_value=pending_value,
                changed=_comparison_token(current_value) != _comparison_token(pending_value),
            )
        )
    return tuple(values)


def _target_sheet_name(ltr_number: str) -> str:
    parsed = _parse_ltr(ltr_number)
    if parsed.year is None:
        raise LtrWorkbookBasicInformationSyncError(
            f"LTR number has no target year: {ltr_number}"
        )
    return str(parsed.year)


def _workbook_signature(path: Path) -> _WorkbookSignature:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    try:
        stat = resolved.stat()
    except OSError:
        return _WorkbookSignature(str(resolved), None, None)
    return _WorkbookSignature(str(resolved), int(stat.st_size), int(stat.st_mtime_ns))


def _read_ltr_number_cells(
    session,
    *,
    sheet_name: str,
) -> tuple[tuple[int, object], ...]:
    if hasattr(session, "read_ltr_number_cells"):
        return tuple(session.read_ltr_number_cells(sheet_name))
    return tuple(
        (index, row[3] if len(row) >= _LTR_DL_COLUMN_NUMBER else None)
        for index, row in enumerate(session.read_annual_sheet(sheet_name), start=2)
    )


def _read_ltr_number_cell(
    session,
    *,
    sheet_name: str,
    row_number: int,
) -> object:
    if hasattr(session, "read_ltr_number_cell"):
        return session.read_ltr_number_cell(sheet_name, row_number)
    row = _read_registration_row(session, sheet_name=sheet_name, row_number=row_number)
    if len(row) < _LTR_DL_COLUMN_NUMBER:
        return None
    return row[_LTR_DL_COLUMN_NUMBER - 1]


def _read_registration_row(
    session,
    *,
    sheet_name: str,
    row_number: int,
) -> tuple[object, ...]:
    if hasattr(session, "read_registration_row"):
        return tuple(session.read_registration_row(sheet_name, row_number))
    rows = session.read_annual_sheet(sheet_name)
    index = row_number - 2
    if index < 0 or index >= len(rows):
        raise LtrWorkbookBasicInformationSyncError(
            f"LTR workbook target row cannot be read: {sheet_name} row {row_number}"
        )
    return tuple(rows[index])


def _find_exact_ltr_number(
    session,
    *,
    ltr_number: str,
    sheet_names: tuple[str, ...],
) -> LtrWorkbookExistingRow | None:
    target = _ltr_lookup_token(ltr_number)
    matches: list[LtrWorkbookExistingRow] = []
    for sheet_name in sheet_names:
        for index, row in enumerate(session.read_annual_sheet(sheet_name), start=2):
            if len(row) >= 4 and _ltr_lookup_token(row[3]) == target:
                matches.append(
                    LtrWorkbookExistingRow(
                        sheet_name=sheet_name,
                        row_number=index,
                        dl_number=_ltr_lookup_token(row[3]),
                        values=row,
                    )
                )
    if len(matches) > 1:
        raise LtrWorkbookBasicInformationSyncError(
            f"Duplicate exact LTR rows found in workbook: {ltr_number}"
        )
    return matches[0] if matches else None


def _ltr_lookup_token(value: object) -> str:
    return str(value or "").replace("\u00a0", " ").strip()


_NUMERIC_COMPARISON_PATTERN = re.compile(r"^[+-]?(?:0|[1-9]\d*)(?:\.\d+)?$")


def _comparison_token(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y/%m/%d")
    if isinstance(value, date):
        return value.strftime("%Y/%m/%d")
    if isinstance(value, Number) and not isinstance(value, bool):
        numeric_token = _numeric_comparison_token(str(value))
        if numeric_token is not None:
            return numeric_token
    text = str(value).replace("\u00a0", " ")
    normalized = " ".join(text.split()).strip()
    if _NUMERIC_COMPARISON_PATTERN.fullmatch(normalized):
        numeric_token = _numeric_comparison_token(normalized)
        if numeric_token is not None:
            return numeric_token
    return normalized


def _numeric_comparison_token(text: str) -> str | None:
    try:
        value = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    if not value.is_finite():
        return None
    if value == value.to_integral_value():
        return str(int(value))
    return format(value.normalize(), "f").rstrip("0").rstrip(".")


def _annual_sheet_names(sheet_names: list[str]) -> tuple[str, ...]:
    return tuple(name for name in sheet_names if name.isdigit() and len(name) == 4)


def _parse_ltr(ltr_number: str):
    try:
        return parse_ltr_number(ltr_number)
    except LtrNumberError as exc:
        raise LtrWorkbookBasicInformationSyncError(str(exc)) from exc


def _required(values: dict[str, str], keys: tuple[str, ...], label: str) -> str:
    for key in keys:
        text = _text(values.get(key))
        if text is not None:
            return text
    raise LtrWorkbookBasicInformationSyncError(
        f"{label} is required in confirmed Basic Information."
    )


def _text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _project_type_to_ltr_value(project_type: str) -> str:
    mapping = {
        "New Product Development": "NPD",
        "Product Extension": "PEX",
        "Innovation": "ADM",
        "Lab Activities (Lab Use Only)": "ADM",
        "Operational Support": "OPS",
        "Cost Reduction": "CR",
    }
    mapped = mapping.get(project_type)
    if mapped is None:
        raise LtrWorkbookBasicInformationSyncError(
            f"Project Type has no LTR workbook mapping: {project_type}"
        )
    return mapped


_LTR_ROW_FIELD_NAMES = (
    "month",
    "total",
    "monthly_number",
    "dl_number",
    "project_type",
    "description_pn",
    "test_item",
    "test_type_in_sheet",
    "requested_by",
    "location",
    "project_leader",
    "test_result",
    "failed_item",
    "sample_deposition",
    "sub_contract",
    "test_fee",
    "remarks_po",
)

_LTR_DL_COLUMN_NUMBER = 4

_LTR_SYNC_COMPARISON_FIELDS = (
    ("project_type", "Project Type"),
    ("description_pn", "Description P/N"),
    ("test_item", "Test Item"),
    ("test_type_in_sheet", "Test Type"),
    ("requested_by", "Requested by"),
    ("location", "Location"),
    ("project_leader", "Project Leader"),
    ("test_result", "Test Result"),
    ("failed_item", "Failed item"),
    ("sample_deposition", "Sample deposition"),
    ("sub_contract", "Sub-contract"),
    ("test_fee", "Test Fee"),
    ("remarks_po", "Remarks (PO)"),
)
