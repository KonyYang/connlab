import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.application.legacy_project_registration_service import LegacyProjectRegistrationService
from backend.infrastructure.files.legacy_project_preview_gateway import LegacyProjectPreviewGateway
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.repositories.legacy_projects import LegacyProjectRepository


@pytest.fixture
def engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'isolated.db'}", connect_args={"timeout": 30})
    init_db(engine)
    yield engine
    engine.dispose()


def service(session):
    return LegacyProjectRegistrationService(LegacyProjectRepository(session), LegacyProjectPreviewGateway())


def folder(tmp_path, name):
    path = tmp_path / name
    path.mkdir()
    (path / "report.pdf").write_bytes(b"original")
    return str(path)


def selection(plan, keep=False):
    return [{"folder": row["folder"], "fingerprint": row["fingerprint"], "keep_separate": keep}
            for row in plan["projects"] if row["status"] != "failed"]


def test_register_320_unstructured_folders_and_retry_without_creating_business_projects(engine, tmp_path):
    paths = [folder(tmp_path, f"Manual old sample {i}") for i in range(320)]
    with Session(engine) as session:
        api = service(session)
        plan = api.plan(paths)
        assert all(row["status"] == "ready" for row in plan["projects"])
        result = api.register(paths, selection(plan))
        assert result["counts"] == {"added": 320, "already_added": 0, "review": 0, "failed": 0}
        assert len(api.search("sample 31")) == 11
        assert api.register(paths, selection(plan))["counts"]["already_added"] == 320
        from sqlalchemy import text
        assert session.execute(text("select count(*) from projects")).scalar() == 0
    assert (tmp_path / "Manual old sample 0" / "report.pdf").read_bytes() == b"original"


def test_conflicts_need_explicit_keep_separate_and_changed_metadata_requires_new_plan(engine, tmp_path):
    paths = [folder(tmp_path, f"DL-2020-01-001 {n}") for n in ("A", "B")]
    with Session(engine) as session:
        api = service(session)
        plan = api.plan(paths)
        assert [row["status"] for row in plan["projects"]] == ["review", "review"]
        assert api.register(paths, selection(plan))["counts"]["review"] == 2
        assert api.register(paths, selection(plan, True))["counts"]["added"] == 2
        fresh = folder(tmp_path, "No number")
        plan = api.plan([fresh])
        from pathlib import Path
        (Path(fresh) / "application_data.json").write_text(json.dumps({"DL": "DL-2020-01-002"}), encoding="utf-8")
        assert api.register([fresh], selection(plan))["counts"]["review"] == 1


def test_two_connections_cannot_register_one_directory_twice(engine, tmp_path):
    path = folder(tmp_path, "Concurrent")
    with Session(engine) as session:
        plan = service(session).plan([path])
    def run():
        with Session(engine) as session:
            return service(session).register([path], selection(plan))["counts"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert sum(row["added"] for row in results) == 1
    assert sum(row["already_added"] for row in results) == 1


@pytest.mark.parametrize("area", ["active", "trash", "history"])
def test_existing_business_identifiers_and_locations_are_checked_in_all_registry_areas(engine, tmp_path, area):
    from backend.infrastructure.storage.models import ProjectModel, LtrRecordModel, ProjectFolderRecordModel
    path = folder(tmp_path, "DL-2020-01-001 same location")
    other = folder(tmp_path, "DL-2020-01-001 copied material")
    with Session(engine) as session:
        session.add(ProjectModel(project_id="formal", project_no="DL-2020-01-099", product_name="Existing",
            requestor="User", status="DRAFT", registry_state=area))
        session.add(LtrRecordModel(ltr_id="ltr", project_id="formal", ltr_number="DL-2020-01-001", status="registered"))
        session.add(ProjectFolderRecordModel(folder_id="folder", project_id="formal", folder_path=path))
        session.commit()
        api = service(session)
        plan = api.plan([path, other])
        assert plan["projects"][0]["status"] == "already_added"
        assert plan["projects"][1]["status"] == "review"
        assert api.register([path, other], selection(plan, True))["counts"] == {
            "added": 1, "already_added": 1, "review": 0, "failed": 0}
        assert session.get(ProjectModel, "formal").registry_state == area
        assert session.get(ProjectModel, "formal").project_no == "DL-2020-01-099"


def test_all_number_evidence_and_legacy_source_id_are_compared_with_formal_projects(engine, tmp_path):
    from pathlib import Path
    from backend.infrastructure.storage.models import ProjectModel
    path = folder(tmp_path, "DL-2020-01-001 mismatch")
    (Path(path) / "application_data.json").write_text(json.dumps({"DL": "DL-2020-01-002"}), encoding="utf-8")
    source = folder(tmp_path, "Unknown old layout")
    (Path(source) / ".connlab").mkdir()
    (Path(source) / ".connlab" / "manifest.json").write_text(json.dumps({"project_id": "formal"}), encoding="utf-8")
    with Session(engine) as session:
        session.add(ProjectModel(project_id="formal", project_no="DL-2020-01-002", product_name="Existing", requestor="User", status="DRAFT"))
        session.commit()
        rows = service(session).plan([path, source])["projects"]
        assert all(row["status"] == "review" for row in rows)
        assert all(any("existing project" in note for note in row["notes"]) for row in rows)


def test_missing_item_does_not_block_others_and_relocation_changes_only_database(engine, tmp_path):
    from pathlib import Path
    from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
    path, another = folder(tmp_path, "Original"), folder(tmp_path, "Second")
    with Session(engine) as session:
        api = service(session)
        plan = api.plan([path, another])
        (Path(another) / "report.pdf").unlink()
        Path(another).rmdir()
        result = api.register([path, another], selection(plan))
        assert result["counts"]["added"] == 1
        assert result["counts"]["failed"] == 1
        record = api.search()[0]
        target = folder(tmp_path, "Moved elsewhere")
        launched = []
        api.opener = LocalFolderOpenGateway(launcher=launched.append)
        assert api.open_folder(record["record_id"])["status"] == "opened"
        assert launched == [path]
        changed = api.change_location(record["record_id"], target, 1)
        assert changed["revision"] == 2 and changed["folder_path"] == target
        with pytest.raises(ValueError, match="record changed"):
            api.change_location(record["record_id"], path, 1)
        (Path(target) / "report.pdf").unlink()
        Path(target).rmdir()
        assert api.search("Moved elsewhere")[0]["record_id"] == record["record_id"]
        assert api.open_folder(record["record_id"])["status"] == "blocked"
        assert (Path(path) / "report.pdf").read_bytes() == b"original"


def test_relocation_cannot_take_another_project_folder_or_a_redirected_path(engine, tmp_path):
    from pathlib import Path
    path, occupied = folder(tmp_path, "Original"), folder(tmp_path, "Occupied")
    with Session(engine) as session:
        api = service(session)
        plan = api.plan([path, occupied])
        api.register([path, occupied], selection(plan))
        first = next(row for row in api.search() if row["folder_path"] == path)
        with pytest.raises(ValueError, match="belongs to another"):
            api.change_location(first["record_id"], occupied, 1)
        assert api.get(first["record_id"])["folder_path"] == path
        alias = tmp_path / "redirected"
        try:
            alias.symlink_to(Path(occupied), target_is_directory=True)
        except OSError:
            return  # Windows hosts may disallow creating test symlinks.
        with pytest.raises(ValueError, match="Redirected"):
            api.change_location(first["record_id"], str(alias), 1)
