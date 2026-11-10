from pathlib import Path
from types import SimpleNamespace
import pytest

from backend.application.project_file_generation_sources import ProjectFileGenerationSources
from backend.application.basic_project_workspace_service import BasicProjectWorkspaceService


class Store:
    def __init__(self, value=None): self.value = value
    def get_by_project(self, _): return self.value
    def get_active_by_project(self, _): return self.value
    def get_latest_confirmed(self, _): return self.value


class Files:
    from backend.infrastructure.files.generation_journal import fingerprint
    from backend.infrastructure.files.recoverable_output_publisher import file_hash as hash, file_identity as identity, require_safe_output_path as require_safe
    fingerprint = staticmethod(fingerprint)
    hash = staticmethod(hash)
    identity = staticmethod(identity)
    require_safe = staticmethod(require_safe)
    is_dir = staticmethod(lambda path: path.is_dir())
    is_file = staticmethod(lambda path: path.is_file())
    is_empty = staticmethod(lambda path: not any(path.iterdir()))
    size = staticmethod(lambda path: path.stat().st_size)


def adapter(tmp_path, *, matrix=None, workspace=None):
    return ProjectFileGenerationSources(
        workspaces=Store(workspace), basic_workspace=SimpleNamespace(
            _record=lambda _: workspace, _verify_record=BasicProjectWorkspaceService._verify_record),
        confirmed=Store(matrix), basic=Store(), fees=None, resources=None,
        settings=SimpleNamespace(), schedules=None, input_context=None, staging=None,
        application=None, llcr=None, llcr_writer=None, ir=None,
        outputs=None, commit=lambda: None, files=Files())


def linked(tmp_path):
    local = tmp_path / "DL-2026-11-001"
    official = local / "DL-2026-11-001 Connector Test"
    for folder in (official, official / "Submitted Material", official / "Test results", local / ".connlab", local / "Source Book"):
        folder.mkdir(parents=True, exist_ok=True)
    manifest = local / ".connlab" / "manifest.json"
    import json
    manifest.write_text(json.dumps({"schema_version": 2,"project_id":"P1", "dl_number":"DL-2026-11-001",
        "official_project_folder_path":str(official)}),encoding="utf-8")
    return SimpleNamespace(project_id="P1", dl_number="DL-2026-11-001",local_workspace_path=local,
        official_folder_path=official,manifest_path=manifest,source_book_path=local/"Source Book")


def test_test_status_needs_only_active_confirmed_matrix(tmp_path):
    record = linked(tmp_path)
    sources = adapter(tmp_path, workspace=record, matrix=SimpleNamespace(version=SimpleNamespace(
        confirmed_matrix_id="matrix-1",confirmed_revision=2)))
    item = sources.source("P1", "test_status")
    assert item.status == "ready"
    assert item.target == record.official_folder_path / "Submitted Material" / "DL-2026-11-001 test status.xlsx"
    assert item.source_token
    assert sources.source("P1", "fee_form").status == "blocked"


def test_unlinked_workspace_cannot_be_created_by_file_generation(tmp_path):
    sources = adapter(tmp_path)
    with pytest.raises(ValueError, match="existing"):
        sources.workspace("P1")
    assert not tuple(tmp_path.iterdir())


def test_workspace_token_binds_manifest_and_directories_not_business_file_contents(tmp_path):
    record = linked(tmp_path)
    sources = adapter(tmp_path, workspace=record)
    before = sources.workspace("P1")["token"]
    (record.official_folder_path / "operator.txt").write_text("operator change",encoding="utf-8")
    assert sources.workspace("P1")["token"] == before
    record.manifest_path.write_text(record.manifest_path.read_text(encoding="utf-8")+" ",encoding="utf-8")
    assert sources.workspace("P1")["token"] != before


def test_feedback_is_independent_of_fee_and_tracks_only_its_template_and_schedule(tmp_path):
    from backend.application.project_basic_information_output import ConfirmedBasicInformationSnapshot
    from backend.application.project_file_generation_staging import RequiredFormsInputContextReader
    record = linked(tmp_path)
    sources = adapter(tmp_path, workspace=record, matrix=SimpleNamespace(version=SimpleNamespace(
        confirmed_matrix_id="matrix-1", confirmed_revision=2)))
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    template = template_folder / "FDQF-E-4243 Customer Feedback Form.xlsx"
    template.write_bytes(b"feedback template")
    sources.resources = SimpleNamespace(get_by_type=lambda _: SimpleNamespace(active=True,path=template_folder))
    sources.basic.value = ConfirmedBasicInformationSnapshot("P1", 1,
        {"project_leader":"Even Yang"}, "basic-source", None, None)
    sources.schedules = Store(SimpleNamespace(context_signature="schedule-1"))
    sources.input_context = RequiredFormsInputContextReader(sources.resources, sources.settings, sources.schedules, None)
    first = sources.source("P1", "customer_feedback_form")
    status = sources.source("P1", "test_status")
    assert first.status == "ready"
    assert first.target.name == "DL-2026-11-001 Customer Feedback Form_Even Yang.xlsx"
    assert sources.source("P1", "fee_form").status == "blocked"
    template.write_bytes(b"changed feedback template")
    assert sources.source("P1", "customer_feedback_form").source_token != first.source_token
    assert sources.source("P1", "test_status").source_token == status.source_token


