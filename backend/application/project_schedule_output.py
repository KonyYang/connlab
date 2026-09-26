"""Formal-output projection of Matrix dates and Basic Information sample receipt."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from backend.application.matrix_schedule_planning import (
    MatrixScheduleValidationError,
    parse_buffer_days,
    validate_matrix_authority_schedule,
)


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
    """Read Matrix-owned dates, guarding unmigrated historical schedule revisions."""

    def __init__(self, repository, basic_information_reader, confirmed_matrix_store) -> None:
        self._repository = repository
        self._basic_information = basic_information_reader
        self._confirmed_matrix = confirmed_matrix_store

    def get_latest_confirmed(
        self, project_id: str
    ) -> ConfirmedProjectScheduleSnapshot | None:
        matrix = self._confirmed_matrix.get_active_by_project(project_id)
        if matrix is None:
            return None
        version = matrix.version
        start = (version.planned_test_start_date or "").strip()
        complete = (version.planned_test_complete_date or "").strip()
        estimated = (version.estimated_completion_date or "").strip()
        post_buffer = (version.post_test_buffer_days or "").strip()
        try:
            validate_matrix_authority_schedule(
                post_test_buffer_days=post_buffer,
                planned_test_start_date=start,
                planned_test_complete_date=complete,
                estimated_completion_date=estimated,
            )
        except MatrixScheduleValidationError:
            return None
        active = self._repository.active_revision(project_id)
        if active is not None:
            try:
                old_buffer = parse_buffer_days(
                    active.post_test_buffer_days, value_name="Post-test buffer days"
                )
                matrix_buffer = parse_buffer_days(
                    post_buffer, value_name="Post-test buffer days"
                )
            except MatrixScheduleValidationError:
                return None
            if (
                old_buffer,
                active.test_start_date.strip(),
                active.test_complete_date.strip(),
                active.estimated_completion_date.strip(),
            ) != (matrix_buffer, start, complete, estimated):
                return None
        basic = self._basic_information.get_latest_confirmed(project_id)
        received = (
            (basic.values.get("date_lab_received_samples") or "").strip()
            if basic is not None else ""
        )
        if not received:
            return None
        return ConfirmedProjectScheduleSnapshot(
            project_id=project_id,
            revision_id=f"legacy:{version.confirmed_matrix_id}",
            revision_sequence=0,
            sample_received_date=received,
            post_test_buffer_days=post_buffer,
            test_start_date=start,
            test_complete_date=complete,
            estimated_completion_date=estimated,
            context_signature=(
                f"schedule:legacy-matrix:{version.confirmed_matrix_id}"
                f"@{version.confirmed_revision}:basic-received:"
                f"{sha256(received.encode('utf-8')).hexdigest()}"
            ),
        )
