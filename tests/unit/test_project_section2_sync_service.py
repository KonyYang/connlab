from __future__ import annotations

from dataclasses import replace

import pytest

from backend.application.project_section2_sync_service import (
    ProjectSection2SyncAmbiguousTargetError,
    ProjectSection2SyncCommand,
    ProjectSection2SyncConflictError,
    ProjectSection2SyncReadinessError,
    ProjectSection2SyncService,
    ProjectSection2SyncValidationError,
)
from backend.domain import (
    ApplicationForm,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
)


def test_preview_reports_will_change_for_valid_confirmed_matrix_dates() -> None:
    service, forms = _service(
        form=_form(received_date="2026-05-01", estimated_completion_date="2026-05-10"),
        snapshot=_snapshot(sample_received_date="2026-06-01", estimated_completion_date="2026-06-08"),
    )

    result = service.preview(ProjectSection2SyncCommand(project_id="P1"))

    assert result.status == "ready"
    assert result.application_form_id == "FORM1"
    assert result.confirmed_matrix_id == "CM1"
    assert result.confirmed_revision == 2
    assert [(field.field_key, field.status, field.next_value) for field in result.fields] == [
        ("received_date", "will_change", "2026-06-01"),
        ("estimated_completion_date", "will_change", "2026-06-08"),
    ]
    assert forms.updated == []


def test_sync_updates_structured_application_form_dates() -> None:
    service, forms = _service(
        form=_form(received_date="2026-05-01", estimated_completion_date="2026-05-10"),
        snapshot=_snapshot(sample_received_date="2026-06-01", estimated_completion_date="2026-06-08"),
    )

    result = service.sync(
        ProjectSection2SyncCommand(
            project_id="P1",
            expected_confirmed_matrix_id="CM1",
            expected_confirmed_revision=2,
            operator="MP Cao",
        )
    )

    assert result.status == "synced"
    assert [(field.field_key, field.status, field.next_value) for field in result.fields] == [
        ("received_date", "changed", "2026-06-01"),
        ("estimated_completion_date", "changed", "2026-06-08"),
    ]
    assert forms.updated[-1].received_date == "2026-06-01"
    assert forms.updated[-1].estimated_completion_date == "2026-06-08"
    assert result.operator == "MP Cao"
    assert result.synced_at == "2026-06-10T12:00:00Z"


def test_preview_reports_unchanged_when_targets_already_match() -> None:
    service, _ = _service(
        form=_form(received_date="2026-06-01", estimated_completion_date="2026-06-08"),
        snapshot=_snapshot(sample_received_date="2026-06-01", estimated_completion_date="2026-06-08"),
    )

    result = service.preview(ProjectSection2SyncCommand(project_id="P1"))

    assert result.status == "up_to_date"
    assert [field.status for field in result.fields] == ["unchanged", "unchanged"]


def test_empty_source_dates_are_skipped_and_do_not_clear_targets() -> None:
    service, forms = _service(
        form=_form(received_date="2026-05-01", estimated_completion_date="2026-05-10"),
        snapshot=_snapshot(sample_received_date=None, estimated_completion_date=" "),
    )

    result = service.sync(
        ProjectSection2SyncCommand(
            project_id="P1",
            expected_confirmed_matrix_id="CM1",
            expected_confirmed_revision=2,
        )
    )

    assert result.status == "partial"
    assert [field.status for field in result.fields] == [
        "skipped_missing_source",
        "skipped_missing_source",
    ]
    assert forms.updated == []


def test_invalid_source_date_blocks_sync_and_does_not_mutate() -> None:
    service, forms = _service(
        form=_form(received_date="2026-05-01", estimated_completion_date="2026-05-10"),
        snapshot=_snapshot(sample_received_date="06/01/2026", estimated_completion_date="2026-06-08"),
    )

    preview = service.preview(ProjectSection2SyncCommand(project_id="P1"))

    assert preview.status == "blocked"
    assert preview.fields[0].status == "blocked_invalid_source"
    with pytest.raises(ProjectSection2SyncValidationError):
        service.sync(
            ProjectSection2SyncCommand(
                project_id="P1",
                expected_confirmed_matrix_id="CM1",
                expected_confirmed_revision=2,
            )
        )
    assert forms.updated == []