def test_contact_record_rejects_legacy_count_projection_without_explicit_profile(tmp_path):
    record = linked(tmp_path)
    sources = adapter(tmp_path, workspace=record, matrix=SimpleNamespace(version=SimpleNamespace(
        confirmed_matrix_id="matrix-1", confirmed_revision=1)))
    sources.llcr = SimpleNamespace(preview=lambda *_: SimpleNamespace(status="ready", sections=(object(),),
        diagnostics=(), preview_fingerprint="legacy-count", point_profile_fingerprint=None))
    item = sources.source("P1", "llcr_record")
    assert item.status == "blocked"
    assert "Point Profile" in item.message


def test_registration_uses_frozen_authority_and_is_idempotent_after_sources_disappear(tmp_path):
    from backend.application.project_folder_required_forms_service import compute_sha256
    from backend.infrastructure.files.recoverable_output_publisher import file_identity
    from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
    record = linked(tmp_path)
    sources = adapter(tmp_path,workspace=record)
    target = record.official_folder_path / "Submitted Material" / "test status.xlsx"
    target.write_bytes(b"published result")
    records,commits = [],[]
    class Outputs:
        def list_records(self,_): return records
        def register_output(self,command):
            records.append(SimpleNamespace(output_record_id="output-1",**__import__("dataclasses").asdict(command)))
            return records[-1]
    sources.outputs = Outputs()
    sources.commit = lambda: commits.append(True)
    item = {"key":"test_status","target":str(target),"output_kind":"test_status", "source_token":"old-token",
        "registration":{"draft_id":"old-draft", "output_kind":"test_status", "source_context_signature":"frozen-matrix-1"}}
    effect = {"target":str(target), "sha":compute_sha256(target), "identity":file_identity(target), "phase":"published"}
    assert sources.register({"project_id":"P1"},item,effect) == "output-1"
    assert sources.register({"project_id":"P1"},item,effect) == "output-1"
    assert len(records) == 1
    assert records[0].draft_id == "old-draft"
    assert records[0].source_context_signature == "frozen-matrix-1"
    target.write_bytes(b"operator replacement")
    with pytest.raises(ValueError,match="changed"):
        sources.register({"project_id":"P1"},item,effect)


def test_composed_sources_read_without_creating_workspace_or_generated_roots(tmp_path):
    from sqlalchemy.orm import Session
    from backend.api.project_file_generation_composition import build_components
    from backend.infrastructure.storage.database import create_engine, init_db
    from backend.shared.config import Settings
    engine = create_engine(f"sqlite:///{(tmp_path / 'isolated.sqlite').as_posix()}")
    init_db(engine)
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",database_path=tmp_path / "isolated.sqlite")
    try:
        with Session(engine) as session:
            sources = build_components(session, settings)
            assert sources.source("missing-project","test_status").status == "blocked"
            assert not session.new
        assert not (tmp_path / "data").exists()
        assert not (tmp_path / "projects").exists()
        assert not (tmp_path / "templates").exists()
    finally:
        engine.dispose()


