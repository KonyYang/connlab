from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.project_creation_draft_lifecycle_service import (
    ProjectCreationDraftLifecycleError,
    ProjectCreationDraftLifecycleService,
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


def test_discard_unsaved_creation_draft_removes_records_and_files(tmp_path: Path) -> None:
    """Discard removes only the unsaved package graph and its storage directory."""
    storage = IntakeStorage(tmp_path / "intake")
    stores = _stores(tmp_path, storage)
    service = _service(storage, stores)

    result = service.discard_unsaved("pkg-1")

    assert result.deleted_package is True
    assert result.deleted_assets == 1
    assert result.deleted_cases == 1
    assert result.deleted_drafts == 1
    assert result.deleted_files is True
    assert stores["packages"].items == {}
    assert not storage.package_root("pkg-1").exists()


def test_saved_creation_draft_is_not_removed_by_unsaved_discard(tmp_path: Path) -> None:
    """Saved drafts are protected from the unsaved-session discard path."""
    storage = IntakeStorage(tmp_path / "intake")
    stores = _stores(tmp_path, storage)
    service = _service(storage, stores)

    saved = service.save_draft("pkg-1")
    assert saved.package_status == "draft_saved"

    with pytest.raises(ProjectCreationDraftLifecycleError):
        service.discard_unsaved("pkg-1")

    assert stores["packages"].items["pkg-1"].status is IntakePackageStatus.DRAFT_SAVED
    assert storage.package_root("pkg-1").exists()


def test_confirmed_case_blocks_creation_draft_lifecycle_actions(tmp_path: Path) -> None:
    """A package that already created a project cannot be saved or discarded."""
    storage = IntakeStorage(tmp_path / "intake")
    stores = _stores(tmp_path, storage)
    stores["cases"].items["case-1"] = IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="asset-1",
        status=IntakeCaseStatus.CONFIRMED,
        confirmed_project_id="project-1",
    )
    service = _service(storage, stores)

    with pytest.raises(ProjectCreationDraftLifecycleError):
        service.save_draft("pkg-1")
    with pytest.raises(ProjectCreationDraftLifecycleError):
        service.discard_unsaved("pkg-1")


class PackageStore:
    """In-memory package store for lifecycle service unit tests."""

    def __init__(self, package: IntakePackage) -> None:
        self.items = {package.package_id: package}

    def get(self, package_id: str) -> IntakePackage | None:
        return self.items.get(package_id)

    def update(self, package: IntakePackage) -> IntakePackage:
        self.items[package.package_id] = package
        return package

    def delete(self, package_id: str) -> bool:
        return self.items.pop(package_id, None) is not None


class AssetStore:
    """In-memory asset store for lifecycle service unit tests."""

    def __init__(self, asset: IntakeAsset) -> None:
        self.items = {asset.asset_id: asset}

    def delete_by_package(self, package_id: str) -> int:
        removed = [
            asset_id
            for asset_id, asset in self.items.items()
            if asset.package_id == package_id
        ]
        for asset_id in removed:
            del self.items[asset_id]
        return len(removed)


class CaseStore:
    """In-memory case store for lifecycle service unit tests."""

    def __init__(self, case: IntakeCase) -> None:
        self.items = {case.case_id: case}

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [case for case in self.items.values() if case.package_id == package_id]

    def delete_by_package(self, package_id: str) -> int:
        removed = [
            case_id for case_id, case in self.items.items() if case.package_id == package_id
        ]
        for case_id in removed:
            del self.items[case_id]
        return len(removed)


class DraftStore:
    """In-memory draft store for lifecycle service unit tests."""

    def __init__(self, draft: IntakeDraft, case_package_ids: dict[str, str]) -> None:
        self.items = {draft.draft_id: draft}
        self.case_package_ids = case_package_ids

    def delete_by_package(self, package_id: str) -> int:
        removed = [
            draft_id
            for draft_id, draft in self.items.items()
            if self.case_package_ids.get(draft.case_id) == package_id
        ]
        for draft_id in removed:
            del self.items[draft_id]
        return len(removed)


def _stores(tmp_path: Path, storage: IntakeStorage) -> dict[str, object]:
    """Create linked in-memory package records and one stored file."""
    package_dir = storage.package_root("pkg-1")
    package_dir.mkdir(parents=True)
    stored_file = package_dir / "manual_intake.json"
    stored_file.write_text("{}", encoding="utf-8")
    return {
        "packages": PackageStore(
            IntakePackage(
                package_id="pkg-1",
                source_type=IntakePackageSourceType.MANUAL,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name="manual_intake.json",
                source_stored_path=stored_file,
            )
        ),
        "assets": AssetStore(
            IntakeAsset(
                asset_id="asset-1",
                package_id="pkg-1",
                original_name="manual_intake.json",
                stored_path=stored_file,
                extension=".json",
                mime_type="application/json",
                size_bytes=2,
                sha256="0" * 64,
                asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
            )
        ),
        "cases": CaseStore(
            IntakeCase(
                case_id="case-1",
                package_id="pkg-1",
                selected_form_asset_id="asset-1",
                status=IntakeCaseStatus.NEEDS_REVIEW,
            )
        ),
        "drafts": DraftStore(
            IntakeDraft(
                draft_id="draft-1",
                case_id="case-1",
                parsed_fields_json="{}",
            ),
            {"case-1": "pkg-1"},
        ),
    }


def _service(
    storage: IntakeStorage,
    stores: dict[str, object],
) -> ProjectCreationDraftLifecycleService:
    """Build the lifecycle service from in-memory stores."""
    return ProjectCreationDraftLifecycleService(
        storage=storage,
        package_store=stores["packages"],
        asset_store=stores["assets"],
        case_store=stores["cases"],
        draft_store=stores["drafts"],
    )
