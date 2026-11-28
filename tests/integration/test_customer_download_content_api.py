"""Use retained test Word documents, temporary project registration and a substitute Word converter."""
from hashlib import sha256
from io import BytesIO

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import pytest

from backend.api import dependencies as deps
from backend.api.main import app
from backend.application.tools_customer_report_job_service import ToolsCustomerReportJobService
from backend.application.tools_service import ToolsService
from backend.infrastructure.office.customer_report_notices import read_customer_notices
from tests.integration.test_internal_report_generation_api import lab, official_report
from tests.integration.test_report_authoring_api import BASE, upload


TOOLS = "/api/tools/customer-report"
INSPECT_PROJECT = "/api/projects/P1/report-workspace/customer-download/inspect"
NOTICE = "7. EQUIPMENT: check the source heading against the template."


def internal_report():
    document = Document()
    document.sections[0].header.paragraphs[0].text = "DL-2026-05-001"
    document.sections[0].footer.paragraphs[0].text = "E-3707"
    document.add_paragraph("LABORATORY TEST REPORT")
    document.add_paragraph("3. SAMPLE DESCRIPTION")
    table = document.add_table(rows=0, cols=3)
    for row in (("Description", "Part #", "Contact Base Material"), ("Fixture PCB", "PCB-19", "C11000")):
        for cell, value in zip(table.add_row().cells, row):
            cell.text = value
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


class WordBoundary:
    def generate_customer_report(self, *, source_path, template_path, output_path, lineage_sha256, progress=None):
        assert len(lineage_sha256) == 64
        document = Document(source_path)
        document.core_properties.identifier = lineage_sha256
        document.paragraphs[0].insert_paragraph_before("Draft review required before use")
        document.paragraphs[1].insert_paragraph_before().add_run(NOTICE).font.highlight_color = WD_COLOR_INDEX.YELLOW
        document.save(output_path)
        return output_path


@pytest.mark.parametrize("registered", [False, True])
def test_one_click_download_keeps_source_and_registered_folder_and_reuses_only_its_own_choices(lab, registered):
    (lab["settings"].templates_dir / "E-4515 Customer Report.docx").write_bytes(b"Word boundary")
    pending = []
    converter = ToolsService(customer_report_writer=WordBoundary(), office_protector=None)
    jobs = ToolsCustomerReportJobService(generator=converter, dispatch=pending.append, read_notices=read_customer_notices)
    app.dependency_overrides[deps.get_tools_customer_report_job_service] = lambda: jobs
    content = internal_report()
    digest = sha256(content).hexdigest()
    client = lab["client"]
    if registered:
        source, _ = official_report(lab)
        source.write_bytes(content)
        def inspect():
            return client.post(INSPECT_PROJECT, json={"source_sha256": digest})
    else:
        def inspect():
            return client.post(TOOLS + "/inspect", files={"file": ("DL-2026-05-001 Report.docx", content)})
    response = inspect()
    assert response.status_code == 200, response.text
    view = response.json()
    assert view["source_sha256"] == digest and view["decisions"] == {}
    sample = next(field for field in view["fields"] if field["kind"] == "sample")
    confirmation = TOOLS + "/inputs/" + view["input_id"] + "/generate"
    assert client.post(confirmation, json={"decisions": {}}).status_code == 422
    assert not pending
    decisions = {sample["id"]: "keep"}
    started = client.post(confirmation, json={"decisions": decisions})
    assert started.status_code == 202, started.text
    assert client.post(confirmation, json={"decisions": decisions}).json()["operation_id"] == started.json()["operation_id"]
    assert len(pending) == 1
    pending.pop()()
    url = TOOLS + "/jobs/" + started.json()["operation_id"]
    status = client.get(url).json()
    assert status["status"] == "completed" and status["notices"] == [NOTICE], status
    assert not list(lab["settings"].data_dir.glob("cr-input-*"))
    assert not list(lab["settings"].data_dir.glob("cr-out-*/prepared.docx"))
    for _ in range(2):
        result = client.get(url + "/download")
        assert result.status_code == 200
        assert "-CR" in result.headers["content-disposition"]
        downloaded = Document(BytesIO(result.content))
        assert downloaded.core_properties.identifier == digest
        row = downloaded.tables[0].rows[1]
        assert [c.text for c in row.cells] == ["Fixture PCB", "PCB-19", "Copper Alloy"]
    repeated = inspect()
    assert repeated.json()["decisions"] == decisions
    cancel = TOOLS + "/inputs/" + repeated.json()["input_id"]
    assert client.delete(cancel).status_code == 204
    assert client.post(cancel + "/generate", json={"decisions": decisions}).status_code == 410
    assert not list(lab["settings"].data_dir.glob("cr-input-*"))
    if registered:
        assert list(source.parent.glob("*.docx")) == [source]
        assert source.read_bytes() == content
        # Another application or operator edited the registered source after inspection.
        next_input = inspect().json()["input_id"]
        extra = Document(source)
        extra.add_paragraph("new revision")
        extra.save(source)
        changed = client.post(TOOLS + "/inputs/" + next_input + "/generate", json={"decisions": decisions})
        assert changed.status_code == 409
        assert not pending


def test_working_copy_returns_source_scoped_choices_and_actual_review_notices(lab, monkeypatch):
    monkeypatch.setattr(deps, "CustomerReportDocumentGateway", WordBoundary)
    (lab["settings"].templates_dir / "E-4515 Customer Report.docx").write_bytes(internal_report())
    source = upload(lab, content=internal_report()).json()["sources"][0]
    client = lab["client"]
    working = client.post(BASE + "/base", json={"source_id": source["source_id"], "expected_revision": 1}).json()
    output = working["outputs"][-1]
    request = {"expected_revision": working["revision"], "output_id": output["output_id"],
               "output_sha256": output["artifact"]["sha256"]}
    inspected = client.post(BASE + "/customer/inspect", json=request)
    assert inspected.status_code == 200, inspected.text
    view = inspected.json()
    assert view["decisions"] == {}
    key = next(item["id"] for item in view["fields"] if item["kind"] == "sample")
    decisions = {key: "omit"}
    generated = client.post(BASE + "/customer/generate", json={**request, "customer_decisions": decisions})
    assert generated.status_code == 200, generated.text
    new_state = generated.json()
    customer = new_state["customer_outputs"][-1]
    assert customer["parent_output_id"] == output["output_id"] and customer["review_notices"] == [NOTICE]
    assert len(Document(BytesIO(client.get(customer["download_url"]).content)).tables[0].rows) == 1
    assert len(Document(BytesIO(client.get(output["download_url"]).content)).tables[0].rows) == 2
    assert client.post(BASE + "/customer/inspect", json={**request, "expected_revision": new_state["revision"]}).json()["decisions"] == decisions
    assert client.post(BASE + "/customer/inspect", json={**request, "output_sha256": "0" * 64}).status_code == 409
