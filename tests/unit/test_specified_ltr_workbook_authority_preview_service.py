from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.specified_ltr_workbook_authority_preview_service import (
    SpecifiedLtrWorkbookAuthorityPreviewAck,
    SpecifiedLtrWorkbookAuthorityPreviewCommand,
    SpecifiedLtrWorkbookAuthorityPreviewError,
    SpecifiedLtrWorkbookAuthorityPreviewService,
)
from backend.infrastructure.office import LtrWorkbookExistingRow


def test_preview_found_returns_business_row_values_and_ack_without_write() -> None:
    transaction = _FakeTransactionGateway(
        _FakeWorkbookSession(
            existing=LtrWorkbookExistingRow(
                sheet_name="2026",
                row_number=12,
                dl_number="DL-2026-05-011",
                values=(
                    "May",
                    10,
                    11,
                    "DL-2026-05-011",
                    "Qualification",
                    "PwrBlade Ultra Pro",
                    "R/A TYPE, WITH 2HP +20S",
                    "Qualification",
                    "Alice",
                    "Dongguan",
                    "Lab User",
                    "",
                    "",
                    "Return",
                    "No",
                    "1200",
                    "PO-1",
                ),
            )
        )
    )
    service = SpecifiedLtrWorkbookAuthorityPreviewService(transaction_gateway=transaction)

    preview = service.preview(
        SpecifiedLtrWorkbookAuthorityPreviewCommand(
            case_id="case-1",
            specified_ltr_number="dl-2026-05-011",
        )
    )

    assert preview.status == "found"
    assert preview.ltr_number == "DL-2026-05-011"
    assert preview.workbook_path == Path("D:/PublicProject/LTR.xlsx")
    assert preview.sheet_name == "2026"
    assert preview.row_number == 12
    assert [value.label for value in preview.row_values] == [
        "Project Type",
        "Description P/N",
        "Test Item",
        "Test Type",
        "Requested by",
        "Location",
        "Project Leader",
        "Test Result",
        "Failed item",
        "Sample deposition",
        "Sub-contract",
        "Test Fee",
        "Remarks (PO)",
    ]
    assert preview.row_values[0].value == "Qualification"
    assert preview.row_values[7].is_blank is True
    assert preview.preview_ack is not None
    assert transaction.write_opened is False


def test_preview_not_found_returns_blocking_message_without_ack() -> None:
    service = SpecifiedLtrWorkbookAuthorityPreviewService(
        transaction_gateway=_FakeTransactionGateway(_FakeWorkbookSession(existing=None))
    )

    preview = service.preview(
        SpecifiedLtrWorkbookAuthorityPreviewCommand(
            case_id="case-1",
            specified_ltr_number="DL-2026-05-099",
        )
    )

    assert preview.status == "not_found"
    assert preview.message == "LTR workbook 中不存在该编号"
    assert preview.preview_ack is None
    assert preview.row_values == ()


def test_verify_ack_rejects_stale_row_before_local_completion_can_continue() -> None:
    found_session = _FakeWorkbookSession(
        existing=LtrWorkbookExistingRow(
            sheet_name="2026",
            row_number=12,
            dl_number="DL-2026-05-011",
            values=_row_values("Initial description"),
        )
    )
    changed_session = _FakeWorkbookSession(
        existing=LtrWorkbookExistingRow(
            sheet_name="2026",
            row_number=12,
            dl_number="DL-2026-05-011",
            values=_row_values("Changed description"),
        )
    )
    transaction = _FakeTransactionGateway(found_session)
    service = SpecifiedLtrWorkbookAuthorityPreviewService(transaction_gateway=transaction)
    preview = service.preview(
        SpecifiedLtrWorkbookAuthorityPreviewCommand(
            case_id="case-1",
            specified_ltr_number="DL-2026-05-011",
        )
    )
    assert preview.preview_ack is not None
    transaction.session = changed_session

    with pytest.raises(
        SpecifiedLtrWorkbookAuthorityPreviewError,
        match="LTR workbook preview changed",
    ):
        service.verify_ack(
            specified_ltr_number="DL-2026-05-011",
            ack=preview.preview_ack,
        )


def test_verify_ack_accepts_current_row() -> None:
    session = _FakeWorkbookSession(
        existing=LtrWorkbookExistingRow(
            sheet_name="2026",
            row_number=12,
            dl_number="DL-2026-05-011",
            values=_row_values("Initial description"),
        )
    )
    service = SpecifiedLtrWorkbookAuthorityPreviewService(
        transaction_gateway=_FakeTransactionGateway(session)
    )
    preview = service.preview(
        SpecifiedLtrWorkbookAuthorityPreviewCommand(
            case_id="case-1",
            specified_ltr_number="DL-2026-05-011",
        )
    )
    assert preview.preview_ack is not None

    verified = service.verify_ack(
        specified_ltr_number="DL-2026-05-011",
        ack=preview.preview_ack,
    )

    assert verified.status == "found"
    assert verified.row_number == 12


def _row_values(description: str) -> tuple[object, ...]:
    return (
        "May",
        10,
        11,
        "DL-2026-05-011",
        "Qualification",
        description,
        "Qualification",
        "Qualification",
        "Alice",
        "Dongguan",
        "Lab User",
        "",
        "",
        "Return",
        "No",
        "1200",
        "PO-1",
    )


class _FakeTransactionGateway:
    def __init__(self, session: "_FakeWorkbookSession") -> None:
        self.session = session
        self.write_opened = False

    def open_read_only_transaction(self):
        return _FakeReadOnlyTransaction(self)

    def open_transaction(self):  # pragma: no cover - safety assertion helper
        self.write_opened = True
        raise AssertionError("Preview must not open a write transaction.")


class _FakeReadOnlyTransaction:
    def __init__(self, gateway: _FakeTransactionGateway) -> None:
        self._gateway = gateway

    def __enter__(self):
        return type(
            "Context",
            (),
            {
                "session": self._gateway.session,
                "workbook_path": Path("D:/PublicProject/LTR.xlsx"),
            },
        )()

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


class _FakeWorkbookSession:
    def __init__(self, *, existing: LtrWorkbookExistingRow | None) -> None:
        self.existing = existing
        self.find_calls: list[tuple[str, tuple[str, ...] | None]] = []

    def find_ltr_number(self, ltr_number: str, sheet_names=None):
        self.find_calls.append((ltr_number, sheet_names))
        return self.existing
