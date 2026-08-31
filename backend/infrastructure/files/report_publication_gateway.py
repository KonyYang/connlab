"""Safe filesystem publication for incremental Word report updates."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import os
from pathlib import Path
import re
import shutil
from typing import Callable
from uuid import uuid4

from backend.application.current_report_update_service import (
    CurrentReportFileConflictError,
    CurrentReportFileUpdateResult,
)


ReportPublicationConflictError = CurrentReportFileConflictError
ReportFilePublicationResult = CurrentReportFileUpdateResult


class ReportPublicationGateway:
    """Build a report update in staging, then archive and replace atomically."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] = datetime.now,
        id_factory: Callable[[], str] = lambda: uuid4().hex,
    ) -> None:
        self._clock = clock
        self._ids = id_factory

    def discover_internal_reports(
        self,
        *,
        official_folder: Path,
        dl_number: str,
    ) -> tuple[Path, ...]:
        """Return controlled internal-report candidates in the official folder root."""
        folder = Path(official_folder)
        if not folder.is_dir():
            return tuple()
        normalized_dl = dl_number.strip().casefold()
        candidates = [
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.casefold() == ".docx"
            and _is_internal_report_name(path.stem, normalized_dl)
        ]
        return tuple(sorted(candidates, key=lambda value: value.name.casefold()))

    def discover_customer_reports(
        self,
        *,
        folder: Path,
        dl_number: str,
    ) -> tuple[Path, ...]:
        """Return customer-report candidates beside the current Internal Report."""
        root = Path(folder)
        if not root.is_dir():
            return tuple()
        normalized_dl = dl_number.strip().casefold()
        candidates = [
            path
            for path in root.iterdir()
            if path.is_file()
            and path.suffix.casefold() == ".docx"
            and _is_customer_report_name(path.stem, normalized_dl)
        ]
        return tuple(
            sorted(
                candidates,
                key=lambda value: (
                    "_customer_" in value.name.casefold(),
                    value.name.casefold(),
                ),
            )
        )

    def fingerprint(self, path: Path) -> str:
        """Return the SHA-256 fingerprint for one report file."""
        report = Path(path)
        if not report.is_file():
            raise FileNotFoundError(f"Current report does not exist: {report}")
        digest = sha256()
        with report.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def publish_update(
        self,
        *,
        current_path: Path,
        expected_current_sha256: str,
        history_root: Path,
        update_document: Callable[[Path, Path], Path],
    ) -> ReportFilePublicationResult:
        """Publish one staged update without exposing a partially written current file."""
        current = Path(current_path)
        if current.suffix.casefold() != ".docx" or not current.is_file():
            raise FileNotFoundError(f"Current internal report does not exist: {current}")
        expected = expected_current_sha256.strip().casefold()
        if not expected or self.fingerprint(current) != expected:
            raise ReportPublicationConflictError(
                "The current report changed after preview. Preview the update again."
            )

        staging = current.with_name(
            f".{current.stem}.{self._ids()}.stage{current.suffix}"
        )
        archive_directory: Path | None = None
        archive_path: Path | None = None
        published = False
        missing_history_parents = _missing_parents(Path(history_root))
        try:
            written = Path(update_document(current, staging))
            if written != staging or not staging.is_file():
                raise RuntimeError(
                    "The report updater did not produce the reserved staging file."
                )
            staged_sha256 = self.fingerprint(staging)
            current_sha256 = self.fingerprint(current)
            if current_sha256 != expected:
                raise ReportPublicationConflictError(
                    "The current report changed after preview. Preview the update again."
                )
            if staged_sha256 == current_sha256:
                return ReportFilePublicationResult(
                    current_path=current,
                    current_sha256=current_sha256,
                    changed=False,
                    archive_path=None,
                )

            archive_directory = _reserve_archive_directory(
                Path(history_root),
                self._clock(),
            )
            archive_directory.mkdir(parents=True, exist_ok=False)
            archive_path = archive_directory / current.name
            try:
                shutil.copy2(current, archive_path)
                if self.fingerprint(archive_path) != expected:
                    raise ReportPublicationConflictError(
                        "The current report changed while it was being archived. Preview the update again."
                    )
                if self.fingerprint(current) != expected:
                    raise ReportPublicationConflictError(
                        "The current report changed after preview. Preview the update again."
                    )
                os.replace(staging, current)
                published = True
            except PermissionError as exc:
                raise ReportPublicationConflictError(
                    "Close the current report in Word before updating it."
                ) from exc

            return ReportFilePublicationResult(
                current_path=current,
                current_sha256=staged_sha256,
                changed=True,
                archive_path=archive_path,
            )
        finally:
            staging.unlink(missing_ok=True)
            if not published and archive_path is not None:
                archive_path.unlink(missing_ok=True)
            if (
                archive_directory is not None
                and archive_directory.is_dir()
                and not any(archive_directory.iterdir())
            ):
                archive_directory.rmdir()
            if not published:
                for directory in missing_history_parents:
                    if directory.is_dir() and not any(directory.iterdir()):
                        directory.rmdir()

    def publish_new_current(
        self,
        *,
        source_path: Path,
        expected_source_sha256: str,
        target_path: Path,
    ) -> ReportFilePublicationResult:
        """Copy one managed draft into an empty official current-report slot."""
        source = Path(source_path)
        target = Path(target_path)
        if source.suffix.casefold() != ".docx" or not source.is_file():
            raise FileNotFoundError(f"Managed report draft does not exist: {source}")
        if target.suffix.casefold() != ".docx" or not target.parent.is_dir():
            raise FileNotFoundError(
                f"Official report folder does not exist: {target.parent}"
            )
        expected = expected_source_sha256.strip().casefold()
        if not expected or self.fingerprint(source) != expected:
            raise ReportPublicationConflictError(
                "The managed report changed after preview. Preview publication again."
            )
        if target.exists():
            raise ReportPublicationConflictError(
                f"An official report already exists at the target path: {target}"
            )

        staging = target.with_name(
            f".{target.stem}.{self._ids()}.stage{target.suffix}"
        )
        owns_target_reservation = False
        published = False
        try:
            shutil.copy2(source, staging)
            staged_sha256 = self.fingerprint(staging)
            if staged_sha256 != expected or self.fingerprint(source) != expected:
                raise ReportPublicationConflictError(
                    "The managed report changed while it was being copied. Preview publication again."
                )
            try:
                descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(descriptor)
                owns_target_reservation = True
                os.replace(staging, target)
                published = True
            except FileExistsError as exc:
                raise ReportPublicationConflictError(
                    f"An official report already exists at the target path: {target}"
                ) from exc
            except PermissionError as exc:
                raise ReportPublicationConflictError(
                    "The official report folder is not writable or the target is open in Word."
                ) from exc
            return ReportFilePublicationResult(
                current_path=target,
                current_sha256=staged_sha256,
                changed=True,
                archive_path=None,
            )
        finally:
            staging.unlink(missing_ok=True)
            if owns_target_reservation and not published:
                target.unlink(missing_ok=True)

    def publish_generated_current(
        self,
        *,
        source_path: Path,
        expected_source_sha256: str,
        target_path: Path,
        generate_document: Callable[[Path, Path], Path],
    ) -> ReportFilePublicationResult:
        """Generate a new sibling report while protecting its source fingerprint."""
        source = Path(source_path)
        target = Path(target_path)
        if source.suffix.casefold() != ".docx" or not source.is_file():
            raise FileNotFoundError(f"Current Internal Report does not exist: {source}")
        if target.suffix.casefold() != ".docx" or not target.parent.is_dir():
            raise FileNotFoundError(
                f"Customer report folder does not exist: {target.parent}"
            )
        expected = expected_source_sha256.strip().casefold()
        if not expected or self.fingerprint(source) != expected:
            raise ReportPublicationConflictError(
                "The current Internal Report changed after preview. Preview generation again."
            )
        if target.exists():
            raise ReportPublicationConflictError(
                f"A customer report already exists at the target path: {target}"
            )

        staging = target.with_name(
            f".{target.stem}.{self._ids()}.stage{target.suffix}"
        )
        owns_target_reservation = False
        published = False
        try:
            written = Path(generate_document(source, staging))
            if written != staging or not staging.is_file():
                raise RuntimeError(
                    "The customer report generator did not produce the reserved staging file."
                )
            staged_sha256 = self.fingerprint(staging)
            if self.fingerprint(source) != expected:
                raise ReportPublicationConflictError(
                    "The current Internal Report changed during customer report generation. Generate again."
                )
            try:
                descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(descriptor)
                owns_target_reservation = True
                os.replace(staging, target)
                published = True
            except FileExistsError as exc:
                raise ReportPublicationConflictError(
                    f"A customer report already exists at the target path: {target}"
                ) from exc
            except PermissionError as exc:
                raise ReportPublicationConflictError(
                    "The customer report folder is not writable or the target is open in Word."
                ) from exc
            return ReportFilePublicationResult(
                current_path=target,
                current_sha256=staged_sha256,
                changed=True,
                archive_path=None,
            )
        finally:
            staging.unlink(missing_ok=True)
            if owns_target_reservation and not published:
                target.unlink(missing_ok=True)


