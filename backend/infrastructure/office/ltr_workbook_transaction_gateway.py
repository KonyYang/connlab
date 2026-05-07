"""Locked short-transaction gateway for external LTR workbook writes."""

from __future__ import annotations

import hashlib
import os
import shutil
import socket
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, TypeVar

from backend.infrastructure.office.excel_com_ltr_workbook_gateway import (
    ExcelComLTRWorkbookGateway,
    ExcelComLTRWorkbookWriteSession,
    LtrWorkbookWriteConfig,
    LtrWorkbookWriteDisabledError,
    LtrWorkbookWriteError,
)
from backend.infrastructure.office.office_facade import OfficeFacade


T = TypeVar("T")


class LtrWorkbookLockTimeoutError(LtrWorkbookWriteError):
    """Raised when the LTR workbook lock cannot be acquired before timeout."""


class LtrWorkbookBackupError(LtrWorkbookWriteError):
    """Raised when the LTR workbook cannot be backed up before writing."""


@dataclass(frozen=True, slots=True)
class LtrWorkbookTransactionConfig:
    """Configuration for one guarded external LTR workbook write transaction."""

    path: Path | None
    write_enabled: bool = False
    modify_password: str | None = None
    lock_dir: Path | None = None
    lock_timeout_seconds: float = 120
    backup_dir: Path | None = None
    lock_poll_seconds: float = 0.2

    def write_config(self) -> LtrWorkbookWriteConfig:
        """Return the existing COM write-session configuration."""
        return LtrWorkbookWriteConfig(
            path=self.path,
            write_enabled=self.write_enabled,
            modify_password=self.modify_password,
        )


@dataclass(frozen=True, slots=True)
class LtrWorkbookTransactionContext:
    """Open workbook transaction state returned to callers."""

    session: ExcelComLTRWorkbookWriteSession
    workbook_path: Path
    lock_path: Path
    backup_path: Path


class LtrWorkbookTransactionGateway:
    """Coordinate lock, backup, COM open, save, close, and lock release."""

    def __init__(
        self,
        office: OfficeFacade,
        config: LtrWorkbookTransactionConfig,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        """Create the transaction gateway."""
        self._office = office
        self._config = config
        self._clock = clock
        self._sleeper = sleeper

    def open_transaction(self) -> "LtrWorkbookTransaction":
        """Open a guarded transaction context without connecting business flows."""
        return LtrWorkbookTransaction(
            office=self._office,
            config=self._config,
            clock=self._clock,
            sleeper=self._sleeper,
        )

    def run_short_transaction(
        self,
        operation: Callable[[LtrWorkbookTransactionContext], T],
    ) -> T:
        """Run one operation, save once, close the workbook, and release the lock."""
        with self.open_transaction() as transaction:
            result = operation(transaction)
            transaction.session.save()
            return result


class LtrWorkbookTransaction:
    """Context manager for one locked LTR workbook write transaction."""

    def __init__(
        self,
        *,
        office: OfficeFacade,
        config: LtrWorkbookTransactionConfig,
        clock: Callable[[], float],
        sleeper: Callable[[float], None],
    ) -> None:
        """Create a transaction context."""
        self._office = office
        self._config = config
        self._clock = clock
        self._sleeper = sleeper
        self._lock_path: Path | None = None
        self._session: ExcelComLTRWorkbookWriteSession | None = None

    def __enter__(self) -> LtrWorkbookTransactionContext:
        """Acquire the lock, create a backup, and open the workbook."""
        workbook_path = _validated_workbook_path(self._config)
        lock_path = _acquire_lock(
            workbook_path,
            self._config,
            clock=self._clock,
            sleeper=self._sleeper,
        )
        self._lock_path = lock_path
        try:
            backup_path = _backup_workbook(workbook_path, self._config)
            session = ExcelComLTRWorkbookGateway(
                self._office,
                self._config.write_config(),
            ).open_write_session()
            self._session = session.__enter__()
            return LtrWorkbookTransactionContext(
                session=self._session,
                workbook_path=workbook_path,
                lock_path=lock_path,
                backup_path=backup_path,
            )
        except Exception:
            self._release_lock()
            raise

    def __exit__(self, exc_type, exc, traceback) -> None:
        """Close the workbook without implicit save and release the lock."""
        try:
            if self._session is not None:
                self._session.__exit__(exc_type, exc, traceback)
        finally:
            self._release_lock()

    def _release_lock(self) -> None:
        """Remove the owned lock file if it still exists."""
        if self._lock_path is None:
            return
        try:
            self._lock_path.unlink(missing_ok=True)
        finally:
            self._lock_path = None


def _validated_workbook_path(config: LtrWorkbookTransactionConfig) -> Path:
    """Validate transaction-level settings before lock acquisition."""
    if not config.write_enabled:
        raise LtrWorkbookWriteDisabledError("LTR workbook write is disabled.")
    if config.path is None:
        raise LtrWorkbookWriteError("LTR workbook path is not configured.")
    if not config.modify_password:
        raise LtrWorkbookWriteError("LTR workbook modify password is not configured.")
    if config.lock_dir is None:
        raise LtrWorkbookWriteError("LTR workbook lock directory is not configured.")
    if config.backup_dir is None:
        raise LtrWorkbookWriteError("LTR workbook backup directory is not configured.")
    if config.lock_timeout_seconds < 0:
        raise LtrWorkbookWriteError("LTR workbook lock timeout cannot be negative.")
    if config.lock_poll_seconds <= 0:
        raise LtrWorkbookWriteError("LTR workbook lock poll interval must be positive.")
    return Path(config.path).resolve()


def _acquire_lock(
    workbook_path: Path,
    config: LtrWorkbookTransactionConfig,
    *,
    clock: Callable[[], float],
    sleeper: Callable[[float], None],
) -> Path:
    """Acquire an exclusive lock file or fail after the configured timeout."""
    lock_dir = Path(config.lock_dir or "").resolve()
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / _lock_file_name(workbook_path)
    deadline = clock() + config.lock_timeout_seconds
    while True:
        try:
            descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            if clock() >= deadline:
                raise LtrWorkbookLockTimeoutError(
                    f"LTR workbook is locked: {lock_path}"
                ) from exc
            sleeper(min(config.lock_poll_seconds, max(deadline - clock(), 0)))
            continue
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(_lock_file_content(workbook_path))
        return lock_path


def _backup_workbook(workbook_path: Path, config: LtrWorkbookTransactionConfig) -> Path:
    """Copy the workbook to the configured backup directory before COM open."""
    if not workbook_path.is_file():
        raise LtrWorkbookBackupError(f"LTR workbook does not exist: {workbook_path}")
    backup_dir = Path(config.backup_dir or "").resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = backup_dir / f"{workbook_path.stem}_{timestamp}{workbook_path.suffix}"
    try:
        shutil.copy2(workbook_path, backup_path)
    except OSError as exc:
        raise LtrWorkbookBackupError(
            f"Failed to back up LTR workbook to {backup_path}"
        ) from exc
    return backup_path


def _lock_file_name(workbook_path: Path) -> str:
    """Return a stable per-workbook lock file name."""
    digest = hashlib.sha1(str(workbook_path).encode("utf-8")).hexdigest()[:12]
    return f"{workbook_path.name}.{digest}.lock"


def _lock_file_content(workbook_path: Path) -> str:
    """Return diagnostic lock metadata without secrets."""
    return (
        f"workbook={workbook_path}\n"
        f"pid={os.getpid()}\n"
        f"host={socket.gethostname()}\n"
        f"created_at={datetime.now().isoformat(timespec='seconds')}\n"
    )
