"""Read-only public LTR workbook authority preview for specified New Project DLs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal, Protocol

from backend.application.intake_confirmation_service import (
    IntakeConfirmationError,
    IntakeConfirmationService,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWritePreviewError,
    LtrWorkbookWritePreviewService,
    PreviewLtrWorkbookWriteCommand,
)
from backend.infrastructure.office import LtrWorkbookExistingRow, LtrWorkbookRowData
from backend.modules.ltr import (
    LtrNumberError,
    LtrNumberKind,
    base_ltr_number,
    parse_ltr_number,
)


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
    plan_date: date
    test_item: str
    sample_description: str
    test_type_in_sheet: str
    project_leader: str


@dataclass(frozen=True, slots=True)
class SpecifiedLtrWorkbookAuthorityPreviewAck:
    """Acknowledgement payload required before full specified DL completion."""

    acknowledged: bool
    ltr_number: str
    sheet_name: str
    row_number: int
    preview_token: str
    row_fingerprint: str
    action: Literal["replace_existing", "append_associated"] = "replace_existing"
    base_ltr_number: str | None = None
    base_sheet_name: str | None = None
    base_row_number: int | None = None
    base_fingerprint: str | None = None
    proposed_fingerprint: str | None = None


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

    status: Literal["found", "associated_candidate", "not_found", "blocked"]
    ltr_number: str
    message: str
    workbook_path: Path | None
    sheet_name: str | None
    row_number: int | None
    row_values: tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...]
    proposed_row_values: tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...]
    preview_ack: SpecifiedLtrWorkbookAuthorityPreviewAck | None
    related_ltr_number: str | None = None
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class SpecifiedLtrWorkbookAuthorityPreviewService:
    """Preview and verify public workbook authority rows before local completion."""

    def __init__(
        self,
        *,
        transaction_gateway: LtrWorkbookTransactionGatewayPort,
        intake_confirmation_service: IntakeConfirmationService,
        row_preview_service: LtrWorkbookWritePreviewService,
    ) -> None:
        self._transaction = transaction_gateway
        self._intake_confirmation = intake_confirmation_service
        self._row_preview = row_preview_service

    def preview(
        self,
        command: SpecifiedLtrWorkbookAuthorityPreviewCommand,
    ) -> SpecifiedLtrWorkbookAuthorityPreview:
        """Return the read-only workbook authority state for one full specified DL."""
        try:
            normalized, _ = _parse_full_dl(command.specified_ltr_number)
            projection = self._intake_confirmation.preview_case(command.case_id)
            proposed_row = self._row_preview.project_row_data(
                projection.project,
                projection.application_form,
                projection.sample_infos,
                PreviewLtrWorkbookWriteCommand(
                    ltr_number=normalized,
                    plan_date=command.plan_date,
                    test_item=command.test_item,
                    sample_description=command.sample_description,
                    location="",
                    test_type_in_sheet=command.test_type_in_sheet,
                    project_leader=command.project_leader,
                ),
            )
            return self._preview_normalized(normalized, proposed_row)
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
                proposed_row_values=(),
                preview_ack=None,
                blockers=(str(exc),),
            )
        except IntakeConfirmationError as exc:
            message = str(exc)
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="blocked",
                ltr_number=_best_effort_ltr(command.specified_ltr_number),
                message=message,
                workbook_path=None,
                sheet_name=None,
                row_number=None,
                row_values=(),
                proposed_row_values=(),
                preview_ack=None,
                blockers=(message,),
            )
        except LtrWorkbookWritePreviewError as exc:
            message = str(exc)
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="blocked",
                ltr_number=_best_effort_ltr(command.specified_ltr_number),
                message=message,
                workbook_path=None,
                sheet_name=None,
                row_number=None,
                row_values=(),
                proposed_row_values=(),
                preview_ack=None,
                blockers=(message,),
            )

    def verify_ack(
        self,
        *,
        specified_ltr_number: str,
        ack: SpecifiedLtrWorkbookAuthorityPreviewAck | None,
        command: SpecifiedLtrWorkbookAuthorityPreviewCommand,
    ) -> SpecifiedLtrWorkbookAuthorityPreview:
        """Verify an operator acknowledgement against the current workbook row."""
        if ack is None or not ack.acknowledged:
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook authority preview must be confirmed before applying this DL."
            )
        normalized, _ = _parse_full_dl(specified_ltr_number)
        if (
            ack.ltr_number != normalized
            or ack.row_number <= 0
            or not ack.preview_token
            or not ack.row_fingerprint
            or not ack.proposed_fingerprint
        ):
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook preview acknowledgement does not match this DL."
            )
        current = self.preview(command)
        if current.preview_ack is None:
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook preview is no longer available. Refresh before applying."
            )
        if (
            current.preview_ack.action != ack.action
            or
            current.sheet_name != ack.sheet_name
            or current.row_number != ack.row_number
            or current.preview_ack.row_fingerprint != ack.row_fingerprint
            or current.preview_ack.preview_token != ack.preview_token
            or current.preview_ack.base_fingerprint != ack.base_fingerprint
            or current.preview_ack.base_ltr_number != ack.base_ltr_number
            or current.preview_ack.base_sheet_name != ack.base_sheet_name
            or current.preview_ack.base_row_number != ack.base_row_number
            or current.preview_ack.proposed_fingerprint != ack.proposed_fingerprint
        ):
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                "LTR workbook preview changed. Refresh before applying."
            )
        return current

    def _preview_normalized(
        self,
        ltr_number: str,
        proposed_row: LtrWorkbookRowData,
    ) -> SpecifiedLtrWorkbookAuthorityPreview:
        try:
            with self._transaction.open_read_only_transaction() as context:
                annual_sheets = tuple(
                    str(name)
                    for name in context.session.list_sheets()
                    if len(str(name)) == 4 and str(name).isdigit()
                )
                row = context.session.find_ltr_number(ltr_number, annual_sheets)
                base_number = base_ltr_number(ltr_number)
                is_associated = base_number != ltr_number
                base = (
                    context.session.find_ltr_number(base_number, annual_sheets)
                    if is_associated
                    else None
                )
                workbook_path = Path(context.workbook_path)
        except SpecifiedLtrWorkbookAuthorityPreviewError:
            raise
        except Exception as exc:
            raise SpecifiedLtrWorkbookAuthorityPreviewError(
                f"Unable to read LTR workbook for preview: {_exception_summary(exc)}"
            ) from exc

        if row is None and not is_associated:
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="not_found",
                ltr_number=ltr_number,
                message="LTR workbook 中不存在该编号",
                workbook_path=workbook_path,
                sheet_name=_parse_full_dl(ltr_number)[1],
                row_number=None,
                row_values=(),
                proposed_row_values=(),
                preview_ack=None,
            )

        proposed_values = _proposed_row_values(proposed_row)
        proposed_fingerprint = _proposed_fingerprint(
            ltr_number,
            proposed_values,
            proposed_row,
        )
        if row is None and is_associated and base is None:
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="not_found",
                ltr_number=ltr_number,
                message=f"Associated base LTR does not exist in the workbook: {base_number}",
                workbook_path=workbook_path,
                sheet_name=None,
                row_number=None,
                row_values=(),
                proposed_row_values=proposed_values,
                preview_ack=None,
                blockers=(f"Associated base LTR does not exist: {base_number}",),
            )

        if row is None and is_associated and base is not None:
            expected_sheet = _parse_full_dl(base_number)[1]
            if base.sheet_name != expected_sheet:
                message = (
                    f"Associated base LTR is stored on {base.sheet_name}, but its number "
                    f"belongs to workbook year {expected_sheet}."
                )
                return SpecifiedLtrWorkbookAuthorityPreview(
                    status="blocked",
                    ltr_number=ltr_number,
                    message=message,
                    workbook_path=workbook_path,
                    sheet_name=base.sheet_name,
                    row_number=base.row_number,
                    row_values=_row_values(base),
                    proposed_row_values=proposed_values,
                    preview_ack=None,
                    related_ltr_number=base_number,
                    blockers=(message,),
                )

        current = row if row is not None else base
        if current is None:
            return SpecifiedLtrWorkbookAuthorityPreview(
                status="not_found",
                ltr_number=ltr_number,
                message="LTR workbook 中不存在该编号",
                workbook_path=workbook_path,
                sheet_name=_parse_full_dl(ltr_number)[1],
                row_number=None,
                row_values=(),
                proposed_row_values=proposed_values,
                preview_ack=None,
                blockers=(f"LTR workbook 中不存在该编号: {ltr_number}",),
            )

        values = _row_values(current)
        fingerprint = _row_fingerprint(
            ltr_number=current.dl_number,
            sheet_name=current.sheet_name,
            row_number=current.row_number,
            values=values,
            workbook_values=current.values,
        )
        action: Literal["replace_existing", "append_associated"] = (
            "replace_existing" if row is not None else "append_associated"
        )
        ack = SpecifiedLtrWorkbookAuthorityPreviewAck(
            acknowledged=True,
            ltr_number=ltr_number,
            sheet_name=current.sheet_name,
            row_number=current.row_number,
            preview_token=_preview_token(
                fingerprint,
                proposed_fingerprint,
                action,
                base_number if is_associated else None,
            ),
            row_fingerprint=fingerprint,
            action=action,
            base_ltr_number=base_number if action == "append_associated" else None,
            base_sheet_name=current.sheet_name if action == "append_associated" else None,
            base_row_number=current.row_number if action == "append_associated" else None,
            base_fingerprint=fingerprint if action == "append_associated" else None,
            proposed_fingerprint=proposed_fingerprint,
        )
        return SpecifiedLtrWorkbookAuthorityPreview(
            status="found" if row is not None else "associated_candidate",
            ltr_number=ltr_number,
            message=(
                "LTR workbook row found; confirmation will replace this row."
                if row is not None
                else f"将基于 {base_number} 信息新增独立关联编号行；不会改写主编号。"
            ),
            workbook_path=workbook_path,
            sheet_name=current.sheet_name,
            row_number=current.row_number,
            row_values=values,
            proposed_row_values=proposed_values,
            preview_ack=ack,
            related_ltr_number=base_number if action == "append_associated" else None,
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
    workbook_values: tuple[object, ...],
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
        "workbook_values": [_json_safe(value) for value in workbook_values],
    }
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _preview_token(
    row_fingerprint: str,
    proposed_fingerprint: str,
    action: str,
    base_ltr_number: str | None,
) -> str:
    payload = ":".join(
        ("specified-ltr-preview", action, row_fingerprint, proposed_fingerprint, base_ltr_number or "")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _proposed_row_values(
    row: LtrWorkbookRowData,
) -> tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...]:
    raw_values = row.as_excel_row()[4:17]
    return tuple(
        SpecifiedLtrWorkbookAuthorityRowValue(
            field_name=field_name,
            label=label,
            value=_normalize_cell_value(value),
            is_blank=_is_blank(value),
        )
        for (field_name, label), value in zip(_FIELD_DEFINITIONS, raw_values, strict=True)
    )


def _proposed_fingerprint(
    ltr_number: str,
    values: tuple[SpecifiedLtrWorkbookAuthorityRowValue, ...],
    row_data: LtrWorkbookRowData,
) -> str:
    row = row_data.as_excel_row()
    payload = {
        "ltr_number": ltr_number,
        "values": [
            {"field_name": value.field_name, "value": _json_safe(value.value)}
            for value in values
        ],
        # Month/sequence/number are stable authorization inputs; Total is a
        # calculated count that can vary with workbook insertion position.
        "workbook_metadata": [_json_safe(row[index]) for index in (0, 2, 3)],
    }
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


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
