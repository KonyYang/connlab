"""Download registered intake assets through the backend API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.domain import IntakeAsset


class IntakeAssetDownloadNotFoundError(LookupError):
    """Raised when an intake asset cannot be found for download."""


class IntakeAssetDownloadError(RuntimeError):
    """Raised when the stored file for an intake asset is not available."""


@dataclass(frozen=True, slots=True)
class DownloadableIntakeAsset:
    """Safe download result with path and original filename."""

    path: Path
    filename: str
    media_type: str | None


class IntakeAssetStore(Protocol):
    """Persistence behavior required for intake asset download."""

    def get(self, asset_id: str) -> IntakeAsset | None:
        """Return one intake asset by id."""


class IntakeAssetDownloadService:
    """Retrieve stored intake asset files for browser download."""

    def __init__(self, asset_store: IntakeAssetStore) -> None:
        """Create the download service with repository dependency."""
        self._asset_store = asset_store

    def get_downloadable(self, asset_id: str) -> DownloadableIntakeAsset:
        """Return a safe download descriptor for one registered intake asset."""
        asset = self._asset_store.get(asset_id)
        if asset is None:
            raise IntakeAssetDownloadNotFoundError(
                f"Intake asset not found: {asset_id}"
            )

        if not asset.stored_path.is_file():
            raise IntakeAssetDownloadError(
                f"Stored intake asset file is missing: {asset.original_name}. "
                "The file may have been moved or deleted."
            )

        return DownloadableIntakeAsset(
            path=asset.stored_path,
            filename=asset.original_name,
            media_type=(
                "application/octet-stream"
                if asset.original_name.lower().endswith(".msg")
                else asset.mime_type or "application/octet-stream"
            ),
        )
