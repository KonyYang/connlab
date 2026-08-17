from __future__ import annotations

from datetime import date
import os
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


def test_preferred_import_directory_prioritizes_submitted_material(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    attachment = intake / "spec.pdf"
    attachment.write_bytes(b"x")
    official = tmp_path / "official"
    submitted = official / "Submitted Material"
    submitted.mkdir(parents=True)
    service = _service(
        assets=[_asset("A1", attachment, "spec.pdf", source_intake_asset_id="I1")],
        official_folder=official,
    )

    result = service.list_source_candidates("P1")

    assert result.preferred_import_directory == submitted
    assert result.preferred_import_directory_source == "submitted_material"


def test_preferred_import_directory_uses_deterministic_intake_parent(tmp_path: Path) -> None:
    later = tmp_path / "z-intake"
    earlier = tmp_path / "a-intake"
    later.mkdir()
    earlier.mkdir()
    service = _service(
        assets=[
            _asset("A1", later / "b.pdf", "b.pdf", source_intake_asset_id="I1"),
            _asset("A2", earlier / "a.docx", "a.docx", source_intake_asset_id="I2"),
            _asset("A3", earlier / "mail.msg", "mail.msg", source_role="email_source"),
        ]
    )
    for asset in service._assets._assets.values():
        asset.path.write_bytes(b"x")

    result = service.list_source_candidates("P1")

    assert result.preferred_import_directory == earlier
    assert result.preferred_import_directory_source == "intake_attachments"


def test_preferred_import_directory_is_unavailable_for_missing_paths(tmp_path: Path) -> None:
    service = _service(
        assets=[
            _asset(
                "A1",
                tmp_path / "missing" / "spec.pdf",
                "spec.pdf",
                source_intake_asset_id="I1",
            )
        ],
        official_folder=tmp_path / "missing-official",
    )

    result = service.list_source_candidates("P1")

    assert result.preferred_import_directory is None
    assert result.preferred_import_directory_source == "unavailable"


def test_resolved_directory_candidates_list_direct_supported_files_in_filename_order(
    tmp_path: Path,
) -> None:
    official = tmp_path / "official"
    submitted = official / "Submitted Material"
    submitted.mkdir(parents=True)
    (submitted / "zeta.PDF").write_bytes(b"pdf")
    (submitted / "Alpha.docx").write_bytes(b"docx")
    (submitted / "middle.doc").write_bytes(b"doc")
    (submitted / "ignore.txt").write_bytes(b"text")
    nested = submitted / "nested"
    nested.mkdir()
    (nested / "hidden.docx").write_bytes(b"nested")
    intake = tmp_path / "intake"
    intake.mkdir()
    attachment = intake / "fallback.pdf"
    attachment.write_bytes(b"fallback")
    service = _service(
        assets=[_asset("A1", attachment, "fallback.pdf", source_intake_asset_id="I1")],
        official_folder=official,
    )

    before = {
        path.name: (path.read_bytes(), path.stat().st_mtime_ns)
        for path in submitted.iterdir()
        if path.is_file()
    }
    result = service.list_resolved_directory_candidates("P1")

    assert result.source_title == "Submitted Material files"
    assert [candidate.file_name for candidate in result.candidates] == [
        "Alpha.docx",
        "middle.doc",
        "zeta.PDF",
    ]
    assert all(len(candidate.candidate_id) == 64 for candidate in result.candidates)
    assert all(str(submitted) not in candidate.candidate_id for candidate in result.candidates)
    assert {
        path.name: (path.read_bytes(), path.stat().st_mtime_ns)
        for path in submitted.iterdir()
        if path.is_file()
    } == before


def test_resolved_directory_candidate_id_expires_after_same_name_content_replacement(
    tmp_path: Path,
) -> None:
    official = tmp_path / "official"
    submitted = official / "Submitted Material"
    submitted.mkdir(parents=True)
    source = submitted / "matrix.docx"
    source.write_bytes(b"first-content")
    service = _service(assets=[], official_folder=official)
    candidate_id = service.list_resolved_directory_candidates("P1").candidates[0].candidate_id
    original_times = (source.stat().st_atime_ns, source.stat().st_mtime_ns)

    source.write_bytes(b"other-content")
    os.utime(source, ns=original_times)

    with pytest.raises(ProjectTestPlanSourceCandidateNotFoundError):
        service.get_resolved_directory_candidate_source_path("P1", candidate_id)

    replacement = service.list_resolved_directory_candidates("P1").candidates[0]
    assert replacement.candidate_id != candidate_id
    assert service.get_resolved_directory_candidate_source_path(
        "P1", replacement.candidate_id
    ) == source


def test_resolved_directory_candidate_id_is_bound_to_current_directory_and_name(
    tmp_path: Path,
) -> None:
    first_official = tmp_path / "first-official"
    first_submitted = first_official / "Submitted Material"
    first_submitted.mkdir(parents=True)
    first_source = first_submitted / "matrix.pdf"
    first_source.write_bytes(b"same-content")
    workspace_store = _WorkspaceStore(first_official)
    service = _service(assets=[], workspace_store=workspace_store)
    candidate_id = service.list_resolved_directory_candidates("P1").candidates[0].candidate_id

    renamed = first_submitted / "renamed.pdf"
    first_source.rename(renamed)
    with pytest.raises(ProjectTestPlanSourceCandidateNotFoundError):
        service.get_resolved_directory_candidate_source_path("P1", candidate_id)

    second_official = tmp_path / "second-official"
    second_submitted = second_official / "Submitted Material"
    second_submitted.mkdir(parents=True)
    (second_submitted / "matrix.pdf").write_bytes(b"same-content")
    workspace_store.official_folder = second_official
    with pytest.raises(ProjectTestPlanSourceCandidateNotFoundError):
        service.get_resolved_directory_candidate_source_path("P1", candidate_id)


def test_resolved_directory_candidates_use_email_attachment_folder_fallback(
    tmp_path: Path,
) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    source = intake / "matrix.pdf"
    source.write_bytes(b"pdf")
    service = _service(
        assets=[_asset("A1", source, "matrix.pdf", source_intake_asset_id="I1")],
        official_folder=tmp_path / "missing-official",
    )

    result = service.list_resolved_directory_candidates("P1")

    assert result.source_title == "Email attachment files"
    assert [candidate.file_name for candidate in result.candidates] == ["matrix.pdf"]


def test_resolved_directory_candidates_do_not_follow_file_symlinks(tmp_path: Path) -> None:
    official = tmp_path / "official"
    submitted = official / "Submitted Material"
    submitted.mkdir(parents=True)
    outside = tmp_path / "outside.docx"
    outside.write_bytes(b"outside")
    link = submitted / "linked.docx"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("File symlinks are not available in this environment.")
    service = _service(assets=[], official_folder=official)

    result = service.list_resolved_directory_candidates("P1")

    assert result.candidates == ()


def _service(
    assets: list[FileAsset],
    official_folder: Path | None = None,
    workspace_store: "_WorkspaceStore | None" = None,
) -> ProjectTestPlanSourceCandidateService:
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
        official_workspace_store=workspace_store or _WorkspaceStore(official_folder),
    )


def _asset(
    asset_id: str,
    path: Path,
    original_name: str,
    *,
    source_intake_asset_id: str | None = None,
    source_role: str | None = None,
) -> FileAsset:
    return FileAsset(
        asset_id=asset_id,
        project_id="P1",
        asset_type=FileAssetType.ATTACHMENT,
        path=path,
        original_name=original_name,
        registered_on=date(2026, 5, 14),
        source_intake_asset_id=source_intake_asset_id,
        source_role=source_role,
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


class _WorkspaceStore:
    def __init__(self, official_folder: Path | None) -> None:
        self.official_folder = official_folder

    def get_by_project(self, project_id: str) -> object | None:
        if self.official_folder is None:
            return None
        return type("Workspace", (), {"official_folder_path": self.official_folder})()
