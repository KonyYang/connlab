from contextlib import contextmanager
from dataclasses import replace
from types import SimpleNamespace

import pytest

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_schedule_service import (
    ConfirmProjectScheduleCommand,
    ProjectScheduleConflictError,
    ProjectScheduleService,
)
from backend.application.project_schedule_output import ProjectScheduleOutputReader


def test_workspace_seeds_received_date_from_basic_information_and_legacy_matrix_dates() -> None:
    service, _ = _service()

    workspace = service.get_workspace("P1")

    assert workspace.status == "not_started"
    assert workspace.sample_received_date == "2026-09-01"
    assert workspace.suggestion.post_test_buffer_days == "2"
    assert workspace.suggestion.test_start_date == "2026-09-02"
    assert workspace.suggestion.test_complete_date == "2026-09-05"
    assert workspace.suggestion.estimated_completion_date == "2026-09-07"
    assert workspace.critical_group_days == "3"


def test_confirm_creates_independent_schedule_and_supersedes_previous_revision() -> None:
    service, repository = _service()
    first = service.confirm(
        ConfirmProjectScheduleCommand(
            project_id="P1",
            expected_revision_id=None,
            expected_fingerprint=None,
            post_test_buffer_days="2",
            test_start_date="2026-09-02",
            test_complete_date="2026-09-05",
            estimated_completion_date="2026-09-07",
            confirmed_by="Lab User",
        )
    )
    second = service.confirm(
        ConfirmProjectScheduleCommand(
            project_id="P1",
            expected_revision_id=first.revision_id,
            expected_fingerprint=first.fingerprint,
            post_test_buffer_days="1",
            test_start_date="2026-09-03",
            test_complete_date="2026-09-06",
            estimated_completion_date="2026-09-07",
            confirmed_by="Lab User",
        )
    )

    assert first.state == "superseded"
    assert second.state == "confirmed"
    assert second.revision_sequence == 2
    assert second.sample_received_date == "2026-09-01"
    assert second.matrix_input_fingerprint
    assert repository.active_revision("P1") == second


def test_confirm_rejects_stale_schedule_identity() -> None:
    service, _ = _service()
    with pytest.raises(ProjectScheduleConflictError, match="changed"):
        service.confirm(
            ConfirmProjectScheduleCommand(
                project_id="P1",
                expected_revision_id="old",
                expected_fingerprint="old",
                post_test_buffer_days="2",
                test_start_date="2026-09-02",
                test_complete_date="2026-09-05",
                estimated_completion_date="2026-09-07",
                confirmed_by="Lab User",
            )
        )


def test_formal_output_rejects_schedule_after_matrix_duration_inputs_change() -> None:
    repository = _Repository()
    basic = _BasicInformationReader()
    matrix = _MatrixStore()
    service = ProjectScheduleService(
        repository=repository,
        basic_information_reader=basic,
        confirmed_matrix_store=matrix,
        clock=lambda: "2026-09-08T00:00:00Z",
        id_factory=lambda: "1",
    )
    service.confirm(
        ConfirmProjectScheduleCommand(
            project_id="P1",
            expected_revision_id=None,
            expected_fingerprint=None,
            post_test_buffer_days="2",
            test_start_date="2026-09-02",
            test_complete_date="2026-09-05",
            estimated_completion_date="2026-09-07",
            confirmed_by="Lab User",
        )
    )
    reader = ProjectScheduleOutputReader(repository, basic, matrix)

    assert reader.get_latest_confirmed("P1") is not None
    matrix.day_expression = "4"

    assert reader.get_latest_confirmed("P1") is None


class _Repository:
    def __init__(self) -> None:
        self.rows = []

    def active_revision(self, project_id):
        return next((row for row in reversed(self.rows) if row.project_id == project_id and row.state == "confirmed"), None)

    def highest_revision_sequence(self, project_id):
        return max((row.revision_sequence for row in self.rows if row.project_id == project_id), default=0)

    def add(self, revision):
        self.rows.append(revision)

    def supersede_active(self, project_id, *, at):
        active = self.active_revision(project_id)
        if active is not None:
            active.state = "superseded"
            active.superseded_at = at
            active.superseded_reason = "Superseded by confirmed Project Schedule revision."

    def flush(self):
        return None

    @contextmanager
    def transaction(self):
        yield


class _BasicInformationReader:
    def get_latest_confirmed(self, project_id):
        return ConfirmedBasicInformationSnapshot(
            project_id=project_id,
            version=4,
            values={"date_lab_received_samples": "2026-09-01"},
            source_signature="basic-signature",
            confirmed_at="2026-09-01T08:00:00ZZ",
            confirmed_by="Lab User",
        )


class _MatrixStore:
    def __init__(self) -> None:
        self.day_expression = "3"

    def get_active_by_project(self, project_id):
        version = SimpleNamespace(
            confirmed_matrix_id="matrix-2",
            confirmed_revision=2,
            post_test_buffer_days="2",
            planned_test_start_date="2026-09-02",
            planned_test_complete_date="2026-09-05",
            estimated_completion_date="2026-09-07",
        )
        groups = (SimpleNamespace(confirmed_group_id="g1"),)
        rows = (SimpleNamespace(confirmed_row_id="r1", day_expression=self.day_expression),)
        cells = (SimpleNamespace(confirmed_row_id="r1", confirmed_group_id="g1", cell_value="1"),)
        return SimpleNamespace(version=version, groups=groups, rows=rows, cells=cells)


def _service():
    repository = _Repository()
    service = ProjectScheduleService(
        repository=repository,
        basic_information_reader=_BasicInformationReader(),
        confirmed_matrix_store=_MatrixStore(),
        clock=lambda: "2026-09-08T00:00:00Z",
        id_factory=iter(("1", "2", "3")).__next__,
    )
    return service, repository
