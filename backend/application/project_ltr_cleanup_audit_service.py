"""Read-only Project/LTR cleanup audit service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Protocol

from backend.domain import LtrRecord, LtrStatus, Project
from backend.modules.ltr import LtrNumberError, parse_ltr_number


class ProjectCleanupStore(Protocol):
    """Project lookup behavior required by cleanup dry-run."""

    def list(self) -> list[Project]:
        """Return all projects."""


class LtrCleanupStore(Protocol):
    """LTR lookup behavior required by cleanup dry-run."""

    def list(self) -> list[LtrRecord]:
        """Return all LTR records."""


@dataclass(frozen=True, slots=True)
class ProjectLtrCleanupIssue:
    """One read-only cleanup candidate issue."""

    issue_type: str
    severity: str
    message: str
    suggested_action: str
    project_id: str | None = None
    project_name: str | None = None
    project_status: str | None = None
    ltr_id: str | None = None
    ltr_number: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectLtrCleanupAuditReport:
    """Read-only Project/LTR cleanup audit report."""

    generated_at: str
    total_projects: int
    total_ltr_records: int
    issues: tuple[ProjectLtrCleanupIssue, ...]


class ProjectLtrCleanupAuditService:
    """Build a read-only report of dirty Project/LTR records."""

    def __init__(
        self,
        *,
        project_store: ProjectCleanupStore,
        ltr_store: LtrCleanupStore,
    ) -> None:
        self._projects = project_store
        self._ltrs = ltr_store

    def dry_run(self) -> ProjectLtrCleanupAuditReport:
        """Return a read-only cleanup report without mutating storage."""
        projects = self._projects.list()
        ltrs = self._ltrs.list()
        projects_by_id = {project.project_id: project for project in projects}
        ltrs_by_project: dict[str, list[LtrRecord]] = {}
        for ltr in ltrs:
            ltrs_by_project.setdefault(ltr.project_id, []).append(ltr)

        issues: list[ProjectLtrCleanupIssue] = []
        issues.extend(_project_without_registered_ltr_issues(projects, ltrs_by_project))
        issues.extend(_invalid_registered_ltr_issues(ltrs, projects_by_id))
        issues.extend(_multiple_registered_ltr_issues(projects, ltrs_by_project))
        issues.extend(_orphan_ltr_issues(ltrs, projects_by_id))

        return ProjectLtrCleanupAuditReport(
            generated_at=datetime.now(UTC).isoformat(),
            total_projects=len(projects),
            total_ltr_records=len(ltrs),
            issues=tuple(issues),
        )


def _project_without_registered_ltr_issues(
    projects: list[Project],
    ltrs_by_project: dict[str, list[LtrRecord]],
) -> list[ProjectLtrCleanupIssue]:
    issues: list[ProjectLtrCleanupIssue] = []
    for project in projects:
        registered = [
            ltr for ltr in ltrs_by_project.get(project.project_id, [])
            if ltr.status is LtrStatus.REGISTERED
        ]
        if registered:
            continue
        issues.append(
            ProjectLtrCleanupIssue(
                issue_type="project_without_registered_ltr",
                severity="warning",
                project_id=project.project_id,
                project_name=_project_name(project),
                project_status=project.status.value,
                message="Project has no registered LTR record.",
                suggested_action="Review whether this is a draft residue; soft-delete or keep as exception in a later approved cleanup task.",
            )
        )
    return issues


def _invalid_registered_ltr_issues(
    ltrs: list[LtrRecord],
    projects_by_id: dict[str, Project],
) -> list[ProjectLtrCleanupIssue]:
    issues: list[ProjectLtrCleanupIssue] = []
    for ltr in ltrs:
        if ltr.status is not LtrStatus.REGISTERED:
            continue
        try:
            parse_ltr_number(ltr.ltr_number)
        except LtrNumberError:
            project = projects_by_id.get(ltr.project_id)
            issues.append(
                ProjectLtrCleanupIssue(
                    issue_type="invalid_registered_ltr_number",
                    severity="error",
                    project_id=ltr.project_id,
                    project_name=_project_name(project) if project else None,
                    project_status=project.status.value if project else None,
                    ltr_id=ltr.ltr_id,
                    ltr_number=ltr.ltr_number,
                    message="Registered LTR number does not match the approved DL number format.",
                    suggested_action="Review against LTR.XLS; cancel, migrate, or mark for recycle in a later approved cleanup task.",
                )
            )
    return issues


def _multiple_registered_ltr_issues(
    projects: list[Project],
    ltrs_by_project: dict[str, list[LtrRecord]],
) -> list[ProjectLtrCleanupIssue]:
    issues: list[ProjectLtrCleanupIssue] = []
    for project in projects:
        registered = [
            ltr for ltr in ltrs_by_project.get(project.project_id, [])
            if ltr.status is LtrStatus.REGISTERED
        ]
        if len(registered) <= 1:
            continue
        issues.append(
            ProjectLtrCleanupIssue(
                issue_type="project_multiple_registered_ltrs",
                severity="error",
                project_id=project.project_id,
                project_name=_project_name(project),
                project_status=project.status.value,
                ltr_number=", ".join(ltr.ltr_number for ltr in registered),
                message="Project has more than one registered LTR record.",
                suggested_action="Manually choose the authoritative LTR and cancel the others in a later approved cleanup task.",
            )
        )
    return issues


def _orphan_ltr_issues(
    ltrs: list[LtrRecord],
    projects_by_id: dict[str, Project],
) -> list[ProjectLtrCleanupIssue]:
    issues: list[ProjectLtrCleanupIssue] = []
    for ltr in ltrs:
        if ltr.project_id in projects_by_id:
            continue
        issues.append(
            ProjectLtrCleanupIssue(
                issue_type="orphan_ltr_record",
                severity="error",
                project_id=ltr.project_id,
                ltr_id=ltr.ltr_id,
                ltr_number=ltr.ltr_number,
                message="LTR record points to a missing project.",
                suggested_action="Review database history; cancel or remap the LTR in a later approved cleanup task.",
            )
        )
    return issues


def _project_name(project: Project | None) -> str | None:
    if project is None:
        return None
    return project.project_no or project.product_name