def test_real_test_status_generator_stays_inside_operation_stage_and_registers_once(tmp_path):
    from sqlalchemy.orm import Session
    from openpyxl import load_workbook
    from backend.application.confirmed_matrix_test_status_workbook_generation_service import ConfirmedMatrixTestStatusWorkbookGenerationService
    from backend.application.project_file_generation_staging import RequiredFormsStagingGenerator
    from backend.application.matrix_editor_llcr_cr_record_projection import _draft_snapshot, MatrixEditorLlcrCrRecordGroupInput as Group, MatrixEditorLlcrCrRecordRowInput as Row
    from backend.infrastructure.office.test_status_workbook_gateway import TestStatusWorkbookGateway
    from backend.infrastructure.storage.database import create_engine, init_db
    from backend.infrastructure.storage.repositories.project import ProjectRepository
    from backend.infrastructure.storage.repositories import ProjectTestPlanDraftRepository
    from backend.infrastructure.storage.repositories.project_output_record import ProjectOutputRecordRepository
    from backend.application.project_output_record_service import ProjectOutputRecordService
    from backend.domain import Project, ProjectStatus
    from backend.infrastructure.files.recoverable_output_publisher import file_identity, file_hash
    record = linked(tmp_path)
    matrix = _draft_snapshot(project_id="P1",groups=(Group("g1","1","2"),),
        rows=(Row("Visual",group_values={"g1":"1"}),),point_profile=None,point_overrides=())
    sources = adapter(tmp_path,workspace=record,matrix=matrix)
    sources.staging = RequiredFormsStagingGenerator(settings=SimpleNamespace(data_dir=tmp_path/"unused"),
        fee_template_resource_store=None,test_record_service=None,fee_export_service=None,customer_feedback_service=None,
        test_status_service=ConfirmedMatrixTestStatusWorkbookGenerationService(confirmed_store=Store(matrix),writer=TestStatusWorkbookGateway()))
    stage = Path(sources.workspace("P1")["stage_parent"]) / "operation" / "test-status"
    stage.mkdir(parents=True)
    preview = sources.source("P1","test_status")
    output = sources.generate("P1","test_status",stage,preview.target.name)
    assert output.parent == stage
    assert not preview.target.exists()
    workbook = load_workbook(output)
    try:
        assert any("Visual" in str(cell.value) for sheet in workbook for row in sheet for cell in row)
    finally:
        workbook.close()
    engine = create_engine(f"sqlite:///{(tmp_path/'outputs.sqlite').as_posix()}")
    init_db(engine)
    try:
        with Session(engine) as session:
            ProjectRepository(session).create(Project(project_id="P1",project_no="DL-2026-11-001",product_name="Connector",requestor="Engineer",status=ProjectStatus.DRAFT))
            session.commit()
            sources.outputs = ProjectOutputRecordService(project_store=ProjectRepository(session),
                draft_store=ProjectTestPlanDraftRepository(session),output_store=ProjectOutputRecordRepository(session))
            sources.commit = session.commit
            registration = sources.registration("P1","test_status")
            output.rename(preview.target)
            item = {"key":"test_status","target":str(preview.target),"output_kind":preview.output_kind,"registration":registration}
            effect = {"target":str(preview.target),"sha":file_hash(preview.target),"identity":file_identity(preview.target)}
            first = sources.register({"project_id":"P1"},item,effect)
            sources.confirmed.value = None
            assert sources.register({"project_id":"P1"},item,effect) == first
            assert len(sources.outputs.list_records("P1")) == 1
    finally:
        engine.dispose()


def test_missing_test_results_does_not_block_submitted_test_status(tmp_path):
    record = linked(tmp_path)
    (record.official_folder_path / "Test results").rmdir()
    record.source_book_path.rmdir()
    sources = adapter(tmp_path, workspace=record, matrix=SimpleNamespace(version=SimpleNamespace(
        confirmed_matrix_id="matrix-1",confirmed_revision=1)))
    assert sources.workspace("P1")["token"]
    assert sources.source("P1","test_status").status == "ready"


def test_missing_source_preserves_known_target_for_skip_choice(tmp_path):
    record = linked(tmp_path)
    target = record.official_folder_path / "Submitted Material" / "DL-2026-11-001 test status.xlsx"
    target.write_bytes(b"existing operator file")
    sources = adapter(tmp_path,workspace=record)
    item = sources.source("P1","test_status")
    assert item.status == "blocked"
    assert item.target == target
    assert target.read_bytes() == b"existing operator file"


def test_output_parent_identity_is_per_item_instead_of_shared_workspace_context(tmp_path):
    record = linked(tmp_path)
    sources = adapter(tmp_path,workspace=record,matrix=SimpleNamespace(version=SimpleNamespace(
        confirmed_matrix_id="matrix-1",confirmed_revision=1)))
    shared = sources.workspace("P1")["token"]
    before = sources.source("P1","test_status").source_token
    parent = record.official_folder_path / "Submitted Material"
    parent.rename(parent.with_name("original submitted"))
    parent.mkdir()
    assert sources.workspace("P1")["token"] == shared
    assert sources.source("P1","test_status").source_token != before


def test_contact_record_does_not_promote_separate_profile_into_matrix_test_points(tmp_path):
    record = linked(tmp_path)
    sources = adapter(tmp_path,workspace=record,matrix=SimpleNamespace(version=SimpleNamespace(
        confirmed_matrix_id="matrix-1",confirmed_revision=1,point_profile=None)))
    sources.llcr = SimpleNamespace(preview=lambda *_: SimpleNamespace(status="ready",sections=(object(),),
        diagnostics=(),preview_fingerprint="separate-profile",point_profile_fingerprint="confirmed-separate-profile"))
    item = sources.source("P1","llcr_record")
    assert item.status == "blocked"
    assert item.target == record.official_folder_path / "Test results" / "DL-2026-11-001 LLCR Record.xlsx"
    assert "Matrix" in item.message
