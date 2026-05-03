from __future__ import annotations

import json
from pathlib import Path

from backend.application import (
    ManualIntakeInput,
    ManualIntakeService,
    ManualSampleInput,
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
from backend.infrastructure.files import IntakeStorage


class PackageStore:
    """In-memory package store."""

    def __init__(self) -> None:
        """Create an empty store."""
        self.items: dict[str, IntakePackage] = {}

    def create(self, package: IntakePackage) -> IntakePackage:
        """Create one package."""
        self.items[package.package_id] = package
        return package


class AssetStore:
    """In-memory asset store."""

    def __init__(self) -> None:
        """Create an empty store."""
        self.items: dict[str, IntakeAsset] = {}

    def create(self, asset: IntakeAsset) -> IntakeAsset:
        """Create one asset."""
        self.items[asset.asset_id] = asset
        return asset


class CaseStore:
    """In-memory case store."""

    def __init__(self) -> None:
        """Create an empty store."""
        self.items: dict[str, IntakeCase] = {}

    def create(self, case: IntakeCase) -> IntakeCase:
        """Create one case."""
        self.items[case.case_id] = case
        return case


class DraftStore:
    """In-memory draft store."""

    def __init__(self) -> None:
        """Create an empty store."""
        self.items: dict[str, IntakeDraft] = {}

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        """Create one draft."""
        self.items[draft.draft_id] = draft
        return draft


def test_manual_intake_creates_review_case_without_project(tmp_path: Path) -> None:
    """Manual no-email intake creates package, asset, case, and draft records."""
    result = _service(tmp_path).create_manual_case(
        ManualIntakeInput(
            product_name="Connector sample",
            requester="White",
            email="white@example.com",
            business_unit="DGLAB",
            requested_testing="Qualification",
            sample=ManualSampleInput(part_number="PN-001", quantity=3),
        )
    )

    assert result.package.source_type is IntakePackageSourceType.MANUAL
    assert result.package.status is IntakePackageStatus.READY_FOR_REVIEW
    assert result.package.source_stored_path.is_file()
    assert result.asset.asset_role is IntakeAssetRole.SELECTED_APPLICATION_FORM
    assert result.asset.stored_path == result.package.source_stored_path
    assert result.case.status is IntakeCaseStatus.NEEDS_REVIEW
    assert result.case.selected_form_asset_id == result.asset.asset_id
    assert result.missing_required_fields == ()
    draft = json.loads(result.draft.parsed_fields_json)
    assert draft["product_name"] == "Connector sample"
    assert draft["requester"] == "White"
    assert draft["samples"][0]["part_number"] == "PN-001"


def test_manual_intake_records_missing_required_fields(tmp_path: Path) -> None:
    """Blank manual intake can be saved but reports confirmation blockers."""
    result = _service(tmp_path).create_manual_case(
        ManualIntakeInput(product_name="", requester=None)
    )

    assert result.missing_required_fields == ("product_name", "requester")
    assert result.case.reviewer_notes == "Missing required fields: product_name, requester"


def _service(tmp_path: Path) -> ManualIntakeService:
    """Build a manual intake service with in-memory stores."""
    return ManualIntakeService(
        IntakeStorage(tmp_path / "intake"),
        PackageStore(),
        AssetStore(),
        CaseStore(),
        DraftStore(),
    )
