from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_task101_design_records_single_page_flow_decisions() -> None:
    """TASK_101 documents the single-page New Project creation model."""
    design = (ROOT / "docs" / "archive" / "historical_plans" / "new_project_single_page_flow_redesign.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Request email source",
        "Email attachments",
        "Editable application information",
        "LTR number option",
        "Apply LTR Number and Create Folder",
        "Double-click must never import attachment data into the editor.",
        "Valid application-form attachments show an explicit `Import` action.",
        "requires explicit replacement confirmation",
        "field-level red state",
        "Do not generate or update a final Word application form during New Project creation.",
        "preview-before-write",
        "Cancel and remove draft",
    ]:
        assert term in design


def test_task101_followup_tasks_are_split_without_runtime_scope() -> None:
    """TASK_102 through TASK_104 stay ordered and do not reopen paused tasks."""
    task102 = (
        ROOT / "tasks" / "completed" / "2026" / "TASK_102_NEW_PROJECT_SINGLE_PAGE_INTAKE_APPLICATION_EDITOR.md"
    ).read_text(encoding="utf-8")
    task103 = (
        ROOT / "tasks" / "completed" / "2026" / "TASK_103_APPLICATION_FORM_IMPORT_TO_EDITOR_NO_SILENT_REPLACE.md"
    ).read_text(encoding="utf-8")
    task104 = (
        ROOT / "tasks" / "completed" / "2026" / "TASK_104_NEW_PROJECT_LTR_AND_FOLDER_ONE_ACTION_ORCHESTRATION.md"
    ).read_text(encoding="utf-8")
    task101 = (
        ROOT / "tasks" / "completed" / "2026" / "TASK_101_NEW_PROJECT_SINGLE_PAGE_FLOW_REDESIGN.md"
    ).read_text(encoding="utf-8")

    assert "## Status\n\ndone" in task101
    assert "Do not implement LTR/folder execution in this task." in task102
    assert "must not silently populate the editor" in task102
    assert "Preserve manual editor data unless the operator confirms replacement." in task103
    assert "Keep attachment double-click/open behavior separate from import." in task103
    assert "Preserve folder preview-before-write internally" in task104
    assert "Do not implement TASK_099 LTR freeze/exception behavior." in task104
