"""Recoverable registry transitions preserve independent business aggregates."""

from contextlib import nullcontext
from dataclasses import replace
from datetime import date

import pytest
from sqlalchemy import create_engine

from backend.application.project_registry_management_service import (
    ProjectRegistryManagementService, ProjectRegistryConflict,
)
from backend.domain import Project, ProjectStatus, LtrRecord, LtrStatus
from backend.infrastructure.storage.database import init_db, create_session_factory
from backend.infrastructure.storage.repositories.project import ProjectRepository
from backend.infrastructure.storage.repositories.project_registry import ProjectRegistryRepository
from backend.infrastructure.storage.repositories import LtrRecordRepository


class NoGeneration:
    def lock(self, project_id):
        return nullcontext()

    def read(self, project_id):
        return None


@pytest.fixture
def context():
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    with create_session_factory(engine)() as session:
        projects = ProjectRepository(session)
        ltrs = LtrRecordRepository(session)
        repository = ProjectRegistryRepository(session)
        service = ProjectRegistryManagementService(repository, ltrs, NoGeneration())
        yield session, projects, ltrs, service
    engine.dispose()


def project(project_id, *, state=ProjectStatus.LTR_REGISTERED):
    return Project(project_id=project_id, project_no="DL-2026-01-002", product_name=project_id,
                   requestor="User", status=state, created_on=date(2026, 9, 9))


def test_trash_hides_from_normal_list_but_retains_record_business_state_and_ltr(context):
    session, projects, ltrs, service = context
    original = projects.create(project("old"))
    session.commit()
    preview = service.preview("old", "trash")
    result = service.trash("old", token=preview.token, reason="Mistaken creation", actor="User")
    assert result.registry_state == "trash"
    assert projects.list() == []
    assert projects.get("old").status == original.status
    assert projects.get("old").project_id == "old"
    assert service.list_entries("trash")[0].project_id == "old"
    assert ltrs.list() == []


