from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_customer_report_job_service
from backend.api.routes_report_workspace import router
from backend.application.project_customer_report_job_service import ProjectCustomerReportJobService
from backend.application.customer_report_projection_service import CustomerReportGenerationResult


def test_async_api_retains_result_and_download_after_refresh(tmp_path):
    pending = []
    def generate(project, source, customer, root, progress):
        progress("saving_document")
        path = root / "result.docx"
        path.write_bytes(b"customer")
        return CustomerReportGenerationResult(project, "managed_download", path.name, path, "b"*64, source, True, None)
    jobs = ProjectCustomerReportJobService(root=tmp_path, generate=generate, dispatch=pending.append)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_project_customer_report_job_service] = lambda: jobs
    client = TestClient(app)
    base = "/api/projects/p/report-workspace/current-customer-report/jobs"
    started = client.post(base, json={"expected_internal_report_sha256": "a"*64})
    assert started.status_code == 202
    operation = started.json()["operation_id"]
    assert client.get(base + "/latest").json()["operation_id"] == operation
    pending.pop()()
    assert client.get(base + "/" + operation).json()["result"]["file_name"] == "result.docx"
    for _ in range(2):
        response = client.get(base + "/" + operation + "/download")
        assert response.status_code == 200
        assert response.content == b"customer"
    assert client.get(base + "/unknown").status_code == 410
    assert client.get(base.replace("/p/", "/other/") + "/" + operation).status_code == 410
