from __future__ import annotations

from datetime import date
from pathlib import Path

from backend.application.registered_ltr_workbook_row_preview_service import (
    RegisteredLtrWorkbookRowPreviewCommand,
    RegisteredLtrWorkbookRowPreviewService,
)
from backend.domain import LtrRecord, LtrStatus


def test_registered_ltr_preview_reads_workbook_row_without_basic_information() -> None:
    service, session, transaction = _service()

    preview = service.preview(
        RegisteredLtrWorkbookRowPreviewCommand(project_id="P1")
    )

    assert preview.status == "found"
    assert preview.project_id == "P1"
    assert preview.ltr_number == "DL-2026-05-011"
    assert preview.workbook_path == Path("D:/PublicProject/LTR.xlsx")
    assert preview.sheet_name == "2026"
    assert preview.row_number == 3
    assert [(value.field_name, value.label) for value in preview.row_values] == [
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
    ]
    assert preview.row_values[0].value == "NPD"
    assert preview.row_values[1].value == "Coolpower HDF"
    assert preview.row_values[7].is_blank is True
    assert session.read_ltr_number_cells_calls == ["2026"]
    assert session.read_registration_row_calls == [("2026", 3)]
    assert transaction.write_opened is False
    assert transaction.short_transaction_opened is False


def test_registered_ltr_preview_blocks_without_registered_ltr() -> None:
    service, _session, _transaction = _service(records=[])

    preview = service.preview(
        RegisteredLtrWorkbookRowPreviewCommand(project_id="P1")
    )

    assert preview.status == "blocked"
    assert preview.ltr_number is None
    assert preview.row_values == ()
    assert preview.blockers == ("Registered LTR is required for workbook row preview.",)


def test_registered_ltr_preview_returns_not_found_for_missing_workbook_row() -> None:
    service, _session, _transaction = _service(rows_by_sheet={"2026": []})

    preview = service.preview(
        RegisteredLtrWorkbookRowPreviewCommand(project_id="P1")
    )

    assert preview.status == "not_found"
    assert preview.ltr_number == "DL-2026-05-011"
    assert preview.row_values == ()
    assert preview.blockers == ("Registered LTR row not found in workbook: DL-2026-05-011",)


def test_registered_ltr_preview_blocks_duplicate_exact_workbook_rows() -> None:
    service, _session, _transaction = _service(
        rows_by_sheet={
            "2026": [
                _row("DL-2026-05-011"),
                _row(" DL-2026-05-011\u00a0"),
            ]
        }
    )

    preview = service.preview(
        RegisteredLtrWorkbookRowPreviewCommand(project_id="P1")
    )

    assert preview.status == "blocked"
    assert preview.blockers == ("Duplicate exact LTR rows found in workbook: DL-2026-05-011",)


def test_registered_ltr_preview_blocks_workbook_open_failures() -> None:
    service, _session, _transaction = _service(open_error=RuntimeError("workbook locked"))

    preview = service.preview(
        RegisteredLtrWorkbookRowPreviewCommand(project_id="P1")
    )

    assert preview.status == "blocked"
    assert preview.ltr_number == "DL-2026-05-011"
    assert preview.row_values == ()
    assert preview.blockers == (
        "Unable to read LTR workbook for preview: workbook locked",
    )


def test_registered_ltr_preview_blocks_workbook_read_failures() -> None:
    service, _session, _transaction = _service(read_error=RuntimeError("sheet unreadable"))

    preview = service.preview(
        RegisteredLtrWorkbookRowPreviewCommand(project_id="P1")
    )

    assert preview.status == "blocked"
    assert preview.ltr_number == "DL-2026-05-011"
    assert preview.row_values == ()
    assert preview.blockers == (
        "Unable to read LTR workbook for preview: sheet unreadable",
    )


def _service(
    *,
    records: list[LtrRecord] | None = None,
    rows_by_sheet: dict[str, list[tuple[object, ...]]] | None = None,
    open_error: Exception | None = None,
    read_error: Exception | None = None,
):
    session = _FakeWorkbookSession(
        rows_by_sheet=rows_by_sheet
        or {"2026": [_row("DL-2026-05-010"), _row("DL-2026-05-011")]},
        read_error=read_error,
    )
    transaction = _FakeTransactionGateway(session, open_error=open_error)
    service = RegisteredLtrWorkbookRowPreviewService(
        ltr_store=_FakeLtrStore(
            records
            if records is not None
            else [
                LtrRecord(
                    ltr_id="LTR1",
                    project_id="P1",
                    ltr_number="DL-2026-05-011",
                    status=LtrStatus.REGISTERED,
                    registered_on=date(2026, 5, 11),
                )
            ]
        ),
        transaction_gateway=transaction,
    )
    return service, session, transaction


def _row(ltr_number: str) -> tuple[object, ...]:
    return (
        "May",
        10,
        11,
        ltr_number,
        "NPD",
        "Coolpower HDF",
        "Qualification Testing",
        "Qualification",
        "MP Cao",
        "Dongguan",
        "Lab User",
        "",
        "",
        "Return",
        "No",
        "1200",
        "PO-1",
    )


class _FakeLtrStore:
    def __init__(self, records: list[LtrRecord]) -> None:
        self._records = records

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [record for record in self._records if record.project_id == project_id]


class _FakeTransactionGateway:
    def __init__(
        self,
        session: "_FakeWorkbookSession",
        *,
        open_error: Exception | None = None,
    ) -> None:
        self.session = session
        self.open_error = open_error
        self.write_opened = False
        self.short_transaction_opened = False

    def open_read_only_transaction(self):
        if self.open_error is not None:
            raise self.open_error
        return _FakeReadOnlyTransaction(self.session)

    def open_transaction(self):  # pragma: no cover - safety assertion helper
        self.write_opened = True
        raise AssertionError("Registered row preview must not open a write transaction.")

    def run_short_transaction(self, operation):  # pragma: no cover - safety assertion helper
        self.short_transaction_opened = True
        raise AssertionError("Registered row preview must not run a write transaction.")


class _FakeReadOnlyTransaction:
    def __init__(self, session: "_FakeWorkbookSession") -> None:
        self._session = session

    def __enter__(self):
        return type(
            "Context",
            (),
            {
                "session": self._session,
                "workbook_path": Path("D:/PublicProject/LTR.xlsx"),
            },
        )()

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


class _FakeWorkbookSession:
    def __init__(
        self,
        *,
        rows_by_sheet: dict[str, list[tuple[object, ...]]],
        read_error: Exception | None = None,
    ) -> None:
        self.rows_by_sheet = rows_by_sheet
        self.read_error = read_error
        self.read_ltr_number_cells_calls: list[str] = []
        self.read_registration_row_calls: list[tuple[str, int]] = []

    def read_ltr_number_cells(self, sheet_name: str):
        if self.read_error is not None:
            raise self.read_error
        self.read_ltr_number_cells_calls.append(sheet_name)
        return tuple(
            (index, row[3] if len(row) > 3 else None)
            for index, row in enumerate(self.rows_by_sheet.get(sheet_name, ()), start=2)
        )

    def read_registration_row(self, sheet_name: str, row_number: int):
        self.read_registration_row_calls.append((sheet_name, row_number))
        rows = self.rows_by_sheet.get(sheet_name, ())
        return rows[row_number - 2]
