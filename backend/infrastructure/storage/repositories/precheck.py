"""Precheck result repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.domain import (
    IssueCategory,
    IssueLevel,
    PrecheckIssue,
    PrecheckResult,
    PrecheckStatus,
)
from backend.infrastructure.storage.models import PrecheckIssueModel, PrecheckResultModel


class PrecheckResultRepository:
    """Persist and load precheck results with their issue rows."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, result: PrecheckResult) -> PrecheckResult:
        """Persist a precheck result and all contained issues."""
        self._session.add(_result_to_model(result))
        self._session.flush()
        return result

    def get(self, result_id: str) -> PrecheckResult | None:
        """Return a precheck result by ID, or None when missing."""
        row = self._session.scalars(
            select(PrecheckResultModel)
            .options(selectinload(PrecheckResultModel.issues))
            .where(PrecheckResultModel.result_id == result_id)
        ).one_or_none()
        return _result_to_domain(row) if row else None

    def list_by_application_form(self, application_form_id: str) -> list[PrecheckResult]:
        """Return precheck results for an application form."""
        rows = self._session.scalars(
            select(PrecheckResultModel)
            .options(selectinload(PrecheckResultModel.issues))
            .where(PrecheckResultModel.application_form_id == application_form_id)
            .order_by(PrecheckResultModel.result_id)
        ).all()
        return [_result_to_domain(row) for row in rows]

    def latest_by_project(self, project_id: str) -> PrecheckResult | None:
        """Return the latest precheck result for a project."""
        from backend.infrastructure.storage.models import ApplicationFormModel

        row = self._session.scalars(
            select(PrecheckResultModel)
            .join(
                ApplicationFormModel,
                PrecheckResultModel.application_form_id == ApplicationFormModel.form_id,
            )
            .options(selectinload(PrecheckResultModel.issues))
            .where(ApplicationFormModel.project_id == project_id)
            .order_by(PrecheckResultModel.checked_on.desc(), PrecheckResultModel.result_id.desc())
            .limit(1)
        ).one_or_none()
        return _result_to_domain(row) if row else None

    def resolve_issue(self, issue_id: str) -> PrecheckIssue | None:
        """Mark one issue resolved and return the updated domain issue."""
        row = self._session.get(PrecheckIssueModel, issue_id)
        if row is None:
            return None
        row.resolved = True
        self._session.flush()
        return _issue_to_domain(row)

    def update(self, result: PrecheckResult) -> PrecheckResult:
        """Replace an existing precheck result and its issue rows."""
        row = self._session.scalars(
            select(PrecheckResultModel)
            .options(selectinload(PrecheckResultModel.issues))
            .where(PrecheckResultModel.result_id == result.result_id)
        ).one_or_none()
        if row is None:
            raise ValueError(f"Precheck result not found: {result.result_id}")
        row.application_form_id = result.application_form_id
        row.status = result.status.value
        row.checked_on = result.checked_on
        row.issues = [_issue_to_model(issue) for issue in result.issues]
        self._session.flush()
        return result


def _result_to_model(result: PrecheckResult) -> PrecheckResultModel:
    """Convert a precheck result domain record to an ORM row."""
    return PrecheckResultModel(
        result_id=result.result_id,
        application_form_id=result.application_form_id,
        status=result.status.value,
        checked_on=result.checked_on,
        issues=[_issue_to_model(issue) for issue in result.issues],
    )


def _issue_to_model(issue: PrecheckIssue) -> PrecheckIssueModel:
    """Convert a precheck issue domain record to an ORM row."""
    return PrecheckIssueModel(
        issue_id=issue.issue_id,
        category=issue.category.value,
        level=issue.level.value,
        message=issue.message,
        field_name=issue.field_name,
        resolved=issue.resolved,
    )


def _result_to_domain(row: PrecheckResultModel) -> PrecheckResult:
    """Convert a precheck result ORM row to a domain record."""
    return PrecheckResult(
        result_id=row.result_id,
        application_form_id=row.application_form_id,
        status=PrecheckStatus(row.status),
        issues=tuple(_issue_to_domain(issue) for issue in row.issues),
        checked_on=row.checked_on,
    )


def _issue_to_domain(row: PrecheckIssueModel) -> PrecheckIssue:
    """Convert a precheck issue ORM row to a domain record."""
    return PrecheckIssue(
        issue_id=row.issue_id,
        category=IssueCategory(row.category),
        level=IssueLevel(row.level),
        message=row.message,
        field_name=row.field_name,
        resolved=row.resolved,
    )
