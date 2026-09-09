"""Confirmed Project Schedule read boundary for formal output consumers."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ConfirmedProjectScheduleSnapshot:
    project_id: str
    revision_id: str
    revision_sequence: int
    sample_received_date: str
    post_test_buffer_days: str
    test_start_date: str
    test_complete_date: str
    estimated_completion_date: str
    context_signature: str


class ConfirmedProjectScheduleReader(Protocol):
    def get_latest_confirmed(
        self, project_id: str
    ) -> ConfirmedProjectScheduleSnapshot | None: ...


class ProjectScheduleOutputReader:
    """Read independent schedule authority, with a legacy Matrix transition fallback."""

    def __init__(self, repository, basic_information_reader, confirmed_matrix_store) -> None:
        self._repository = repository
        self._basic_information = basic_information_reader
        self._confirmed_matrix = confirmed_matrix_store

    def get_latest_confirmed(
        self, project_id: str
    ) -> ConfirmedProjectScheduleSnapshot | None:
        active = self._repository.active_revision(project_id)
        if active is not None:
            return ConfirmedProjectScheduleSnapshot(
                project_id=active.project_id,
                revision_id=active.revision_id,
                revision_sequence=active.revision_sequence,
                sample_received_date=active.sample_received_date,
                post_test_buffer_days=active.post_test_buffer_days,
                test_start_date=active.test_start_date,
                test_complete_date=active.test_complete_date,
                estimated_completion_date=active.estimated_completion_date,
                context_signature=f"schedule:{active.revision_id}@{active.fingerprint}",
            )
        basic = self._basic_information.get_latest_confirmed(project_id)
        matrix = self._confirmed_matrix.get_active_by_project(project_id)
        if basic is None or matrix is None:
            return None
        version = matrix.version
        start = (version.planned_test_start_date or "").strip()
        complete = (version.planned_test_complete_date or "").strip()
        estimated = (version.estimated_completion_date or "").strip()
        received = (basic.values.get("date_lab_received_samples") or "").strip()
        if not all((received, start, complete, estimated)):
            return None
        return ConfirmedProjectScheduleSnapshot(
            project_id=project_id,
            revision_id=f"legacy:{version.confirmed_matrix_id}",
            revision_sequence=0,
            sample_received_date=received,
            post_test_buffer_days=(version.post_test_buffer_days or "").strip(),
            test_start_date=start,
            test_complete_date=complete,
            estimated_completion_date=estimated,
            context_signature=(
                f"schedule:legacy-matrix:{version.confirmed_matrix_id}"
                f"@{version.confirmed_revision}:basic-received:"
                f"{sha256(received.encode('utf-8')).hexdigest()}"
            ),
        )
