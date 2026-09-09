"""Independent Project Schedule confirmation and read interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
import logging
from typing import Protocol
from uuid import uuid4

from backend.application.matrix_schedule_planning import (
    MatrixScheduleValidationError,
    calculate_group_test_days,
    parse_buffer_days,
)
from backend.domain.project_schedule_models import (
    ProjectScheduleRevision,
    ProjectScheduleSuggestion,
    ProjectScheduleWorkspace,
)

logger = logging.getLogger(__name__)


class ProjectScheduleError(ValueError):
    """Base Project Schedule command error."""


class ProjectScheduleReadinessError(ProjectScheduleError):
    """Required confirmed authority is unavailable."""


class ProjectScheduleProjectNotFoundError(LookupError):
    """The requested Project does not exist."""


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
    def project_exists(self, project_id: str) -> bool: ...
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
        self._require_project(project_id)
        basic, matrix = self._sources(project_id)
        basic_values = basic.values if basic is not None else {}
        received = (basic_values.get("date_lab_received_samples") or "").strip()
        active = self._repository.active_revision(project_id)
        group_days = calculate_schedule_group_days(matrix)
        critical_group_id, critical_days = _critical_group(group_days)
        if active is not None:
            suggestion = _suggestion_from_revision(active)
            status = "confirmed"
        else:
            suggestion = _legacy_suggestion(matrix.version if matrix is not None else None, basic_values)
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
        basic_values = basic.values if basic is not None else {}
        received = (basic_values.get("date_lab_received_samples") or "").strip()
        group_days = calculate_schedule_group_days(matrix)
        _validate_schedule_dates(command)
        with self._repository.transaction():
            self._require_project(command.project_id)
            active = self._repository.active_revision(command.project_id)
            _assert_expected(active, command)
            now = self._clock()
            matrix_fingerprint = schedule_matrix_input_fingerprint(group_days)
            fingerprint = _schedule_fingerprint(
                project_id=command.project_id,
                post_buffer=command.post_test_buffer_days.strip(),
                start=command.test_start_date.strip(),
                complete=command.test_complete_date.strip(),
                estimated=command.estimated_completion_date.strip(),
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
                based_on_confirmed_matrix_id=matrix.version.confirmed_matrix_id if matrix is not None else None,
                based_on_confirmed_matrix_revision=matrix.version.confirmed_revision if matrix is not None else None,
                based_on_basic_information_version=basic.version if basic is not None else None,
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

    def _require_project(self, project_id: str) -> None:
        if not self._repository.project_exists(project_id):
            raise ProjectScheduleProjectNotFoundError(f"Project {project_id} does not exist.")

    def _sources(self, project_id: str):
        basic = self._basic_information.get_latest_confirmed(project_id)
        matrix = self._confirmed_matrix.get_active_by_project(project_id)
        return basic, matrix


def _assert_expected(active, command: ConfirmProjectScheduleCommand) -> None:
    actual = (active.revision_id, active.fingerprint) if active is not None else (None, None)
    expected = (command.expected_revision_id, command.expected_fingerprint)
    if actual != expected:
        raise ProjectScheduleConflictError(
            "Project Schedule changed. Refresh the latest confirmed schedule."
        )


def calculate_schedule_group_days(matrix):
    if matrix is None:
        return {}
    try:
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
    except MatrixScheduleValidationError as exc:
        # Historical duration hints do not govern independent schedule confirmation.
        logger.warning(
            "Schedule duration hint unavailable for Matrix %s: %s",
            matrix.version.confirmed_matrix_id,
            exc,
        )
        return {}


def _critical_group(group_days):
    if not group_days:
        return None, 0
    return max(group_days.items(), key=lambda item: (item[1], item[0]))


def schedule_matrix_input_fingerprint(group_days) -> str:
    payload = {key: _decimal_text(value) for key, value in sorted(group_days.items())}
    return sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _schedule_fingerprint(**values: str) -> str:
    return sha256(json.dumps(values, sort_keys=True).encode("utf-8")).hexdigest()


def _validate_schedule_dates(command: ConfirmProjectScheduleCommand) -> None:
    dates = []
    for name in ("test_start_date", "test_complete_date", "estimated_completion_date"):
        value = getattr(command, name).strip()
        if not value:
            raise ProjectScheduleError(f"{name} is required.")
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ProjectScheduleError(f"{name} must use YYYY-MM-DD format.") from exc
        if parsed.isoformat() != value:
            raise ProjectScheduleError(f"{name} must use YYYY-MM-DD format.")
        dates.append(parsed)
    start, complete, estimated = dates
    if complete < start:
        raise ProjectScheduleError("test_complete_date is earlier than test_start_date.")
    post_days = parse_buffer_days(command.post_test_buffer_days, value_name="Post-test buffer days")
    # Comparing the available interval also avoids overflow for very large buffers.
    if Decimal((estimated - complete).days) < post_days:
        raise ProjectScheduleError(
            "estimated_completion_date is earlier than test_complete_date plus post-test buffer days."
        )


def _legacy_suggestion(version, basic_values: dict[str, str]) -> ProjectScheduleSuggestion:
    return ProjectScheduleSuggestion(
        post_test_buffer_days=(getattr(version, "post_test_buffer_days", None) or "").strip(),
        test_start_date=(getattr(version, "planned_test_start_date", None) or "").strip(),
        test_complete_date=(getattr(version, "planned_test_complete_date", None) or "").strip(),
        estimated_completion_date=(
            getattr(version, "estimated_completion_date", None)
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
