from datetime import date
from pathlib import Path

import pytest

from backend.application.ltr_renumber_preview_service import (
    LtrRenumberPreviewError,
    LtrRenumberPreviewNotFoundError,
    LtrRenumberPreviewService,
    PreviewLtrRenumberCommand,
)
from backend.domain import (
    FileAsset,
    FileAssetType,
    LtrRecord,
    LtrStatus,
    Project,
    ProjectFolderRecord,
)


def test_ltr_renumber_preview_reports_folder_and_asset_impacts(tmp_path: Path) -> None:
    old_number = "DL-2026-04-001"
    new_number = "DL-2026-04-002"
    project_folder = tmp_path / f"{old_number}_PRJ-001"
    asset_path = project_folder / f"{old_number}_application.docx"
    service = _build_service(
        tmp_path,
        folders=[
            ProjectFolderRecord(
                folder_id="FOLDER1",
                project_id="P1",
                folder_path=project_folder,
            )
        ],
        assets=[
            FileAsset(
                asset_id="ASSET1",
                project_id="P1",
                asset_type=FileAssetType.APPLICATION_FORM,
                path=asset_path,
            )
        ],
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRenumberCommand(
            old_ltr_number=old_number,
            new_ltr_number=new_number,
            reason="Corrected workbook number",
            operator_confirmed=True,
        ),
    )

    assert preview.ltr_record_id == "LTR1"
    assert preview.operator_confirmation_required is True
    assert preview.operator_confirmed is True
    assert preview.conflicts == ()
    assert [impact.record_type for impact in preview.impacts] == [
        "project_folder",
        "file_asset:application_form",
    ]
    assert all(new_number in str(impact.target_path) for impact in preview.impacts)
    assert project_folder.exists() is False
    assert asset_path.exists() is False


def test_ltr_renumber_preview_requires_reason(tmp_path: Path) -> None:
    service = _build_service(tmp_path)

    with pytest.raises(LtrRenumberPreviewError, match="reason"):
        service.preview_project(
            "P1",
            PreviewLtrRenumberCommand(
                old_ltr_number="DL-2026-04-001",
                new_ltr_number="DL-2026-04-002",
                reason=" ",
            ),
        )


def test_ltr_renumber_preview_requires_preview_reason_for_ltr_changes(
    tmp_path: Path,
) -> None:
    service = _build_service(tmp_path)

    preview = service.preview_project(
        "P1",
        PreviewLtrRenumberCommand(
            old_ltr_number="DL-2026-04-001",
            new_ltr_number="DL-2026-04-002",
            reason="Corrected after applicant update",
        ),
    )

    assert preview.operator_confirmation_required is True
    assert "Corrected after applicant update" in preview.audit_summary
    assert preview.old_ltr_number == "DL-2026-04-001"
    assert preview.new_ltr_number == "DL-2026-04-002"


def test_ltr_renumber_preview_reports_duplicate_local_ltr(tmp_path: Path) -> None:
    service = _build_service(
        tmp_path,
        duplicate_ltrs=[
            LtrRecord(
                ltr_id="LTR2",
                project_id="P2",
                ltr_number="DL-2026-04-002",
                status=LtrStatus.REGISTERED,
            )
        ],
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRenumberCommand(
            old_ltr_number="DL-2026-04-001",
            new_ltr_number="DL-2026-04-002",
            reason="Correct duplicate",
        ),
    )

    assert "LTR number already exists in local records: DL-2026-04-002" in (
        preview.conflicts
    )


def test_ltr_renumber_preview_reports_target_path_conflict(tmp_path: Path) -> None:
    old_number = "DL-2026-04-001"
    new_number = "DL-2026-04-002"
    current_folder = tmp_path / f"{old_number}_PRJ-001"
    target_folder = tmp_path / f"{new_number}_PRJ-001"
    target_folder.mkdir()
    service = _build_service(
        tmp_path,
        folders=[
            ProjectFolderRecord(
                folder_id="FOLDER1",
                project_id="P1",
                folder_path=current_folder,
            )
        ],
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRenumberCommand(
            old_ltr_number=old_number,
            new_ltr_number=new_number,
            reason="Correct typo",
        ),
    )

    assert any("Target path already exists" in conflict for conflict in preview.conflicts)


def test_ltr_renumber_preview_reports_missing_ltr(tmp_path: Path) -> None:
    service = _build_service(tmp_path, project_ltrs=[])

    with pytest.raises(LtrRenumberPreviewNotFoundError, match="LTR record not found"):
        service.preview_project(
            "P1",
            PreviewLtrRenumberCommand(
                old_ltr_number="DL-2026-04-001",
                new_ltr_number="DL-2026-04-002",
                reason="Correct typo",
            ),
        )


def _build_service(
    tmp_path: Path,
    *,
    project_ltrs: list[LtrRecord] | None = None,
    duplicate_ltrs: list[LtrRecord] | None = None,
    folders: list[ProjectFolderRecord] | None = None,
    assets: list[FileAsset] | None = None,
) -> LtrRenumberPreviewService:
    return LtrRenumberPreviewService(
        project_repository=_ProjectRepo(),
        ltr_repository=_LtrRepo(project_ltrs, duplicate_ltrs),
        folder_repository=_FolderRepo(folders or []),
        file_asset_repository=_AssetRepo(assets or []),
    )


class _ProjectRepo:
    def get(self, project_id: str) -> Project | None:
        return Project(
            project_id=project_id,
            project_no="PRJ-001",
            product_name="Connector",
            requestor="Alice",
        )


class _LtrRepo:
    def __init__(
        self,
        project_ltrs: list[LtrRecord] | None,
        duplicate_ltrs: list[LtrRecord] | None,
    ) -> None:
        self._project_ltrs = project_ltrs if project_ltrs is not None else [
            LtrRecord(
                ltr_id="LTR1",
                project_id="P1",
                ltr_number="DL-2026-04-001",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 4, 28),
            )
        ]
        self._duplicates = duplicate_ltrs or []

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [ltr for ltr in self._project_ltrs if ltr.project_id == project_id]

    def search(self, query: str) -> list[LtrRecord]:
        return [ltr for ltr in self._duplicates if query in ltr.ltr_number]


class _FolderRepo:
    def __init__(self, folders: list[ProjectFolderRecord]) -> None:
        self._folders = folders

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        return [folder for folder in self._folders if folder.project_id == project_id]


class _AssetRepo:
    def __init__(self, assets: list[FileAsset]) -> None:
        self._assets = assets

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        return [asset for asset in self._assets if asset.project_id == project_id]
