"""Safe filesystem publication for incremental Word report updates."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import os
from pathlib import Path
import re
import shutil
import tempfile
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

    def publish_regenerated_current(
        self,
        *,
        source_path: Path,
        expected_source_sha256: str,
        current_path: Path | None,
        expected_current_sha256: str | None,
        target_path: Path,
        history_root: Path,
        persist: Callable[[ReportFilePublicationResult], None],
        pre_publish: Callable[[], None] | None = None,
    ) -> ReportFilePublicationResult:
        """Replace a validated fresh report and retain recovery until metadata commits.

        Explicit regeneration always archives, including byte-identical output. The
        archive is also the rollback copy when the metadata transaction fails.
        """
        source, target = Path(source_path), Path(target_path)
        current = Path(current_path) if current_path is not None else None
        if target.suffix.casefold() != ".docx" or not target.parent.is_dir():
            raise FileNotFoundError("The report destination folder is unavailable. Restore it and preview again.")
        if self.fingerprint(source) != expected_source_sha256:
            raise ReportPublicationConflictError("The generated report changed. Generate again.")
        current_identity = _file_identity(current) if current is not None else None

        def require_current() -> None:
            if current is not None and (
                not current.is_file() or self.fingerprint(current) != expected_current_sha256
                or _file_identity(current) != current_identity
            ):
                raise ReportPublicationConflictError("The current report changed. Preview generation again.")
            if target != current and target.exists():
                raise ReportPublicationConflictError("A report already occupies the new destination. Resolve the conflict and preview again.")

        require_current()
        descriptor, staging_name = tempfile.mkstemp(prefix=".report-", suffix=".stage", dir=target.parent)
        os.close(descriptor)
        staging = Path(staging_name)
        staging_identity = _file_identity(staging)
        archive: Path | None = None
        archive_identity: tuple[int, int] | None = None
        published = False
        old_removed = False
        committed = False
        missing_parents = _missing_parents(Path(history_root))
        try:
            shutil.copy2(source, staging)
            staged_hash = self.fingerprint(staging)
            if staged_hash != expected_source_sha256 or self.fingerprint(source) != expected_source_sha256:
                raise ReportPublicationConflictError("The generated report changed during publication. Generate again.")
            if pre_publish:
                pre_publish()
            require_current()
            if current is not None:
                archive = _reserve_archive_path(Path(history_root), current, self._clock())
                archive_identity = _file_identity(archive)
                shutil.copy2(current, archive)
                if self.fingerprint(archive) != expected_current_sha256:
                    raise ReportPublicationConflictError("The old report changed during archival. Preview generation again.")
            if pre_publish:
                pre_publish()
            require_current()
            if current is not None:
                # Retire the reviewed current file before publishing any active
                # sibling. No observer ever sees two current internal reports.
                if _file_identity(archive) != archive_identity or self.fingerprint(archive) != expected_current_sha256:
                    raise ReportPublicationConflictError("The reserved report archive changed. Review History/Report and preview again.")
                os.replace(current, archive)
                old_removed = True
                archive_identity = _file_identity(archive)
                if self.fingerprint(archive) != expected_current_sha256 or _file_identity(archive) != current_identity:
                    raise ReportPublicationConflictError("The report changed while being moved into History. Preview generation again.")
            if self.fingerprint(staging) != expected_source_sha256:
                raise ReportPublicationConflictError("The staged report changed before publication. Generate again.")
            # The existing folder publisher uses the same no-overwrite hard-link
            # primitive: the first visible target already contains complete bytes.
            os.link(staging, target)
            published = True
            result = ReportFilePublicationResult(target, staged_hash, True, archive)
            persist(result)
            committed = True
            return result
        except PermissionError as exc:
            raise ReportPublicationConflictError("Close the report in Word and check folder write access, then preview generation again.") from exc
        except FileExistsError as exc:
            raise ReportPublicationConflictError("The report destination changed. Preview generation again.") from exc
        finally:
            try:
                if not committed:
                    # Restore business files before attempting staging cleanup.
                    if published:
                        if (not target.is_file() or self.fingerprint(target) != expected_source_sha256
                                or _file_identity(target) != staging_identity):
                            raise ReportPublicationConflictError("The published report changed during rollback. The previous report is retained in History/Report; review both files before retrying.")
                        target.unlink()
                    if archive is not None and (
                        not archive.is_file() or _file_identity(archive) != archive_identity
                        or self.fingerprint(archive) != expected_current_sha256
                    ):
                        raise ReportPublicationConflictError("The recovery archive changed. Retain History/Report for manual review before retrying.")
                    if old_removed and archive is not None and current is not None:
                        if current.exists():
                            raise ReportPublicationConflictError("The old report location changed during rollback. Restore the retained History/Report copy after review.")
                        os.replace(archive, current)
                        archive = None
                    if archive is not None:
                        archive.unlink()
                    for directory in missing_parents:
                        if directory.is_dir() and not any(directory.iterdir()):
                            directory.rmdir()
            finally:
                if staging.exists():
                    if _file_identity(staging) != staging_identity:
                        raise ReportPublicationConflictError("Publication staging identity changed. Retain the temporary file and History/Report for review before retrying.")
                    staging.unlink()

    def publish_update(
        self,
        *,
        current_path: Path,
        expected_current_sha256: str,
        history_root: Path,
        update_document: Callable[[Path, Path], Path],
        pre_publish: Callable[[], None] | None = None,
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

            archive_path = _reserve_archive_path(
                Path(history_root),
                current,
                self._clock(),
            )
            try:
                shutil.copy2(current, archive_path)
                if self.fingerprint(archive_path) != expected:
                    raise ReportPublicationConflictError(
                        "The current report changed while it was being archived. Preview the update again."
                    )
                if pre_publish:
                    pre_publish()
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
        pre_publish: Callable[[], None] | None = None,
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
                if pre_publish:
                    pre_publish()
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


def _file_identity(path: Path) -> tuple[int, int]:
    information = path.stat()
    if not information.st_ino:
        raise ReportPublicationConflictError("The report filesystem cannot prove file identity. Review the report location before retrying.")
    return information.st_dev, information.st_ino


def _is_customer_report_name(stem: str, normalized_dl: str) -> bool:
    normalized = " ".join(stem.split()).casefold()
    expected_prefix = f"{normalized_dl}-cr"
    if not normalized_dl or not (
        normalized == expected_prefix or normalized.startswith(f"{expected_prefix} ")
    ):
        return False
    return "report" in normalized and "test record" not in normalized


def _reserve_archive_path(
    history_root: Path,
    current: Path,
    timestamp: datetime,
) -> Path:
    root = Path(history_root)
    root.mkdir(parents=True, exist_ok=True)
    stamp = timestamp.strftime("%Y%m%d-%H%M%S")
    identity_match = re.match(
        r"^(DL-\d{4}-\d{2}-\d{3}(?:-CR)?)\b",
        current.stem,
        flags=re.IGNORECASE,
    )
    revision_match = re.search(
        r"Report(?:_Customer)?_Rev_([A-Za-z0-9]+)$",
        current.stem,
        flags=re.IGNORECASE,
    )
    if identity_match and revision_match:
        archive_stem = (
            f"{identity_match.group(1)} Report_Rev_{revision_match.group(1)} {stamp}"
        )
    else:
        archive_stem = f"{current.stem} {stamp}"

    for suffix in range(1, 10_000):
        duplicate_suffix = "" if suffix == 1 else f" ({suffix})"
        candidate = root / f"{archive_stem}{duplicate_suffix}{current.suffix}"
        try:
            descriptor = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue
        os.close(descriptor)
        return candidate
    raise RuntimeError("Unable to reserve a report History file.")


def _missing_parents(path: Path) -> tuple[Path, ...]:
    missing: list[Path] = []
    current = Path(path)
    while not current.exists() and current != current.parent:
        missing.append(current)
        current = current.parent
    return tuple(missing)
