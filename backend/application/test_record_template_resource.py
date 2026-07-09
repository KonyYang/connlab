"""Resolve Test Record templates from configured external resources."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.domain import ExternalResource, ExternalResourceType


class TestRecordTemplateResourceError(ValueError):
    """Raised when the Test Record template cannot be resolved."""

    __test__ = False


class TestRecordTemplateResourceStore(Protocol):
    """Repository behavior required to resolve the Test Record template."""

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return a registered resource by type."""


def resolve_test_record_template_path(
    resource_store: TestRecordTemplateResourceStore,
    *,
    configured_template_path: Path | None = None,
) -> Path:
    """Return the Test Record template from config or the Settings Template folder."""
    if configured_template_path is not None:
        return configured_template_path

    resource = resource_store.get_by_type(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)
    if resource is None:
        raise TestRecordTemplateResourceError(
            "Test Record template path is not configured."
        )
    if not resource.active:
        raise TestRecordTemplateResourceError("Template folder is inactive.")
    return discover_test_record_template(Path(resource.path))


def discover_test_record_template(template_folder: Path) -> Path:
    """Discover the unique FDQF-E-036 Test Record template in a template folder."""
    folder = Path(template_folder)
    if not folder.is_dir():
        raise TestRecordTemplateResourceError(
            f"Template folder does not exist: {folder}"
        )
    matches = sorted(
        path
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".docx"
        and "FDQF-E-036" in path.name.upper()
        and "TEST RECORD" in path.name.upper()
    )
    if not matches:
        raise TestRecordTemplateResourceError(
            "Test Record template not found in Template folder."
        )
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise TestRecordTemplateResourceError(
            f"Multiple Test Record templates found in Template folder: {names}"
        )
    return matches[0]
