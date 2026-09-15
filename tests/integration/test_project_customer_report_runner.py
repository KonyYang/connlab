from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import threading
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api import dependencies as deps
from backend.api.project_customer_report_runner import ProjectCustomerReportRunner
from backend.api.project_registry_access_guard import protect_project_mutations
from backend.api.routes_report_workspace import router
from backend.application.project_customer_report_job_service import ProjectCustomerReportJobService
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.models import ProjectModel, ProjectOfficialWorkspaceRecordModel, ExternalResourceModel
from backend.domain import ExternalResourceType
from backend.shared.config import Settings


def test_guard_handoff_worker_session_and_official_publication_are_serialized(tmp_path):
    engine = create_engine("sqlite:///" + str(tmp_path / "test.sqlite"))
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine)
    folder = tmp_path / "project"
    folder.mkdir()
    source = folder / "DL-2026-09-001 Qualification Test Report_Rev_A.docx"
    source.write_bytes(b"internal")
    template = tmp_path / "E-4515_F.docx"
    template.write_bytes(b"template")
    with sessions.begin() as session:
        session.add(ProjectModel(project_id="p", product_name="test", requestor="test", status="active"))
        session.add(ProjectOfficialWorkspaceRecordModel(workspace_id="w", project_id="p", dl_number="DL-2026-09-001", local_workspace_path=str(folder), source_book_path=str(folder), official_folder_path=str(folder), manifest_path=str(folder / "manifest"), template_source_path=str(tmp_path), created_at="2026-09-15"))
        session.add(ExternalResourceModel(resource_id="template", resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE.value, path=str(tmp_path), active=True, validation_status="valid"))
    entered = threading.Event()
    release = threading.Event()
    class Writer:
        def read_source_report_sha256(self, path):
            return None
        def generate_customer_report(self, *, source_path, template_path, output_path, progress):
            progress("formatting_document")
            entered.set()
            assert release.wait(10)
            output_path.write_bytes(b"customer")
            return output_path
    settings = Settings(data_dir=tmp_path / "data", projects_dir=folder, templates_dir=tmp_path, database_path=tmp_path / "test.sqlite")
    runner = ProjectCustomerReportRunner(session_factory=sessions, settings=settings, writer_factory=lambda root: Writer())
    pool = ThreadPoolExecutor(max_workers=1)
    jobs = ProjectCustomerReportJobService(root=tmp_path / "jobs", generate=runner, dispatch=pool.submit)
    app = FastAPI()
    app.include_router(protect_project_mutations(router))
    def request_session():
        with sessions() as session:
            yield session
    app.dependency_overrides[deps.get_session] = request_session
    app.dependency_overrides[deps.get_settings] = lambda: settings
    app.dependency_overrides[deps.get_project_customer_report_job_service] = lambda: jobs
    client = TestClient(app)
    base = "/api/projects/p/report-workspace/current-customer-report/jobs"
    payload = {"expected_internal_report_sha256": sha256(b"internal").hexdigest()}
    try:
        first = client.post(base, json=payload)
        assert first.status_code == 202, first.text
        assert entered.wait(10)
        assert client.get(base + "/latest").json()["stage"] == "formatting_document"
        blocked = client.post(base, json=payload)
        assert blocked.status_code == 409
        release.set()
        for _ in range(200):
            result = jobs.latest("p")
            if result["status"] in {"completed", "failed"}:
                break
            time.sleep(0.01)
        assert result["status"] == "completed", result
        assert result["result"]["mode"] == "official"
        assert (folder / "DL-2026-09-001-CR Qualification Test Report_Rev_A.docx").read_bytes() == b"customer"
        assert source.read_bytes() == b"internal"
        assert engine.pool.checkedout() == 0
    finally:
        release.set()
        pool.shutdown()
        engine.dispose()
