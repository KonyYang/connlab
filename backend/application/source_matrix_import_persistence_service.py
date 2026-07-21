"""Application persistence boundary for Source Matrix import snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from typing import Any, Protocol

from backend.application.source_matrix_import_builder import (
    PreparedSourceMatrixImport,
    prepare_source_matrix_import,
)
from backend.domain import SourceMatrixImportRecord, SourceMatrixSnapshot


class SourceMatrixImportPersistenceError(ValueError):
    """Raised when source matrix snapshot persistence input is invalid."""


class SourceMatrixImportStore(Protocol):
    def create_import_snapshot(
        self,
        import_record: SourceMatrixImportRecord,
        snapshot: SourceMatrixSnapshot,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class PersistSourceMatrixImportCommand:
    project_id: str
    draft_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    source_asset_id: str | None
    source_case_id: str | None
    source_draft_id: str | None
    payload: dict[str, Any]
    created_at: str
    task261_commit_fingerprint: str | None = None


@dataclass(frozen=True, slots=True)
class PersistSourceMatrixFromPreviewCommand:
    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    payload: dict[str, Any]
    selected_group_keys: tuple[str, ...]
    created_at: str
    task261_commit_fingerprint: str | None = None


@dataclass(frozen=True, slots=True)
class SourceMatrixPersistResult:
    import_id: str
    snapshot_id: str


class SourceMatrixImportPersistenceService:
    """Prepare and persist immutable Source Matrix import aggregates."""

    def __init__(self, *, store: SourceMatrixImportStore) -> None:
        self._store = store

    def persist_from_draft(self, command: PersistSourceMatrixImportCommand) -> str:
        if not isinstance(command.payload, dict):
            raise SourceMatrixImportPersistenceError(
                "Source matrix payload must be an object."
            )
        prepared = prepare_source_matrix_import(
            project_id=command.project_id,
            draft_id=command.draft_id,
            source_document_path=command.source_document_path,
            source_document_name=command.source_document_name,
            source_format=command.source_format,
            source_asset_id=command.source_asset_id,
            source_case_id=command.source_case_id,
            source_draft_id=command.source_draft_id,
            payload=command.payload,
            created_at=command.created_at,
            selected_group_keys_override=None,
            task261_commit_fingerprint=command.task261_commit_fingerprint,
        )
        return self.persist_prepared(prepared).import_id

    def prepare_from_preview(
        self,
        command: PersistSourceMatrixFromPreviewCommand,
    ) -> PreparedSourceMatrixImport:
        """Build preview lineage without touching the repository."""
        if not command.selected_group_keys:
            raise SourceMatrixImportPersistenceError(
                "selected_group_keys is required for preview persistence."
            )
        return prepare_source_matrix_import(
            project_id=command.project_id,
            draft_id=None,
            source_document_path=command.source_document_path,
            source_document_name=command.source_document_name,
            source_format=command.source_format,
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            payload=command.payload,
            created_at=command.created_at,
            selected_group_keys_override=command.selected_group_keys,
            task261_commit_fingerprint=command.task261_commit_fingerprint,
        )

    def persist_prepared(
        self,
        prepared: PreparedSourceMatrixImport,
    ) -> SourceMatrixPersistResult:
        """Persist one previously validated source aggregate."""
        self._store.create_import_snapshot(prepared.import_record, prepared.snapshot)
        return SourceMatrixPersistResult(
            import_id=prepared.import_record.import_id,
            snapshot_id=prepared.snapshot.snapshot_id,
        )

    def persist_from_preview(
        self,
        command: PersistSourceMatrixFromPreviewCommand,
    ) -> SourceMatrixPersistResult:
        """Preserve the TASK_261 compatibility command."""
        return self.persist_prepared(self.prepare_from_preview(command))

    def compute_task261_fingerprint(
        self,
        *,
        payload: dict[str, Any],
        selected_group_keys: tuple[str, ...],
    ) -> str:
        canonical_payload = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        canonical_selected = json.dumps(
            list(selected_group_keys), ensure_ascii=False, separators=(",", ":")
        )
        return hashlib.sha256(
            f"{canonical_payload}|{canonical_selected}".encode("utf-8")
        ).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()
