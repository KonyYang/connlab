from __future__ import annotations

from pathlib import Path

import pytest

from backend.application import (
    IntakePackageQueryNotFoundError,
    IntakePackageQueryService,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)


class PackageStore:
    """In-memory package read store."""

    def __init__(self, packages: list[IntakePackage]) -> None:
        """Create the store."""
        self.items = {package.package_id: package for package in packages}

    def get(self, package_id: str) -> IntakePackage | None:
        """Return one package."""
        return self.items.get(package_id)


class AssetStore:
    """In-memory asset read store."""

    def __init__(self, assets: list[IntakeAsset]) -> None:
        """Create the store."""
        self.items = assets

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        """Return package assets."""
        return [asset for asset in self.items if asset.package_id == package_id]


class CaseStore:
    """In-memory case read store."""

    def __init__(self, cases: list[IntakeCase]) -> None:
        """Create the store."""
        self.items = cases

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        """Return package cases."""
        return [case for case in self.items if case.package_id == package_id]


def test_query_service_returns_package_assets_candidates_and_cases() -> None:
    """Package detail includes source metadata, candidates, and created cases."""
    service = IntakePackageQueryService(
        PackageStore([_package()]),
        AssetStore(
            [
                _asset("email", "request.msg", IntakeAssetRole.EMAIL_SOURCE),
                _asset("form", "Application Form.docx", IntakeAssetRole.APPLICATION_FORM_CANDIDATE),
                _asset("spec", "drawing.pdf", IntakeAssetRole.SUPPORTING_ATTACHMENT),
            ]
        ),
        CaseStore([_case()]),
    )

    detail = service.get_detail("pkg-1")

    assert detail.package.package_id == "pkg-1"
    assert len(detail.assets) == 3
    assert [asset.asset_id for asset in detail.candidate_assets] == ["form"]
    assert [case.case_id for case in detail.cases] == ["case-1"]


def test_query_service_raises_for_missing_package() -> None:
    """Missing packages fail clearly."""
    service = IntakePackageQueryService(PackageStore([]), AssetStore([]), CaseStore([]))

    with pytest.raises(IntakePackageQueryNotFoundError):
        service.get_detail("missing")


def _package() -> IntakePackage:
    """Return a package."""
    return IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="request.msg",
        source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
        subject="Request",
    )


def _asset(asset_id: str, name: str, role: IntakeAssetRole) -> IntakeAsset:
    """Return an asset."""
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=name,
        stored_path=Path(f"data/intake/pkg-1/attachments/{name}"),
        extension=Path(name).suffix,
        mime_type="application/octet-stream",
        size_bytes=100,
        sha256="a" * 64,
        asset_role=role,
        candidate_score=80 if role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE else None,
    )


def _case() -> IntakeCase:
    """Return a case."""
    return IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="form",
        status=IntakeCaseStatus.NEEDS_REVIEW,
    )
