"""Cleanup dry-run API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import (
    get_no_ltr_project_cleanup_service,
    get_project_ltr_cleanup_audit_service,
)
from backend.application.no_ltr_project_cleanup_service import (
    NoLtrProjectCleanupCommand,
    NoLtrProjectCleanupError,
    NoLtrProjectCleanupResult,
    NoLtrProjectCleanupService,
)
from backend.application.project_ltr_cleanup_audit_service import (
    ProjectLtrCleanupAuditReport,
    ProjectLtrCleanupAuditService,
)


router = APIRouter(prefix="/api/cleanup", tags=["cleanup"])


class ProjectLtrCleanupIssueResponse(BaseModel):
    """One cleanup dry-run issue returned by the API."""

    issue_type: str
    severity: str
    message: str
    suggested_action: str
    project_id: str | None = None
    project_name: str | None = None
    project_status: str | None = None
    ltr_id: str | None = None
    ltr_number: str | None = None


class ProjectLtrCleanupAuditResponse(BaseModel):
    """Read-only Project/LTR cleanup audit response."""

    generated_at: str
    total_projects: int
    total_ltr_records: int
    issues: list[ProjectLtrCleanupIssueResponse]


class NoLtrProjectCleanupExecuteRequest(BaseModel):
    """Operator request for controlled no-LTR project cleanup execution."""

    project_ids: list[str]
    reason: str
    operator: str | None = None


class NoLtrProjectCleanupChangedProjectResponse(BaseModel):
    """One project changed by cleanup execution."""

    project_id: str
    previous_status: str
    new_status: str
    cleanup_id: str


class NoLtrProjectCleanupRejectedProjectResponse(BaseModel):
    """One project rejected by cleanup execution."""

    project_id: str
    reason: str


class NoLtrProjectCleanupExecuteResponse(BaseModel):
    """Controlled no-LTR project cleanup execution response."""

    cancelled_count: int
    skipped_count: int
    changed: list[NoLtrProjectCleanupChangedProjectResponse]
    rejected: list[NoLtrProjectCleanupRejectedProjectResponse]


@router.get(
    "/project-ltr/dry-run",
    response_model=ProjectLtrCleanupAuditResponse,
)
def project_ltr_cleanup_dry_run(
    service: ProjectLtrCleanupAuditService = Depends(
        get_project_ltr_cleanup_audit_service
    ),
) -> ProjectLtrCleanupAuditResponse:
    """Return read-only Project/LTR cleanup candidates."""
    return _to_response(service.dry_run())


@router.post(
    "/project-ltr/no-ltr-projects/execute",
    response_model=NoLtrProjectCleanupExecuteResponse,
)
def execute_no_ltr_project_cleanup(
    request: NoLtrProjectCleanupExecuteRequest,
    service: NoLtrProjectCleanupService = Depends(
        get_no_ltr_project_cleanup_service
    ),
) -> NoLtrProjectCleanupExecuteResponse:
    """Cancel selected projects that still have no registered LTR."""
    try:
        result = service.execute(
            NoLtrProjectCleanupCommand(
                project_ids=tuple(request.project_ids),
                reason=request.reason,
                operator=request.operator,
            )
        )
    except NoLtrProjectCleanupError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_execute_response(result)


def _to_response(report: ProjectLtrCleanupAuditReport) -> ProjectLtrCleanupAuditResponse:
    return ProjectLtrCleanupAuditResponse(
        generated_at=report.generated_at,
        total_projects=report.total_projects,
        total_ltr_records=report.total_ltr_records,
        issues=[
            ProjectLtrCleanupIssueResponse(
                issue_type=issue.issue_type,
                severity=issue.severity,
                message=issue.message,
                suggested_action=issue.suggested_action,
                project_id=issue.project_id,
                project_name=issue.project_name,
                project_status=issue.project_status,
                ltr_id=issue.ltr_id,
                ltr_number=issue.ltr_number,
            )
            for issue in report.issues
        ],
    )


def _to_execute_response(
    result: NoLtrProjectCleanupResult,
) -> NoLtrProjectCleanupExecuteResponse:
    return NoLtrProjectCleanupExecuteResponse(
        cancelled_count=result.cancelled_count,
        skipped_count=result.skipped_count,
        changed=[
            NoLtrProjectCleanupChangedProjectResponse(
                project_id=project.project_id,
                previous_status=project.previous_status,
                new_status=project.new_status,
                cleanup_id=project.cleanup_id,
            )
            for project in result.changed
        ],
        rejected=[
            NoLtrProjectCleanupRejectedProjectResponse(
                project_id=project.project_id,
                reason=project.reason,
            )
            for project in result.rejected
        ],
    )
