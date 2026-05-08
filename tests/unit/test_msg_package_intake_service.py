from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from backend.application import MsgPackageIntakeError, MsgPackageIntakeService
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)
from backend.infrastructure.files import IntakeStorage


class PackageStore:
    """In-memory intake package store for service tests."""

    def __init__(self) -> None:
        self.items: dict[str, IntakePackage] = {}

    def create(self, package: IntakePackage) -> IntakePackage:
        self.items[package.package_id] = package
        return package

    def update(self, package: IntakePackage) -> IntakePackage:
        self.items[package.package_id] = package
        return package

    def get(self, package_id: str) -> IntakePackage | None:
        return self.items.get(package_id)

    def list(self) -> list[IntakePackage]:
        return list(self.items.values())

    def delete(self, package_id: str) -> bool:
        return self.items.pop(package_id, None) is not None


class AssetStore:
    """In-memory intake asset store for service tests."""

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

    def delete_by_package(self, package_id: str) -> int:
        keys = [key for key, value in self.items.items() if value.package_id == package_id]
        for key in keys:
            del self.items[key]
        return len(keys)


def _service(
    tmp_path: Path,
    package_store: PackageStore | None = None,
    asset_store: AssetStore | None = None,
) -> MsgPackageIntakeService:
    return MsgPackageIntakeService(
        IntakeStorage(tmp_path / "intake"),
        package_store or PackageStore(),
        asset_store or AssetStore(),
    )


def test_msg_package_import_preserves_email_and_registers_candidate(
    tmp_path: Path,
) -> None:
    package_store = PackageStore()
    asset_store = AssetStore()
    source = _msg_bytes(
        [
            "Subject: Connector qualification request",
            "From: Jane Engineer <jane@example.com>",
            "Attachment: E-3718 Application Form.docx; content=docx bytes",
            "Attachment: drawing.pdf; content=pdf bytes",
        ]
    )

    result = _service(tmp_path, package_store, asset_store).import_msg_package(
        "request.msg", BytesIO(source)
    )

    assert result.package.source_type is IntakePackageSourceType.OUTLOOK_MSG
    assert result.package.status is IntakePackageStatus.READY_FOR_REVIEW
    assert result.package.subject == "Connector qualification request"
    assert result.package.sender_email == "jane@example.com"
    assert result.package.source_stored_path.is_file()
    assert len(result.assets) == 3
    assert [candidate.original_name for candidate in result.candidates] == [
        "E-3718 Application Form.docx"
    ]
    roles = {asset.original_name: asset.asset_role for asset in result.assets}
    assert roles["request.msg"] is IntakeAssetRole.EMAIL_SOURCE
    assert roles["E-3718 Application Form.docx"] is IntakeAssetRole.APPLICATION_FORM_CANDIDATE
    assert roles["drawing.pdf"] is IntakeAssetRole.SUPPORTING_ATTACHMENT


def test_msg_package_import_marks_no_form_package_for_selection(
    tmp_path: Path,
) -> None:
    result = _service(tmp_path).import_msg_package(
        "request.msg",
        BytesIO(
            _msg_bytes(
                [
                    "Subject: Connector qualification request",
                    "From: Jane Engineer <jane@example.com>",
                    "Attachment: drawing.pdf; content=pdf bytes",
                ]
            )
        ),
    )

    assert result.package.status is IntakePackageStatus.NEEDS_APPLICATION_FORM_SELECTION
    assert result.candidates == ()


def test_msg_package_import_allows_same_email_until_draft_identity_is_known(tmp_path: Path) -> None:
    package_store = PackageStore()
    asset_store = AssetStore()
    service = _service(tmp_path, package_store, asset_store)
    source = _msg_bytes(
        [
            "Subject: Connector qualification request",
            "From: Jane Engineer <jane@example.com>",
            "Attachment: drawing.pdf; content=pdf bytes",
        ]
    )
    first = service.import_msg_package("request.msg", BytesIO(source))
    second = service.import_msg_package("request.msg", BytesIO(source))

    assert first.package.package_id != second.package.package_id
    assert first.duplicate_check is None
    assert second.duplicate_check is None


def test_msg_package_import_rejects_import_time_duplicate_resolution(tmp_path: Path) -> None:
    service = _service(tmp_path)
    with pytest.raises(MsgPackageIntakeError):
        service.import_msg_package(
            "request.msg",
            BytesIO(
                _msg_bytes(
                    [
                        "Subject: Connector qualification request",
                        "From: Jane Engineer <jane@example.com>",
                    ]
                )
            ),
            resolution_action="replace_existing",
            resolution_package_id="pkg-existing",
        )


def test_msg_package_import_rejects_non_msg_upload(tmp_path: Path) -> None:
    package_store = PackageStore()
    asset_store = AssetStore()

    with pytest.raises(MsgPackageIntakeError):
        _service(tmp_path, package_store, asset_store).import_msg_package(
            "request.docx", BytesIO(b"word")
        )

    assert package_store.items == {}
    assert asset_store.items == {}


def _msg_bytes(lines: list[str]) -> bytes:
    return "\n".join(lines).encode("utf-8")