def _is_internal_report_name(stem: str, normalized_dl: str) -> bool:
    normalized = " ".join(stem.split()).casefold()
    if not normalized_dl or not (
        normalized == normalized_dl or normalized.startswith(f"{normalized_dl} ")
    ):
        return False
    if "report" not in normalized or "test record" in normalized:
        return False
    first_token = re.split(r"\s+", normalized, maxsplit=1)[0]
    return not first_token.endswith("-cr") and "customer" not in normalized


def _is_customer_report_name(stem: str, normalized_dl: str) -> bool:
    normalized = " ".join(stem.split()).casefold()
    expected_prefix = f"{normalized_dl}-cr"
    if not normalized_dl or not (
        normalized == expected_prefix or normalized.startswith(f"{expected_prefix} ")
    ):
        return False
    return "report" in normalized and "test record" not in normalized


def _reserve_archive_directory(history_root: Path, timestamp: datetime) -> Path:
    base = Path(history_root) / timestamp.strftime("%Y%m%d-%H%M%S")
    if not base.exists():
        return base
    for suffix in range(2, 10_000):
        candidate = base.with_name(f"{base.name} ({suffix})")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Unable to reserve a report History directory.")


def _missing_parents(path: Path) -> tuple[Path, ...]:
    missing: list[Path] = []
    current = Path(path)
    while not current.exists() and current != current.parent:
        missing.append(current)
        current = current.parent
    return tuple(missing)
