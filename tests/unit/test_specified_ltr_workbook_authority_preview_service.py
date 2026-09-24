from __future__ import annotations

from pathlib import Path
from datetime import date

import pytest

from backend.application.specified_ltr_workbook_authority_preview_service import (
    SpecifiedLtrWorkbookAuthorityPreviewAck,
    SpecifiedLtrWorkbookAuthorityPreviewCommand,
    SpecifiedLtrWorkbookAuthorityPreviewError,
    SpecifiedLtrWorkbookAuthorityPreviewService,
)
from backend.infrastructure.office import LtrWorkbookExistingRow
from backend.infrastructure.office import LtrWorkbookRowData


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
    service = _service(transaction)

    preview = service.preview(
        _command("dl-2026-05-011")
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
    service = _service(_FakeTransactionGateway(_FakeWorkbookSession(existing=None)))

    preview = service.preview(
        _command("DL-2026-05-099")
    )

    assert preview.status == "not_found"
    assert preview.message == "LTR workbook 中不存在该编号"
    assert preview.preview_ack is None
    assert preview.row_values == ()
    assert preview.proposed_row_values == ()
    assert preview.blockers == ()


def test_preview_missing_associated_number_shows_base_and_proposed_rows() -> None:
    """A missing associated DL is reviewable when its base exists."""
    base = LtrWorkbookExistingRow(
        sheet_name="2026",
        row_number=12,
        dl_number="DL-2026-05-011",
        values=_row_values("Existing base description"),
    )
    session = _FakeWorkbookSession(existing_by_number={base.dl_number: base})
    service = _service(_FakeTransactionGateway(session))

    preview = service.preview(
        _command("DL-2026-05-011A")
    )

    assert preview.status == "associated_candidate"
    assert preview.ltr_number == "DL-2026-05-011A"
    assert preview.related_ltr_number == "DL-2026-05-011"
    assert preview.row_values[1].value == "Existing base description"
    assert preview.proposed_row_values[1].value == "Proposed description"
    assert preview.preview_ack is not None
    assert preview.preview_ack.action == "append_associated"
    assert preview.preview_ack.base_fingerprint


def test_preview_blocks_associated_base_stored_on_wrong_annual_sheet() -> None:
    base = LtrWorkbookExistingRow(
        sheet_name="2024",
        row_number=12,
        dl_number="DL-2025-05-011",
        values=_row_values("Misfiled base description"),
    )
    service = _service(
        _FakeTransactionGateway(
            _FakeWorkbookSession(existing_by_number={base.dl_number: base})
        )
    )

    preview = service.preview(_command("DL-2025-05-011A"))

    assert preview.status == "blocked"
    assert preview.preview_ack is None
    assert preview.blockers
    assert "belongs to workbook year 2025" in preview.message


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
    service = _service(transaction)
    command = _command("DL-2026-05-011")
    preview = service.preview(command)
    assert preview.preview_ack is not None
    transaction.session = changed_session

    with pytest.raises(
        SpecifiedLtrWorkbookAuthorityPreviewError,
        match="LTR workbook preview changed",
    ):
        service.verify_ack(
            specified_ltr_number="DL-2026-05-011",
            ack=preview.preview_ack,
            command=command,
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
    service = _service(_FakeTransactionGateway(session))
    command = _command("DL-2026-05-011")
    preview = service.preview(command)
    assert preview.preview_ack is not None

    verified = service.verify_ack(
        specified_ltr_number="DL-2026-05-011",
        ack=preview.preview_ack,
        command=command,
    )

    assert verified.status == "found"
    assert verified.row_number == 12


def test_verify_ack_rejects_changed_manual_setup_values() -> None:
    session = _FakeWorkbookSession(
        existing=LtrWorkbookExistingRow(
            sheet_name="2026",
            row_number=12,
            dl_number="DL-2026-05-011",
            values=_row_values("Initial description"),
        )
    )
    service = _service(_FakeTransactionGateway(session))
    command = _command("DL-2026-05-011")
    preview = service.preview(command)
    assert preview.preview_ack is not None
    changed_command = SpecifiedLtrWorkbookAuthorityPreviewCommand(
        case_id=command.case_id,
        specified_ltr_number=command.specified_ltr_number,
        plan_date=command.plan_date,
        test_item="Changed qualification",
        sample_description=command.sample_description,
        test_type_in_sheet=command.test_type_in_sheet,
        project_leader=command.project_leader,
    )

    with pytest.raises(
        SpecifiedLtrWorkbookAuthorityPreviewError,
        match="LTR workbook preview changed",
    ):
        service.verify_ack(
            specified_ltr_number=command.specified_ltr_number,
            ack=preview.preview_ack,
            command=changed_command,
        )


def test_verify_ack_rejects_changed_plan_date_metadata() -> None:
    session = _FakeWorkbookSession(
        existing=LtrWorkbookExistingRow(
            sheet_name="2026",
            row_number=12,
            dl_number="DL-2026-05-011",
            values=_row_values("Initial description"),
        )
    )
    service = _service(_FakeTransactionGateway(session))
    command = _command("DL-2026-05-011")
    preview = service.preview(command)
    assert preview.preview_ack is not None
    changed_command = SpecifiedLtrWorkbookAuthorityPreviewCommand(
        case_id=command.case_id,
        specified_ltr_number=command.specified_ltr_number,
        plan_date=date(2026, 6, 10),
        test_item=command.test_item,
        sample_description=command.sample_description,
        test_type_in_sheet=command.test_type_in_sheet,
        project_leader=command.project_leader,
    )

    with pytest.raises(
        SpecifiedLtrWorkbookAuthorityPreviewError,
        match="LTR workbook preview changed",
    ):
        service.verify_ack(
            specified_ltr_number=command.specified_ltr_number,
            ack=preview.preview_ack,
            command=changed_command,
        )


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
    def __init__(
        self,
        *,
        existing: LtrWorkbookExistingRow | None = None,
        existing_by_number: dict[str, LtrWorkbookExistingRow] | None = None,
    ) -> None:
        self.existing = existing
        self.existing_by_number = existing_by_number or {}
        self.find_calls: list[tuple[str, tuple[str, ...] | None]] = []

    def find_ltr_number(self, ltr_number: str, sheet_names=None):
        self.find_calls.append((ltr_number, sheet_names))
        if self.existing_by_number:
            return self.existing_by_number.get(ltr_number)
        return self.existing

    def list_sheets(self):
        return ["2026"]


def _proposed_values(description: str):
    from backend.application.specified_ltr_workbook_authority_preview_service import (
        SpecifiedLtrWorkbookAuthorityRowValue,
    )

    labels = (
        ("project_type", "Project Type", "NPD"),
        ("description_pn", "Description P/N", description),
        ("test_item", "Test Item", "Qualification"),
        ("test_type", "Test Type", "Qualification"),
        ("requested_by", "Requested by", "Alice"),
        ("location", "Location", "Dongguan"),
        ("project_leader", "Project Leader", "Lab User"),
        ("test_result", "Test Result", None),
        ("failed_item", "Failed item", None),
        ("sample_deposition", "Sample deposition", "Return"),
        ("sub_contract", "Sub-contract", "No"),
        ("test_fee", "Test Fee", None),
        ("remarks_po", "Remarks (PO)", None),
    )
    return tuple(
        SpecifiedLtrWorkbookAuthorityRowValue(
            field_name=field_name,
            label=label,
            value=value,
            is_blank=value is None,
        )
        for field_name, label, value in labels
    )


def _command(ltr_number: str) -> SpecifiedLtrWorkbookAuthorityPreviewCommand:
    return SpecifiedLtrWorkbookAuthorityPreviewCommand(
        case_id="case-1",
        specified_ltr_number=ltr_number,
        plan_date=date(2026, 5, 10),
        test_item="Qualification",
        sample_description="Proposed description",
        test_type_in_sheet="Qualification",
        project_leader="Lab User",
    )


def _service(transaction):
    return SpecifiedLtrWorkbookAuthorityPreviewService(
        transaction_gateway=transaction,
        intake_confirmation_service=_FakeIntakeConfirmationService(),
        row_preview_service=_FakeLtrRowPreviewService(),
    )


class _FakeIntakeConfirmationService:
    def preview_case(self, case_id: str):
        return type(
            "Projection",
            (),
            {"project": object(), "application_form": object(), "sample_infos": ()},
        )()


class _FakeLtrRowPreviewService:
    def project_row_data(self, project, form, samples, command):
        return LtrWorkbookRowData(
            month=command.plan_date.strftime("%b"),
            total=0,
            monthly_number=11,
            dl_number=command.ltr_number,
            project_type="NPD",
            description_pn="Proposed description",
            test_item=command.test_item,
            test_type=command.test_type_in_sheet,
            requested_by="Alice",
            location="Dongguan",
            project_leader=command.project_leader,
            test_result=None,
            failed_item=None,
            sample_deposition="Return",
            sub_contract="No",
            test_fee=None,
            remarks_po=None,
        )
