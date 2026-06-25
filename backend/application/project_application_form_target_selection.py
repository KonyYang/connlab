"""Select the copied Application Form target inside Submitted Material."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.project_application_form_write_back_support import sha256_file
from backend.application.project_request_material_collection_helpers import (
    safe_material_filename,
)
from backend.domain import FileAsset, FileAssetType


class RequestMaterialCollectionStore(Protocol):
    """Request-material collection lookup port."""

    def latest_by_project(self, project_id: str) -> object | None:
        """Return the latest request-material collection run."""

    def list_items(self, collection_id: str) -> tuple[object, ...]:
        """Return persisted request-material items for one collection run."""


@dataclass(frozen=True, slots=True)
class SelectedApplicationFormTarget:
    """Selected copied Application Form target and source fingerprint."""

    path: Path
    source_sha256: str | None = None


class ApplicationFormTargetSelectionError(ValueError):
    """Raised when the copied Application Form target cannot be selected."""


def target_application_form(
    submitted_material: Path,
    project_id: str,
    assets: list[FileAsset],
    collection_store: RequestMaterialCollectionStore | None,
) -> SelectedApplicationFormTarget:
    """Return the selected copied Application Form target."""
    from_collection = _target_from_latest_collection(
        submitted_material,
        project_id,
        collection_store,
    )
    if from_collection is not None:
        return from_collection
    selected = [
        asset
        for asset in assets
        if asset.asset_type is FileAssetType.APPLICATION_FORM
        or (asset.source_role or "").casefold() == "selected_application_form"
    ]
    if selected:
        name = safe_material_filename(
            selected[0].original_name or selected[0].path.name,
            selected[0].asset_id,
        )
        target = submitted_material / name
        if target.is_file():
            return SelectedApplicationFormTarget(
                path=target,
                source_sha256=_source_asset_sha256(selected[0], target),
            )
    candidates = sorted(submitted_material.glob("*.docx"))
    candidates = [path for path in candidates if ".bak-" not in path.name]
    if len(candidates) == 1:
        return SelectedApplicationFormTarget(path=candidates[0])
    if not candidates:
        raise ApplicationFormTargetSelectionError(
            f"No Application Form .docx found in Submitted Material: {submitted_material}"
        )
    raise ApplicationFormTargetSelectionError(
        "Multiple .docx files exist in Submitted Material. Cannot choose the Application Form automatically."
    )


def _target_from_latest_collection(
    submitted_material: Path,
    project_id: str,
    collection_store: RequestMaterialCollectionStore | None,
) -> SelectedApplicationFormTarget | None:
    if collection_store is None:
        return None
    collection = collection_store.latest_by_project(project_id)
    collection_id = getattr(collection, "collection_id", None)
    if not collection_id:
        return None
    for item in collection_store.list_items(collection_id):
        if getattr(item, "target_area", None) != "submitted_material":
            continue
        source_type = str(getattr(item, "source_asset_type", "") or "").casefold()
        source_role = str(getattr(item, "source_role", "") or "").casefold()
        if source_type != FileAssetType.APPLICATION_FORM.value and (
            source_role != "selected_application_form"
        ):
            continue
        target_path = Path(getattr(item, "target_path"))
        if not _is_direct_child(target_path, submitted_material) or not target_path.is_file():
            continue
        return SelectedApplicationFormTarget(
            path=target_path,
            source_sha256=_collection_source_sha256(item, target_path),
        )
    return None


def _is_direct_child(path: Path, folder: Path) -> bool:
    try:
        return path.parent.resolve() == folder.resolve()
    except OSError:
        return path.parent == folder


def _collection_source_sha256(item: object, target: Path) -> str | None:
    sha = getattr(item, "sha256", None)
    if sha:
        return str(sha)
    source_path = Path(getattr(item, "source_path", ""))
    try:
        if source_path.resolve() == target.resolve():
            return None
    except OSError:
        if source_path == target:
            return None
    return sha256_file(source_path) if source_path.is_file() else None


def _source_asset_sha256(asset: FileAsset, target: Path) -> str | None:
    if asset.sha256:
        return asset.sha256
    try:
        if asset.path.resolve() == target.resolve():
            return None
    except OSError:
        if asset.path == target:
            return None
    return sha256_file(asset.path) if asset.path.is_file() else None
