"""Resolve the approved internal test-report template from Settings resources."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.domain import ExternalResource, ExternalResourceType


class TestReportTemplateResourceError(ValueError):
    """Raised when the E-3707_H report template cannot be resolved safely."""

    __test__ = False


class TestReportTemplateResourceStore(Protocol):
    """External-resource lookup needed by report draft generation."""

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return one registered resource by type."""


def resolve_test_report_template_path(
    resource_store: TestReportTemplateResourceStore,
) -> Path:
    """Return the unique E-3707_H `.docx` under Settings > Template folder."""
    resource = resource_store.get_by_type(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)
    if resource is None:
        raise TestReportTemplateResourceError("Template folder is not configured.")
    if not resource.active:
        raise TestReportTemplateResourceError("Template folder is inactive.")
    return discover_test_report_template(Path(resource.path))


def discover_test_report_template(template_folder: Path) -> Path:
    """Discover exactly one approved E-3707_H report template."""
    folder = Path(template_folder)
    if not folder.is_dir():
        raise TestReportTemplateResourceError(
            f"Template folder does not exist: {folder}"
        )
    matches = sorted(
        path
        for path in folder.iterdir()
        if path.is_file()
        and not path.name.startswith("~$")
        and path.suffix.lower() == ".docx"
        and "E-3707_H" in path.name.upper()
    )
    if not matches:
        raise TestReportTemplateResourceError(
            "E-3707_H test report template not found in Template folder."
        )
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise TestReportTemplateResourceError(
            f"Multiple E-3707_H test report templates found in Template folder: {names}"
        )
    return matches[0]
