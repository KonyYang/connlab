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


def test_schedule_rejects_nonexistent_project_without_persisting_revision():
    service, repository = _service()
    with pytest.raises(LookupError, match="missing-project"):
        service.get_workspace("missing-project")
    with pytest.raises(LookupError, match="missing-project"):
        service.confirm(_command(project_id="missing-project"))
    assert repository.active_revision("missing-project") is None


def test_confirmed_schedule_remains_authoritative_after_upstream_changes() -> None:
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

    original = reader.get_latest_confirmed("P1")
    assert original is not None
    matrix.day_expression = "4"
    basic.received_date = "2026-10-01"

    assert reader.get_latest_confirmed("P1") == original
    assert service.get_workspace("P1").status == "confirmed"
    matrix.available = basic.available = False
    assert reader.get_latest_confirmed("P1") == original
    assert service.get_workspace("P1").status == "confirmed"


@pytest.mark.parametrize("basic_available,matrix_available", [(False, False), (True, False), (False, True)])
def test_schedule_can_be_confirmed_without_upstream_confirmation(basic_available, matrix_available):
    basic, matrix, repository = _BasicInformationReader(), _MatrixStore(), _Repository()
    basic.available, matrix.available = basic_available, matrix_available
    service = ProjectScheduleService(repository=repository, basic_information_reader=basic,
        confirmed_matrix_store=matrix, clock=lambda: "2026-09-08T00:00:00Z")
    assert service.get_workspace("P1").status == "not_started"
    revision = service.confirm(_command())
    assert revision.based_on_basic_information_version == (4 if basic_available else None)
    assert revision.based_on_confirmed_matrix_id == ("matrix-2" if matrix_available else None)
    assert revision.based_on_confirmed_matrix_revision == (2 if matrix_available else None)
    assert revision.sample_received_date == ("2026-09-01" if basic_available else "")
    assert ProjectScheduleOutputReader(repository, basic, matrix).get_latest_confirmed("P1").revision_id == revision.revision_id


def test_schedule_dates_do_not_depend_on_sample_received_or_matrix_duration():
    service, _ = _service()
    revision = service.confirm(_command(test_start_date="2026-08-01", test_complete_date="2026-08-01",
        estimated_completion_date="2026-08-03"))
    assert revision.test_start_date == "2026-08-01"


def test_schedule_retains_legacy_output_fallback_only_before_independent_confirmation():
    repository, basic, matrix = _Repository(), _BasicInformationReader(), _MatrixStore()
    reader = ProjectScheduleOutputReader(repository, basic, matrix)
    assert reader.get_latest_confirmed("P1").revision_id == "legacy:matrix-2"
    service = ProjectScheduleService(repository=repository, basic_information_reader=basic,
        confirmed_matrix_store=matrix, clock=lambda: "2026-09-08T00:00:00Z")
    revision = service.confirm(_command())
    assert reader.get_latest_confirmed("P1").revision_id == revision.revision_id


def test_confirmed_basic_without_received_date_does_not_block_schedule():
    basic, matrix, repository = _BasicInformationReader(), _MatrixStore(), _Repository()
    basic.received_date = ""
    service = ProjectScheduleService(repository=repository, basic_information_reader=basic,
        confirmed_matrix_store=matrix, clock=lambda: "2026-09-08T00:00:00Z")
    revision = service.confirm(_command())
    assert revision.sample_received_date == ""
    assert revision.based_on_basic_information_version == 4


def test_invalid_legacy_matrix_day_hint_does_not_block_independent_schedule(caplog):
    basic, matrix, repository = _BasicInformationReader(), _MatrixStore(), _Repository()
    matrix.day_expression = "legacy note"
    service = ProjectScheduleService(repository=repository, basic_information_reader=basic,
        confirmed_matrix_store=matrix, clock=lambda: "2026-09-08T00:00:00Z")
    revision = service.confirm(_command())
    assert revision.based_on_confirmed_matrix_id == "matrix-2"
    assert service.get_workspace("P1").status == "confirmed"
    assert "matrix-2" in caplog.text


@pytest.mark.parametrize("changes", [
    {"test_start_date": ""}, {"test_complete_date": " "}, {"estimated_completion_date": ""},
    {"test_start_date": "20260902"}, {"test_start_date": "2026-W36-3"},
    {"test_start_date": "2026-02-30"}, {"test_complete_date": "2026-09-01"},
    {"estimated_completion_date": "2026-09-06"}, {"post_test_buffer_days": "-1"},
    {"post_test_buffer_days": "NaN"}, {"post_test_buffer_days": "2x"},
    {"post_test_buffer_days": "2.1"}, {"post_test_buffer_days": "9" * 60},
])
def test_schedule_requires_valid_own_dates_and_post_buffer(changes):
    service, repository = _service()
    with pytest.raises(ValueError):
        service.confirm(_command(**changes))
    assert repository.active_revision("P1") is None


def _command(**changes):
    return replace(ConfirmProjectScheduleCommand(project_id="P1", expected_revision_id=None,
        expected_fingerprint=None, post_test_buffer_days="2", test_start_date="2026-09-02",
        test_complete_date="2026-09-05", estimated_completion_date="2026-09-07", confirmed_by="Lab User"), **changes)


class _Repository:
    def __init__(self) -> None:
        self.rows = []

    def project_exists(self, project_id):
        return project_id == "P1"

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
    available = True
    received_date = "2026-09-01"

    def get_latest_confirmed(self, project_id):
        if not self.available:
            return None
        return ConfirmedBasicInformationSnapshot(
            project_id=project_id,
            version=4,
            values={"date_lab_received_samples": self.received_date},
            source_signature="basic-signature",
            confirmed_at="2026-09-01T08:00:00ZZ",
            confirmed_by="Lab User",
        )


class _MatrixStore:
    available = True
    def __init__(self) -> None:
        self.day_expression = "3"

    def get_active_by_project(self, project_id):
        if not self.available:
            return None
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
