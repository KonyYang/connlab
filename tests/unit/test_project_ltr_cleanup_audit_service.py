from backend.application.project_ltr_cleanup_audit_service import (
    ProjectLtrCleanupAuditService,
)
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus


def test_cleanup_audit_classifies_dirty_project_ltr_records() -> None:
    service = ProjectLtrCleanupAuditService(
        project_store=_ProjectStore(
            [
                _project("P-NO-LTR", "No LTR", ProjectStatus.CONFIRMED),
                _project("P-BAD", "Bad LTR", ProjectStatus.LTR_REGISTERED),
                _project("P-MULTI", "Multi LTR", ProjectStatus.LTR_REGISTERED),
                _project("P-GOOD", "Good LTR", ProjectStatus.LTR_REGISTERED),
            ]
        ),
        ltr_store=_LtrStore(
            [
                _ltr("L-BAD", "P-BAD", "DL-2026-04-075810"),
                _ltr("L-MULTI-1", "P-MULTI", "DL-2026-04-001"),
                _ltr("L-MULTI-2", "P-MULTI", "DL-2026-04-002"),
                _ltr("L-GOOD", "P-GOOD", "DL-2026-04-003"),
                _ltr("L-ORPHAN", "P-MISSING", "DL-2026-04-004"),
            ]
        ),
    )

    report = service.dry_run()

    assert report.total_projects == 4
    assert report.total_ltr_records == 5
    issue_types = [issue.issue_type for issue in report.issues]
    assert "project_without_registered_ltr" in issue_types
    assert "invalid_registered_ltr_number" in issue_types
    assert "project_multiple_registered_ltrs" in issue_types
    assert "orphan_ltr_record" in issue_types
    invalid = [
        issue for issue in report.issues
        if issue.issue_type == "invalid_registered_ltr_number"
    ][0]
    assert invalid.ltr_number == "DL-2026-04-075810"
    assert invalid.severity == "error"


def _project(project_id: str, product_name: str, status: ProjectStatus) -> Project:
    return Project(
        project_id=project_id,
        project_no=None,
        product_name=product_name,
        requestor="Alice",
        status=status,
    )


def _ltr(ltr_id: str, project_id: str, number: str) -> LtrRecord:
    return LtrRecord(
        ltr_id=ltr_id,
        project_id=project_id,
        ltr_number=number,
        status=LtrStatus.REGISTERED,
    )


class _ProjectStore:
    def __init__(self, projects: list[Project]) -> None:
        self._projects = projects

    def list(self) -> list[Project]:
        return self._projects


class _LtrStore:
    def __init__(self, ltrs: list[LtrRecord]) -> None:
        self._ltrs = ltrs

    def list(self) -> list[LtrRecord]:
        return self._ltrs
