"""Existing folders become managed without inventing test or LTR authority."""
from contextlib import nullcontext
import json

import pytest
from sqlalchemy import create_engine

from backend.infrastructure.storage.database import init_db, create_session_factory
from backend.application.existing_project_service import ExistingProjectService
from backend.infrastructure.files.existing_project_gateway import ExistingProjectGateway
from backend.infrastructure.storage.repositories.existing_project import ExistingProjectRepository
from backend.infrastructure.storage.repositories.project_registry import ProjectRegistryRepository


class IdleGeneration:
    def lock(self, _): return nullcontext()
    def read(self, _): return None


@pytest.fixture
def service(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    with create_session_factory(engine)() as session:
        yield ExistingProjectService(ExistingProjectRepository(session), ProjectRegistryRepository(session),
                                     ExistingProjectGateway(), IdleGeneration()), tmp_path
    engine.dispose()


def test_manual_folder_preview_cancel_and_repeat_confirmation_preserve_originals(service):
    svc, root = service
    folder = root / "DL-2026-01-003 old sample"
    folder.mkdir()
    (folder / "results.txt").write_bytes(b"original")
    preview = svc.preview(str(folder))
    assert svc.list_locations() == []
    result = svc.register(path=str(folder), token=preview["token"], action="register",
                          management_number="LEGACY-003")
    again = svc.register(path=str(folder), token=preview["token"], action="register",
                         management_number="LEGACY-003")
    assert again == result
    assert len(svc.list_locations()) == 1
    assert svc.files(result["location_id"])["entries"][0]["name"] == "results.txt"
    assert (folder / "results.txt").read_bytes() == b"original"
    assert not (folder / ".connlab").exists()
    project = svc.registry.get(result["project_id"])
    assert project.status.value == "draft"


def test_foreign_identity_preserved_but_same_number_never_overwrites(service):
    svc, root = service
    folder = root / "one"; folder.mkdir(); (folder / ".connlab").mkdir()
    manifest = {"schema_version": 1, "project_id": "a" * 32, "dl_number": "DL-2026-01-003",
                "official_project_folder_path": "Z:/old/computer/folder"}
    (folder / ".connlab" / "manifest.json").write_text(json.dumps(manifest))
    first = svc.register(path=str(folder), token=svc.preview(str(folder))["token"], action="register",
                         management_number="DL-2026-01-003")
    assert first["project_id"] == "a" * 32
    second = root / "DL-2026-01-003 other"; second.mkdir()
    preview = svc.preview(str(second))
    assert preview["conflicts"][0]["project_id"] == first["project_id"]
    with pytest.raises(ValueError, match="number"):
        svc.register(path=str(second), token=preview["token"], action="independent",
                     management_number="DL-2026-01-003")
    assert len(svc.list_locations()) == 1
    independent = svc.register(path=str(second), token=preview["token"], action="independent",
                               management_number="LOCAL-003-B")
    assert independent["project_id"] != first["project_id"]
    assert independent["source_number"] == "DL-2026-01-003"


def test_source_change_rejects_confirmation_and_allows_fresh_preview(service):
    svc, root = service
    folder = root / "sample"; folder.mkdir()
    before = svc.preview(str(folder))
    (folder / ".connlab").mkdir()
    (folder / ".connlab" / "manifest.json").write_text('{"schema_version":99}')
    with pytest.raises(ValueError, match="changed"):
        svc.register(path=str(folder), token=before["token"], action="register", management_number="X")
    latest = svc.preview(str(folder))
    assert latest["manifest_error"]
    with pytest.raises(ValueError, match="manifest"):
        svc.register(path=str(folder), token=latest["token"], action="register", management_number="X")
    assert svc.list_locations() == []


def test_hidden_source_match_requires_restore_and_relocation_retains_project(service):
    svc, root = service
    folder = root / "source"; folder.mkdir()
    registered = svc.register(path=str(folder), token=svc.preview(str(folder))["token"], action="register", management_number="OLD")
    moved = root / "moved"; folder.rename(moved)
    preview = svc.preview_relocation(registered["location_id"], str(moved))
    result = svc.relocate(registered["location_id"], path=str(moved), token=preview["token"])
    assert result["project_id"] == registered["project_id"]
    assert result["revision"] == 1
    with svc.registry.atomic():
        svc.registry.move(result["project_id"], "trash", expected_revision=0, reason="test", actor=None,
                          changed_at="today", operation_id="test")
        svc.registry.commit()
    with pytest.raises(ValueError, match="Restore"):
        svc.register(path=str(moved), token=svc.preview(str(moved))["token"], action="link", target_project_id=result["project_id"])


def test_explicit_link_keeps_both_folders_and_invalid_manifest_requires_files_only_choice(service):
    svc, root = service
    one = root / "one"; one.mkdir()
    registered = svc.register(path=str(one), token=svc.preview(str(one))["token"], action="register", management_number="M1")
    two = root / "two"; two.mkdir()
    result = svc.register(path=str(two), token=svc.preview(str(two))["token"], action="link", target_project_id=registered["project_id"])
    assert result["project_id"] == registered["project_id"]
    assert len(svc.list_locations()) == 2
    bad = root / "bad"; bad.mkdir(); (bad / ".connlab").mkdir()
    (bad / ".connlab" / "manifest.json").write_text("not json")
    result = svc.register(path=str(bad), token=svc.preview(str(bad))["token"], action="independent",
                          management_number="M2", ignore_manifest=True)
    assert result["source_project_id"] is None


def test_replaced_physical_folder_is_not_silently_browsed_but_ordinary_edits_continue(service):
    svc,root=service
    folder=root/"project";folder.mkdir()
    saved=svc.register(path=str(folder),token=svc.preview(str(folder))["token"],action="register",management_number="SAFE")
    (folder/"new.txt").write_text("normal user edit")
    assert svc.files(saved["location_id"])["entries"][0]["name"] == "new.txt"
    folder.rename(root/"retained-original");folder.mkdir();(folder/"different.txt").write_text("different project")
    with pytest.raises(ValueError,match="replaced"):
        svc.files(saved["location_id"])
    assert len(svc.list_locations()) == 1


def test_target_registry_change_invalidates_link_preview(service):
    svc,root=service
    first=root/"first";first.mkdir()
    saved=svc.register(path=str(first),token=svc.preview(str(first))["token"],action="register",management_number="ONE")
    second=root/"second";second.mkdir();before=svc.preview(str(second))
    with svc.registry.atomic():
        svc.registry.move(saved["project_id"],"trash",expected_revision=0,reason="Keep",actor=None,changed_at="now",operation_id="move")
        svc.registry.commit()
    with pytest.raises(ValueError,match="changed"):
        svc.register(path=str(second),token=before["token"],action="link",target_project_id=saved["project_id"])
    assert len(svc.list_locations()) == 1


def test_source_alias_from_independent_import_remains_a_conflict_for_copied_folder(service):
    svc,root=service
    folders=[]
    for name in ["first","copy"]:
        folder=root/name;folder.mkdir();(folder/".connlab").mkdir()
        (folder/".connlab"/"manifest.json").write_text(json.dumps({"schema_version":1,"project_id":"c"*32,"dl_number":"DL-2026-01-007"}))
        folders.append(folder)
    original=svc.register(path=str(folders[0]),token=svc.preview(str(folders[0]))["token"],action="independent",management_number="RENAMED-007")
    preview=svc.preview(str(folders[1]))
    assert preview["conflicts"][0]["project_id"] == original["project_id"]
    with pytest.raises(ValueError,match="source|matching"):
        svc.register(path=str(folders[1]),token=preview["token"],action="register",management_number="ANOTHER")
    linked=svc.register(path=str(folders[1]),token=preview["token"],action="link",target_project_id=original["project_id"])
    assert linked["project_id"] == original["project_id"]


def test_hidden_source_alias_cannot_be_bypassed_by_linking_to_another_active_record(service):
    svc,root=service
    first=root/"first";first.mkdir();(first/".connlab").mkdir()
    data=json.dumps({"schema_version":1,"project_id":"d"*32,"dl_number":"DL-2026-01-008"})
    (first/".connlab"/"manifest.json").write_text(data)
    old=svc.register(path=str(first),token=svc.preview(str(first))["token"],action="independent",management_number="RENAMED")
    other=root/"other";other.mkdir()
    active=svc.register(path=str(other),token=svc.preview(str(other))["token"],action="register",management_number="ACTIVE")
    with svc.registry.atomic():
        svc.registry.move(old["project_id"],"trash",expected_revision=0,reason="Keep",actor=None,changed_at="now",operation_id="move")
        svc.registry.commit()
    copied=root/"copy";copied.mkdir();(copied/".connlab").mkdir();(copied/".connlab"/"manifest.json").write_text(data)
    with pytest.raises(ValueError,match="Restore"):
        svc.register(path=str(copied),token=svc.preview(str(copied))["token"],action="link",target_project_id=active["project_id"])
    assert len(svc.list_locations()) == 2


def test_conflict_preview_shows_real_registered_identity_separately_from_local_management_number(service):
    from backend.domain import LtrRecord,LtrStatus
    from backend.infrastructure.storage.repositories.records import LtrRecordRepository
    svc,root=service
    local=root/"local";local.mkdir()
    saved=svc.register(path=str(local),token=svc.preview(str(local))["token"],action="register",management_number="LEGACY-NUMBER")
    LtrRecordRepository(svc.locations.session).create(LtrRecord(ltr_id="registered",project_id=saved["project_id"],ltr_number="DL-2026-01-009",status=LtrStatus.REGISTERED))
    svc.registry.commit()
    candidate=root/"DL-2026-01-009 historical";candidate.mkdir()
    preview=svc.preview(str(candidate))
    conflict=preview["conflicts"][0]
    assert conflict["project_id"] == saved["project_id"]
    assert conflict["display_project_id"] == "DL-2026-01-009"
    assert conflict["number"] == "LEGACY-NUMBER"
    assert next(item for item in preview["targets"] if item["project_id"]==saved["project_id"])["display_project_id"] == "DL-2026-01-009"


