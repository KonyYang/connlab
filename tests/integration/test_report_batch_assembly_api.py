"""One confirmed batch produces one recoverable copy, never an official report."""
from io import BytesIO
from hashlib import sha256
import sqlite3
from docx import Document
from sqlalchemy import event

from tests.integration.test_internal_report_generation_api import lab
from tests.integration.test_report_authoring_api import BASE, upload
from tests.integration.test_report_preparation_coverage import confirm_cr


def prepared_results(lab):
    state = lab["client"].get(BASE).json()
    document = Document()
    document.sections[0].header.paragraphs[0].text = "DL-2026-05-001"
    document.sections[0].footer.paragraphs[0].text = "E-3707"
    document.add_paragraph("Approved wording stays unchanged")
    for step in state["context"]["steps"]:
        document.add_paragraph(f"Group {step['group_label']} Test Results")
        table = document.add_table(rows=2, cols=4)
        for cell, text in zip(table.rows[0].cells, ["Step", "Test Item", "Result", "Comment"]):
            cell.text = text
        table.cell(1, 0).text = step["step_token"]
        table.cell(1, 1).text = step["test_item"]
    stream = BytesIO()
    document.save(stream)
    original = stream.getvalue()
    state = upload(lab, content=original).json()
    response = lab["client"].post(BASE + "/base", json={
        "expected_revision": state["revision"], "source_id": state["sources"][0]["source_id"],
    })
    assert response.status_code == 200, response.text
    state = response.json()
    for index in range(2):
        state = upload(lab, role="cr", revision=state["revision"], name=f"CR{index}.csv",
                       content=f"SN,V,I\nSN{index + 1},{50 + 10 * index},100\n".encode()).json()
        state = confirm_cr(lab, state, step_index=index, outcome="pass")
    return state, original


def preview_batch(lab, state):
    output = state["outputs"][-1]
    return lab["client"].post(BASE + "/assembly/preview", json={
        "expected_revision": state["revision"], "output_id": output["output_id"],
        "output_sha256": output["artifact"]["sha256"],
        "results": [{"result_id": result["result_id"]} for result in state["results"]],
    })


def test_preview_survives_reload_and_multiple_results_make_only_one_new_working_copy(lab):
    initial, original = prepared_results(lab)
    preview = preview_batch(lab, initial)
    assert preview.status_code == 200, preview.text
    state = preview.json()
    plan = state["assembly_plan"]
    assert plan["can_apply"] is True
    assert len(state["outputs"]) == 1
    assert lab["client"].get(BASE).json()["assembly_plan"] == plan
    request = {"expected_revision": state["revision"], "plan_id": plan["plan_id"],
               "preview_sha256": plan["preview_sha256"]}
    applied = lab["client"].post(BASE + "/assembly/apply", json=request)
    assert applied.status_code == 200, applied.text
    final = applied.json()
    assert len(final["outputs"]) == 2
    assert final["assembly_plan"]["status"] == "completed"
    assert set(final["applied_result_ids"]) == {item["result_id"] for item in initial["results"]}
    document = Document(BytesIO(lab["client"].get(final["outputs"][-1]["download_url"]).content))
    assert "0.5" in document.tables[0].cell(1, 2).text
    assert "0.6" in document.tables[1].cell(1, 2).text
    assert document.paragraphs[0].text == "Approved wording stays unchanged"
    assert lab["client"].get(initial["sources"][0]["download_url"]).content == original
    repeated = lab["client"].post(BASE + "/assembly/apply", json=request)
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == final
    assert lab["client"].get(BASE + "/coverage").json()["complete"] is True
    assert lab["client"].get("/api/projects/P1/report-workspace/current-report").json()["status"] == "missing"


def test_changed_source_invalidates_prepared_plan_without_replacing_current_copy(lab):
    initial, _ = prepared_results(lab)
    preview = preview_batch(lab, initial)
    assert preview.status_code == 200, preview.text
    state = preview.json()
    plan = state["assembly_plan"]
    changed = upload(lab, role="cr", revision=state["revision"], name="CR0.csv",
                     content=b"SN,V,I\nSN1,90,100\n").json()
    rejected = lab["client"].post(BASE + "/assembly/apply", json={
        "expected_revision": changed["revision"], "plan_id": plan["plan_id"],
        "preview_sha256": plan["preview_sha256"],
    })
    assert rejected.status_code == 409, rejected.text
    reopened = lab["client"].get(BASE).json()
    assert reopened["outputs"] == initial["outputs"]
    assert reopened["assembly_plan"]["can_apply"] is False


def test_unrelated_source_does_not_invalidate_selected_result_decisions_or_batch(lab):
    initial, _ = prepared_results(lab)
    preview = preview_batch(lab, initial)
    assert preview.status_code == 200, preview.text
    plan = preview.json()["assembly_plan"]
    changed = upload(lab, role="evidence", revision=preview.json()["revision"], name="Extra note.txt",
                     content=b"Independent supporting note, not used by this batch").json()
    assert changed["assembly_plan"]["can_apply"] is True
    applied = lab["client"].post(BASE + "/assembly/apply", json={
        "expected_revision": changed["revision"], "plan_id": plan["plan_id"],
        "preview_sha256": plan["preview_sha256"],
    })
    assert applied.status_code == 200, applied.text
    assert len(applied.json()["outputs"]) == 2


def test_database_failure_after_word_generation_recovers_exact_copy_without_regeneration(lab):
    initial, original = prepared_results(lab)
    preview = preview_batch(lab, initial)
    assert preview.status_code == 200, preview.text
    state = preview.json()
    plan = state["assembly_plan"]
    request = {"expected_revision": state["revision"], "plan_id": plan["plan_id"],
               "preview_sha256": plan["preview_sha256"]}
    with lab["factory"]() as session:
        engine = session.get_bind()

    def disk_full(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO report_authoring_revisions"):
            raise sqlite3.OperationalError("isolated database write failure after document generation")

    event.listen(engine, "before_cursor_execute", disk_full)
    try:
        failed = lab["client"].post(BASE + "/assembly/apply", json=request)
    finally:
        event.remove(engine, "before_cursor_execute", disk_full)
    assert failed.status_code == 500, failed.text
    reopened = lab["client"].get(BASE).json()
    assert reopened["outputs"] == initial["outputs"]
    assert reopened["assembly_plan"]["status"] == "prepared"
    completed_files = list(lab["settings"].data_dir.rglob(f"{plan['plan_id']}/*.docx"))
    assert len(completed_files) == 1
    generated = completed_files[0]
    saved_bytes, saved_mtime = generated.read_bytes(), generated.stat().st_mtime_ns
    recovered = lab["client"].post(BASE + "/assembly/apply", json=request)
    assert recovered.status_code == 200, recovered.text
    final = recovered.json()
    assert len(final["outputs"]) == 2
    assert final["outputs"][-1]["artifact"]["sha256"] == sha256(saved_bytes).hexdigest()
    assert generated.read_bytes() == saved_bytes and generated.stat().st_mtime_ns == saved_mtime
    assert lab["client"].get(initial["sources"][0]["download_url"]).content == original
    assert lab["client"].post(BASE + "/assembly/apply", json=request).json() == final
