from backend.application.intake_section1_precheck import (
    blocking_issue_fields,
    evaluate_section1_precheck,
)


def test_revision_mismatch_is_warning_not_blocker() -> None:
    """Revision mismatch stays visible but does not block project creation."""
    issues = evaluate_section1_precheck(_base_payload(revision="A"))

    revision = [issue for issue in issues if issue.field_key == "revision"]
    assert revision
    assert all(issue.level == "warning" for issue in revision)
    assert "revision" not in blocking_issue_fields(issues)


def test_form_number_mismatch_remains_blocker() -> None:
    """Form No mismatch remains a blocking error."""
    issues = evaluate_section1_precheck(_base_payload(form_no="X-0000"))

    form_issues = [issue for issue in issues if issue.field_key == "form_no"]
    assert form_issues
    assert all(issue.level == "error" for issue in form_issues)
    assert "form_no" in blocking_issue_fields(issues)


def _base_payload(*, form_no: str = "E-3718", revision: str = "H") -> dict:
    return {
        "form_no": form_no,
        "revision": revision,
        "product_name": "Connector sample",
        "requester": "White",
        "phone": "555-0100",
        "request_date": "2026-05-03",
        "email": "white@example.com",
        "business_unit": "Power Solutions",
        "manufacturing_site": "Nantong",
        "results_format": "Formal Report (Customer)",
        "requested_completion_date": "2026-05-10",
        "test_type": "Mechanical",
        "sample_status": "Received",
        "project_type": "Reliability",
        "requested_testing": "Connector reliability test",
        "post_testing_disposition": "Return to requestor",
        "confidential": "No",
        "subcontract": "No",
        "send_copies_recipients": "white@example.com",
        "project_no": "",
        "samples": [{"product_name": "Connector sample", "quantity": "10"}],
    }
