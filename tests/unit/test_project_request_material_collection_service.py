from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionConflictError,
    ProjectRequestMaterialCollectionService,
)
from backend.domain import FileAsset, FileAssetType, Project, ProjectStatus
from backend.infrastructure.files.request_material_copy_gateway import (
    RequestMaterialCopyGateway,
)


def test_preview_allows_partial_collection_when_request_email_is_missing(
    tmp_path: Path,
) -> None:
    app_form = _write(tmp_path / "source" / "application.docx", b"form")
    support = _write(tmp_path / "source" / "drawing.pdf", b"drawing")
    unknown = _write(tmp_path / "source" / "inline.png", b"image")
    service = _service(
        tmp_path,
        [
            _asset(
                "form-1",
                FileAssetType.APPLICATION_FORM,
                app_form,
                "application.docx",
                role="selected_application_form",
                sha256=_sha("form"),
            ),
            _asset(
                "support-1",
                FileAssetType.ATTACHMENT,
                support,
                "drawing.pdf",
                role="supporting_attachment",
                sha256=_sha("drawing"),
            ),
            _asset(
                "unknown-1",
                FileAssetType.ATTACHMENT,
                unknown,
                "inline.png",
            ),
        ],
    )

    preview = service.preview("P1")

    assert preview.status == "partial"
    assert "Request email missing" in preview.warnings
    target_areas = [(item.source_asset_id, item.target_area) for item in preview.items]
    assert ("form-1", "source_book_application_form") in target_areas
    assert ("form-1", "submitted_material") in target_areas
    assert ("support-1", "submitted_material") in target_areas
    assert ("unknown-1", "source_book_attachment") in target_areas
    assert ("unknown-1", "submitted_material") not in target_areas
    unknown_item = next(item for item in preview.items if item.source_asset_id == "unknown-1")
    assert unknown_item.review_required is True
    assert unknown_item.status == "needs_review"


def test_preview_blocks_multiple_request_email_candidates(tmp_path: Path) -> None:
    app_form = _write(tmp_path / "source" / "application.docx", b"form")
    msg_one = _write(tmp_path / "source" / "request-a.msg", b"mail-a")
    msg_two = _write(tmp_path / "source" / "request-b.msg", b"mail-b")
    service = _service(
        tmp_path,
        [
            _asset("form-1", FileAssetType.APPLICATION_FORM, app_form, "application.docx"),
            _asset(
                "mail-1",
                FileAssetType.ATTACHMENT,
                msg_one,
                "request-a.msg",
                role="email_source",
                sha256=_sha("mail-a"),
            ),
            _asset(
                "mail-2",
                FileAssetType.ATTACHMENT,
                msg_two,
                "request-b.msg",
                role="email_source",
                sha256=_sha("mail-b"),
            ),
        ],
    )

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert "Multiple request email candidates need review" in preview.blockers


def test_preview_deduplicates_duplicate_request_email_rows(tmp_path: Path) -> None:
    app_form = _write(tmp_path / "source" / "application.docx", b"form")
    request_email = _write(tmp_path / "source" / "request.msg", b"mail")
    service = _service(
        tmp_path,
        [
            _asset("form-1", FileAssetType.APPLICATION_FORM, app_form, "application.docx"),
            _asset(
                "mail-1",
                FileAssetType.ATTACHMENT,
                request_email,
                "request.msg",
                role="email_source",
                sha256=_sha("mail"),
            ),
            _asset(
                "mail-duplicate",
                FileAssetType.ATTACHMENT,
                request_email,
                "request.msg",
                sha256=_sha("mail"),
            ),
        ],
    )

    preview = service.preview("P1")

    email_items = [item for item in preview.items if item.target_area == "official_email"]
    assert len(email_items) == 1
    assert email_items[0].source_asset_id == "mail-1"


