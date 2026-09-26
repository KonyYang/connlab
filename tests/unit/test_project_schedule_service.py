"""Historical Project Schedule data stays readable during Matrix authority migration."""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from backend.application.project_basic_information_output import ConfirmedBasicInformationSnapshot
from backend.application.project_schedule_output import ProjectScheduleOutputReader
from backend.application.project_schedule_service import ProjectScheduleConflictError, ProjectScheduleService
from backend.domain.project_schedule_models import ProjectScheduleRevision


def test_workspace_shows_basic_receipt_and_matrix_plan_when_no_legacy_revision() -> None:
    service, _ = _service()
    workspace = service.get_workspace("P1")
    assert workspace.status == "not_started"
    assert workspace.sample_received_date == "2026-09-01"
    assert workspace.suggestion.test_start_date == "2026-09-02"
    assert workspace.suggestion.test_complete_date == "2026-09-05"
    assert workspace.suggestion.estimated_completion_date == "2026-09-07"
    assert workspace.critical_group_days == "3"


def test_workspace_exposes_old_revision_for_matrix_editor_prefill() -> None:
    service, repository = _service()
    repository.add(_legacy(start="2026-09-03", complete="2026-09-06", estimated="2026-09-08"))
    workspace = service.get_workspace("P1")
    assert workspace.status == "confirmed"
    assert workspace.confirmed_revision is not None
    assert workspace.suggestion.test_start_date == "2026-09-03"


def test_formal_output_uses_matrix_dates_and_basic_receipt_only() -> None:
    repository, basic, matrix = _Repository(), _BasicInformationReader(), _MatrixStore()
    repository.add(_legacy())
    reader = ProjectScheduleOutputReader(repository, basic, matrix)
    snapshot = reader.get_latest_confirmed("P1")
    assert snapshot is not None
    assert snapshot.test_start_date == "2026-09-02"
    assert snapshot.revision_id == "legacy:matrix-2"
    basic.received_date = "2026-09-03"
    assert reader.get_latest_confirmed("P1").sample_received_date == "2026-09-03"


def test_formal_output_blocks_unmigrated_historical_dates() -> None:
    repository, basic, matrix = _Repository(), _BasicInformationReader(), _MatrixStore()
    repository.add(_legacy(start="2026-09-03", complete="2026-09-06", estimated="2026-09-08"))
    assert ProjectScheduleOutputReader(repository, basic, matrix).get_latest_confirmed("P1") is None


@pytest.mark.parametrize("old_buffer,matrix_buffer", [
    ("2.0", "2"), ("0", ""), ("0", None),
])
def test_formal_output_accepts_equivalent_legacy_and_matrix_buffer_days(
    old_buffer: str, matrix_buffer: str | None,
) -> None:
    repository, basic, matrix = (
        _Repository(), _BasicInformationReader(), _MatrixStore(matrix_buffer)
    )
    repository.add(_legacy(post_buffer=old_buffer))

    snapshot = ProjectScheduleOutputReader(repository, basic, matrix).get_latest_confirmed("P1")

    assert snapshot is not None
    assert snapshot.test_start_date == "2026-09-02"


def test_formal_output_requires_basic_receipt_without_blocking_matrix_authority() -> None:
    repository, basic, matrix = _Repository(), _BasicInformationReader(), _MatrixStore()
    basic.available = False
    reader = ProjectScheduleOutputReader(repository, basic, matrix)
    assert reader.get_latest_confirmed("P1") is None
    basic.available = True
    basic.received_date = ""
    assert reader.get_latest_confirmed("P1") is None
    basic.received_date = "2026-09-01"
    assert reader.get_latest_confirmed("P1") is not None
    matrix.start_date = ""
    assert reader.get_latest_confirmed("P1") is None


def test_legacy_retirement_requires_matching_identity_and_preserves_history() -> None:
    service, repository = _service()
    revision = _legacy()
    repository.add(revision)
    with pytest.raises(ProjectScheduleConflictError):
        service.verify_legacy_revision("P1", expected_revision_id=None, expected_fingerprint=None)
    service.verify_legacy_revision(
        "P1", expected_revision_id=revision.revision_id,
        expected_fingerprint=revision.fingerprint,
    )
    service.retire_legacy_revision(
        "P1", expected_revision_id=revision.revision_id,
        expected_fingerprint=revision.fingerprint,
        matrix_publish_status="no_change",
    )
    assert repository.active_revision("P1") is None
    assert repository.rows[0].state == "superseded"
    assert repository.rows[0].revision_id == revision.revision_id


