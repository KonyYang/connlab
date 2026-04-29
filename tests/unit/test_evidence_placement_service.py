from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.evidence_placement_service import (
    EvidencePlacementConflictError,
    EvidencePlacementService,
)
from backend.domain import FileAsset, FileAssetType, Project, ProjectFolderRecord
from backend.modules.folder import EvidencePlacementCategory


def test_evidence_preview_places_assets_in_real_project_shape(tmp_path: Path) -> None:
    project_folder = _create_real_style_project_folder(tmp_path)
    sources = tmp_path / "sources"
    sources.mkdir()
    email = _touch(sources / "DL-2025-09-054 request.msg")
    form = _touch(sources / "E-3718_H Laboratory Test Request-Even.docx")
    spec = _touch(sources / "customer_specification.pdf")
    photo = _touch(sources / "sample_photo.jpg")
    ltr = _touch(sources / "ltr_commit_audit.json")
    correction = _touch(sources / "corrected_request.docx")
    service = _service(
        tmp_path,
        project_folder,
        [
            _asset("email", FileAssetType.ATTACHMENT, email),
            _asset("form", FileAssetType.APPLICATION_FORM, form),
            _asset("spec", FileAssetType.ATTACHMENT, spec),
            _asset("photo", FileAssetType.ATTACHMENT, photo),
            _asset("ltr", FileAssetType.LTR, ltr),
            _asset("correction", FileAssetType.ATTACHMENT, correction),
        ],
    )

    plan = service.preview_project("project-1")
    by_id = {item.asset_id: item for item in plan.items}

    assert plan.conflict is False
    assert plan.evidence_root_path.name.startswith("DL-2025-09-054 ")
    assert by_id["email"].category is EvidencePlacementCategory.EMAIL
    assert by_id["email"].target_path.parent.name == "E-mail"
    assert by_id["form"].target_path.parent.name == "Submitted Material"
    assert by_id["spec"].target_path.parent.name == "Specifications"
    assert by_id["photo"].target_path.parent.name == "Photos"
    assert by_id["ltr"].target_path.parent.name == "LTR Evidence"
    assert by_id["correction"].target_path.parent.name == "Corrections"


def test_evidence_place_copies_without_overwrite(tmp_path: Path) -> None:
    project_folder = _create_real_style_project_folder(tmp_path)
    source = _touch(tmp_path / "sources" / "request.msg")
    service = _service(
        tmp_path,
        project_folder,
        [_asset("email", FileAssetType.ATTACHMENT, source)],
    )

    result = service.place_project("project-1")

    assert len(result.copied_paths) == 1
    assert result.copied_paths[0].read_text(encoding="utf-8") == "evidence"
    with pytest.raises(EvidencePlacementConflictError):
        service.place_project("project-1")


def test_evidence_preview_blocks_missing_sources_and_duplicate_targets(
    tmp_path: Path,
) -> None:
    project_folder = _create_real_style_project_folder(tmp_path)
    missing = tmp_path / "sources" / "missing.pdf"
    source = _touch(tmp_path / "sources" / "same.pdf")
    service = _service(
        tmp_path,
        project_folder,
        [
            _asset("missing", FileAssetType.ATTACHMENT, missing),
            _asset("a", FileAssetType.ATTACHMENT, source, original_name="same.pdf"),
            _asset("b", FileAssetType.ATTACHMENT, source, original_name="same.pdf"),
        ],
    )

    plan = service.preview_project("project-1")

    assert plan.conflict is True
    assert any(item.missing_source for item in plan.items)
    assert sum(item.duplicate_target for item in plan.items) == 2


def test_corrected_evidence_is_placed_without_deleting_original_evidence(
    tmp_path: Path,
) -> None:
    project_folder = _create_real_style_project_folder(tmp_path)
    original = _touch(tmp_path / "sources" / "request.docx")
    corrected = _touch(tmp_path / "sources" / "corrected_request.docx")
    service = _service(
        tmp_path,
        project_folder,
        [
            _asset("original", FileAssetType.APPLICATION_FORM, original),
            _asset("corrected", FileAssetType.ATTACHMENT, corrected),
        ],
    )

    result = service.place_project("project-1")

    copied_names = {path.name for path in result.copied_paths}
    assert copied_names == {"request.docx", "corrected_request.docx"}
    assert (project_folder / "DL-2025-09-054 EK550A Qualification Testing" / "Submitted Material" / "request.docx").is_file()
    assert (
        project_folder
        / "DL-2025-09-054 EK550A Qualification Testing"
        / "Submitted Material"
        / "Corrections"
        / "corrected_request.docx"
    ).is_file()


def _service(
    tmp_path: Path,
    folder_path: Path,
    assets: list[FileAsset],
) -> EvidencePlacementService:
    """Create an evidence placement service backed by in-memory repositories."""
    return EvidencePlacementService(
        project_repository=_ProjectRepo(),
        folder_repository=_FolderRepo(folder_path),
        file_asset_repository=_AssetRepo(assets),
    )


def _create_real_style_project_folder(tmp_path: Path) -> Path:
    """Create a minimal real-sample-like generated project folder."""
    project_folder = tmp_path / "DL-2025-09-054"
    title = project_folder / "DL-2025-09-054 EK550A Qualification Testing"
    for child in (
        title / "E-mail",
        title / "Photos",
        title / "Submitted Material",
        title / "Test results",
        project_folder / "Source Book",
    ):
        child.mkdir(parents=True)
    return project_folder


def _touch(path: Path) -> Path:
    """Create a small evidence file for tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("evidence", encoding="utf-8")
    return path


def _asset(
    asset_id: str,
    asset_type: FileAssetType,
    path: Path,
    original_name: str | None = None,
) -> FileAsset:
    """Build a project file asset for tests."""
    return FileAsset(
        asset_id=asset_id,
        project_id="project-1",
        asset_type=asset_type,
        path=path,
        original_name=original_name,
    )


class _ProjectRepo:
    """In-memory project repository for evidence tests."""

    def get(self, project_id: str) -> Project | None:
        """Return a fixed project."""
        return Project(
            project_id=project_id,
            project_no="PRJ-1",
            product_name="Connector",
            requestor="Alice",
        )


class _FolderRepo:
    """In-memory folder repository for evidence tests."""

    def __init__(self, folder_path: Path) -> None:
        """Create a fixed folder repository."""
        self._folder_path = folder_path

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        """Return one generated folder record."""
        return [
            ProjectFolderRecord(
                folder_id="folder-1",
                project_id=project_id,
                folder_path=self._folder_path,
            )
        ]


class _AssetRepo:
    """In-memory file asset repository for evidence tests."""

    def __init__(self, assets: list[FileAsset]) -> None:
        """Create a repository with fixed assets."""
        self._assets = assets

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return fixed assets."""
        return self._assets
