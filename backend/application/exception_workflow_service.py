"""Explicit exception workflows for real intake and LTR correction cases."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageStatus,
)


class ExceptionWorkflowKind(StrEnum):
    """Supported explicit exception workflow kinds."""

    NO_APPLICATION_FORM = "no_application_form"
    MULTIPLE_APPLICATION_FORMS = "multiple_application_forms"
    MISSING_INFORMATION = "missing_information"
    CORRECTION_EVIDENCE = "correction_evidence"
    LTR_RENUMBER_REQUIRED = "ltr_renumber_required"


class ExceptionWorkflowError(ValueError):
    """Raised when an exception workflow cannot proceed."""


class ExceptionWorkflowNotFoundError(LookupError):
    """Raised when exception workflow input records are missing."""


@dataclass(frozen=True, slots=True)
class ExceptionWorkflowIssue:
    """One explicit exception issue and operator action."""

    kind: ExceptionWorkflowKind
    message: str
    operator_action: str
    blocking: bool
    asset_id: str | None = None
    case_id: str | None = None


@dataclass(frozen=True, slots=True)
class ExceptionWorkflowReview:
    """Review result for intake exception workflows."""

    package_id: str
    issues: tuple[ExceptionWorkflowIssue, ...]
    cases: tuple[IntakeCase, ...]
    drafts: tuple[IntakeDraft, ...]
    package: IntakePackage


class IntakePackageStore(Protocol):
    """Package store behavior required by exception workflows."""

    def get(self, package_id: str) -> IntakePackage | None:
        """Return an intake package by ID."""

    def update(self, package: IntakePackage) -> IntakePackage:
        """Update an intake package."""


class IntakeAssetStore(Protocol):
    """Asset store behavior required by exception workflows."""

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        """Return intake assets for one package."""


class IntakeCaseStore(Protocol):
    """Case store behavior required by exception workflows."""

    def create(self, case: IntakeCase) -> IntakeCase:
        """Create an intake case."""

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        """Return cases for one package."""


class IntakeDraftStore(Protocol):
    """Draft store behavior required by exception workflows."""

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        """Create an intake draft."""

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        """Return the draft for one case."""


class ExceptionWorkflowService:
    """Make real intake exception cases explicit and traceable."""

    _candidate_roles = {
        IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        IntakeAssetRole.SELECTED_APPLICATION_FORM,
    }

    def __init__(
        self,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
    ) -> None:
        """Create an exception workflow service."""
        self._packages = package_store
        self._assets = asset_store
        self._cases = case_store
        self._drafts = draft_store

    def review_package(self, package_id: str) -> ExceptionWorkflowReview:
        """Review and persist explicit exception state for one intake package."""
        package = self._get_package(package_id)
        assets = self._assets.list_by_package(package.package_id)
        candidates = [asset for asset in assets if asset.asset_role in self._candidate_roles]
        if not candidates:
            updated = self._mark_package_follow_up(package)
            return ExceptionWorkflowReview(
                package_id=package.package_id,
                issues=(
                    ExceptionWorkflowIssue(
                        kind=ExceptionWorkflowKind.NO_APPLICATION_FORM,
                        message="No application form candidate was found in this intake package.",
                        operator_action=(
                            "Request the application form or import the Word form directly."
                        ),
                        blocking=True,
                    ),
                ),
                cases=(),
                drafts=(),
                package=updated,
            )

        cases, drafts = self._ensure_cases(package.package_id, candidates)
        issues = self._issues_for_candidates(candidates, cases)
        return ExceptionWorkflowReview(
            package_id=package.package_id,
            issues=tuple(issues),
            cases=tuple(cases),
            drafts=tuple(drafts),
            package=package,
        )

    def _get_package(self, package_id: str) -> IntakePackage:
        """Load a package or raise not found."""
        package = self._packages.get(package_id)
        if package is None:
            raise ExceptionWorkflowNotFoundError(f"Intake package not found: {package_id}")
        return package

    def _mark_package_follow_up(self, package: IntakePackage) -> IntakePackage:
        """Mark a package as needing application-form follow-up."""
        return self._packages.update(
            replace(
                package,
                status=IntakePackageStatus.NEEDS_APPLICATION_FORM_SELECTION,
                notes=_json_notes(
                    ExceptionWorkflowKind.NO_APPLICATION_FORM,
                    "No application form candidate was found.",
                ),
            )
        )

    def _ensure_cases(
        self,
        package_id: str,
        candidates: list[IntakeAsset],
    ) -> tuple[list[IntakeCase], list[IntakeDraft]]:
        """Ensure each application form candidate has its own case and draft."""
        existing = self._cases.list_by_package(package_id)
        existing_by_asset = {
            case.selected_form_asset_id: case
            for case in existing
            if case.selected_form_asset_id
        }
        cases: list[IntakeCase] = []
        drafts: list[IntakeDraft] = []
        multi = len(candidates) > 1
        for candidate in candidates:
            case = existing_by_asset.get(candidate.asset_id)
            if case is None:
                case = self._cases.create(
                    IntakeCase(
                        case_id=f"case-{uuid4().hex}",
                        package_id=package_id,
                        selected_form_asset_id=candidate.asset_id,
                        status=IntakeCaseStatus.NEEDS_REVIEW,
                        reviewer_notes=_case_note(candidate, multi),
                    )
                )
            draft = self._drafts.get_by_case(case.case_id)
            if draft is None:
                draft = self._drafts.create(_draft_for_case(case, multi))
            cases.append(case)
            drafts.append(draft)
        return cases, drafts

    def _issues_for_candidates(
        self,
        candidates: list[IntakeAsset],
        cases: list[IntakeCase],
    ) -> list[ExceptionWorkflowIssue]:
        """Return explicit issues for candidate review results."""
        if len(candidates) <= 1:
            return []
        case_by_asset = {case.selected_form_asset_id: case for case in cases}
        return [
            ExceptionWorkflowIssue(
                kind=ExceptionWorkflowKind.MULTIPLE_APPLICATION_FORMS,
                message="Multiple application form candidates were found.",
                operator_action=(
                    "Review each generated case separately; each selected form can "
                    "be confirmed into its own project."
                ),
                blocking=False,
                asset_id=candidate.asset_id,
                case_id=case_by_asset.get(candidate.asset_id).case_id
                if case_by_asset.get(candidate.asset_id)
                else None,
            )
            for candidate in candidates
        ]


def _draft_for_case(case: IntakeCase, multi: bool) -> IntakeDraft:
    """Create an empty review draft with exception workflow warnings."""
    return IntakeDraft(
        draft_id=f"draft-{uuid4().hex}",
        case_id=case.case_id,
        parsed_fields_json="{}",
        parser_warnings_json=json.dumps(_draft_warnings(multi), separators=(",", ":")),
    )


def _draft_warnings(multi: bool) -> list[str]:
    """Return parser warnings for exception-created drafts."""
    warnings = ["Review and confirm required fields before project creation."]
    if multi:
        warnings.append("Multiple application forms were found in the same intake package.")
    return warnings


def _case_note(candidate: IntakeAsset, multi: bool) -> str:
    """Return business-readable notes for exception-created cases."""
    if multi:
        return (
            "Exception workflow: multiple application forms were found; "
            f"review candidate {candidate.original_name} as a separate case."
        )
    return f"Exception workflow: review candidate {candidate.original_name}."


def _json_notes(kind: ExceptionWorkflowKind, message: str) -> str:
    """Build package notes payload for explicit exception workflows."""
    return json.dumps(
        {"exception_workflow": kind.value, "message": message},
        ensure_ascii=True,
        sort_keys=True,
    )
