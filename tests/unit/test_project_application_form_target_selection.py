from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from backend.application.project_application_form_target_selection import (
    target_application_form,
)
from backend.domain import FileAsset, FileAssetType


def test_target_prefers_typed_application_form_over_stale_selected_role(
    tmp_path: Path,
) -> None:
    submitted = tmp_path / "Submitted Material"
    submitted.mkdir()
    first = submitted / "first.docx"
    second = submitted / "second.docx"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    assets = [
        _asset(
            "first",
            FileAssetType.ATTACHMENT,
            first,
            role="selected_application_form",
        ),
        _asset(
            "second",
            FileAssetType.APPLICATION_FORM,
            second,
            role="selected_application_form",
        ),
    ]

    selected = target_application_form(submitted, "P1", assets, None)

    assert selected.path == second


def test_target_prefers_typed_application_form_in_latest_collection(
    tmp_path: Path,
) -> None:
    submitted = tmp_path / "Submitted Material"
    submitted.mkdir()
    first = submitted / "first.docx"
    second = submitted / "second.docx"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    store = _CollectionStore(first, second)

    selected = target_application_form(submitted, "P1", [], store)

    assert selected.path == second


def _asset(
    asset_id: str,
    asset_type: FileAssetType,
    path: Path,
    *,
    role: str,
) -> FileAsset:
    return FileAsset(
        asset_id=asset_id,
        project_id="P1",
        asset_type=asset_type,
        path=path,
        original_name=path.name,
        source_role=role,
    )


class _CollectionStore:
    def __init__(self, first: Path, second: Path) -> None:
        self._first = first
        self._second = second

    def latest_by_project(self, project_id: str) -> object:
        return SimpleNamespace(collection_id="collection-1")

    def list_items(self, collection_id: str) -> tuple[object, ...]:
        return (
            self._item("first", "attachment", self._first),
            self._item("second", "application_form", self._second),
        )

    @staticmethod
    def _item(asset_id: str, asset_type: str, path: Path) -> object:
        return SimpleNamespace(
            source_asset_id=asset_id,
            source_asset_type=asset_type,
            source_role="selected_application_form",
            source_path=path,
            target_area="submitted_material",
            target_path=path,
            sha256=None,
        )