def test_collect_copies_request_material_without_deleting_sources(tmp_path: Path) -> None:
    app_form = _write(tmp_path / "source" / "application.docx", b"form")
    request_email = _write(tmp_path / "source" / "request.msg", b"mail")
    support = _write(tmp_path / "source" / "drawing.pdf", b"drawing")
    needs_review = _write(tmp_path / "source" / "inline.png", b"image")
    service = _service(
        tmp_path,
        [
            _asset(
                "form-1",
                FileAssetType.APPLICATION_FORM,
                app_form,
                "application.docx",
                role="selected_application_form",
                sha256=_sha("form"),
            ),
            _asset(
                "mail-1",
                FileAssetType.ATTACHMENT,
                request_email,
                "request.msg",
                role="email_source",
                sha256=_sha("mail"),
            ),
            _asset(
                "support-1",
                FileAssetType.ATTACHMENT,
                support,
                "drawing.pdf",
                role="supporting_attachment",
                sha256=_sha("drawing"),
            ),
            _asset("review-1", FileAssetType.ATTACHMENT, needs_review, "inline.png"),
        ],
    )

    result = service.collect("P1")

    assert result.status == "partial"
    assert request_email.is_file()
    assert app_form.is_file()
    assert support.is_file()
    assert needs_review.is_file()
    source_book = tmp_path / "DL-001" / "Source Book" / "Request Material"
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    assert (source_book / "E-mail" / "request.msg").read_bytes() == b"mail"
    assert (official / "E-mail" / "request.msg").read_bytes() == b"mail"
    assert (source_book / "Application Form" / "application.docx").read_bytes() == b"form"
    assert (official / "Submitted Material" / "application.docx").read_bytes() == b"form"
    assert (official / "Submitted Material" / "drawing.pdf").read_bytes() == b"drawing"
    assert (source_book / "Attachments" / "inline.png").read_bytes() == b"image"
    assert not (official / "Submitted Material" / "inline.png").exists()
    assert result.skipped_paths


def test_collect_blocks_existing_target_with_different_content(tmp_path: Path) -> None:
    app_form = _write(tmp_path / "source" / "application.docx", b"form")
    request_email = _write(tmp_path / "source" / "request.msg", b"mail")
    official_target = (
        tmp_path
        / "DL-001"
        / "DL-001 Connector Qualification test"
        / "E-mail"
        / "request.msg"
    )
    _write(official_target, b"different")
    service = _service(
        tmp_path,
        [
            _asset("form-1", FileAssetType.APPLICATION_FORM, app_form, "application.docx"),
            _asset(
                "mail-1",
                FileAssetType.ATTACHMENT,
                request_email,
                "request.msg",
                role="email_source",
                sha256=_sha("mail"),
            ),
        ],
    )

    preview = service.preview("P1")

    assert preview.status == "conflict"
    with pytest.raises(ProjectRequestMaterialCollectionConflictError):
        service.collect("P1")


def _write(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _sha(label: str) -> str:
    return (label.encode().hex() * 64)[:64]


def _asset(
    asset_id: str,
    asset_type: FileAssetType,
    path: Path,
    original_name: str,
    *,
    role: str | None = None,
    sha256: str | None = None,
) -> FileAsset:
    return FileAsset(
        asset_id=asset_id,
        project_id="P1",
        asset_type=asset_type,
        path=path,
        original_name=original_name,
        source_role=role,
        sha256=sha256,
    )


def _service(tmp_path: Path, assets: list[FileAsset]) -> ProjectRequestMaterialCollectionService:
    local_folder = tmp_path / "DL-001"
    source_book = local_folder / "Source Book"
    official = local_folder / "DL-001 Connector Qualification test"
    source_book.mkdir(parents=True, exist_ok=True)
    (official / "E-mail").mkdir(parents=True, exist_ok=True)
    (official / "Submitted Material").mkdir(parents=True, exist_ok=True)
    return ProjectRequestMaterialCollectionService(
        project_repository=_ProjectStore(),
        workspace_repository=_WorkspaceStore(
            OfficialWorkspaceRecord(
                workspace_id="workspace-1",
                project_id="P1",
                dl_number="DL-001",
                local_workspace_path=local_folder,
                source_book_path=source_book,
                official_folder_path=official,
                manifest_path=local_folder / ".connlab" / "manifest.json",
                template_source_path=tmp_path / "template",
                created_at="2026-06-13T00:00:00+00:00",
            )
        ),
        file_asset_repository=_FileAssetStore(assets),
        collection_repository=_CollectionStore(),
        copy_gateway=RequestMaterialCopyGateway(),
    )


class _ProjectStore:
    def get(self, project_id: str) -> Project | None:
        return Project(
            project_id=project_id,
            project_no="DL-001",
            product_name="Connector",
            requestor="White",
            status=ProjectStatus.FOLDER_CREATED,
        )


class _WorkspaceStore:
    def __init__(self, record: OfficialWorkspaceRecord | None) -> None:
        self.record = record

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return self.record if self.record and self.record.project_id == project_id else None


class _FileAssetStore:
    def __init__(self, assets: list[FileAsset]) -> None:
        self.assets = assets

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        return [asset for asset in self.assets if asset.project_id == project_id]


class _CollectionStore:
    def __init__(self) -> None:
        self.saved = []

    def save_collection(self, collection, items):
        self.saved.append((collection, items))
        return collection

    def latest_by_project(self, project_id: str):
        return self.saved[-1][0] if self.saved else None

    def list_items(self, collection_id: str):
        for collection, items in reversed(self.saved):
            if collection.collection_id == collection_id:
                return items
        return tuple()
