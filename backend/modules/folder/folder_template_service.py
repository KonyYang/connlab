"""Project folder template preview service."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from backend.domain import FileAsset, Project


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


@dataclass(frozen=True, slots=True)
class FolderGenerationResult:
    """Result of executing a folder generation plan."""

    project_folder_path: Path
    generated_paths: tuple[Path, ...]


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

    def generate(
        self,
        plan: FolderPlan,
        application_form_asset: FileAsset | None = None,
    ) -> FolderGenerationResult:
        """Generate folders/files from a preview plan without overwriting."""
        if plan.conflict or any(item.conflict for item in plan.items):
            raise FileExistsError(f"Target folder already exists: {plan.project_folder_path}")
        generated: list[Path] = []
        plan.project_folder_path.mkdir(parents=False, exist_ok=False)
        generated.append(plan.project_folder_path)
        for item in plan.items:
            if item.item_type == "directory":
                item.target_path.mkdir(parents=True, exist_ok=False)
            else:
                item.target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item.source_path, item.target_path)
            generated.append(item.target_path)
        if application_form_asset is not None:
            generated.append(_copy_application_form(plan, application_form_asset))
        return FolderGenerationResult(
            project_folder_path=plan.project_folder_path,
            generated_paths=tuple(generated),
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


def _copy_application_form(plan: FolderPlan, asset: FileAsset) -> Path:
    """Copy the original application form into the request folder when available."""
    if not asset.path.is_file():
        raise FileNotFoundError(f"Application form asset not found: {asset.path}")
    request_dir = _find_request_folder(plan) or plan.project_folder_path
    target = request_dir / (asset.original_name or asset.path.name)
    if target.exists():
        raise FileExistsError(f"Application form target already exists: {target}")
    shutil.copy2(asset.path, target)
    return target


def _find_request_folder(plan: FolderPlan) -> Path | None:
    """Return the first generated directory that looks like a request folder."""
    for item in plan.items:
        if item.item_type == "directory" and "request" in item.target_path.name.lower():
            return item.target_path
    return None
