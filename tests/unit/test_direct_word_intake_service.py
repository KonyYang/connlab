from pathlib import Path

import pytest

from backend.application import DirectWordIntakeError, DirectWordIntakeService
from backend.domain import IntakeAsset, IntakeAssetRole, IntakePackageSourceType, IntakePackageStatus
from backend.infrastructure.files import IntakeStorage


class PackageStore:
    def __init__(self) -> None:
        self.items = {}

    def create(self, package):
        self.items[package.package_id] = package
        return package


class AssetStore:
    def __init__(self) -> None:
        self.items: dict[str, IntakeAsset] = {}

    def create(self, asset: IntakeAsset) -> IntakeAsset:
        self.items[asset.asset_id] = asset
        return asset

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        return [asset for asset in self.items.values() if asset.package_id == package_id]

    def update(self, asset: IntakeAsset) -> IntakeAsset:
        self.items[asset.asset_id] = asset
        return asset


def test_direct_word_import_preserves_source_and_registers_candidate(tmp_path: Path) -> None:
    source = tmp_path / "E-3718 Application Form.docx"
    source.write_bytes(b"fake docx content")
    package_store = PackageStore()
    asset_store = AssetStore()

    result = DirectWordIntakeService(
        IntakeStorage(tmp_path / "intake"),
        package_store,
        asset_store,
    ).import_word_form(source)

    assert result.package.source_type is IntakePackageSourceType.DIRECT_APPLICATION_FORM
    assert result.package.status is IntakePackageStatus.READY_FOR_REVIEW
    assert result.package.source_stored_path.read_bytes() == source.read_bytes()
    assert result.asset.asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE
    assert result.asset.stored_path == result.package.source_stored_path
    assert len(package_store.items) == 1
    assert len(asset_store.items) == 1


def test_direct_word_import_allows_doc_but_keeps_low_score_as_supporting(tmp_path: Path) -> None:
    source = tmp_path / "customer supplied file.doc"
    source.write_bytes(b"fake doc content")

    result = DirectWordIntakeService(
        IntakeStorage(tmp_path / "intake"),
        PackageStore(),
        AssetStore(),
    ).import_word_form(source)

    assert result.asset.extension == ".doc"
    assert result.asset.asset_role is IntakeAssetRole.SUPPORTING_ATTACHMENT


def test_direct_word_import_rejects_non_word_sources(tmp_path: Path) -> None:
    source = tmp_path / "request.pdf"
    source.write_bytes(b"pdf")
    package_store = PackageStore()
    asset_store = AssetStore()

    with pytest.raises(DirectWordIntakeError):
        DirectWordIntakeService(
            IntakeStorage(tmp_path / "intake"),
            package_store,
            asset_store,
        ).import_word_form(source)

    assert package_store.items == {}
    assert asset_store.items == {}
