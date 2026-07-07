"""Read-only preview of a registered LTR workbook row for a project."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from backend.application.ltr_workbook_basic_information_sync_service import (
    _read_ltr_number_cells,
    _read_registration_row,
)
from backend.domain.enums import LtrStatus
from backend.domain.models import LtrRecord
from backend.modules.ltr import LtrNumberError, parse_ltr_number


class RegisteredLtrWorkbookRowPreviewError(ValueError):
    """Raised when the read-only registered LTR workbook row cannot be previewed."""


class LtrRecordStore(Protocol):
    """Read port for project LTR records."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return all LTR records for a project."""


class LtrWorkbookReadOnlyTransactionGateway(Protocol):
    """Read-only workbook transaction boundary."""

    def open_read_only_transaction(self):
        """Open a read-only workbook transaction."""


@dataclass(frozen=True)
class RegisteredLtrWorkbookRowPreviewCommand:
    """Request to preview the registered LTR workbook row for one project."""

    project_id: str


@dataclass(frozen=True)
class RegisteredLtrWorkbookRowPreviewRowValue:
    """One workbook row value exposed for read-only operator review."""

    field_name: str
    label: str
    value: object
    is_blank: bool


@dataclass(frozen=True)
class RegisteredLtrWorkbookRowPreview:
    """Read-only registered LTR workbook row preview result."""

    status: Literal["found", "not_found", "blocked"]
    project_id: str
    ltr_number: str | None
    message: str
    workbook_path: Path | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    row_values: tuple[RegisteredLtrWorkbookRowPreviewRowValue, ...] = field(
        default_factory=tuple
    )
    blockers: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


class RegisteredLtrWorkbookRowPreviewService:
    """Preview the public LTR workbook row for a registered project DL number."""

    def __init__(
        self,
        *,
        ltr_store: LtrRecordStore,
        transaction_gateway: LtrWorkbookReadOnlyTransactionGateway,
    ) -> None:
        self._ltrs = ltr_store
        self._transaction_gateway = transaction_gateway

    def preview(
        self, command: RegisteredLtrWorkbookRowPreviewCommand
    ) -> RegisteredLtrWorkbookRowPreview:
        """Return the configured workbook row for the latest registered project LTR."""
        ltr = self._latest_registered_ltr(command.project_id)
        if ltr is None:
            return _blocked_preview(
                project_id=command.project_id,
                ltr_number=None,
                blocker="Registered LTR is required for workbook row preview.",
            )

        try:
            parsed = parse_ltr_number(ltr.ltr_number)
            if parsed.year is None:
                raise RegisteredLtrWorkbookRowPreviewError(
                    f"Registered LTR year is required: {ltr.ltr_number}"
                )
            sheet_name = str(parsed.year)
            with self._transaction_gateway.open_read_only_transaction() as context:
                row_number = _locate_exact_ltr_row(
                    context.session,
                    sheet_name=sheet_name,
                    ltr_number=ltr.ltr_number,
                )
                if row_number is None:
                    blocker = (
                        f"Registered LTR row not found in workbook: {ltr.ltr_number}"
                    )
                    return RegisteredLtrWorkbookRowPreview(
                        status="not_found",
                        project_id=command.project_id,
                        ltr_number=ltr.ltr_number,
                        message=blocker,
                        workbook_path=_context_workbook_path(context),
                        sheet_name=sheet_name,
                        blockers=(blocker,),
                    )
                row = _read_registration_row(
                    context.session,
                    sheet_name=sheet_name,
                    row_number=row_number,
                )
                return RegisteredLtrWorkbookRowPreview(
                    status="found",
                    project_id=command.project_id,
                    ltr_number=ltr.ltr_number,
                    message="LTR workbook row found.",
                    workbook_path=_context_workbook_path(context),
                    sheet_name=sheet_name,
                    row_number=row_number,
                    row_values=_row_values(row),
                )
        except RegisteredLtrWorkbookRowPreviewError as exc:
            return _blocked_preview(
                project_id=command.project_id,
                ltr_number=ltr.ltr_number,
                blocker=str(exc),
            )
        except LtrNumberError as exc:
            return _blocked_preview(
                project_id=command.project_id,
                ltr_number=ltr.ltr_number,
                blocker=f"Registered LTR is invalid: {exc}",
            )
        except Exception as exc:
            return _blocked_preview(
                project_id=command.project_id,
                ltr_number=ltr.ltr_number,
                blocker=f"Unable to read LTR workbook for preview: {exc}",
            )

    def _latest_registered_ltr(self, project_id: str) -> LtrRecord | None:
        records = [
            record
            for record in self._ltrs.list_by_project(project_id)
            if record.status is LtrStatus.REGISTERED
        ]
        if not records:
            return None
        return max(
            records,
            key=lambda record: (
                record.registered_on is not None,
                record.registered_on,
                record.ltr_number,
            ),
        )


def _locate_exact_ltr_row(
    session,
    *,
    sheet_name: str,
    ltr_number: str,
) -> int | None:
    target = _ltr_lookup_token(ltr_number)
    matches = [
        row_number
        for row_number, value in _read_ltr_number_cells(
            session,
            sheet_name=sheet_name,
        )
        if _ltr_lookup_token(value) == target
    ]
    if len(matches) > 1:
        raise RegisteredLtrWorkbookRowPreviewError(
            f"Duplicate exact LTR rows found in workbook: {ltr_number}"
        )
    return matches[0] if matches else None


def _row_values(
    row: tuple[object, ...]
) -> tuple[RegisteredLtrWorkbookRowPreviewRowValue, ...]:
    values: list[RegisteredLtrWorkbookRowPreviewRowValue] = []
    for index, (field_name, label) in enumerate(_LTR_ROW_PREVIEW_FIELDS, start=4):
        value = row[index] if index < len(row) else None
        values.append(
            RegisteredLtrWorkbookRowPreviewRowValue(
                field_name=field_name,
                label=label,
                value=value,
                is_blank=value is None or value == "",
            )
        )
    return tuple(values)


def _blocked_preview(
    *,
    project_id: str,
    ltr_number: str | None,
    blocker: str,
) -> RegisteredLtrWorkbookRowPreview:
    return RegisteredLtrWorkbookRowPreview(
        status="blocked",
        project_id=project_id,
        ltr_number=ltr_number,
        message=blocker,
        blockers=(blocker,),
    )


def _ltr_lookup_token(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _context_workbook_path(context) -> Path | None:
    if hasattr(context, "signature"):
        return context.signature.path
    workbook_path = getattr(context, "workbook_path", None)
    return Path(workbook_path) if workbook_path is not None else None


_LTR_ROW_PREVIEW_FIELDS = (
    ("project_type", "Project Type"),
    ("description_pn", "Description P/N"),
    ("test_item", "Test Item"),
    ("test_type", "Test Type"),
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
