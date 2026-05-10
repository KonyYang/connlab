from datetime import date

import pytest

from backend.application.no_ltr_project_cleanup_service import (
    NO_LTR_PROJECT_RESIDUE,
    NoLtrProjectCleanupCommand,
    NoLtrProjectCleanupError,
    NoLtrProjectCleanupService,
    ProjectCleanupAuditRecord,
)
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus


def test_execute_cancels_selected_project_without_registered_ltr() -> None:
    projects = FakeProjectStore(
        [
            Project(
                project_id="P-NO-LTR",
                project_no=None,
                product_name="No LTR Project",
                requestor="Alice",
                status=ProjectStatus.CONFIRMED,
                created_on=date(2026, 5, 10),
            )
        ]
    )
    ltrs = FakeLtrStore({})
    audits = FakeAuditStore()
    service = NoLtrProjectCleanupService(projects, ltrs, audits)

    result = service.execute(
        NoLtrProjectCleanupCommand(
            project_ids=("P-NO-LTR",),
            reason="Historical test project without LTR.",
            operator="tester",
        )
    )

    assert result.cancelled_count == 1
    assert result.skipped_count == 0
    assert result.rejected == ()
    assert projects.items["P-NO-LTR"].status is ProjectStatus.CANCELLED
    assert len(audits.items) == 1
    audit = audits.items[0]
    assert audit.cleanup_type == NO_LTR_PROJECT_RESIDUE
    assert audit.previous_status == ProjectStatus.CONFIRMED.value
    assert audit.new_status == ProjectStatus.CANCELLED.value
    assert audit.reason == "Historical test project without LTR."
    assert audit.operator == "tester"


def test_execute_rejects_project_with_registered_ltr() -> None:
    projects = FakeProjectStore(
        [
            Project(
                project_id="P-HAS-LTR",
                project_no=None,
                product_name="Registered Project",
                requestor="Bob",
                status=ProjectStatus.LTR_REGISTERED,
            )
        ]
    )
    ltrs = FakeLtrStore(
        {
            "P-HAS-LTR": [
                LtrRecord(
                    ltr_id="LTR-1",
                    project_id="P-HAS-LTR",
                    ltr_number="DL-2026-04-099",
                    status=LtrStatus.REGISTERED,
                )
            ]
        }
    )
    audits = FakeAuditStore()
    service = NoLtrProjectCleanupService(projects, ltrs, audits)

    result = service.execute(
        NoLtrProjectCleanupCommand(
            project_ids=("P-HAS-LTR",),
            reason="Clean old no-LTR residue.",
        )
    )

    assert result.cancelled_count == 0
    assert len(result.rejected) == 1
    assert result.rejected[0].project_id == "P-HAS-LTR"
    assert "registered LTR" in result.rejected[0].reason
    assert projects.items["P-HAS-LTR"].status is ProjectStatus.LTR_REGISTERED
    assert audits.items == []


def test_execute_requires_reason() -> None:
    service = NoLtrProjectCleanupService(
        FakeProjectStore([]),
        FakeLtrStore({}),
        FakeAuditStore(),
    )

    with pytest.raises(NoLtrProjectCleanupError):
        service.execute(
            NoLtrProjectCleanupCommand(project_ids=("P-1",), reason="  ")
        )


def test_execute_skips_already_cancelled_project_without_duplicate_audit() -> None:
    projects = FakeProjectStore(
        [
            Project(
                project_id="P-CANCELLED",
                project_no=None,
                product_name="Cancelled Project",
                requestor="Alice",
                status=ProjectStatus.CANCELLED,
            )
        ]
    )
    audits = FakeAuditStore()
    service = NoLtrProjectCleanupService(projects, FakeLtrStore({}), audits)

    result = service.execute(
        NoLtrProjectCleanupCommand(
            project_ids=("P-CANCELLED",),
            reason="Already cleaned.",
        )
    )

    assert result.cancelled_count == 0
    assert result.skipped_count == 1
    assert result.changed == ()
    assert result.rejected == ()
    assert audits.items == []


class FakeProjectStore:
    def __init__(self, projects: list[Project]) -> None:
        self.items = {project.project_id: project for project in projects}

    def get(self, project_id: str) -> Project | None:
        return self.items.get(project_id)

    def update(self, project: Project) -> Project:
        self.items[project.project_id] = project
        return project


class FakeLtrStore:
    def __init__(self, ltrs_by_project: dict[str, list[LtrRecord]]) -> None:
        self._items = ltrs_by_project

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return self._items.get(project_id, [])


class FakeAuditStore:
    def __init__(self) -> None:
        self.items: list[ProjectCleanupAuditRecord] = []

    def create(
        self,
        record: ProjectCleanupAuditRecord,
    ) -> ProjectCleanupAuditRecord:
        self.items.append(record)
        return record
