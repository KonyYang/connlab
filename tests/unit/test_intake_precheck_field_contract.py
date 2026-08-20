from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_intake_precheck_field_contract_records_section1_policy() -> None:
    """The current contract documents the authoritative SECTION 1 policy."""
    source = (ROOT / "docs" / "product_contracts" / "INTAKE_PRECHECK.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "SECTION 1 TO BE COMPLETED BY THE REQUESTOR",
        "SECTION 2 TO BE COMPLETED BY THE TESTING LABORATORY",
        "`required_before_project`",
        "`warning_before_project`",
        "`auto_clear_with_warning`",
        "`section2_excluded`",
        "`project_no` | Project # | `warning_before_project`",
        "`lab_test_request_number` | Lab Test Request Number | `auto_clear_with_warning`",
        "`send_copies_recipients` | Send copies of test results/reports to | `required_before_project`",
        "New Project Precheck must run before Project creation.",
    ]:
        assert term in source


def test_intake_precheck_field_contract_records_samples_lookups_and_msg_policy() -> None:
    """The current contract captures sample, lookup, and MSG display rules."""
    source = (ROOT / "docs" / "product_contracts" / "INTAKE_PRECHECK.md").read_text(
        encoding="utf-8"
    )
    task = (
        ROOT / "tasks" / "completed" / "2026" / "TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES.md"
    ).read_text(encoding="utf-8")

    for term in [
        "Operator may add sample rows.",
        "Operator may delete sample rows.",
        "Deleting the last remaining sample row is not allowed.",
        "Operator may copy a whole sample row into a new row.",
        "Text quantities such as `20 pcs` must be preserved in draft review.",
        "`business_unit`",
        "`manufacturing_site`",
        "`post_testing_disposition`",
        "GET /api/lookups/intake-precheck",
        "Direct `.docx` is a first-class no-email entry path.",
        "Do not list the source `.msg` package in the Attachments list.",
        "display it as an attachment with `MSG` type",
    ]:
        assert term in source

    assert "No parser code changes." in task
    assert "No backend API changes." in task
    assert "No frontend UI changes." in task
