from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from backend.application.project_test_plan_source_candidate_service import (
    ProjectTestPlanSourceCandidateNotFoundError,
    ProjectTestPlanSourceCandidateService,
)
from backend.domain import FileAsset, FileAssetType, Project, ProjectStatus


def test_list_source_candidates_ranks_likely_spec_docx_first(tmp_path: Path) -> None:
    available = tmp_path / "product_matrix_spec.docx"
    available.write_bytes(b"x")
    generic = tmp_path / "notes.docx"
    generic.write_bytes(b"x")
    service = _service(
        assets=[
            _asset("A1", available, "Product_Matrix_Spec.docx"),
            _asset("A2", generic, "notes.docx"),
        ]
    )

    result = service.list_source_candidates("P1")

    assert [item.source_asset_id for item in result.candidates] == ["A1", "A2"]
    assert result.candidates[0].candidate_kind == "likely_spec_or_matrix"
    assert result.candidates[0].stored_file_available is True
    assert result.warnings == ()


def test_list_source_candidates_warns_when_docx_missing_or_absent(tmp_path: Path) -> None:
    missing_docx = tmp_path / "missing.docx"
    non_docx = tmp_path / "spec.pdf"
    non_docx.write_bytes(b"%PDF-1.4")
    service = _service(
        assets=[
            _asset("A1", missing_docx, "missing.docx"),
            _asset("A2", non_docx, "spec.pdf"),
        ]
    )

    result = service.list_source_candidates("P1")

    assert len(result.candidates) == 1
    assert result.candidates[0].source_asset_id == "A1"
    assert "missing from local storage" in result.warnings[0]

    empty = _service(assets=[_asset("A3", non_docx, "spec.pdf")]).list_source_candidates("P1")
    assert empty.candidates == ()
    assert "No `.docx` project source candidates were found" in empty.warnings[0]


def test_get_candidate_source_path_checks_project_ownership_and_file(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.docx"
    spec_path.write_bytes(b"x")
    service = _service(assets=[_asset("A1", spec_path, "spec.docx")])

    resolved = service.get_candidate_source_path("P1", "A1")
    assert resolved == spec_path

    with pytest.raises(ProjectTestPlanSourceCandidateNotFoundError):
        service.get_candidate_source_path("P2", "A1")

    missing_service = _service(assets=[_asset("A2", tmp_path / "gone.docx", "gone.docx")])
    with pytest.raises(ProjectTestPlanSourceCandidateNotFoundError):
        missing_service.get_candidate_source_path("P1", "A2")


def _service(assets: list[FileAsset]) -> ProjectTestPlanSourceCandidateService:
    project = Project(
        project_id="P1",
        project_no="DL-2026-05-001",
        product_name="Connector",
        requestor="Alice",
        status=ProjectStatus.LTR_REGISTERED,
        created_on=date(2026, 5, 14),
    )
    return ProjectTestPlanSourceCandidateService(
        project_store=_ProjectStore({"P1": project}),
        file_asset_store=_FileAssetStore(assets),
    )


def _asset(asset_id: str, path: Path, original_name: str) -> FileAsset:
    return FileAsset(
        asset_id=asset_id,
        project_id="P1",
        asset_type=FileAssetType.ATTACHMENT,
        path=path,
        original_name=original_name,
        registered_on=date(2026, 5, 14),
    )


class _ProjectStore:
    def __init__(self, projects: dict[str, Project]) -> None:
        self._projects = projects

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)


class _FileAssetStore:
    def __init__(self, assets: list[FileAsset]) -> None:
        self._assets = {asset.asset_id: asset for asset in assets}

    def get(self, asset_id: str) -> FileAsset | None:
        return self._assets.get(asset_id)

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        return [item for item in self._assets.values() if item.project_id == project_id]
