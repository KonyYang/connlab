"""Deterministic precheck engine for parsed application forms."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Callable

from backend.domain import IssueLevel, PrecheckIssue, PrecheckResult, PrecheckStatus
from backend.modules.intake import ParsedApplicationForm
from backend.modules.precheck.rules import DEFAULT_RULES


@dataclass(frozen=True, slots=True)
class RuleContext:
    """Input context shared by all precheck rules."""

    form: ParsedApplicationForm
    registered_attachments: tuple[str, ...] = ()


Rule = Callable[[RuleContext], list[PrecheckIssue]]


class PrecheckEngine:
    """Run deterministic precheck rules against parsed application forms."""

    def __init__(self, rules: Sequence[Rule] | None = None) -> None:
        """Create a precheck engine with default or supplied rules."""
        self._rules = tuple(rules or DEFAULT_RULES)

    def run(
        self,
        form: ParsedApplicationForm,
        registered_attachments: Sequence[str] = (),
    ) -> PrecheckResult:
        """Run precheck rules and return a domain result."""
        context = RuleContext(
            form=form,
            registered_attachments=tuple(registered_attachments),
        )
        issues: list[PrecheckIssue] = []
        for rule in self._rules:
            issues.extend(rule(context))
        issues = _renumber_issues(issues)
        return PrecheckResult(
            result_id="precheck-current",
            application_form_id=form.lab_test_request_number or "parsed-application-form",
            status=_status_from_issues(issues),
            issues=tuple(issues),
            checked_on=date.today(),
        )


def _renumber_issues(issues: list[PrecheckIssue]) -> list[PrecheckIssue]:
    """Assign deterministic issue IDs to a list of issues."""
    return [
        PrecheckIssue(
            issue_id=f"issue-{index:03d}",
            category=issue.category,
            level=issue.level,
            message=issue.message,
            field_name=issue.field_name,
            resolved=issue.resolved,
        )
        for index, issue in enumerate(issues, start=1)
    ]


def _status_from_issues(issues: list[PrecheckIssue]) -> PrecheckStatus:
    """Calculate the aggregate precheck status from issue severity."""
    if any(issue.level is IssueLevel.ERROR for issue in issues):
        return PrecheckStatus.FAILED
    if any(issue.level is IssueLevel.WARNING for issue in issues):
        return PrecheckStatus.WARNING
    return PrecheckStatus.PASSED