def test_missing_confirmed_matrix_is_readiness_blocker() -> None:
    service, _ = _service(form=_form(), snapshot=None)

    with pytest.raises(ProjectSection2SyncReadinessError, match="Confirm Matrix authority"):
        service.preview(ProjectSection2SyncCommand(project_id="P1"))


def test_missing_application_form_is_readiness_blocker() -> None:
    service, _ = _service(form=None, snapshot=_snapshot())

    with pytest.raises(ProjectSection2SyncReadinessError, match="Application Form"):
        service.preview(ProjectSection2SyncCommand(project_id="P1"))


def test_multiple_application_forms_are_ambiguous_target_blocker() -> None:
    service, _ = _service(
        form=[_form(form_id="FORM1"), _form(form_id="FORM2")],
        snapshot=_snapshot(),
    )

    with pytest.raises(ProjectSection2SyncAmbiguousTargetError, match="Multiple Application Forms"):
        service.preview(ProjectSection2SyncCommand(project_id="P1"))


def test_expected_confirmed_matrix_mismatch_rejects_before_mutation() -> None:
    service, forms = _service(
        form=_form(received_date="2026-05-01", estimated_completion_date="2026-05-10"),
        snapshot=_snapshot(sample_received_date="2026-06-01", estimated_completion_date="2026-06-08"),
    )

    with pytest.raises(ProjectSection2SyncConflictError):
        service.sync(
            ProjectSection2SyncCommand(
                project_id="P1",
                expected_confirmed_matrix_id="OLD",
                expected_confirmed_revision=2,
            )
        )

    assert forms.updated == []


def test_unknown_project_is_not_found() -> None:
    service, _ = _service(project=None, form=_form(), snapshot=_snapshot())

    with pytest.raises(ProjectSection2SyncReadinessError, match="Project not found"):
        service.preview(ProjectSection2SyncCommand(project_id="P1"))


class _ProjectStore:
    def __init__(self, project: Project | None) -> None:
        self._project = project

    def get(self, project_id: str) -> Project | None:
        return self._project if self._project and self._project.project_id == project_id else None


class _MatrixStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot | None) -> None:
        self._snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self._snapshot and self._snapshot.version.project_id == project_id:
            return self._snapshot
        return None


class _FormStore:
    def __init__(self, forms: list[ApplicationForm]) -> None:
        self._forms = forms
        self.updated: list[ApplicationForm] = []

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [form for form in self._forms if form.project_id == project_id]

    def update(self, form: ApplicationForm) -> ApplicationForm:
        self.updated.append(form)
        self._forms = [form if existing.form_id == form.form_id else existing for existing in self._forms]
        return form


def _service(
    *,
    project: Project | None = Project(project_id="P1", project_no="DL-1", product_name="Product", requestor="MP Cao"),
    form: ApplicationForm | list[ApplicationForm] | None = None,
    snapshot: ConfirmedMatrixSnapshot | None = None,
) -> tuple[ProjectSection2SyncService, _FormStore]:
    forms = form if isinstance(form, list) else ([] if form is None else [form])
    form_store = _FormStore(forms)
    return (
        ProjectSection2SyncService(
            project_store=_ProjectStore(project),
            confirmed_matrix_store=_MatrixStore(snapshot),
            application_form_store=form_store,
            clock=lambda: "2026-06-10T12:00:00Z",
        ),
        form_store,
    )


def _form(
    *,
    form_id: str = "FORM1",
    received_date: str | None = None,
    estimated_completion_date: str | None = None,
) -> ApplicationForm:
    return ApplicationForm(
        form_id=form_id,
        project_id="P1",
        form_no="E-3718",
        revision="H",
        requester="MP Cao",
        received_date=received_date,
        estimated_completion_date=estimated_completion_date,
    )


def _snapshot(
    *,
    sample_received_date: str | None = "2026-06-01",
    estimated_completion_date: str | None = "2026-06-08",
) -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="CM1",
            project_id="P1",
            project_matrix_draft_id="D1",
            source_import_id="I1",
            source_snapshot_id="S1",
            confirmed_revision=2,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-06-01T00:00:00Z",
            sample_received_date=sample_received_date,
            estimated_completion_date=estimated_completion_date,
        )
    )
