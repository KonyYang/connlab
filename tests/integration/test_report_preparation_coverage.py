"""The preparation checklist reports evidence coverage, never inferred engineering Pass."""
import pytest

from tests.integration.test_internal_report_generation_api import lab
from tests.integration.test_report_authoring_api import BASE, upload


def confirm_cr(lab, state, *, step_index=0, outcome="pending"):
    step = state["context"]["steps"][step_index]
    request = {
        "expected_revision": state["revision"], "source_id": state["sources"][-1]["source_id"],
        "kind": "cr", "columns": {"sample": 1, "voltage": 2, "current": 3},
        "start_row": 2, "end_row": 2, "unit": "mV", "outcome": outcome,
        "acceptance_reason": "Reviewed against this project's recorded requirement" if outcome != "pending" else "",
        **{key: step[key] for key in ("group_id", "row_id", "step_token")},
    }
    preview = lab["client"].post(BASE + "/results/preview", json=request)
    assert preview.status_code == 200, preview.text
    response = lab["client"].post(BASE + "/results/confirm", json={
        **request, "preview_sha256": preview.json()["preview_sha256"],
    })
    assert response.status_code == 200, response.text
    return response.json()


def test_checklist_lists_confirmed_matrix_steps_without_inventing_results(lab):
    before = lab["client"].get(BASE).json()
    response = lab["client"].get(BASE + "/coverage")
    assert response.status_code == 200, response.text
    coverage = response.json()
    assert coverage["has_confirmed_matrix"] is True
    assert coverage["complete"] is False
    assert coverage["rows"]
    assert all(row["status"] == "missing" and not row["result_ids"] for row in coverage["rows"])
    assert lab["client"].get(BASE).json() == before  # Opening the checklist writes nothing.


def test_reviewed_measurements_with_pending_outcome_are_usable_but_not_complete(lab):
    state = upload(lab, role="cr", name="CR.csv", content=b"SN,V,I\nSN1,50,100\n").json()
    state = confirm_cr(lab, state)
    response = lab["client"].get(BASE + "/coverage")
    assert response.status_code == 200, response.text
    coverage = response.json()
    row = next(row for row in coverage["rows"] if row["result_ids"])
    assert row["status"] == "needs_review"
    assert row["result_ids"] == [state["results"][-1]["result_id"]]
    assert row["applied_result_ids"] == []
    assert any("acceptance" in reason.lower() for reason in row["reasons"])
    assert coverage["complete"] is False


def test_replaced_source_marks_only_its_result_stale_without_discarding_history(lab):
    state = upload(lab, role="cr", name="CR.csv", content=b"SN,V,I\nSN1,50,100\n").json()
    state = confirm_cr(lab, state, outcome="pass")
    result_id = state["results"][-1]["result_id"]
    ready = lab["client"].get(BASE + "/coverage")
    assert ready.status_code == 200, ready.text
    assert next(row for row in ready.json()["rows"] if result_id in row["result_ids"])["status"] == "ready"
    replaced = upload(lab, role="cr", name="CR.csv", revision=state["revision"],
                      content=b"SN,V,I\nSN1,60,100\n")
    assert replaced.status_code == 200, replaced.text
    coverage = lab["client"].get(BASE + "/coverage").json()
    row = next(row for row in coverage["rows"] if result_id in row["result_ids"])
    assert row["status"] == "needs_review"
    assert any("source" in reason.lower() for reason in row["reasons"])
    assert lab["client"].get(BASE).json()["results"][0]["result_id"] == result_id


def apply_selected_results(lab, state, result_ids):
    output = state["outputs"][-1]
    preview = lab["client"].post(BASE + "/assembly/preview", json={
        "expected_revision": state["revision"], "output_id": output["output_id"],
        "output_sha256": output["artifact"]["sha256"],
        "results": [{"result_id": result_id} for result_id in result_ids],
    })
    assert preview.status_code == 200, preview.text
    prepared = preview.json()
    plan = prepared["assembly_plan"]
    assert plan["can_apply"] is True, plan["issues"]
    applied = lab["client"].post(BASE + "/assembly/apply", json={
        "expected_revision": prepared["revision"], "plan_id": plan["plan_id"],
        "preview_sha256": plan["preview_sha256"],
    })
    assert applied.status_code == 200, applied.text
    return applied.json()


def test_new_unapplied_result_cannot_borrow_completion_from_stale_applied_result(lab):
    from tests.integration.test_report_batch_assembly_api import prepared_results

    state, _ = prepared_results(lab)
    old_result = state["results"][0]["result_id"]
    state = apply_selected_results(lab, state, [item["result_id"] for item in state["results"]])
    assert lab["client"].get(BASE + "/coverage").json()["complete"] is True
    replaced = upload(lab, role="cr", name="CR0.csv", revision=state["revision"],
                      content=b"SN,V,I\nSN1,90,100\n")
    assert replaced.status_code == 200, replaced.text
    state = confirm_cr(lab, replaced.json(), step_index=0, outcome="pass")
    replacement = state["results"][-1]["result_id"]

    response = lab["client"].get(BASE + "/coverage")
    assert response.status_code == 200, response.text
    coverage = response.json()
    row = next(item for item in coverage["rows"] if old_result in item["result_ids"])
    assert row["usable_result_ids"] == [replacement]
    assert row["applied_result_ids"] == []
    assert coverage["complete"] is False
    assert old_result in lab["client"].get(BASE).json()["applied_result_ids"]  # History still identifies the stale report content.


@pytest.mark.parametrize("outcome, expected_status, complete", [
    ("pass", "ready", True), ("pending", "needs_review", False),
])
def test_applying_one_valid_candidate_resolves_history_ambiguity_for_coverage(lab, outcome, expected_status, complete):
    from tests.integration.test_report_batch_assembly_api import prepared_results

    state, _ = prepared_results(lab)
    historical = state["results"][0]["result_id"]
    other_step = state["results"][1]["result_id"]
    added = upload(lab, role="cr", name="CR0_retest.csv", revision=state["revision"],
                   content=b"SN,V,I\nSN1,90,100\n")
    assert added.status_code == 200, added.text
    state = confirm_cr(lab, added.json(), step_index=0, outcome=outcome)
    selected = state["results"][-1]["result_id"]
    unresolved = lab["client"].get(BASE + "/coverage").json()
    row = next(item for item in unresolved["rows"] if selected in item["result_ids"])
    assert row["status"] == "needs_review"
    assert row["applied_result_ids"] == []
    assert unresolved["complete"] is False

    state = apply_selected_results(lab, state, [selected, other_step])
    coverage = lab["client"].get(BASE + "/coverage").json()
    row = next(item for item in coverage["rows"] if selected in item["result_ids"])
    assert row["usable_result_ids"] == [historical, selected]  # Both sources remain valid and available.
    assert row["applied_result_ids"] == [selected]
    assert row["status"] == expected_status
    assert not any("multiple" in reason.lower() for reason in row["reasons"])
    assert coverage["complete"] is complete
    assert len(lab["client"].get(BASE).json()["results"]) == 3
