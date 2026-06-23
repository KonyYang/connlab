"""Synchronize existing LTR workbook rows from confirmed Basic Information."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWriteColumnPreview,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.office import LtrWorkbookRowData, LtrWorkbookRowPointer
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


class LtrWorkbookBasicInformationSyncService:
    """Preview and commit existing LTR workbook row sync from Basic Information."""

    def __init__(
        self,
        *,
        ltr_store: LtrRecordStore,
        basic_information_reader: ConfirmedBasicInformationReader,
        transaction_gateway: LtrWorkbookTransactionGatewayPort,
    ) -> None:
        """Create the sync service."""
        self._ltrs = ltr_store
        self._basic_information = basic_information_reader
        self._transaction = transaction_gateway

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

    def _build_preview(
        self,
        *,
        project_id: str,
        ltr: LtrRecord,
        basic_information: ConfirmedBasicInformationSnapshot,
        context,
    ) -> LtrWorkbookBasicInformationSyncPreview:
        sheet_names = _annual_sheet_names(context.session.list_sheets())
        existing = context.session.find_ltr_number(ltr.ltr_number, sheet_names)
        if existing is None:
            raise LtrWorkbookBasicInformationSyncError(
                f"Registered LTR row not found in workbook: {ltr.ltr_number}"
            )
        row_data = _row_data_from_basic_information(
            basic_information,
            ltr_number=ltr.ltr_number,
            row_number=existing.row_number,
        )
        columns = _column_previews(row_data)
        return LtrWorkbookBasicInformationSyncPreview(
            project_id=project_id,
            ltr_number=ltr.ltr_number,
            workbook_path=context.workbook_path,
            target_sheet=existing.sheet_name,
            target_row=existing.row_number,
            row_data=row_data,
            columns=columns,
            comparison_values=_comparison_values(
                current_row=existing.values,
                pending_columns=columns,
            ),
            confirmed_basic_information_version=basic_information.version,
            confirmed_basic_information_source_signature_hash=(
                basic_information.source_signature_hash
            ),
        )

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
    return tuple(
        LtrWorkbookBasicInformationSyncComparisonValue(
            field_name=field_name,
            label=label,
            current_value=current_by_field.get(field_name),
            pending_value=pending_by_field.get(field_name),
        )
        for field_name, label in _LTR_SYNC_COMPARISON_FIELDS
    )


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
