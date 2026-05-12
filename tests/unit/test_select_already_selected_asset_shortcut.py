"""Tests for select_form_asset shortcut when asset already selected (Phase 1.2 fixes).

These tests verify that select_form_asset returns the existing case directly
when the asset is already selected, preventing unnecessary duplicate detection.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from backend.application.intake_form_selection_service import (
    FormSelectionResult,
    IntakeFormSelectionService,
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


def _email_asset() -> IntakeAsset:
    return IntakeAsset(
        asset_id="email-1",
        package_id="pkg-1",
        original_name="email.msg",
        stored_path=Path("email.msg"),
        extension=".msg",
        mime_type="application/vnd.ms-outlook",
        size_bytes=1000,
        sha256="email-hash",
        asset_role=IntakeAssetRole.EMAIL_SOURCE,
    )


def _asset(asset_id: str, role: IntakeAssetRole) -> IntakeAsset:
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
    )


class FakePackageStore:
    def __init__(self, package: IntakePackage) -> None:
        self._package = package

    def get(self, package_id: str) -> IntakePackage | None:
        return self._package if package_id == self._package.package_id else None

    def list(self) -> list[IntakePackage]:
        return [self._package]

    def delete(self, package_id: str) -> bool:
        return True


class FakeAssetStore:
    def __init__(self, *assets: IntakeAsset) -> None:
        self._assets = {a.asset_id: a for a in assets}

    def get(self, asset_id: str) -> IntakeAsset | None:
        return self._assets.get(asset_id)

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        return [a for a in self._assets.values() if a.package_id == package_id]

    def update(self, asset: IntakeAsset) -> IntakeAsset:
        self._assets[asset.asset_id] = asset
        return asset

    def delete_by_package(self, package_id: str) -> int:
        return 0


class FakeCaseStore:
    def __init__(self, *cases: IntakeCase) -> None:
        self._cases = list(cases)

    def create(self, case: IntakeCase) -> IntakeCase:
        self._cases.append(case)
        return case

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [c for c in self._cases if c.package_id == package_id]

    def update(self, case: IntakeCase) -> IntakeCase:
        self._cases = [case if c.case_id == case.case_id else c for c in self._cases]
        return case

    def delete_by_package(self, package_id: str) -> int:
        return 0


class FakeDraftStore:
    def __init__(self, *drafts: IntakeDraft) -> None:
        self._drafts = {d.case_id: d for d in drafts}

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        self._drafts[draft.case_id] = draft
        return draft

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        return self._drafts.get(case_id)

    def update(self, draft: IntakeDraft) -> IntakeDraft:
        self._drafts[draft.case_id] = draft
        return draft

    def delete_by_case(self, case_id: str) -> int:
        if case_id in self._drafts:
            del self._drafts[case_id]
            return 1
        return 0

    def delete_by_package(self, package_id: str) -> int:
        return 0


class FakeEligibilityValidator:
    def evaluate(self, asset: IntakeAsset):
        class Result:
            eligible = True
            message = ""
        return Result()


def _service(
    assets: list[IntakeAsset],
    cases: list[IntakeCase] | None = None,
    drafts: list[IntakeDraft] | None = None,
) -> tuple[IntakeFormSelectionService, FakeAssetStore, FakeCaseStore, FakeDraftStore]:
    package = IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.IMPORTED,
        source_original_name="test.msg",
        source_stored_path=Path("test.msg"),
    )
    package_store = FakePackageStore(package)
    asset_store = FakeAssetStore(*assets)
    case_store = FakeCaseStore(*(cases or []))
    draft_store = FakeDraftStore(*(drafts or []))

    service = IntakeFormSelectionService(
        package_store=package_store,
        asset_store=asset_store,
        case_store=case_store,
        draft_store=draft_store,
        parser=None,
        eligibility_validator=FakeEligibilityValidator(),
    )
    return service, asset_store, case_store, draft_store


class TestSelectAlreadySelectedAssetShortcut:
    """Tests that select_form_asset returns existing case when asset already selected."""

    def test_returns_existing_case_without_re_parsing(self):
        """When asset already selected, return existing case without re-parsing."""
        asset = _asset("asset-a", IntakeAssetRole.SELECTED_APPLICATION_FORM)
        existing_case = IntakeCase(
            case_id="case-a",
            package_id="pkg-1",
            selected_form_asset_id="asset-a",
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        existing_draft = IntakeDraft(
            draft_id="draft-a",
            case_id="case-a",
            parsed_fields_json='{"requester":"Test"}',
        )
        service, asset_store, case_store, draft_store = _service(
            [_email_asset(), asset],
            cases=[existing_case],
            drafts=[existing_draft],
        )

        # Call select_form_asset for already-selected asset
        result = service.select_form_asset("pkg-1", "asset-a")

        # Should return existing case/draft directly
        assert result.case.case_id == "case-a"
        assert result.draft.draft_id == "draft-a"
        assert result.draft.parsed_fields_json == '{"requester":"Test"}'
        assert result.selected_asset.asset_id == "asset-a"

    def test_skips_duplicate_detection_for_already_selected(self):
        """Duplicate detection should be skipped for already-selected asset."""
        # This test verifies the shortcut path is taken, not the duplicate detection path
        asset = _asset("asset-a", IntakeAssetRole.SELECTED_APPLICATION_FORM)
        existing_case = IntakeCase(
            case_id="case-a",
            package_id="pkg-1",
            selected_form_asset_id="asset-a",
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        existing_draft = IntakeDraft(
            draft_id="draft-a",
            case_id="case-a",
            parsed_fields_json="{}",
        )
        service, _, _, _ = _service(
            [_email_asset(), asset],
            cases=[existing_case],
            drafts=[existing_draft],
        )

        # Should complete without raising IntakeDraftDuplicateResolutionRequiredError
        result = service.select_form_asset("pkg-1", "asset-a")

        assert isinstance(result, FormSelectionResult)
        assert result.case.selected_form_asset_id == "asset-a"

    def test_does_not_shortcut_when_replace_explicitly_requested(self):
        """When replace_existing=True, should not take shortcut; enters duplicate resolution."""
        from backend.application.intake_form_selection_service import (
            IntakeDraftDuplicateResolutionRequiredError,
        )

        asset = _asset("asset-a", IntakeAssetRole.SELECTED_APPLICATION_FORM)
        existing_case = IntakeCase(
            case_id="case-a",
            package_id="pkg-1",
            selected_form_asset_id="asset-a",
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        existing_draft = IntakeDraft(
            draft_id="draft-a",
            case_id="case-a",
            parsed_fields_json="{}",
            manual_overrides_json='{"test_item":"Edited"}',
        )
        service, _, case_store, draft_store = _service(
            [_email_asset(), asset],
            cases=[existing_case],
            drafts=[existing_draft],
        )

        # Call with replace_existing=True but no resolution_action
        # Should NOT take shortcut and should raise duplicate resolution error
        with pytest.raises(IntakeDraftDuplicateResolutionRequiredError):
            service.select_form_asset("pkg-1", "asset-a", replace_existing=True)

    def test_reinitializes_when_replace_explicitly_confirmed(self):
        """When replace_existing is confirmed via resolution_action, should reinitialize."""
        asset = _asset("asset-a", IntakeAssetRole.SELECTED_APPLICATION_FORM)
        existing_case = IntakeCase(
            case_id="case-a",
            package_id="pkg-1",
            selected_form_asset_id="asset-a",
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        existing_draft = IntakeDraft(
            draft_id="draft-a",
            case_id="case-a",
            parsed_fields_json="{}",
            manual_overrides_json='{"test_item":"Edited"}',
        )
        service, _, case_store, draft_store = _service(
            [_email_asset(), asset],
            cases=[existing_case],
            drafts=[existing_draft],
        )

        # Call with resolution_action="replace_existing" to confirm intent
        result = service.select_form_asset(
            "pkg-1",
            "asset-a",
            resolution_action="replace_existing",
            resolution_case_id="case-a",
        )

        # Should return the same case but draft should be reinitialized
        assert result.case.case_id == "case-a"
        # Manual overrides should be cleared due to reinitialization
        rebuilt_draft = draft_store.get_by_case("case-a")
        assert rebuilt_draft is not None
        assert rebuilt_draft.manual_overrides_json is None

    def test_does_not_shortcut_for_confirmed_case(self):
        """When case is already confirmed, should create new case instead of shortcut."""
        asset = _asset("asset-a", IntakeAssetRole.SELECTED_APPLICATION_FORM)
        confirmed_case = IntakeCase(
            case_id="case-confirmed",
            package_id="pkg-1",
            selected_form_asset_id="asset-a",
            status=IntakeCaseStatus.CONFIRMED,
            confirmed_project_id="proj-1",
        )
        confirmed_draft = IntakeDraft(
            draft_id="draft-confirmed",
            case_id="case-confirmed",
            parsed_fields_json="{}",
        )
        service, _, case_store, draft_store = _service(
            [_email_asset(), asset],
            cases=[confirmed_case],
            drafts=[confirmed_draft],
        )

        # Call for already-confirmed asset
        result = service.select_form_asset("pkg-1", "asset-a")

        # Should create a new case, not return the confirmed one
        assert result.case.case_id != "case-confirmed"
        assert result.case.confirmed_project_id is None
