import hashlib
from pathlib import Path

import pytest

from backend.infrastructure.office import (
    LtrWorkbookBackupError,
    LtrWorkbookLockTimeoutError,
    LtrWorkbookRowData,
    LtrWorkbookTransactionConfig,
    LtrWorkbookTransactionGateway,
)


def test_ltr_workbook_transaction_locks_backs_up_opens_and_releases(
    tmp_path: Path,
) -> None:
    """Transaction creates a lock and backup before opening the workbook."""
    workbook = tmp_path / "LTR_number.xls"
    workbook.write_bytes(b"workbook")
    office = _FakeOfficeFacade()
    gateway = LtrWorkbookTransactionGateway(
        office,
        _config(workbook, tmp_path),
    )

    with gateway.open_transaction() as transaction:
        assert transaction.lock_path.is_file()
        assert transaction.backup_path.is_file()
        assert transaction.backup_path.read_bytes() == b"workbook"
        transaction.session.append_registration_row(
            "2026",
            LtrWorkbookRowData(
                month="Apr",
                total=31,
                monthly_number=31,
                dl_number="DL-2026-04-031",
            ),
        )
        transaction.session.save()
        lock_path = transaction.lock_path

    assert lock_path.exists() is False
    assert office.open_calls == [
        {
            "path": workbook.resolve(),
            "modify_password": "operator-secret",
            "read_only": False,
        }
    ]
    assert office.handle.saved is True
    assert office.handle.closed is True


def test_ltr_workbook_transaction_timeout_preserves_existing_lock(
    tmp_path: Path,
) -> None:
    """Existing locks block COM open and remain for diagnostics."""
    workbook = tmp_path / "LTR_number.xls"
    workbook.write_bytes(b"workbook")
    config = _config(workbook, tmp_path, lock_timeout_seconds=0)
    existing_lock = _expected_lock_path(config)
    existing_lock.parent.mkdir(parents=True, exist_ok=True)
    existing_lock.write_text("owner=other", encoding="utf-8")
    office = _FakeOfficeFacade()

    with pytest.raises(LtrWorkbookLockTimeoutError, match="locked"):
        with LtrWorkbookTransactionGateway(
            office,
            config,
            sleeper=lambda _: None,
        ).open_transaction():
            pass

    assert existing_lock.read_text(encoding="utf-8") == "owner=other"
    assert office.open_calls == []
    backup_dir = tmp_path / "backups"
    assert not backup_dir.exists() or not any(backup_dir.iterdir())


def test_ltr_workbook_transaction_backup_failure_releases_lock(
    tmp_path: Path,
) -> None:
    """A missing workbook fails before COM open and releases the owned lock."""
    workbook = tmp_path / "missing.xls"
    config = _config(workbook, tmp_path)

    with pytest.raises(LtrWorkbookBackupError, match="does not exist"):
        with LtrWorkbookTransactionGateway(
            _FakeOfficeFacade(),
            config,
        ).open_transaction():
            pass

    assert _expected_lock_path(config).exists() is False


def test_ltr_workbook_short_transaction_saves_closes_and_releases(
    tmp_path: Path,
) -> None:
    """run_short_transaction saves exactly after the supplied operation."""
    workbook = tmp_path / "LTR_number.xls"
    workbook.write_bytes(b"workbook")
    office = _FakeOfficeFacade()
    gateway = LtrWorkbookTransactionGateway(office, _config(workbook, tmp_path))

    result = gateway.run_short_transaction(lambda transaction: transaction.backup_path.name)

    assert result.endswith(".xls")
    assert office.handle.saved is True
    assert office.handle.closed is True
    assert _expected_lock_path(_config(workbook, tmp_path)).exists() is False


def _config(
    workbook: Path,
    tmp_path: Path,
    *,
    lock_timeout_seconds: float = 1,
) -> LtrWorkbookTransactionConfig:
    """Return a complete transaction config for tests."""
    return LtrWorkbookTransactionConfig(
        path=workbook,
        write_enabled=True,
        modify_password="operator-secret",
        lock_dir=tmp_path / "locks",
        lock_timeout_seconds=lock_timeout_seconds,
        backup_dir=tmp_path / "backups",
        lock_poll_seconds=0.01,
    )


def _expected_lock_path(config: LtrWorkbookTransactionConfig) -> Path:
    """Return the only lock path created for a test workbook."""
    lock_dir = Path(config.lock_dir or "")
    workbook = Path(config.path or "").resolve()
    digest = hashlib.sha1(str(workbook).encode("utf-8")).hexdigest()[:12]
    return lock_dir / f"{workbook.name}.{digest}.lock"


class _FakeOfficeFacade:
    def __init__(self) -> None:
        self.handle = _FakeHandle()
        self.open_calls: list[dict] = []

    def open_excel_workbook(
        self,
        source_path: Path,
        *,
        modify_password: str | None = None,
        read_only: bool = False,
    ):
        self.open_calls.append(
            {
                "path": source_path,
                "modify_password": modify_password,
                "read_only": read_only,
            }
        )
        return self.handle


class _FakeHandle:
    def __init__(self) -> None:
        self.workbook = _FakeWorkbook()
        self.saved = False
        self.closed = False

    def save(self) -> None:
        self.saved = True

    def close(self, save_changes: bool = False) -> None:
        self.closed = True


class _FakeWorkbook:
    def __init__(self) -> None:
        self.ReadOnly = False
        self.Worksheets = _FakeWorksheets()


class _FakeWorksheets:
    def __init__(self) -> None:
        self._sheets = {"2026": _FakeSheet()}

    def __iter__(self):
        return iter(self._sheets.values())

    def Item(self, name: str):
        return self._sheets[name]


class _FakeSheet:
    def __init__(self) -> None:
        self.Name = "2026"
        self.UsedRange = _FakeUsedRange()
        self.last_written_rows: list[list[object]] = []
        self._cells = {
            (2, 1): "Apr",
            (2, 2): 30,
            (2, 3): 30,
            (2, 4): "DL-2026-04-030",
        }

    def Range(self, address: str):
        return _FakeRange(self, address)

    def Cells(self, row: int, column: int):
        return _FakeCell(self, row, column)


class _FakeUsedRange:
    def __init__(self) -> None:
        self.Rows = _FakeRows()


class _FakeRows:
    Count = 2


class _FakeRange:
    def __init__(self, sheet: _FakeSheet, address: str) -> None:
        self._sheet = sheet
        self._address = address

    @property
    def Value(self):
        return (("Apr", 30, 30, "DL-2026-04-030"),)

    @Value.setter
    def Value(self, rows) -> None:
        if not isinstance(rows, list):
            return
        self._sheet.last_written_rows.extend(rows)
        start_row = _row_number(self._address.split(":", 1)[0])
        for offset, row_values in enumerate(rows):
            row_number = start_row + offset
            for column, value in enumerate(row_values, start=1):
                self._sheet._cells[(row_number, column)] = value

    def Merge(self) -> None:
        return None

    def UnMerge(self) -> None:
        return None


class _FakeCell:
    MergeCells = False

    def __init__(self, sheet: _FakeSheet, row: int, column: int) -> None:
        self._sheet = sheet
        self._row = row
        self._column = column

    @property
    def Value(self):
        return self._sheet._cells.get((self._row, self._column))

    @Value.setter
    def Value(self, value) -> None:
        self._sheet._cells[(self._row, self._column)] = value


def _row_number(address: str) -> int:
    digits = "".join(character for character in address if character.isdigit())
    return int(digits)
