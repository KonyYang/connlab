"""Read-only library queries use isolated folders, never operator data."""
from pathlib import Path
import pytest
from backend.application.project_library.search import LibrarySearchService
from backend.infrastructure.project_library.search_files import SearchFiles


class Catalog:
    def __init__(self, root):
        self.root = root

    def catalog(self):
        return [dict(key="project:p1", project_id="p1", member_id=None,
                     title="PwrBlade", number="DL-2026-08-079", test_item="温升",
                     source="connlab", folder_path=str(self.root))]


def test_search_combines_project_fields_and_deep_filename_and_refreshes(tmp_path):
    folder = tmp_path / "Records" / "Group 1"
    folder.mkdir(parents=True)
    record = folder / "温升记录.xlsx"
    record.write_bytes(b"manual data")
    service = LibrarySearchService(Catalog(tmp_path), SearchFiles(), lambda path: None)
    result = service.search("PwrBlade 温升记录")
    assert [r["relative_path"] for r in result["files"]] == ["Records/Group 1/温升记录.xlsx"]
    assert result["files"][0]["kind"] == "record"
    assert service.search("DL-2026-08-079 温升")["projects"][0]["key"] == "project:p1"
    record.rename(folder / "new.xlsx")
    assert service.search("温升记录")["files"] == []
    assert service.search("new.xlsx")["files"][0]["name"] == "new.xlsx"
    assert (folder / "new.xlsx").read_bytes() == b"manual data"


def test_missing_root_retains_project_and_reports_incomplete_search(tmp_path):
    service = LibrarySearchService(Catalog(tmp_path / "missing"), SearchFiles(), lambda path: None)
    result = service.search("PwrBlade")
    assert result["projects"][0]["available"] is False
    assert result["warnings"]
    assert result["files"] == []


def test_type_filter_without_query_and_scan_limit_are_explicit(tmp_path):
    (tmp_path / "report.pdf").write_bytes(b"report")
    (tmp_path / "record.xlsx").write_bytes(b"record")
    service = LibrarySearchService(Catalog(tmp_path), SearchFiles(), lambda path: None)
    assert [row["name"] for row in service.search(kind="report")["files"]] == ["report.pdf"]
    _, warnings = SearchFiles().scan(tmp_path, limit=1)
    assert warnings and "incomplete" in warnings[0]


def test_redirected_files_are_not_scanned_or_opened(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "report.docx").write_bytes(b"private")
    root = tmp_path / "project"
    root.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Host does not allow creating test symlinks")
    service = LibrarySearchService(Catalog(root), SearchFiles(), lambda path: None)
    assert service.search("report")["files"] == []
    assert service.search("report")["warnings"]
    with pytest.raises(ValueError):
        service.open("project:p1", "link/report.docx")


def test_open_revalidates_relative_path_and_blocks_programs(tmp_path):
    opened = []
    (tmp_path / "report.docx").write_bytes(b"report")
    (tmp_path / "run.cmd").write_text("echo unsafe", encoding="utf-8")
    service = LibrarySearchService(Catalog(tmp_path), SearchFiles(), opened.append)
    assert service.open("project:p1", "report.docx")["status"] == "opened"
    assert opened == [tmp_path / "report.docx"]
    for relative in ("../outside.docx", str(tmp_path / "report.docx"), "run.cmd", "report.docx:secret", "\\\\server\\share\\report.docx"):
        with pytest.raises(ValueError):
            service.open("project:p1", relative)
    (tmp_path / "report.docx").unlink()
    with pytest.raises(ValueError):
        service.open("project:p1", "report.docx")


def test_api_unifies_existing_identities_without_copying_or_writing(tmp_path):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    from backend.infrastructure.storage.database import init_db
    from backend.infrastructure.storage.models import ProjectModel, ProjectFolderRecordModel, ProjectTemporaryContextModel
    from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
    from backend.infrastructure.storage.models_legacy_projects import LegacyProjectRecordModel
    from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
    from backend.api.dependencies import get_project_registry_summary_service
    from backend.api.routes_project_library import router, get_library_search_service

    root = tmp_path / "native"
    root.mkdir()
    (root / "report.docx").write_bytes(b"human edits")
    old = tmp_path / "old"
    old.mkdir()
    (old / "record.xlsx").write_bytes(b"old record")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite'}", connect_args={"check_same_thread": False})
    init_db(engine)
    opened = []
    with Session(engine) as session:
        session.add(ProjectModel(project_id="p1", product_name="PwrBlade", project_no="DL-2026-08-079", requestor="Lab", status="draft"))
        session.add(ProjectModel(project_id="hidden", product_name="PwrBlade hidden", requestor="Lab", status="draft", registry_state="trash"))
        session.commit()
        session.add_all([
            ProjectTemporaryContextModel(context_id="c1", project_id="p1", sample_description="PwrBlade", test_item="温升"),
            ProjectFolderRecordModel(folder_id="f1", project_id="p1", folder_path=str(root)),
            ProjectLibraryMemberModel(member_id="m1", project_id="p1", title="PwrBlade", ltr_number="DL-2026-08-079", folder_path=str(root).replace("\\", "/").swapcase(), source_path="original", created_at="2026-11-14"),
            ProjectLibraryMemberModel(member_id="m2", title="Old PwrBlade", ltr_number="DL-2026-08-079", folder_path=str(old), source_path="original2", created_at="2026-11-14"),
            ProjectLibraryMemberModel(member_id="hidden-member", project_id="hidden", title="PwrBlade hidden", folder_path=str(tmp_path / "hidden"), source_path="original3", created_at="2026-11-14"),
            LegacyProjectRecordModel(record_id="l1", name="Linked PwrBlade", number="DL-2026-08-079", evidence_json="[]", folder_path=str(tmp_path / "missing"), normalized_path="missing", notes_json="[]", imported_at="2026-11-14", updated_at="2026-11-14"),
        ])
        session.commit()
    app = FastAPI()
    app.include_router(router)
    def service():
        with Session(engine) as session:
            yield LibrarySearchService(LibrarySearchRepository(session, get_project_registry_summary_service(session)), SearchFiles(), opened.append)
    app.dependency_overrides[get_library_search_service] = service
    with engine.connect() as connection:
        before = list(connection.execute(text("SELECT * FROM projects")))
    with TestClient(app) as client:
        result = client.get("/api/project-library/search", params={"q": "PwrBlade"})
        assert result.status_code == 200, result.text
        assert len(result.json()["projects"]) == 3
        assert len(result.json()["files"]) == 2
        assert result.json()["warnings"]
        assert client.post("/api/project-library/open-file", json={"key": "project:p1", "relative_path": "report.docx"}).status_code == 200
        assert opened == [root / "report.docx"]
        assert client.post("/api/project-library/open-file", json={"key": "project:p1", "relative_path": "../outside.docx"}).status_code == 409
    with engine.connect() as connection:
        assert list(connection.execute(text("SELECT * FROM projects"))) == before
    assert (root / "report.docx").read_bytes() == b"human edits"
    assert list(root.iterdir()) == [root / "report.docx"]
    engine.dispose()