def test_restore_conflict_requires_explicit_choice_and_preserves_both_records(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    registered_ltr(ltrs, "old")
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Duplicate")
    projects.create(project("new"))
    registered_ltr(ltrs, "new")
    session.commit()
    preview = service.preview("old", "restore")
    assert [p.project_id for p in preview.conflicts] == ["new"]
    with pytest.raises(ProjectRegistryConflict, match="conflict"):
        service.restore("old", token=preview.token, destination="active")
    assert projects.get("old").registry_state == "trash"
    result = service.restore("old", token=preview.token, destination="active", replace_conflicts=True)
    assert result.registry_state == "active"
    assert projects.get("new").registry_state == "history"
    assert projects.get("new").product_name == "new"
    assert [p.project_id for p in projects.list()] == ["old"]


def test_stale_restore_preview_does_not_partially_move_projects(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    registered_ltr(ltrs, "old")
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Mistaken creation")
    preview = service.preview("old", "restore")
    projects.create(project("new"))
    registered_ltr(ltrs, "new")
    session.commit()
    with pytest.raises(ProjectRegistryConflict, match="changed"):
        service.restore("old", token=preview.token, destination="active", replace_conflicts=True)
    assert projects.get("old").registry_state == "trash"
    assert projects.get("new").registry_state == "active"


def test_history_restore_preserves_closed_lifecycle_and_can_be_reversed(context):
    from backend.domain import ProjectLifecycleState
    session, projects, ltrs, service = context
    original = replace(project("old", state=ProjectStatus.CLOSED), lifecycle_state=ProjectLifecycleState.CLOSED,
                       closed_reason="Completed externally", closed_at="2026-09-01")
    projects.create(original)
    registered_ltr(ltrs, "old")
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Duplicate")
    projects.create(project("new"))
    registered_ltr(ltrs, "new")
    session.commit()
    service.restore("old", token=service.preview("old", "restore").token, destination="history")
    assert projects.get("new").registry_state == "active"
    assert service.list_entries("history")[0].lifecycle_state == "closed"
    service.restore("old", token=service.preview("old", "restore").token,
                    destination="active", replace_conflicts=True)
    assert projects.get("old").closed_reason == original.closed_reason
    assert projects.get("old").lifecycle_state == ProjectLifecycleState.CLOSED
    assert projects.get("new").registry_state == "history"


def test_registry_moves_leave_all_ltr_ownership_and_business_fields_intact(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    original_ltr = LtrRecord(ltr_id="L1", project_id="old", ltr_number="DL-2026-01-002",
                             status=LtrStatus.REGISTERED, is_current_owner=False,
                             superseded_by_ltr_id="L2", superseded_reason="Existing ownership decision")
    ltrs.create(original_ltr)
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Duplicate")
    projects.create(replace(project("new"), project_no="LEGACY-NUMBER"))
    ltrs.create(LtrRecord(ltr_id="L2", project_id="new", ltr_number="DL-2026-01-002",
                          status=LtrStatus.REGISTERED))
    session.commit()
    assert service.preview("old", "restore").conflicts[0].project_id == "new"
    service.restore("old", token=service.preview("old", "restore").token,
                    destination="active", replace_conflicts=True)
    assert ltrs.list_by_project("old") == [original_ltr]
    assert ltrs.list_by_project("new")[0].is_current_owner is True
    events = ProjectRegistryRepository(session).list_events("old")
    assert [(e.previous_state, e.new_state) for e in events] == [("active", "trash"), ("trash", "active")]
    assert events[-1].operation_id == ProjectRegistryRepository(session).list_events("new")[-1].operation_id


def test_all_conflicts_are_rechecked_and_moved_as_one_operation(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    registered_ltr(ltrs, "old")
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Duplicate")
    for project_id in ["new1", "new2"]:
        projects.create(project(project_id))
        registered_ltr(ltrs, project_id)
    session.commit()
    preview = service.preview("old", "restore")
    assert {e.project_id for e in preview.conflicts} == {"new1", "new2"}
    service.restore("old", token=preview.token, destination="active", replace_conflicts=True)
    assert {e.project_id for e in service.list_entries("history")} == {"new1", "new2"}


def test_failed_commit_rolls_back_every_conflict_and_audit_event(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    registered_ltr(ltrs, "old")
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Duplicate")
    projects.create(project("new"))
    registered_ltr(ltrs, "new")
    session.commit()
    class FailingRepository(ProjectRegistryRepository):
        def commit(self):
            raise RuntimeError("Storage failure")
    service = ProjectRegistryManagementService(FailingRepository(session), ltrs, NoGeneration())
    with pytest.raises(RuntimeError, match="Storage failure"):
        service.restore("old", token=service.preview("old", "restore").token,
                        destination="active", replace_conflicts=True)
    assert projects.get("old").registry_state == "trash"
    assert projects.get("new").registry_state == "active"
    assert ProjectRegistryRepository(session).list_events("new") == []


def test_changed_display_ltr_identifier_invalidates_preview(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    registered_ltr(ltrs, "old")
    session.commit()
    preview = service.preview("old", "trash")
    assert preview.project.display_project_id == "DL-2026-01-002"
    ltrs.update(replace(ltrs.get("ltr-old"), ltr_number="DL-2026-01-003"))
    session.commit()
    assert service.preview("old", "trash").project.display_project_id == "DL-2026-01-003"
    with pytest.raises(ProjectRegistryConflict, match="changed"):
        service.trash("old", token=preview.token, reason="Mistake")


def registered_ltr(ltrs, project_id):
    ltrs.create(LtrRecord(ltr_id="ltr-"+project_id, project_id=project_id, ltr_number="DL-2026-01-002",
                          status=LtrStatus.REGISTERED, is_current_owner=False))


def test_unregistered_project_numbers_do_not_create_invisible_display_conflicts(context):
    session, projects, _, service = context
    projects.create(project("old"))
    session.commit()
    service.trash("old", token=service.preview("old", "trash").token, reason="Mistake")
    projects.create(project("new"))
    session.commit()
    preview = service.preview("old", "restore")
    assert preview.project.display_project_id == "TMP-OLD"
    assert preview.conflicts == ()
    service.restore("old", token=preview.token, destination="active")
    assert {p.project_id for p in projects.list()} == {"old", "new"}


def test_delete_preview_discloses_actual_retained_relations(context):
    session, projects, ltrs, service = context
    projects.create(project("old"))
    registered_ltr(ltrs, "old")
    session.commit()
    preview = service.preview("old", "trash")
    assert "LTR records retained: 1" in preview.retained_data
    assert "Confirmed Matrix versions retained: 0" in preview.retained_data
