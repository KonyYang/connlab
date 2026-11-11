from backend.application.project_library.automatic_snapshot import AutomaticPortableSnapshotService


class FakeStore:
    def __init__(self, member=None, workspace=None):
        self._member = member
        self._workspace = workspace

    def member_for_project(self, project_id):
        assert project_id == "project-1"
        return self._member

    def workspace(self, project_id):
        return self._workspace


class FakePortability:
    def __init__(self, error=None):
        self.error = error
        self.prepared = []
        self.options = []

    def prepare_latest(self, member, **options):
        self.prepared.append(member)
        self.options.append(options)
        if self.error:
            raise self.error
        return {"status": "current"}


def test_refresh_prepares_the_current_library_member_after_a_lifecycle_write():
    member = {"member_id": "member-1", "project_id": "project-1"}
    portability = FakePortability()
    service = AutomaticPortableSnapshotService(
        FakeStore(member, {"workspace_id": "workspace-1"}), portability
    )

    result = service.refresh("project-1")

    assert result.status == "updated"
    assert portability.prepared == [member]
    assert portability.options == [{
        "locked": False,
        "project_locked": False,
        "persist_member": False,
    }]


def test_refresh_skips_projects_without_a_managed_workspace():
    portability = FakePortability()
    service = AutomaticPortableSnapshotService(
        FakeStore({"member_id": "member-1", "project_id": "project-1"}, None), portability
    )
    assert service.refresh("project-1").status == "skipped"
    assert portability.prepared == []


def test_refresh_reports_failure_without_raising_after_business_commit():
    portability = FakePortability(OSError("disk temporarily unavailable"))
    service = AutomaticPortableSnapshotService(
        FakeStore({"member_id": "member-1", "project_id": "project-1"}, {"workspace_id": "workspace-1"}),
        portability,
    )
    result = service.refresh("project-1")
    assert result.status == "failed"
    assert "disk temporarily unavailable" in result.message
