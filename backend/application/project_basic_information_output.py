"""Project Basic Information snapshot types for formal output consumers."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
)


@dataclass(frozen=True, slots=True)
class ConfirmedBasicInformationSnapshot:
    """Confirmed Basic Information values used by formal outputs."""

    project_id: str
    version: int
    values: dict[str, str]
    source_signature: str
    confirmed_at: str | None
    confirmed_by: str | None

    @property
    def source_signature_hash(self) -> str:
        """Return a bounded signature token safe for output records."""
        return sha256(self.source_signature.encode("utf-8")).hexdigest()

    @property
    def context_signature(self) -> str:
        """Return the Basic Information portion of an output context."""
        return f"basic:{self.version}@{self.source_signature_hash}"


class ConfirmedBasicInformationReader(Protocol):
    """Read latest confirmed Basic Information for formal outputs."""

    def get_latest_confirmed(
        self, project_id: str
    ) -> ConfirmedBasicInformationSnapshot | None:
        """Return latest confirmed Basic Information, if available."""


class ProjectBasicInformationSnapshotReader:
    """Adapt the Basic Information repository to output snapshot reads."""

    def __init__(self, repository: object) -> None:
        """Create the reader from a repository with get_latest_confirmed."""
        self._repository = repository

    def get_latest_confirmed(
        self, project_id: str
    ) -> ConfirmedBasicInformationSnapshot | None:
        """Return the latest confirmed Basic Information snapshot."""
        record = self._repository.get_latest_confirmed(project_id)
        return snapshot_from_record(record) if record is not None else None


def snapshot_from_record(
    record: ProjectBasicInformationRecord,
) -> ConfirmedBasicInformationSnapshot:
    """Convert a persisted Basic Information record into an output snapshot."""
    return ConfirmedBasicInformationSnapshot(
        project_id=record.project_id,
        version=record.version,
        values=dict(record.values),
        source_signature=record.source_signature,
        confirmed_at=record.confirmed_at,
        confirmed_by=record.confirmed_by,
    )
