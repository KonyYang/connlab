from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.basic_project_workspace_service import BasicProjectWorkspaceService
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus
from backend.shared.config import OfficialWorkspaceSettings


class Store:
    def __init__(self):
        self.record = None

    def get_by_project(self, project_id):
        return self.record

    def save(self, record):
        self.record = record
        return record


def service(tmp_path):
    root = tmp_path / "output"
    root.mkdir()
    project = Project(project_id="P1", project_no="DL-2026-09-002A", product_name="Connector", requestor="Engineer", status=ProjectStatus.DRAFT)
    ltr = LtrRecord(ltr_id="L1", project_id="P1", ltr_number="DL-2026-09-002A", status=LtrStatus.REGISTERED, registered_on=date(2026, 9, 1))
    store = Store()
    value = BasicProjectWorkspaceService(
        projects=SimpleNamespace(get=lambda _: project), workspaces=store,
        ltrs=SimpleNamespace(list_by_project=lambda _: [ltr]),
        settings=OfficialWorkspaceSettings(local_workspace_root=root),
        data_dir=tmp_path / "data", collect_materials=None,
    )
    return value, store, project


def test_basic_creation_without_authorities_or_templates_and_idempotent_reuse(tmp_path):
    value, store, project = service(tmp_path)
    preview = value.preview("P1")
    assert preview["status"] == "ready"
    result = value.create("P1", preview["expected_context"], "request-1")
    assert result["directory_available"]
    folder = store.record.official_folder_path
    assert store.record.template_source_path is None
    assert store.record.creation_kind == "basic"
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        assert (folder / name).is_dir()
    manual = folder / "Test results" / "manual.txt"
    manual.write_text("operator bytes", encoding="utf-8")
    object.__setattr__(project, "product_name", "Changed description")
    again = value.create("P1", value.preview("P1")["expected_context"], "request-2")
    assert again["directory_available"]
    assert store.record.official_folder_path == folder
    assert manual.read_text(encoding="utf-8") == "operator bytes"


def test_unknown_existing_folder_requires_review_and_preserves_files(tmp_path):
    value, store, _ = service(tmp_path)
    preview = value.preview("P1")
    folder = Path(preview["official_project_folder_path"])
    folder.mkdir(parents=True)
    (folder / "manual.txt").write_text("keep", encoding="utf-8")
    preview = value.preview("P1")
    assert preview["status"] == "review_required"
    with pytest.raises(ValueError):
        value.create("P1", preview["expected_context"], "request")
    assert store.record is None
    result = value.create("P1", preview["expected_context"], "confirmed", confirm_existing=True)
    assert result["directory_available"]
    assert (folder / "manual.txt").read_text(encoding="utf-8") == "keep"


def test_changed_linked_identity_is_not_recreated(tmp_path):
    value, store, _ = service(tmp_path)
    value.create("P1", value.preview("P1")["expected_context"], "first")
    folder = store.record.official_folder_path
    folder.rename(folder.with_name("operator-moved"))
    preview = value.preview("P1")
    assert preview["status"] == "blocked"
    with pytest.raises(ValueError):
        value.create("P1", preview["expected_context"], "second")
    assert not folder.exists()


def test_directory_appearing_after_preview_is_not_silently_adopted(tmp_path, monkeypatch):
    from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspacePublisher
    value, store, _ = service(tmp_path)
    preview = value.preview("P1")
    target = Path(preview["official_project_folder_path"])
    original = BasicProjectWorkspacePublisher.directory
    def inject(self, path, **kwargs):
        if path == target and not target.exists():
            target.mkdir()
            (target / 'colleague.txt').write_text('keep', encoding='utf-8')
        return original(self, path, **kwargs)
    monkeypatch.setattr(BasicProjectWorkspacePublisher, 'directory', inject)
    with pytest.raises(ValueError, match='changed'):
        value.create('P1', preview['expected_context'], 'race')
    assert store.record is None
    assert (target / 'colleague.txt').read_text(encoding='utf-8') == 'keep'


def test_basic_resume_uses_durable_stage_and_preserves_manual_files(tmp_path, monkeypatch):
    from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspacePublisher
    value, store, _ = service(tmp_path)
    original = BasicProjectWorkspacePublisher.manifest
    def fail(*args):
        raise OSError('injected disconnect')
    monkeypatch.setattr(BasicProjectWorkspacePublisher, 'manifest', fail)
    with pytest.raises(OSError):
        value.create('P1', value.preview('P1')['expected_context'], 'resume')
    state = value.journal.read('P1')
    folder = Path(state['record']['official_folder_path'])
    (folder / 'manual.txt').write_text('keep', encoding='utf-8')
    monkeypatch.setattr(BasicProjectWorkspacePublisher, 'manifest', original)
    assert value.resume('P1', state['operation_id'])['directory_available']
    assert (folder / 'manual.txt').read_text(encoding='utf-8') == 'keep'


@pytest.mark.parametrize("changed", ["root", "ltr"])
def test_resume_refuses_changed_registered_inputs(tmp_path, monkeypatch, changed):
    from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspacePublisher
    value, store, _ = service(tmp_path)
    original = BasicProjectWorkspacePublisher.manifest
    monkeypatch.setattr(BasicProjectWorkspacePublisher, "manifest", lambda *_: (_ for _ in ()).throw(OSError("disconnect")))
    with pytest.raises(OSError):
        value.create("P1", value.preview("P1")["expected_context"], "interrupted")
    state = value.journal.read("P1")
    folder = Path(state["record"]["official_folder_path"])
    marker = folder / "manual.txt"
    marker.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(BasicProjectWorkspacePublisher, "manifest", original)
    if changed == "root":
        new_root = tmp_path / "other"
        new_root.mkdir()
        value.settings = OfficialWorkspaceSettings(local_workspace_root=new_root)
    else:
        value.ltrs = SimpleNamespace(list_by_project=lambda _: [LtrRecord(ltr_id="L2", project_id="P1", ltr_number="DL-2026-09-003", status=LtrStatus.REGISTERED, registered_on=date(2026, 9, 2))])
    with pytest.raises(ValueError, match="changed"):
        value.resume("P1", state["operation_id"])
    assert marker.read_text(encoding="utf-8") == "keep"
    assert store.record is None


def test_closed_project_retains_directory_availability_without_creation_permission(tmp_path):
    from backend.domain import ProjectLifecycleState
    value, _, project = service(tmp_path)
    value.create("P1", value.preview("P1")["expected_context"], "first")
    object.__setattr__(project, "lifecycle_state", ProjectLifecycleState.CLOSED)
    preview = value.preview("P1")
    assert preview["status"] == "blocked" and preview["directory_available"]
    with pytest.raises(ValueError):
        value.create("P1", preview["expected_context"], "second")


def test_draft_ltr_number_is_not_registered_directory_authority(tmp_path):
    value, store, _ = service(tmp_path)
    value.ltrs = SimpleNamespace(list_by_project=lambda _: [LtrRecord(ltr_id="draft", project_id="P1", ltr_number="DL-2026-09-002A", status=LtrStatus.DRAFT)])
    preview = value.preview("P1")
    assert preview["status"] == "blocked"
    assert any("registered LTR" in message for message in preview["blockers"])
    assert store.record is None
