from __future__ import annotations

import json
from pathlib import Path

from backend.application.exception_workflow_service import (
    ExceptionWorkflowKind,
    ExceptionWorkflowService,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)


def test_no_application_form_marks_package_for_follow_up() -> None:
    package_store = _PackageStore([_package()])
    service = _service(
        package_store=package_store,
        assets=[_asset("spec-1", IntakeAssetRole.SPECIFICATION, ".pdf")],
    )

    review = service.review_package("pkg-1")

    assert review.package.status is IntakePackageStatus.NEEDS_APPLICATION_FORM_SELECTION
    assert review.issues[0].kind is ExceptionWorkflowKind.NO_APPLICATION_FORM
    assert review.issues[0].blocking is True
    notes = json.loads(package_store.packages["pkg-1"].notes or "{}")
    assert notes["exception_workflow"] == "no_application_form"
    assert review.cases == ()


def test_multiple_application_forms_create_separate_cases_and_drafts() -> None:
    service = _service(
        assets=[
            _asset("form-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE),
            _asset("form-b", IntakeAssetRole.APPLICATION_FORM_CANDIDATE),
        ]
    )

    review = service.review_package("pkg-1")

    assert [issue.kind for issue in review.issues] == [
        ExceptionWorkflowKind.MULTIPLE_APPLICATION_FORMS,
        ExceptionWorkflowKind.MULTIPLE_APPLICATION_FORMS,
    ]
    assert len(review.cases) == 2
    assert len({case.selected_form_asset_id for case in review.cases}) == 2
    assert all(case.status is IntakeCaseStatus.NEEDS_REVIEW for case in review.cases)
    assert len(review.drafts) == 2
    assert all("Multiple application forms" in (draft.parser_warnings_json or "") for draft in review.drafts)


def test_existing_case_for_candidate_is_reused() -> None:
    case = IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="form-a",
        status=IntakeCaseStatus.NEEDS_REVIEW,
    )
    draft = IntakeDraft(
        draft_id="draft-1",
        case_id="case-1",
        parsed_fields_json="{}",
    )
    service = _service(
        assets=[_asset("form-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE)],
        cases=[case],
        drafts=[draft],
    )

    review = service.review_package("pkg-1")

    assert review.cases == (case,)
    assert review.drafts == (draft,)


def _service(
    *,
    assets: list[IntakeAsset],
    package_store: "_PackageStore | None" = None,
    cases: list[IntakeCase] | None = None,
    drafts: list[IntakeDraft] | None = None,
) -> ExceptionWorkflowService:
    """Create a service with in-memory stores."""
    return ExceptionWorkflowService(
        package_store=package_store or _PackageStore([_package()]),
        asset_store=_AssetStore(assets),
        case_store=_CaseStore(cases or []),
        draft_store=_DraftStore(drafts or []),
    )


def _package() -> IntakePackage:
    """Return a test intake package."""
    return IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="request.msg",
        source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
    )


def _asset(
    asset_id: str,
    role: IntakeAssetRole,
    extension: str = ".docx",
) -> IntakeAsset:
    """Return a test intake asset."""
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=f"{asset_id}{extension}",
        stored_path=Path(f"data/intake/pkg-1/attachments/{asset_id}{extension}"),
        extension=extension,
        mime_type="application/octet-stream",
        size_bytes=100,
        sha256=asset_id * 16,
        asset_role=role,
    )


class _PackageStore:
    """In-memory package store."""

    def __init__(self, packages: list[IntakePackage]) -> None:
        """Create a store."""
        self.packages = {package.package_id: package for package in packages}

    def get(self, package_id: str) -> IntakePackage | None:
        """Return a package."""
        return self.packages.get(package_id)

    def update(self, package: IntakePackage) -> IntakePackage:
        """Update a package."""
        self.packages[package.package_id] = package
        return package


class _AssetStore:
    """In-memory asset store."""

    def __init__(self, assets: list[IntakeAsset]) -> None:
        """Create a store."""
        self.assets = assets

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        """Return assets for a package."""
        return [asset for asset in self.assets if asset.package_id == package_id]


class _CaseStore:
    """In-memory case store."""

    def __init__(self, cases: list[IntakeCase]) -> None:
        """Create a store."""
        self.cases = {case.case_id: case for case in cases}

    def create(self, case: IntakeCase) -> IntakeCase:
        """Create a case."""
        self.cases[case.case_id] = case
        return case

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        """Return cases for a package."""
        return [case for case in self.cases.values() if case.package_id == package_id]


class _DraftStore:
    """In-memory draft store."""

    def __init__(self, drafts: list[IntakeDraft]) -> None:
        """Create a store."""
        self.drafts = {draft.draft_id: draft for draft in drafts}

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        """Create a draft."""
        self.drafts[draft.draft_id] = draft
        return draft

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        """Return a draft by case."""
        return next(
            (draft for draft in self.drafts.values() if draft.case_id == case_id),
            None,
        )
