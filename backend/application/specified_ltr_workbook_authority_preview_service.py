"""Read-only public LTR workbook authority preview for specified New Project DLs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from backend.infrastructure.office import LtrWorkbookExistingRow
from backend.modules.ltr import LtrNumberError, LtrNumberKind, parse_ltr_number


class SpecifiedLtrWorkbookAuthorityPreviewError(ValueError):
    """Raised when specified LTR workbook preview acknowledgement is invalid."""


class LtrWorkbookTransactionGatewayPort(Protocol):
    """Read-only transaction behavior required by specified LTR preview."""

    def open_read_only_transaction(self):
        """Open a read-only workbook transaction."""


@dataclass(frozen=True, slots=True)
class SpecifiedLtrWorkbookAuthorityPreviewCommand:
    """Input command for a specified LTR workbook authority preview."""

    case_id: str
    specified_ltr_number: str


@dataclass(frozen=True, slots=True)
class SpecifiedLtrWorkbookAuthorityPreviewAck:
    """Acknowledgement payload required before full specified DL completion."""

    acknowledged: bool
    ltr_number: str
    sheet_name: str
    row_number: int
    preview_token: str
    row_fingerprint: str


@dataclass(frozen=True, slots=True)
class SpecifiedLtrWorkbookAuthorityRowValue:
    """One business-readable workbook row value."""

    field_name: str
    label: str
    value: object | None
    is_blank: bool


@dataclass(frozen=True, slots=True)
class SpecifiedLtrWorkbookAuthorityPreview:
    """Read-only specified LTR workbook preview result."""

    status: Literal["found", "not_found", "blocked"]
    ltr_number: str
    message: str
    workbook_path: Path | None
    sheet_name: str | None
    row_number: int | None
    row_values: tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...]
    preview_ack: SpecifiedLtrWorkbookAuthorityPreviewAck | None
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class SpecifiedLtrWorkbookAuthorityPreviewService:
    """Preview and verify public workbook authority rows before local completion."""

    def __init__(self, *, transaction_gateway: LtrWorkbookTransactionGatewayPort) -> None:
        self._transaction = transaction_gateway

    def preview(
        self,
        command: SpecifiedLtrWorkbookAuthorityPreviewCommand,
    ) -> SpecifiedLtrWorkbookAuthorityPreview:
        """Return the read-only workbook authority state for one full specified DL."""
        try:
            normalized, sheet_name = _parse_full_dl(command.specified_ltr_number)
            return self._preview_normalized(normalized, sheet_name)
        except SpecifiedLtrWorkbookAuthorityPreviewError as exc:
            ltr_number = _best_effort_ltr(command.specified_ltr_number)
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="blocked",
                ltr_number=ltr_number,
                message=str(exc),
                workbook_path=None,
                sheet_name=None,
                row_number=None,
                row_values=(),
                preview_ack=None,
                blockers=(str(exc),),
            )

    def verify_ack(
        self,
        *,
        specified_ltr_number: str,
        ack: SpecifiedLtrWorkbookAuthorityPreviewAck | None,
    ) -> SpecifiedLtrWorkbookAuthorityPreview:
        """Verify an operator acknowledgement against the current workbook row."""
        if ack is None or not ack.acknowledged:
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook authority preview must be confirmed before applying this DL."
            )
        normalized, sheet_name = _parse_full_dl(specified_ltr_number)
        if (
            ack.ltr_number != normalized
            or ack.sheet_name != sheet_name
            or ack.row_number <= 0
            or not ack.preview_token
            or not ack.row_fingerprint
        ):
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook preview acknowledgement does not match this DL."
            )
        current = self._preview_normalized(normalized, sheet_name)
        if current.status != "found" or current.preview_ack is None:
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook preview is no longer available. Refresh before applying."
            )
        if (
            current.sheet_name != ack.sheet_name
            or current.row_number != ack.row_number
            or current.preview_ack.row_fingerprint != ack.row_fingerprint
            or current.preview_ack.preview_token != ack.preview_token
        ):
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook preview changed. Refresh before applying."
            )
        return current

    def _preview_normalized(
        self,
        ltr_number: str,
        sheet_name: str,
    ) -> SpecifiedLtrWorkbookAuthorityPreview:
        try:
            with self._transaction.open_read_only_transaction() as context:
                row = context.session.find_ltr_number(ltr_number, (sheet_name,))
                workbook_path = Path(context.workbook_path)
        except SpecifiedLtrWorkbookAuthorityPreviewError:
            raise
        except Exception as exc:
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                f"Unable to read LTR workbook for preview: {_exception_summary(exc)}"
            ) from exc

        if row is None:
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="not_found",
                ltr_number=ltr_number,
                message="LTR workbook 中不存在该编号",
                workbook_path=workbook_path,
                sheet_name=sheet_name,
                row_number=None,
                row_values=(),
                preview_ack=None,
            )

        values = _row_values(row)
        fingerprint = _row_fingerprint(
            ltr_number=ltr_number,
            sheet_name=row.sheet_name,
            row_number=row.row_number,
            values=values,
        )
        ack = SpecifiedLtrWorkbookAuthorityPreviewAck(
            acknowledged=True,
            ltr_number=ltr_number,
            sheet_name=row.sheet_name,
            row_number=row.row_number,
            preview_token=_preview_token(fingerprint),
            row_fingerprint=fingerprint,
        )
        return SpecifiedLtrWorkbookAuthorityPreview(
            status="found",
            ltr_number=ltr_number,
            message="LTR workbook row found.",
            workbook_path=workbook_path,
            sheet_name=row.sheet_name,
            row_number=row.row_number,
            row_values=values,
            preview_ack=ack,
        )


def _parse_full_dl(value: str) -> tuple[str, str]:
    try:
        parsed = parse_ltr_number(value)
    except LtrNumberError as exc:
        raise SpecifiedLtrWorkbookAuthorityPreviewError(str(exc)) from exc
    if parsed.kind is not LtrNumberKind.STANDARD_DL or parsed.year is None:
        raise SpecifiedLtrWorkbookAuthorityPreviewError(
            "LTR workbook authority preview requires a full DL number."
        )
    return parsed.normalized, f"{parsed.year:04d}"


def _best_effort_ltr(value: str) -> str:
    try:
        return parse_ltr_number(value).normalized
    except LtrNumberError:
        return value.strip()


def _row_values(
    row: LtrWorkbookExistingRow,
) -> tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...]:
    values = tuple(row.values)
    selected = values[4:17]
    padded = selected + (None,) * max(0, len(_FIELD_DEFINITIONS) - len(selected))
    return tuple(
        SpecifiedLtrWorkbookAuthorityRowValue(
            field_name=field_name,
            label=label,
            value=_normalize_cell_value(value),
            is_blank=_is_blank(value),
        )
        for (field_name, label), value in zip(
            _FIELD_DEFINITIONS,
            padded,
            strict=True,
        )
    )


def _row_fingerprint(
    *,
    ltr_number: str,
    sheet_name: str,
    row_number: int,
    values: tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...],
) -> str:
    payload = {
        "ltr_number": ltr_number,
        "sheet_name": sheet_name,
        "row_number": row_number,
        "values": [
            {
                "field_name": value.field_name,
                "value": _json_safe(value.value),
            }
            for value in values
        ],
    }
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _preview_token(row_fingerprint: str) -> str:
    return hashlib.sha256(f"specified-ltr-preview:{row_fingerprint}".encode("utf-8")).hexdigest()


def _normalize_cell_value(value: object) -> object | None:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return value


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _json_safe(value: object | None) -> object | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _exception_summary(exc: Exception) -> str:
    return str(exc).strip() or exc.__class__.__name__


_FIELD_DEFINITIONS: tuple[tuple[str, str], ...] = (
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
