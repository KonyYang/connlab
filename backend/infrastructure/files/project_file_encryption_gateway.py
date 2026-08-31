"""Recoverable filesystem transaction for one encrypted project file."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Protocol

from backend.application.project_file_encryption_service import ProjectFileEncryptionPlanItem


class OfficeFilePasswordGatewayPort(Protocol):
    """Office-format encryption operation required by the file transaction."""

    def encrypt_and_verify(
        self,
        *,
        source_path: Path,
        output_path: Path,
        password: str,
        office_kind: str,
    ) -> None:
        """Write and verify one password-protected Office file."""


class ProjectFileEncryptionConflictError(RuntimeError):
    """Raised when a secured target appeared without overwrite authority."""


class ProjectFileEncryptionRollbackError(RuntimeError):
    """Raised when the primary error is accompanied by a rollback failure."""


class LocalProjectFileEncryptionGateway:
    """Stage, verify, and commit one encryption mutation on the same volume."""

    def __init__(self, protector: OfficeFilePasswordGatewayPort) -> None:
        self._protector = protector

    def encrypt(
        self,
        *,
        item: ProjectFileEncryptionPlanItem,
        password: str,
        history_root: Path,
        overwrite: bool,
    ) -> Path:
        """Apply one item without exposing a partially written final file."""
        source = item.source_path
        target = item.target_path
        if not source.is_file():
            raise FileNotFoundError(f"Source file is no longer available: {source.name}")
        if item.mode == "secured_copy" and target.exists() and not overwrite:
            raise ProjectFileEncryptionConflictError(
                f"Secured target already exists: {target.name}"
            )
        stage = source.parent / f".connlab-encryption-{uuid.uuid4().hex}{source.suffix}"
        try:
            self._protector.encrypt_and_verify(
                source_path=source,
                output_path=stage,
                password=password,
                office_kind=item.office_kind,
            )
            if not stage.is_file() or stage.stat().st_size <= 0:
                raise RuntimeError("Office did not produce a verified encrypted file.")
            if item.mode == "replace_in_place":
                os.replace(stage, source)
                return source
            return self._commit_secured_copy(
                source=source,
                target=target,
                stage=stage,
                history_root=history_root,
                overwrite=overwrite,
            )
        finally:
            if stage.exists():
                stage.unlink()

    def _commit_secured_copy(
        self,
        *,
        source: Path,
        target: Path,
        stage: Path,
        history_root: Path,
        overwrite: bool,
    ) -> Path:
        history_root.mkdir(parents=True, exist_ok=True)
        archived_source = history_root / source.name
        archived_target = history_root / target.name
        moved_source = False
        moved_target = False
        try:
            if target.exists():
                if not overwrite:
                    raise ProjectFileEncryptionConflictError(
                        f"Secured target already exists: {target.name}"
                    )
                if archived_target.exists():
                    raise FileExistsError(f"History target already exists: {target.name}")
                os.replace(target, archived_target)
                moved_target = True
            if archived_source.exists():
                raise FileExistsError(f"History source already exists: {source.name}")
            os.replace(source, archived_source)
            moved_source = True
            os.replace(stage, target)
            return target
        except Exception as primary_error:
            rollback_errors: list[Exception] = []
            if moved_source and archived_source.exists() and not source.exists():
                try:
                    os.replace(archived_source, source)
                except Exception as exc:  # pragma: no cover - host filesystem failure
                    rollback_errors.append(exc)
            if moved_target and archived_target.exists() and not target.exists():
                try:
                    os.replace(archived_target, target)
                except Exception as exc:  # pragma: no cover - host filesystem failure
                    rollback_errors.append(exc)
            if rollback_errors:
                raise ProjectFileEncryptionRollbackError(
                    "Encryption failed and one or more original files could not be restored."
                ) from primary_error
            raise

