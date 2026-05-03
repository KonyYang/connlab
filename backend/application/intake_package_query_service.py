from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.domain import IntakeAsset, IntakeAssetRole, IntakeCase, IntakePackage


class IntakePackageQueryNotFoundError(LookupError):
    """Raised when an intake package detail record cannot be found."""


class IntakePackageStore(Protocol):
    """Read port for intake packages."""

    def get(self, package_id: str) -> IntakePackage | None: ...


class IntakeAssetStore(Protocol):
    """Read port for intake package assets."""

    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...


class IntakeCaseStore(Protocol):
    """Read port for intake cases."""

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...


@dataclass(frozen=True)
class IntakePackageDetail:
    """Read model for one intake package detail page."""

    package: IntakePackage
    assets: tuple[IntakeAsset, ...]
    candidate_assets: tuple[IntakeAsset, ...]
    cases: tuple[IntakeCase, ...]


class IntakePackageQueryService:
    """Loads intake package metadata, assets, candidates, and cases."""

    _candidate_roles = {
        IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        IntakeAssetRole.SELECTED_APPLICATION_FORM,
    }

    def __init__(
        self,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
    ) -> None:
        """Create the query service from explicit read ports."""
        self._packages = package_store
        self._assets = asset_store
        self._cases = case_store

    def get_detail(self, package_id: str) -> IntakePackageDetail:
        """Return detail data for one intake package."""
        package = self._packages.get(package_id)
        if package is None:
            raise IntakePackageQueryNotFoundError(f"Intake package not found: {package_id}")
        assets = tuple(self._assets.list_by_package(package.package_id))
        candidate_assets = tuple(
            asset for asset in assets if asset.asset_role in self._candidate_roles
        )
        return IntakePackageDetail(
            package=package,
            assets=assets,
            candidate_assets=candidate_assets,
            cases=tuple(self._cases.list_by_package(package.package_id)),
        )