def test_unchanged_matrix_cannot_retire_different_legacy_schedule_dates() -> None:
    service, repository = _service()
    revision = _legacy(start="2026-09-03")
    repository.add(revision)

    with pytest.raises(ProjectScheduleConflictError, match="differ from Matrix"):
        service.retire_legacy_revision(
            "P1",
            expected_revision_id=revision.revision_id,
            expected_fingerprint=revision.fingerprint,
            matrix_publish_status="no_change",
        )

    assert repository.active_revision("P1") is revision


@pytest.mark.parametrize("old_buffer,matrix_buffer", [
    ("2.0", "2"), ("0", ""), ("0", None),
])
def test_unchanged_matrix_retires_legacy_schedule_with_equivalent_buffer_days(
    old_buffer: str, matrix_buffer: str | None,
) -> None:
    service, repository = _service(matrix_buffer=matrix_buffer)
    revision = _legacy(post_buffer=old_buffer)
    repository.add(revision)

    service.retire_legacy_revision(
        "P1",
        expected_revision_id=revision.revision_id,
        expected_fingerprint=revision.fingerprint,
        matrix_publish_status="no_change",
    )

    assert repository.active_revision("P1") is None


def _legacy(
    *, post_buffer: str = "2", start: str = "2026-09-02", complete: str = "2026-09-05",
    estimated: str = "2026-09-07",
) -> ProjectScheduleRevision:
    return ProjectScheduleRevision(
        revision_id="psr-historical-1", project_id="P1", revision_sequence=1,
        state="confirmed", fingerprint="historical-fingerprint",
        matrix_input_fingerprint="historical-matrix", based_on_confirmed_matrix_id="matrix-2",
        based_on_confirmed_matrix_revision=2, based_on_basic_information_version=4,
        sample_received_date="2026-08-31", post_test_buffer_days=post_buffer,
        test_start_date=start, test_complete_date=complete,
        estimated_completion_date=estimated, confirmed_by="historical operator",
        confirmed_at="2026-09-01T00:00:00+00:00",
    )


class _Repository:
    def __init__(self) -> None:
        self.rows: list[ProjectScheduleRevision] = []

    def project_exists(self, project_id: str) -> bool:
        return project_id == "P1"

    def active_revision(self, project_id: str) -> ProjectScheduleRevision | None:
        return next((row for row in reversed(self.rows)
                     if row.project_id == project_id and row.state == "confirmed"), None)

    def add(self, revision: ProjectScheduleRevision) -> None:
        self.rows.append(revision)

    def supersede_active(self, project_id: str, *, at: str) -> None:
        active = self.active_revision(project_id)
        if active is not None:
            active.state = "superseded"
            active.superseded_at = at

    def flush(self) -> None:
        pass

    @contextmanager
    def transaction(self):
        yield


class _BasicInformationReader:
    def __init__(self) -> None:
        self.available = True
        self.received_date = "2026-09-01"

    def get_latest_confirmed(self, project_id: str):
        if not self.available:
            return None
        return ConfirmedBasicInformationSnapshot(
            project_id=project_id, version=4,
            values={"date_lab_received_samples": self.received_date},
            source_signature="basic-signature", confirmed_at="2026-09-01T08:00:00Z",
            confirmed_by="Lab User",
        )


class _MatrixStore:
    def __init__(self, post_buffer_days: str | None = "2") -> None:
        self.available = True
        self.start_date = "2026-09-02"
        self.post_buffer_days = post_buffer_days

    def get_active_by_project(self, project_id: str):
        if not self.available:
            return None
        version = SimpleNamespace(
            confirmed_matrix_id="matrix-2", confirmed_revision=2,
            post_test_buffer_days=self.post_buffer_days, planned_test_start_date=self.start_date,
            planned_test_complete_date="2026-09-05",
            estimated_completion_date="2026-09-07",
        )
        groups = (SimpleNamespace(confirmed_group_id="g1"),)
        rows = (SimpleNamespace(confirmed_row_id="r1", day_expression="3"),)
        cells = (SimpleNamespace(confirmed_row_id="r1", confirmed_group_id="g1", cell_value="1"),)
        return SimpleNamespace(version=version, groups=groups, rows=rows, cells=cells)


def _service(*, matrix_buffer: str | None = "2"):
    repository = _Repository()
    service = ProjectScheduleService(
        repository=repository, basic_information_reader=_BasicInformationReader(),
        confirmed_matrix_store=_MatrixStore(matrix_buffer), clock=lambda: "2026-09-08T00:00:00Z",
    )
    return service, repository
