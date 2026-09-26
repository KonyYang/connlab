"""Read and retire historical independent Project Schedule revisions."""

from __future__ import annotations

import logging
from typing import Protocol

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


class ProjectScheduleRepository(Protocol):
    def project_exists(self, project_id: str) -> bool: ...
    def active_revision(self, project_id: str) -> ProjectScheduleRevision | None: ...
    def supersede_active(self, project_id: str, *, at: str) -> None: ...
    def flush(self) -> None: ...
    def transaction(self): ...


class ProjectScheduleService:
    """Read historical schedules and retire their authority after Matrix migration."""

    def __init__(
        self,
        *,
        repository: ProjectScheduleRepository,
        basic_information_reader,
        confirmed_matrix_store,
        clock,
    ) -> None:
        self._repository = repository
        self._basic_information = basic_information_reader
        self._confirmed_matrix = confirmed_matrix_store
        self._clock = clock

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

    def verify_legacy_revision(
        self,
        project_id: str,
        *,
        expected_revision_id: str | None,
        expected_fingerprint: str | None,
    ) -> ProjectScheduleRevision | None:
        """Guard a Matrix confirmation against unseen historical schedule changes."""
        active = self._repository.active_revision(project_id)
        actual = (active.revision_id, active.fingerprint) if active is not None else (None, None)
        if actual != (expected_revision_id, expected_fingerprint):
            raise ProjectScheduleConflictError(
                "Project Schedule changed. Refresh Matrix Editor before confirming."
            )
        return active

    def retire_legacy_revision(
        self,
        project_id: str,
        *,
        expected_revision_id: str | None,
        expected_fingerprint: str | None,
        matrix_publish_status: str,
    ) -> None:
        """Retain historical data but remove its active authority after Matrix publish."""
        with self._repository.transaction():
            active = self.verify_legacy_revision(
                project_id,
                expected_revision_id=expected_revision_id,
                expected_fingerprint=expected_fingerprint,
            )
            if active is not None:
                if matrix_publish_status == "no_change":
                    matrix = self._confirmed_matrix.get_active_by_project(project_id)
                    if matrix is None or (
                        parse_buffer_days(active.post_test_buffer_days, value_name="Post-test buffer days"),
                        active.test_start_date.strip(),
                        active.test_complete_date.strip(),
                        active.estimated_completion_date.strip(),
                    ) != (
                        parse_buffer_days(matrix.version.post_test_buffer_days, value_name="Post-test buffer days"),
                        (matrix.version.planned_test_start_date or "").strip(),
                        (matrix.version.planned_test_complete_date or "").strip(),
                        (matrix.version.estimated_completion_date or "").strip(),
                    ):
                        raise ProjectScheduleConflictError(
                            "Legacy Project Schedule dates differ from Matrix. "
                            "Reload and confirm the migrated dates."
                        )
                self._repository.supersede_active(project_id, at=self._clock())
                self._repository.flush()

    def _require_project(self, project_id: str) -> None:
        if not self._repository.project_exists(project_id):
            raise ProjectScheduleProjectNotFoundError(f"Project {project_id} does not exist.")

    def _sources(self, project_id: str):
        basic = self._basic_information.get_latest_confirmed(project_id)
        matrix = self._confirmed_matrix.get_active_by_project(project_id)
        return basic, matrix


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
