from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.new_project_application_draft_service import (
    NewProjectApplicationDraftNotFoundError,
    NewProjectApplicationDraftService,
)
from backend.application.intake_form_selection_service import FormSelectionResult
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


class PackageStore:
    """In-memory package persistence for draft service tests."""

    def __init__(self, package: IntakePackage | None = None) -> None:
        self.items = {package.package_id: package} if package else {}

    def get(self, package_id: str) -> IntakePackage | None:
        return self.items.get(package_id)

    def update(self, package: IntakePackage) -> IntakePackage:
        self.items[package.package_id] = package
        return package


class CaseStore:
    """In-memory case persistence for draft service tests."""

    def __init__(self, *cases: IntakeCase) -> None:
        self.items = list(cases)

    def create(self, case: IntakeCase) -> IntakeCase:
        self.items.append(case)
        return case

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [case for case in self.items if case.package_id == package_id]

    def update(self, case: IntakeCase) -> IntakeCase:
        self.items = [case if item.case_id == case.case_id else item for item in self.items]
        return case


class AssetStore:
    """In-memory asset persistence for draft service tests."""

    def __init__(self, *assets: IntakeAsset) -> None:
        self.items = list(assets)

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        return [asset for asset in self.items if asset.package_id == package_id]


class DraftStore:
    """In-memory draft persistence for draft service tests."""

    def __init__(self, *drafts: IntakeDraft) -> None:
        self.items = {draft.case_id: draft for draft in drafts}

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        self.items[draft.case_id] = draft
        return draft

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        return self.items.get(case_id)


class SelectionService:
    """Fake selection service for draft service tests."""

    def __init__(self) -> None:
        self.selected_asset_ids: list[str] = []

    def select_form_asset(
        self,
        package_id: str,
        asset_id: str,
        replace_existing: bool = False,
    ) -> FormSelectionResult:
        self.selected_asset_ids.append(asset_id)
        case = IntakeCase(
            case_id="case-selected",
            package_id=package_id,
            selected_form_asset_id=asset_id,
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        draft = IntakeDraft(
            draft_id="draft-selected",
            case_id=case.case_id,
            parsed_fields_json='{"requester":"Imported"}',
        )
        selected_asset = IntakeAsset(
            asset_id=asset_id,
            package_id=package_id,
            original_name=f"{asset_id}.docx",
            stored_path=Path(f"{asset_id}.docx"),
            extension=".docx",
            mime_type="application/octet-stream",
            size_bytes=10,
            sha256="a" * 64,
            asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
        )
        return FormSelectionResult(
            package_id=package_id,
            case=case,
            draft=draft,
            selected_asset=selected_asset,
        )


def test_ensure_draft_creates_blank_case_for_email_package(tmp_path: Path) -> None:
    """TASK_102 can open a blank durable editor for an imported email package."""
    package_store = PackageStore(_package(tmp_path))
    case_store = CaseStore()
    draft_store = DraftStore()
    service = NewProjectApplicationDraftService(package_store, case_store, draft_store)

    result = service.ensure_draft("pkg-1")

    assert result.package.status is IntakePackageStatus.READY_FOR_REVIEW
    assert result.case.package_id == "pkg-1"
    assert result.case.selected_form_asset_id is None
    assert result.case.status is IntakeCaseStatus.NEEDS_REVIEW
    assert result.draft.case_id == result.case.case_id
    assert result.draft.parsed_fields_json == "{}"


def test_ensure_draft_reuses_existing_unconfirmed_case(tmp_path: Path) -> None:
    """Existing draft edits are not replaced when the single page reopens."""
    package = _package(tmp_path)
    case = IntakeCase(
        case_id="case-1",
        package_id=package.package_id,
        selected_form_asset_id=None,
        status=IntakeCaseStatus.DRAFT_CREATED,
    )
    draft = IntakeDraft(
        draft_id="draft-1",
        case_id=case.case_id,
        parsed_fields_json="{}",
        manual_overrides_json='{"requester": "White"}',
    )
    service = NewProjectApplicationDraftService(
        PackageStore(package),
        CaseStore(case),
        DraftStore(draft),
    )

    result = service.ensure_draft(package.package_id)

    assert result.case.case_id == "case-1"
    assert result.draft.draft_id == "draft-1"
    assert result.draft.manual_overrides_json == '{"requester": "White"}'


def test_ensure_draft_raises_for_missing_package() -> None:
    """Unknown package IDs fail before creating orphan draft records."""
    service = NewProjectApplicationDraftService(PackageStore(), CaseStore(), DraftStore())

    with pytest.raises(NewProjectApplicationDraftNotFoundError):
        service.ensure_draft("missing")


def test_ensure_draft_defaults_to_first_application_form_candidate(tmp_path: Path) -> None:
    """The single-page editor opens on the strongest form candidate by default."""
    package = _package(tmp_path)
    first = _asset("asset-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE, score=60)
    second = _asset("asset-b", IntakeAssetRole.APPLICATION_FORM_CANDIDATE, score=90)
    selection_service = SelectionService()
    service = NewProjectApplicationDraftService(
        PackageStore(package),
        CaseStore(),
        DraftStore(),
        AssetStore(first, second),
        selection_service,
    )

    result = service.ensure_draft(package.package_id)

    assert result.case.selected_form_asset_id == "asset-a"
    assert result.draft.case_id == result.case.case_id
    assert selection_service.selected_asset_ids == ["asset-a"]


def _package(tmp_path: Path) -> IntakePackage:
    return IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.IMPORTED,
        source_original_name="request.msg",
        source_stored_path=tmp_path / "request.msg",
    )


def _asset(
    asset_id: str,
    role: IntakeAssetRole,
    *,
    score: int | None = None,
) -> IntakeAsset:
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=f"{asset_id}.docx",
        stored_path=Path(f"{asset_id}.docx"),
        extension=".docx",
        mime_type="application/octet-stream",
        size_bytes=10,
        sha256=asset_id * 64,
        asset_role=role,
        candidate_score=score,
    )
