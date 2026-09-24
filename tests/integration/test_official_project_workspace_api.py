from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from hashlib import sha256
import runpy

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import Session

from backend.api.dependencies import get_official_project_workspace_service, get_settings
from backend.shared.config import OfficialWorkspaceSettings, Settings
from backend.api.main import app
from backend.api import dependencies as deps
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    LtrRecord,
    LtrStatus,
    Project,
    ProjectStatus,
)
from backend.application.official_project_workspace_service import (
    OfficialProjectWorkspaceService,
    OfficialWorkspaceConflictOption,
    OfficialWorkspaceCreateError,
    OfficialWorkspaceCreateResult,
    OfficialWorkspaceNotFoundError,
    OfficialWorkspacePreview,
    OfficialWorkspaceRecord,
)
from backend.infrastructure.storage.models import (
    FileAssetModel, ProjectFolderRecordModel, ProjectOutputRecordModel,
    ProjectRequestMaterialCollectionModel, ProjectRequestMaterialCollectionItemModel,
    ProjectModel,
)
from backend.infrastructure.official_workspace_manifest import stable_folder_identity


@pytest.fixture(autouse=True)
def _isolated_generation_storage(tmp_path):
    app.dependency_overrides[get_settings] = lambda: Settings(
        data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates", database_path=tmp_path / "fixture.sqlite")
    yield
    app.dependency_overrides.pop(get_settings, None)


def test_real_workspace_preview_tracks_confirmations_not_basic_drafts(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    client, engine, sessions = fixture["_client"](tmp_path)
    try:
        fixture["_seed_project"]("P1", tmp_path)
        template, output = tmp_path / "template", tmp_path / "output"
        output.mkdir()
        for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
            (template / name).mkdir(parents=True)
        with sessions() as session:
            deps.LtrRecordRepository(session).create(
                LtrRecord("ltr", "P1", "DL-2026-08-079", LtrStatus.REGISTERED)
            )
            resources = deps.ExternalResourceRepository(session)
            resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
            resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
            session.commit()
        values = {
            "dl_number": "DL-2026-08-079", "project_type": "NPD",
            "product_description": "Confirmed connector", "test_item": "Mechanical Testing",
            "tests_to_be_performed": "Mechanical Testing",
            "requested_by": "Alice", "project_leader": "Engineer", "lab_performing_tests": "Dongguan",
        }
        response = client.post("/api/projects/P1/basic-information/confirm", json={"values": values, "confirmed_by": "operator"})
        assert response.status_code == 200, response.text

        def folder_name():
            response = client.get("/api/projects/P1/official-workspace/preview")
            assert response.status_code == 200, response.text
            return Path(response.json()["official_project_folder_path"]).name

        original = "DL-2026-08-079 Confirmed connector Mechanical Testing"
        assert folder_name() == original
        revised = {**values, "product_description": "Customized PBU Connector with 14P",
                   "test_item": "Solderability  and Mechanical Testing"}
        response = client.put("/api/projects/P1/basic-information/draft", json={"values": revised})
        assert response.status_code == 200, response.text
        assert folder_name() == original
        response = client.post("/api/projects/P1/basic-information/confirm", json={"values": revised, "confirmed_by": "operator"})
        assert response.status_code == 200, response.text
        assert folder_name() == (
            "DL-2026-08-079 Customized PBU Connector with 14P Solderability and Mechanical Testing"
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_relocation_recovers_sqlite_commit_failure_and_rebinds_live_paths(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    client, engine, sessions = fixture["_client"](tmp_path)
    try:
        fixture["_seed_project"]("P1", tmp_path)
        template, output = tmp_path / "template", tmp_path / "output"
        output.mkdir()
        for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
            (template / name).mkdir(parents=True)
        with sessions() as session:
            deps.LtrRecordRepository(session).create(
                LtrRecord("ltr", "P1", "DL-2026-08-079", LtrStatus.REGISTERED)
            )
            resources = deps.ExternalResourceRepository(session)
            resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
            resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
            session.commit()
        values = {
            "dl_number": "DL-2026-08-079", "project_type": "NPD",
            "product_description": "Original connector", "test_item": "Qualification test",
            "tests_to_be_performed": "Qualification test",
            "requested_by": "Alice", "project_leader": "Engineer", "lab_performing_tests": "Dongguan",
        }
        confirmed = client.post("/api/projects/P1/basic-information/confirm", json={
            "values": values, "confirmed_by": "operator",
        })
        assert confirmed.status_code == 200, confirmed.text
        created = client.post("/api/projects/P1/official-workspace/create")
        assert created.status_code == 201, created.text
        source = Path(created.json()["official_project_folder_path"])
        report = source / "Test results" / "operator.docx"
        report.write_bytes(b"operator report")
        edited_asset = source / "Test results" / "edited.docx"
        edited_asset.write_bytes(b"original")
        edited_digest = sha256(edited_asset.read_bytes()).hexdigest()
        edited_asset.write_bytes(b"operator edit")
        missing_asset = source / "Test results" / "removed.docx"
        missing_folder = source / "Test results" / "Removed By Operator"
        application_form = source / "Submitted Material" / "application.docx"
        application_form.write_bytes(b"submitted application")
        application_digest = sha256(application_form.read_bytes()).hexdigest()
        digest = sha256(report.read_bytes()).hexdigest()
        with sessions() as session:
            session.add(FileAssetModel(
                asset_id="asset-1", project_id="P1", asset_type="attachment",
                path=str(report), sha256=digest,
            ))
            session.add(FileAssetModel(
                asset_id="edited-asset", project_id="P1", asset_type="attachment",
                path=str(edited_asset), sha256=edited_digest,
            ))
            session.add(FileAssetModel(
                asset_id="missing-asset", project_id="P1", asset_type="attachment",
                path=str(missing_asset), sha256=digest,
            ))
            session.add(ProjectFolderRecordModel(
                folder_id="missing-folder", project_id="P1", folder_path=str(missing_folder),
            ))
            session.add(ProjectOutputRecordModel(
                output_record_id="old-output", project_id="P1", draft_id=None,
                draft_version=None, output_kind="test_record_form", output_path=str(report),
                output_sha256=digest, output_size_bytes=report.stat().st_size,
                source_context_signature="confirmed-fixture", status="current",
                source="system_generated", created_at="2026-09-24T00:00:00+00:00",
                updated_at="2026-09-24T00:00:00+00:00",
            ))
            for collection_id, created_at in (
                ("prior-materials", "2026-09-23T00:00:00+00:00"),
                ("current-materials", "2026-09-24T00:00:00+00:00"),
            ):
                session.add(ProjectRequestMaterialCollectionModel(
                    collection_id=collection_id, project_id="P1", workspace_id="workspace-1",
                    status="completed", item_count=1, copied_count=1,
                    already_present_count=0, conflict_count=0, skipped_count=0,
                    missing_source_count=0, created_at=created_at, updated_at=created_at,
                    warnings_json="[]",
                ))
                session.add(ProjectRequestMaterialCollectionItemModel(
                    item_id=f"{collection_id}-item", collection_id=collection_id,
                    project_id="P1", source_asset_id="asset-1",
                    source_asset_type="application_form", source_role="selected_application_form",
                    dedupe_key=collection_id, source_path=str(application_form),
                    original_name="application.docx", target_area="submitted_material",
                    target_path=str(application_form), status="copied", action="copy",
                    review_required=False, size_bytes=application_form.stat().st_size,
                    sha256=application_digest,
                ))
            planned_target = source / "Submitted Material" / "missing-optional.docx"
            session.add(ProjectRequestMaterialCollectionItemModel(
                item_id="current-materials-skipped", collection_id="current-materials",
                project_id="P1", source_asset_id="missing-asset",
                source_asset_type="application_form", source_role="other",
                dedupe_key="skipped-material", source_path=str(tmp_path / "missing-optional.docx"),
                original_name="missing-optional.docx", target_area="submitted_material",
                target_path=str(planned_target), status="missing_source", action="skip",
                review_required=True, size_bytes=None, sha256=None,
            ))
            session.add(ProjectOutputRecordModel(
                output_record_id="unverified-output", project_id="P1", draft_id=None,
                draft_version=None, output_kind="customer_report", output_path=str(report),
                output_sha256=None, output_size_bytes=None,
                source_context_signature="old-fixture", status="current",
                source="system_generated", created_at="2026-09-24T00:00:00+00:00",
                updated_at="2026-09-24T00:00:00+00:00",
            ))
            session.commit()
        revised = {**values, "product_description": "Updated connector"}
        confirmed = client.post("/api/projects/P1/basic-information/confirm", json={
            "values": revised, "confirmed_by": "operator",
        })
        assert confirmed.status_code == 200, confirmed.text
        reviewed = client.get("/api/projects/P1/official-workspace/relocation/preview")
        assert reviewed.status_code == 200, reviewed.text
        assert reviewed.json()["status"] == "rename_available"
        token = reviewed.json()["expected_context"]
        application_form.write_bytes(b"operator changed placed material")
        preflight_blocked = client.post("/api/projects/P1/official-workspace/relocation", json={
            "action": "rename_to_confirmed", "expected_context": token,
        })
        assert preflight_blocked.status_code == 409, preflight_blocked.text
        assert source.is_dir()
        assert not (source.parent / "DL-2026-08-079 Updated connector Qualification test").exists()
        application_form.write_bytes(b"submitted application")
        pending_preflight = client.get("/api/projects/P1/official-workspace/relocation/preview")
        assert pending_preflight.json()["status"] == "interrupted"
        failed_once = False

        def fail_first_commit(_session):
            nonlocal failed_once
            if not failed_once:
                failed_once = True
                raise OSError("simulated SQLite commit interruption")

        event.listen(Session, "before_commit", fail_first_commit)
        try:
            failed = client.post("/api/projects/P1/official-workspace/relocation", json={
                "action": "resume", "expected_context": pending_preflight.json()["expected_context"],
            })
        finally:
            event.remove(Session, "before_commit", fail_first_commit)
        assert failed.status_code == 409, failed.text
        pending = client.get("/api/projects/P1/official-workspace/relocation/preview")
        assert pending.status_code == 200, pending.text
        assert pending.json()["status"] == "interrupted"
        resumed = client.post("/api/projects/P1/official-workspace/relocation", json={
            "action": "resume", "expected_context": pending.json()["expected_context"],
        })
        assert resumed.status_code == 200, resumed.text
        target = Path(resumed.json()["official_project_folder_path"])
        assert target.name == "DL-2026-08-079 Updated connector Qualification test"
        assert (target / "Test results" / "operator.docx").read_bytes() == b"operator report"
        assert not source.exists()
        with sessions() as session:
            asset = session.get(FileAssetModel, "asset-1")
            assert session.get(FileAssetModel, "edited-asset").path == str(edited_asset)
            assert session.get(FileAssetModel, "missing-asset").path == str(missing_asset)
            assert session.get(ProjectFolderRecordModel, "missing-folder").folder_path == str(missing_folder)
            records = session.scalars(select(ProjectOutputRecordModel).where(
                ProjectOutputRecordModel.project_id == "P1"
            ).order_by(ProjectOutputRecordModel.created_at)).all()
            assert asset.path == str(target / "Test results" / "operator.docx")
            assert len(records) == 4
            assert sum(record.output_path == str(report) for record in records) == 2
            relocated = [record for record in records if record.output_path == str(target / "Test results" / "operator.docx")]
            assert len(relocated) == 2
            assert {record.output_kind: record.status for record in relocated} == {
                "test_record_form": "current", "customer_report": "failed",
            }
            current_item = session.get(ProjectRequestMaterialCollectionItemModel, "current-materials-item")
            prior_item = session.get(ProjectRequestMaterialCollectionItemModel, "prior-materials-item")
            assert current_item.target_path == str(target / "Submitted Material" / "application.docx")
            assert prior_item.target_path == str(application_form)
            assert session.get(
                ProjectRequestMaterialCollectionItemModel, "current-materials-skipped"
            ).target_path == str(planned_target)
            session.get(ProjectModel, "P1").lifecycle_state = "closed"
            session.commit()
        rejected = client.post("/api/projects/P1/official-workspace/relocation", json={
            "action": "keep_current_name", "expected_context": "stale-preview",
        })
        assert rejected.status_code == 409, rejected.text
        assert "closed" in rejected.json()["detail"].lower()
        assert target.is_dir()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_relocation_database_commit_rejects_replaced_target_directory(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    _client, engine, sessions = fixture["_client"](tmp_path)
    try:
        fixture["_seed_project"]("P1", tmp_path)
        workspace = tmp_path / "output" / "DL-2026-08-079"
        source = workspace / "DL-2026-08-079 Original"
        target = workspace / "DL-2026-08-079 Confirmed"
        source.mkdir(parents=True)
        (workspace / "Source Book").mkdir()
        record = OfficialWorkspaceRecord(
            "workspace-1", "P1", "DL-2026-08-079", workspace,
            workspace / "Source Book", source,
            workspace / ".connlab" / "manifest.json", tmp_path / "template",
            "2026-09-24T00:00:00+00:00",
        )
        with sessions() as session:
            deps.ProjectOfficialWorkspaceRepository(session).save(record)
            session.commit()
        source.rename(target)
        expected_identity = stable_folder_identity(target)
        retained = workspace / "retained-original"
        target.rename(retained)
        target.mkdir()
        (target / "foreign.txt").write_text("foreign", encoding="utf-8")

        with sessions() as session:
            repository = deps.ProjectOfficialWorkspaceRepository(session)
            with pytest.raises(ValueError, match="identity|changed"):
                repository.publish_relocation(
                    replace(record, official_folder_path=target), source=source,
                    target=target, operation_id="replacement-race",
                    expected_identity=expected_identity,
                )
            assert repository.get_by_project("P1").official_folder_path == source
        assert (target / "foreign.txt").read_text(encoding="utf-8") == "foreign"
        assert retained.is_dir()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_official_workspace_preview_api_returns_typed_preview() -> None:
    service = _FakeWorkspaceService(
        preview=OfficialWorkspacePreview(
            project_id="P1",
            dl_number="DL-2025-11-074",
            local_workspace_root=Path("D:/Projects"),
            local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
            source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
            template_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
            official_folder_path=Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"),
            manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
            template_root_mode="template_root",
            status="ready",
            blockers=(),
            warnings=("Public Project locations is not configured; upload readiness will be checked later.",),
            planned_paths=(Path("D:/Projects/DL-2025-11-074"),),
            conflict_paths=(),
            conflict_options=(),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["status"] == "ready"
    assert payload["dl_number"] == "DL-2025-11-074"
    assert payload["warnings"][0].startswith("Public Project locations")
    assert payload["conflict_paths"] == []
    assert payload["conflict_options"] == []


def test_official_workspace_preview_api_returns_conflict_for_non_object_manifest(
    tmp_path: Path,
) -> None:
    root = tmp_path / "workspaces"
    manifest = root / "DL-2025-11-074" / ".connlab" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("[]", encoding="utf-8")
    project = Project(
        project_id="P1",
        project_no="DL-2025-11-074",
        product_name="Connector",
        requestor="Operator",
        status=ProjectStatus.CONFIRMED,
    )
    ltr = LtrRecord(
        ltr_id="ltr-1",
        project_id="P1",
        ltr_number="DL-2025-11-074",
        status=LtrStatus.REGISTERED,
    )

    class Projects:
        def get(self, project_id):
            return project if project_id == "P1" else None

    class Workspaces:
        def get_by_project(self, _project_id):
            return None

        def save(self, record):
            return record

    class Ltrs:
        def list_by_project(self, project_id):
            return [ltr] if project_id == "P1" else []

    service = OfficialProjectWorkspaceService(
        Projects(),
        Workspaces(),
        OfficialWorkspaceSettings(root, None, None),
        ltr_repository=Ltrs(),
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    try:
        response = TestClient(app).get("/api/projects/P1/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "conflict"
    assert "cannot be read" in response.json()["blockers"][0]


def test_official_workspace_preview_api_returns_conflict_options() -> None:
    conflict_path = Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test")
    service = _FakeWorkspaceService(
        preview=OfficialWorkspacePreview(
            project_id="P1",
            dl_number="DL-2025-11-074",
            local_workspace_root=Path("D:/Projects"),
            local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
            source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
            template_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
            official_folder_path=conflict_path,
            manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
            template_root_mode="template_root",
            status="exists",
            blockers=(f"Official project folder already exists: {conflict_path}",),
            warnings=(),
            planned_paths=(Path("D:/Projects/DL-2025-11-074"), conflict_path),
            conflict_paths=(conflict_path,),
            conflict_options=(
                OfficialWorkspaceConflictOption(
                    key="backup_and_recreate",
                    label="Backup and Rebuild",
                    description="Move the existing folder to a timestamped backup first.",
                ),
            ),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "exists"
    assert payload["conflict_paths"] == [str(conflict_path)]
    assert payload["conflict_options"][0]["key"] == "backup_and_recreate"


def test_official_workspace_create_api_returns_created_paths() -> None:
    record = OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-2025-11-074",
        local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
        source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
        official_folder_path=Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"),
        manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
        template_source_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
        created_at="2026-06-12T00:00:00+00:00",
    )
    service = _FakeWorkspaceService(
        create=OfficialWorkspaceCreateResult(
            record=record,
            created_paths=(record.local_workspace_path, record.official_folder_path),
            warnings=(),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post(
            "/api/projects/P1/official-workspace/create",
            json={"conflict_strategy": "backup_and_recreate"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["workspace_id"] == "W1"
    assert payload["official_project_folder_path"].endswith("Qualification test")
    assert len(payload["created_paths"]) == 2
    assert service.created_with_strategy == "backup_and_recreate"


def test_official_workspace_adopt_api_uses_identity_only_service_action() -> None:
    record = OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-2025-11-074",
        local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
        source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
        official_folder_path=Path(
            "D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"
        ),
        manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
        template_source_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
        created_at="2026-06-12T00:00:00+00:00",
    )
    service = _FakeWorkspaceService(
        adopt=OfficialWorkspaceCreateResult(
            record=record,
            created_paths=(record.manifest_path,),
            warnings=(),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    try:
        response = TestClient(app).post("/api/projects/P1/official-workspace/adopt")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert response.json()["workspace_id"] == "W1"
    assert service.adopted_project_id == "P1"


def test_official_workspace_create_blocked_returns_409_without_touching_operator_tree(
    tmp_path: Path,
) -> None:
    operator_folder = tmp_path / "existing-project"
    operator_folder.mkdir()
    operator_file = operator_folder / "completed-report.docx"
    operator_file.write_bytes(b"retained")
    before = tuple((path.name, path.stat().st_size) for path in operator_folder.iterdir())
    service = _FakeWorkspaceService(
        error=OfficialWorkspaceCreateError(
            "Existing project folder is ready to link. Use Link existing folder."
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/official-workspace/create")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "Link existing folder" in response.json()["detail"]
    assert tuple((path.name, path.stat().st_size) for path in operator_folder.iterdir()) == before
    assert operator_file.read_bytes() == b"retained"


def test_official_workspace_missing_project_returns_404() -> None:
    service = _FakeWorkspaceService(error=OfficialWorkspaceNotFoundError("Project not found: P404"))
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P404/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


class _FakeWorkspaceService:
    def __init__(
        self,
        *,
        preview: OfficialWorkspacePreview | None = None,
        create: OfficialWorkspaceCreateResult | None = None,
        adopt: OfficialWorkspaceCreateResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview
        self._create = create
        self._adopt = adopt
        self._error = error
        self.adopted_project_id: str | None = None

    def preview(self, project_id: str) -> OfficialWorkspacePreview:
        if self._error:
            raise self._error
        assert self._preview is not None
        return self._preview

    def create(
        self,
        project_id: str,
        conflict_strategy: str | None = None,
    ) -> OfficialWorkspaceCreateResult:
        if self._error:
            raise self._error
        assert self._create is not None
        self.created_with_strategy = conflict_strategy
        return self._create

    def adopt_existing(self, project_id: str) -> OfficialWorkspaceCreateResult:
        if self._error:
            raise self._error
        assert self._adopt is not None
        self.adopted_project_id = project_id
        return self._adopt
