from datetime import date
from pathlib import Path

from backend.domain import Project
from backend.modules.folder import FolderTemplateService


def test_preview_simple_template(tmp_path: Path) -> None:
    template = tmp_path / "template"
    (template / "docs").mkdir(parents=True)
    (template / "docs" / "readme.txt").write_text("template", encoding="utf-8")
    target_root = tmp_path / "projects"

    plan = FolderTemplateService().preview(_project(), template, target_root)

    assert plan.project_folder_path == target_root / "template"
    assert [item.item_type for item in plan.items] == ["directory", "file"]
    assert plan.conflict is False


def test_preview_replaces_supported_placeholders(tmp_path: Path) -> None:
    template = tmp_path / "{DL_NUMBER}_{PROJECT_NO}_{PRODUCT_NAME}"
    (template / "{REQUESTOR}" / "{BUSINESS_UNIT}_{DATE}.txt").parent.mkdir(
        parents=True
    )
    (template / "{REQUESTOR}" / "{BUSINESS_UNIT}_{DATE}.txt").write_text(
        "template",
        encoding="utf-8",
    )

    plan = FolderTemplateService().preview(
        _project(),
        template,
        tmp_path / "projects",
        dl_number="DL-001",
        plan_date=date(2026, 4, 26),
    )

    assert plan.project_folder_path.name == "DL-001_PRJ-001_Connector"
    assert plan.items[-1].target_path.name == "BU-1_2026-04-26.txt"
    assert "Alice" in plan.items[-1].target_path.parts


def test_preview_reports_existing_target_conflict(tmp_path: Path) -> None:
    template = tmp_path / "{PROJECT_NO}"
    template.mkdir()
    target_root = tmp_path / "projects"
    (target_root / "PRJ-001").mkdir(parents=True)

    plan = FolderTemplateService().preview(_project(), template, target_root)

    assert plan.conflict is True
    assert plan.project_folder_path == target_root / "PRJ-001"


def _project() -> Project:
    return Project(
        project_id="project-1",
        project_no="PRJ-001",
        product_name="Connector",
        requestor="Alice",
        business_unit="BU-1",
    )
