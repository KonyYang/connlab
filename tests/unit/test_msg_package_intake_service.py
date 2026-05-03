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
        """Create an empty store."""
        self.items: dict[str, IntakePackage] = {}

    def create(self, package: IntakePackage) -> IntakePackage:
        """Create one package."""
        self.items[package.package_id] = package
        return package

    def update(self, package: IntakePackage) -> IntakePackage:
        """Update one package."""
        self.items[package.package_id] = package
        return package


class AssetStore:
    """In-memory intake asset store for service tests."""

    def __init__(self) -> None:
        """Create an empty store."""
        self.items: dict[str, IntakeAsset] = {}

    def create(self, asset: IntakeAsset) -> IntakeAsset:
        """Create one asset."""
        self.items[asset.asset_id] = asset
        return asset

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        """Return assets for one package."""
        return [asset for asset in self.items.values() if asset.package_id == package_id]

    def update(self, asset: IntakeAsset) -> IntakeAsset:
        """Update one asset."""
        self.items[asset.asset_id] = asset
        return asset


def test_msg_package_import_preserves_email_and_registers_candidate(
    tmp_path: Path,
) -> None:
    """Manual `.msg` import persists source email, attachments, and candidates."""
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

    result = MsgPackageIntakeService(
        IntakeStorage(tmp_path / "intake"),
        package_store,
        asset_store,
    ).import_msg_package("request.msg", BytesIO(source))

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
    assert roles["E-3718 Application Form.docx"] is (
        IntakeAssetRole.APPLICATION_FORM_CANDIDATE
    )
    assert roles["drawing.pdf"] is IntakeAssetRole.SUPPORTING_ATTACHMENT


def test_msg_package_import_marks_no_form_package_for_selection(
    tmp_path: Path,
) -> None:
    """Packages without a form candidate remain traceable for follow-up."""
    result = MsgPackageIntakeService(
        IntakeStorage(tmp_path / "intake"),
        PackageStore(),
        AssetStore(),
    ).import_msg_package(
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


def test_msg_package_import_rejects_non_msg_upload(tmp_path: Path) -> None:
    """Only exported Outlook `.msg` packages are accepted by this task."""
    package_store = PackageStore()
    asset_store = AssetStore()

    with pytest.raises(MsgPackageIntakeError):
        MsgPackageIntakeService(
            IntakeStorage(tmp_path / "intake"),
            package_store,
            asset_store,
        ).import_msg_package("request.docx", BytesIO(b"word"))

    assert package_store.items == {}
    assert asset_store.items == {}


def _msg_bytes(lines: list[str]) -> bytes:
    """Build a fixture-style `.msg` byte stream."""
    return "\n".join(lines).encode("utf-8")
