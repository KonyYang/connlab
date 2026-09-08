"""Independent Project Schedule confirmation and read interface."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Protocol
from uuid import uuid4

from backend.application.matrix_schedule_planning import (
    MatrixScheduleFields,
    calculate_group_test_days,
    validate_planned_schedule,
)
from backend.domain.project_schedule_models import (
    ProjectScheduleRevision,
    ProjectScheduleSuggestion,
    ProjectScheduleWorkspace,
)


class ProjectScheduleError(ValueError):
    """Base Project Schedule command error."""


class ProjectScheduleReadinessError(ProjectScheduleError):
    """Required confirmed authority is unavailable."""


class ProjectScheduleConflictError(ProjectScheduleError):
    """The caller edited an obsolete schedule revision."""


@dataclass(frozen=True, slots=True)
class ConfirmProjectScheduleCommand:
    project_id: str
    expected_revision_id: str | None
    expected_fingerprint: str | None
    post_test_buffer_days: str
    test_start_date: str
    test_complete_date: str
    estimated_completion_date: str
    confirmed_by: str


class ProjectScheduleRepository(Protocol):
    def active_revision(self, project_id: str) -> ProjectScheduleRevision | None: ...
    def highest_revision_sequence(self, project_id: str) -> int: ...
    def add(self, revision: ProjectScheduleRevision) -> None: ...
    def supersede_active(self, project_id: str, *, at: str) -> None: ...
    def flush(self) -> None: ...
    def transaction(self): ...


class ProjectScheduleService:
    """Own Project Schedule lifecycle behind one read/confirm interface."""

    def __init__(
        self,
        *,
        repository: ProjectScheduleRepository,
        basic_information_reader,
        confirmed_matrix_store,
        clock,
        id_factory=lambda: uuid4().hex,
    ) -> None:
        self._repository = repository
        self._basic_information = basic_information_reader
        self._confirmed_matrix = confirmed_matrix_store
        self._clock = clock
        self._ids = id_factory

    def get_workspace(self, project_id: str) -> ProjectScheduleWorkspace:
        basic, matrix = self._sources(project_id)
        received = _required_received_date(basic.values)
        active = self._repository.active_revision(project_id)
        group_days = calculate_schedule_group_days(matrix)
        critical_group_id, critical_days = _critical_group(group_days)
        input_fingerprint = schedule_matrix_input_fingerprint(group_days)
        if active is not None:
            suggestion = _suggestion_from_revision(active)
            status = (
                "confirmed"
                if active.sample_received_date == received
                and active.matrix_input_fingerprint == input_fingerprint
                else "stale_inputs"
            )
        else:
            suggestion = _legacy_suggestion(matrix.version, basic.values)
            status = "not_started"
        return ProjectScheduleWorkspace(
            status=status,
            project_id=project_id,
            sample_received_date=received,
            critical_group_id=critical_group_id,
            critical_group_days=_decimal_text(critical_days),
            suggestion=suggestion,
            confirmed_revision=active,
        )

    def confirm(self, command: ConfirmProjectScheduleCommand) -> ProjectScheduleRevision:
        basic, matrix = self._sources(command.project_id)
        received = _required_received_date(basic.values)
        group_days = calculate_schedule_group_days(matrix)
        validate_planned_schedule(
            fields=MatrixScheduleFields(
                post_test_buffer_days=command.post_test_buffer_days,
                sample_received_date=received,
                planned_test_start_date=command.test_start_date,
                planned_test_complete_date=command.test_complete_date,
                estimated_completion_date=command.estimated_completion_date,
            ),
            group_test_days=group_days,
        )
        with self._repository.transaction():
            active = self._repository.active_revision(command.project_id)
            _assert_expected(active, command)
            now = self._clock()
            matrix_fingerprint = schedule_matrix_input_fingerprint(group_days)
            fingerprint = _schedule_fingerprint(
                project_id=command.project_id,
                matrix_input_fingerprint=matrix_fingerprint,
                received=received,
                post_buffer=command.post_test_buffer_days,
                start=command.test_start_date,
                complete=command.test_complete_date,
                estimated=command.estimated_completion_date,
            )
            if active is not None and active.fingerprint == fingerprint:
                return active
            if active is not None:
                active.state = "superseded"
                active.superseded_at = now
                active.superseded_reason = "Superseded by confirmed Project Schedule revision."
                self._repository.supersede_active(command.project_id, at=now)
            revision = ProjectScheduleRevision(
                revision_id=f"psr-{self._ids()}",
                project_id=command.project_id,
                revision_sequence=self._repository.highest_revision_sequence(command.project_id) + 1,
                state="confirmed",
                fingerprint=fingerprint,
                matrix_input_fingerprint=matrix_fingerprint,
                based_on_confirmed_matrix_id=matrix.version.confirmed_matrix_id,
                based_on_confirmed_matrix_revision=matrix.version.confirmed_revision,
                based_on_basic_information_version=basic.version,
                sample_received_date=received,
                post_test_buffer_days=command.post_test_buffer_days.strip(),
                test_start_date=command.test_start_date.strip(),
                test_complete_date=command.test_complete_date.strip(),
                estimated_completion_date=command.estimated_completion_date.strip(),
                confirmed_by=command.confirmed_by.strip(),
                confirmed_at=now,
            )
            self._repository.add(revision)
            self._repository.flush()
            return revision

    def _sources(self, project_id: str):
        basic = self._basic_information.get_latest_confirmed(project_id)
        if basic is None:
            raise ProjectScheduleReadinessError(
                "Confirm Basic Information before confirming Project Schedule."
            )
        matrix = self._confirmed_matrix.get_active_by_project(project_id)
        if matrix is None:
            raise ProjectScheduleReadinessError(
                "Confirm Matrix before confirming Project Schedule."
            )
        return basic, matrix


def _assert_expected(active, command: ConfirmProjectScheduleCommand) -> None:
    actual = (active.revision_id, active.fingerprint) if active is not None else (None, None)
    expected = (command.expected_revision_id, command.expected_fingerprint)
    if actual != expected:
        raise ProjectScheduleConflictError(
            "Project Schedule changed. Refresh the latest confirmed schedule."
        )


def calculate_schedule_group_days(matrix):
    return calculate_group_test_days(
        rows=(
            {"row_id": row.confirmed_row_id, "day_expression": row.day_expression}
            for row in matrix.rows
        ),
        cells=(
            {
                "row_id": cell.confirmed_row_id,
                "group_id": cell.confirmed_group_id,
                "cell_value": cell.cell_value,
            }
            for cell in matrix.cells
        ),
        selected_group_ids=(group.confirmed_group_id for group in matrix.groups),
    )


def _critical_group(group_days):
    if not group_days:
        return None, 0
    return max(group_days.items(), key=lambda item: (item[1], item[0]))


def schedule_matrix_input_fingerprint(group_days) -> str:
    payload = {key: _decimal_text(value) for key, value in sorted(group_days.items())}
    return sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _schedule_fingerprint(**values: str) -> str:
    return sha256(json.dumps(values, sort_keys=True).encode("utf-8")).hexdigest()


def _required_received_date(values: dict[str, str]) -> str:
    value = (values.get("date_lab_received_samples") or "").strip()
    if not value:
        raise ProjectScheduleReadinessError(
            "Confirmed Basic Information requires Date Lab Received Samples."
        )
    return value


def _legacy_suggestion(version, basic_values: dict[str, str]) -> ProjectScheduleSuggestion:
    return ProjectScheduleSuggestion(
        post_test_buffer_days=(version.post_test_buffer_days or "").strip(),
        test_start_date=(version.planned_test_start_date or "").strip(),
        test_complete_date=(version.planned_test_complete_date or "").strip(),
        estimated_completion_date=(
            version.estimated_completion_date
            or basic_values.get("estimated_completion_date")
            or ""
        ).strip(),
    )


def _suggestion_from_revision(revision: ProjectScheduleRevision) -> ProjectScheduleSuggestion:
    return ProjectScheduleSuggestion(
        post_test_buffer_days=revision.post_test_buffer_days,
        test_start_date=revision.test_start_date,
        test_complete_date=revision.test_complete_date,
        estimated_completion_date=revision.estimated_completion_date,
    )


def _decimal_text(value) -> str:
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text
