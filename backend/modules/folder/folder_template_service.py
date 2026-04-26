"""Project folder template preview service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from backend.domain import Project


@dataclass(frozen=True, slots=True)
class FolderPlanItem:
    """One directory or file action in a folder preview plan."""

    source_path: Path
    target_path: Path
    item_type: str
    conflict: bool = False


@dataclass(frozen=True, slots=True)
class FolderPlan:
    """Preview plan for project folder generation."""

    template_path: Path
    target_root: Path
    project_folder_path: Path
    items: tuple[FolderPlanItem, ...]
    conflict: bool = False


class FolderTemplateService:
    """Build folder generation preview plans without writing files."""

    def preview(
        self,
        project: Project,
        template_path: Path,
        target_root: Path,
        dl_number: str | None = None,
        plan_date: date | None = None,
    ) -> FolderPlan:
        """Preview directories/files that would be created from a template."""
        template = template_path.resolve()
        root = target_root.resolve()
        if not template.is_dir():
            raise ValueError(f"Template path is not a directory: {template}")
        placeholders = _placeholders(project, dl_number, plan_date or date.today())
        project_folder_name = _replace_placeholders(template.name, placeholders)
        project_folder_path = root / project_folder_name
        items = tuple(
            _plan_item(source, template, project_folder_path, placeholders)
            for source in _iter_template_items(template)
        )
        return FolderPlan(
            template_path=template,
            target_root=root,
            project_folder_path=project_folder_path,
            items=items,
            conflict=project_folder_path.exists(),
        )


def _iter_template_items(template_path: Path) -> list[Path]:
    """Return template children in deterministic path order."""
    return sorted(
        (path for path in template_path.rglob("*")),
        key=lambda path: path.relative_to(template_path).as_posix(),
    )


def _plan_item(
    source: Path,
    template_path: Path,
    project_folder_path: Path,
    placeholders: dict[str, str],
) -> FolderPlanItem:
    """Create a preview item for one template path."""
    relative_parts = [
        _replace_placeholders(part, placeholders)
        for part in source.relative_to(template_path).parts
    ]
    target = project_folder_path.joinpath(*relative_parts)
    return FolderPlanItem(
        source_path=source,
        target_path=target,
        item_type="directory" if source.is_dir() else "file",
        conflict=target.exists(),
    )


def _replace_placeholders(value: str, placeholders: dict[str, str]) -> str:
    """Replace supported placeholders in a path segment."""
    result = value
    for key, replacement in placeholders.items():
        result = result.replace(key, replacement)
    return result


def _placeholders(
    project: Project,
    dl_number: str | None,
    plan_date: date,
) -> dict[str, str]:
    """Build supported folder-name placeholder values."""
    return {
        "{DL_NUMBER}": dl_number or "",
        "{PROJECT_NO}": project.project_no,
        "{PRODUCT_NAME}": project.product_name,
        "{REQUESTOR}": project.requestor,
        "{DATE}": plan_date.isoformat(),
        "{BUSINESS_UNIT}": project.business_unit or "",
    }
