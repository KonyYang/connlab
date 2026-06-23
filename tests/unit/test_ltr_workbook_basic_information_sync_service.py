from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.ltr_workbook_basic_information_sync_service import (
    CommitLtrWorkbookBasicInformationSyncCommand,
    LtrWorkbookBasicInformationSyncError,
    LtrWorkbookBasicInformationSyncService,
    PreviewLtrWorkbookBasicInformationSyncCommand,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.office import LtrWorkbookExistingRow, LtrWorkbookRowPointer


def test_preview_builds_row_from_confirmed_basic_information_and_existing_workbook_row() -> None:
    service, session = _service()

    preview = service.preview(
        PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1")
    )

    assert preview.ltr_number == "DL-2026-05-011"
    assert preview.target_sheet == "2026"
    assert preview.target_row == 3
    assert preview.row_data.dl_number == "DL-2026-05-011"
    assert preview.row_data.project_type == "NPD"
    assert preview.row_data.description_pn == "Coolpower HDF:PN-001"
    assert preview.row_data.test_item == "Qualification Testing"
    assert preview.row_data.test_type == "Partial Qualification"
    assert preview.row_data.requested_by == "MP Cao"
    assert preview.row_data.location == "Dongguan"
    assert preview.row_data.project_leader == "Even Yang"
    assert preview.row_data.sub_contract == "No"
    assert [value.field_name for value in preview.comparison_values] == [
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
    ]
    comparison_by_field = {
        value.field_name: value for value in preview.comparison_values
    }
    assert comparison_by_field["project_type"].label == "Project Type"
    assert comparison_by_field["project_type"].current_value == "NPD"
    assert comparison_by_field["project_type"].pending_value == "NPD"
    assert comparison_by_field["description_pn"].label == "Description P/N"
    assert comparison_by_field["description_pn"].current_value == "Old P/N"
    assert comparison_by_field["description_pn"].pending_value == "Coolpower HDF:PN-001"
    assert comparison_by_field["test_item"].label == "Test Item"
    assert comparison_by_field["test_item"].current_value == "Old testing"
    assert comparison_by_field["test_item"].pending_value == "Qualification Testing"
    assert comparison_by_field["test_result"].label == "Test Result"
    assert comparison_by_field["test_result"].current_value == "In progress"
    assert comparison_by_field["test_result"].pending_value is None
    assert comparison_by_field["test_fee"].current_value == "1200"
    assert comparison_by_field["test_fee"].pending_value is None
    assert comparison_by_field["location"].current_value == "Suzhou"
    assert comparison_by_field["location"].pending_value == "Dongguan"
    assert session.find_calls == [("DL-2026-05-011", ("2026",))]
    assert session.appended == []


def test_preview_uses_sheet_test_type_without_application_form_fallback() -> None:
    service, _ = _service(
        basic_information=_basic_information(
            {
                "test_type": "Product/Process Qualification",
                "test_type_in_sheet": "Reliability",
            }
        )
    )

    preview = service.preview(
        PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1")
    )

    assert preview.status == "ready"
    assert preview.row_data is not None
    assert preview.row_data.test_type == "Reliability"


def test_preview_blocks_when_sheet_test_type_is_missing_even_if_application_type_exists() -> None:
    service, _ = _service(
        basic_information=_basic_information(
            {
                "test_type": "Product/Process Qualification",
                "test_type_in_sheet": "",
            }
        )
    )

    preview = service.preview(
        PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1")
    )

    assert preview.status == "blocked"
    assert preview.blockers == (
        "Test Type in sheet is required in confirmed Basic Information.",
    )


def test_preview_blocks_when_description_pn_is_missing_even_if_product_description_exists() -> None:
    service, _ = _service(
        basic_information=_basic_information(
            {
                "description_pn": "",
                "product_description": "Product Description must not be used",
            }
        )
    )

    preview = service.preview(
        PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1")
    )

    assert preview.status == "blocked"
    assert preview.blockers == (
        "Description P/N is required in confirmed Basic Information.",
    )


def test_preview_blocks_without_confirmed_basic_information() -> None:
    service, _ = _service(basic_information=None)

    preview = service.preview(PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1"))

    assert preview.status == "blocked"
    assert preview.blockers == (
        "Confirm Basic Information before synchronizing LTR workbook.",
    )
    assert preview.columns == ()
    assert preview.comparison_values == ()


def test_preview_blocks_when_existing_ltr_row_is_missing() -> None:
    service, _ = _service(rows_by_sheet={"2026": []})

    preview = service.preview(PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1"))

    assert preview.status == "blocked"
    assert preview.blockers == (
        "Registered LTR row not found in workbook: DL-2026-05-011",
    )


def test_commit_rejects_stale_basic_information_context() -> None:
    service, _ = _service()

    with pytest.raises(LtrWorkbookBasicInformationSyncError, match="Basic Information changed"):
        service.commit(
            CommitLtrWorkbookBasicInformationSyncCommand(
                project_id="P1",
                operator_confirmed=True,
                preview_acknowledged=True,
                expected_confirmed_basic_information_version=99,
                expected_confirmed_basic_information_source_signature_hash="old",
            )
        )


def test_commit_writes_existing_row_only() -> None:
    service, session = _service()
    preview = service.preview(
        PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1")
    )

    result = service.commit(
        CommitLtrWorkbookBasicInformationSyncCommand(
            project_id="P1",
            operator_confirmed=True,
            preview_acknowledged=True,
            expected_confirmed_basic_information_version=preview.confirmed_basic_information_version,
            expected_confirmed_basic_information_source_signature_hash=(
                preview.confirmed_basic_information_source_signature_hash
            ),
        )
    )

    assert result.row_number == 3
    assert result.sheet_name == "2026"
    assert session.replaced[0].row_number == 3
    assert session.replaced[0].dl_number == "DL-2026-05-011"
    assert session.appended == []
    assert session.saved is True


def test_preview_uses_read_only_transaction_without_saving() -> None:
    service, session, transaction = _service(return_gateway=True)

    preview = service.preview(
        PreviewLtrWorkbookBasicInformationSyncCommand(project_id="P1")
    )

    assert preview.status == "ready"
    assert transaction.read_only_open_count == 1
    assert transaction.write_open_count == 0
    assert session.saved is False


def _service(
    *,
    basic_information: ConfirmedBasicInformationSnapshot | None | object = "__default__",
    rows_by_sheet: dict[str, list[tuple[object, ...]]] | None = None,
    return_gateway: bool = False,
):
    session = _FakeWorkbookSession(
        rows_by_sheet
        if rows_by_sheet is not None
        else {
            "2026": [
                ("May", 1, 1, "DL-2026-05-001"),
                (
                    "May",
                    2,
                    2,
                    "DL-2026-05-011",
                    "NPD",
                    "Old P/N",
                    "Old testing",
                    "Old type",
                    "Old requester",
                    "Suzhou",
                    "Old leader",
                    "In progress",
                    "Old failed item",
                    "Old sample deposition",
                    "Yes",
                    "1200",
                    "Old PO",
                ),
            ]
        }
    )
    snapshot = _basic_information() if basic_information == "__default__" else basic_information
    transaction_gateway = _FakeTransactionGateway(session)
    service = LtrWorkbookBasicInformationSyncService(
        ltr_store=_LtrStore(),
        basic_information_reader=_BasicInformationReader(snapshot),
        transaction_gateway=transaction_gateway,
    )
    if return_gateway:
        return service, session, transaction_gateway
    return service, session


class _BasicInformationReader:
    def __init__(self, snapshot: ConfirmedBasicInformationSnapshot | None) -> None:
        self.snapshot = snapshot

    def get_latest_confirmed(self, project_id: str):
        return self.snapshot if project_id == "P1" else None


class _LtrStore:
    def list_by_project(self, project_id: str):
        if project_id != "P1":
            return []
        return [
            LtrRecord(
                ltr_id="L1",
                project_id="P1",
                ltr_number="DL-2026-05-011",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 5, 1),
            )
        ]


class _FakeTransactionGateway:
    def __init__(self, session: "_FakeWorkbookSession") -> None:
        self.session = session
        self.read_only_open_count = 0
        self.write_open_count = 0

    def open_transaction(self):
        self.write_open_count += 1
        return _FakeTransaction(self.session, save_on_exit=False)

    def open_read_only_transaction(self):
        self.read_only_open_count += 1
        return _FakeTransaction(self.session, save_on_exit=False)

    def run_short_transaction(self, operation):
        context = _context(self.session)
        result = operation(context)
        self.session.saved = True
        return result


class _FakeTransaction:
    def __init__(self, session: "_FakeWorkbookSession", *, save_on_exit: bool) -> None:
        self.session = session
        self.save_on_exit = save_on_exit

    def __enter__(self):
        return _context(self.session)

    def __exit__(self, exc_type, exc, traceback):
        if self.save_on_exit and exc_type is None:
            self.session.saved = True


def _context(session: "_FakeWorkbookSession"):
    return SimpleNamespace(
        session=session,
        workbook_path=Path("LTR_number.xls"),
        backup_path=Path("backups/LTR_number.xls"),
    )


class _FakeWorkbookSession:
    def __init__(self, rows_by_sheet: dict[str, list[tuple[object, ...]]]) -> None:
        self.rows_by_sheet = rows_by_sheet
        self.find_calls: list[tuple[str, tuple[str, ...] | None]] = []
        self.replaced: list[LtrWorkbookRowPointer] = []
        self.appended: list[LtrWorkbookRowPointer] = []
        self.saved = False

    def list_sheets(self):
        return list(self.rows_by_sheet)

    def find_ltr_number(self, ltr_number: str, sheet_names=None):
        normalized_sheets = tuple(sheet_names) if sheet_names is not None else None
        self.find_calls.append((ltr_number, normalized_sheets))
        for sheet in sheet_names or tuple(self.rows_by_sheet):
            for index, row in enumerate(self.rows_by_sheet[sheet], start=2):
                if len(row) >= 4 and str(row[3]).upper() == ltr_number.upper():
                    return LtrWorkbookExistingRow(sheet, index, str(row[3]).upper(), row)
        return None

    def write_registration_row(self, sheet_name, row_number, row_data):
        pointer = LtrWorkbookRowPointer(sheet_name, row_number, row_data.dl_number)
        self.replaced.append(pointer)
        return pointer

    def append_registration_row(self, sheet_name, row_data):
        pointer = LtrWorkbookRowPointer(sheet_name, 999, row_data.dl_number)
        self.appended.append(pointer)
        return pointer


def _basic_information(
    value_overrides: dict[str, str] | None = None,
) -> ConfirmedBasicInformationSnapshot:
    values = {
        "dl_number": "DL-2026-05-011",
        "project_type": "New Product Development",
        "product_description": "Coolpower HDF 3.40mm pin",
        "description_pn": "Coolpower HDF:PN-001",
        "test_item": "Qualification Testing",
        "test_type": "Application Type",
        "test_type_in_sheet": "Partial Qualification",
        "requested_by": "MP Cao",
        "location": "Dongguan",
        "project_leader": "Even Yang",
        "sub_contract": "No",
    }
    if value_overrides:
        values.update(value_overrides)
    return ConfirmedBasicInformationSnapshot(
        project_id="P1",
        version=7,
        values=values,
        source_signature='{"basic":"info"}',
        confirmed_at="2026-06-20T00:00:00+00:00",
        confirmed_by="tester",
    )
