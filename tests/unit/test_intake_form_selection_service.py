from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from backend.application.intake_form_selection_service import (
    IntakeFormSelectionService,
    IntakeSelectionError,
    IntakeSelectionNotFoundError,
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


class PackageStore:
    def __init__(self, packages: list[IntakePackage]) -> None:
        self.packages = {package.package_id: package for package in packages}

    def get(self, package_id: str) -> IntakePackage | None:
        return self.packages.get(package_id)


class AssetStore:
    def __init__(self, assets: list[IntakeAsset]) -> None:
        self.assets = {asset.asset_id: asset for asset in assets}

    def get(self, asset_id: str) -> IntakeAsset | None:
        return self.assets.get(asset_id)

    def update(self, asset: IntakeAsset) -> IntakeAsset:
        self.assets[asset.asset_id] = asset
        return asset


class CaseStore:
    def __init__(self, cases: list[IntakeCase] | None = None) -> None:
        self.cases = {case.case_id: case for case in cases or []}

    def create(self, case: IntakeCase) -> IntakeCase:
        self.cases[case.case_id] = case
        return case

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [case for case in self.cases.values() if case.package_id == package_id]

    def update(self, case: IntakeCase) -> IntakeCase:
        self.cases[case.case_id] = case
        return case


class DraftStore:
    def __init__(self, drafts: list[IntakeDraft] | None = None) -> None:
        self.drafts = {draft.draft_id: draft for draft in drafts or []}

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        self.drafts[draft.draft_id] = draft
        return draft

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        return next((draft for draft in self.drafts.values() if draft.case_id == case_id), None)

    def update(self, draft: IntakeDraft) -> IntakeDraft:
        self.drafts[draft.draft_id] = draft
        return draft


def _package() -> IntakePackage:
    return IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="request.msg",
        source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
    )


def _asset(asset_id: str, role: IntakeAssetRole, extension: str = ".docx") -> IntakeAsset:
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=f"{asset_id}{extension}",
        stored_path=Path(f"data/intake/pkg-1/attachments/{asset_id}{extension}"),
        extension=extension,
        mime_type="application/octet-stream",
        size_bytes=100,
        sha256=asset_id * 64,
        asset_role=role,
    )


def _service(
    assets: list[IntakeAsset],
    cases: list[IntakeCase] | None = None,
    drafts: list[IntakeDraft] | None = None,
) -> tuple[IntakeFormSelectionService, AssetStore, CaseStore, DraftStore]:
    asset_store = AssetStore(assets)
    case_store = CaseStore(cases)
    draft_store = DraftStore(drafts)
    return (
        IntakeFormSelectionService(PackageStore([_package()]), asset_store, case_store, draft_store),
        asset_store,
        case_store,
        draft_store,
    )


def test_select_candidate_creates_case_and_empty_draft() -> None:
    service, asset_store, case_store, draft_store = _service(
        [_asset("asset-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE)]
    )

    result = service.select_form_asset("pkg-1", "asset-a")

    assert result.selected_asset.asset_role is IntakeAssetRole.SELECTED_APPLICATION_FORM
    assert asset_store.assets["asset-a"].asset_role is IntakeAssetRole.SELECTED_APPLICATION_FORM
    assert result.case.status is IntakeCaseStatus.NEEDS_REVIEW
    assert result.case.confirmed_project_id is None
    assert result.draft.parsed_fields_json == "{}"
    assert len(case_store.cases) == 1
    assert len(draft_store.drafts) == 1


def test_select_word_asset_without_candidate_role_is_allowed_for_human_override() -> None:
    service, _, _, _ = _service([_asset("asset-a", IntakeAssetRole.SUPPORTING_ATTACHMENT)])

    result = service.select_form_asset("pkg-1", "asset-a")

    assert result.selected_asset.asset_role is IntakeAssetRole.SELECTED_APPLICATION_FORM


def test_selection_updates_existing_case_and_draft() -> None:
    existing_case = IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="old-asset",
        status=IntakeCaseStatus.DRAFT_CREATED,
        confirmed_project_id="project-should-be-cleared",
    )
    existing_draft = IntakeDraft(
        draft_id="draft-1",
        case_id="case-1",
        parsed_fields_json='{"old":true}',
    )
    service, _, case_store, draft_store = _service(
        [_asset("asset-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE)],
        cases=[existing_case],
        drafts=[existing_draft],
    )

    result = service.select_form_asset("pkg-1", "asset-a")

    assert result.case.case_id == "case-1"
    assert result.case.selected_form_asset_id == "asset-a"
    assert result.case.confirmed_project_id is None
    assert case_store.cases["case-1"].status is IntakeCaseStatus.NEEDS_REVIEW
    assert draft_store.drafts["draft-1"].parsed_fields_json == "{}"


def test_selection_rejects_non_word_non_candidate_asset() -> None:
    service, _, _, _ = _service([_asset("asset-a", IntakeAssetRole.UNKNOWN, ".pdf")])

    with pytest.raises(IntakeSelectionError):
        service.select_form_asset("pkg-1", "asset-a")


def test_selection_rejects_missing_package_or_asset() -> None:
    service, _, _, _ = _service([_asset("asset-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE)])

    with pytest.raises(IntakeSelectionNotFoundError):
        service.select_form_asset("missing", "asset-a")
    with pytest.raises(IntakeSelectionNotFoundError):
        service.select_form_asset("pkg-1", "missing")


def test_selection_rejects_asset_from_another_package() -> None:
    foreign_asset = replace(
        _asset("asset-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE),
        package_id="pkg-2",
    )
    service, _, _, _ = _service([foreign_asset])

    with pytest.raises(IntakeSelectionError):
        service.select_form_asset("pkg-1", "asset-a")
